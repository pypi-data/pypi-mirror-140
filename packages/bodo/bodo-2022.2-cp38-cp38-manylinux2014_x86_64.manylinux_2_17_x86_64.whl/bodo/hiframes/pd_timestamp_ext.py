import calendar
import datetime
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import ConcreteTemplate, infer_global, signature
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo.libs.str_ext
import bodo.utils.utils
from bodo.hiframes.datetime_date_ext import DatetimeDateType, _ord2ymd, _ymd2ord, get_isocalendar
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, _no_input, datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdatetime_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import BodoError, check_unsupported_args, get_overload_const_str, is_iterable_type, is_overload_constant_int, is_overload_constant_str, is_overload_none, raise_bodo_error
ll.add_symbol('extract_year_days', hdatetime_ext.extract_year_days)
ll.add_symbol('get_month_day', hdatetime_ext.get_month_day)
ll.add_symbol('npy_datetimestruct_to_datetime', hdatetime_ext.
    npy_datetimestruct_to_datetime)
npy_datetimestruct_to_datetime = types.ExternalFunction(
    'npy_datetimestruct_to_datetime', types.int64(types.int64, types.int32,
    types.int32, types.int32, types.int32, types.int32, types.int32))
date_fields = ['year', 'month', 'day', 'hour', 'minute', 'second',
    'microsecond', 'nanosecond', 'quarter', 'dayofyear', 'day_of_year',
    'dayofweek', 'day_of_week', 'daysinmonth', 'days_in_month',
    'is_leap_year', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end', 'week', 'weekofyear',
    'weekday']
date_methods = ['normalize', 'day_name', 'month_name']
timedelta_fields = ['days', 'seconds', 'microseconds', 'nanoseconds']
timedelta_methods = ['total_seconds', 'to_pytimedelta']
iNaT = pd._libs.tslibs.iNaT


class PandasTimestampType(types.Type):

    def __init__(self):
        super(PandasTimestampType, self).__init__(name='PandasTimestampType()')


pd_timestamp_type = PandasTimestampType()


@typeof_impl.register(pd.Timestamp)
def typeof_pd_timestamp(val, c):
    return pd_timestamp_type


ts_field_typ = types.int64


@register_model(PandasTimestampType)
class PandasTimestampModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gqly__mte = [('year', ts_field_typ), ('month', ts_field_typ), (
            'day', ts_field_typ), ('hour', ts_field_typ), ('minute',
            ts_field_typ), ('second', ts_field_typ), ('microsecond',
            ts_field_typ), ('nanosecond', ts_field_typ), ('value',
            ts_field_typ)]
        models.StructModel.__init__(self, dmm, fe_type, gqly__mte)


make_attribute_wrapper(PandasTimestampType, 'year', 'year')
make_attribute_wrapper(PandasTimestampType, 'month', 'month')
make_attribute_wrapper(PandasTimestampType, 'day', 'day')
make_attribute_wrapper(PandasTimestampType, 'hour', 'hour')
make_attribute_wrapper(PandasTimestampType, 'minute', 'minute')
make_attribute_wrapper(PandasTimestampType, 'second', 'second')
make_attribute_wrapper(PandasTimestampType, 'microsecond', 'microsecond')
make_attribute_wrapper(PandasTimestampType, 'nanosecond', 'nanosecond')
make_attribute_wrapper(PandasTimestampType, 'value', 'value')


@unbox(PandasTimestampType)
def unbox_pandas_timestamp(typ, val, c):
    ueg__hsmhu = c.pyapi.object_getattr_string(val, 'year')
    wqv__jbz = c.pyapi.object_getattr_string(val, 'month')
    rete__cvjjl = c.pyapi.object_getattr_string(val, 'day')
    hpwng__sloew = c.pyapi.object_getattr_string(val, 'hour')
    npww__via = c.pyapi.object_getattr_string(val, 'minute')
    wlgv__nsw = c.pyapi.object_getattr_string(val, 'second')
    jorgo__zovlq = c.pyapi.object_getattr_string(val, 'microsecond')
    alcn__pnbh = c.pyapi.object_getattr_string(val, 'nanosecond')
    aqgdo__qdcz = c.pyapi.object_getattr_string(val, 'value')
    pgyl__hoi = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pgyl__hoi.year = c.pyapi.long_as_longlong(ueg__hsmhu)
    pgyl__hoi.month = c.pyapi.long_as_longlong(wqv__jbz)
    pgyl__hoi.day = c.pyapi.long_as_longlong(rete__cvjjl)
    pgyl__hoi.hour = c.pyapi.long_as_longlong(hpwng__sloew)
    pgyl__hoi.minute = c.pyapi.long_as_longlong(npww__via)
    pgyl__hoi.second = c.pyapi.long_as_longlong(wlgv__nsw)
    pgyl__hoi.microsecond = c.pyapi.long_as_longlong(jorgo__zovlq)
    pgyl__hoi.nanosecond = c.pyapi.long_as_longlong(alcn__pnbh)
    pgyl__hoi.value = c.pyapi.long_as_longlong(aqgdo__qdcz)
    c.pyapi.decref(ueg__hsmhu)
    c.pyapi.decref(wqv__jbz)
    c.pyapi.decref(rete__cvjjl)
    c.pyapi.decref(hpwng__sloew)
    c.pyapi.decref(npww__via)
    c.pyapi.decref(wlgv__nsw)
    c.pyapi.decref(jorgo__zovlq)
    c.pyapi.decref(alcn__pnbh)
    c.pyapi.decref(aqgdo__qdcz)
    iifmr__ydf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pgyl__hoi._getvalue(), is_error=iifmr__ydf)


@box(PandasTimestampType)
def box_pandas_timestamp(typ, val, c):
    mqq__qxcai = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ueg__hsmhu = c.pyapi.long_from_longlong(mqq__qxcai.year)
    wqv__jbz = c.pyapi.long_from_longlong(mqq__qxcai.month)
    rete__cvjjl = c.pyapi.long_from_longlong(mqq__qxcai.day)
    hpwng__sloew = c.pyapi.long_from_longlong(mqq__qxcai.hour)
    npww__via = c.pyapi.long_from_longlong(mqq__qxcai.minute)
    wlgv__nsw = c.pyapi.long_from_longlong(mqq__qxcai.second)
    qxi__xtqd = c.pyapi.long_from_longlong(mqq__qxcai.microsecond)
    tpc__nkb = c.pyapi.long_from_longlong(mqq__qxcai.nanosecond)
    ejmtt__coax = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timestamp))
    res = c.pyapi.call_function_objargs(ejmtt__coax, (ueg__hsmhu, wqv__jbz,
        rete__cvjjl, hpwng__sloew, npww__via, wlgv__nsw, qxi__xtqd, tpc__nkb))
    c.pyapi.decref(ueg__hsmhu)
    c.pyapi.decref(wqv__jbz)
    c.pyapi.decref(rete__cvjjl)
    c.pyapi.decref(hpwng__sloew)
    c.pyapi.decref(npww__via)
    c.pyapi.decref(wlgv__nsw)
    c.pyapi.decref(qxi__xtqd)
    c.pyapi.decref(tpc__nkb)
    return res


@intrinsic
def init_timestamp(typingctx, year, month, day, hour, minute, second,
    microsecond, nanosecond, value=None):

    def codegen(context, builder, sig, args):
        (year, month, day, hour, minute, second, wpubk__ldj, utf__qxwpm, value
            ) = args
        ts = cgutils.create_struct_proxy(pd_timestamp_type)(context, builder)
        ts.year = year
        ts.month = month
        ts.day = day
        ts.hour = hour
        ts.minute = minute
        ts.second = second
        ts.microsecond = wpubk__ldj
        ts.nanosecond = utf__qxwpm
        ts.value = value
        return ts._getvalue()
    return pd_timestamp_type(types.int64, types.int64, types.int64, types.
        int64, types.int64, types.int64, types.int64, types.int64, types.int64
        ), codegen


@numba.generated_jit
def zero_if_none(value):
    if value == types.none:
        return lambda value: 0
    return lambda value: value


@lower_constant(PandasTimestampType)
def constant_timestamp(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    nanosecond = context.get_constant(types.int64, pyval.nanosecond)
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct((year, month, day, hour, minute,
        second, microsecond, nanosecond, value))


@overload(pd.Timestamp, no_unliteral=True)
def overload_pd_timestamp(ts_input=_no_input, freq=None, tz=None, unit=None,
    year=None, month=None, day=None, hour=None, minute=None, second=None,
    microsecond=None, nanosecond=None, tzinfo=None):
    if ts_input == _no_input or getattr(ts_input, 'value', None) == _no_input:

        def impl_kw(ts_input=_no_input, freq=None, tz=None, unit=None, year
            =None, month=None, day=None, hour=None, minute=None, second=
            None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value)
        return impl_kw
    if isinstance(types.unliteral(freq), types.Integer):

        def impl_pos(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(ts_input, freq, tz,
                zero_if_none(unit), zero_if_none(year), zero_if_none(month),
                zero_if_none(day))
            value += zero_if_none(hour)
            return init_timestamp(ts_input, freq, tz, zero_if_none(unit),
                zero_if_none(year), zero_if_none(month), zero_if_none(day),
                zero_if_none(hour), value)
        return impl_pos
    if isinstance(ts_input, types.Number):
        if is_overload_none(unit):
            unit = 'ns'
        if not is_overload_constant_str(unit):
            raise BodoError(
                'pandas.Timedelta(): unit argument must be a constant str')
        unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
            get_overload_const_str(unit))
        zuoy__zzkgc, precision = (pd._libs.tslibs.conversion.
            precision_from_unit(unit))
        if isinstance(ts_input, types.Integer):

            def impl_int(ts_input=_no_input, freq=None, tz=None, unit=None,
                year=None, month=None, day=None, hour=None, minute=None,
                second=None, microsecond=None, nanosecond=None, tzinfo=None):
                value = ts_input * zuoy__zzkgc
                return convert_datetime64_to_timestamp(integer_to_dt64(value))
            return impl_int

        def impl_float(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            jclk__kyuhm = np.int64(ts_input)
            mua__ujh = ts_input - jclk__kyuhm
            if precision:
                mua__ujh = np.round(mua__ujh, precision)
            value = jclk__kyuhm * zuoy__zzkgc + np.int64(mua__ujh * zuoy__zzkgc
                )
            return convert_datetime64_to_timestamp(integer_to_dt64(value))
        return impl_float
    if ts_input == bodo.string_type or is_overload_constant_str(ts_input):
        types.pd_timestamp_type = pd_timestamp_type

        def impl_str(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            with numba.objmode(res='pd_timestamp_type'):
                res = pd.Timestamp(ts_input)
            return res
        return impl_str
    if ts_input == pd_timestamp_type:
        return (lambda ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None: ts_input)
    if ts_input == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:

        def impl_datetime(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            hour = ts_input.hour
            minute = ts_input.minute
            second = ts_input.second
            microsecond = ts_input.microsecond
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value)
        return impl_datetime
    if ts_input == bodo.hiframes.datetime_date_ext.datetime_date_type:

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value)
        return impl_date


@overload_attribute(PandasTimestampType, 'dayofyear')
@overload_attribute(PandasTimestampType, 'day_of_year')
def overload_pd_dayofyear(ptt):

    def pd_dayofyear(ptt):
        return get_day_of_year(ptt.year, ptt.month, ptt.day)
    return pd_dayofyear


@overload_method(PandasTimestampType, 'weekday')
@overload_attribute(PandasTimestampType, 'dayofweek')
@overload_attribute(PandasTimestampType, 'day_of_week')
def overload_pd_dayofweek(ptt):

    def pd_dayofweek(ptt):
        return get_day_of_week(ptt.year, ptt.month, ptt.day)
    return pd_dayofweek


@overload_attribute(PandasTimestampType, 'week')
@overload_attribute(PandasTimestampType, 'weekofyear')
def overload_week_number(ptt):

    def pd_week_number(ptt):
        cfhe__gfna, splo__lyg, cfhe__gfna = get_isocalendar(ptt.year, ptt.
            month, ptt.day)
        return splo__lyg
    return pd_week_number


@overload_method(PandasTimestampType, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(val.value)


@overload_attribute(PandasTimestampType, 'days_in_month')
@overload_attribute(PandasTimestampType, 'daysinmonth')
def overload_pd_daysinmonth(ptt):

    def pd_daysinmonth(ptt):
        return get_days_in_month(ptt.year, ptt.month)
    return pd_daysinmonth


@overload_attribute(PandasTimestampType, 'is_leap_year')
def overload_pd_is_leap_year(ptt):

    def pd_is_leap_year(ptt):
        return is_leap_year(ptt.year)
    return pd_is_leap_year


@overload_attribute(PandasTimestampType, 'is_month_start')
def overload_pd_is_month_start(ptt):

    def pd_is_month_start(ptt):
        return ptt.day == 1
    return pd_is_month_start


@overload_attribute(PandasTimestampType, 'is_month_end')
def overload_pd_is_month_end(ptt):

    def pd_is_month_end(ptt):
        return ptt.day == get_days_in_month(ptt.year, ptt.month)
    return pd_is_month_end


@overload_attribute(PandasTimestampType, 'is_quarter_start')
def overload_pd_is_quarter_start(ptt):

    def pd_is_quarter_start(ptt):
        return ptt.day == 1 and ptt.month % 3 == 1
    return pd_is_quarter_start


@overload_attribute(PandasTimestampType, 'is_quarter_end')
def overload_pd_is_quarter_end(ptt):

    def pd_is_quarter_end(ptt):
        return ptt.month % 3 == 0 and ptt.day == get_days_in_month(ptt.year,
            ptt.month)
    return pd_is_quarter_end


@overload_attribute(PandasTimestampType, 'is_year_start')
def overload_pd_is_year_start(ptt):

    def pd_is_year_start(ptt):
        return ptt.day == 1 and ptt.month == 1
    return pd_is_year_start


@overload_attribute(PandasTimestampType, 'is_year_end')
def overload_pd_is_year_end(ptt):

    def pd_is_year_end(ptt):
        return ptt.day == 31 and ptt.month == 12
    return pd_is_year_end


@overload_attribute(PandasTimestampType, 'quarter')
def overload_quarter(ptt):

    def quarter(ptt):
        return (ptt.month - 1) // 3 + 1
    return quarter


@overload_method(PandasTimestampType, 'date', no_unliteral=True)
def overload_pd_timestamp_date(ptt):

    def pd_timestamp_date_impl(ptt):
        return datetime.date(ptt.year, ptt.month, ptt.day)
    return pd_timestamp_date_impl


@overload_method(PandasTimestampType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(ptt):

    def impl(ptt):
        year, splo__lyg, rjwq__ajcx = get_isocalendar(ptt.year, ptt.month,
            ptt.day)
        return year, splo__lyg, rjwq__ajcx
    return impl


@overload_method(PandasTimestampType, 'isoformat', no_unliteral=True)
def overload_pd_timestamp_isoformat(ts, sep=None):
    if is_overload_none(sep):

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            kmwj__mxsge = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + 'T' + kmwj__mxsge
            return res
        return timestamp_isoformat_impl
    else:

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            kmwj__mxsge = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + sep + kmwj__mxsge
            return res
    return timestamp_isoformat_impl


@overload_method(PandasTimestampType, 'normalize', no_unliteral=True)
def overload_pd_timestamp_normalize(ptt):

    def impl(ptt):
        return pd.Timestamp(year=ptt.year, month=ptt.month, day=ptt.day)
    return impl


@overload_method(PandasTimestampType, 'day_name', no_unliteral=True)
def overload_pd_timestamp_day_name(ptt, locale=None):
    gxvy__vkgj = dict(locale=locale)
    qrosw__zrabm = dict(locale=None)
    check_unsupported_args('Timestamp.day_name', gxvy__vkgj, qrosw__zrabm,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        zigd__wgqmj = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday')
        cfhe__gfna, cfhe__gfna, taz__tze = ptt.isocalendar()
        return zigd__wgqmj[taz__tze - 1]
    return impl


@overload_method(PandasTimestampType, 'month_name', no_unliteral=True)
def overload_pd_timestamp_month_name(ptt, locale=None):
    gxvy__vkgj = dict(locale=locale)
    qrosw__zrabm = dict(locale=None)
    check_unsupported_args('Timestamp.month_name', gxvy__vkgj, qrosw__zrabm,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        xuzpj__znpp = ('January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November',
            'December')
        return xuzpj__znpp[ptt.month - 1]
    return impl


@numba.njit
def str_2d(a):
    res = str(a)
    if len(res) == 1:
        return '0' + res
    return res


@overload(str, no_unliteral=True)
def ts_str_overload(a):
    if a == pd_timestamp_type:
        return lambda a: a.isoformat(' ')


@intrinsic
def extract_year_days(typingctx, dt64_t=None):
    assert dt64_t in (types.int64, types.NPDatetime('ns'))

    def codegen(context, builder, sig, args):
        ena__gvgdi = cgutils.alloca_once(builder, lir.IntType(64))
        builder.store(args[0], ena__gvgdi)
        year = cgutils.alloca_once(builder, lir.IntType(64))
        lszcb__kgbl = cgutils.alloca_once(builder, lir.IntType(64))
        biwk__ieeoi = lir.FunctionType(lir.VoidType(), [lir.IntType(64).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        jcip__rlinm = cgutils.get_or_insert_function(builder.module,
            biwk__ieeoi, name='extract_year_days')
        builder.call(jcip__rlinm, [ena__gvgdi, year, lszcb__kgbl])
        return cgutils.pack_array(builder, [builder.load(ena__gvgdi),
            builder.load(year), builder.load(lszcb__kgbl)])
    return types.Tuple([types.int64, types.int64, types.int64])(dt64_t
        ), codegen


@intrinsic
def get_month_day(typingctx, year_t, days_t=None):
    assert year_t == types.int64
    assert days_t == types.int64

    def codegen(context, builder, sig, args):
        month = cgutils.alloca_once(builder, lir.IntType(64))
        day = cgutils.alloca_once(builder, lir.IntType(64))
        biwk__ieeoi = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        jcip__rlinm = cgutils.get_or_insert_function(builder.module,
            biwk__ieeoi, name='get_month_day')
        builder.call(jcip__rlinm, [args[0], args[1], month, day])
        return cgutils.pack_array(builder, [builder.load(month), builder.
            load(day)])
    return types.Tuple([types.int64, types.int64])(types.int64, types.int64
        ), codegen


@register_jitable
def get_day_of_year(year, month, day):
    uckby__zdtmj = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 
        365, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    kvt__sydln = is_leap_year(year)
    uhlop__ytdk = uckby__zdtmj[kvt__sydln * 13 + month - 1]
    rrx__inm = uhlop__ytdk + day
    return rrx__inm


@register_jitable
def get_day_of_week(y, m, d):
    enk__xvhez = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    day = (y + y // 4 - y // 100 + y // 400 + enk__xvhez[m - 1] + d) % 7
    return (day + 6) % 7


@register_jitable
def get_days_in_month(year, month):
    is_leap_year = year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)
    jkil__uwi = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 29, 31,
        30, 31, 30, 31, 31, 30, 31, 30, 31]
    return jkil__uwi[12 * is_leap_year + month - 1]


@register_jitable
def is_leap_year(year):
    return year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)


@numba.njit(no_cpython_wrapper=True)
def convert_datetime64_to_timestamp(dt64):
    ena__gvgdi, year, lszcb__kgbl = extract_year_days(dt64)
    month, day = get_month_day(year, lszcb__kgbl)
    return pd.Timestamp(year, month, day, ena__gvgdi // (60 * 60 * 
        1000000000), ena__gvgdi // (60 * 1000000000) % 60, ena__gvgdi // 
        1000000000 % 60, ena__gvgdi // 1000 % 1000000, ena__gvgdi % 1000)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_datetime_timedelta(dt64):
    yhx__mumi = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    uta__rvf = yhx__mumi // (86400 * 1000000000)
    kzp__zcn = yhx__mumi - uta__rvf * 86400 * 1000000000
    teh__uzdn = kzp__zcn // 1000000000
    horm__nko = kzp__zcn - teh__uzdn * 1000000000
    sdg__cxhbl = horm__nko // 1000
    return datetime.timedelta(uta__rvf, teh__uzdn, sdg__cxhbl)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_pd_timedelta(dt64):
    yhx__mumi = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    return pd.Timedelta(yhx__mumi)


@intrinsic
def integer_to_timedelta64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPTimedelta('ns')(val), codegen


@intrinsic
def integer_to_dt64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPDatetime('ns')(val), codegen


@intrinsic
def dt64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(types.NPDatetime('ns'), types.int64)
def cast_dt64_to_integer(context, builder, fromty, toty, val):
    return val


@overload_method(types.NPDatetime, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@overload_method(types.NPTimedelta, '__hash__', no_unliteral=True)
def td64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@intrinsic
def timedelta64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(bodo.timedelta64ns, types.int64)
def cast_td64_to_integer(context, builder, fromty, toty, val):
    return val


@numba.njit
def parse_datetime_str(val):
    with numba.objmode(res='int64'):
        res = pd.Timestamp(val).value
    return integer_to_dt64(res)


@numba.njit
def datetime_timedelta_to_timedelta64(val):
    with numba.objmode(res='NPTimedelta("ns")'):
        res = pd.to_timedelta(val)
        res = res.to_timedelta64()
    return res


@numba.njit
def series_str_dt64_astype(data):
    with numba.objmode(res="NPDatetime('ns')[::1]"):
        res = pd.Series(data).astype('datetime64[ns]').values
    return res


@numba.njit
def series_str_td64_astype(data):
    with numba.objmode(res="NPTimedelta('ns')[::1]"):
        res = data.astype('timedelta64[ns]')
    return res


@numba.njit
def datetime_datetime_to_dt64(val):
    with numba.objmode(res='NPDatetime("ns")'):
        res = np.datetime64(val).astype('datetime64[ns]')
    return res


@register_jitable
def datetime_date_arr_to_dt64_arr(arr):
    with numba.objmode(res='NPDatetime("ns")[:]'):
        res = np.array(arr, dtype='datetime64[ns]')
    return res


types.pd_timestamp_type = pd_timestamp_type


@register_jitable
def to_datetime_scalar(a, errors='raise', dayfirst=False, yearfirst=False,
    utc=None, format=None, exact=True, unit=None, infer_datetime_format=
    False, origin='unix', cache=True):
    with numba.objmode(t='pd_timestamp_type'):
        t = pd.to_datetime(a, errors=errors, dayfirst=dayfirst, yearfirst=
            yearfirst, utc=utc, format=format, exact=exact, unit=unit,
            infer_datetime_format=infer_datetime_format, origin=origin,
            cache=cache)
    return t


@numba.njit
def pandas_string_array_to_datetime(arr, errors, dayfirst, yearfirst, utc,
    format, exact, unit, infer_datetime_format, origin, cache):
    with numba.objmode(result='datetime_index'):
        result = pd.to_datetime(arr, errors=errors, dayfirst=dayfirst,
            yearfirst=yearfirst, utc=utc, format=format, exact=exact, unit=
            unit, infer_datetime_format=infer_datetime_format, origin=
            origin, cache=cache)
    return result


@overload(pd.to_datetime, inline='always', no_unliteral=True)
def overload_to_datetime(arg_a, errors='raise', dayfirst=False, yearfirst=
    False, utc=None, format=None, exact=True, unit=None,
    infer_datetime_format=False, origin='unix', cache=True):
    if arg_a == bodo.string_type or is_overload_constant_str(arg_a
        ) or is_overload_constant_int(arg_a) or isinstance(arg_a, types.Integer
        ):

        def pd_to_datetime_impl(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return to_datetime_scalar(arg_a, errors=errors, dayfirst=
                dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                exact=exact, unit=unit, infer_datetime_format=
                infer_datetime_format, origin=origin, cache=cache)
        return pd_to_datetime_impl
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            kpy__lgfz = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nnzrd__hqg = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            sxv__snldp = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_datetime(arr, errors=errors, dayfirst=dayfirst,
                yearfirst=yearfirst, utc=utc, format=format, exact=exact,
                unit=unit, infer_datetime_format=infer_datetime_format,
                origin=origin, cache=cache))
            return bodo.hiframes.pd_series_ext.init_series(sxv__snldp,
                kpy__lgfz, nnzrd__hqg)
        return impl_series
    if arg_a == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        phsxv__hyh = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            ncqrh__kujw = len(arg_a)
            hem__hhalm = np.empty(ncqrh__kujw, phsxv__hyh)
            for ldsa__ddrz in numba.parfors.parfor.internal_prange(ncqrh__kujw
                ):
                val = iNaT
                if not bodo.libs.array_kernels.isna(arg_a, ldsa__ddrz):
                    data = arg_a[ldsa__ddrz]
                    val = (bodo.hiframes.pd_timestamp_ext.
                        npy_datetimestruct_to_datetime(data.year, data.
                        month, data.day, 0, 0, 0, 0))
                hem__hhalm[ldsa__ddrz
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(hem__hhalm,
                None)
        return impl_date_arr
    if arg_a == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return (lambda arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True: bodo.
            hiframes.pd_index_ext.init_datetime_index(arg_a, None))
    if arg_a == string_array_type:
        phsxv__hyh = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_string_array(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return pandas_string_array_to_datetime(arg_a, errors, dayfirst,
                yearfirst, utc, format, exact, unit, infer_datetime_format,
                origin, cache)
        return impl_string_array
    if isinstance(arg_a, types.Array) and isinstance(arg_a.dtype, types.Integer
        ):
        phsxv__hyh = np.dtype('datetime64[ns]')

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            ncqrh__kujw = len(arg_a)
            hem__hhalm = np.empty(ncqrh__kujw, phsxv__hyh)
            for ldsa__ddrz in numba.parfors.parfor.internal_prange(ncqrh__kujw
                ):
                data = arg_a[ldsa__ddrz]
                val = to_datetime_scalar(data, errors=errors, dayfirst=
                    dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                    exact=exact, unit=unit, infer_datetime_format=
                    infer_datetime_format, origin=origin, cache=cache)
                hem__hhalm[ldsa__ddrz
                    ] = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(hem__hhalm,
                None)
        return impl_date_arr
    if isinstance(arg_a, CategoricalArrayType
        ) and arg_a.dtype.elem_type == bodo.string_type:
        phsxv__hyh = np.dtype('datetime64[ns]')

        def impl_cat_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            ncqrh__kujw = len(arg_a)
            hem__hhalm = np.empty(ncqrh__kujw, phsxv__hyh)
            havc__fyh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arg_a))
            nzxe__eown = pandas_string_array_to_datetime(arg_a.dtype.
                categories.values, errors, dayfirst, yearfirst, utc, format,
                exact, unit, infer_datetime_format, origin, cache).values
            for ldsa__ddrz in numba.parfors.parfor.internal_prange(ncqrh__kujw
                ):
                c = havc__fyh[ldsa__ddrz]
                if c == -1:
                    bodo.libs.array_kernels.setna(hem__hhalm, ldsa__ddrz)
                    continue
                hem__hhalm[ldsa__ddrz] = nzxe__eown[c]
            return bodo.hiframes.pd_index_ext.init_datetime_index(hem__hhalm,
                None)
        return impl_cat_arr
    if arg_a == pd_timestamp_type:

        def impl_timestamp(arg_a, errors='raise', dayfirst=False, yearfirst
            =False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return arg_a
        return impl_timestamp
    raise_bodo_error(f'pd.to_datetime(): cannot convert date type {arg_a}')


@overload(pd.to_timedelta, inline='always', no_unliteral=True)
def overload_to_timedelta(arg_a, unit='ns', errors='raise'):
    if not is_overload_constant_str(unit):
        raise BodoError(
            'pandas.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, unit='ns', errors='raise'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            kpy__lgfz = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nnzrd__hqg = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            sxv__snldp = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_timedelta(arr, unit, errors))
            return bodo.hiframes.pd_series_ext.init_series(sxv__snldp,
                kpy__lgfz, nnzrd__hqg)
        return impl_series
    if is_overload_constant_str(arg_a) or arg_a in (pd_timedelta_type,
        datetime_timedelta_type, bodo.string_type):

        def impl_string(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a)
        return impl_string
    if isinstance(arg_a, types.Float):
        m, wsbh__zjkq = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_float_scalar(arg_a, unit='ns', errors='raise'):
            val = float_to_timedelta_val(arg_a, wsbh__zjkq, m)
            return pd.Timedelta(val)
        return impl_float_scalar
    if isinstance(arg_a, types.Integer):
        m, cfhe__gfna = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_integer_scalar(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a * m)
        return impl_integer_scalar
    if is_iterable_type(arg_a) and not isinstance(arg_a, types.BaseTuple):
        m, wsbh__zjkq = pd._libs.tslibs.conversion.precision_from_unit(unit)
        xqgcr__jdxo = np.dtype('timedelta64[ns]')
        if isinstance(arg_a.dtype, types.Float):

            def impl_float(arg_a, unit='ns', errors='raise'):
                ncqrh__kujw = len(arg_a)
                hem__hhalm = np.empty(ncqrh__kujw, xqgcr__jdxo)
                for ldsa__ddrz in numba.parfors.parfor.internal_prange(
                    ncqrh__kujw):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, ldsa__ddrz):
                        val = float_to_timedelta_val(arg_a[ldsa__ddrz],
                            wsbh__zjkq, m)
                    hem__hhalm[ldsa__ddrz
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hem__hhalm, None)
            return impl_float
        if isinstance(arg_a.dtype, types.Integer):

            def impl_int(arg_a, unit='ns', errors='raise'):
                ncqrh__kujw = len(arg_a)
                hem__hhalm = np.empty(ncqrh__kujw, xqgcr__jdxo)
                for ldsa__ddrz in numba.parfors.parfor.internal_prange(
                    ncqrh__kujw):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, ldsa__ddrz):
                        val = arg_a[ldsa__ddrz] * m
                    hem__hhalm[ldsa__ddrz
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hem__hhalm, None)
            return impl_int
        if arg_a.dtype == bodo.timedelta64ns:

            def impl_td64(arg_a, unit='ns', errors='raise'):
                arr = bodo.utils.conversion.coerce_to_ndarray(arg_a)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(arr,
                    None)
            return impl_td64
        if arg_a.dtype == bodo.string_type or isinstance(arg_a.dtype, types
            .UnicodeCharSeq):

            def impl_str(arg_a, unit='ns', errors='raise'):
                return pandas_string_array_to_timedelta(arg_a, unit, errors)
            return impl_str
        if arg_a.dtype == datetime_timedelta_type:

            def impl_datetime_timedelta(arg_a, unit='ns', errors='raise'):
                ncqrh__kujw = len(arg_a)
                hem__hhalm = np.empty(ncqrh__kujw, xqgcr__jdxo)
                for ldsa__ddrz in numba.parfors.parfor.internal_prange(
                    ncqrh__kujw):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, ldsa__ddrz):
                        ohtf__oqe = arg_a[ldsa__ddrz]
                        val = (ohtf__oqe.microseconds + 1000 * 1000 * (
                            ohtf__oqe.seconds + 24 * 60 * 60 * ohtf__oqe.days)
                            ) * 1000
                    hem__hhalm[ldsa__ddrz
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hem__hhalm, None)
            return impl_datetime_timedelta
    raise_bodo_error(
        f'pd.to_timedelta(): cannot convert date type {arg_a.dtype}')


@register_jitable
def float_to_timedelta_val(data, precision, multiplier):
    jclk__kyuhm = np.int64(data)
    mua__ujh = data - jclk__kyuhm
    if precision:
        mua__ujh = np.round(mua__ujh, precision)
    return jclk__kyuhm * multiplier + np.int64(mua__ujh * multiplier)


@numba.njit
def pandas_string_array_to_timedelta(arg_a, unit='ns', errors='raise'):
    with numba.objmode(result='timedelta_index'):
        result = pd.to_timedelta(arg_a, errors=errors)
    return result


def create_timestamp_cmp_op_overload(op):

    def overload_date_timestamp_cmp(lhs, rhs):
        if (lhs == pd_timestamp_type and rhs == bodo.hiframes.
            datetime_date_ext.datetime_date_type):
            return lambda lhs, rhs: op(lhs.value, bodo.hiframes.
                pd_timestamp_ext.npy_datetimestruct_to_datetime(rhs.year,
                rhs.month, rhs.day, 0, 0, 0, 0))
        if (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and 
            rhs == pd_timestamp_type):
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                npy_datetimestruct_to_datetime(lhs.year, lhs.month, lhs.day,
                0, 0, 0, 0), rhs.value)
        if lhs == pd_timestamp_type and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs.value, rhs.value)
        if lhs == pd_timestamp_type and rhs == bodo.datetime64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(lhs.value), rhs)
        if lhs == bodo.datetime64ns and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(rhs.value))
    return overload_date_timestamp_cmp


@overload_method(PandasTimestampType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


def overload_freq_methods(method):

    def freq_overload(td, freq, ambiguous='raise', nonexistent='raise'):
        gxvy__vkgj = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        xtyl__sydkj = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Timestamp.{method}', gxvy__vkgj,
            xtyl__sydkj, package_name='pandas', module_name='Timestamp')
        otjc__hpc = ["freq == 'D'", "freq == 'H'",
            "freq == 'min' or freq == 'T'", "freq == 'S'",
            "freq == 'ms' or freq == 'L'", "freq == 'U' or freq == 'us'",
            "freq == 'N'"]
        erqxu__ianmg = [24 * 60 * 60 * 1000000 * 1000, 60 * 60 * 1000000 * 
            1000, 60 * 1000000 * 1000, 1000000 * 1000, 1000 * 1000, 1000, 1]
        woqs__ryn = (
            "def impl(td, freq, ambiguous='raise', nonexistent='raise'):\n")
        for ldsa__ddrz, byj__igqla in enumerate(otjc__hpc):
            uoa__mrabp = 'if' if ldsa__ddrz == 0 else 'elif'
            woqs__ryn += '    {} {}:\n'.format(uoa__mrabp, byj__igqla)
            woqs__ryn += '        unit_value = {}\n'.format(erqxu__ianmg[
                ldsa__ddrz])
        woqs__ryn += '    else:\n'
        woqs__ryn += (
            "        raise ValueError('Incorrect Frequency specification')\n")
        if td == pd_timedelta_type:
            woqs__ryn += (
                """    return pd.Timedelta(unit_value * np.int64(np.{}(td.value / unit_value)))
"""
                .format(method))
        elif td == pd_timestamp_type:
            if method == 'ceil':
                woqs__ryn += (
                    '    value = td.value + np.remainder(-td.value, unit_value)\n'
                    )
            if method == 'floor':
                woqs__ryn += (
                    '    value = td.value - np.remainder(td.value, unit_value)\n'
                    )
            if method == 'round':
                woqs__ryn += '    if unit_value == 1:\n'
                woqs__ryn += '        value = td.value\n'
                woqs__ryn += '    else:\n'
                woqs__ryn += (
                    '        quotient, remainder = np.divmod(td.value, unit_value)\n'
                    )
                woqs__ryn += """        mask = np.logical_or(remainder > (unit_value // 2), np.logical_and(remainder == (unit_value // 2), quotient % 2))
"""
                woqs__ryn += '        if mask:\n'
                woqs__ryn += '            quotient = quotient + 1\n'
                woqs__ryn += '        value = quotient * unit_value\n'
            woqs__ryn += '    return pd.Timestamp(value)\n'
        lem__jjj = {}
        exec(woqs__ryn, {'np': np, 'pd': pd}, lem__jjj)
        impl = lem__jjj['impl']
        return impl
    return freq_overload


def _install_freq_methods():
    xjbeb__jkl = ['ceil', 'floor', 'round']
    for method in xjbeb__jkl:
        kifw__ndy = overload_freq_methods(method)
        overload_method(PDTimeDeltaType, method, no_unliteral=True)(kifw__ndy)
        overload_method(PandasTimestampType, method, no_unliteral=True)(
            kifw__ndy)


_install_freq_methods()


@register_jitable
def compute_pd_timestamp(totmicrosec, nanosecond):
    microsecond = totmicrosec % 1000000
    jvv__lfy = totmicrosec // 1000000
    second = jvv__lfy % 60
    tbn__mljkg = jvv__lfy // 60
    minute = tbn__mljkg % 60
    knkl__sfcg = tbn__mljkg // 60
    hour = knkl__sfcg % 24
    bxah__bcwql = knkl__sfcg // 24
    year, month, day = _ord2ymd(bxah__bcwql)
    value = npy_datetimestruct_to_datetime(year, month, day, hour, minute,
        second, microsecond)
    value += zero_if_none(nanosecond)
    return init_timestamp(year, month, day, hour, minute, second,
        microsecond, nanosecond, value)


def overload_sub_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            rmfko__ovao = lhs.toordinal()
            ihhvg__amdpy = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            dqdqa__ydlj = lhs.microsecond
            nanosecond = lhs.nanosecond
            kbbp__ttyb = rhs.days
            svzw__edcpa = rhs.seconds
            riadu__ioo = rhs.microseconds
            eys__ozwo = rmfko__ovao - kbbp__ttyb
            zbg__vzqu = ihhvg__amdpy - svzw__edcpa
            cfb__wmm = dqdqa__ydlj - riadu__ioo
            totmicrosec = 1000000 * (eys__ozwo * 86400 + zbg__vzqu) + cfb__wmm
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl_timestamp(lhs, rhs):
            return convert_numpy_timedelta64_to_pd_timedelta(lhs.value -
                rhs.value)
        return impl_timestamp
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


def overload_add_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            rmfko__ovao = lhs.toordinal()
            ihhvg__amdpy = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            dqdqa__ydlj = lhs.microsecond
            nanosecond = lhs.nanosecond
            kbbp__ttyb = rhs.days
            svzw__edcpa = rhs.seconds
            riadu__ioo = rhs.microseconds
            eys__ozwo = rmfko__ovao + kbbp__ttyb
            zbg__vzqu = ihhvg__amdpy + svzw__edcpa
            cfb__wmm = dqdqa__ydlj + riadu__ioo
            totmicrosec = 1000000 * (eys__ozwo * 86400 + zbg__vzqu) + cfb__wmm
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            rmfko__ovao = lhs.toordinal()
            ihhvg__amdpy = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            dqdqa__ydlj = lhs.microsecond
            dbrdb__yzjym = lhs.nanosecond
            riadu__ioo = rhs.value // 1000
            ggmxq__sigiv = rhs.nanoseconds
            cfb__wmm = dqdqa__ydlj + riadu__ioo
            totmicrosec = 1000000 * (rmfko__ovao * 86400 + ihhvg__amdpy
                ) + cfb__wmm
            xhgj__sqpg = dbrdb__yzjym + ggmxq__sigiv
            return compute_pd_timestamp(totmicrosec, xhgj__sqpg)
        return impl
    if (lhs == pd_timedelta_type and rhs == pd_timestamp_type or lhs ==
        datetime_timedelta_type and rhs == pd_timestamp_type):

        def impl(lhs, rhs):
            return rhs + lhs
        return impl


@overload(min, no_unliteral=True)
def timestamp_min(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def timestamp_max(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, 'strftime')
@overload_method(PandasTimestampType, 'strftime')
def strftime(ts, format):
    if isinstance(ts, DatetimeDateType):
        hhuz__mwk = 'datetime.date'
    else:
        hhuz__mwk = 'pandas.Timestamp'
    if types.unliteral(format) != types.unicode_type:
        raise BodoError(
            f"{hhuz__mwk}.strftime(): 'strftime' argument must be a string")

    def impl(ts, format):
        with numba.objmode(res='unicode_type'):
            res = ts.strftime(format)
        return res
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='pd_timestamp_type'):
        d = pd.Timestamp.now()
    return d


class CompDT64(ConcreteTemplate):
    cases = [signature(types.boolean, types.NPDatetime('ns'), types.
        NPDatetime('ns'))]


@infer_global(operator.lt)
class CmpOpLt(CompDT64):
    key = operator.lt


@infer_global(operator.le)
class CmpOpLe(CompDT64):
    key = operator.le


@infer_global(operator.gt)
class CmpOpGt(CompDT64):
    key = operator.gt


@infer_global(operator.ge)
class CmpOpGe(CompDT64):
    key = operator.ge


@infer_global(operator.eq)
class CmpOpEq(CompDT64):
    key = operator.eq


@infer_global(operator.ne)
class CmpOpNe(CompDT64):
    key = operator.ne


@typeof_impl.register(calendar._localized_month)
def typeof_python_calendar(val, c):
    return types.Tuple([types.StringLiteral(bzgme__ucq) for bzgme__ucq in val])


@overload(str)
def overload_datetime64_str(val):
    if val == bodo.datetime64ns:

        def impl(val):
            return (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(val).isoformat('T'))
        return impl


timestamp_unsupported_attrs = ['asm8', 'components', 'freqstr', 'tz',
    'fold', 'tzinfo', 'freq']
timestamp_unsupported_methods = ['astimezone', 'ctime', 'dst', 'isoweekday',
    'replace', 'strptime', 'time', 'timestamp', 'timetuple', 'timetz',
    'to_datetime64', 'to_julian_date', 'to_numpy', 'to_period',
    'to_pydatetime', 'tz_convert', 'tz_localize', 'tzname', 'utcoffset',
    'utctimetuple']


def _install_pd_timestamp_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for jlrtq__ybnk in timestamp_unsupported_attrs:
        jiv__lyb = 'pandas.Timestamp.' + jlrtq__ybnk
        overload_attribute(PandasTimestampType, jlrtq__ybnk)(
            create_unsupported_overload(jiv__lyb))
    for ojihd__sbux in timestamp_unsupported_methods:
        jiv__lyb = 'pandas.Timestamp.' + ojihd__sbux
        overload_method(PandasTimestampType, ojihd__sbux)(
            create_unsupported_overload(jiv__lyb + '()'))


_install_pd_timestamp_unsupported()
