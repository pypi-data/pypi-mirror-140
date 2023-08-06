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
        maabt__mbow = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, maabt__mbow)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    vhdr__riigo = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yzyxg__mjehs = c.pyapi.long_from_longlong(vhdr__riigo.n)
    sofue__apjwa = c.pyapi.from_native_value(types.boolean, vhdr__riigo.
        normalize, c.env_manager)
    nojzz__dmov = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    qmuhl__nzewn = c.pyapi.call_function_objargs(nojzz__dmov, (yzyxg__mjehs,
        sofue__apjwa))
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    c.pyapi.decref(nojzz__dmov)
    return qmuhl__nzewn


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    yzyxg__mjehs = c.pyapi.object_getattr_string(val, 'n')
    sofue__apjwa = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yzyxg__mjehs)
    normalize = c.pyapi.to_native_value(types.bool_, sofue__apjwa).value
    vhdr__riigo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vhdr__riigo.n = n
    vhdr__riigo.normalize = normalize
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    yxgo__ymvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vhdr__riigo._getvalue(), is_error=yxgo__ymvu)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        vhdr__riigo = cgutils.create_struct_proxy(typ)(context, builder)
        vhdr__riigo.n = args[0]
        vhdr__riigo.normalize = args[1]
        return vhdr__riigo._getvalue()
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
        maabt__mbow = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, maabt__mbow)


@box(MonthEndType)
def box_month_end(typ, val, c):
    lwjfv__wlllf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yzyxg__mjehs = c.pyapi.long_from_longlong(lwjfv__wlllf.n)
    sofue__apjwa = c.pyapi.from_native_value(types.boolean, lwjfv__wlllf.
        normalize, c.env_manager)
    kzk__naic = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    qmuhl__nzewn = c.pyapi.call_function_objargs(kzk__naic, (yzyxg__mjehs,
        sofue__apjwa))
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    c.pyapi.decref(kzk__naic)
    return qmuhl__nzewn


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    yzyxg__mjehs = c.pyapi.object_getattr_string(val, 'n')
    sofue__apjwa = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yzyxg__mjehs)
    normalize = c.pyapi.to_native_value(types.bool_, sofue__apjwa).value
    lwjfv__wlllf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lwjfv__wlllf.n = n
    lwjfv__wlllf.normalize = normalize
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    yxgo__ymvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lwjfv__wlllf._getvalue(), is_error=yxgo__ymvu)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        lwjfv__wlllf = cgutils.create_struct_proxy(typ)(context, builder)
        lwjfv__wlllf.n = args[0]
        lwjfv__wlllf.normalize = args[1]
        return lwjfv__wlllf._getvalue()
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
        lwjfv__wlllf = get_days_in_month(year, month)
        if lwjfv__wlllf > day:
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
        maabt__mbow = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, maabt__mbow)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    vxvd__exd = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    icj__rbqp = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for iqqvr__jklhs, ccv__naexa in enumerate(date_offset_fields):
        c.builder.store(getattr(vxvd__exd, ccv__naexa), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(icj__rbqp, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * iqqvr__jklhs)), lir.IntType(
            64).as_pointer()))
    cylp__zup = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    hxhux__braw = cgutils.get_or_insert_function(c.builder.module,
        cylp__zup, name='box_date_offset')
    cvxuv__wvt = c.builder.call(hxhux__braw, [vxvd__exd.n, vxvd__exd.
        normalize, icj__rbqp, vxvd__exd.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return cvxuv__wvt


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    yzyxg__mjehs = c.pyapi.object_getattr_string(val, 'n')
    sofue__apjwa = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(yzyxg__mjehs)
    normalize = c.pyapi.to_native_value(types.bool_, sofue__apjwa).value
    icj__rbqp = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    cylp__zup = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    dtdg__jipjo = cgutils.get_or_insert_function(c.builder.module,
        cylp__zup, name='unbox_date_offset')
    has_kws = c.builder.call(dtdg__jipjo, [val, icj__rbqp])
    vxvd__exd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vxvd__exd.n = n
    vxvd__exd.normalize = normalize
    for iqqvr__jklhs, ccv__naexa in enumerate(date_offset_fields):
        setattr(vxvd__exd, ccv__naexa, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(icj__rbqp, lir.IntType(64)), lir
            .Constant(lir.IntType(64), 8 * iqqvr__jklhs)), lir.IntType(64).
            as_pointer())))
    vxvd__exd.has_kws = has_kws
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    yxgo__ymvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vxvd__exd._getvalue(), is_error=yxgo__ymvu)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    ngc__amzg = [n, normalize]
    has_kws = False
    tbcko__bnpkk = [0] * 9 + [-1] * 9
    for iqqvr__jklhs, ccv__naexa in enumerate(date_offset_fields):
        if hasattr(pyval, ccv__naexa):
            cjo__nsrb = context.get_constant(types.int64, getattr(pyval,
                ccv__naexa))
            if ccv__naexa != 'nanoseconds' and ccv__naexa != 'nanosecond':
                has_kws = True
        else:
            cjo__nsrb = context.get_constant(types.int64, tbcko__bnpkk[
                iqqvr__jklhs])
        ngc__amzg.append(cjo__nsrb)
    has_kws = context.get_constant(types.boolean, has_kws)
    ngc__amzg.append(has_kws)
    return lir.Constant.literal_struct(ngc__amzg)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    fvkn__lmvn = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for ttpof__xagw in fvkn__lmvn:
        if not is_overload_none(ttpof__xagw):
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
        vxvd__exd = cgutils.create_struct_proxy(typ)(context, builder)
        vxvd__exd.n = args[0]
        vxvd__exd.normalize = args[1]
        vxvd__exd.years = args[2]
        vxvd__exd.months = args[3]
        vxvd__exd.weeks = args[4]
        vxvd__exd.days = args[5]
        vxvd__exd.hours = args[6]
        vxvd__exd.minutes = args[7]
        vxvd__exd.seconds = args[8]
        vxvd__exd.microseconds = args[9]
        vxvd__exd.nanoseconds = args[10]
        vxvd__exd.year = args[11]
        vxvd__exd.month = args[12]
        vxvd__exd.day = args[13]
        vxvd__exd.weekday = args[14]
        vxvd__exd.hour = args[15]
        vxvd__exd.minute = args[16]
        vxvd__exd.second = args[17]
        vxvd__exd.microsecond = args[18]
        vxvd__exd.nanosecond = args[19]
        vxvd__exd.has_kws = args[20]
        return vxvd__exd._getvalue()
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
        orcsp__iiwm = -1 if dateoffset.n < 0 else 1
        for hltzq__yan in range(np.abs(dateoffset.n)):
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
            year += orcsp__iiwm * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += orcsp__iiwm * dateoffset._months
            year, month, gmwm__pbljk = calculate_month_end_date(year, month,
                day, 0)
            if day > gmwm__pbljk:
                day = gmwm__pbljk
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
            ikb__oyn = pd.Timedelta(days=dateoffset._days + 7 * dateoffset.
                _weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            if orcsp__iiwm == -1:
                ikb__oyn = -ikb__oyn
            ts = ts + ikb__oyn
            if dateoffset._weekday != -1:
                mbmo__hqykz = ts.weekday()
                vfa__ueom = (dateoffset._weekday - mbmo__hqykz) % 7
                ts = ts + pd.Timedelta(days=vfa__ueom)
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
        maabt__mbow = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, maabt__mbow)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        avfos__bdemy = -1 if weekday is None else weekday
        return init_week(n, normalize, avfos__bdemy)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        xxc__grt = cgutils.create_struct_proxy(typ)(context, builder)
        xxc__grt.n = args[0]
        xxc__grt.normalize = args[1]
        xxc__grt.weekday = args[2]
        return xxc__grt._getvalue()
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
    xxc__grt = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    yzyxg__mjehs = c.pyapi.long_from_longlong(xxc__grt.n)
    sofue__apjwa = c.pyapi.from_native_value(types.boolean, xxc__grt.
        normalize, c.env_manager)
    qoag__hlkl = c.pyapi.long_from_longlong(xxc__grt.weekday)
    qxye__oiv = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    bur__alst = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -
        1), xxc__grt.weekday)
    with c.builder.if_else(bur__alst) as (weekday_defined, weekday_undefined):
        with weekday_defined:
            sqm__jysjq = c.pyapi.call_function_objargs(qxye__oiv, (
                yzyxg__mjehs, sofue__apjwa, qoag__hlkl))
            wkovh__rdo = c.builder.block
        with weekday_undefined:
            qejz__bpzxy = c.pyapi.call_function_objargs(qxye__oiv, (
                yzyxg__mjehs, sofue__apjwa))
            effu__xig = c.builder.block
    qmuhl__nzewn = c.builder.phi(sqm__jysjq.type)
    qmuhl__nzewn.add_incoming(sqm__jysjq, wkovh__rdo)
    qmuhl__nzewn.add_incoming(qejz__bpzxy, effu__xig)
    c.pyapi.decref(qoag__hlkl)
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    c.pyapi.decref(qxye__oiv)
    return qmuhl__nzewn


@unbox(WeekType)
def unbox_week(typ, val, c):
    yzyxg__mjehs = c.pyapi.object_getattr_string(val, 'n')
    sofue__apjwa = c.pyapi.object_getattr_string(val, 'normalize')
    qoag__hlkl = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(yzyxg__mjehs)
    normalize = c.pyapi.to_native_value(types.bool_, sofue__apjwa).value
    cxdo__tmxf = c.pyapi.make_none()
    fifky__uxu = c.builder.icmp_unsigned('==', qoag__hlkl, cxdo__tmxf)
    with c.builder.if_else(fifky__uxu) as (weekday_undefined, weekday_defined):
        with weekday_defined:
            sqm__jysjq = c.pyapi.long_as_longlong(qoag__hlkl)
            wkovh__rdo = c.builder.block
        with weekday_undefined:
            qejz__bpzxy = lir.Constant(lir.IntType(64), -1)
            effu__xig = c.builder.block
    qmuhl__nzewn = c.builder.phi(sqm__jysjq.type)
    qmuhl__nzewn.add_incoming(sqm__jysjq, wkovh__rdo)
    qmuhl__nzewn.add_incoming(qejz__bpzxy, effu__xig)
    xxc__grt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xxc__grt.n = n
    xxc__grt.normalize = normalize
    xxc__grt.weekday = qmuhl__nzewn
    c.pyapi.decref(yzyxg__mjehs)
    c.pyapi.decref(sofue__apjwa)
    c.pyapi.decref(qoag__hlkl)
    yxgo__ymvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xxc__grt._getvalue(), is_error=yxgo__ymvu)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            vrdf__vdnki = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                bzlxd__jhbm = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                bzlxd__jhbm = rhs
            return bzlxd__jhbm + vrdf__vdnki
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            vrdf__vdnki = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                bzlxd__jhbm = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                bzlxd__jhbm = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return bzlxd__jhbm + vrdf__vdnki
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            vrdf__vdnki = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            return rhs + vrdf__vdnki
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
        oxhon__ipk = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=oxhon__ipk)


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
    for syyq__kukrc in date_offset_unsupported_attrs:
        oyk__cmbw = 'pandas.tseries.offsets.DateOffset.' + syyq__kukrc
        overload_attribute(DateOffsetType, syyq__kukrc)(
            create_unsupported_overload(oyk__cmbw))
    for syyq__kukrc in date_offset_unsupported:
        oyk__cmbw = 'pandas.tseries.offsets.DateOffset.' + syyq__kukrc
        overload_method(DateOffsetType, syyq__kukrc)(
            create_unsupported_overload(oyk__cmbw))


def _install_month_begin_unsupported():
    for syyq__kukrc in month_begin_unsupported_attrs:
        oyk__cmbw = 'pandas.tseries.offsets.MonthBegin.' + syyq__kukrc
        overload_attribute(MonthBeginType, syyq__kukrc)(
            create_unsupported_overload(oyk__cmbw))
    for syyq__kukrc in month_begin_unsupported:
        oyk__cmbw = 'pandas.tseries.offsets.MonthBegin.' + syyq__kukrc
        overload_method(MonthBeginType, syyq__kukrc)(
            create_unsupported_overload(oyk__cmbw))


def _install_month_end_unsupported():
    for syyq__kukrc in date_offset_unsupported_attrs:
        oyk__cmbw = 'pandas.tseries.offsets.MonthEnd.' + syyq__kukrc
        overload_attribute(MonthEndType, syyq__kukrc)(
            create_unsupported_overload(oyk__cmbw))
    for syyq__kukrc in date_offset_unsupported:
        oyk__cmbw = 'pandas.tseries.offsets.MonthEnd.' + syyq__kukrc
        overload_method(MonthEndType, syyq__kukrc)(create_unsupported_overload
            (oyk__cmbw))


def _install_week_unsupported():
    for syyq__kukrc in week_unsupported_attrs:
        oyk__cmbw = 'pandas.tseries.offsets.Week.' + syyq__kukrc
        overload_attribute(WeekType, syyq__kukrc)(create_unsupported_overload
            (oyk__cmbw))
    for syyq__kukrc in week_unsupported:
        oyk__cmbw = 'pandas.tseries.offsets.Week.' + syyq__kukrc
        overload_method(WeekType, syyq__kukrc)(create_unsupported_overload(
            oyk__cmbw))


def _install_offsets_unsupported():
    for cjo__nsrb in offsets_unsupported:
        oyk__cmbw = 'pandas.tseries.offsets.' + cjo__nsrb.__name__
        overload(cjo__nsrb)(create_unsupported_overload(oyk__cmbw))


def _install_frequencies_unsupported():
    for cjo__nsrb in frequencies_unsupported:
        oyk__cmbw = 'pandas.tseries.frequencies.' + cjo__nsrb.__name__
        overload(cjo__nsrb)(create_unsupported_overload(oyk__cmbw))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
