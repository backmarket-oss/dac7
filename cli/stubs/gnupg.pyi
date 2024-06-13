from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import overload

D = TypeVar("D", bound=str | bytes)

class Crypt(Generic[D]):
    ok: bool
    data: D
    stderr: str

class ImportResult:
    stderr: str
    count: int

class GPG:
    @overload
    def encrypt(
        self,
        data: str | bytes,
        recipients: str | list[str],
        armor: Literal[True] = True,
        always_trust: bool = False,
    ) -> Crypt[str]: ...
    @overload
    def encrypt(
        self,
        data: str | bytes,
        recipients: str | list[str],
        armor: Literal[False],
        always_trust: bool = False,
    ) -> Crypt[bytes]: ...
    def list_keys(self) -> list[dict]: ...
    def import_keys(self, key_data: str | bytes, extra_args: list[str] | None = None) -> ImportResult: ...
