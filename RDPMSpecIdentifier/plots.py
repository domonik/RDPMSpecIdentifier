import pandas as pd
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from typing import Iterable, Tuple, List, Any
from plotly.colors import qualitative
from RDPMSpecIdentifier.datastructures import RDPMSpecData
import plotly.io as pio
import copy

DEFAULT_COLORS = {"primary": "rgb(138, 255, 172)", "secondary": "rgb(255, 138, 221)"}

COLOR_SCHEMES = {
    "Flamingo": (DEFAULT_COLORS["primary"], DEFAULT_COLORS["secondary"]),
    "Viking": ("rgb(79, 38, 131) ", "rgb(255, 198, 47)"),
    "Dolphin": ("rgb(0, 142, 151) ", "rgb(252, 76, 2)"),
    "Cardinal": ("rgb(151,35,63)", "rgb(0,0,0)"),
    "Falcon": ("rgb(167, 25, 48)", "rgb(0, 0, 0)"),
    "Raven": ("rgb(26, 25, 95)", "rgb(0, 0, 0)"),
    "Bill": ("rgb(0, 51, 141)", "rgb(198, 12, 48)"),
    "Panther": ("rgb(0, 133, 202)", "rgb(16, 24, 32)"),
    "Bear": ("rgb(111, 22, 42)", "rgb(12, 35, 64)"),
    "Bengal": ("rgb(251, 79, 20)", "rgb(0, 0, 0)"),
    "Brown": ("rgb(49, 29, 0)", "rgb(255, 60, 0)"),
    "Cowboy": ("rgb(0, 34, 68)", "rgb(255, 255, 255)"),
    "Bronco": ("rgb(251, 79, 20)", "rgb(0, 34, 68)"),
    "Lion": ("rgb(0, 118, 182)", "rgb(176, 183, 188)"),
    "Packer": ("rgb(24, 48, 40)", "rgb(255, 184, 28)"),
    "Texan": ("rgb(3, 32, 47)", "rgb(167, 25, 48)"),
    "Colt": ("rgb(0, 44, 95)", "rgb(162, 170, 173)"),
    "Jaguar": ("rgb(215, 162, 42)", "rgb(0, 103, 120)"),
    "Chief": ("rgb(227, 24, 55)", "rgb(255, 184, 28)"),
    "Charger": ("rgb(0, 128, 198)", "rgb(255, 194, 14)"),
    "Ram": ("rgb(0, 53, 148)", "rgb(255, 163, 0)"),
    "Patriot": ("rgb(0, 34, 68)", "rgb(198, 12, 48)"),
    "Saint": ("rgb(211, 188, 141)", "rgb(16, 24, 31)"),
    "Giant": ("rgb(100, 75, 0, 30)", "rgb(163, 13, 45)"),
    "Jet": ("rgb(18, 87, 64)", "rgb(255, 255, 255)"),
    "Raider": ("rgb(0, 0, 0)", "rgb(165, 172, 175)"),
    "Eagle": ("rgb(0, 76, 84)", "rgb(165, 172, 175)"),
    "Steeler": ("rgb(255, 182, 18)", "rgb(16, 24, 32)"),
    "49": ("rgb(170, 0, 0)", "rgb(173, 153, 93)"),
    "Seahawk": ("rgb(0, 34, 68)", "rgb(105, 190, 40)"),
    "Buccaneer": ("rgb(213, 10, 10)", "rgb(255, 121, 0)"),
    "Titan": ("rgb(75, 146, 219)", "rgb(200, 16, 46)"),
    "Commander": ("rgb(90, 20, 20)", "rgb(255, 182, 18)"),
}

COLORS = list(qualitative.Alphabet) + list(qualitative.Light24) + list(qualitative.Dark24) + list(qualitative.G10)


DEFAULT_TEMPLATE = copy.deepcopy(pio.templates["plotly_white"])

DEFAULT_TEMPLATE.update(
    {
        "layout": {
            # e.g. you want to change the background to transparent
            "paper_bgcolor": "rgba(255,255,255,1)",
            "plot_bgcolor": " rgba(0,0,0,0)",
            "font": dict(color="black"),
            "xaxis": dict(linecolor="black", showline=True, mirror=True),
            "yaxis": dict(linecolor="black", showline=True, mirror=True),
            "coloraxis": dict(colorbar=dict(outlinewidth=1, outlinecolor="black"))
        }
    }
)

DEFAULT_TEMPLATE_DARK = copy.deepcopy(DEFAULT_TEMPLATE)

DEFAULT_TEMPLATE_DARK.update(
    {
        "layout": {
            # e.g. you want to change the background to transparent
            "paper_bgcolor": "#181818",
            "plot_bgcolor": " rgba(0,0,0,0)",
            "font": dict(color="white"),
            "coloraxis": dict(colorbar=dict(outlinewidth=0)),
            "xaxis": dict(linecolor="white", showline=True),
            "yaxis": dict(linecolor="white", showline=True),

        }
    }
)


def _color_to_calpha(color: str, alpha: float = 0.2):
    color = color.split("(")[-1].split(")")[0]
    return f"rgba({color}, {alpha})"


def _plot_pca(components, labels, to_plot: tuple = (0, 1, 2)):
    fig = go.Figure()
    x, y, z = to_plot

    for idx in range(components.shape[0]):
        fig.add_trace(
            go.Scatter3d(
                x=[components[idx, x]],
                y=[components[idx, y]],
                z=[components[idx, z]],
                mode="markers",
                marker=dict(color=DEFAULT_COLORS[labels[idx][1]]),
                name=labels[idx][0]
            )
        )
    return fig


def empty_figure(annotation: str = None, font_color: str = None):
    fig = go.Figure()
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.update_xaxes(showgrid=False, showticklabels=False)
    fig.update_layout(
        margin={"t": 0, "b": 0, "r": 50},
        font=dict(
            size=16,
        ),
        yaxis=dict(zeroline=False),
        xaxis=dict(zeroline=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

    )
    if annotation is not None:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            x=0.5,
            y=0.5,
            text=annotation,
            showarrow=False,
            font=(dict(size=28))
        )
    fig.layout.template = "plotly_white"
    fig.update_layout(
        font=dict(color=font_color),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),

    )
    return fig


def plot_replicate_distribution(
        subdata: np.ndarray,
        design: pd.DataFrame,
        groups: str,
        offset: int = 0,
        colors: Iterable[str] = None
):
    """Plots the distribution of protein for each replicate

    Args:
        subdata (np.ndarray): an array of shape :code:`num samples x num_fractions`. Rows need to add up to one
        design (pd.Dataframe): the design dataframe to distinguish the groups from the samples dimension
        groups (str): which design column to use for grouping.
        offset (int): adds this offset to the fractions at the x-axis range
        colors (Iterable[str]): An iterable of color strings to use for plotting

    Returns: go.Figure

        A plotly figure containing a scatter-line per replicate.

    """
    if colors is None:
        colors = DEFAULT_COLORS
    indices = design.groupby(groups, group_keys=True).apply(lambda x: list(x.index))
    x = list(range(offset+1, subdata.shape[1] + offset+1))
    fig = go.Figure()
    names = []
    values = []
    for eidx, (name, idx) in enumerate(indices.items()):
        name = f"{groups}: {name}".ljust(15, " ")
        legend = f"legend{eidx + 1}"
        names.append(name)
        for row_idx in idx:
            rep = design.iloc[row_idx]["Replicate"]
            values.append(
                go.Scatter(
                    x=x,
                    y=subdata[row_idx],
                    marker=dict(color=colors[eidx]),
                    name=f"Replicate {rep}",
                    legend=legend,
                    line=dict(width=5)
                )
            )
    fig.add_traces(values)
    fig = _update_distribution_layout(fig, names, x, offset)
    return fig


def plot_protein_distributions(rdpmspecids, rdpmsdata: RDPMSpecData, colors, title_col: str = "RDPMSpecID", **kwargs):
    """Plots a figure containing distributions of proteins using mean, median, min and max values of replicates

        Args:
            rdpmspecids (List[any]): RDPMSpecIDs that should be plotted
            rdpmsdata (RDPMSpecData): a RDPMSpecData object containing the IDs from rdpmspecids
            colors (Iterable[str]): An iterable of color strings to use for plotting
            title_col (str): Name of a column that is present of the dataframe in rdpmsdata. Will add this column
                as a subtitle in the plot (Default: RDPMSpecID)
            vspace (float): Vertical space between subplots

        Returns: go.Figure

            A plotly figure containing a plot of the protein distribution  for each protein identified via the
            rdpmspecids.

            """
    if rdpmsdata.state.kernel_size is not None:
        i = int(rdpmsdata.state.kernel_size // 2)
    else:
        i = 0
    proteins = rdpmsdata[rdpmspecids]

    annotation = list(rdpmsdata.df[title_col][proteins])
    if "rows" in kwargs and "cols" in kwargs:
        m = kwargs["rows"]
        n = kwargs["cols"]
        del kwargs["rows"]
        del kwargs["cols"]
    else:
        n = 1
        m = len(proteins)
    if m * n < len(proteins):
        raise ValueError(f"Not enough columns ({n}) and rows ({m}) to place {len(proteins)} figures")
    fig_subplots = make_subplots(
        rows=m, cols=n,
        shared_xaxes=True,
        x_title="Fraction",
        y_title="Protein Amount [%]",
        #row_titles=list(annotation),
        **kwargs
    )
    idx = 0
    for p in range(m):
        for q in range(n):
            if idx < len(proteins):
                protein = proteins[idx]
                xref = f"x domain" if idx == 0 else f"x{idx+1} domain"
                yref = f"y domain" if idx == 0 else f"y{idx+1} domain"
                array = rdpmsdata.norm_array[protein]
                fig = plot_distribution(array, rdpmsdata.internal_design_matrix, groups="RNase", offset=i, colors=colors)
                fig_subplots.add_annotation(
                    text=annotation[idx],
                    xref=xref,
                    yref=yref,
                    x=1,
                    y=0.5,
                    yanchor="middle",
                    xanchor="left",
                    showarrow=False,
                    textangle=90
                )
                for trace in fig["data"]:
                    if idx > 0:
                        trace['showlegend'] = False
                    fig_subplots.add_trace(trace, row=p+1, col=q+1)
                idx += 1

    fig_subplots.update_layout(
        legend=fig["layout"]["legend"],
        legend2=fig["layout"]["legend2"],

    )
    return fig_subplots


def plot_distribution(subdata, design: pd.DataFrame, groups: str, offset: int = 0, colors = None, show_outliers: bool = True):
    """Plots the distribution of proteins using mean, median, min and max values of replicates

        Args:
            subdata (np.ndarray): an array of shape :code:`num samples x num_fractions`. Rows need to add up to one
            design (pd.Dataframe): the design dataframe to distinguish the groups from the samples dimension
            groups (str): which design column to use for grouping.
            offset (int): adds this offset to the fractions at the x-axis range
            colors (Iterable[str]): An iterable of color strings to use for plotting

        Returns: go.Figure

            A plotly figure containing a scatter-line for the mean, median, min and max of
            the replicates.

        """
    if colors is None:
        colors = DEFAULT_COLORS
    fig = go.Figure()
    indices = design.groupby(groups, group_keys=True).apply(lambda x: list(x.index))
    medians = []
    means = []
    errors = []
    x = list(range(offset+1, subdata.shape[1] + offset+1))
    names = []
    for eidx, (name, idx) in enumerate(indices.items()):
        name = f"{groups}: {name}".ljust(15, " ")
        legend=f"legend{eidx+1}"
        names.append(name)
        median_values = np.nanmedian(subdata[idx,], axis=0)

        mean_values = np.nanmean(subdata[idx,], axis=0)
        upper_quantile = np.nanquantile(subdata[idx,], 0.75, axis=0)
        lower_quantile = np.nanquantile(subdata[idx,], 0.25, axis=0)
        color = colors[eidx]
        a_color = _color_to_calpha(color, 0.4)
        a_color2 = _color_to_calpha(color, 0.15)
        medians.append(go.Scatter(
            x=x,
            y=median_values,
            marker=dict(color=colors[eidx]),
            name="Median",
            legend=legend,
            line=dict(width=3, dash="dot")

            ))
        means.append(go.Scatter(
            x=x,
            y=mean_values,
            marker=dict(color=colors[eidx]),
            name="Mean",
            legend=legend,
            line=dict(width=5)

        ))
        y = np.concatenate((upper_quantile, np.flip(lower_quantile)), axis=0)
        if show_outliers:
            max_values = np.nanmax(subdata[idx,], axis=0)
            min_values = np.nanmin(subdata[idx,], axis=0)
            outliers = np.concatenate((max_values, np.flip(min_values)), axis=0)
            errors.append(
                go.Scatter(
                    x=x + x[::-1],
                    y=outliers,
                    marker=dict(color=colors[eidx]),
                    name="Min-Max",
                    legend=legend,
                    fill="tonexty",
                    fillcolor=a_color2,
                    line=dict(color='rgba(255,255,255,0)')
                )
            )
        errors.append(
            go.Scatter(
                x=x + x[::-1],
                y=y,
                marker=dict(color=colors[eidx]),
                name="Q.25-Q.75",
                legend=legend,
                fill="toself",
                fillcolor=a_color,
                line=dict(color='rgba(255,255,255,0)')
            )
        )
    fig.add_traces(
        errors
    )
    fig.add_traces(
        medians + means
    )
    fig = _update_distribution_layout(fig, names, x, offset)
    return fig


def _update_distribution_layout(fig, names, x, offset):
    fig.update_layout(hovermode="x")
    fig.update_layout(xaxis_range=[x[0] - offset - 0.5, x[-1] + offset + 0.5])
    fig.update_layout(
        yaxis_title="Protein Amount [%]",
    )
    fig.update_layout(
        xaxis=dict(title="Fraction"),
        legend=dict(
            title=names[0],
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="left",
            x=0,
            itemsizing="constant"

        ),
        legend2=dict(
            title=names[1],
            orientation="h",
            yanchor="bottom",
            y=1.15,
            xanchor="left",
            x=0,
            itemsizing="constant"
        )

    )
    return fig

def plot_heatmap(distances, design: pd.DataFrame, groups: str, colors=None):
    """Plots a heatmap of the sample distances

    Args:
        distances (np.ndarray): between sample distances of shape :code:`num samples x num samples`
        design (pd.Dataframe): the design dataframe to distinguish the groups from the samples dimension
        groups (str): which design column to use for naming.
        colors (Iterable[str]): An iterable of color strings to use for plotting

    Returns: go.Figure

    """
    if colors is None:
        colors = DEFAULT_COLORS
    names = groups + design[groups].astype(str) + " " + design["Replicate"].astype(str)
    fig = go.Figure(
        data=go.Heatmap(
            z=distances,
            x=names,
            y=names,
            colorscale=colors[:2]
        )
    )
    fig.update_yaxes(showgrid=False, mirror=True, showline=True, linecolor="black", linewidth=2)
    fig.update_xaxes(showgrid=False, mirror=True, showline=True, linecolor="black", linewidth=2)
    return fig


def plot_protein_westernblots(rdpmspecids, rdpmsdata: RDPMSpecData, colors, title_col: str = "RDPMSpecID", vspace: float = 0.01):
    """Plots a figure containing a pseudo westernblot of the protein distribution.

    This will ignore smoothing kernels and plots raw mean replicate intensities.
    It will also normalize subplot colors based on the maximum intensity.

    Args:
        rdpmspecids (List[any]): RDPMSpecIDs that should be plotted
        rdpmsdata (RDPMSpecData): a RDPMSpecData object containing the IDs from rdpmspecids
        colors (Iterable[str]): An iterable of color strings to use for plotting
        title_col (str): Name of a column that is present of the dataframe in rdpmsdata. Will add this column
            as a subtitle in the plot (Default: RDPMSpecID)
        vspace (float): Vertical space between subplots

    Returns: go.Figure

        A plotly figure containing a pseudo westernblot of the protein distribution  for each protein identified via the
        rdpmspecids.

    """

    proteins = rdpmsdata[rdpmspecids]
    annotation = rdpmsdata.df[title_col][proteins].repeat(2)
    fig_subplots = make_subplots(rows=len(proteins) * 2, cols=1, shared_xaxes=True, x_title="Fraction",
                                 row_titles=list(annotation), vertical_spacing=0.0,
                                 specs=[
                                     [
                                         {
                                             "t": vspace/2 if not idx % 2 else 0.000,
                                             "b": vspace/2 if idx % 2 else 0.000
                                         }
                                     ] for idx in range(len(proteins) * 2)
                                 ]

                                 )
    for idx, protein in enumerate(proteins, 1):
        array = rdpmsdata.array[protein]
        fig = plot_barcode_plot(array, rdpmsdata.internal_design_matrix, groups="RNase", colors=colors)
        for i_idx, trace in enumerate(fig["data"]):
            fig_subplots.add_trace(trace, row=(idx * 2) + i_idx - 1, col=1)
    fig = fig_subplots
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        marker=dict(color=colors[0], symbol="square"),
        showlegend=True,
        mode="markers",
        name=fig.data[0].name

    )),
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        marker=dict(color=colors[1],  symbol="square"),
        showlegend=True,
        mode="markers",
        name=fig.data[1].name,
    ))
    fig.update_layout(
        legend=dict(
            itemsizing="constant",
            x=0,
            y=1,
            yanchor="bottom"
        )
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_yaxes(showgrid=False,  showline=True, linewidth=2, mirror=True )
    fig.update_xaxes(showticklabels=True, row=len(proteins) * 2, col=1)
    v = 1 / len(proteins)
    for idx in range(len(proteins) * 2):
        fig.update_xaxes(showgrid=False, showline=True, linewidth=2, side="top" if not idx % 2 else "bottom", row=idx + 1, col=1)
        fig.data[idx].colorbar.update(
            len=v,
            yref="paper",
            y=1 - v * (idx // 2),
            yanchor="top",
            nticks=3,
            x=1. + 0.05 if idx % 2 else 1.,
            showticklabels=True if idx % 2 else False,
            thickness=0.05,
            thicknessmode="fraction"


        )
        y_domain = f"y{idx + 1} domain" if idx != 0 else "y domain"
        if not idx % 2:
            fig["layout"]["annotations"][idx].update(y=0, yref=y_domain, x=-0.05, textangle=270)
        else:
            fig["layout"]["annotations"][idx].update(text="")



    return fig_subplots



def plot_barcode_plot(subdata, design: pd.DataFrame, groups, colors=None, vspace: float = 0.025):
    """Creates a Westernblot like plot from the mean of protein intensities

    Args:
        subdata (np.ndarray): an array of shape :code:`num samples x num_fractions`. Rows don´t need to add up to one
        design (pd.Dataframe): the design dataframe to distinguish the groups from the samples dimension
        groups (str): which design column to use for grouping.
        offset (int): adds this offset to the fractions at the x-axis range
        colors (Iterable[str]): An iterable of color strings to use for plotting
        vspace (float): vertical space between westernblots (between 0 and 1)

    Returns: go.Figure

        A figure containing two subplots of heatmaps of the non normalized intensities.

    """
    if colors is None:
        colors = DEFAULT_COLORS
    indices = design.groupby(groups, group_keys=True).apply(lambda x: list(x.index))
    fig = make_subplots(cols=1, rows=2, vertical_spacing=vspace)

    ys = []
    scale = []
    means = []
    xs = []
    names = []
    for eidx, (name, idx) in enumerate(indices.items()):
        color = colors[eidx]
        a_color = _color_to_calpha(color, 0.)
        color = _color_to_calpha(color, 1)
        scale.append([[0, a_color], [1, color]])
        name = f"{groups}: {name}"
        mean_values = np.mean(subdata[idx, ], axis=0)
        ys.append([name for _ in range(len(mean_values))])
        xs.append(list(range(1, subdata.shape[1]+1)))
        names.append(name)
        means.append(mean_values)

    m_val = max([np.max(a) for a in means])
    for idx, (x, y, z) in enumerate(zip(xs, ys, means)):

        fig.add_trace(
            go.Heatmap(
                x=x,
                y=y,
                z=z,
                colorscale=scale[idx],
                name = names[idx],
                hovertemplate='<b>Fraction: %{x}</b><br><b>Protein Intensity: %{z:.2e}</b> ',

            ),
            row=idx+1, col=1
        )
    fig.data[0].update(zmin=0, zmax=m_val)
    fig.data[1].update(zmin=0, zmax=m_val)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showgrid=False, mirror=True, showline=True, linecolor="black", linewidth=2)
    fig.update_xaxes(showgrid=False, mirror=True, showline=True, linecolor="black", linewidth=2)
    fig.update_xaxes(title="Fraction", row=2, col=1)
    fig.data[0].colorbar.update(
        len=0.5,
        yref="paper",
        y=1,
        yanchor="top"

    )
    fig.data[1].colorbar.update(
        len=0.5,
        yref="paper",
        y=0.5,
        yanchor="top",

    )


    return fig


def plot_dimension_reduction(
        rdpmspecdata: RDPMSpecData,
        colors: Iterable[str] = None,
        highlight: Iterable[Any] = None,
        show_cluster: bool = False,
        dimensions: int = 2,
        marker_max_size: int = 40,
        second_bg_color: str = "white",
        bubble_legend_color: str = "black",
        legend_start: float = 0.2,
        legend_spread: float = 0.1,
        title_col: str = None,
):
    """

    Args:
        rdpmspecdata (RDPMSpecData): A :class:`~RDPMSpecIdentifier.datastructures.RDPMSpecData` object where distances
            are calculated and the array is normalized already.
        colors (Iterable[str]): An iterable of color strings to use for plotting
        highlight (Iterable[Any]): RDPMSpecIDs to highlight in the plot
        show_cluster (bool): If set to true it will show clusters in different colors.
            (Only works if rdpmspecdata is clustered)
        dimensions (int): Either 2 or 3. 2 will produce a plot where the mean distance axis is represented via a marker
            size. If 3, it will add another axis and return a three-dimensional figure
        marker_max_size (int): maximum marker size for highest mean distance (This has no effect if dimensions is 3)
        second_bg_color (str): changes background color of the bubble legend (This has no effect if dimensions is 3)
        bubble_legend_color (str): color of the bubbles and text in the bubble legend
            (This has no effect if dimensions is 3)
        legend_start (float): start position of the bubble legend in relative coordinates
            (This has no effect if dimensions is 3)
        legend_spread (float): spread of the bubble legend (This has no effect if dimensions is 3)
        title_col (str): Will display names from that column in the rdpmspecdata for highlighted proteins
            (This has no effect if dimensions is 3)

    Returns: go.Figure()

    """
    colors = COLORS + list(colors)
    if highlight is not None:
        highlight = rdpmspecdata[highlight]
    if show_cluster:
        clusters = rdpmspecdata.df["Cluster"]
    else:
        clusters = None

    if dimensions == 2:

        fig = _plot_dimension_reduction_result2d(
            rdpmspecdata,
            colors,
            clusters,
            highlight,
            marker_max_size,
            second_bg_color,
            bubble_legend_color,
            legend_start,
            legend_spread,
            title_col
        )
    elif dimensions == 3:
        fig = _plot_dimension_reduction_result3d(
                rdpmspecdata,
                colors=colors,
                clusters=clusters,
                highlight=highlight
        )
    else:
        raise ValueError("Unsupported dimensionality")
    return fig


def _plot_dimension_reduction_result3d(rdpmspecdata, colors=None, clusters=None, highlight=None):
    embedding = rdpmspecdata.current_embedding

    fig = go.Figure()
    clusters = np.full(embedding.shape[0], -1) if clusters is None else clusters

    n_cluster = int(np.nanmax(clusters)) + 1
    mask = np.ones(embedding.shape[0], dtype=bool)
    hovertext = rdpmspecdata.df.index.astype(str) + ": " + rdpmspecdata.df["RDPMSpecID"].astype(str)
    data = rdpmspecdata.df["Mean Distance"].to_numpy()

    if highlight is not None and len(highlight) > 0:
        indices = np.asarray([rdpmspecdata.df.index.get_loc(idx) for idx in highlight])
        mask[indices] = 0
    if n_cluster > len(colors)-2:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            x=0.5,
            y=0.5,
            text="Too Many Clusters<br> Will not show all<br>Please adjust cluster Settings",
            showarrow=False,
            font=(dict(size=28))
        )
    if np.any(clusters == -1):
        c_mask = mask & (clusters == -1)
        fig.add_trace(go.Scatter3d(
            x=embedding[c_mask, :][:, 0],
            y=embedding[c_mask, :][:, 1],
            z=data[c_mask],
            mode="markers",
            hovertext=hovertext[c_mask],
            marker=dict(color=colors[-2], size=4),
            name=f"Not Clustered",
        ))
        nmask = ~mask & (clusters == -1)
        fig.add_trace(
            go.Scatter3d(
                x=embedding[nmask, :][:, 0],
                y=embedding[nmask, :][:, 1],
                z=data[nmask],
                mode="markers",
                hovertext=hovertext[nmask],
                marker=dict(color=colors[-2], size=8, line=dict(color=colors[-1], width=4)),
                name="Not Clustered",

        )
        )
    for color_idx, cluster in enumerate(range(min(n_cluster, len(colors)-2))):
        c_mask = mask & (clusters == cluster)
        fig.add_trace(go.Scatter3d(
            x=embedding[c_mask, :][:, 0],
            y=embedding[c_mask, :][:, 1],
            z=data[c_mask],
            mode="markers",
            hovertext=hovertext[c_mask],
            marker=dict(color=colors[color_idx], size=4),
            name=f"Cluster {cluster}"
        ))
        nmask = ~mask & (clusters == cluster)
        fig.add_trace(
            go.Scatter3d(
                x=embedding[nmask, :][:, 0],
                y=embedding[nmask, :][:, 1],
                z=data[nmask],
                mode="markers",
                hovertext=hovertext[nmask],
                marker=dict(color=colors[color_idx], size=8, line=dict(color=colors[-1], width=4)),
                name=f"Cluster {cluster}"
            )
        )


    fig.update_layout(
        scene=go.layout.Scene(
            xaxis=go.layout.scene.XAxis(title=f"relative fraction shift"),
            yaxis=go.layout.scene.YAxis(title=f"relative distribution change"),
            zaxis=go.layout.scene.ZAxis(title=f"Mean Distance"),
        )

    )
    return fig


def update_bubble_legend(fig, legend_start: float = 0.2, legend_spread: float = 0.1, second_bg_color: str = None, bubble_legend_color: str = None):
    xloc = [legend_start + idx * legend_spread for idx in range(3)]
    fig.data[0].x = xloc
    annos = [annotation for annotation in fig.layout.annotations if annotation.text != "Mean Distance"]
    if second_bg_color is not None:
        fig.update_shapes(fillcolor=second_bg_color)
    for idx, annotation in enumerate(annos):
        annotation.update(
            x=xloc[idx] + 0.02 + idx * 0.02 / 3,
        )
    if bubble_legend_color is not None:
        fig.data[0].update(marker=dict(line=dict(color=bubble_legend_color)))
    return fig


def _plot_dimension_reduction_result2d(rdpmspecdata: RDPMSpecData, colors=None, clusters=None,
                                       highlight=None, marker_max_size: int = 40, second_bg_color: str = "white",
                                       bubble_legend_color: str = "black", legend_start: float = 0.2, legend_spread: float = 0.1,
                                       sel_column = None
                                       ):
    embedding = rdpmspecdata.current_embedding
    displayed_text = rdpmspecdata.df["RDPMSpecID"] if sel_column is None else rdpmspecdata.df[sel_column]
    fig = make_subplots(rows=2, cols=1, row_width=[0.85, 0.15], vertical_spacing=0.0)
    hovertext = rdpmspecdata.df.index.astype(str) + ": " + rdpmspecdata.df["RDPMSpecID"].astype(str)
    clusters = np.full(embedding.shape[0], -1) if clusters is None else clusters
    n_cluster = int(np.nanmax(clusters)) + 1
    mask = np.ones(embedding.shape[0], dtype=bool)
    data = rdpmspecdata.df["Mean Distance"]
    desired_min = 1
    min_data, max_data = np.nanmin(data), np.nanmax(data)

    marker_size = desired_min + (data - min_data) * (marker_max_size - desired_min) / (max_data - min_data)
    marker_size[np.isnan(marker_size)] = 1
    min_x = np.nanmin(embedding[:, 0])
    min_y = np.nanmin(embedding[:, 1])
    max_x = np.max(embedding[:, 0])
    max_y = np.max(embedding[:, 1])
    fig.add_shape(type="rect",
                  x0=-2, y0=-2, x1=2, y1=2,
                  fillcolor=second_bg_color,
                  layer="below"
                  )
    circles = np.asarray([0.3, 0.6, 1.]) * max_data
    legend_marker_sizes = desired_min + (circles - min_data) * (marker_max_size - desired_min) / (max_data - min_data)
    xloc = [legend_start + idx * legend_spread for idx in range(3)]
    fig.add_trace(
        go.Scatter(
            x=xloc,
            y=np.full(len(xloc), 0.5),
            mode="markers",
            marker=dict(color="rgba(0,0,0,0)", line=dict(color=bubble_legend_color, width=1),
                        size=legend_marker_sizes),
            name=f"Size 100",
            showlegend=False,
            hoverinfo='skip',

        ),
        row=1,
        col=1

    )
    for idx, entry in enumerate(circles):

        fig.add_annotation(
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="middle",
            x=xloc[idx] + 0.02 + idx * 0.02 / 3,
            y=0.5,
            text=f"{entry:.1f}",
            showarrow=False,
            font=(dict(size=16)),
            row=1,
            col=1
        )
    fig.add_annotation(
        xref="x",
        yref="y",
        xanchor="left",
        yanchor="middle",
        x=0.01,
        y=0.5,
        text="Mean Distance",
        showarrow=False,
        font=(dict(size=18)),
        row=1,
        col=1
    )


    if highlight is not None and len(highlight) > 0:
        indices = np.asarray([rdpmspecdata.df.index.get_loc(idx) for idx in highlight])
        mask[indices] = 0

    if n_cluster > len(colors)-2:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="middle",
            x=0.5,
            y=0.5,
            text="Too Many Clusters<br> Will not show all<br>Please adjust cluster Settings",
            showarrow=False,
            font=(dict(size=28)),
            row=2,
            col=1
        )

    if np.any(clusters == -1):
        c_mask = mask & (clusters == -1)
        fig.add_trace(go.Scatter(
            x=embedding[c_mask, :][:, 0],
            y=embedding[c_mask, :][:, 1],
            mode="markers",
            hovertext=hovertext[c_mask],
            marker=dict(color=colors[-2], size=marker_size[c_mask]),
            name=f"Not Clustered",
        ),
            row=2,
            col=1
        )
        nmask = ~mask & (clusters == -1)
        fig.add_trace(
            go.Scatter(
                x=embedding[nmask, :][:, 0],
                y=embedding[nmask, :][:, 1],
                mode="markers+text",
                text=displayed_text[nmask],
                hovertext=hovertext[nmask],
                marker=dict(color=colors[-2], size=marker_size[nmask], line=dict(color=colors[-1], width=4)),
                name="Not Clustered",

        ),
            row=2,
            col=1
        )
    for color_idx, cluster in enumerate(range(min(n_cluster, len(colors)-2))):
        c_mask = mask & (clusters == cluster)
        fig.add_trace(go.Scatter(
            x=embedding[c_mask, :][:, 0],
            y=embedding[c_mask, :][:, 1],
            mode="markers",
            hovertext=hovertext[c_mask],
            marker=dict(color=colors[color_idx], size=marker_size[c_mask]),
            name=f"Cluster {cluster}"
        ),
            row=2,
            col=1
        )
        nmask = ~mask & (clusters == cluster)
        fig.add_trace(
            go.Scatter(
                x=embedding[nmask, :][:, 0],
                y=embedding[nmask, :][:, 1],
                mode="markers",
                hovertext=hovertext[nmask],
                marker=dict(color=colors[color_idx], size=marker_size[nmask], line=dict(color=colors[-1], width=4)),
                name=f"Cluster {cluster}"
            ),
            row=2,
            col=1
        )
    fig.update_layout(
        legend=dict(
            title="Clusters",
            yanchor="top",
            yref="paper",
            y=0.85,

        ),
        margin=dict(r=0, l=0)
    )

    fig.update_layout(
        xaxis2=dict(title="relative fraction shift"),
        yaxis2=dict(title="relative distribution change"),
        yaxis=dict(range=[0, 1], showgrid=False, showline=False, showticklabels=False, zeroline=False, ticklen=0, fixedrange=True),
        xaxis=dict(range=[0, 1], showgrid=False, showline=False, showticklabels=False, zeroline=False, ticklen=0, fixedrange=True),
        legend={'itemsizing': 'constant'},
    )
    return fig



if __name__ == '__main__':
    from RDPMSpecIdentifier.datastructures import RDPMSpecData
    df = pd.read_csv("../testData/testFile.tsv", sep="\t", index_col=0)

    design = pd.read_csv("../testData/testDesign.tsv", sep="\t")
    df.index = df.index.astype(str)
    rdpmspec = RDPMSpecData(df, design, logbase=2)
    rdpmspec.normalize_array_with_kernel(kernel_size=3)
    array = rdpmspec.norm_array
    design = rdpmspec.internal_design_matrix

    fig = plot_replicate_distribution(array[0], design, "RNase")
    fig.show()


