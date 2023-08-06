from dataclasses import (
    dataclass,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenDict,
)
from redshift_client.sql_client.core import (
    SqlClient,
)
from redshift_client.sql_client.query import (
    dynamic_query,
)
from redshift_client.table.core import (
    TableId,
)


@dataclass(frozen=True)
class TableClient:
    _db_client: SqlClient

    def unload(self, table: TableId, bucket: str, role: str) -> Cmd[None]:
        stm = (
            "UNLOAD ('SELECT * FROM {schema}.{table}')"
            "TO %(bucket)s iam_role %(role)s MANIFEST"
        )
        return self._db_client.execute(
            dynamic_query(
                stm,
                FrozenDict(
                    {"schema": table._schema._name, "table": table._name}
                ),
            ),
            FrozenDict({"bucket": bucket, "role": role}),
        )

    def load(self, table: TableId, manifest: str, role: str) -> Cmd[None]:
        stm = (
            "COPY {schema}.{table} FROM %(manifest_file)s"
            "iam_role %(role)s MANIFEST"
        )
        return self._db_client.execute(
            dynamic_query(
                stm,
                FrozenDict(
                    {"schema": table._schema._name, "table": table._name}
                ),
            ),
            FrozenDict({"manifest_file": manifest, "role": role}),
        )
