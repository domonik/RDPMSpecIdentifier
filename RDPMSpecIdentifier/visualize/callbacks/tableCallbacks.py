import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Output, Input, ctx, html
from dash.exceptions import PreventUpdate

from RDPMSpecIdentifier.visualize.dataTable import SELECTED_STYLE, _create_table
from dash_extensions.enrich import Serverside, State, callback
import logging

logger = logging.getLogger(__name__)


@callback(
    Output('tbl', 'data'),
    Output('tbl', "page_current"),
    Output("table-selector", "options", allow_duplicate=True),
    Output('tbl', 'active_cell'),
    Input('tbl', "page_current"),
    Input('tbl', "page_size"),
    Input('tbl', 'sort_by'),
    Input('tbl', 'filter_query'),
    State('table-selector', 'value'),
    State("current-protein-id", "data"),
    State("data-store", "data"),
    State("unique-id", "data"),
    State("table-selector", "options"),
    prevent_initial_call=True
)
def update_table(page_current, page_size, sort_by, filter, selected_columns, key, rdpmspec, uid, options):
    logger.info(f"{ctx.triggered_prop_ids} triggered update of table")
    if rdpmspec is None or page_current is None:
        raise PreventUpdate
    active_cell_out = dash.no_update

    new_options = rdpmspec.extra_df.columns
    options = dash.no_update if set(new_options) == set(options) else new_options
    if selected_columns is None:
        selected_columns = []

    data = rdpmspec.extra_df.loc[:, rdpmspec._id_columns + selected_columns]

    if filter is not None:
        filtering_expressions = filter.split(' && ')
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)

            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                # these operators match pandas series operator method names
                data = data.loc[getattr(data[col_name], operator)(filter_value)]
            elif operator == 'contains':
                filter_value = str(filter_value).split(".0")[0]
                data = data.loc[data[col_name].str.contains(filter_value).fillna(False)]
            elif operator == 'datestartswith':
                filter_value = str(filter_value).split(".0")[0]

                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                data = data.loc[data[col_name].str.startswith(filter_value)]

    if sort_by is not None:
        if len(sort_by):
            data = data.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
                inplace=False
            )
    if "tbl.page_current" in ctx.triggered_prop_ids or "tbl.sort_by" in ctx.triggered_prop_ids:
        page = page_current
        size = page_size
        if len(data) > 0:
            loc = data.iloc[0].id
            active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': loc}
        else:
            active_cell_out = None
    elif "tbl.filter_query" in ctx.triggered_prop_ids:
        logger.info(page_current)
        page = 0
        size = page_size
        if len(data) > 0:
            loc = data.iloc[0].id
            active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': loc}
        else:
            active_cell_out = None


    elif key in data.index:
        loc = data.index.get_loc(key)
        page = int(np.floor(loc / page_size))
        size = page_size
    else:
        page = page_current
        size = page_size
    logger.info(f"updated Table: page:{page}, options: {options}")
    return data.iloc[page * size: (page + 1) * size].to_dict('records'), page, options, active_cell_out




@callback(
    [
        Output("data-table", "children"),
        Output("alert-div", "children", allow_duplicate=True),
        Output('tbl', 'sort_by'),
        Output('data-store', 'data', allow_duplicate=True),
        Output('run-clustering', 'data', allow_duplicate=True),
        Output('table-selector', 'value'),

    ],
    [
        Input('table-selector', 'value'),
        Input('score-btn', 'n_clicks'),
        Input('permanova-btn', 'n_clicks'),
        Input('anosim-btn', 'n_clicks'),
        Input('local-t-test-btn', 'n_clicks'),
        Input("recomputation", "children"),
        Input("rank-btn",  "n_clicks")

    ],
    [
        State("permanova-permutation-nr", "value"),
        State("anosim-permutation-nr", "value"),
        State("distance-cutoff", "value"),
        State('tbl', 'sort_by'),
        State('data-store', 'data'),
        State("unique-id", "data"),

    ],
    prevent_intital_call=True

)
def new_columns(
        sel_columns,
        n_clicks,
        permanova_clicks,
        anosim_clicks,
        t_test_clicks,
        recompute,
        ranking,
        permanova_permutations,
        anosim_permutations,
        distance_cutoff,
        current_sorting,
        rdpmsdata,
        uid
):
    logger.info(f"{ctx.triggered_id} triggered rendering of new table")
    if rdpmsdata is None:
        raise PreventUpdate
    alert = False
    run_cluster = dash.no_update
    sel_columns = [] if sel_columns is None else sel_columns
    if ctx.triggered_id == "rank-btn":
        try:
            cols = [col['column_id'] for col in current_sorting if col != "Rank"]
            asc = [col['direction'] == "asc" for col in current_sorting if col != "Rank"]

            rdpmsdata.rank_table(cols, asc)
            sel_columns += ["Rank"]
        except Exception as e:
            alert = True
            alert_msg = f"Ranking Failed:\n{str(e)}"

    if ctx.triggered_id == "permanova-btn":

        if permanova_clicks == 0:
            raise PreventUpdate
        else:
            sel_columns += ["PERMANOVA F"]

            if permanova_permutations is None:
                permanova_permutations = 9999
            if rdpmsdata.permutation_sufficient_samples:
                rdpmsdata.calc_permanova_p_value(permutations=permanova_permutations, threads=1, mode="local")
                sel_columns += ["local PERMANOVA adj p-Value"]

            else:
                rdpmsdata.calc_permanova_p_value(permutations=permanova_permutations, threads=1, mode="global")
                sel_columns += ["global PERMANOVA adj p-Value"]

                alert = True
                alert_msg = "Insufficient Number of Samples per Groups. P-Value is derived using all Proteins as background."
                " This might be unreliable"
    if ctx.triggered_id == "anosim-btn":
        if anosim_clicks == 0:
            raise PreventUpdate
        else:
            if anosim_permutations is None:
                anosim_permutations = 9999
            sel_columns += ["ANOSIM R"]

            if rdpmsdata.permutation_sufficient_samples:
                rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="local")
                sel_columns += ["local ANOSIM adj p-Value"]

            else:
                rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="global")
                sel_columns += ["global ANOSIM adj p-Value"]

                alert = True
                alert_msg = "Insufficient Number of Samples per Groups. P-Value is derived using all Proteins as background."
                " This might be unreliable"
    if ctx.triggered_id == "local-t-test-btn":
        if "RNase True peak pos" not in rdpmsdata.df:
            rdpmsdata.determine_peaks()
        rdpmsdata.calc_welchs_t_test(distance_cutoff=distance_cutoff)
        sel_columns += ["CTRL Peak adj p-Value", "RNase Peak adj p-Value"]

    if ctx.triggered_id == "score-btn":
        if n_clicks == 0:
            raise PreventUpdate
        else:
            rdpmsdata.calc_all_scores()
            run_cluster = True
            sel_columns += ["ANOSIM R", "Mean Distance", "shift direction", "RNase False peak pos", "RNase True peak pos", "relative fraction shift"]
    if alert:
        alert_msg = html.Div(
            dbc.Alert(
                alert_msg,
                color="danger",
                dismissable=True,
            ),
            className="p-2 align-items-center, alert-msg",

        )
    else:
        alert_msg = []
    tbl = _create_table(rdpmsdata, sel_columns)
    logger.info(f"Created New Table - sorting: {current_sorting}; run_cluster: {run_cluster}")
    current_sorting = dash.no_update if current_sorting is None else current_sorting
    return tbl, alert_msg, current_sorting, Serverside(rdpmsdata, key=uid), run_cluster, list(set(sel_columns))


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3




operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]
