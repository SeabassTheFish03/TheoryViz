__all__ = {
    "FiniteAutomaton"
}

# Standard Lib
from copy import deepcopy
import tomllib

# Dependencies
import numpy as np

# Manim
from manim.mobject.graph import DiGraph
from manim.mobject.geometry.arc import CurvedArrow, Dot, Annulus, LabeledDot
from manim.mobject.geometry.labeled import LabeledLine
from manim.mobject.geometry.line import Arrow
from manim.mobject.geometry.shape_matchers import BackgroundRectangle, SurroundingRectangle
from manim.mobject.text.tex_mobject import MathTex
from manim.mobject.types.vectorized_mobject import VGroup, VDict
from manim.animation.indication import Indicate

# TheoryViz Internal
from utils import angle_between


class FiniteAutomaton(DiGraph):
    """
    A renderer for various types of finite Automata.
    An extension of the Directed Graph (DiGraph) which supports labels on the edges,
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
    config
        A dict containing all the configuration keys/values. Every key must be
        accounted for, but the existing config.toml file is always up to date
        and contains all the keys.
    flags
        The flags dictionary has keys corresponding to specific vertices. Not
        all vertices need be included. To pass multiple flags, put them together
        in a string. For example, a final state that is also the current state
        would have a flag string of "fc".
        Supported flags:
            'f': The vertex is a [f]inal state
            'c': The vertex is the [c]urrent state (one allowed)
            'i': The vertex is the [i]nitial state (one allowed)
    """

    def _vertex_config_from_bigconfig(self, config: dict) -> dict:
        # These keys in config.toml map to these keys in Manim
        toml_to_mobject: dict[str, str] = {
            "vertex_color": "color",
            "vertex_text_color": "label_fill_color",
            "vertex_stroke_color": "stroke_color"
        }
        # These are the kwargs that Manim understands and affect the appearance of the vertex
        mobject_keys: list[str] = [
            # From LabeledDot
            "label",
            "radius",
            # From Dot
            "point",
            "stroke_width",
            "fill_opacity",
            "color",
            # From Circle
            # From Arc
            # From TipableVMobject
            # From VMobject
            "fill_color",
            "stroke_color",
            "stroke_opacity",
            "background_stroke_color",
            "background_stroke_opacity",
            "background_stroke_width",
            "sheen_factor",
            "sheen_direction",
        ]

        vertex_config: dict = dict()
        for key, value in config.enumerate():
            # If it's in there, translate, else leave it
            key = toml_to_mobject.get(key, key)

            if key in mobject_keys:
                vertex_config.update(key, value)
        return vertex_config

    def __init__(
        self,
        vertices: list[str],
        edges: list[tuple[str, str]],
        config: dict,
        flags: dict = dict(),
        override_labels=None
    ):
        super().__init__(
            vertices,
            edges
        )

        if override_labels is not None:
            self._labels = override_labels
        else:
            self._labels = {v: MathTex(
                v, fill_color=config["vertex_text_color"]) for v in vertices
            }

        vertex_mobjects = dict()

        for v, label in self._labels.items():
            self._vertex_config[v]["label"] = label

        vertex_mobjects = {v: LabeledDot(
            **self._vertex_config[v]) for v in vertices}

        vertex_mobjects = {v: {
            "mobject":
                VDict({
                    "base": deepcopy(vertex),
                    "accessories": VGroup()
                }),
            "flags": flags.get(v, list())
        } for v, vertex in vertex_mobjects.items()}

        self.layout_scale = config["layout_scale"]

        self._redraw_vertices()

    def vcenter(self):
        """
        Gets the average position of each vertex in the graph
        """
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
                ) - self.vcenter(), np.array([1, 0, 0]))
                if self[u].get_center()[1] < self.vcenter()[1]:
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
                ) - self.vcenter(), np.array([1, 0, 0]))
                if self[u].get_center()[1] < self.vcenter()[1]:
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
                    inner_radius=self.vertices[v]["base"].width + 0.1 * self.layout_scale / 2,
                    outer_radius=self.vertices[v]["base"].width + 0.2 * self.layout_scale / 2,
                    z_index=-1,
                    fill_color="white"
                ).move_to(
                    self.vertices[v]["base"].get_center()
                ).scale(1 / self.layout_scale)

                self.vertices[v]["accessories"].add(ring)

            if "i" in self.flags[v]:
                ray = self.vertices[v]["base"].get_center() - \
                    self.vcenter()
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
