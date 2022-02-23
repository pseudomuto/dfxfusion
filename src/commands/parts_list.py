from collections import defaultdict
from functools import reduce

import adsk.core
import adsk.fusion

from .base import BaseCommand


def count_by(f, seq):
    d = defaultdict(int)
    for c in seq:
        d[f(c)] += 1

    return dict(d)


def sanitizePartNumber(x):
    return x.replace(' (1)', '').replace('(Mirror)', '')


class PartsListCommand(BaseCommand):
    """A command which generates a part list from the model

    A part in this sense is a visible body within a component. Any component
    without a body will not have a part generated for it, though this will
    recurse into it's subcomponents (think assemblies).

    Parts will be named <partNumber>.<bodyName>. Measurement units are all in
    centimetres, but can be converted to the document units by making use of
    the units manager.

    Mirrored parts will be merged with the originals.
    """

    def register(addin):
        """Register this command in the utilities dropdown"""
        addin.add_command('Parts List', PartsListCommand, {
            'cmd_description': 'View Parts List',
            'cmd_id': 'dfx_parts_list',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'SolidScriptsAddinsPanel',
            'cmd_resources': 'command_icons',
            'command_visible': True,
        })

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = self._app_objects()
        command.okButtonText = "Export"

        # get a list of all components that have bodies
        components = [x.component for x in ao.design.rootComponent.allOccurrences
                      if x.component.bRepBodies.count > 0]

        # before uniq'ing the list, get counts for each partName
        counts = count_by(lambda x: sanitizePartNumber(x.partNumber), components)

        # make unique by partName
        components = {sanitizePartNumber(x.partNumber): x for x in components}.values()

        parts = []
        for component in components:
            comp_parts = [Part.from_body(counts[sanitizePartNumber(component.partNumber)], b)
                          for b in component.bRepBodies
                          if b.isVisible]

            parts.extend(comp_parts)

        self._build_table_input(ao.units_manager, inputs, parts)

    def _build_table_input(self, um, inputs, parts):
        table = inputs.addTableCommandInput(
            id='dfx_parts_list',
            name='Parts List',
            numberOfColumns=0,
            columnRatio='3:1:1:1:1',
        )

        #  table.minimumVisibleRows = 10
        table.maximumVisibleRows = 10
        table.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle
        table.hasGrid = True

        fields = [inputs.addStringValueInput(n, n, n) for n in ('Name', 'Qty', 'Length', 'Width', 'Thickness')]
        for idx, field in enumerate(fields):
            field.isEnabled = False
            field.isReadOnly = True
            table.addCommandInput(field, 0, idx)

        [self._add_row(p, table, inputs, um) for p in parts]

    def _add_row(self, part, table, inputs, um):
        row = table.rowCount
        fields = [
            inputs.addStringValueInput("p{}_name".format(row), 'Name', part.name),
            inputs.addStringValueInput('p{}_qty'.format(row), 'Qty', str(part.count)),
            inputs.addStringValueInput('p{}-len'.format(row), 'Length', um.formatInternalValue(part.length)),
            inputs.addStringValueInput('p{}_w'.format(row), 'Width', um.formatInternalValue(part.width)),
            inputs.addStringValueInput('p{}_t'.format(row), 'Thickness', um.formatInternalValue(part.thickness)),
        ]

        for idx, field in enumerate(fields):
            field.isReadOnly = True
            table.addCommandInput(field, row, idx)


class Part:
    """A class that represents a single "part".

    This is the body details along with the count.
    """
    def from_body(count: int, body: adsk.fusion.BRepBody):
        """Creates a Part from the given body and units manager"""
        min = body.boundingBox.minPoint
        max = body.boundingBox.maxPoint

        # TODO: Is this the right move?
        #
        # Currently, we take the x delta, y delta, a z delta values and sort them
        # in descending order. The longest one is the length, followed by the
        # width, then finally, the thickness.
        dimensions = [max.x - min.x, max.y - min.y, max.z - min.z]
        dimensions.sort(reverse=True)

        name = "{}.{}".format(body.parentComponent.partNumber, body.name)
        if body.parentComponent.bRepBodies.count == 1:
            # special case if there's only 1 body, just use the component name
            name = body.parentComponent.partNumber

        return Part(
            sanitizePartNumber(name),
            count,
            dimensions[0],
            dimensions[1],
            dimensions[2],
        )

    def __init__(self, name: str, count: int, length: float, width: float, thickness: float):
        """Creates a new part

        All inputs here are floats are represent the value in centimeters
        """
        self._name = name
        self._count = count
        self._length = round(length, 2)
        self._width = round(width, 2)
        self._thickness = round(thickness, 2)

    def __str__(self):
        return "({}) {}: {}cm x {}cm x {}cm".format(
            self.count,
            self.name,
            self.length,
            self.width,
            self.thickness,
        )

    @property
    def name(self):
        return self._name

    @property
    def count(self):
        return self._count

    @property
    def length(self):
        """The length (in cm)"""
        return self._length

    @property
    def width(self):
        """The width (in cm)"""
        return self._width

    @property
    def thickness(self):
        """The thickness (in cm)"""
        return self._thickness
