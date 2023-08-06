"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        bta__mmw = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(bta__mmw)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lsorl__tfkgw = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, lsorl__tfkgw)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        toelw__vyajz, = args
        ayr__jaoy = signature.return_type
        lbyx__ute = cgutils.create_struct_proxy(ayr__jaoy)(context, builder)
        lbyx__ute.obj = toelw__vyajz
        context.nrt.incref(builder, signature.args[0], toelw__vyajz)
        return lbyx__ute._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPDatetime('ns'):
            return
        njcr__xxqhr = 'def impl(S_dt):\n'
        njcr__xxqhr += '    S = S_dt._obj\n'
        njcr__xxqhr += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        njcr__xxqhr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        njcr__xxqhr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        njcr__xxqhr += '    numba.parfors.parfor.init_prange()\n'
        njcr__xxqhr += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            njcr__xxqhr += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            njcr__xxqhr += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        njcr__xxqhr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        njcr__xxqhr += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        njcr__xxqhr += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        njcr__xxqhr += '            continue\n'
        njcr__xxqhr += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            njcr__xxqhr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                njcr__xxqhr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            njcr__xxqhr += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            vil__tnokg = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            njcr__xxqhr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            njcr__xxqhr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            njcr__xxqhr += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(vil__tnokg[field]))
        elif field == 'is_leap_year':
            njcr__xxqhr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            njcr__xxqhr += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            vil__tnokg = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            njcr__xxqhr += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            njcr__xxqhr += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            njcr__xxqhr += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(vil__tnokg[field]))
        else:
            njcr__xxqhr += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            njcr__xxqhr += '        out_arr[i] = ts.' + field + '\n'
        njcr__xxqhr += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ruo__kgz = {}
        exec(njcr__xxqhr, {'bodo': bodo, 'numba': numba, 'np': np}, ruo__kgz)
        impl = ruo__kgz['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        vomg__wypx = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vomg__wypx)


_install_date_fields()


def create_date_method_overload(method):
    hvjm__eyy = method in ['day_name', 'month_name']
    if hvjm__eyy:
        njcr__xxqhr = 'def overload_method(S_dt, locale=None):\n'
        njcr__xxqhr += '    unsupported_args = dict(locale=locale)\n'
        njcr__xxqhr += '    arg_defaults = dict(locale=None)\n'
        njcr__xxqhr += '    bodo.utils.typing.check_unsupported_args(\n'
        njcr__xxqhr += f"        'Series.dt.{method}',\n"
        njcr__xxqhr += '        unsupported_args,\n'
        njcr__xxqhr += '        arg_defaults,\n'
        njcr__xxqhr += "        package_name='pandas',\n"
        njcr__xxqhr += "        module_name='Series',\n"
        njcr__xxqhr += '    )\n'
    else:
        njcr__xxqhr = 'def overload_method(S_dt):\n'
    njcr__xxqhr += '    if not S_dt.stype.dtype == bodo.datetime64ns:\n'
    njcr__xxqhr += '        return\n'
    if hvjm__eyy:
        njcr__xxqhr += '    def impl(S_dt, locale=None):\n'
    else:
        njcr__xxqhr += '    def impl(S_dt):\n'
    njcr__xxqhr += '        S = S_dt._obj\n'
    njcr__xxqhr += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    njcr__xxqhr += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    njcr__xxqhr += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    njcr__xxqhr += '        numba.parfors.parfor.init_prange()\n'
    njcr__xxqhr += '        n = len(arr)\n'
    if hvjm__eyy:
        njcr__xxqhr += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        njcr__xxqhr += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    njcr__xxqhr += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    njcr__xxqhr += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    njcr__xxqhr += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    njcr__xxqhr += '                continue\n'
    njcr__xxqhr += """            ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(arr[i])
"""
    njcr__xxqhr += f'            method_val = ts.{method}()\n'
    if hvjm__eyy:
        njcr__xxqhr += '            out_arr[i] = method_val\n'
    else:
        njcr__xxqhr += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    njcr__xxqhr += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    njcr__xxqhr += '    return impl\n'
    ruo__kgz = {}
    exec(njcr__xxqhr, {'bodo': bodo, 'numba': numba, 'np': np}, ruo__kgz)
    overload_method = ruo__kgz['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        vomg__wypx = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vomg__wypx)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not S_dt.stype.dtype == types.NPDatetime('ns'):
        return

    def impl(S_dt):
        xupgm__pxtkn = S_dt._obj
        wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(xupgm__pxtkn)
        yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(xupgm__pxtkn)
        bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(xupgm__pxtkn)
        numba.parfors.parfor.init_prange()
        kjf__xva = len(wwzm__qpgnc)
        hwu__uldj = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            kjf__xva)
        for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva):
            fosn__zwr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                wwzm__qpgnc[fzo__uaqu])
            bmz__tav = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(fosn__zwr))
            hwu__uldj[fzo__uaqu] = datetime.date(bmz__tav.year, bmz__tav.
                month, bmz__tav.day)
        return bodo.hiframes.pd_series_ext.init_series(hwu__uldj, yzba__rrp,
            bta__mmw)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and S_dt.stype.dtype ==
            types.NPDatetime('ns')):
            return
        if attr == 'components':
            aaqv__rua = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            fsnlo__pzkgg = 'convert_numpy_timedelta64_to_pd_timedelta'
            fwcn__ovc = 'np.empty(n, np.int64)'
            kxswy__ifv = attr
        elif attr == 'isocalendar':
            aaqv__rua = ['year', 'week', 'day']
            fsnlo__pzkgg = 'convert_datetime64_to_timestamp'
            fwcn__ovc = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            kxswy__ifv = attr + '()'
        njcr__xxqhr = 'def impl(S_dt):\n'
        njcr__xxqhr += '    S = S_dt._obj\n'
        njcr__xxqhr += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        njcr__xxqhr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        njcr__xxqhr += '    numba.parfors.parfor.init_prange()\n'
        njcr__xxqhr += '    n = len(arr)\n'
        for field in aaqv__rua:
            njcr__xxqhr += '    {} = {}\n'.format(field, fwcn__ovc)
        njcr__xxqhr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        njcr__xxqhr += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in aaqv__rua:
            njcr__xxqhr += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        njcr__xxqhr += '            continue\n'
        xnw__xzsd = '(' + '[i], '.join(aaqv__rua) + '[i])'
        njcr__xxqhr += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(xnw__xzsd, fsnlo__pzkgg, kxswy__ifv))
        jyygg__dhz = '(' + ', '.join(aaqv__rua) + ')'
        ohb__imzg = "('" + "', '".join(aaqv__rua) + "')"
        njcr__xxqhr += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, {})\n'
            .format(jyygg__dhz, ohb__imzg))
        ruo__kgz = {}
        exec(njcr__xxqhr, {'bodo': bodo, 'numba': numba, 'np': np}, ruo__kgz)
        impl = ruo__kgz['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    opxfv__zqy = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, mino__nvmk in opxfv__zqy:
        vomg__wypx = create_series_dt_df_output_overload(attr)
        mino__nvmk(SeriesDatetimePropertiesType, attr, inline='always')(
            vomg__wypx)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        njcr__xxqhr = 'def impl(S_dt):\n'
        njcr__xxqhr += '    S = S_dt._obj\n'
        njcr__xxqhr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        njcr__xxqhr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        njcr__xxqhr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        njcr__xxqhr += '    numba.parfors.parfor.init_prange()\n'
        njcr__xxqhr += '    n = len(A)\n'
        njcr__xxqhr += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        njcr__xxqhr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        njcr__xxqhr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        njcr__xxqhr += '            bodo.libs.array_kernels.setna(B, i)\n'
        njcr__xxqhr += '            continue\n'
        njcr__xxqhr += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            njcr__xxqhr += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            njcr__xxqhr += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            njcr__xxqhr += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            njcr__xxqhr += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        njcr__xxqhr += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        ruo__kgz = {}
        exec(njcr__xxqhr, {'numba': numba, 'np': np, 'bodo': bodo}, ruo__kgz)
        impl = ruo__kgz['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        njcr__xxqhr = 'def impl(S_dt):\n'
        njcr__xxqhr += '    S = S_dt._obj\n'
        njcr__xxqhr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        njcr__xxqhr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        njcr__xxqhr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        njcr__xxqhr += '    numba.parfors.parfor.init_prange()\n'
        njcr__xxqhr += '    n = len(A)\n'
        if method == 'total_seconds':
            njcr__xxqhr += '    B = np.empty(n, np.float64)\n'
        else:
            njcr__xxqhr += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        njcr__xxqhr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        njcr__xxqhr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        njcr__xxqhr += '            bodo.libs.array_kernels.setna(B, i)\n'
        njcr__xxqhr += '            continue\n'
        njcr__xxqhr += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            njcr__xxqhr += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            njcr__xxqhr += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            njcr__xxqhr += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            njcr__xxqhr += '    return B\n'
        ruo__kgz = {}
        exec(njcr__xxqhr, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, ruo__kgz)
        impl = ruo__kgz['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        vomg__wypx = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vomg__wypx)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        vomg__wypx = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vomg__wypx)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if S_dt.stype.dtype != types.NPDatetime('ns'):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        xupgm__pxtkn = S_dt._obj
        aty__lwvh = bodo.hiframes.pd_series_ext.get_series_data(xupgm__pxtkn)
        yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(xupgm__pxtkn)
        bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(xupgm__pxtkn)
        numba.parfors.parfor.init_prange()
        kjf__xva = len(aty__lwvh)
        nifei__cit = bodo.libs.str_arr_ext.pre_alloc_string_array(kjf__xva, -1)
        for oipz__wfj in numba.parfors.parfor.internal_prange(kjf__xva):
            if bodo.libs.array_kernels.isna(aty__lwvh, oipz__wfj):
                bodo.libs.array_kernels.setna(nifei__cit, oipz__wfj)
                continue
            nifei__cit[oipz__wfj
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                aty__lwvh[oipz__wfj]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(nifei__cit,
            yzba__rrp, bta__mmw)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'):
            return
        ysci__itual = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        srp__lexfc = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', ysci__itual,
            srp__lexfc, package_name='pandas', module_name='Series')
        njcr__xxqhr = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        njcr__xxqhr += '    S = S_dt._obj\n'
        njcr__xxqhr += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        njcr__xxqhr += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        njcr__xxqhr += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        njcr__xxqhr += '    numba.parfors.parfor.init_prange()\n'
        njcr__xxqhr += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            njcr__xxqhr += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            njcr__xxqhr += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        njcr__xxqhr += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        njcr__xxqhr += '        if bodo.libs.array_kernels.isna(A, i):\n'
        njcr__xxqhr += '            bodo.libs.array_kernels.setna(B, i)\n'
        njcr__xxqhr += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            uln__mdmbv = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            cifxx__ncwm = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            uln__mdmbv = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            cifxx__ncwm = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        njcr__xxqhr += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            cifxx__ncwm, uln__mdmbv, method)
        njcr__xxqhr += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        ruo__kgz = {}
        exec(njcr__xxqhr, {'numba': numba, 'np': np, 'bodo': bodo}, ruo__kgz)
        impl = ruo__kgz['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    ushyg__qolm = ['ceil', 'floor', 'round']
    for method in ushyg__qolm:
        vomg__wypx = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vomg__wypx)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                cgq__eoexm = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ufkv__ymae = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kjf__xva = len(cgq__eoexm)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    xnny__irlrn = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(cgq__eoexm[fzo__uaqu]))
                    idgh__fgscw = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ufkv__ymae[fzo__uaqu]))
                    if xnny__irlrn == pug__gqwb or idgh__fgscw == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(xnny__irlrn, idgh__fgscw)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ufkv__ymae = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, dt64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ufkv__ymae[fzo__uaqu]))
                    if ltlzl__hsfl == pug__gqwb or kspxb__cizq == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, kspxb__cizq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ufkv__ymae = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, dt64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ufkv__ymae[fzo__uaqu]))
                    if ltlzl__hsfl == pug__gqwb or kspxb__cizq == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, kspxb__cizq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                oqkzg__hqd = rhs.value
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if ltlzl__hsfl == pug__gqwb or oqkzg__hqd == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, oqkzg__hqd)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                oqkzg__hqd = lhs.value
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if oqkzg__hqd == pug__gqwb or ltlzl__hsfl == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(oqkzg__hqd, ltlzl__hsfl)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, dt64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                qty__jxgjk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qty__jxgjk))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if ltlzl__hsfl == pug__gqwb or kspxb__cizq == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, kspxb__cizq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, dt64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                qty__jxgjk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qty__jxgjk))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    ltlzl__hsfl = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if ltlzl__hsfl == pug__gqwb or kspxb__cizq == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, kspxb__cizq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                fosn__zwr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                ltlzl__hsfl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    fosn__zwr)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    bezk__lpq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        wwzm__qpgnc[fzo__uaqu])
                    if bezk__lpq == pug__gqwb or ltlzl__hsfl == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(bezk__lpq, ltlzl__hsfl)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                fosn__zwr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                ltlzl__hsfl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    fosn__zwr)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    bezk__lpq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        wwzm__qpgnc[fzo__uaqu])
                    if ltlzl__hsfl == pug__gqwb or bezk__lpq == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(ltlzl__hsfl, bezk__lpq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(blbh__ahjd))
                qty__jxgjk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qty__jxgjk))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    osn__bjh = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if kspxb__cizq == pug__gqwb or osn__bjh == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(osn__bjh, kspxb__cizq)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                xupgm__pxtkn = np.empty(kjf__xva, timedelta64_dtype)
                pug__gqwb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(blbh__ahjd))
                qty__jxgjk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                kspxb__cizq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qty__jxgjk))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    osn__bjh = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if kspxb__cizq == pug__gqwb or osn__bjh == pug__gqwb:
                        rrzg__apml = pug__gqwb
                    else:
                        rrzg__apml = op(kspxb__cizq, osn__bjh)
                    xupgm__pxtkn[fzo__uaqu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        rrzg__apml)
                return bodo.hiframes.pd_series_ext.init_series(xupgm__pxtkn,
                    yzba__rrp, bta__mmw)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            fobv__ngqfk = True
        else:
            fobv__ngqfk = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(blbh__ahjd))
                nzezh__buiyj = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                efpzx__dsr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(nzezh__buiyj))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    bei__dcx = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if bei__dcx == pug__gqwb or efpzx__dsr == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(bei__dcx, efpzx__dsr)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(blbh__ahjd))
                uoi__dpioz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                bei__dcx = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uoi__dpioz))
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    efpzx__dsr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if bei__dcx == pug__gqwb or efpzx__dsr == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(bei__dcx, efpzx__dsr)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    bei__dcx = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        wwzm__qpgnc[fzo__uaqu])
                    if bei__dcx == pug__gqwb or rhs.value == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(bei__dcx, rhs.value)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    efpzx__dsr = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(wwzm__qpgnc[fzo__uaqu]))
                    if efpzx__dsr == pug__gqwb or lhs.value == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(lhs.value, efpzx__dsr)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            blbh__ahjd = lhs.dtype('NaT')

            def impl(lhs, rhs):
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                nabto__yinn = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                uef__xqx = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nabto__yinn)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    bei__dcx = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        wwzm__qpgnc[fzo__uaqu])
                    if bei__dcx == pug__gqwb or uef__xqx == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(bei__dcx, uef__xqx)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            blbh__ahjd = rhs.dtype('NaT')

            def impl(lhs, rhs):
                wwzm__qpgnc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yzba__rrp = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                bta__mmw = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                kjf__xva = len(wwzm__qpgnc)
                hwu__uldj = bodo.libs.bool_arr_ext.alloc_bool_array(kjf__xva)
                pug__gqwb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    blbh__ahjd)
                nabto__yinn = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                uef__xqx = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nabto__yinn)
                for fzo__uaqu in numba.parfors.parfor.internal_prange(kjf__xva
                    ):
                    fosn__zwr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        wwzm__qpgnc[fzo__uaqu])
                    if fosn__zwr == pug__gqwb or uef__xqx == pug__gqwb:
                        rrzg__apml = fobv__ngqfk
                    else:
                        rrzg__apml = op(uef__xqx, fosn__zwr)
                    hwu__uldj[fzo__uaqu] = rrzg__apml
                return bodo.hiframes.pd_series_ext.init_series(hwu__uldj,
                    yzba__rrp, bta__mmw)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'tz_convert', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for pnup__gmhq in series_dt_unsupported_attrs:
        ctob__jmgo = 'Series.dt.' + pnup__gmhq
        overload_attribute(SeriesDatetimePropertiesType, pnup__gmhq)(
            create_unsupported_overload(ctob__jmgo))
    for vpog__ybcn in series_dt_unsupported_methods:
        ctob__jmgo = 'Series.dt.' + vpog__ybcn
        overload_method(SeriesDatetimePropertiesType, vpog__ybcn,
            no_unliteral=True)(create_unsupported_overload(ctob__jmgo))


_install_series_dt_unsupported()
