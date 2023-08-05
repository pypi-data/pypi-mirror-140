"""module for positive validator."""
from __future__ import annotations
from typing import TYPE_CHECKING
from ..excs import ValidationException
from .validator import Validator
if TYPE_CHECKING:
    from ..ctx import Ctx


class PositiveValidator(Validator):
    """Positive validator marks value valid for large than zero."""

    def validate(self, ctx: Ctx) -> None:
        if ctx.val is None:
            return ctx.val
        if ctx.val <= 0:
            kp = '.'.join([str(k) for k in ctx.keypathr])
            v = ctx.val
            raise ValidationException(
                {kp: f'Value \'{v}\' at \'{kp}\' should be positive.'},
                ctx.root
            )
