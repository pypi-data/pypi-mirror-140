from typing import Any

class User:
    type: Any
    id: Any
    display_name: Any
    def __init__(self, parent: Any | None = ..., id: str = ..., display_name: str = ...) -> None: ...
    def startElement(self, name, attrs, connection): ...
    def endElement(self, name, value, connection): ...
    def to_xml(self, element_name: str = ...): ...
