from typing import Any

__copyright__: Any
DEV_NULL: Any

def libc_ver(executable=..., lib=..., version=..., chunksize: int = ...): ...
def linux_distribution(distname=..., version=..., id=..., supported_dists=..., full_distribution_name: int = ...): ...
def dist(distname=..., version=..., id=..., supported_dists=...): ...

class _popen:
    tmpfile: Any
    pipe: Any
    bufsize: Any
    mode: Any
    def __init__(self, cmd, mode=..., bufsize: Any | None = ...): ...
    def read(self): ...
    def readlines(self): ...
    def close(self, remove=..., error=...): ...
    __del__: Any

def popen(cmd, mode=..., bufsize: Any | None = ...): ...
def win32_ver(release: str = ..., version: str = ..., csd: str = ..., ptype: str = ...) -> tuple[str, str, str, str]: ...
def mac_ver(
    release: str = ..., versioninfo: tuple[str, str, str] = ..., machine: str = ...
) -> tuple[str, tuple[str, str, str], str]: ...
def java_ver(
    release: str = ..., vendor: str = ..., vminfo: tuple[str, str, str] = ..., osinfo: tuple[str, str, str] = ...
) -> tuple[str, str, tuple[str, str, str], tuple[str, str, str]]: ...
def system_alias(system, release, version): ...
def architecture(executable=..., bits=..., linkage=...) -> tuple[str, str]: ...
def uname() -> tuple[str, str, str, str, str, str]: ...
def system() -> str: ...
def node() -> str: ...
def release() -> str: ...
def version() -> str: ...
def machine() -> str: ...
def processor() -> str: ...
def python_implementation() -> str: ...
def python_version() -> str: ...
def python_version_tuple() -> tuple[str, str, str]: ...
def python_branch() -> str: ...
def python_revision() -> str: ...
def python_build() -> tuple[str, str]: ...
def python_compiler() -> str: ...
def platform(aliased: int = ..., terse: int = ...) -> str: ...
