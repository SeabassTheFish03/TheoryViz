__all__ = [
    "ProcessText",
    "TuringTape"
]

from manim.animation.composition import AnimationGroup
from manim.animation.creation import Unwrite
from manim.animation.transform import FadeToColor
from manim.mobject.text.text_mobject import Text
from manim.mobject.types.vectorized_mobject import VGroup, VDict


class ProcessText(Text):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(text, **kwargs)

        if ' ' in text:
            print("Warning, the rendering engine does not play well with whitespace. Consider replacing with a different character, like _ (underscore)")

        self.textptr = 0

        # The shadow that's left behind after the unwrites
        self.add(Text(text, color=0x333333))

    def peek_next_letter(self) -> str:
        return self.original_text[self.textptr]

    def increment_letter(self) -> None:
        self.textptr += 1

    def RemoveOneCharacter(self):
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
        self.index = 0
        self.mobj = VDict({
            "boxes": VGroup(),
            "indicator": None,  # Implemented below
            "letters": VGroup()
        })
