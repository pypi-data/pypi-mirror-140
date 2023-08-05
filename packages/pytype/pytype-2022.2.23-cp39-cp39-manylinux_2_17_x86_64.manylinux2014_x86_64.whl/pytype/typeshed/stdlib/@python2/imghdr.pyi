from typing import Any, BinaryIO, Callable, Protocol, Text, Union, overload

class _ReadableBinary(Protocol):
    def tell(self) -> int: ...
    def read(self, size: int) -> bytes: ...
    def seek(self, offset: int) -> Any: ...

_File = Union[Text, _ReadableBinary]

@overload
def what(file: _File, h: None = ...) -> str | None: ...
@overload
def what(file: Any, h: bytes) -> str | None: ...

tests: list[Callable[[bytes, BinaryIO | None], str | None]]
