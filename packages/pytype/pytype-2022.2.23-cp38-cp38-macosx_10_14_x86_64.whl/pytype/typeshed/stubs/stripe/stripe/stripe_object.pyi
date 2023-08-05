import json
from typing import Any

from stripe import api_requestor as api_requestor

class StripeObject(dict[Any, Any]):
    class ReprJSONEncoder(json.JSONEncoder):
        def default(self, obj): ...

    def __init__(
        self,
        id: Any | None = ...,
        api_key: Any | None = ...,
        stripe_version: Any | None = ...,
        stripe_account: Any | None = ...,
        last_response: Any | None = ...,
        **params,
    ) -> None: ...
    @property
    def last_response(self): ...
    def update(self, update_dict): ...
    def __setattr__(self, k, v): ...
    def __getattr__(self, k): ...
    def __delattr__(self, k): ...
    def __setitem__(self, k, v) -> None: ...
    def __getitem__(self, k): ...
    def __delitem__(self, k) -> None: ...
    def __reduce__(self): ...
    @classmethod
    def construct_from(
        cls, values, key, stripe_version: Any | None = ..., stripe_account: Any | None = ..., last_response: Any | None = ...
    ): ...
    api_key: Any
    stripe_version: Any
    stripe_account: Any
    def refresh_from(
        self,
        values,
        api_key: Any | None = ...,
        partial: bool = ...,
        stripe_version: Any | None = ...,
        stripe_account: Any | None = ...,
        last_response: Any | None = ...,
    ) -> None: ...
    @classmethod
    def api_base(cls) -> None: ...
    def request(self, method, url, params: Any | None = ..., headers: Any | None = ...): ...
    def request_stream(self, method, url, params: Any | None = ..., headers: Any | None = ...): ...
    def to_dict(self): ...
    def to_dict_recursive(self): ...
    @property
    def stripe_id(self): ...
    def serialize(self, previous): ...
    def __copy__(self): ...
    def __deepcopy__(self, memo): ...
