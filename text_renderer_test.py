from manim._config import tempconfig

from manim.scene.scene import Scene
from manim.mobject.text.text_mobject import Text
from manim.animation.creation import Unwrite


class TextSceneTest(Scene):
    def construct(self):
        text = Text('I am a line of Text!')
        text.id = 'a'
        self.add(text)

        for i in range(len(text)):
            self.play(Unwrite(text[i]))
        self.wait(1)

    def get_mobject_by_id(self, id):
        for mobject in self.mobjects:
            if hasattr(mobject, 'id'):
                if mobject.id == id:
                    return mobject
        return None


if __name__ == "__main__":
    with tempconfig({"quality": "low_quality", "preview": True}):
        scene = TextSceneTest()
        scene.render()
