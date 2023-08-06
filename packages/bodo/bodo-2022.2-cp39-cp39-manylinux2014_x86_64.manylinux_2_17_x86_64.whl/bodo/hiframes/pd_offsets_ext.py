"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qhbnu__fjfet = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, qhbnu__fjfet)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    axsf__htm = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ioe__ugy = c.pyapi.long_from_longlong(axsf__htm.n)
    ospe__mzawm = c.pyapi.from_native_value(types.boolean, axsf__htm.
        normalize, c.env_manager)
    qux__wva = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    kcs__sjt = c.pyapi.call_function_objargs(qux__wva, (ioe__ugy, ospe__mzawm))
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    c.pyapi.decref(qux__wva)
    return kcs__sjt


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    ioe__ugy = c.pyapi.object_getattr_string(val, 'n')
    ospe__mzawm = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioe__ugy)
    normalize = c.pyapi.to_native_value(types.bool_, ospe__mzawm).value
    axsf__htm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    axsf__htm.n = n
    axsf__htm.normalize = normalize
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    uxgl__zju = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(axsf__htm._getvalue(), is_error=uxgl__zju)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        axsf__htm = cgutils.create_struct_proxy(typ)(context, builder)
        axsf__htm.n = args[0]
        axsf__htm.normalize = args[1]
        return axsf__htm._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qhbnu__fjfet = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, qhbnu__fjfet)


@box(MonthEndType)
def box_month_end(typ, val, c):
    yclx__qkkbq = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ioe__ugy = c.pyapi.long_from_longlong(yclx__qkkbq.n)
    ospe__mzawm = c.pyapi.from_native_value(types.boolean, yclx__qkkbq.
        normalize, c.env_manager)
    gzlh__ncuxi = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    kcs__sjt = c.pyapi.call_function_objargs(gzlh__ncuxi, (ioe__ugy,
        ospe__mzawm))
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    c.pyapi.decref(gzlh__ncuxi)
    return kcs__sjt


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    ioe__ugy = c.pyapi.object_getattr_string(val, 'n')
    ospe__mzawm = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioe__ugy)
    normalize = c.pyapi.to_native_value(types.bool_, ospe__mzawm).value
    yclx__qkkbq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    yclx__qkkbq.n = n
    yclx__qkkbq.normalize = normalize
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    uxgl__zju = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(yclx__qkkbq._getvalue(), is_error=uxgl__zju)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        yclx__qkkbq = cgutils.create_struct_proxy(typ)(context, builder)
        yclx__qkkbq.n = args[0]
        yclx__qkkbq.normalize = args[1]
        return yclx__qkkbq._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        yclx__qkkbq = get_days_in_month(year, month)
        if yclx__qkkbq > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            nanoseconds = lhs._nanoseconds
            nanosecond = lhs._nanosecond
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize,
                    nanoseconds=nanoseconds, nanosecond=nanosecond)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qhbnu__fjfet = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, qhbnu__fjfet)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    iszx__cakz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    nnzk__wamk = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for ogix__tjt, upuns__uzil in enumerate(date_offset_fields):
        c.builder.store(getattr(iszx__cakz, upuns__uzil), c.builder.
            inttoptr(c.builder.add(c.builder.ptrtoint(nnzk__wamk, lir.
            IntType(64)), lir.Constant(lir.IntType(64), 8 * ogix__tjt)),
            lir.IntType(64).as_pointer()))
    mcphg__yqdpq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    khxy__rtuh = cgutils.get_or_insert_function(c.builder.module,
        mcphg__yqdpq, name='box_date_offset')
    mruuj__vzgue = c.builder.call(khxy__rtuh, [iszx__cakz.n, iszx__cakz.
        normalize, nnzk__wamk, iszx__cakz.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return mruuj__vzgue


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    ioe__ugy = c.pyapi.object_getattr_string(val, 'n')
    ospe__mzawm = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ioe__ugy)
    normalize = c.pyapi.to_native_value(types.bool_, ospe__mzawm).value
    nnzk__wamk = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    mcphg__yqdpq = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    tom__mlsrx = cgutils.get_or_insert_function(c.builder.module,
        mcphg__yqdpq, name='unbox_date_offset')
    has_kws = c.builder.call(tom__mlsrx, [val, nnzk__wamk])
    iszx__cakz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    iszx__cakz.n = n
    iszx__cakz.normalize = normalize
    for ogix__tjt, upuns__uzil in enumerate(date_offset_fields):
        setattr(iszx__cakz, upuns__uzil, c.builder.load(c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(nnzk__wamk, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * ogix__tjt)), lir.IntType(64).
            as_pointer())))
    iszx__cakz.has_kws = has_kws
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    uxgl__zju = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iszx__cakz._getvalue(), is_error=uxgl__zju)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    bjmid__emn = [n, normalize]
    has_kws = False
    dehu__mwbom = [0] * 9 + [-1] * 9
    for ogix__tjt, upuns__uzil in enumerate(date_offset_fields):
        if hasattr(pyval, upuns__uzil):
            jjdaj__ioul = context.get_constant(types.int64, getattr(pyval,
                upuns__uzil))
            if upuns__uzil != 'nanoseconds' and upuns__uzil != 'nanosecond':
                has_kws = True
        else:
            jjdaj__ioul = context.get_constant(types.int64, dehu__mwbom[
                ogix__tjt])
        bjmid__emn.append(jjdaj__ioul)
    has_kws = context.get_constant(types.boolean, has_kws)
    bjmid__emn.append(has_kws)
    return lir.Constant.literal_struct(bjmid__emn)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    eiupx__dnoal = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for dic__wninl in eiupx__dnoal:
        if not is_overload_none(dic__wninl):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        iszx__cakz = cgutils.create_struct_proxy(typ)(context, builder)
        iszx__cakz.n = args[0]
        iszx__cakz.normalize = args[1]
        iszx__cakz.years = args[2]
        iszx__cakz.months = args[3]
        iszx__cakz.weeks = args[4]
        iszx__cakz.days = args[5]
        iszx__cakz.hours = args[6]
        iszx__cakz.minutes = args[7]
        iszx__cakz.seconds = args[8]
        iszx__cakz.microseconds = args[9]
        iszx__cakz.nanoseconds = args[10]
        iszx__cakz.year = args[11]
        iszx__cakz.month = args[12]
        iszx__cakz.day = args[13]
        iszx__cakz.weekday = args[14]
        iszx__cakz.hour = args[15]
        iszx__cakz.minute = args[16]
        iszx__cakz.second = args[17]
        iszx__cakz.microsecond = args[18]
        iszx__cakz.nanosecond = args[19]
        iszx__cakz.has_kws = args[20]
        return iszx__cakz._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        rsm__bnvm = -1 if dateoffset.n < 0 else 1
        for zsz__abgu in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += rsm__bnvm * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += rsm__bnvm * dateoffset._months
            year, month, yjv__rwz = calculate_month_end_date(year, month,
                day, 0)
            if day > yjv__rwz:
                day = yjv__rwz
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            hix__xpem = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            if rsm__bnvm == -1:
                hix__xpem = -hix__xpem
            ts = ts + hix__xpem
            if dateoffset._weekday != -1:
                otipg__heitk = ts.weekday()
                pau__jiq = (dateoffset._weekday - otipg__heitk) % 7
                ts = ts + pd.Timedelta(days=pau__jiq)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            nanoseconds = lhs._nanoseconds
            nanosecond = lhs._nanosecond
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize,
                    nanoseconds=nanoseconds, nanosecond=nanosecond)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qhbnu__fjfet = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, qhbnu__fjfet)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        urhda__cxw = -1 if weekday is None else weekday
        return init_week(n, normalize, urhda__cxw)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        mibfb__npna = cgutils.create_struct_proxy(typ)(context, builder)
        mibfb__npna.n = args[0]
        mibfb__npna.normalize = args[1]
        mibfb__npna.weekday = args[2]
        return mibfb__npna._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    mibfb__npna = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ioe__ugy = c.pyapi.long_from_longlong(mibfb__npna.n)
    ospe__mzawm = c.pyapi.from_native_value(types.boolean, mibfb__npna.
        normalize, c.env_manager)
    perpj__iwo = c.pyapi.long_from_longlong(mibfb__npna.weekday)
    ggri__unvh = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    iguwx__enn = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), mibfb__npna.weekday)
    with c.builder.if_else(iguwx__enn) as (weekday_defined, weekday_undefined):
        with weekday_defined:
            jzgwq__sro = c.pyapi.call_function_objargs(ggri__unvh, (
                ioe__ugy, ospe__mzawm, perpj__iwo))
            brtmr__gqur = c.builder.block
        with weekday_undefined:
            cnkev__jzgc = c.pyapi.call_function_objargs(ggri__unvh, (
                ioe__ugy, ospe__mzawm))
            vqzd__cxew = c.builder.block
    kcs__sjt = c.builder.phi(jzgwq__sro.type)
    kcs__sjt.add_incoming(jzgwq__sro, brtmr__gqur)
    kcs__sjt.add_incoming(cnkev__jzgc, vqzd__cxew)
    c.pyapi.decref(perpj__iwo)
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    c.pyapi.decref(ggri__unvh)
    return kcs__sjt


@unbox(WeekType)
def unbox_week(typ, val, c):
    ioe__ugy = c.pyapi.object_getattr_string(val, 'n')
    ospe__mzawm = c.pyapi.object_getattr_string(val, 'normalize')
    perpj__iwo = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(ioe__ugy)
    normalize = c.pyapi.to_native_value(types.bool_, ospe__mzawm).value
    kdg__csvyd = c.pyapi.make_none()
    gxo__npwx = c.builder.icmp_unsigned('==', perpj__iwo, kdg__csvyd)
    with c.builder.if_else(gxo__npwx) as (weekday_undefined, weekday_defined):
        with weekday_defined:
            jzgwq__sro = c.pyapi.long_as_longlong(perpj__iwo)
            brtmr__gqur = c.builder.block
        with weekday_undefined:
            cnkev__jzgc = lir.Constant(lir.IntType(64), -1)
            vqzd__cxew = c.builder.block
    kcs__sjt = c.builder.phi(jzgwq__sro.type)
    kcs__sjt.add_incoming(jzgwq__sro, brtmr__gqur)
    kcs__sjt.add_incoming(cnkev__jzgc, vqzd__cxew)
    mibfb__npna = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mibfb__npna.n = n
    mibfb__npna.normalize = normalize
    mibfb__npna.weekday = kcs__sjt
    c.pyapi.decref(ioe__ugy)
    c.pyapi.decref(ospe__mzawm)
    c.pyapi.decref(perpj__iwo)
    uxgl__zju = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mibfb__npna._getvalue(), is_error=uxgl__zju)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            snz__lgyr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                yuw__rek = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day)
            else:
                yuw__rek = rhs
            return yuw__rek + snz__lgyr
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            snz__lgyr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                yuw__rek = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day)
            else:
                yuw__rek = pd.Timestamp(year=rhs.year, month=rhs.month, day
                    =rhs.day, hour=rhs.hour, minute=rhs.minute, second=rhs.
                    second, microsecond=rhs.microsecond)
            return yuw__rek + snz__lgyr
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            snz__lgyr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + snz__lgyr
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        ijnn__szlqc = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=ijnn__szlqc)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for ppivy__kssog in date_offset_unsupported_attrs:
        pdcr__sxv = 'pandas.tseries.offsets.DateOffset.' + ppivy__kssog
        overload_attribute(DateOffsetType, ppivy__kssog)(
            create_unsupported_overload(pdcr__sxv))
    for ppivy__kssog in date_offset_unsupported:
        pdcr__sxv = 'pandas.tseries.offsets.DateOffset.' + ppivy__kssog
        overload_method(DateOffsetType, ppivy__kssog)(
            create_unsupported_overload(pdcr__sxv))


def _install_month_begin_unsupported():
    for ppivy__kssog in month_begin_unsupported_attrs:
        pdcr__sxv = 'pandas.tseries.offsets.MonthBegin.' + ppivy__kssog
        overload_attribute(MonthBeginType, ppivy__kssog)(
            create_unsupported_overload(pdcr__sxv))
    for ppivy__kssog in month_begin_unsupported:
        pdcr__sxv = 'pandas.tseries.offsets.MonthBegin.' + ppivy__kssog
        overload_method(MonthBeginType, ppivy__kssog)(
            create_unsupported_overload(pdcr__sxv))


def _install_month_end_unsupported():
    for ppivy__kssog in date_offset_unsupported_attrs:
        pdcr__sxv = 'pandas.tseries.offsets.MonthEnd.' + ppivy__kssog
        overload_attribute(MonthEndType, ppivy__kssog)(
            create_unsupported_overload(pdcr__sxv))
    for ppivy__kssog in date_offset_unsupported:
        pdcr__sxv = 'pandas.tseries.offsets.MonthEnd.' + ppivy__kssog
        overload_method(MonthEndType, ppivy__kssog)(create_unsupported_overload
            (pdcr__sxv))


def _install_week_unsupported():
    for ppivy__kssog in week_unsupported_attrs:
        pdcr__sxv = 'pandas.tseries.offsets.Week.' + ppivy__kssog
        overload_attribute(WeekType, ppivy__kssog)(create_unsupported_overload
            (pdcr__sxv))
    for ppivy__kssog in week_unsupported:
        pdcr__sxv = 'pandas.tseries.offsets.Week.' + ppivy__kssog
        overload_method(WeekType, ppivy__kssog)(create_unsupported_overload
            (pdcr__sxv))


def _install_offsets_unsupported():
    for jjdaj__ioul in offsets_unsupported:
        pdcr__sxv = 'pandas.tseries.offsets.' + jjdaj__ioul.__name__
        overload(jjdaj__ioul)(create_unsupported_overload(pdcr__sxv))


def _install_frequencies_unsupported():
    for jjdaj__ioul in frequencies_unsupported:
        pdcr__sxv = 'pandas.tseries.frequencies.' + jjdaj__ioul.__name__
        overload(jjdaj__ioul)(create_unsupported_overload(pdcr__sxv))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
