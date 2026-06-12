"""Unified data source bridge — read-only access to registered databases."""
import sqlite3
import sqlparse
import re
from dataprojection.config import HISTORICAL_DB_PATH, QUERY_TIMEOUT, MAX_RESULT_ROWS


class DataSource:
    """Represents a registered data source."""

    def __init__(self, name: str, db_type: str, path_or_conn: str,
                 description: str = ""):
        self.name = name
        self.db_type = db_type  # "sqlite" or "mysql"
        self.path_or_conn = path_or_conn
        self.description = description
        self._conn = None

    def _get_connection(self):
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.path_or_conn)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    def get_schema(self) -> list[dict]:
        """Get all tables and their column schemas."""
        tables = []
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if self.db_type == "sqlite":
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite!_%' ESCAPE '!'"
                )
                table_names = [row[0] for row in cursor.fetchall()]

                for tname in table_names:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{tname}\"")
                    row_count = cursor.fetchone()[0]

                    cursor.execute(f"PRAGMA table_info(\"{tname}\")")
                    columns = []
                    for col in cursor.fetchall():
                        # Get sample values for better AI understanding
                        cursor.execute(
                            f"SELECT DISTINCT \"{col[1]}\" FROM \"{tname}\" "
                            f"WHERE \"{col[1]}\" IS NOT NULL LIMIT 5"
                        )
                        samples = [str(r[0])[:100] for r in cursor.fetchall()]

                        columns.append({
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "pk": bool(col[5]),
                            "samples": samples,
                        })

                    tables.append({
                        "table_name": tname,
                        "row_count": row_count,
                        "columns": columns,
                    })
        finally:
            conn.close()

        return tables

    def execute_query(self, sql: str, params: dict = None) -> dict:
        """Execute a read-only SQL query with safety checks.

        Returns: {"columns": [...], "rows": [[...], ...], "row_count": int}
        """
        # ── SQL Safety Validation ──
        self._validate_sql(sql)

        conn = self._get_connection()
        try:
            conn.execute(f"PRAGMA query_only = ON")
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = []
            for row in cursor.fetchmany(MAX_RESULT_ROWS + 1):
                rows.append([str(v) if v is not None else None for v in row])

            truncated = len(rows) > MAX_RESULT_ROWS
            if truncated:
                rows = rows[:MAX_RESULT_ROWS]

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated,
                "max_rows": MAX_RESULT_ROWS,
            }
        except sqlite3.Error as e:
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": str(e),
            }
        finally:
            conn.close()

    def _validate_sql(self, sql: str):
        """Validate that the SQL query is read-only and safe.

        Raises ValueError if SQL is rejected.
        """
        sql_upper = sql.upper().strip()

        # Block dangerous statements
        dangerous = [
            "DROP", "INSERT", "UPDATE", "DELETE", "ALTER", "CREATE",
            "ATTACH", "DETACH", "PRAGMA", "REPLACE", "GRANT", "REVOKE",
        ]
        for kw in dangerous:
            # Check as standalone keyword, not inside column names
            if re.search(rf'\b{kw}\b', sql_upper):
                raise ValueError(
                    f"Dangerous SQL keyword '{kw}' is not allowed. "
                    f"Only SELECT queries are permitted."
                )

        # Must be a SELECT statement (possibly with WITH clause)
        stripped = sql_upper.strip()
        allowed_start = stripped.startswith("SELECT") or stripped.startswith("WITH")
        if not allowed_start:
            raise ValueError(
                "Only SELECT (or WITH ... SELECT) queries are permitted."
            )

        # Block sqlite_master direct access
        if "sqlite_master" in sql_upper.lower():
            raise ValueError("Direct access to sqlite_master is not allowed.")


# ── Pre-configured data sources ──

def get_liangke_historical() -> DataSource:
    return DataSource(
        name="liangke_historical",
        db_type="sqlite",
        path_or_conn=HISTORICAL_DB_PATH,
        description="量科历史数据库 — 量子科技新闻/融资/行业动态，含11789条记录",
    )
