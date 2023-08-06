import hashlib
import inspect
import warnings
import snowflake.sqlalchemy
import sqlalchemy.types as sqltypes
from sqlalchemy import exc as sa_exc
from sqlalchemy import util as sa_util
from sqlalchemy.sql import text
_check_snowflake_sqlalchemy_change = True


def _get_schema_columns(self, connection, schema, **kw):
    xneh__addjl = {}
    gsv__jzqm, cszh__koxu = self._current_database_schema(connection, **kw)
    iyqeg__dzr = self._denormalize_quote_join(gsv__jzqm, schema)
    try:
        bmdu__teejf = self._get_schema_primary_keys(connection, iyqeg__dzr,
            **kw)
        qzpk__bwm = connection.execute(text(
            """
        SELECT /* sqlalchemy:_get_schema_columns */
                ic.table_name,
                ic.column_name,
                ic.data_type,
                ic.character_maximum_length,
                ic.numeric_precision,
                ic.numeric_scale,
                ic.is_nullable,
                ic.column_default,
                ic.is_identity,
                ic.comment
            FROM information_schema.columns ic
            WHERE ic.table_schema=:table_schema
            ORDER BY ic.ordinal_position"""
            ), {'table_schema': self.denormalize_name(schema)})
    except sa_exc.ProgrammingError as bri__gkr:
        if bri__gkr.orig.errno == 90030:
            return None
        raise
    for table_name, lrs__qwbk, vcit__yqz, bpl__qiuby, pam__aujcv, uyetq__xpawe, ekhcr__jcy, seb__fhdr, tngmi__edhgg, apc__zfai in qzpk__bwm:
        table_name = self.normalize_name(table_name)
        lrs__qwbk = self.normalize_name(lrs__qwbk)
        if table_name not in xneh__addjl:
            xneh__addjl[table_name] = list()
        if lrs__qwbk.startswith('sys_clustering_column'):
            continue
        ejdqq__uvgbb = self.ischema_names.get(vcit__yqz, None)
        cxtdd__rlzo = {}
        if ejdqq__uvgbb is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(vcit__yqz, lrs__qwbk))
            ejdqq__uvgbb = sqltypes.NULLTYPE
        elif issubclass(ejdqq__uvgbb, sqltypes.FLOAT):
            cxtdd__rlzo['precision'] = pam__aujcv
            cxtdd__rlzo['decimal_return_scale'] = uyetq__xpawe
        elif issubclass(ejdqq__uvgbb, sqltypes.Numeric):
            cxtdd__rlzo['precision'] = pam__aujcv
            cxtdd__rlzo['scale'] = uyetq__xpawe
        elif issubclass(ejdqq__uvgbb, (sqltypes.String, sqltypes.BINARY)):
            cxtdd__rlzo['length'] = bpl__qiuby
        hxvk__ygnlz = ejdqq__uvgbb if isinstance(ejdqq__uvgbb, sqltypes.
            NullType) else ejdqq__uvgbb(**cxtdd__rlzo)
        txkdx__kzc = bmdu__teejf.get(table_name)
        xneh__addjl[table_name].append({'name': lrs__qwbk, 'type':
            hxvk__ygnlz, 'nullable': ekhcr__jcy == 'YES', 'default':
            seb__fhdr, 'autoincrement': tngmi__edhgg == 'YES', 'comment':
            apc__zfai, 'primary_key': lrs__qwbk in bmdu__teejf[table_name][
            'constrained_columns'] if txkdx__kzc else False})
    return xneh__addjl


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_schema_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdf39af1ac165319d3b6074e8cf9296a090a21f0e2c05b644ff8ec0e56e2d769':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_schema_columns = (
    _get_schema_columns)


def _get_table_columns(self, connection, table_name, schema=None, **kw):
    xneh__addjl = []
    gsv__jzqm, cszh__koxu = self._current_database_schema(connection, **kw)
    iyqeg__dzr = self._denormalize_quote_join(gsv__jzqm, schema)
    bmdu__teejf = self._get_schema_primary_keys(connection, iyqeg__dzr, **kw)
    qzpk__bwm = connection.execute(text(
        """
    SELECT /* sqlalchemy:get_table_columns */
            ic.table_name,
            ic.column_name,
            ic.data_type,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.is_nullable,
            ic.column_default,
            ic.is_identity,
            ic.comment
        FROM information_schema.columns ic
        WHERE ic.table_schema=:table_schema
        AND ic.table_name=:table_name
        ORDER BY ic.ordinal_position"""
        ), {'table_schema': self.denormalize_name(schema), 'table_name':
        self.denormalize_name(table_name)})
    for table_name, lrs__qwbk, vcit__yqz, bpl__qiuby, pam__aujcv, uyetq__xpawe, ekhcr__jcy, seb__fhdr, tngmi__edhgg, apc__zfai in qzpk__bwm:
        table_name = self.normalize_name(table_name)
        lrs__qwbk = self.normalize_name(lrs__qwbk)
        if lrs__qwbk.startswith('sys_clustering_column'):
            continue
        ejdqq__uvgbb = self.ischema_names.get(vcit__yqz, None)
        cxtdd__rlzo = {}
        if ejdqq__uvgbb is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(vcit__yqz, lrs__qwbk))
            ejdqq__uvgbb = sqltypes.NULLTYPE
        elif issubclass(ejdqq__uvgbb, sqltypes.FLOAT):
            cxtdd__rlzo['precision'] = pam__aujcv
            cxtdd__rlzo['decimal_return_scale'] = uyetq__xpawe
        elif issubclass(ejdqq__uvgbb, sqltypes.Numeric):
            cxtdd__rlzo['precision'] = pam__aujcv
            cxtdd__rlzo['scale'] = uyetq__xpawe
        elif issubclass(ejdqq__uvgbb, (sqltypes.String, sqltypes.BINARY)):
            cxtdd__rlzo['length'] = bpl__qiuby
        hxvk__ygnlz = ejdqq__uvgbb if isinstance(ejdqq__uvgbb, sqltypes.
            NullType) else ejdqq__uvgbb(**cxtdd__rlzo)
        txkdx__kzc = bmdu__teejf.get(table_name)
        xneh__addjl.append({'name': lrs__qwbk, 'type': hxvk__ygnlz,
            'nullable': ekhcr__jcy == 'YES', 'default': seb__fhdr,
            'autoincrement': tngmi__edhgg == 'YES', 'comment': apc__zfai if
            apc__zfai != '' else None, 'primary_key': lrs__qwbk in
            bmdu__teejf[table_name]['constrained_columns'] if txkdx__kzc else
            False})
    return xneh__addjl


if _check_snowflake_sqlalchemy_change:
    lines = inspect.getsource(snowflake.sqlalchemy.snowdialect.
        SnowflakeDialect._get_table_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9ecc8a2425c655836ade4008b1b98a8fd1819f3be43ba77b0fbbfc1f8740e2be':
        warnings.warn(
            'snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns has changed'
            )
snowflake.sqlalchemy.snowdialect.SnowflakeDialect._get_table_columns = (
    _get_table_columns)
