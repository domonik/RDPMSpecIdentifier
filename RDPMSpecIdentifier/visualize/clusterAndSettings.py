
from dash import dcc, dash_table, html
from dash import html, ctx
import dash_loading_spinners as dls
import dash_daq as daq
from RDPMSpecIdentifier.visualize.staticContent import DEFAULT_COLORS
from RDPMSpecIdentifier.datastructures import RDPMSpecData
from RDPMSpecIdentifier.plots import empty_figure
from RDPMSpecIdentifier.visualize.colorSelection import _color_theme_modal, _modal_color_selection, _color_selection
from RDPMSpecIdentifier.visualize import BOOTSH5, BOOTSROW



def _get_cluster_panel(disabled: bool = False):
    panel = html.Div(
        [
            html.Div(
                html.Div(
                    [
                        dcc.Store(id="run-clustering"),
                        html.Div(
                            html.Div(
                                dls.RingChase(
                                    [
                                        dcc.Store(id="plot-dim-red", data=False),
                                        dcc.Graph(id="cluster-graph", figure=empty_figure(),
                                                  style={"min-width": "1000px", "height": "400px"}),

                                    ],
                                    color="var(--primary-color)",
                                    width=200,
                                    thickness=20,
                                ),
                                style={"overflow-x": "auto"}, className="m-2"
                            ),
                            className="col-12 col-md-7"
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            html.Span("Marker Size", style={"text-align": "center"}),
                                            className="col-10 col-md-3 justify-content-center align-self-center"
                                        ),
                                        html.Div(
                                            dcc.Slider(
                                                10, 50, step=1, marks=None,
                                                value=40,
                                                tooltip={"placement": "bottom", "always_visible": True},
                                                className="justify-content-center",
                                                id="cluster-marker-slider",
                                            ),
                                            className="col-10 col-md-7 justify-content-center",
                                        ),
                                    ],
                                    className="row justify-content-center p-2"
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            html.Span("3D", style={"text-align": "center"}),
                                            className="col-3 col-md-3 justify-content-center align-self-center"
                                        ),
                                        html.Div(
                                            daq.BooleanSwitch(
                                                label='',
                                                labelPosition='left',
                                                color="var(--primary-color)",
                                                on=False,
                                                id="3d-plot",
                                                className="align-self-center px-2",
                                                persistence=True,
                                                disabled=disabled

                                            ),
                                            className="col-7 justify-content-center text-align-center"
                                        )
                                    ],
                                    className="row justify-content-center p-2"
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            html.Span("Cluster Method", style={"text-align": "center"}),
                                            className="col-3 col-md-3 justify-content-center align-self-center"
                                        ),
                                        html.Div(
                                            dcc.Dropdown(
                                                ["HDBSCAN", "DBSCAN", "K-Means", "None"], "None",
                                                className="justify-content-center",
                                                id="cluster-method",
                                                clearable=False,
                                                disabled=disabled

                                            ),
                                            className="col-7 justify-content-center text-align-center"
                                        )
                                    ],
                                    className="row justify-content-center p-2"
                                ),
                                html.Div(
                                    html.Div(
                                        html.Button('Adjust Cluster Settings', id='adj-cluster-settings', n_clicks=0, disabled=disabled,
                                                    className="btn btn-primary", style={"width": "100%"}),
                                        className="col-10 justify-content-center text-align-center"
                                    ),
                                    className="row justify-content-center p-2"
                                ),
                                html.Div(
                                    html.Div(
                                        html.Button('Download Image', id='cluster-img-modal-btn', n_clicks=0,
                                                    className="btn btn-primary", style={"width": "100%"}),
                                        className="col-10 justify-content-center text-align-center"
                                    ),
                                    className="row justify-content-center p-2"
                                ),
                                dcc.Download(id="download-cluster-image"),

                            ],

                            className="col-md-5 col-12"
                        )
                    ],
                    className="row"
                ),
                className="databox databox-open"
            )
        ],
        className="col-12 px-1 pb-1 justify-content-center"
    )
    return panel


def selector_box(disabled: bool = False):
    sel_box = html.Div(
        [
            _color_theme_modal(2),
            _modal_color_selection("primary-2"),
            _modal_color_selection("secondary-2"),
            html.Div(
                [
                    html.Div(
                        html.Div(
                            html.H4("Settings", style={"text-align": "center"}),
                            className="col-12 justify-content-center"
                        ),
                        className="row justify-content-center p-2 p-md-2"
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Span("Distance Method", style={"text-align": "center"}),
                                className="col-4 justify-content-center align-self-center"
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    RDPMSpecData.methods, RDPMSpecData.methods[0],
                                    className="justify-content-center",
                                    id="distance-method",
                                    clearable=False,
                                    disabled=disabled,
                                    persistence=True,
                                    persistence_type="session"

                                ),
                                className="col-8 justify-content-center text-align-center"
                            )
                        ],
                        className=BOOTSROW
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Span("Kernel Size", style={"text-align": "center"}),
                                className="col-12 col-md-4 justify-content-center align-self-center"
                            ),
                            html.Div(
                                dcc.Slider(
                                    0, 5, step=None,
                                    marks={
                                        0: "0",
                                        3: '3',
                                        5: '5',
                                    }, value=3,
                                    className="justify-content-center",
                                    id="kernel-slider",
                                    disabled=disabled
                                ),
                                className="col-12 col-md-8 justify-content-center",
                            ),
                        ],
                        className=BOOTSROW
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Button('Get Score', id='score-btn', n_clicks=0, className="btn btn-primary",
                                            style={"width": "100%"}, disabled=disabled),
                                className="col-6 justify-content-center text-align-center"
                            ),
                            html.Div(
                                html.Button('Rank Table', id='rank-btn', n_clicks=0, className="btn btn-primary",
                                            disabled=disabled,
                                            style={"width": "100%"}),
                                className="col-6 justify-content-center text-align-center"
                            ),
                        ],

                        className=BOOTSROW
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Input(
                                    style={"width": "100%", "height": "100%", "border-radius": "5px", "color": "white",
                                           "text-align": "center"},
                                    id="distance-cutoff",
                                    placeholder="Distance Cutoff",
                                    className="text-align-center",
                                    type="number",
                                    min=0,
                                    disabled=disabled
                                ),
                                className="col-4 text-align-center align-items-center"
                            ),
                            html.Div(
                                html.Button('Peak T-Tests', id='local-t-test-btn', n_clicks=0,
                                            className="btn btn-primary",
                                            style={"width": "100%"}, disabled=disabled),
                                className="col-8 justify-content-center text-align-center"
                            ),
                        ],
                        className=BOOTSROW
                    ),

                    html.Div(
                        [
                            html.Div(
                                dcc.Input(
                                    style={"width": "100%", "height": "100%", "border-radius": "5px", "color": "white", "text-align": "center"},
                                    id="permanova-permutation-nr",
                                    placeholder="Number of Permutations",
                                    className="text-align-center",
                                    type="number",
                                    min=1,
                                    disabled=disabled
                                ),
                                className="col-4 text-align-center align-items-center"
                            ),
                            html.Div(
                                html.Button('Run PERMANOVA', id='permanova-btn', n_clicks=0,
                                            className="btn btn-primary",
                                            style={"width": "100%"}, disabled=disabled),
                                className="col-8 justify-content-center text-align-center"
                            ),
                            html.Div(
                                id="alert-div",
                                className="col-12"
                            )

                        ],
                        className=BOOTSROW
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Input(
                                    style={"width": "100%", "height": "100%", "border-radius": "5px", "color": "white",
                                           "text-align": "center"},
                                    id="anosim-permutation-nr",
                                    placeholder="Number of Permutations",
                                    className="text-align-center",
                                    type="number",
                                    min=1,
                                    disabled=disabled
                                ),
                                className="col-4 text-align-center align-items-center"
                            ),
                            html.Div(
                                html.Button('Run ANOSIM', id='anosim-btn', n_clicks=0,
                                            className="btn btn-primary", disabled=disabled,
                                            style={"width": "100%"}),
                                className="col-8 justify-content-center text-align-center"
                            ),

                        ],
                        className=BOOTSROW
                    ),

                    html.Div(
                        [
                            html.Div(
                                html.Button('Export JSON', id='export-pickle-btn', n_clicks=0, className="btn btn-primary",
                                            style={"width": "100%"}),
                                className="col-6 justify-content-center text-align-center"
                            ),
                            dcc.Download(id="download-pickle"),
                            html.Div(
                                html.Button('Export TSV', id='export-btn', n_clicks=0, className="btn btn-primary",
                                            style={"width": "100%"}),
                                className="col-6 justify-content-center text-align-center"
                            ),
                            dcc.Download(id="download-dataframe-csv"),
                        ],

                        className=BOOTSROW
                    ),
                    html.Div(
                        html.Div(
                            _color_selection(),
                            className="col-12"),
                        className="row justify-content-center pb-2"
                    ),
                ],
                className="databox justify-content-center"
            )
        ],
        className="col-12 col-md-6 p-1 justify-content-center equal-height-column"
    )
    return sel_box
