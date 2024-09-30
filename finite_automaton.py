__all__ = {
    "FiniteAutomaton"
}

# Standard Lib
from copy import deepcopy

# Dependencies
import numpy as np

# Manim
from manim.mobject.graph import DiGraph
from manim.mobject.geometry.arc import CurvedArrow, Annulus, LabeledDot
from manim.mobject.geometry.labeled import LabeledLine
from manim.mobject.geometry.line import Arrow
from manim.mobject.geometry.shape_matchers import BackgroundRectangle, SurroundingRectangle
from manim.mobject.text.tex_mobject import MathTex
from manim.mobject.types.vectorized_mobject import VGroup

from manim.animation.indication import Indicate


def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


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
        A list of edges, specified as tuples ``(u, v, label)`` where both ``u``
        and ``v`` are vertices.

        Now supported: Self-looping edges (written ``(u, u)``) and multi-edges
        (where both ``(u, v)`` and ``(v, u)`` are present and shown)
    visual_config
        A dict containing all the visual configuration keys/values. Every key must be
        accounted for, but the existing config.toml file is always up to date
        and contains all the keys. It's not strictly necessary to load from the toml file,
        but that is the surest way to ensure all the keys are present.
    options
        Not to be confused with visual_config, this dict modifies the content of
        the original DiGraph and affects *what* is displayed, not *how* it's displayed.

        In this dict, you can specify vertex labels via `{"vertices": {<vertex>: {"label": <display_name>}}}`,
        edge labels via `{"edges": {(<u>, <v>): {"label": <display_label>}}}`, and the flags associated with each
        vertex via `{"vertices": {<vertex>: {"flags": [flags]}}}`. If left unspeciried, the vertices will be labeled with their state names, and the edges will be labeled with their transition symbols. By default, a vertex has no flags.

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
            "vertex_stroke_color": "stroke_color",
            "vertex_radius": "radius"
        }
        # These are the kwargs that Manim understands and affect the appearance of the vertex
        mobject_keys: list[str] = [
            # From LabeledDot
            "label_fill_color",
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
        for key, value in config.items():
            # If it's in there, translate, else let it pass
            key = toml_to_mobject.get(key, key)

            if key in mobject_keys:
                vertex_config[str(key)] = value
        return vertex_config

    def _edge_config_from_bigconfig(self, config: dict) -> dict:
        toml_to_mobject: dict[str, str] = {
            "edge_color": "color",
            "edge_text_color": "label_color",
            "edge_label_position": "label_position",
            "edge_label_frame": "label_frame",
            "edge_label_frame_fill": "frame_fill_color",
            "edge_label_frame_opacity": "frame_fill_opacity",
        }

        # These are the kwargs that Manim understands and affect the appearance of the edge
        mobject_keys: list[str] = [
            # From LabeledLine
            "color",
            "label_color",
            "font_size",
            "label_position",
            "label_frame",
            "frame_fill_color",
            "frame_fill_opacity",
            # From Line
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

        edge_config: dict = dict()
        for key, value in config.items():
            # If it's in there, translate, else let it pass
            key = toml_to_mobject.get(key, key)

            if key in mobject_keys:
                edge_config[str(key)] = value
        return edge_config

    def _graph_config_from_bigconfig(self, config: dict) -> dict:
        toml_to_mobject: dict[str, str] = {
            "layout_type": "layout",
            "vertex_text_color": "label_fill_color",
        }

        # These are the kwargs that Manim understands and affect the appearance of the edge
        mobject_keys: list[str] = [
            # From GenericGraph
            "label_fill_color",
            "layout",
            "layout_scale",
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

        graph_config: dict = dict()
        for key, value in config.items():
            # If it's in there, translate, else let it pass
            key = toml_to_mobject.get(key, key)

            if key in mobject_keys:
                graph_config[str(key)] = value
        return graph_config

    def __init__(
        self,
        vertices: list[str],
        edges: list[tuple[str, str]],
        visual_config: dict,  # Expected to come straight from config.toml. Handles rest internally
        options: dict = dict()
    ) -> None:

        # Setting up the vertex config
        _vertex_config: dict = self._vertex_config_from_bigconfig(visual_config)
        _vertex_labels: dict = dict()
        _flags: dict = dict()

        # Must handle labels and flags
        if "vertices" in options:
            for vertex, opts in options["vertices"].items():
                _vertex_config[vertex] = deepcopy(opts)
                if "label" in opts:
                    del _vertex_config[vertex]["label"]
                    _vertex_labels[vertex] = opts["label"]
                if "flags" in opts:
                    _flags[vertex] = _vertex_config[vertex].pop("flags")
                else:
                    _vertex_labels[vertex] = str(vertex)

        # Setting up the edge config
        _edge_config: dict = self._edge_config_from_bigconfig(visual_config)
        _edge_labels: dict = dict()

        if "edges" in options:
            for (start, end), opts in options["edges"].items():
                _edge_config[(start, end)] = deepcopy(opts)
                if "label" in opts:
                    del _edge_config[(start, end)]["label"]
                    _edge_labels[(start, end)] = opts["label"]
                else:
                    _edge_labels[(start, end)] = str((start, end))

        _graph_config = self._graph_config_from_bigconfig(visual_config)

        # We let DiGraph (really, GenericGraph) do most of the heavy lifting.
        # When it accepts configs, it takes global options (i.e. options that apply to every vertex/edge)
        #   and override options keyed to a specific vertex/edge name (which override the global ones).
        # That's what the above was for, trimming out any specific things and making sure the input is sanitary.
        super().__init__(
            vertices,
            edges,
            vertex_type=LabeledDot,
            edge_type=LabeledLine,
            labels=_vertex_labels,  # This refers specifically to vertex labels
            vertex_config=_vertex_config,
            edge_config=_edge_config,
            **_graph_config
        )
        # Give the edges a little refresh since DiGraph isn't built
        #  for edge labels
        self.remove(*self.edges.values())
        self._repopulate_edge_dict(edges, _edge_config, _edge_labels)
        self.add(*self.edges.values())

        # We add accessories using flags, and they live on top of the vertices
        self.accessories: dict[str, VGroup] = {
            k: VGroup().move_to(v.get_center()) for k, v in self.vertices.items()
        }

    def vcenter(self) -> np.ndarray:
        """
        Gets the average position of each vertex in the graph
        """
        centers: list = [vertex.get_center() for vertex in self.vertices.values()]
        return np.average(np.array(centers), axis=0)

    # We're beholden to this function call in super().__init__()
    # This works just enough to avoid errors, then gets fixed by
    # _repopulate_edge_dict() below
    def _populate_edge_dict(
        self,
        edges: dict[(str, str), LabeledLine],
        labels: dict[(str, str), str]
    ) -> None:
        tmp_edge_conf: dict = deepcopy(self._edge_config)

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

                edge_label = tmp_edge_conf[(u, v)].pop("label", "why??")
                if edge_label == "":
                    edge_label = "\\epsilon"
                self.edges[(u, v)] = LabeledLine(
                    label=edge_label,
                    start=self[u],
                    end=self[v],
                    **tmp_edge_conf[(u, v)]
                ).shift(offset)
            else:
                edge_label = tmp_edge_conf[(u, u)].pop("label", "g")

                between = angle_between(self[u].get_center() - self.vcenter(), np.array([1, 0, 0]))
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

    def _repopulate_edge_dict(
        self,
        edges: dict[(str, str), LabeledLine],
        edge_config: dict,
        labels: dict[(str, str), str]
    ) -> None:
        self.edges = dict()
        general_edge_config = {k: v for k, v in edge_config.items() if isinstance(k, str)}
        specific_edge_config = {k: v for k, v in edge_config.items() if isinstance(k, tuple)}

        for (u, v) in edges:
            if u != v:
                this_edge_config = deepcopy(general_edge_config)
                this_edge_config.update(specific_edge_config.get((u, v), dict()))
                edge_label = labels.get((u, v), str((u, v)))

                # This is a straight edge between two different vertices
                if (v, u) in edges:
                    # We need to offset two edges between the same vertices
                    vec1 = self[v].get_center() - self[u].get_center()
                    vec2 = np.cross(vec1, np.array([0, 0, 1]))

                    length = np.linalg.norm(vec2)
                    offset = 0.1 * vec2 / length  # TODO: Make configurable?
                else:
                    offset = np.array([0, 0, 0])

                # An empty label is different from one that doesn't exist
                if edge_label == "":
                    edge_label = "\\epsilon"
                self.edges[(u, v)] = LabeledLine(
                    label=edge_label,
                    start=self[u],
                    end=self[v],
                    **this_edge_config
                ).shift(offset)
            else:
                edge_label = labels.get((u, u), str((u, u)))

                this_edge_config = deepcopy(general_edge_config)
                this_edge_config.update(specific_edge_config.get((u, v), dict()))

                between = angle_between(self[u].get_center() - self.vcenter(), np.array([1, 0, 0]))
                if self[u].get_center()[1] < self.vcenter()[1]:
                    between *= -1

                loop = CurvedArrow(
                    start_point=self[u].get_top(),
                    end_point=self[u].get_bottom(),
                    angle=-4,
                    z_index=-1,
                    color=this_edge_config["color"]
                )
                label_mobject = MathTex(
                    edge_label,
                    fill_color=this_edge_config["label_color"],
                    font_size=this_edge_config["font_size"],
                ).move_to(loop.get_center()).shift(
                    np.array([0.5, 0, 0])
                ).rotate(-1 * between)

                label_background = BackgroundRectangle(
                    label_mobject,
                    buff=0.05,
                    color=this_edge_config["frame_fill_color"],
                    fill_opacity=this_edge_config["frame_fill_opacity"],
                    stroke_width=0.5,
                ).rotate(-1 * between)
                label_frame = SurroundingRectangle(
                    label_mobject,
                    buff=0.05,
                    color=this_edge_config["label_color"],
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

        print(self.edges[('1', '1')][0][3])

    def _redraw_vertices(self) -> None:
        for vertex, opts in self.options["vertices"].items():
            if "flags" in opts and len(opts["flags"]) > 0:
                focused_flags: list[str] = opts["flags"]
                if "i" in focused_flags:
                    ray = vertex.get_center() - self.vcenter()
                    start_arrow: Arrow = Arrow(
                        start=ray * 2,
                        end=ray * 1.05,
                        fill_color="white",
                        stroke_width=20
                    )
                    self.accessories.add(start_arrow)

                if "c" in focused_flags:
                    vertex.set_color(self.visual_config["current_state_color"])
                else:
                    vertex.set_color(self.visual_config["vertex_color"])

                if "f" in focused_flags:
                    ring = Annulus(
                        inner_radius=vertex["base"].width + 0.1 * self.layout_scale / 2,
                        outer_radius=vertex["base"].width + 0.2 * self.layout_scale / 2,
                        z_index=-1,
                        fill_color="white"
                    ).move_to(
                        vertex["base"].get_center()
                    ).scale(1 / self.layout_scale)

                    self.accessories.add(ring)

    def add_flag(self, state: str, flag: str) -> None:
        if state in self.vertices:
            self.options["flags"][state].append(flag)
        self._redraw_vertices()

    def remove_flag(self, state: str, flag: str) -> None:
        if state in self.vertices:
            if flag in self.flags[state]:
                self.flags[state].remove(flag)
        self._redraw_vertices()

    def _arrow_from(self, edge: LabeledLine | CurvedArrow) -> None:
        return Arrow(
            z_index=-2,
            stroke_width=15
        ).put_start_and_end_on(*edge.get_start_and_end())

    def transition_animation(self, start: LabeledDot, end: LabeledDot) -> Indicate:
        if (start, end) not in self.edges:
            raise Exception(f"Transition does not exist: {(start, end)}")

        if start == end:
            return Indicate(self.edges[(start, end)].copy())
        else:
            return Indicate(self._arrow_from(self.edges[(start, end)]))

    def __repr__(self) -> str:
        return f"Directed Graph with labeled edges with\
            {len(self.vertices)} vertices and {len(self.edges)} edges"
