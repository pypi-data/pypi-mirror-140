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
    jknpd__nfrku = {}
    ritzu__mdy, enm__krx = self._current_database_schema(connection, **kw)
    llqr__ssk = self._denormalize_quote_join(ritzu__mdy, schema)
    try:
        cjo__qqwag = self._get_schema_primary_keys(connection, llqr__ssk, **kw)
        gpngo__jgx = connection.execute(text(
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
    except sa_exc.ProgrammingError as qwta__qzwl:
        if qwta__qzwl.orig.errno == 90030:
            return None
        raise
    for table_name, gxnm__mbfw, mvuvs__daikg, ijjg__nqyzg, nkbvd__whvjp, mswir__dscr, kajn__bjde, ohxb__stykv, rtnx__veupq, wqzg__luopl in gpngo__jgx:
        table_name = self.normalize_name(table_name)
        gxnm__mbfw = self.normalize_name(gxnm__mbfw)
        if table_name not in jknpd__nfrku:
            jknpd__nfrku[table_name] = list()
        if gxnm__mbfw.startswith('sys_clustering_column'):
            continue
        puk__latr = self.ischema_names.get(mvuvs__daikg, None)
        xid__fwc = {}
        if puk__latr is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(mvuvs__daikg, gxnm__mbfw))
            puk__latr = sqltypes.NULLTYPE
        elif issubclass(puk__latr, sqltypes.FLOAT):
            xid__fwc['precision'] = nkbvd__whvjp
            xid__fwc['decimal_return_scale'] = mswir__dscr
        elif issubclass(puk__latr, sqltypes.Numeric):
            xid__fwc['precision'] = nkbvd__whvjp
            xid__fwc['scale'] = mswir__dscr
        elif issubclass(puk__latr, (sqltypes.String, sqltypes.BINARY)):
            xid__fwc['length'] = ijjg__nqyzg
        akok__sxz = puk__latr if isinstance(puk__latr, sqltypes.NullType
            ) else puk__latr(**xid__fwc)
        pok__qhdby = cjo__qqwag.get(table_name)
        jknpd__nfrku[table_name].append({'name': gxnm__mbfw, 'type':
            akok__sxz, 'nullable': kajn__bjde == 'YES', 'default':
            ohxb__stykv, 'autoincrement': rtnx__veupq == 'YES', 'comment':
            wqzg__luopl, 'primary_key': gxnm__mbfw in cjo__qqwag[table_name
            ]['constrained_columns'] if pok__qhdby else False})
    return jknpd__nfrku


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
    jknpd__nfrku = []
    ritzu__mdy, enm__krx = self._current_database_schema(connection, **kw)
    llqr__ssk = self._denormalize_quote_join(ritzu__mdy, schema)
    cjo__qqwag = self._get_schema_primary_keys(connection, llqr__ssk, **kw)
    gpngo__jgx = connection.execute(text(
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
    for table_name, gxnm__mbfw, mvuvs__daikg, ijjg__nqyzg, nkbvd__whvjp, mswir__dscr, kajn__bjde, ohxb__stykv, rtnx__veupq, wqzg__luopl in gpngo__jgx:
        table_name = self.normalize_name(table_name)
        gxnm__mbfw = self.normalize_name(gxnm__mbfw)
        if gxnm__mbfw.startswith('sys_clustering_column'):
            continue
        puk__latr = self.ischema_names.get(mvuvs__daikg, None)
        xid__fwc = {}
        if puk__latr is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(mvuvs__daikg, gxnm__mbfw))
            puk__latr = sqltypes.NULLTYPE
        elif issubclass(puk__latr, sqltypes.FLOAT):
            xid__fwc['precision'] = nkbvd__whvjp
            xid__fwc['decimal_return_scale'] = mswir__dscr
        elif issubclass(puk__latr, sqltypes.Numeric):
            xid__fwc['precision'] = nkbvd__whvjp
            xid__fwc['scale'] = mswir__dscr
        elif issubclass(puk__latr, (sqltypes.String, sqltypes.BINARY)):
            xid__fwc['length'] = ijjg__nqyzg
        akok__sxz = puk__latr if isinstance(puk__latr, sqltypes.NullType
            ) else puk__latr(**xid__fwc)
        pok__qhdby = cjo__qqwag.get(table_name)
        jknpd__nfrku.append({'name': gxnm__mbfw, 'type': akok__sxz,
            'nullable': kajn__bjde == 'YES', 'default': ohxb__stykv,
            'autoincrement': rtnx__veupq == 'YES', 'comment': wqzg__luopl if
            wqzg__luopl != '' else None, 'primary_key': gxnm__mbfw in
            cjo__qqwag[table_name]['constrained_columns'] if pok__qhdby else
            False})
    return jknpd__nfrku


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
