from typing import Any, Text

from .models import Response
from .sessions import _Data, _Params

def request(
    method: Text | bytes,
    url: Text | bytes,
    params: _Params | None = ...,
    data: Any | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def get(
    url: Text | bytes,
    params: _Params | None = ...,
    data: Any | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def options(
    url: Text | bytes,
    params: _Params | None = ...,
    data: Any | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def head(
    url: Text | bytes,
    params: _Params | None = ...,
    data: Any | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def post(
    url: Text | bytes,
    data: _Data = ...,
    json: Any | None = ...,
    params: _Params | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
) -> Response: ...
def put(
    url: Text | bytes,
    data: _Data = ...,
    params: _Params | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def patch(
    url: Text | bytes,
    data: _Data = ...,
    params: _Params | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
def delete(
    url: Text | bytes,
    params: _Params | None = ...,
    data: Any | None = ...,
    headers: Any | None = ...,
    cookies: Any | None = ...,
    files: Any | None = ...,
    auth: Any | None = ...,
    timeout: Any | None = ...,
    allow_redirects: bool = ...,
    proxies: Any | None = ...,
    hooks: Any | None = ...,
    stream: Any | None = ...,
    verify: Any | None = ...,
    cert: Any | None = ...,
    json: Any | None = ...,
) -> Response: ...
