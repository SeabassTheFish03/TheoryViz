__all__ = [
    "ProcessText",
    "TuringTape"
]

from manim.animation.animation import Animation
from manim.animation.composition import AnimationGroup
from manim.animation.creation import Unwrite
from manim.animation.transform import FadeToColor, Transform, ReplacementTransform
from manim.mobject.geometry.polygram import Rectangle
from manim.mobject.table import Table
from manim.mobject.text.tex_mobject import MathTex
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VDict
from manim.utils.color.core import ManimColor

from automata.tm.tape import TMTape


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


class TuringTape(Table):
    def __init__(
        self,
        tape: TMTape,
        config: dict = dict(),
        highlight_color="yellow"
    ):
        self.text = "".join(list(tape.tape))
        self.blank = tape.blank_symbol
        self.index = tape.current_position

        super().__init__(
            [(list(self.text) + [self.blank])],
            element_to_mobject=Text,
            element_to_mobject_config={
                "color": config["color"]
            },
            line_config={
                "color": config["color"]
            },
            include_outer_lines=True
        )

        for element in self.get_entries():
            element.scale(config["font_size"] / 48)

        self.indicator = self.get_cell(
            (1, (self.index + 1) % len(self.text)),
            color=highlight_color
        )
        self.config = config
        self.add(self.indicator)

    def animate_update(self, changes):
        write = changes[1]
        direction = changes[2]
        if direction == "L":
            self.index -= 1 if self.index > 0 else 0
        elif direction == "R":
            self.index += 1 if self.index < len(self.text) - 1 else 0
        else:
            raise ValueError("Direction invalid")

        new_entry = Text(write).move_to(
            self.get_entries((1, self.index + 1))
        ).scale(self.config["font_size"] / 48).set_color(self.config["color"])

        if write == self.blank:
            write = " "

        return AnimationGroup(
            self.indicator.animate.move_to(
                self.get_cell((1, self.index + 1))),
            Transform(
                self.get_entries((1, self.index + 1)),
                new_entry
            )
        )
