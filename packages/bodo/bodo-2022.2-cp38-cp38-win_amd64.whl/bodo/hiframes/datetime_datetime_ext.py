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
        wujwr__byoxc = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, wujwr__byoxc)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    iemlx__fcv = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    zcovq__wfy = c.pyapi.long_from_longlong(iemlx__fcv.year)
    lqdmy__hyg = c.pyapi.long_from_longlong(iemlx__fcv.month)
    jbm__qiny = c.pyapi.long_from_longlong(iemlx__fcv.day)
    faqyv__wbsxf = c.pyapi.long_from_longlong(iemlx__fcv.hour)
    qdei__seoom = c.pyapi.long_from_longlong(iemlx__fcv.minute)
    pxjeq__eii = c.pyapi.long_from_longlong(iemlx__fcv.second)
    kwu__rzwb = c.pyapi.long_from_longlong(iemlx__fcv.microsecond)
    wdwpz__fkdt = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    evw__vrkn = c.pyapi.call_function_objargs(wdwpz__fkdt, (zcovq__wfy,
        lqdmy__hyg, jbm__qiny, faqyv__wbsxf, qdei__seoom, pxjeq__eii,
        kwu__rzwb))
    c.pyapi.decref(zcovq__wfy)
    c.pyapi.decref(lqdmy__hyg)
    c.pyapi.decref(jbm__qiny)
    c.pyapi.decref(faqyv__wbsxf)
    c.pyapi.decref(qdei__seoom)
    c.pyapi.decref(pxjeq__eii)
    c.pyapi.decref(kwu__rzwb)
    c.pyapi.decref(wdwpz__fkdt)
    return evw__vrkn


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    zcovq__wfy = c.pyapi.object_getattr_string(val, 'year')
    lqdmy__hyg = c.pyapi.object_getattr_string(val, 'month')
    jbm__qiny = c.pyapi.object_getattr_string(val, 'day')
    faqyv__wbsxf = c.pyapi.object_getattr_string(val, 'hour')
    qdei__seoom = c.pyapi.object_getattr_string(val, 'minute')
    pxjeq__eii = c.pyapi.object_getattr_string(val, 'second')
    kwu__rzwb = c.pyapi.object_getattr_string(val, 'microsecond')
    iemlx__fcv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    iemlx__fcv.year = c.pyapi.long_as_longlong(zcovq__wfy)
    iemlx__fcv.month = c.pyapi.long_as_longlong(lqdmy__hyg)
    iemlx__fcv.day = c.pyapi.long_as_longlong(jbm__qiny)
    iemlx__fcv.hour = c.pyapi.long_as_longlong(faqyv__wbsxf)
    iemlx__fcv.minute = c.pyapi.long_as_longlong(qdei__seoom)
    iemlx__fcv.second = c.pyapi.long_as_longlong(pxjeq__eii)
    iemlx__fcv.microsecond = c.pyapi.long_as_longlong(kwu__rzwb)
    c.pyapi.decref(zcovq__wfy)
    c.pyapi.decref(lqdmy__hyg)
    c.pyapi.decref(jbm__qiny)
    c.pyapi.decref(faqyv__wbsxf)
    c.pyapi.decref(qdei__seoom)
    c.pyapi.decref(pxjeq__eii)
    c.pyapi.decref(kwu__rzwb)
    igltd__kdoqq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(iemlx__fcv._getvalue(), is_error=igltd__kdoqq)


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
        iemlx__fcv = cgutils.create_struct_proxy(typ)(context, builder)
        iemlx__fcv.year = args[0]
        iemlx__fcv.month = args[1]
        iemlx__fcv.day = args[2]
        iemlx__fcv.hour = args[3]
        iemlx__fcv.minute = args[4]
        iemlx__fcv.second = args[5]
        iemlx__fcv.microsecond = args[6]
        return iemlx__fcv._getvalue()
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
                y, xkmbt__djga = lhs.year, rhs.year
                uxtnl__yun, pnu__fbo = lhs.month, rhs.month
                d, gbcv__mlg = lhs.day, rhs.day
                mdd__vzjsn, jocsx__ztffb = lhs.hour, rhs.hour
                yfx__ntli, jhsbl__zfuua = lhs.minute, rhs.minute
                kzjj__oig, vzu__yzvg = lhs.second, rhs.second
                oau__nwrzy, tlfdh__wfdgl = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, uxtnl__yun, d, mdd__vzjsn, yfx__ntli,
                    kzjj__oig, oau__nwrzy), (xkmbt__djga, pnu__fbo,
                    gbcv__mlg, jocsx__ztffb, jhsbl__zfuua, vzu__yzvg,
                    tlfdh__wfdgl)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            xbj__pctv = lhs.toordinal()
            nqiz__ygprg = rhs.toordinal()
            xcry__gmuh = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            spci__wnxqz = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            imtr__jfl = datetime.timedelta(xbj__pctv - nqiz__ygprg, 
                xcry__gmuh - spci__wnxqz, lhs.microsecond - rhs.microsecond)
            return imtr__jfl
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    xmcsg__ounwy = context.make_helper(builder, fromty, value=val)
    zkl__kbou = cgutils.as_bool_bit(builder, xmcsg__ounwy.valid)
    with builder.if_else(zkl__kbou) as (then, orelse):
        with then:
            jjbg__qkr = context.cast(builder, xmcsg__ounwy.data, fromty.
                type, toty)
            jtti__ivx = builder.block
        with orelse:
            tedym__cmfg = numba.np.npdatetime.NAT
            qvetu__aeb = builder.block
    evw__vrkn = builder.phi(jjbg__qkr.type)
    evw__vrkn.add_incoming(jjbg__qkr, jtti__ivx)
    evw__vrkn.add_incoming(tedym__cmfg, qvetu__aeb)
    return evw__vrkn
