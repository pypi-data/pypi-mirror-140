# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DynamicGrid(Component):
    """A DynamicGrid component.
dd

Keyword arguments:

- id (string; optional):
    dd.

- cellPadding (dict; default { horizontal: 3, vertical: 2 }):
    dd.

- columns (list; optional):
    dd.

- data (list; optional):
    dd.

- editable (list; optional):
    dd.

- editedValues (list; optional):
    dd.

- font (string; default '13px Microsoft Sans Serif'):
    dd.

- height (string; default 'fit-all-rows'):
    dd.

- ids (list; optional):
    dd.

- rowHeight (number; default 16):
    dd.

- selectedCells (list; optional):
    dd.

- width (string; default 'fit-all-columns'):
    dd."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.UNDEFINED, columns=Component.UNDEFINED, ids=Component.UNDEFINED, editable=Component.UNDEFINED, selectedCells=Component.UNDEFINED, editedValues=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, rowHeight=Component.UNDEFINED, font=Component.UNDEFINED, cellPadding=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'cellPadding', 'columns', 'data', 'editable', 'editedValues', 'font', 'height', 'ids', 'rowHeight', 'selectedCells', 'width']
        self._type = 'DynamicGrid'
        self._namespace = 'dash_dynamic_grid'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'cellPadding', 'columns', 'data', 'editable', 'editedValues', 'font', 'height', 'ids', 'rowHeight', 'selectedCells', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DynamicGrid, self).__init__(**args)
