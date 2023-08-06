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
        uzx__xhy = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(uzx__xhy)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kye__lnvk = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, kye__lnvk)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        eer__rsa, = args
        gpmap__mbqb = signature.return_type
        nutuc__otojp = cgutils.create_struct_proxy(gpmap__mbqb)(context,
            builder)
        nutuc__otojp.obj = eer__rsa
        context.nrt.incref(builder, signature.args[0], eer__rsa)
        return nutuc__otojp._getvalue()
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
        kie__hcxyj = 'def impl(S_dt):\n'
        kie__hcxyj += '    S = S_dt._obj\n'
        kie__hcxyj += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kie__hcxyj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kie__hcxyj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        kie__hcxyj += '    numba.parfors.parfor.init_prange()\n'
        kie__hcxyj += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            kie__hcxyj += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            kie__hcxyj += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        kie__hcxyj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        kie__hcxyj += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        kie__hcxyj += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        kie__hcxyj += '            continue\n'
        kie__hcxyj += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            kie__hcxyj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                kie__hcxyj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            kie__hcxyj += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            efvk__cgb = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            kie__hcxyj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            kie__hcxyj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            kie__hcxyj += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(efvk__cgb[field]))
        elif field == 'is_leap_year':
            kie__hcxyj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            kie__hcxyj += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            efvk__cgb = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            kie__hcxyj += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            kie__hcxyj += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            kie__hcxyj += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(efvk__cgb[field]))
        else:
            kie__hcxyj += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            kie__hcxyj += '        out_arr[i] = ts.' + field + '\n'
        kie__hcxyj += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        fek__gvyfa = {}
        exec(kie__hcxyj, {'bodo': bodo, 'numba': numba, 'np': np}, fek__gvyfa)
        impl = fek__gvyfa['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        mlw__alv = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(mlw__alv)


_install_date_fields()


def create_date_method_overload(method):
    phjig__crz = method in ['day_name', 'month_name']
    if phjig__crz:
        kie__hcxyj = 'def overload_method(S_dt, locale=None):\n'
        kie__hcxyj += '    unsupported_args = dict(locale=locale)\n'
        kie__hcxyj += '    arg_defaults = dict(locale=None)\n'
        kie__hcxyj += '    bodo.utils.typing.check_unsupported_args(\n'
        kie__hcxyj += f"        'Series.dt.{method}',\n"
        kie__hcxyj += '        unsupported_args,\n'
        kie__hcxyj += '        arg_defaults,\n'
        kie__hcxyj += "        package_name='pandas',\n"
        kie__hcxyj += "        module_name='Series',\n"
        kie__hcxyj += '    )\n'
    else:
        kie__hcxyj = 'def overload_method(S_dt):\n'
    kie__hcxyj += '    if not S_dt.stype.dtype == bodo.datetime64ns:\n'
    kie__hcxyj += '        return\n'
    if phjig__crz:
        kie__hcxyj += '    def impl(S_dt, locale=None):\n'
    else:
        kie__hcxyj += '    def impl(S_dt):\n'
    kie__hcxyj += '        S = S_dt._obj\n'
    kie__hcxyj += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    kie__hcxyj += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    kie__hcxyj += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    kie__hcxyj += '        numba.parfors.parfor.init_prange()\n'
    kie__hcxyj += '        n = len(arr)\n'
    if phjig__crz:
        kie__hcxyj += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        kie__hcxyj += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    kie__hcxyj += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    kie__hcxyj += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    kie__hcxyj += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    kie__hcxyj += '                continue\n'
    kie__hcxyj += """            ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(arr[i])
"""
    kie__hcxyj += f'            method_val = ts.{method}()\n'
    if phjig__crz:
        kie__hcxyj += '            out_arr[i] = method_val\n'
    else:
        kie__hcxyj += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    kie__hcxyj += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    kie__hcxyj += '    return impl\n'
    fek__gvyfa = {}
    exec(kie__hcxyj, {'bodo': bodo, 'numba': numba, 'np': np}, fek__gvyfa)
    overload_method = fek__gvyfa['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        mlw__alv = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            mlw__alv)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not S_dt.stype.dtype == types.NPDatetime('ns'):
        return

    def impl(S_dt):
        swexh__mgdcn = S_dt._obj
        dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(swexh__mgdcn)
        rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(swexh__mgdcn)
        uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(swexh__mgdcn)
        numba.parfors.parfor.init_prange()
        kxtju__yufz = len(dxycm__tluc)
        yke__bup = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            kxtju__yufz)
        for uab__gmd in numba.parfors.parfor.internal_prange(kxtju__yufz):
            vcjnp__ecwr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                dxycm__tluc[uab__gmd])
            sles__ytaw = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(vcjnp__ecwr))
            yke__bup[uab__gmd] = datetime.date(sles__ytaw.year, sles__ytaw.
                month, sles__ytaw.day)
        return bodo.hiframes.pd_series_ext.init_series(yke__bup, rrdgu__kqn,
            uzx__xhy)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and S_dt.stype.dtype ==
            types.NPDatetime('ns')):
            return
        if attr == 'components':
            eljea__bmk = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            kfe__rzrg = 'convert_numpy_timedelta64_to_pd_timedelta'
            lohx__rgtrp = 'np.empty(n, np.int64)'
            lzfi__rzq = attr
        elif attr == 'isocalendar':
            eljea__bmk = ['year', 'week', 'day']
            kfe__rzrg = 'convert_datetime64_to_timestamp'
            lohx__rgtrp = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            lzfi__rzq = attr + '()'
        kie__hcxyj = 'def impl(S_dt):\n'
        kie__hcxyj += '    S = S_dt._obj\n'
        kie__hcxyj += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kie__hcxyj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kie__hcxyj += '    numba.parfors.parfor.init_prange()\n'
        kie__hcxyj += '    n = len(arr)\n'
        for field in eljea__bmk:
            kie__hcxyj += '    {} = {}\n'.format(field, lohx__rgtrp)
        kie__hcxyj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        kie__hcxyj += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in eljea__bmk:
            kie__hcxyj += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        kie__hcxyj += '            continue\n'
        vll__olgrw = '(' + '[i], '.join(eljea__bmk) + '[i])'
        kie__hcxyj += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(vll__olgrw, kfe__rzrg, lzfi__rzq))
        ardu__olyus = '(' + ', '.join(eljea__bmk) + ')'
        bsm__tgamt = "('" + "', '".join(eljea__bmk) + "')"
        kie__hcxyj += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, {})\n'
            .format(ardu__olyus, bsm__tgamt))
        fek__gvyfa = {}
        exec(kie__hcxyj, {'bodo': bodo, 'numba': numba, 'np': np}, fek__gvyfa)
        impl = fek__gvyfa['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    ftt__jpc = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, zqa__ohr in ftt__jpc:
        mlw__alv = create_series_dt_df_output_overload(attr)
        zqa__ohr(SeriesDatetimePropertiesType, attr, inline='always')(mlw__alv)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        kie__hcxyj = 'def impl(S_dt):\n'
        kie__hcxyj += '    S = S_dt._obj\n'
        kie__hcxyj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kie__hcxyj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kie__hcxyj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        kie__hcxyj += '    numba.parfors.parfor.init_prange()\n'
        kie__hcxyj += '    n = len(A)\n'
        kie__hcxyj += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        kie__hcxyj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        kie__hcxyj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        kie__hcxyj += '            bodo.libs.array_kernels.setna(B, i)\n'
        kie__hcxyj += '            continue\n'
        kie__hcxyj += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            kie__hcxyj += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            kie__hcxyj += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            kie__hcxyj += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            kie__hcxyj += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        kie__hcxyj += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        fek__gvyfa = {}
        exec(kie__hcxyj, {'numba': numba, 'np': np, 'bodo': bodo}, fek__gvyfa)
        impl = fek__gvyfa['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        kie__hcxyj = 'def impl(S_dt):\n'
        kie__hcxyj += '    S = S_dt._obj\n'
        kie__hcxyj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kie__hcxyj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kie__hcxyj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        kie__hcxyj += '    numba.parfors.parfor.init_prange()\n'
        kie__hcxyj += '    n = len(A)\n'
        if method == 'total_seconds':
            kie__hcxyj += '    B = np.empty(n, np.float64)\n'
        else:
            kie__hcxyj += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        kie__hcxyj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        kie__hcxyj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        kie__hcxyj += '            bodo.libs.array_kernels.setna(B, i)\n'
        kie__hcxyj += '            continue\n'
        kie__hcxyj += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            kie__hcxyj += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            kie__hcxyj += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            kie__hcxyj += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            kie__hcxyj += '    return B\n'
        fek__gvyfa = {}
        exec(kie__hcxyj, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, fek__gvyfa)
        impl = fek__gvyfa['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        mlw__alv = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(mlw__alv)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        mlw__alv = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            mlw__alv)


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
        swexh__mgdcn = S_dt._obj
        kupm__agpoo = bodo.hiframes.pd_series_ext.get_series_data(swexh__mgdcn)
        rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(swexh__mgdcn)
        uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(swexh__mgdcn)
        numba.parfors.parfor.init_prange()
        kxtju__yufz = len(kupm__agpoo)
        kcl__pbg = bodo.libs.str_arr_ext.pre_alloc_string_array(kxtju__yufz, -1
            )
        for sjum__zea in numba.parfors.parfor.internal_prange(kxtju__yufz):
            if bodo.libs.array_kernels.isna(kupm__agpoo, sjum__zea):
                bodo.libs.array_kernels.setna(kcl__pbg, sjum__zea)
                continue
            kcl__pbg[sjum__zea
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                kupm__agpoo[sjum__zea]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(kcl__pbg, rrdgu__kqn,
            uzx__xhy)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'):
            return
        egjv__qgss = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        wcizx__mbi = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', egjv__qgss,
            wcizx__mbi, package_name='pandas', module_name='Series')
        kie__hcxyj = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        kie__hcxyj += '    S = S_dt._obj\n'
        kie__hcxyj += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kie__hcxyj += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kie__hcxyj += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        kie__hcxyj += '    numba.parfors.parfor.init_prange()\n'
        kie__hcxyj += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            kie__hcxyj += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            kie__hcxyj += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        kie__hcxyj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        kie__hcxyj += '        if bodo.libs.array_kernels.isna(A, i):\n'
        kie__hcxyj += '            bodo.libs.array_kernels.setna(B, i)\n'
        kie__hcxyj += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            bbnig__tra = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            qsxjv__uskil = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            bbnig__tra = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            qsxjv__uskil = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        kie__hcxyj += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            qsxjv__uskil, bbnig__tra, method)
        kie__hcxyj += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        fek__gvyfa = {}
        exec(kie__hcxyj, {'numba': numba, 'np': np, 'bodo': bodo}, fek__gvyfa)
        impl = fek__gvyfa['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    nsg__rwb = ['ceil', 'floor', 'round']
    for method in nsg__rwb:
        mlw__alv = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            mlw__alv)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ahvrp__der = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                gzchf__inbyc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kxtju__yufz = len(ahvrp__der)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    dah__ytlti = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ahvrp__der[uab__gmd]))
                    hfm__avjxq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(gzchf__inbyc[uab__gmd]))
                    if dah__ytlti == dlff__kigr or hfm__avjxq == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(dah__ytlti, hfm__avjxq)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                gzchf__inbyc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, dt64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gzchf__inbyc[uab__gmd]))
                    if uekv__xsb == dlff__kigr or oiotz__ijji == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, oiotz__ijji)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                gzchf__inbyc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, dt64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(gzchf__inbyc[uab__gmd]))
                    if uekv__xsb == dlff__kigr or oiotz__ijji == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, oiotz__ijji)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                pex__oam = rhs.value
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    if uekv__xsb == dlff__kigr or pex__oam == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, pex__oam)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                pex__oam = lhs.value
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    if pex__oam == dlff__kigr or uekv__xsb == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(pex__oam, uekv__xsb)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, dt64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                gta__sgoa = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(gta__sgoa))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    if uekv__xsb == dlff__kigr or oiotz__ijji == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, oiotz__ijji)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, dt64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                gta__sgoa = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(gta__sgoa))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        dxycm__tluc[uab__gmd])
                    if uekv__xsb == dlff__kigr or oiotz__ijji == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, oiotz__ijji)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                vcjnp__ecwr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vcjnp__ecwr)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    rfh__adlgq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if rfh__adlgq == dlff__kigr or uekv__xsb == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(rfh__adlgq, uekv__xsb)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                vcjnp__ecwr = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                uekv__xsb = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vcjnp__ecwr)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    rfh__adlgq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if uekv__xsb == dlff__kigr or rfh__adlgq == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(uekv__xsb, rfh__adlgq)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uass__qxh))
                gta__sgoa = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(gta__sgoa))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    fgyj__yolr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dxycm__tluc[uab__gmd]))
                    if oiotz__ijji == dlff__kigr or fgyj__yolr == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(fgyj__yolr, oiotz__ijji)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                swexh__mgdcn = np.empty(kxtju__yufz, timedelta64_dtype)
                dlff__kigr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uass__qxh))
                gta__sgoa = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                oiotz__ijji = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(gta__sgoa))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    fgyj__yolr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dxycm__tluc[uab__gmd]))
                    if oiotz__ijji == dlff__kigr or fgyj__yolr == dlff__kigr:
                        redg__qibz = dlff__kigr
                    else:
                        redg__qibz = op(oiotz__ijji, fgyj__yolr)
                    swexh__mgdcn[uab__gmd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        redg__qibz)
                return bodo.hiframes.pd_series_ext.init_series(swexh__mgdcn,
                    rrdgu__kqn, uzx__xhy)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            nnh__dwins = True
        else:
            nnh__dwins = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uass__qxh))
                evv__suq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                arbrt__jwire = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(evv__suq))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    azlvc__vfdcb = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dxycm__tluc[uab__gmd]))
                    if (azlvc__vfdcb == dlff__kigr or arbrt__jwire ==
                        dlff__kigr):
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(azlvc__vfdcb, arbrt__jwire)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(uass__qxh))
                ivk__nzz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                azlvc__vfdcb = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ivk__nzz))
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    arbrt__jwire = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(dxycm__tluc[uab__gmd]))
                    if (azlvc__vfdcb == dlff__kigr or arbrt__jwire ==
                        dlff__kigr):
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(azlvc__vfdcb, arbrt__jwire)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    azlvc__vfdcb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if azlvc__vfdcb == dlff__kigr or rhs.value == dlff__kigr:
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(azlvc__vfdcb, rhs.value)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    arbrt__jwire = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if arbrt__jwire == dlff__kigr or lhs.value == dlff__kigr:
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(lhs.value, arbrt__jwire)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            uass__qxh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                xmem__modvh = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                qhdps__euoe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xmem__modvh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    azlvc__vfdcb = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if azlvc__vfdcb == dlff__kigr or qhdps__euoe == dlff__kigr:
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(azlvc__vfdcb, qhdps__euoe)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            uass__qxh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                dxycm__tluc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                rrdgu__kqn = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                uzx__xhy = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                kxtju__yufz = len(dxycm__tluc)
                yke__bup = bodo.libs.bool_arr_ext.alloc_bool_array(kxtju__yufz)
                dlff__kigr = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    uass__qxh)
                xmem__modvh = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                qhdps__euoe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xmem__modvh)
                for uab__gmd in numba.parfors.parfor.internal_prange(
                    kxtju__yufz):
                    vcjnp__ecwr = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(dxycm__tluc[uab__gmd]))
                    if vcjnp__ecwr == dlff__kigr or qhdps__euoe == dlff__kigr:
                        redg__qibz = nnh__dwins
                    else:
                        redg__qibz = op(qhdps__euoe, vcjnp__ecwr)
                    yke__bup[uab__gmd] = redg__qibz
                return bodo.hiframes.pd_series_ext.init_series(yke__bup,
                    rrdgu__kqn, uzx__xhy)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'tz_convert', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for zwzin__fjlto in series_dt_unsupported_attrs:
        rrzr__snlb = 'Series.dt.' + zwzin__fjlto
        overload_attribute(SeriesDatetimePropertiesType, zwzin__fjlto)(
            create_unsupported_overload(rrzr__snlb))
    for dhz__zek in series_dt_unsupported_methods:
        rrzr__snlb = 'Series.dt.' + dhz__zek
        overload_method(SeriesDatetimePropertiesType, dhz__zek,
            no_unliteral=True)(create_unsupported_overload(rrzr__snlb))


_install_series_dt_unsupported()
