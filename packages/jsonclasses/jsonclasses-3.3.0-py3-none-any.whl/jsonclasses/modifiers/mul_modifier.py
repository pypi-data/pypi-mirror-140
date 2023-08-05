"""module for mul modifier."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Callable
from .modifier import Modifier
if TYPE_CHECKING:
    from ..ctx import Ctx
    from ..types import Types

class MulModifier(Modifier):
    """Mul modifier muls number value."""

    def __init__(self, by: int | float | Callable | Types):
        self.by = by

    def transform(self, ctx: Ctx) -> Any:
        return self.resolve_param(self.by, ctx) * ctx.val if type(ctx.val) is int or type(ctx.val) is float else ctx.val
