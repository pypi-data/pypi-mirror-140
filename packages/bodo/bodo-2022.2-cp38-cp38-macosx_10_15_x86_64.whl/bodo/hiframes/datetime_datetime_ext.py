import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gjcou__gatew = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, gjcou__gatew)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    ahmw__ybvx = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    arlm__xqvke = c.pyapi.long_from_longlong(ahmw__ybvx.year)
    bsc__bkp = c.pyapi.long_from_longlong(ahmw__ybvx.month)
    fioz__uvgy = c.pyapi.long_from_longlong(ahmw__ybvx.day)
    hsw__ditb = c.pyapi.long_from_longlong(ahmw__ybvx.hour)
    rshm__fqwvw = c.pyapi.long_from_longlong(ahmw__ybvx.minute)
    hfdd__wvvyy = c.pyapi.long_from_longlong(ahmw__ybvx.second)
    xvqf__qmhlc = c.pyapi.long_from_longlong(ahmw__ybvx.microsecond)
    fvms__hcqpj = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    qsbb__zpy = c.pyapi.call_function_objargs(fvms__hcqpj, (arlm__xqvke,
        bsc__bkp, fioz__uvgy, hsw__ditb, rshm__fqwvw, hfdd__wvvyy, xvqf__qmhlc)
        )
    c.pyapi.decref(arlm__xqvke)
    c.pyapi.decref(bsc__bkp)
    c.pyapi.decref(fioz__uvgy)
    c.pyapi.decref(hsw__ditb)
    c.pyapi.decref(rshm__fqwvw)
    c.pyapi.decref(hfdd__wvvyy)
    c.pyapi.decref(xvqf__qmhlc)
    c.pyapi.decref(fvms__hcqpj)
    return qsbb__zpy


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    arlm__xqvke = c.pyapi.object_getattr_string(val, 'year')
    bsc__bkp = c.pyapi.object_getattr_string(val, 'month')
    fioz__uvgy = c.pyapi.object_getattr_string(val, 'day')
    hsw__ditb = c.pyapi.object_getattr_string(val, 'hour')
    rshm__fqwvw = c.pyapi.object_getattr_string(val, 'minute')
    hfdd__wvvyy = c.pyapi.object_getattr_string(val, 'second')
    xvqf__qmhlc = c.pyapi.object_getattr_string(val, 'microsecond')
    ahmw__ybvx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ahmw__ybvx.year = c.pyapi.long_as_longlong(arlm__xqvke)
    ahmw__ybvx.month = c.pyapi.long_as_longlong(bsc__bkp)
    ahmw__ybvx.day = c.pyapi.long_as_longlong(fioz__uvgy)
    ahmw__ybvx.hour = c.pyapi.long_as_longlong(hsw__ditb)
    ahmw__ybvx.minute = c.pyapi.long_as_longlong(rshm__fqwvw)
    ahmw__ybvx.second = c.pyapi.long_as_longlong(hfdd__wvvyy)
    ahmw__ybvx.microsecond = c.pyapi.long_as_longlong(xvqf__qmhlc)
    c.pyapi.decref(arlm__xqvke)
    c.pyapi.decref(bsc__bkp)
    c.pyapi.decref(fioz__uvgy)
    c.pyapi.decref(hsw__ditb)
    c.pyapi.decref(rshm__fqwvw)
    c.pyapi.decref(hfdd__wvvyy)
    c.pyapi.decref(xvqf__qmhlc)
    efef__firkx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ahmw__ybvx._getvalue(), is_error=efef__firkx)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        ahmw__ybvx = cgutils.create_struct_proxy(typ)(context, builder)
        ahmw__ybvx.year = args[0]
        ahmw__ybvx.month = args[1]
        ahmw__ybvx.day = args[2]
        ahmw__ybvx.hour = args[3]
        ahmw__ybvx.minute = args[4]
        ahmw__ybvx.second = args[5]
        ahmw__ybvx.microsecond = args[6]
        return ahmw__ybvx._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, jlb__gbo = lhs.year, rhs.year
                guevz__goh, lce__ayoa = lhs.month, rhs.month
                d, yfabg__wdnt = lhs.day, rhs.day
                jkgl__mviwn, ari__gpbjo = lhs.hour, rhs.hour
                tfllk__ebl, ztjc__igx = lhs.minute, rhs.minute
                iic__vneu, rtx__ameb = lhs.second, rhs.second
                qesi__apxdt, ahcyk__hfkdu = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, guevz__goh, d, jkgl__mviwn, tfllk__ebl,
                    iic__vneu, qesi__apxdt), (jlb__gbo, lce__ayoa,
                    yfabg__wdnt, ari__gpbjo, ztjc__igx, rtx__ameb,
                    ahcyk__hfkdu)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            kkbrg__lzfjx = lhs.toordinal()
            xfwgc__mbzz = rhs.toordinal()
            qhhaq__hqja = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            mfif__oiun = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            qtght__bhi = datetime.timedelta(kkbrg__lzfjx - xfwgc__mbzz, 
                qhhaq__hqja - mfif__oiun, lhs.microsecond - rhs.microsecond)
            return qtght__bhi
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    nuzws__nuc = context.make_helper(builder, fromty, value=val)
    wboxv__eaa = cgutils.as_bool_bit(builder, nuzws__nuc.valid)
    with builder.if_else(wboxv__eaa) as (then, orelse):
        with then:
            pmqf__qobxq = context.cast(builder, nuzws__nuc.data, fromty.
                type, toty)
            qonk__yfj = builder.block
        with orelse:
            mwhxm__mvemz = numba.np.npdatetime.NAT
            rnbbm__oppct = builder.block
    qsbb__zpy = builder.phi(pmqf__qobxq.type)
    qsbb__zpy.add_incoming(pmqf__qobxq, qonk__yfj)
    qsbb__zpy.add_incoming(mwhxm__mvemz, rnbbm__oppct)
    return qsbb__zpy
