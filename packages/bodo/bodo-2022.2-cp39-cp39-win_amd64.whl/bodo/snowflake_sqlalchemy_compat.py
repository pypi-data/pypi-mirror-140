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
    ptu__few = {}
    tdwk__xhoy, qzg__cvpxn = self._current_database_schema(connection, **kw)
    iue__qmfpl = self._denormalize_quote_join(tdwk__xhoy, schema)
    try:
        gwt__oie = self._get_schema_primary_keys(connection, iue__qmfpl, **kw)
        nslzs__pst = connection.execute(text(
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
    except sa_exc.ProgrammingError as aqoyv__axfhw:
        if aqoyv__axfhw.orig.errno == 90030:
            return None
        raise
    for table_name, dvinl__bxfhy, rmywl__kbiq, sspzt__uxn, avat__pyjqa, lol__orru, ltjw__czjn, obhix__rtd, moey__cod, vgm__lmg in nslzs__pst:
        table_name = self.normalize_name(table_name)
        dvinl__bxfhy = self.normalize_name(dvinl__bxfhy)
        if table_name not in ptu__few:
            ptu__few[table_name] = list()
        if dvinl__bxfhy.startswith('sys_clustering_column'):
            continue
        xhb__flo = self.ischema_names.get(rmywl__kbiq, None)
        ffn__sxiux = {}
        if xhb__flo is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(rmywl__kbiq, dvinl__bxfhy))
            xhb__flo = sqltypes.NULLTYPE
        elif issubclass(xhb__flo, sqltypes.FLOAT):
            ffn__sxiux['precision'] = avat__pyjqa
            ffn__sxiux['decimal_return_scale'] = lol__orru
        elif issubclass(xhb__flo, sqltypes.Numeric):
            ffn__sxiux['precision'] = avat__pyjqa
            ffn__sxiux['scale'] = lol__orru
        elif issubclass(xhb__flo, (sqltypes.String, sqltypes.BINARY)):
            ffn__sxiux['length'] = sspzt__uxn
        vodzl__sinl = xhb__flo if isinstance(xhb__flo, sqltypes.NullType
            ) else xhb__flo(**ffn__sxiux)
        kawau__cxd = gwt__oie.get(table_name)
        ptu__few[table_name].append({'name': dvinl__bxfhy, 'type':
            vodzl__sinl, 'nullable': ltjw__czjn == 'YES', 'default':
            obhix__rtd, 'autoincrement': moey__cod == 'YES', 'comment':
            vgm__lmg, 'primary_key': dvinl__bxfhy in gwt__oie[table_name][
            'constrained_columns'] if kawau__cxd else False})
    return ptu__few


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
    ptu__few = []
    tdwk__xhoy, qzg__cvpxn = self._current_database_schema(connection, **kw)
    iue__qmfpl = self._denormalize_quote_join(tdwk__xhoy, schema)
    gwt__oie = self._get_schema_primary_keys(connection, iue__qmfpl, **kw)
    nslzs__pst = connection.execute(text(
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
    for table_name, dvinl__bxfhy, rmywl__kbiq, sspzt__uxn, avat__pyjqa, lol__orru, ltjw__czjn, obhix__rtd, moey__cod, vgm__lmg in nslzs__pst:
        table_name = self.normalize_name(table_name)
        dvinl__bxfhy = self.normalize_name(dvinl__bxfhy)
        if dvinl__bxfhy.startswith('sys_clustering_column'):
            continue
        xhb__flo = self.ischema_names.get(rmywl__kbiq, None)
        ffn__sxiux = {}
        if xhb__flo is None:
            sa_util.warn("Did not recognize type '{}' of column '{}'".
                format(rmywl__kbiq, dvinl__bxfhy))
            xhb__flo = sqltypes.NULLTYPE
        elif issubclass(xhb__flo, sqltypes.FLOAT):
            ffn__sxiux['precision'] = avat__pyjqa
            ffn__sxiux['decimal_return_scale'] = lol__orru
        elif issubclass(xhb__flo, sqltypes.Numeric):
            ffn__sxiux['precision'] = avat__pyjqa
            ffn__sxiux['scale'] = lol__orru
        elif issubclass(xhb__flo, (sqltypes.String, sqltypes.BINARY)):
            ffn__sxiux['length'] = sspzt__uxn
        vodzl__sinl = xhb__flo if isinstance(xhb__flo, sqltypes.NullType
            ) else xhb__flo(**ffn__sxiux)
        kawau__cxd = gwt__oie.get(table_name)
        ptu__few.append({'name': dvinl__bxfhy, 'type': vodzl__sinl,
            'nullable': ltjw__czjn == 'YES', 'default': obhix__rtd,
            'autoincrement': moey__cod == 'YES', 'comment': vgm__lmg if 
            vgm__lmg != '' else None, 'primary_key': dvinl__bxfhy in
            gwt__oie[table_name]['constrained_columns'] if kawau__cxd else 
            False})
    return ptu__few


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
