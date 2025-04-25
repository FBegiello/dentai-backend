from typing import Any, Iterable

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id: Any

    def to_dict(
        self,
        columns: Iterable[str] | None = None,
        exclude: list[str] | None = None,
    ):
        model_cols = [
            column.key for column in inspect(self).mapper.column_attrs  # type: ignore
        ]
        if not columns:
            columns = model_cols

        if not exclude:
            exclude = []

        return {
            column: getattr(self, column)
            for column in columns
            if column in model_cols and column not in exclude
        }
