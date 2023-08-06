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
        zhj__mny = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(zhj__mny)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dkm__aqxr = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, dkm__aqxr)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        jehxc__mkqhd, = args
        vwyde__xmnij = signature.return_type
        kak__npix = cgutils.create_struct_proxy(vwyde__xmnij)(context, builder)
        kak__npix.obj = jehxc__mkqhd
        context.nrt.incref(builder, signature.args[0], jehxc__mkqhd)
        return kak__npix._getvalue()
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
        uaaus__lljv = 'def impl(S_dt):\n'
        uaaus__lljv += '    S = S_dt._obj\n'
        uaaus__lljv += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        uaaus__lljv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        uaaus__lljv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        uaaus__lljv += '    numba.parfors.parfor.init_prange()\n'
        uaaus__lljv += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            uaaus__lljv += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            uaaus__lljv += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        uaaus__lljv += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        uaaus__lljv += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        uaaus__lljv += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        uaaus__lljv += '            continue\n'
        uaaus__lljv += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            uaaus__lljv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                uaaus__lljv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            uaaus__lljv += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            ijd__fprcs = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            uaaus__lljv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            uaaus__lljv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            uaaus__lljv += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(ijd__fprcs[field]))
        elif field == 'is_leap_year':
            uaaus__lljv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            uaaus__lljv += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            ijd__fprcs = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            uaaus__lljv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            uaaus__lljv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            uaaus__lljv += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(ijd__fprcs[field]))
        else:
            uaaus__lljv += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            uaaus__lljv += '        out_arr[i] = ts.' + field + '\n'
        uaaus__lljv += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        craj__hvdgh = {}
        exec(uaaus__lljv, {'bodo': bodo, 'numba': numba, 'np': np}, craj__hvdgh
            )
        impl = craj__hvdgh['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        gpv__kgt = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(gpv__kgt)


_install_date_fields()


def create_date_method_overload(method):
    fhwuk__mgjou = method in ['day_name', 'month_name']
    if fhwuk__mgjou:
        uaaus__lljv = 'def overload_method(S_dt, locale=None):\n'
        uaaus__lljv += '    unsupported_args = dict(locale=locale)\n'
        uaaus__lljv += '    arg_defaults = dict(locale=None)\n'
        uaaus__lljv += '    bodo.utils.typing.check_unsupported_args(\n'
        uaaus__lljv += f"        'Series.dt.{method}',\n"
        uaaus__lljv += '        unsupported_args,\n'
        uaaus__lljv += '        arg_defaults,\n'
        uaaus__lljv += "        package_name='pandas',\n"
        uaaus__lljv += "        module_name='Series',\n"
        uaaus__lljv += '    )\n'
    else:
        uaaus__lljv = 'def overload_method(S_dt):\n'
    uaaus__lljv += '    if not S_dt.stype.dtype == bodo.datetime64ns:\n'
    uaaus__lljv += '        return\n'
    if fhwuk__mgjou:
        uaaus__lljv += '    def impl(S_dt, locale=None):\n'
    else:
        uaaus__lljv += '    def impl(S_dt):\n'
    uaaus__lljv += '        S = S_dt._obj\n'
    uaaus__lljv += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    uaaus__lljv += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    uaaus__lljv += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    uaaus__lljv += '        numba.parfors.parfor.init_prange()\n'
    uaaus__lljv += '        n = len(arr)\n'
    if fhwuk__mgjou:
        uaaus__lljv += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        uaaus__lljv += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    uaaus__lljv += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    uaaus__lljv += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    uaaus__lljv += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    uaaus__lljv += '                continue\n'
    uaaus__lljv += """            ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(arr[i])
"""
    uaaus__lljv += f'            method_val = ts.{method}()\n'
    if fhwuk__mgjou:
        uaaus__lljv += '            out_arr[i] = method_val\n'
    else:
        uaaus__lljv += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    uaaus__lljv += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    uaaus__lljv += '    return impl\n'
    craj__hvdgh = {}
    exec(uaaus__lljv, {'bodo': bodo, 'numba': numba, 'np': np}, craj__hvdgh)
    overload_method = craj__hvdgh['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        gpv__kgt = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gpv__kgt)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not S_dt.stype.dtype == types.NPDatetime('ns'):
        return

    def impl(S_dt):
        kghz__mson = S_dt._obj
        oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(kghz__mson)
        htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(kghz__mson)
        zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(kghz__mson)
        numba.parfors.parfor.init_prange()
        kzhy__dhbyt = len(oov__tleva)
        tpa__lts = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            kzhy__dhbyt)
        for yxz__afwr in numba.parfors.parfor.internal_prange(kzhy__dhbyt):
            wva__fwp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                oov__tleva[yxz__afwr])
            zxmml__bve = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(wva__fwp))
            tpa__lts[yxz__afwr] = datetime.date(zxmml__bve.year, zxmml__bve
                .month, zxmml__bve.day)
        return bodo.hiframes.pd_series_ext.init_series(tpa__lts, htp__doumg,
            zhj__mny)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and S_dt.stype.dtype ==
            types.NPDatetime('ns')):
            return
        if attr == 'components':
            kaqsg__gajkj = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            jgq__emdt = 'convert_numpy_timedelta64_to_pd_timedelta'
            skexd__kgnxi = 'np.empty(n, np.int64)'
            bet__jbl = attr
        elif attr == 'isocalendar':
            kaqsg__gajkj = ['year', 'week', 'day']
            jgq__emdt = 'convert_datetime64_to_timestamp'
            skexd__kgnxi = (
                'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)')
            bet__jbl = attr + '()'
        uaaus__lljv = 'def impl(S_dt):\n'
        uaaus__lljv += '    S = S_dt._obj\n'
        uaaus__lljv += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        uaaus__lljv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        uaaus__lljv += '    numba.parfors.parfor.init_prange()\n'
        uaaus__lljv += '    n = len(arr)\n'
        for field in kaqsg__gajkj:
            uaaus__lljv += '    {} = {}\n'.format(field, skexd__kgnxi)
        uaaus__lljv += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        uaaus__lljv += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in kaqsg__gajkj:
            uaaus__lljv += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        uaaus__lljv += '            continue\n'
        mcxzl__ygsj = '(' + '[i], '.join(kaqsg__gajkj) + '[i])'
        uaaus__lljv += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(mcxzl__ygsj, jgq__emdt, bet__jbl))
        dskyh__kmscg = '(' + ', '.join(kaqsg__gajkj) + ')'
        ojqf__zrnzy = "('" + "', '".join(kaqsg__gajkj) + "')"
        uaaus__lljv += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, {})\n'
            .format(dskyh__kmscg, ojqf__zrnzy))
        craj__hvdgh = {}
        exec(uaaus__lljv, {'bodo': bodo, 'numba': numba, 'np': np}, craj__hvdgh
            )
        impl = craj__hvdgh['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    txrvk__sem = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, sfin__btgz in txrvk__sem:
        gpv__kgt = create_series_dt_df_output_overload(attr)
        sfin__btgz(SeriesDatetimePropertiesType, attr, inline='always')(
            gpv__kgt)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        uaaus__lljv = 'def impl(S_dt):\n'
        uaaus__lljv += '    S = S_dt._obj\n'
        uaaus__lljv += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        uaaus__lljv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        uaaus__lljv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        uaaus__lljv += '    numba.parfors.parfor.init_prange()\n'
        uaaus__lljv += '    n = len(A)\n'
        uaaus__lljv += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        uaaus__lljv += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        uaaus__lljv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        uaaus__lljv += '            bodo.libs.array_kernels.setna(B, i)\n'
        uaaus__lljv += '            continue\n'
        uaaus__lljv += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            uaaus__lljv += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            uaaus__lljv += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            uaaus__lljv += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            uaaus__lljv += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        uaaus__lljv += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        craj__hvdgh = {}
        exec(uaaus__lljv, {'numba': numba, 'np': np, 'bodo': bodo}, craj__hvdgh
            )
        impl = craj__hvdgh['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        uaaus__lljv = 'def impl(S_dt):\n'
        uaaus__lljv += '    S = S_dt._obj\n'
        uaaus__lljv += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        uaaus__lljv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        uaaus__lljv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        uaaus__lljv += '    numba.parfors.parfor.init_prange()\n'
        uaaus__lljv += '    n = len(A)\n'
        if method == 'total_seconds':
            uaaus__lljv += '    B = np.empty(n, np.float64)\n'
        else:
            uaaus__lljv += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        uaaus__lljv += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        uaaus__lljv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        uaaus__lljv += '            bodo.libs.array_kernels.setna(B, i)\n'
        uaaus__lljv += '            continue\n'
        uaaus__lljv += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            uaaus__lljv += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            uaaus__lljv += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            uaaus__lljv += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            uaaus__lljv += '    return B\n'
        craj__hvdgh = {}
        exec(uaaus__lljv, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, craj__hvdgh)
        impl = craj__hvdgh['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        gpv__kgt = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(gpv__kgt)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        gpv__kgt = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gpv__kgt)


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
        kghz__mson = S_dt._obj
        dhavf__zfeqf = bodo.hiframes.pd_series_ext.get_series_data(kghz__mson)
        htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(kghz__mson)
        zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(kghz__mson)
        numba.parfors.parfor.init_prange()
        kzhy__dhbyt = len(dhavf__zfeqf)
        titfc__doewb = bodo.libs.str_arr_ext.pre_alloc_string_array(kzhy__dhbyt
            , -1)
        for ryzb__giseq in numba.parfors.parfor.internal_prange(kzhy__dhbyt):
            if bodo.libs.array_kernels.isna(dhavf__zfeqf, ryzb__giseq):
                bodo.libs.array_kernels.setna(titfc__doewb, ryzb__giseq)
                continue
            titfc__doewb[ryzb__giseq
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                dhavf__zfeqf[ryzb__giseq]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(titfc__doewb,
            htp__doumg, zhj__mny)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'):
            return
        pmlq__whmx = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        rwht__kdkr = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', pmlq__whmx,
            rwht__kdkr, package_name='pandas', module_name='Series')
        uaaus__lljv = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        uaaus__lljv += '    S = S_dt._obj\n'
        uaaus__lljv += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        uaaus__lljv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        uaaus__lljv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        uaaus__lljv += '    numba.parfors.parfor.init_prange()\n'
        uaaus__lljv += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            uaaus__lljv += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            uaaus__lljv += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        uaaus__lljv += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        uaaus__lljv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        uaaus__lljv += '            bodo.libs.array_kernels.setna(B, i)\n'
        uaaus__lljv += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            ilamd__qol = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            dmko__hxik = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            ilamd__qol = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            dmko__hxik = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        uaaus__lljv += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            dmko__hxik, ilamd__qol, method)
        uaaus__lljv += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        craj__hvdgh = {}
        exec(uaaus__lljv, {'numba': numba, 'np': np, 'bodo': bodo}, craj__hvdgh
            )
        impl = craj__hvdgh['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    lkhth__sghv = ['ceil', 'floor', 'round']
    for method in lkhth__sghv:
        gpv__kgt = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gpv__kgt)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ojewq__bfao = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kqzj__bfflp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kzhy__dhbyt = len(ojewq__bfao)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    jph__ohfyz = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(ojewq__bfao[yxz__afwr]))
                    apzeb__mswr = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(kqzj__bfflp[yxz__afwr]))
                    if jph__ohfyz == wrc__tkzu or apzeb__mswr == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(jph__ohfyz, apzeb__mswr)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kqzj__bfflp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, dt64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(kqzj__bfflp[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or poas__vqnf == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, poas__vqnf)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kqzj__bfflp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, dt64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(kqzj__bfflp[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or poas__vqnf == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, poas__vqnf)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                mxat__ybwun = rhs.value
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or mxat__ybwun == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, mxat__ybwun)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                mxat__ybwun = lhs.value
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if mxat__ybwun == wrc__tkzu or oifmk__cqtub == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(mxat__ybwun, oifmk__cqtub)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, dt64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                rtp__mirng = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rtp__mirng))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or poas__vqnf == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, poas__vqnf)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, dt64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                rtp__mirng = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rtp__mirng))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    oifmk__cqtub = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or poas__vqnf == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, poas__vqnf)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                wva__fwp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                oifmk__cqtub = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wva__fwp)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    sdvad__lxvt = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if sdvad__lxvt == wrc__tkzu or oifmk__cqtub == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(sdvad__lxvt, oifmk__cqtub)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                wva__fwp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                oifmk__cqtub = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wva__fwp)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    sdvad__lxvt = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if oifmk__cqtub == wrc__tkzu or sdvad__lxvt == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(oifmk__cqtub, sdvad__lxvt)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wab__fdr))
                rtp__mirng = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rtp__mirng))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    sqmu__pxsg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oov__tleva[yxz__afwr]))
                    if poas__vqnf == wrc__tkzu or sqmu__pxsg == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(sqmu__pxsg, poas__vqnf)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                kghz__mson = np.empty(kzhy__dhbyt, timedelta64_dtype)
                wrc__tkzu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wab__fdr))
                rtp__mirng = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                poas__vqnf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rtp__mirng))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    sqmu__pxsg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oov__tleva[yxz__afwr]))
                    if poas__vqnf == wrc__tkzu or sqmu__pxsg == wrc__tkzu:
                        ytsdk__ajd = wrc__tkzu
                    else:
                        ytsdk__ajd = op(poas__vqnf, sqmu__pxsg)
                    kghz__mson[yxz__afwr
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        ytsdk__ajd)
                return bodo.hiframes.pd_series_ext.init_series(kghz__mson,
                    htp__doumg, zhj__mny)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            mdai__hxn = True
        else:
            mdai__hxn = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wab__fdr))
                kmlg__dzczv = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                hyc__tuwhr = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kmlg__dzczv))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    grlix__xkhov = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oov__tleva[yxz__afwr]))
                    if grlix__xkhov == wrc__tkzu or hyc__tuwhr == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(grlix__xkhov, hyc__tuwhr)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(wab__fdr))
                eprs__musb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                grlix__xkhov = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(eprs__musb))
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    hyc__tuwhr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(oov__tleva[yxz__afwr]))
                    if grlix__xkhov == wrc__tkzu or hyc__tuwhr == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(grlix__xkhov, hyc__tuwhr)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    grlix__xkhov = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if grlix__xkhov == wrc__tkzu or rhs.value == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(grlix__xkhov, rhs.value)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    hyc__tuwhr = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if hyc__tuwhr == wrc__tkzu or lhs.value == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(lhs.value, hyc__tuwhr)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            wab__fdr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                flo__afzjt = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                wrsvy__esqk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    flo__afzjt)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    grlix__xkhov = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(oov__tleva[yxz__afwr]))
                    if grlix__xkhov == wrc__tkzu or wrsvy__esqk == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(grlix__xkhov, wrsvy__esqk)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            wab__fdr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                oov__tleva = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                htp__doumg = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                zhj__mny = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                kzhy__dhbyt = len(oov__tleva)
                tpa__lts = bodo.libs.bool_arr_ext.alloc_bool_array(kzhy__dhbyt)
                wrc__tkzu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wab__fdr)
                flo__afzjt = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                wrsvy__esqk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    flo__afzjt)
                for yxz__afwr in numba.parfors.parfor.internal_prange(
                    kzhy__dhbyt):
                    wva__fwp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        oov__tleva[yxz__afwr])
                    if wva__fwp == wrc__tkzu or wrsvy__esqk == wrc__tkzu:
                        ytsdk__ajd = mdai__hxn
                    else:
                        ytsdk__ajd = op(wrsvy__esqk, wva__fwp)
                    tpa__lts[yxz__afwr] = ytsdk__ajd
                return bodo.hiframes.pd_series_ext.init_series(tpa__lts,
                    htp__doumg, zhj__mny)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'tz_convert', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for flh__qhkc in series_dt_unsupported_attrs:
        axk__nnf = 'Series.dt.' + flh__qhkc
        overload_attribute(SeriesDatetimePropertiesType, flh__qhkc)(
            create_unsupported_overload(axk__nnf))
    for pmkex__qbly in series_dt_unsupported_methods:
        axk__nnf = 'Series.dt.' + pmkex__qbly
        overload_method(SeriesDatetimePropertiesType, pmkex__qbly,
            no_unliteral=True)(create_unsupported_overload(axk__nnf))


_install_series_dt_unsupported()
