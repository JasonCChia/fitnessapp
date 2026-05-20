from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnDefinition:
    name: str
    mysql_type: str
    nullable: bool = False
    default: str | None = None
    comment: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "mysql_type": self.mysql_type,
            "nullable": self.nullable,
            "default": self.default,
            "comment": self.comment,
        }


@dataclass(frozen=True)
class TableDefinition:
    name: str
    description: str
    columns: tuple[ColumnDefinition, ...]
    primary_key: tuple[str, ...]
    unique_keys: tuple[tuple[str, ...], ...] = ()
    indexes: tuple[tuple[str, ...], ...] = ()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "columns": [column.to_dict() for column in self.columns],
            "primary_key": list(self.primary_key),
            "unique_keys": [list(key) for key in self.unique_keys],
            "indexes": [list(index) for index in self.indexes],
        }
