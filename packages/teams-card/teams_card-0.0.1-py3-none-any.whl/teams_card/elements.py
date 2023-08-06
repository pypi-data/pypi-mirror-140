
class TextBlock:
    def __init__(self) -> None:
        super().__init__()
        self._text = ""
        self._size = "default"
        self._type = "TextBlock"

    def set_size(self, text_size) -> None:
        allowed = [
            "default",
            "small",
            "medium",
            "large",
            "extraLarge"
        ]

        if text_size in allowed:
            self._size = text_size
        else:
            raise Exception("Text Size not allowed")

    def set_text(self,text) -> None:
        # TODO Add validation based on specification
        self._text = text

    @staticmethod
    def make_text(text):
        # TODO Add more parameters for caller
        text_block = TextBlock()
        text_block.set_text(text)
        return text_block
