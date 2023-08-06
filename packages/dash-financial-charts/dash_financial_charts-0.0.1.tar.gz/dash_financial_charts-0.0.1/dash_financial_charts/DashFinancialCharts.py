# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashFinancialCharts(Component):
    """A DashFinancialCharts component.
Prototype chart from example

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- chartStyle (dict; optional):
    Chart style.

- data (list; optional):
    Initial data.

- emaList (list | number; optional):
    EMA list."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.UNDEFINED, emaList=Component.UNDEFINED, chartStyle=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'chartStyle', 'data', 'emaList']
        self._type = 'DashFinancialCharts'
        self._namespace = 'dash_financial_charts'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'chartStyle', 'data', 'emaList']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DashFinancialCharts, self).__init__(**args)
