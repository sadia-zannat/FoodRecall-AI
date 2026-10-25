"""Local Zetaris Lightning JDBC adapter (read-only, opt-in).

This adapts the hackathon's self-hosted Zetaris platform to the existing
FoodRecall evidence projection. It does NOT verify source-to-inventory joins.
All connection credentials stay in environment variables on the user's host.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from backend.zetaris import ZetarisError, safe_table_name

JDBC_DRIVER = 'com.zetaris.lightning.jdbc.LightningDriver'
DEFAULT_LOCAL_URL = 'jdbc:zetaris:lightning@localhost:10000'


def jdbc_configured() -> bool:
    return bool(os.environ.get('ZETARIS_JDBC_USER') and
                os.environ.get('ZETARIS_JDBC_PASSWORD') and
                os.environ.get('ZETARIS_JDBC_JAR'))


def _safe_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)[:512]


class ZetarisJDBCClient:
    """Run bounded SELECTs via Zetaris's JDBC driver, never user-supplied SQL."""

    def __init__(self, url=None, user=None, password=None, jar=None, connect=None):
        self.url = url if url is not None else os.getenv('ZETARIS_JDBC_URL', DEFAULT_LOCAL_URL)
        self.user = user if user is not None else os.getenv('ZETARIS_JDBC_USER', '')
        self.password = password if password is not None else os.getenv('ZETARIS_JDBC_PASSWORD', '')
        self.jar = jar if jar is not None else os.getenv('ZETARIS_JDBC_JAR', '')
        self._connect_override = connect
        # Prevent accidentally routing private local credentials to a remote host.
        match = re.fullmatch(r'jdbc:zetaris:lightning@(localhost|127\.0\.0\.1):(\d{1,5})', self.url)
        if not match or not (1 <= int(match.group(2)) <= 65535):
            raise ZetarisError('Local JDBC URL must use localhost or 127.0.0.1 and an allowed port')

    @property
    def ready(self):
        return bool(self.user and self.password and self.jar)

    def _connection(self):
        if not self.ready:
            raise ZetarisError('Local Zetaris JDBC user, password and driver JAR required')
        if self._connect_override is None:
            if not Path(self.jar).is_file():
                raise ZetarisError('Local Zetaris JDBC driver JAR not found')
            try:
                import jaydebeapi
            except ImportError:
                raise ZetarisError('Install optional JDBC dependencies: JayDeBeApi and JPype1') from None
            connect = jaydebeapi.connect
        else:
            connect = self._connect_override
        try:
            return connect(JDBC_DRIVER, self.url, [self.user, self.password], self.jar)
        except Exception:
            # The JDBC/JVM exception may embed passwords or query rows.
            raise ZetarisError('Local Zetaris JDBC connection failed; inspect private local settings') from None

    def _execute(self, sql):
        connection = self._connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            description = cursor.description or []
            fields = [str(column[0])[:128] for column in description]
            data = cursor.fetchall()
            return [dict(zip(fields, (_safe_value(v) for v in record))) for record in data]
        except Exception:
            raise ZetarisError('Local Zetaris JDBC read failed; check table permissions/schema') from None
        finally:
            if cursor is not None:
                try: cursor.close()
                except Exception: pass
            try: connection.close()
            except Exception: pass

    def ping(self):
        rows = self._execute('SELECT 1')
        if not rows:
            raise ZetarisError('Local Zetaris JDBC SELECT 1 returned no rows')
        return {'status': 'LIVE_SELECT1_OBSERVED', 'query': 'SELECT 1', 'rows_observed': len(rows)}

    def query(self, table, columns=('*',), page_limit=20):
        table = safe_table_name(table)
        if not (isinstance(page_limit, int) and 1 <= page_limit <= 100):
            raise ZetarisError('pageLimit out of range')
        if columns != ('*',) and (not columns or any(not re.fullmatch(r'[A-Za-z_][\w]*', v) for v in columns)):
            raise ZetarisError('Invalid allowlisted column identifiers')
        sql = f"SELECT {', '.join(columns)} FROM {table} LIMIT {page_limit}"
        rows = self._execute(sql)
        return {'query': sql, 'response': {'rows': rows}, 'mode': 'LIVE_TENANT_RESPONSE',
                'page_limit': page_limit, 'transport': 'zetaris_local_jdbc'}

    def read_approved_sources(self):
        tables = (os.getenv('ZETARIS_RECALL_TABLE', ''), os.getenv('ZETARIS_SHIPMENT_TABLE', ''))
        if not all(tables):
            raise ZetarisError('Both Zetaris table mappings are required')
        return {'recall': self.query(tables[0]), 'shipment': self.query(tables[1]),
                'verified_product_lot_links': [], 'writes_performed': 0}
