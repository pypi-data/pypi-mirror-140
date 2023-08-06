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
        yzdjv__dgnck = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, yzdjv__dgnck)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    keh__yaak = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    eiam__boq = c.pyapi.long_from_longlong(keh__yaak.n)
    mqh__ttwy = c.pyapi.from_native_value(types.boolean, keh__yaak.
        normalize, c.env_manager)
    bph__ibugt = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    cmtu__wfpd = c.pyapi.call_function_objargs(bph__ibugt, (eiam__boq,
        mqh__ttwy))
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    c.pyapi.decref(bph__ibugt)
    return cmtu__wfpd


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    eiam__boq = c.pyapi.object_getattr_string(val, 'n')
    mqh__ttwy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(eiam__boq)
    normalize = c.pyapi.to_native_value(types.bool_, mqh__ttwy).value
    keh__yaak = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    keh__yaak.n = n
    keh__yaak.normalize = normalize
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    tmspr__kqlk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(keh__yaak._getvalue(), is_error=tmspr__kqlk)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        keh__yaak = cgutils.create_struct_proxy(typ)(context, builder)
        keh__yaak.n = args[0]
        keh__yaak.normalize = args[1]
        return keh__yaak._getvalue()
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
        yzdjv__dgnck = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, yzdjv__dgnck)


@box(MonthEndType)
def box_month_end(typ, val, c):
    plgj__wszq = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    eiam__boq = c.pyapi.long_from_longlong(plgj__wszq.n)
    mqh__ttwy = c.pyapi.from_native_value(types.boolean, plgj__wszq.
        normalize, c.env_manager)
    plthl__rac = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    cmtu__wfpd = c.pyapi.call_function_objargs(plthl__rac, (eiam__boq,
        mqh__ttwy))
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    c.pyapi.decref(plthl__rac)
    return cmtu__wfpd


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    eiam__boq = c.pyapi.object_getattr_string(val, 'n')
    mqh__ttwy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(eiam__boq)
    normalize = c.pyapi.to_native_value(types.bool_, mqh__ttwy).value
    plgj__wszq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    plgj__wszq.n = n
    plgj__wszq.normalize = normalize
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    tmspr__kqlk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(plgj__wszq._getvalue(), is_error=tmspr__kqlk)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        plgj__wszq = cgutils.create_struct_proxy(typ)(context, builder)
        plgj__wszq.n = args[0]
        plgj__wszq.normalize = args[1]
        return plgj__wszq._getvalue()
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
        plgj__wszq = get_days_in_month(year, month)
        if plgj__wszq > day:
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
        yzdjv__dgnck = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, yzdjv__dgnck)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    jaw__dwvf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    aur__dklu = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for zzqn__ffiy, fub__eoymq in enumerate(date_offset_fields):
        c.builder.store(getattr(jaw__dwvf, fub__eoymq), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(aur__dklu, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * zzqn__ffiy)), lir.IntType(64)
            .as_pointer()))
    rao__lfsdy = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    wvr__mlruv = cgutils.get_or_insert_function(c.builder.module,
        rao__lfsdy, name='box_date_offset')
    knpjt__vpk = c.builder.call(wvr__mlruv, [jaw__dwvf.n, jaw__dwvf.
        normalize, aur__dklu, jaw__dwvf.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return knpjt__vpk


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    eiam__boq = c.pyapi.object_getattr_string(val, 'n')
    mqh__ttwy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(eiam__boq)
    normalize = c.pyapi.to_native_value(types.bool_, mqh__ttwy).value
    aur__dklu = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    rao__lfsdy = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    dorar__moru = cgutils.get_or_insert_function(c.builder.module,
        rao__lfsdy, name='unbox_date_offset')
    has_kws = c.builder.call(dorar__moru, [val, aur__dklu])
    jaw__dwvf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jaw__dwvf.n = n
    jaw__dwvf.normalize = normalize
    for zzqn__ffiy, fub__eoymq in enumerate(date_offset_fields):
        setattr(jaw__dwvf, fub__eoymq, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(aur__dklu, lir.IntType(64)), lir
            .Constant(lir.IntType(64), 8 * zzqn__ffiy)), lir.IntType(64).
            as_pointer())))
    jaw__dwvf.has_kws = has_kws
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    tmspr__kqlk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jaw__dwvf._getvalue(), is_error=tmspr__kqlk)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    gnrvd__grzy = [n, normalize]
    has_kws = False
    sszg__mgfuo = [0] * 9 + [-1] * 9
    for zzqn__ffiy, fub__eoymq in enumerate(date_offset_fields):
        if hasattr(pyval, fub__eoymq):
            ozobv__trwq = context.get_constant(types.int64, getattr(pyval,
                fub__eoymq))
            if fub__eoymq != 'nanoseconds' and fub__eoymq != 'nanosecond':
                has_kws = True
        else:
            ozobv__trwq = context.get_constant(types.int64, sszg__mgfuo[
                zzqn__ffiy])
        gnrvd__grzy.append(ozobv__trwq)
    has_kws = context.get_constant(types.boolean, has_kws)
    gnrvd__grzy.append(has_kws)
    return lir.Constant.literal_struct(gnrvd__grzy)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    jhfk__pem = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for lgc__bbun in jhfk__pem:
        if not is_overload_none(lgc__bbun):
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
        jaw__dwvf = cgutils.create_struct_proxy(typ)(context, builder)
        jaw__dwvf.n = args[0]
        jaw__dwvf.normalize = args[1]
        jaw__dwvf.years = args[2]
        jaw__dwvf.months = args[3]
        jaw__dwvf.weeks = args[4]
        jaw__dwvf.days = args[5]
        jaw__dwvf.hours = args[6]
        jaw__dwvf.minutes = args[7]
        jaw__dwvf.seconds = args[8]
        jaw__dwvf.microseconds = args[9]
        jaw__dwvf.nanoseconds = args[10]
        jaw__dwvf.year = args[11]
        jaw__dwvf.month = args[12]
        jaw__dwvf.day = args[13]
        jaw__dwvf.weekday = args[14]
        jaw__dwvf.hour = args[15]
        jaw__dwvf.minute = args[16]
        jaw__dwvf.second = args[17]
        jaw__dwvf.microsecond = args[18]
        jaw__dwvf.nanosecond = args[19]
        jaw__dwvf.has_kws = args[20]
        return jaw__dwvf._getvalue()
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
        omzwf__acfcn = -1 if dateoffset.n < 0 else 1
        for qkacu__qufvr in range(np.abs(dateoffset.n)):
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
            year += omzwf__acfcn * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += omzwf__acfcn * dateoffset._months
            year, month, frh__slc = calculate_month_end_date(year, month,
                day, 0)
            if day > frh__slc:
                day = frh__slc
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
            pto__grid = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            if omzwf__acfcn == -1:
                pto__grid = -pto__grid
            ts = ts + pto__grid
            if dateoffset._weekday != -1:
                fjtw__ypb = ts.weekday()
                xwv__egr = (dateoffset._weekday - fjtw__ypb) % 7
                ts = ts + pd.Timedelta(days=xwv__egr)
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
        yzdjv__dgnck = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, yzdjv__dgnck)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        unv__avlim = -1 if weekday is None else weekday
        return init_week(n, normalize, unv__avlim)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        vdbq__vbbo = cgutils.create_struct_proxy(typ)(context, builder)
        vdbq__vbbo.n = args[0]
        vdbq__vbbo.normalize = args[1]
        vdbq__vbbo.weekday = args[2]
        return vdbq__vbbo._getvalue()
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
    vdbq__vbbo = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    eiam__boq = c.pyapi.long_from_longlong(vdbq__vbbo.n)
    mqh__ttwy = c.pyapi.from_native_value(types.boolean, vdbq__vbbo.
        normalize, c.env_manager)
    gisr__qkzz = c.pyapi.long_from_longlong(vdbq__vbbo.weekday)
    mqeo__rco = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    dxcop__ytu = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), vdbq__vbbo.weekday)
    with c.builder.if_else(dxcop__ytu) as (weekday_defined, weekday_undefined):
        with weekday_defined:
            yyv__jqow = c.pyapi.call_function_objargs(mqeo__rco, (eiam__boq,
                mqh__ttwy, gisr__qkzz))
            bwuqq__clm = c.builder.block
        with weekday_undefined:
            jbt__rgr = c.pyapi.call_function_objargs(mqeo__rco, (eiam__boq,
                mqh__ttwy))
            pox__exxh = c.builder.block
    cmtu__wfpd = c.builder.phi(yyv__jqow.type)
    cmtu__wfpd.add_incoming(yyv__jqow, bwuqq__clm)
    cmtu__wfpd.add_incoming(jbt__rgr, pox__exxh)
    c.pyapi.decref(gisr__qkzz)
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    c.pyapi.decref(mqeo__rco)
    return cmtu__wfpd


@unbox(WeekType)
def unbox_week(typ, val, c):
    eiam__boq = c.pyapi.object_getattr_string(val, 'n')
    mqh__ttwy = c.pyapi.object_getattr_string(val, 'normalize')
    gisr__qkzz = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(eiam__boq)
    normalize = c.pyapi.to_native_value(types.bool_, mqh__ttwy).value
    buci__vjvef = c.pyapi.make_none()
    fsc__bsuz = c.builder.icmp_unsigned('==', gisr__qkzz, buci__vjvef)
    with c.builder.if_else(fsc__bsuz) as (weekday_undefined, weekday_defined):
        with weekday_defined:
            yyv__jqow = c.pyapi.long_as_longlong(gisr__qkzz)
            bwuqq__clm = c.builder.block
        with weekday_undefined:
            jbt__rgr = lir.Constant(lir.IntType(64), -1)
            pox__exxh = c.builder.block
    cmtu__wfpd = c.builder.phi(yyv__jqow.type)
    cmtu__wfpd.add_incoming(yyv__jqow, bwuqq__clm)
    cmtu__wfpd.add_incoming(jbt__rgr, pox__exxh)
    vdbq__vbbo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vdbq__vbbo.n = n
    vdbq__vbbo.normalize = normalize
    vdbq__vbbo.weekday = cmtu__wfpd
    c.pyapi.decref(eiam__boq)
    c.pyapi.decref(mqh__ttwy)
    c.pyapi.decref(gisr__qkzz)
    tmspr__kqlk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vdbq__vbbo._getvalue(), is_error=tmspr__kqlk)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            teucr__jky = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                uhm__cspop = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                uhm__cspop = rhs
            return uhm__cspop + teucr__jky
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            teucr__jky = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                uhm__cspop = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                uhm__cspop = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return uhm__cspop + teucr__jky
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            teucr__jky = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + teucr__jky
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
        qrep__ksdh = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=qrep__ksdh)


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
    for ccl__tnw in date_offset_unsupported_attrs:
        smj__qve = 'pandas.tseries.offsets.DateOffset.' + ccl__tnw
        overload_attribute(DateOffsetType, ccl__tnw)(
            create_unsupported_overload(smj__qve))
    for ccl__tnw in date_offset_unsupported:
        smj__qve = 'pandas.tseries.offsets.DateOffset.' + ccl__tnw
        overload_method(DateOffsetType, ccl__tnw)(create_unsupported_overload
            (smj__qve))


def _install_month_begin_unsupported():
    for ccl__tnw in month_begin_unsupported_attrs:
        smj__qve = 'pandas.tseries.offsets.MonthBegin.' + ccl__tnw
        overload_attribute(MonthBeginType, ccl__tnw)(
            create_unsupported_overload(smj__qve))
    for ccl__tnw in month_begin_unsupported:
        smj__qve = 'pandas.tseries.offsets.MonthBegin.' + ccl__tnw
        overload_method(MonthBeginType, ccl__tnw)(create_unsupported_overload
            (smj__qve))


def _install_month_end_unsupported():
    for ccl__tnw in date_offset_unsupported_attrs:
        smj__qve = 'pandas.tseries.offsets.MonthEnd.' + ccl__tnw
        overload_attribute(MonthEndType, ccl__tnw)(create_unsupported_overload
            (smj__qve))
    for ccl__tnw in date_offset_unsupported:
        smj__qve = 'pandas.tseries.offsets.MonthEnd.' + ccl__tnw
        overload_method(MonthEndType, ccl__tnw)(create_unsupported_overload
            (smj__qve))


def _install_week_unsupported():
    for ccl__tnw in week_unsupported_attrs:
        smj__qve = 'pandas.tseries.offsets.Week.' + ccl__tnw
        overload_attribute(WeekType, ccl__tnw)(create_unsupported_overload(
            smj__qve))
    for ccl__tnw in week_unsupported:
        smj__qve = 'pandas.tseries.offsets.Week.' + ccl__tnw
        overload_method(WeekType, ccl__tnw)(create_unsupported_overload(
            smj__qve))


def _install_offsets_unsupported():
    for ozobv__trwq in offsets_unsupported:
        smj__qve = 'pandas.tseries.offsets.' + ozobv__trwq.__name__
        overload(ozobv__trwq)(create_unsupported_overload(smj__qve))


def _install_frequencies_unsupported():
    for ozobv__trwq in frequencies_unsupported:
        smj__qve = 'pandas.tseries.frequencies.' + ozobv__trwq.__name__
        overload(ozobv__trwq)(create_unsupported_overload(smj__qve))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
