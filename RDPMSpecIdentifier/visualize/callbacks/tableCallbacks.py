import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Output, Input, ctx, html
from dash.exceptions import PreventUpdate
from pandas.core.dtypes.common import is_numeric_dtype
from dash.dash_table.Format import Format
from RDPMSpecIdentifier.visualize.dataTable import SELECTED_STYLE, _create_table
from dash_extensions.enrich import Serverside, State, callback
import logging
logger = logging.getLogger(__name__)

MAXPERMUTATIONS = 9999

@callback(
    Output("ff-ids", "data", allow_duplicate=True),
    Input('tbl', 'selected_row_ids'),
    State('data-store', 'data'),

)
def update_ff_ids(selected_columns, rdpmsdata):
    if selected_columns is None or selected_columns == []:
        raise PreventUpdate
    proteins = rdpmsdata.df.iloc[list(selected_columns)]["RDPMSpecID"]

    return proteins


@callback(
    Output("tbl", "selected_rows"),
    Output("current-row-ids", "data", allow_duplicate=True),
    Output("tbl", "selected_row_ids", allow_duplicate=True),
    Input("tbl", "derived_viewport_row_ids"),
    State("tbl", "selected_row_ids"),
    State("current-row-ids", "data"),

)
def update_selection_on_page_switch(vpids, selected_ids, current_ids):
    if vpids is None:
        raise PreventUpdate
    if selected_ids is None:
        selected_ids = []
    logger.info(f"Syncing row Ids {selected_ids}, {current_ids}, {vpids}")
    vpids = np.asarray(vpids)
    selected_ids = list(dict.fromkeys(selected_ids + current_ids)) if current_ids is not None else selected_ids
    selected_ids = np.asarray(selected_ids)
    rows = np.where(np.isin(vpids, selected_ids))[0]
    return rows, selected_ids, selected_ids




@callback(
    Output("tbl", "selected_rows", allow_duplicate=True),
    Output("current-row-ids", "data", allow_duplicate=True),
    Output("tbl", "selected_row_ids", allow_duplicate=True),
    Input("reset-rows-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_selected_rows(n_clicks):
    if n_clicks is not None:
        return [], [], []
    else: raise PreventUpdate


@callback(
    Output("current-row-ids", "data", allow_duplicate=True),
    Input("tbl", "selected_row_ids"),
    State("current-row-ids", "data"),
    State("tbl", "derived_viewport_row_ids"),

)
def update_current_rows(sel_rows, current_selection, vpids):
    if sel_rows is None or vpids is None:
        raise PreventUpdate
    if current_selection is None:
        current_selection = []
    logger.info(f"selected-row-ids on page {sel_rows}")
    current_selection = [cid for cid in current_selection if cid not in set(vpids)]
    sel_rows = list(dict.fromkeys(sel_rows + current_selection))
    logger.info(f"current-row-ids {sel_rows}")
    return sel_rows

#
# @callback(
#     Output('tbl', 'data'),
#     Output('tbl', "page_current"),
#     Output("table-selector", "options", allow_duplicate=True),
#     Output('tbl', 'active_cell'),
#     Output("tbl", "selected_row_ids"),
#     Input('tbl', "page_current"),
#     Input('tbl', "page_size"),
#     Input('tbl', 'sort_by'),
#     Input('tbl', 'filter_query'),
#     State('table-selector', 'value'),
#     State("current-protein-id", "data"),
#     State("data-store", "data"),
#     State("unique-id", "data"),
#     State("table-selector", "options"),
#     State('tbl', 'selected_row_ids'),
#
#     prevent_initial_call=True
# )
# def update_table(page_current, page_size, sort_by, filter, selected_columns, key, rdpmspec, uid, options, selected_rows):
#     logger.info(f"{ctx.triggered_prop_ids} triggered update of table")
#     logger.info(f"selected rows are: {selected_rows}")
#     if rdpmspec is None or page_current is None:
#         raise PreventUpdate
#     active_cell_out = dash.no_update
#
#     new_options = rdpmspec.extra_df.columns
#     options = dash.no_update if set(new_options) == set(options) else new_options
#     if selected_columns is None:
#         selected_columns = []
#
#     data = rdpmspec.extra_df.loc[:, rdpmspec._id_columns + selected_columns]
#
#     if filter is not None:
#         filtering_expressions = filter.split(' && ')
#         for filter_part in filtering_expressions:
#             col_name, operator, filter_value = split_filter_part(filter_part)
#
#             if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
#                 # these operators match pandas series operator method names
#                 data = data.loc[getattr(data[col_name], operator)(filter_value)]
#             elif operator == 'contains':
#                 filter_value = str(filter_value).split(".0")[0]
#                 data = data.loc[data[col_name].str.contains(filter_value).fillna(False)]
#             elif operator == 'datestartswith':
#                 filter_value = str(filter_value).split(".0")[0]
#
#                 # this is a simplification of the front-end filtering logic,
#                 # only works with complete fields in standard format
#                 data = data.loc[data[col_name].str.startswith(filter_value)]
#
#     if sort_by is not None:
#         if len(sort_by):
#             data = data.sort_values(
#                 [col['column_id'] for col in sort_by],
#                 ascending=[
#                     col['direction'] == 'asc'
#                     for col in sort_by
#                 ],
#                 inplace=False
#             )
#     if "tbl.page_current" in ctx.triggered_prop_ids or "tbl.sort_by" in ctx.triggered_prop_ids:
#         page = page_current
#         size = page_size
#         if len(data) > 0:
#             loc = data.iloc[0].id
#             active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': loc}
#         else:
#             active_cell_out = None
#     elif "tbl.filter_query" in ctx.triggered_prop_ids:
#         logger.info(page_current)
#         page = 0
#         size = page_size
#         if len(data) > 0:
#             loc = data.iloc[0].id
#             active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': loc}
#         else:
#             active_cell_out = None
#
#
#     elif key in data.index:
#         loc = data.index.get_loc(key)
#         page = int(np.floor(loc / page_size))
#         size = page_size
#     else:
#         page = page_current
#         size = page_size
#     logger.info(f"updated Table: page:{page}, options: {options}")
#     return data.iloc[page * size: (page + 1) * size].to_dict('records'), page, options, active_cell_out, selected_rows

@callback(
    Output("table-state", "data"),
    Input('tbl', "page_current"),
    Input('tbl', 'sort_by'),
    Input('tbl', 'filter_query'),

)
def save_table_state(page_current, sort_by, filter_query):
    tbl_state = {"page_current": page_current, "sort_by": sort_by, "filter_query": filter_query}
    return tbl_state


@callback(
    Output('tbl', "page_current", allow_duplicate=True),
    Output('tbl', 'sort_by'),
    Output('tbl', 'filter_query'),
    Input("tbl", "columns"),
    State("table-state", "data"),

)
def load_table_state(pathname, table_state):
    if table_state is None:
        raise PreventUpdate
    return table_state["page_current"], table_state["sort_by"], table_state["filter_query"]


@callback(
    Output('tbl', 'data'),
    Output('tbl', 'selected_row_ids'),
    Output('tbl', 'active_cell'),
    Output('tbl', 'page_current'),
    Input('tbl', "data"),
    Input('tbl', "page_current"),
    Input('tbl', "page_size"),
    Input('tbl', 'sort_by'),
    Input('tbl', 'filter_query'),
    State('table-selector', 'value'),
    State("current-row-ids", "data"),
    State("data-store", "data")
)
def update_table(table_data, page_current, page_size, sort_by, filter_query, selected_columns, selected_row_ids, rdpmsdata):
    if rdpmsdata is None or page_current is None:
        raise PreventUpdate

    if selected_columns is None:
        selected_columns = []
    data = rdpmsdata.extra_df.loc[:, rdpmsdata._id_columns + selected_columns]

    if filter_query is not None:
        filtering_expressions = filter_query.split(' && ')
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
        if len(data) > 0:
            active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': 0}
        else:
            active_cell_out = None
    elif "tbl.filter_query" in ctx.triggered_prop_ids:
        logger.info(page_current)
        page = 0
        if len(data) > 0:
            active_cell_out = {'row': 1, 'column': 1, 'column_id': 'RDPMSpecID', 'row_id': 0}
        else:
            active_cell_out = None
    else:
        active_cell_out = dash.no_update
        page = page_current

    return_value = data.iloc[page * page_size: (page_current + 1) * page_size]
    if isinstance(active_cell_out, dict):
        loc = return_value.iloc[0].id
        active_cell_out['row_id'] = loc
    return return_value.to_dict('records'), selected_row_ids, active_cell_out, page

#
# @callback(
#     [
#         Output("tbl", "columns"),
#         Output('tbl', 'data', allow_duplicate=True),
#         Output("alert-div", "children", allow_duplicate=True),
#         Output('tbl', 'sort_by'),
#         Output('data-store', 'data', allow_duplicate=True),
#         Output('run-clustering', 'data', allow_duplicate=True),
#         Output('table-selector', 'value'),
#
#     ],
#     [
#         Input('table-selector', 'value'),
#         Input('score-btn', 'n_clicks'),
#         Input('permanova-btn', 'n_clicks'),
#         Input('anosim-btn', 'n_clicks'),
#         Input('local-t-test-btn', 'n_clicks'),
#         Input("recomputation", "children"),
#         Input("rank-btn",  "n_clicks")
#
#     ],
#     [
#         State("permanova-permutation-nr", "value"),
#         State("anosim-permutation-nr", "value"),
#         State("distance-cutoff", "value"),
#         State('tbl', 'sort_by'),
#         State('data-store', 'data'),
#         State("unique-id", "data"),
#
#     ],
#     prevent_intital_call=True
#
# )
# def new_columns(
#         sel_columns,
#         n_clicks,
#         permanova_clicks,
#         anosim_clicks,
#         t_test_clicks,
#         recompute,
#         ranking,
#         permanova_permutations,
#         anosim_permutations,
#         distance_cutoff,
#         current_sorting,
#         rdpmsdata,
#         uid
# ):
#     logger.info(f"{ctx.triggered_id} triggered rendering of new table")
#     if rdpmsdata is None:
#         raise PreventUpdate
#     alert = False
#     run_cluster = dash.no_update
#     sel_columns = [] if sel_columns is None else sel_columns
#     if ctx.triggered_id == "rank-btn":
#         try:
#             cols = [col['column_id'] for col in current_sorting if col != "Rank"]
#             asc = [col['direction'] == "asc" for col in current_sorting if col != "Rank"]
#
#             rdpmsdata.rank_table(cols, asc)
#             sel_columns += ["Rank"]
#         except Exception as e:
#             alert = True
#             alert_msg = f"Ranking Failed:\n{str(e)}"
#
#     if ctx.triggered_id == "permanova-btn":
#
#         if permanova_clicks == 0:
#             raise PreventUpdate
#         else:
#             sel_columns += ["PERMANOVA F"]
#
#             if permanova_permutations is None:
#                 permanova_permutations = 9999
#             if rdpmsdata.permutation_sufficient_samples:
#                 rdpmsdata.calc_permanova_p_value(permutations=permanova_permutations, threads=1, mode="local")
#                 sel_columns += ["local PERMANOVA adj p-Value"]
#
#             else:
#                 rdpmsdata.calc_permanova_p_value(permutations=permanova_permutations, threads=1, mode="global")
#                 sel_columns += ["global PERMANOVA adj p-Value"]
#
#                 alert = True
#                 alert_msg = "Insufficient Number of Samples per Groups. P-Value is derived using all Proteins as background."
#                 " This might be unreliable"
#     if ctx.triggered_id == "anosim-btn":
#         if anosim_clicks == 0:
#             raise PreventUpdate
#         else:
#             if anosim_permutations is None:
#                 anosim_permutations = 9999
#             sel_columns += ["ANOSIM R"]
#
#             if rdpmsdata.permutation_sufficient_samples:
#                 rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="local")
#                 sel_columns += ["local ANOSIM adj p-Value"]
#
#             else:
#                 rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="global")
#                 sel_columns += ["global ANOSIM adj p-Value"]
#
#                 alert = True
#                 alert_msg = "Insufficient Number of Samples per Groups. P-Value is derived using all Proteins as background."
#                 " This might be unreliable"
#     if ctx.triggered_id == "local-t-test-btn":
#         if "RNase True peak pos" not in rdpmsdata.df:
#             rdpmsdata.determine_peaks()
#         rdpmsdata.calc_welchs_t_test(distance_cutoff=distance_cutoff)
#         sel_columns += ["CTRL Peak adj p-Value", "RNase Peak adj p-Value"]
#
#     if ctx.triggered_id == "score-btn":
#         if n_clicks == 0:
#             raise PreventUpdate
#         else:
#             rdpmsdata.calc_all_scores()
#             run_cluster = True
#             sel_columns += ["ANOSIM R", "Mean Distance", "shift direction", "RNase False peak pos", "RNase True peak pos", "relative fraction shift"]
#     if alert:
#         alert_msg = html.Div(
#             dbc.Alert(
#                 alert_msg,
#                 color="danger",
#                 dismissable=True,
#             ),
#             className="p-2 align-items-center, alert-msg",
#
#         )
#     else:
#         alert_msg = []
#     #tbl = _create_table(rdpmsdata, sel_columns)
#     selected_columns = list(set(sel_columns))
#
#     data = rdpmsdata.extra_df.loc[:, rdpmsdata._id_columns + selected_columns]
#     columns = []
#     num_cols = ["shift direction"]
#     for i in data.columns:
#         if i != "id":
#             d = dict()
#             d["name"] = str(i)
#             d["id"] = str(i)
#             if is_numeric_dtype(data[i]):
#                 d["type"] = "numeric"
#                 if "p-Value" in i:
#                     d["format"] = Format(precision=2)
#                 else:
#                     d["format"] = Format(precision=4)
#
#                 num_cols.append(str(i))
#             columns.append(d)
#     logger.info(f"Created New Table - sorting: {current_sorting}; run_cluster: {run_cluster}")
#     current_sorting = dash.no_update if current_sorting is None else current_sorting
#     logger.info(data.to_dict("records"))
#     logger.info(columns)
#     return columns, data.to_dict('records'), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update



@callback(
    Output("table-selector", "value", allow_duplicate=True),
    Output("data-store", "data", allow_duplicate=True),
    Output("run-clustering", "data", allow_duplicate=True),
    Input('score-btn', 'n_clicks'),
    State("table-selector", "value"),
    State("data-store", "data"),
    State("unique-id", "data")

)
def run_scoring(n_clicks, sel_columns, rdpmsdata, uid):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        rdpmsdata.calc_all_scores()
        sel_columns += ["ANOSIM R", "Mean Distance", "position strongest shift"]
        if not rdpmsdata.categorical_fraction:
            peak_names = rdpmsdata.score_columns[-2:]
            if isinstance(peak_names, np.ndarray):
                peak_names = peak_names.tolist()
            sel_columns += ["shift direction", "relative fraction shift"]
            sel_columns += peak_names
        sel_columns = list(set(sel_columns))
    return sel_columns, Serverside(rdpmsdata, key=uid), True


@callback(
    Output("table-selector", "value", allow_duplicate=True),
    Output("data-store", "data", allow_duplicate=True),
    Output("alert-div", "children", allow_duplicate=True),
    Input('rank-btn', 'n_clicks'),
    State("table-selector", "value"),
    State('tbl', 'sort_by'),

    State("data-store", "data"),
    State("unique-id", "data"),
    prevent_initial_call=True
)
def rank_table(btn, sel_columns, current_sorting, rdpmsdata, uid):
    alert = False
    if btn is None or btn == 0:
        raise PreventUpdate
    try:
        cols = [col['column_id'] for col in current_sorting if col != "Rank"]
        asc = [col['direction'] == "asc" for col in current_sorting if col != "Rank"]

        rdpmsdata.rank_table(cols, asc)
        sel_columns += ["Rank"]
    except Exception as e:
        alert = True
        alert_msg = f"Ranking Failed:\n{str(e)}"
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
        alert_msg = dash.no_update

    return sel_columns, Serverside(rdpmsdata, key=uid), alert_msg

@callback(
    Output("table-selector", "value", allow_duplicate=True),
    Output("data-store", "data", allow_duplicate=True),
    Output("alert-div", "children", allow_duplicate=True),
    Output("tbl", "data", allow_duplicate=True),
    Input('anosim-btn', 'n_clicks'),
    State("table-selector", "value"),
    State("anosim-permutation-nr", "value"),
    State("data-store", "data"),
    State("unique-id", "data"),

)
def run_anosim(n_clicks, sel_columns, anosim_permutations, rdpmsdata, uid):
    alert_msg = dash.no_update
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        if anosim_permutations is None:
            anosim_permutations = 999
        if anosim_permutations > 9999:
            alert_msg = f"Number of permutations ({anosim_permutations}) too high. " \
                        f"Only less than {MAXPERMUTATIONS} supported."
            alert_msg = html.Div(
                dbc.Alert(
                    alert_msg,
                    color="danger",
                    dismissable=True,
                ),
                className="p-2 align-items-center, alert-msg",

            )
            return dash.no_update, dash.no_update, alert_msg, dash.no_update

        sel_columns += ["ANOSIM R"]

        if rdpmsdata.permutation_sufficient_samples:
            rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="local")
            sel_columns += ["local ANOSIM adj p-Value"]

        else:
            rdpmsdata.calc_anosim_p_value(permutations=anosim_permutations, threads=1, mode="global")
            sel_columns += ["global ANOSIM adj p-Value"]

            alert_msg = "Insufficient Number of Samples per Groups. P-Value is derived using all Proteins as background."
            " This might be unreliable"
            alert_msg = html.Div(
                dbc.Alert(
                    alert_msg,
                    color="danger",
                    dismissable=True,
                ),
                className="p-2 align-items-center, alert-msg",

            )
    sel_columns = list(set(sel_columns))
    return sel_columns, Serverside(rdpmsdata, key=uid), alert_msg, dash.no_update


@callback(
    Output("sel-col-state", "data"),
    Output('table-selector', 'value'),
    Input('table-selector', 'value'),
    State('sel-col-state', 'data'),
    State("data-store", "data"),

)
def set_columns_from_state(selected_columns, sel_col_state, rdpmsdata):
    logger.info(f"Will update columns: {selected_columns}, col_state: {sel_col_state}")
    sel_col_state = [] if sel_col_state is None else sel_col_state
    check = all(column in rdpmsdata.extra_df.columns for column in sel_col_state)

    if (selected_columns is None or len(selected_columns) == 0) and len(sel_col_state) > 0 and check:
        selected_columns = sel_col_state
        sel_col_state = dash.no_update
    else:
        sel_col_state = selected_columns
        selected_columns = dash.no_update
    return sel_col_state, selected_columns


@callback(
    Output("tbl", "columns"),
    Output('tbl', 'data', allow_duplicate=True),
    Input('table-selector', 'value'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def update_columns(selected_columns, rdpmsdata):

    selected_columns = [] if selected_columns is None else selected_columns

    data = rdpmsdata.extra_df.loc[0:1, rdpmsdata._id_columns + selected_columns]
    columns = []
    num_cols = ["shift direction"]
    for i in data.columns:
        if i != "id":
            d = dict()
            d["name"] = str(i)
            d["id"] = str(i)
            if is_numeric_dtype(data[i]):
                d["type"] = "numeric"
                if "p-Value" in i:
                    d["format"] = Format(precision=2)
                else:
                    d["format"] = Format(precision=4)

                num_cols.append(str(i))
            columns.append(d)
    logger.info(f"Updated displayed columns- {columns}")
    return columns, data.to_dict('records')


@callback(
    Output("table-selector", "options", allow_duplicate=True),
    Input('data-store', 'data'),
    Input("table-selector", "options"),

)
def update_selectable_columns(rdpmsdata, options):
    if rdpmsdata is None:
        raise PreventUpdate
    new_options = rdpmsdata.extra_df.columns
    new_options = list(new_options)
    new_options.remove("RDPMSpecID")
    options = dash.no_update if set(new_options) == set(options) else new_options
    return options


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
