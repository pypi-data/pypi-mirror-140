from typing import Optional, Union

from sessionize.sa import SqlAlchemy, Engine, Table


def drop_table(
    table: Union[Table, str],
    engine: Engine,
    if_exists: Optional[bool] = True,
    schema: Optional[str] = None
) -> None:
    SqlAlchemy.drop_table(table, engine, if_exists, schema)