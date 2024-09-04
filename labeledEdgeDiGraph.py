__all__ = {
    "LabeledEdgeDiGraph"
}

import numpy as np

from manim.mobject.graph import DiGraph
from manim.mobject.geometry.arc import CurvedArrow, Dot, Annulus, LabeledDot
from manim.mobject.geometry.labeled import LabeledLine
from manim.mobject.geometry.line import Arrow
from manim.mobject.geometry.shape_matchers import BackgroundRectangle, SurroundingRectangle
from manim.mobject.text.tex_mobject import MathTex
from manim.mobject.types.vectorized_mobject import VGroup, VDict
from manim.animation.indication import Indicate

from copy import copy, deepcopy

from utils import angle_between


class LabeledEdgeDiGraph(DiGraph):
    """An extension of the Directed Graph (DiGraph) which supports labels on the edges,
    up to two edges between the same two vertices, and edges which start and end on the
    same vertex.


    .. note::

        In contrast to undirected graphs, the order in which vertices in a given
        edge are specified is relevant here.

    See also
    --------

    :class:`.DiGraph`

    Parameters
    ----------

    vertices
        A list of vertices. Must be hashable elements.

    edges
        A list of edges, specified as tuples ``(u, v)`` where both ``u``
        and ``v`` are vertices.

        Now supported: Self-looping edges (written ``(u, u)``) and multi-edges
        (where both ``(u, v)`` and ``(v, u)`` are present and shown)
    labels
        Controls whether or not vertices are labeled. If ``False`` (the default),
        the vertices are not labeled; if ``True`` they are labeled using their
        names (as specified in ``vertices``) via :class:`~.MathTex`. Alternatives,
        custom labels can be specified by passing a dictionary whose keys are
        the vertices, and whose values are the corresponding vertex labels
        (rendered via, e.g., :class:`~.Text` or :class:`~.Tex`).
    label_fill_color
        Sets the fill color of the default labels generated when ``labels``
        is set to ``True``. Has no effect for other values of ``labels``. Defaults
        to black (0x000000).
    layout
        Either one of ``"spring"``, ``"circular"``, ``"kamada_kawai"`` (the default),
        ``"planar"``, ``"random"``, ``"shell"``, ``"spectral"``, ``"spiral"``, ``"tree"``, and ``"partite"``
        for automatic vertex positioning primarily using ``networkx``
        (see `their documentation <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`_
        for more details), a dictionary specifying a coordinate (value)
        for each vertex (key) for manual positioning, or a .:class:`~.LayoutFunction` with a user-defined automatic layout.
    layout_config
        Only for automatic layouts. A dictionary whose entries
        are passed as keyword arguments to the named layout or automatic layout function
        specified via ``layout``.
        The ``tree`` layout also accepts a special parameter ``vertex_spacing``
        passed as a keyword argument inside the ``layout_config`` dictionary.
        Passing a tuple ``(space_x, space_y)`` as this argument overrides
        the value of ``layout_scale`` and ensures that vertices are arranged
        in a way such that the centers of siblings in the same layer are
        at least ``space_x`` units apart horizontally, and neighboring layers
        are spaced ``space_y`` units vertically.
    layout_scale
        The scale of automatically generated layouts: the vertices will
        be arranged such that the coordinates are located within the
        interval ``[-scale, scale]``. Some layouts accept a tuple ``(scale_x, scale_y)``
        causing the first coordinate to be in the interval ``[-scale_x, scale_x]``,
        and the second in ``[-scale_y, scale_y]``. Default: 2.
    vertex_type
        The mobject class used for displaying vertices in the scene.
    vertex_config
        Either a dictionary containing keyword arguments to be passed to
        the class specified via ``vertex_type``, or a dictionary whose keys
        are the vertices, and whose values are dictionaries containing keyword
        arguments for the mobject related to the corresponding vertex.

        Reserved Key: "flags"; Value is None|string[]
        You can use flags to enable special features of the vertex useful for DFAs.

        Possible Flags:
            "f": Final State. The state is a final state and has a small ring drawn around it.
            "i": Initial State. The state is an initial state and has an arrow pointing into it.
            "c": Current State. The state is the current state and is colored yellow. This will
                be configurable in the future.
    vertex_mobjects
        A dictionary whose keys are the vertices, and whose values are
        mobjects to be used as vertices. Passing vertices here overrides
        all other configuration options for a vertex.
    edge_type
        The mobject class used for displaying edges in the scene.
    edge_config
        Either a dictionary containing keyword arguments to be passed
        to the class specified via ``edge_type``, or a dictionary whose
        keys are the edges, and whose values are dictionaries containing
        keyword arguments for the mobject related to the corresponding edge.
        You can further customize the tip by adding a ``tip_config`` dictionary
        for global styling, or by adding the dict to a specific ``edge_config``.

        Reserved for Labels: {(u, v): {"label" = <label>}}:
            Each edge accepts a label under the label key inside its individual config
            dictionary.
    """

    def __init__(
        self,
        vertices,
        edges,
        labels=False,
        label_fill_color="black",
        layout="kamada_kawai",
        layout_scale=2,
        layout_config=None,
        vertex_type=Dot,
        vertex_config=None,
        vertex_mobjects=None,
        edge_type=LabeledLine,
        edge_config=None,
    ):
        # WARN: There used to be "root_vertex" and "partitions" params in this
        # constructor which were passed directly into super.__init__() below.
        # Looking at the current Manim GitHub (1 SEP 2024) I can't see any
        # mention of these, so I took them out. However, if something breaks,
        # this could be a reason why.
        # TODO: Update or remove above warning when answer is found.

        if isinstance(labels, dict):
            self._labels = labels
        elif isinstance(labels, bool):
            if labels:
                self._labels = {v: MathTex(
                    v, fill_color=label_fill_color) for v in vertices}
            else:
                self._labels = dict()

        if self._labels and vertex_type is Dot:
            vertex_type = LabeledDot

        self.common_vertex_config = dict()
        if vertex_mobjects is None:
            vertex_mobjects = dict()
        else:
            for key, value in vertex_config.items():
                if key not in vertices:
                    self.common_vertex_config[key] = value

        if vertex_config is not None:
            self.flags = {v: vertex_config[v].pop(
                "flags") for v in vertex_config}

        self._vertex_config = {
            v: vertex_config.get(
                v, copy(self.common_vertex_config)
            ) for v in vertices
        }

        for v, label in self._labels.items():
            self._vertex_config[v]["label"] = label

        vertex_mobjects = {v: vertex_type(
            **self._vertex_config[v]) for v in vertices}

        vertex_mobjects = {v: VDict({
            "base": deepcopy(vertex),
            "accessories": VGroup()
        }) for v, vertex in vertex_mobjects.items()}

        super().__init__(
            vertices,
            edges,
            labels,
            label_fill_color,
            layout,
            layout_scale,
            layout_config,
            vertex_type,
            vertex_config,
            vertex_mobjects,
            edge_type,
            edge_config,
        )
        self.layout_scale = layout_scale

        self._redraw_vertices()

    def get_vcenter(self):
        centers = [vertex["base"].get_center() for vertex in self.vertices.values()]
        return np.average(np.array(centers), axis=0)

    def _populate_edge_dict(self, edges, edge_type):
        if (e_type := edge_type.__name__) != "LabeledLine":
            err_msg = "Unsupported edge type: " + e_type + ". Use LabeledLine"
            raise TypeError(err_msg)

        tmp_edge_conf = deepcopy(self._edge_config)

        self.edges = dict()
        for (u, v) in edges:
            if u != v:
                if (v, u) in edges:
                    vec1 = self[v].get_center() - self[u].get_center()
                    vec2 = np.cross(vec1, np.array([0, 0, 1]))

                    length = np.linalg.norm(vec2)
                    offset = 0.1 * vec2 / length
                else:
                    offset = np.array([0, 0, 0])

                edge_label = tmp_edge_conf[(u, v)].pop("label", "f")
                if edge_label == "":
                    edge_label = "\\epsilon"
                self.edges[(u, v)] = edge_type(
                    label=edge_label,
                    start=self[u],
                    end=self[v],
                    **tmp_edge_conf[(u, v)]
                ).shift(offset)
            else:
                edge_label = tmp_edge_conf[(u, u)].pop("label", "g")

                between = angle_between(self[u].get_center(
                ) - self.get_vcenter(), np.array([1, 0, 0]))
                if self[u].get_center()[1] < self.get_vcenter()[1]:
                    between *= -1

                loop = CurvedArrow(
                    start_point=self[u].get_top(),
                    end_point=self[u].get_bottom(),
                    angle=-4,
                    z_index=-1,
                    **tmp_edge_conf[(u, u)]
                )
                label_mobject = MathTex(
                    edge_label,
                    fill_color="white",
                    font_size=40,
                ).move_to(loop.get_center()).shift(
                    np.array([0.5, 0, 0])
                ).rotate(-1 * between)

                label_background = BackgroundRectangle(
                    label_mobject,
                    buff=0.05,
                    color="black",
                    fill_opacity=1,
                    stroke_width=0.5,
                ).rotate(-1 * between)
                label_frame = SurroundingRectangle(
                    label_mobject,
                    buff=0.05,
                    color="white",
                    stroke_width=0.5
                ).rotate(-1 * between)

                label_group = VGroup(
                    loop,
                    label_frame,
                    label_background,
                    label_mobject
                )
                self.edges[(u, u)] = VGroup(label_group).rotate(
                    between,
                    about_point=self[u].get_center()
                )

        for (u, v), edge in self.edges.items():
            try:
                if isinstance(edge, LabeledLine):
                    edge.add_tip(**self._tip_config[(u, v)])
            except TypeError:
                print("Unexpected tip type!")
                print(self._tip_config)
                exit()

    def update_edges(self, graph):
        tmp_edge_conf = deepcopy(self._edge_config)

        for (u, v), edge in graph.edges.items():
            if u != v:
                # Handling arrows going both ways
                if (v, u) in self.edges:
                    vec1 = self.vertices[v]["base"].get_center() -\
                        self.vertices[u]["base"].get_center()
                    vec2 = np.cross(vec1, np.array([0, 0, 1]))

                    length = np.linalg.norm(vec2)
                    offset = 0.1 * vec2 / length
                else:
                    offset = np.array([0, 0, 0])

                # Housekeeping
                edge_type = type(edge)
                tip = edge.pop_tips()[0]
                edge_label = tmp_edge_conf[(u, v)].pop(
                    "label", "update_edges fail")
                if edge_label == "":
                    edge_label = "\\epsilon"

                new_edge = edge_type(
                    label=edge_label,
                    start=self.vertices[u]["base"],
                    end=self.vertices[v]["base"],
                    **tmp_edge_conf[(u, v)]
                ).shift(offset)

                edge.become(new_edge)
                edge.add_tip(tip)
            else:
                edge_label = tmp_edge_conf[(u, u)].pop(
                    "label", "update_edges fail")

                between = angle_between(self.vertices[u]["base"].get_center(
                ) - self.get_vcenter(), np.array([1, 0, 0]))
                if self[u].get_center()[1] < self.get_vcenter()[1]:
                    between *= -1

                loop = CurvedArrow(
                    start_point=self.vertices[u]["base"].get_top(),
                    end_point=self.vertices[u]["base"].get_bottom(),
                    angle=-4,
                    z_index=-1,
                    **tmp_edge_conf[(u, u)]
                )
                label_mobject = MathTex(
                    edge_label,
                    fill_color="white",
                    font_size=40,
                ).move_to(
                    loop.get_center()
                ).shift(np.array([0.5, 0, 0])).rotate(-1 * between)

                label_background = BackgroundRectangle(
                    label_mobject,
                    buff=0.05,
                    color="black",
                    fill_opacity=1,
                    stroke_width=0.5,
                ).rotate(-1 * between)
                label_frame = SurroundingRectangle(
                    label_mobject,
                    buff=0.05,
                    color="white",
                    stroke_width=0.5
                ).rotate(-1 * between)

                label_group = VGroup(
                    loop,
                    label_frame,
                    label_background,
                    label_mobject
                )
                edge.become(label_group).rotate(
                    between,
                    about_point=self.vertices[u]["base"].get_center()
                )

    def _redraw_vertices(self):
        for v in self.vertices:
            if "f" in self.flags[v]:
                ring = Annulus(
                    inner_radius=self.vertices[v]["base"].width +
                    0.1 * self.layout_scale / 2,
                    outer_radius=self.vertices[v]["base"].width +
                    0.2 * self.layout_scale / 2,
                    z_index=-1,
                    fill_color="white"
                ).move_to(
                    self.vertices[v]["base"].get_center()
                ).scale(1 / self.layout_scale)

                self.vertices[v]["accessories"].add(ring)

            if "i" in self.flags[v]:
                ray = self.vertices[v]["base"].get_center() - \
                    self.get_vcenter()
                start_arrow = Arrow(
                    start=ray * 2,
                    end=ray * 1.05,
                    fill_color="white",
                    stroke_width=20
                )
                self.vertices[v]["accessories"].add(start_arrow)

            if "c" in self.flags[v]:
                for item in self.vertices[v]["base"]:
                    if isinstance(item, Dot):
                        item.set_color("yellow")
                    else:
                        item.set_color("black")
            else:
                for item in self.vertices[v]["base"]:
                    if isinstance(item, Dot):
                        item.set_color("white")
                    else:
                        item.set_color("black")

    def add_flag(self, state, flag):
        if state in self.vertices:
            self.flags[state].append(flag)
        self._redraw_vertices()

    def remove_flag(self, state, flag):
        if state in self.vertices:
            if flag in self.flags[state]:
                self.flags[state].remove(flag)
        self._redraw_vertices()

    def _arrow_from(self, edge):
        return Arrow(
            z_index=-2,
            stroke_width=15
        ).put_start_and_end_on(*edge.get_start_and_end())

    def transition_animation(self, start, end):
        if (start, end) not in self.edges:
            raise Exception(f"Transition does not exist: {(start, end)}")

        if start == end:
            return Indicate(self.edges[(start, end)].copy())
        else:
            return Indicate(self._arrow_from(self.edges[(start, end)]))

    def __repr__(self):
        return f"Directed Graph with labeled edges with\
            {len(self.vertices)} vertices and {len(self.edges)} edges"
