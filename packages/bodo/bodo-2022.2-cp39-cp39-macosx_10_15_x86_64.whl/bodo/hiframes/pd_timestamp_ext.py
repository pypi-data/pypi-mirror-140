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
        zkpdn__blaqt = [('year', ts_field_typ), ('month', ts_field_typ), (
            'day', ts_field_typ), ('hour', ts_field_typ), ('minute',
            ts_field_typ), ('second', ts_field_typ), ('microsecond',
            ts_field_typ), ('nanosecond', ts_field_typ), ('value',
            ts_field_typ)]
        models.StructModel.__init__(self, dmm, fe_type, zkpdn__blaqt)


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
    hyv__cbg = c.pyapi.object_getattr_string(val, 'year')
    bfu__iqdjl = c.pyapi.object_getattr_string(val, 'month')
    gif__pgc = c.pyapi.object_getattr_string(val, 'day')
    zhi__psfwc = c.pyapi.object_getattr_string(val, 'hour')
    jlr__nndiw = c.pyapi.object_getattr_string(val, 'minute')
    aqa__lcg = c.pyapi.object_getattr_string(val, 'second')
    ijg__wngj = c.pyapi.object_getattr_string(val, 'microsecond')
    xezm__rxqar = c.pyapi.object_getattr_string(val, 'nanosecond')
    ywgx__pmgp = c.pyapi.object_getattr_string(val, 'value')
    owg__ateil = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    owg__ateil.year = c.pyapi.long_as_longlong(hyv__cbg)
    owg__ateil.month = c.pyapi.long_as_longlong(bfu__iqdjl)
    owg__ateil.day = c.pyapi.long_as_longlong(gif__pgc)
    owg__ateil.hour = c.pyapi.long_as_longlong(zhi__psfwc)
    owg__ateil.minute = c.pyapi.long_as_longlong(jlr__nndiw)
    owg__ateil.second = c.pyapi.long_as_longlong(aqa__lcg)
    owg__ateil.microsecond = c.pyapi.long_as_longlong(ijg__wngj)
    owg__ateil.nanosecond = c.pyapi.long_as_longlong(xezm__rxqar)
    owg__ateil.value = c.pyapi.long_as_longlong(ywgx__pmgp)
    c.pyapi.decref(hyv__cbg)
    c.pyapi.decref(bfu__iqdjl)
    c.pyapi.decref(gif__pgc)
    c.pyapi.decref(zhi__psfwc)
    c.pyapi.decref(jlr__nndiw)
    c.pyapi.decref(aqa__lcg)
    c.pyapi.decref(ijg__wngj)
    c.pyapi.decref(xezm__rxqar)
    c.pyapi.decref(ywgx__pmgp)
    fvov__jffd = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(owg__ateil._getvalue(), is_error=fvov__jffd)


@box(PandasTimestampType)
def box_pandas_timestamp(typ, val, c):
    zqx__inany = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    hyv__cbg = c.pyapi.long_from_longlong(zqx__inany.year)
    bfu__iqdjl = c.pyapi.long_from_longlong(zqx__inany.month)
    gif__pgc = c.pyapi.long_from_longlong(zqx__inany.day)
    zhi__psfwc = c.pyapi.long_from_longlong(zqx__inany.hour)
    jlr__nndiw = c.pyapi.long_from_longlong(zqx__inany.minute)
    aqa__lcg = c.pyapi.long_from_longlong(zqx__inany.second)
    lbz__ptczp = c.pyapi.long_from_longlong(zqx__inany.microsecond)
    qne__vdsfz = c.pyapi.long_from_longlong(zqx__inany.nanosecond)
    xkogc__vgoc = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timestamp))
    res = c.pyapi.call_function_objargs(xkogc__vgoc, (hyv__cbg, bfu__iqdjl,
        gif__pgc, zhi__psfwc, jlr__nndiw, aqa__lcg, lbz__ptczp, qne__vdsfz))
    c.pyapi.decref(hyv__cbg)
    c.pyapi.decref(bfu__iqdjl)
    c.pyapi.decref(gif__pgc)
    c.pyapi.decref(zhi__psfwc)
    c.pyapi.decref(jlr__nndiw)
    c.pyapi.decref(aqa__lcg)
    c.pyapi.decref(lbz__ptczp)
    c.pyapi.decref(qne__vdsfz)
    return res


@intrinsic
def init_timestamp(typingctx, year, month, day, hour, minute, second,
    microsecond, nanosecond, value=None):

    def codegen(context, builder, sig, args):
        (year, month, day, hour, minute, second, lluip__hopo, efaps__avib,
            value) = args
        ts = cgutils.create_struct_proxy(pd_timestamp_type)(context, builder)
        ts.year = year
        ts.month = month
        ts.day = day
        ts.hour = hour
        ts.minute = minute
        ts.second = second
        ts.microsecond = lluip__hopo
        ts.nanosecond = efaps__avib
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
        jih__okuiu, precision = pd._libs.tslibs.conversion.precision_from_unit(
            unit)
        if isinstance(ts_input, types.Integer):

            def impl_int(ts_input=_no_input, freq=None, tz=None, unit=None,
                year=None, month=None, day=None, hour=None, minute=None,
                second=None, microsecond=None, nanosecond=None, tzinfo=None):
                value = ts_input * jih__okuiu
                return convert_datetime64_to_timestamp(integer_to_dt64(value))
            return impl_int

        def impl_float(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            gah__hwrqu = np.int64(ts_input)
            shje__cqjwi = ts_input - gah__hwrqu
            if precision:
                shje__cqjwi = np.round(shje__cqjwi, precision)
            value = gah__hwrqu * jih__okuiu + np.int64(shje__cqjwi * jih__okuiu
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
        tnecz__naru, latxh__nio, tnecz__naru = get_isocalendar(ptt.year,
            ptt.month, ptt.day)
        return latxh__nio
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
        year, latxh__nio, hip__doa = get_isocalendar(ptt.year, ptt.month,
            ptt.day)
        return year, latxh__nio, hip__doa
    return impl


@overload_method(PandasTimestampType, 'isoformat', no_unliteral=True)
def overload_pd_timestamp_isoformat(ts, sep=None):
    if is_overload_none(sep):

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            ctcg__midm = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + 'T' + ctcg__midm
            return res
        return timestamp_isoformat_impl
    else:

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            ctcg__midm = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + sep + ctcg__midm
            return res
    return timestamp_isoformat_impl


@overload_method(PandasTimestampType, 'normalize', no_unliteral=True)
def overload_pd_timestamp_normalize(ptt):

    def impl(ptt):
        return pd.Timestamp(year=ptt.year, month=ptt.month, day=ptt.day)
    return impl


@overload_method(PandasTimestampType, 'day_name', no_unliteral=True)
def overload_pd_timestamp_day_name(ptt, locale=None):
    wdpr__siphj = dict(locale=locale)
    dsjut__ykdpv = dict(locale=None)
    check_unsupported_args('Timestamp.day_name', wdpr__siphj, dsjut__ykdpv,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        brht__lsn = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday')
        tnecz__naru, tnecz__naru, ddi__dbdf = ptt.isocalendar()
        return brht__lsn[ddi__dbdf - 1]
    return impl


@overload_method(PandasTimestampType, 'month_name', no_unliteral=True)
def overload_pd_timestamp_month_name(ptt, locale=None):
    wdpr__siphj = dict(locale=locale)
    dsjut__ykdpv = dict(locale=None)
    check_unsupported_args('Timestamp.month_name', wdpr__siphj,
        dsjut__ykdpv, package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        elwr__lgps = ('January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November',
            'December')
        return elwr__lgps[ptt.month - 1]
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
        hvrsk__ndkzb = cgutils.alloca_once(builder, lir.IntType(64))
        builder.store(args[0], hvrsk__ndkzb)
        year = cgutils.alloca_once(builder, lir.IntType(64))
        zlmic__hyofc = cgutils.alloca_once(builder, lir.IntType(64))
        mkhbd__ekay = lir.FunctionType(lir.VoidType(), [lir.IntType(64).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        xjuc__zwu = cgutils.get_or_insert_function(builder.module,
            mkhbd__ekay, name='extract_year_days')
        builder.call(xjuc__zwu, [hvrsk__ndkzb, year, zlmic__hyofc])
        return cgutils.pack_array(builder, [builder.load(hvrsk__ndkzb),
            builder.load(year), builder.load(zlmic__hyofc)])
    return types.Tuple([types.int64, types.int64, types.int64])(dt64_t
        ), codegen


@intrinsic
def get_month_day(typingctx, year_t, days_t=None):
    assert year_t == types.int64
    assert days_t == types.int64

    def codegen(context, builder, sig, args):
        month = cgutils.alloca_once(builder, lir.IntType(64))
        day = cgutils.alloca_once(builder, lir.IntType(64))
        mkhbd__ekay = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        xjuc__zwu = cgutils.get_or_insert_function(builder.module,
            mkhbd__ekay, name='get_month_day')
        builder.call(xjuc__zwu, [args[0], args[1], month, day])
        return cgutils.pack_array(builder, [builder.load(month), builder.
            load(day)])
    return types.Tuple([types.int64, types.int64])(types.int64, types.int64
        ), codegen


@register_jitable
def get_day_of_year(year, month, day):
    ccy__zgsov = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 
        365, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    byfdz__hmcep = is_leap_year(year)
    jjugg__lykuc = ccy__zgsov[byfdz__hmcep * 13 + month - 1]
    wzytm__kezzu = jjugg__lykuc + day
    return wzytm__kezzu


@register_jitable
def get_day_of_week(y, m, d):
    ele__ulq = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    day = (y + y // 4 - y // 100 + y // 400 + ele__ulq[m - 1] + d) % 7
    return (day + 6) % 7


@register_jitable
def get_days_in_month(year, month):
    is_leap_year = year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)
    egyj__fdy = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 29, 31,
        30, 31, 30, 31, 31, 30, 31, 30, 31]
    return egyj__fdy[12 * is_leap_year + month - 1]


@register_jitable
def is_leap_year(year):
    return year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)


@numba.njit(no_cpython_wrapper=True)
def convert_datetime64_to_timestamp(dt64):
    hvrsk__ndkzb, year, zlmic__hyofc = extract_year_days(dt64)
    month, day = get_month_day(year, zlmic__hyofc)
    return pd.Timestamp(year, month, day, hvrsk__ndkzb // (60 * 60 * 
        1000000000), hvrsk__ndkzb // (60 * 1000000000) % 60, hvrsk__ndkzb //
        1000000000 % 60, hvrsk__ndkzb // 1000 % 1000000, hvrsk__ndkzb % 1000)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_datetime_timedelta(dt64):
    eqtzs__rac = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    grddr__chzp = eqtzs__rac // (86400 * 1000000000)
    dmr__ijo = eqtzs__rac - grddr__chzp * 86400 * 1000000000
    ile__sja = dmr__ijo // 1000000000
    vbu__dkzmc = dmr__ijo - ile__sja * 1000000000
    vdrhs__cnw = vbu__dkzmc // 1000
    return datetime.timedelta(grddr__chzp, ile__sja, vdrhs__cnw)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_pd_timedelta(dt64):
    eqtzs__rac = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    return pd.Timedelta(eqtzs__rac)


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
            xbpbm__nvvok = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nle__vyub = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            xshbg__mfq = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_datetime(arr, errors=errors, dayfirst=dayfirst,
                yearfirst=yearfirst, utc=utc, format=format, exact=exact,
                unit=unit, infer_datetime_format=infer_datetime_format,
                origin=origin, cache=cache))
            return bodo.hiframes.pd_series_ext.init_series(xshbg__mfq,
                xbpbm__nvvok, nle__vyub)
        return impl_series
    if arg_a == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        kori__amgwl = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tsxry__npy = len(arg_a)
            hvvzf__tmct = np.empty(tsxry__npy, kori__amgwl)
            for pisy__noas in numba.parfors.parfor.internal_prange(tsxry__npy):
                val = iNaT
                if not bodo.libs.array_kernels.isna(arg_a, pisy__noas):
                    data = arg_a[pisy__noas]
                    val = (bodo.hiframes.pd_timestamp_ext.
                        npy_datetimestruct_to_datetime(data.year, data.
                        month, data.day, 0, 0, 0, 0))
                hvvzf__tmct[pisy__noas
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(hvvzf__tmct,
                None)
        return impl_date_arr
    if arg_a == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return (lambda arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True: bodo.
            hiframes.pd_index_ext.init_datetime_index(arg_a, None))
    if arg_a == string_array_type:
        kori__amgwl = np.dtype('datetime64[ns]')
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
        kori__amgwl = np.dtype('datetime64[ns]')

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tsxry__npy = len(arg_a)
            hvvzf__tmct = np.empty(tsxry__npy, kori__amgwl)
            for pisy__noas in numba.parfors.parfor.internal_prange(tsxry__npy):
                data = arg_a[pisy__noas]
                val = to_datetime_scalar(data, errors=errors, dayfirst=
                    dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                    exact=exact, unit=unit, infer_datetime_format=
                    infer_datetime_format, origin=origin, cache=cache)
                hvvzf__tmct[pisy__noas
                    ] = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(hvvzf__tmct,
                None)
        return impl_date_arr
    if isinstance(arg_a, CategoricalArrayType
        ) and arg_a.dtype.elem_type == bodo.string_type:
        kori__amgwl = np.dtype('datetime64[ns]')

        def impl_cat_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tsxry__npy = len(arg_a)
            hvvzf__tmct = np.empty(tsxry__npy, kori__amgwl)
            fyehd__mzye = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arg_a))
            gau__ovi = pandas_string_array_to_datetime(arg_a.dtype.
                categories.values, errors, dayfirst, yearfirst, utc, format,
                exact, unit, infer_datetime_format, origin, cache).values
            for pisy__noas in numba.parfors.parfor.internal_prange(tsxry__npy):
                c = fyehd__mzye[pisy__noas]
                if c == -1:
                    bodo.libs.array_kernels.setna(hvvzf__tmct, pisy__noas)
                    continue
                hvvzf__tmct[pisy__noas] = gau__ovi[c]
            return bodo.hiframes.pd_index_ext.init_datetime_index(hvvzf__tmct,
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
            xbpbm__nvvok = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            nle__vyub = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            xshbg__mfq = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_timedelta(arr, unit, errors))
            return bodo.hiframes.pd_series_ext.init_series(xshbg__mfq,
                xbpbm__nvvok, nle__vyub)
        return impl_series
    if is_overload_constant_str(arg_a) or arg_a in (pd_timedelta_type,
        datetime_timedelta_type, bodo.string_type):

        def impl_string(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a)
        return impl_string
    if isinstance(arg_a, types.Float):
        m, vmvp__kjy = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_float_scalar(arg_a, unit='ns', errors='raise'):
            val = float_to_timedelta_val(arg_a, vmvp__kjy, m)
            return pd.Timedelta(val)
        return impl_float_scalar
    if isinstance(arg_a, types.Integer):
        m, tnecz__naru = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_integer_scalar(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a * m)
        return impl_integer_scalar
    if is_iterable_type(arg_a) and not isinstance(arg_a, types.BaseTuple):
        m, vmvp__kjy = pd._libs.tslibs.conversion.precision_from_unit(unit)
        leh__tlju = np.dtype('timedelta64[ns]')
        if isinstance(arg_a.dtype, types.Float):

            def impl_float(arg_a, unit='ns', errors='raise'):
                tsxry__npy = len(arg_a)
                hvvzf__tmct = np.empty(tsxry__npy, leh__tlju)
                for pisy__noas in numba.parfors.parfor.internal_prange(
                    tsxry__npy):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, pisy__noas):
                        val = float_to_timedelta_val(arg_a[pisy__noas],
                            vmvp__kjy, m)
                    hvvzf__tmct[pisy__noas
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hvvzf__tmct, None)
            return impl_float
        if isinstance(arg_a.dtype, types.Integer):

            def impl_int(arg_a, unit='ns', errors='raise'):
                tsxry__npy = len(arg_a)
                hvvzf__tmct = np.empty(tsxry__npy, leh__tlju)
                for pisy__noas in numba.parfors.parfor.internal_prange(
                    tsxry__npy):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, pisy__noas):
                        val = arg_a[pisy__noas] * m
                    hvvzf__tmct[pisy__noas
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hvvzf__tmct, None)
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
                tsxry__npy = len(arg_a)
                hvvzf__tmct = np.empty(tsxry__npy, leh__tlju)
                for pisy__noas in numba.parfors.parfor.internal_prange(
                    tsxry__npy):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, pisy__noas):
                        rjrjd__xxku = arg_a[pisy__noas]
                        val = (rjrjd__xxku.microseconds + 1000 * 1000 * (
                            rjrjd__xxku.seconds + 24 * 60 * 60 *
                            rjrjd__xxku.days)) * 1000
                    hvvzf__tmct[pisy__noas
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    hvvzf__tmct, None)
            return impl_datetime_timedelta
    raise_bodo_error(
        f'pd.to_timedelta(): cannot convert date type {arg_a.dtype}')


@register_jitable
def float_to_timedelta_val(data, precision, multiplier):
    gah__hwrqu = np.int64(data)
    shje__cqjwi = data - gah__hwrqu
    if precision:
        shje__cqjwi = np.round(shje__cqjwi, precision)
    return gah__hwrqu * multiplier + np.int64(shje__cqjwi * multiplier)


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
        wdpr__siphj = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        ywn__vusqz = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Timestamp.{method}', wdpr__siphj,
            ywn__vusqz, package_name='pandas', module_name='Timestamp')
        zfem__nbq = ["freq == 'D'", "freq == 'H'",
            "freq == 'min' or freq == 'T'", "freq == 'S'",
            "freq == 'ms' or freq == 'L'", "freq == 'U' or freq == 'us'",
            "freq == 'N'"]
        vic__innc = [24 * 60 * 60 * 1000000 * 1000, 60 * 60 * 1000000 * 
            1000, 60 * 1000000 * 1000, 1000000 * 1000, 1000 * 1000, 1000, 1]
        rzmt__dhlkt = (
            "def impl(td, freq, ambiguous='raise', nonexistent='raise'):\n")
        for pisy__noas, fplfn__mqk in enumerate(zfem__nbq):
            xewt__mrhaj = 'if' if pisy__noas == 0 else 'elif'
            rzmt__dhlkt += '    {} {}:\n'.format(xewt__mrhaj, fplfn__mqk)
            rzmt__dhlkt += '        unit_value = {}\n'.format(vic__innc[
                pisy__noas])
        rzmt__dhlkt += '    else:\n'
        rzmt__dhlkt += (
            "        raise ValueError('Incorrect Frequency specification')\n")
        if td == pd_timedelta_type:
            rzmt__dhlkt += (
                """    return pd.Timedelta(unit_value * np.int64(np.{}(td.value / unit_value)))
"""
                .format(method))
        elif td == pd_timestamp_type:
            if method == 'ceil':
                rzmt__dhlkt += (
                    '    value = td.value + np.remainder(-td.value, unit_value)\n'
                    )
            if method == 'floor':
                rzmt__dhlkt += (
                    '    value = td.value - np.remainder(td.value, unit_value)\n'
                    )
            if method == 'round':
                rzmt__dhlkt += '    if unit_value == 1:\n'
                rzmt__dhlkt += '        value = td.value\n'
                rzmt__dhlkt += '    else:\n'
                rzmt__dhlkt += (
                    '        quotient, remainder = np.divmod(td.value, unit_value)\n'
                    )
                rzmt__dhlkt += """        mask = np.logical_or(remainder > (unit_value // 2), np.logical_and(remainder == (unit_value // 2), quotient % 2))
"""
                rzmt__dhlkt += '        if mask:\n'
                rzmt__dhlkt += '            quotient = quotient + 1\n'
                rzmt__dhlkt += '        value = quotient * unit_value\n'
            rzmt__dhlkt += '    return pd.Timestamp(value)\n'
        xudga__rasj = {}
        exec(rzmt__dhlkt, {'np': np, 'pd': pd}, xudga__rasj)
        impl = xudga__rasj['impl']
        return impl
    return freq_overload


def _install_freq_methods():
    aus__rfft = ['ceil', 'floor', 'round']
    for method in aus__rfft:
        uflyg__mktuu = overload_freq_methods(method)
        overload_method(PDTimeDeltaType, method, no_unliteral=True)(
            uflyg__mktuu)
        overload_method(PandasTimestampType, method, no_unliteral=True)(
            uflyg__mktuu)


_install_freq_methods()


@register_jitable
def compute_pd_timestamp(totmicrosec, nanosecond):
    microsecond = totmicrosec % 1000000
    nrktl__jpnaw = totmicrosec // 1000000
    second = nrktl__jpnaw % 60
    inuw__kel = nrktl__jpnaw // 60
    minute = inuw__kel % 60
    kmc__igb = inuw__kel // 60
    hour = kmc__igb % 24
    sda__vicqu = kmc__igb // 24
    year, month, day = _ord2ymd(sda__vicqu)
    value = npy_datetimestruct_to_datetime(year, month, day, hour, minute,
        second, microsecond)
    value += zero_if_none(nanosecond)
    return init_timestamp(year, month, day, hour, minute, second,
        microsecond, nanosecond, value)


def overload_sub_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            vby__spvl = lhs.toordinal()
            lywnx__gmi = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            kbzl__jbtjj = lhs.microsecond
            nanosecond = lhs.nanosecond
            csrg__iotj = rhs.days
            uxqnk__xkx = rhs.seconds
            nvye__zqkx = rhs.microseconds
            jmsy__fsuw = vby__spvl - csrg__iotj
            zvtz__wufcc = lywnx__gmi - uxqnk__xkx
            fdna__iqt = kbzl__jbtjj - nvye__zqkx
            totmicrosec = 1000000 * (jmsy__fsuw * 86400 + zvtz__wufcc
                ) + fdna__iqt
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
            vby__spvl = lhs.toordinal()
            lywnx__gmi = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            kbzl__jbtjj = lhs.microsecond
            nanosecond = lhs.nanosecond
            csrg__iotj = rhs.days
            uxqnk__xkx = rhs.seconds
            nvye__zqkx = rhs.microseconds
            jmsy__fsuw = vby__spvl + csrg__iotj
            zvtz__wufcc = lywnx__gmi + uxqnk__xkx
            fdna__iqt = kbzl__jbtjj + nvye__zqkx
            totmicrosec = 1000000 * (jmsy__fsuw * 86400 + zvtz__wufcc
                ) + fdna__iqt
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            vby__spvl = lhs.toordinal()
            lywnx__gmi = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            kbzl__jbtjj = lhs.microsecond
            lqy__xuvwq = lhs.nanosecond
            nvye__zqkx = rhs.value // 1000
            ogzr__umy = rhs.nanoseconds
            fdna__iqt = kbzl__jbtjj + nvye__zqkx
            totmicrosec = 1000000 * (vby__spvl * 86400 + lywnx__gmi
                ) + fdna__iqt
            mtcj__xllmj = lqy__xuvwq + ogzr__umy
            return compute_pd_timestamp(totmicrosec, mtcj__xllmj)
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
        typ__baduy = 'datetime.date'
    else:
        typ__baduy = 'pandas.Timestamp'
    if types.unliteral(format) != types.unicode_type:
        raise BodoError(
            f"{typ__baduy}.strftime(): 'strftime' argument must be a string")

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
    return types.Tuple([types.StringLiteral(nqwlg__cta) for nqwlg__cta in val])


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
    for vbz__ijkx in timestamp_unsupported_attrs:
        cnmk__fevac = 'pandas.Timestamp.' + vbz__ijkx
        overload_attribute(PandasTimestampType, vbz__ijkx)(
            create_unsupported_overload(cnmk__fevac))
    for elwwj__kehfj in timestamp_unsupported_methods:
        cnmk__fevac = 'pandas.Timestamp.' + elwwj__kehfj
        overload_method(PandasTimestampType, elwwj__kehfj)(
            create_unsupported_overload(cnmk__fevac + '()'))


_install_pd_timestamp_unsupported()
