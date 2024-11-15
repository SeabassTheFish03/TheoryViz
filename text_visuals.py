__all__ = [
    "ProcessText",
    "TuringTape"
]

from manim.animation.animation import Animation
from manim.animation.composition import AnimationGroup
from manim.animation.creation import Unwrite
from manim.animation.transform import FadeToColor
from manim.mobject.table import Table
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VDict
from manim.utils.color.core import ManimColor


class ProcessText(Text):
    """
    A Mobject which displays text being processed by a DFA, NFA, or PDA.
    Capable of animating an "Unwrite" of the first character, to correspond with a step taken by an FA.
    """

    def __init__(
        self,
        text: str,
        text_color: ManimColor = "white",
        highlight_color: ManimColor = "yellow",
        shadow_color: ManimColor = "dark_grey",
        **kwargs
    ) -> None:
        super().__init__(text, color=text_color, **kwargs)

        if ' ' in text:
            print("Warning: Whitespace does not translate well to this Mobject. Consider replacing with a different character, like _ (underscore)")

        self.textptr = 0
        self[0].set_color(highlight_color)

        # The shadow that's left behind after the unwrites
        self.add(Text(text, color=shadow_color).set_z_index(-1))

    def peek_next_letter(self) -> str:
        return self.original_text[self.textptr]

    def increment_letter(self) -> None:
        self.textptr += 1

    def RemoveOneCharacter(self):
        """
        Unwrites the character pointed to by self.textptr, leaving the shadow behind.
        ------
        Inputs:
            None
        Outputs:
            An animation of the first character unwriting. If that character is not the last letter,
            the next character in the string is highlighted
        Side Effects:
            Unwriting the first character causes it to be removed from this Mobject. Even if the animation
            is not displayed, the effect still occurs on every call.
        """
        if self.textptr < len(self.original_text) - 1:
            return AnimationGroup(
                FadeToColor(self[self.textptr + 1], color="yellow"),
                Unwrite(self[self.textptr])
            )
        else:
            return Unwrite(self[self.textptr])


class TuringTape:
    def __init__(
        self,
        text: str,
        blank_char: str = "_",
        config: dict = dict()
    ):
        self.text = text
        self.blank = blank_char  # Character representing a blank space, not shown
        self.index = 0

        self.mobj = VDict({
            "table": Table(
                [list(text)],
                element_to_mobject=Text,
                element_to_mobject_config={
                    "color": config["edge_text_color"]
                },
                line_config={
                    "color": config["table_border_color"]
                },
                include_outer_lines=True
            ),
            "indicator": VGroup()
        })
        self.mobj["indicator"] = self.mobj["table"].get_cell(
            (1, (self.index + 1) % len(self.text)),
            color=config["current_state_color"]
        )

    def animate_change_highlighted(self, new_index: int) -> Animation:
        if new_index >= len(self.text):
            raise ValueError(f"Index {new_index} out of range for text {self.text}")

        self.index = new_index
        return self.mobj["indicator"].animate.move_to(
            self.mobj["table"].get_cell((1, new_index + 1))
        )
