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
        jypu__iogm = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, jypu__iogm)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    mof__fyb = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    nkshp__glw = c.pyapi.long_from_longlong(mof__fyb.year)
    rgl__dtbr = c.pyapi.long_from_longlong(mof__fyb.month)
    xoqjn__kml = c.pyapi.long_from_longlong(mof__fyb.day)
    hcjmr__mvf = c.pyapi.long_from_longlong(mof__fyb.hour)
    yywsf__kywo = c.pyapi.long_from_longlong(mof__fyb.minute)
    kgn__euk = c.pyapi.long_from_longlong(mof__fyb.second)
    ufom__ndirw = c.pyapi.long_from_longlong(mof__fyb.microsecond)
    tul__pubki = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    icebr__mjn = c.pyapi.call_function_objargs(tul__pubki, (nkshp__glw,
        rgl__dtbr, xoqjn__kml, hcjmr__mvf, yywsf__kywo, kgn__euk, ufom__ndirw))
    c.pyapi.decref(nkshp__glw)
    c.pyapi.decref(rgl__dtbr)
    c.pyapi.decref(xoqjn__kml)
    c.pyapi.decref(hcjmr__mvf)
    c.pyapi.decref(yywsf__kywo)
    c.pyapi.decref(kgn__euk)
    c.pyapi.decref(ufom__ndirw)
    c.pyapi.decref(tul__pubki)
    return icebr__mjn


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    nkshp__glw = c.pyapi.object_getattr_string(val, 'year')
    rgl__dtbr = c.pyapi.object_getattr_string(val, 'month')
    xoqjn__kml = c.pyapi.object_getattr_string(val, 'day')
    hcjmr__mvf = c.pyapi.object_getattr_string(val, 'hour')
    yywsf__kywo = c.pyapi.object_getattr_string(val, 'minute')
    kgn__euk = c.pyapi.object_getattr_string(val, 'second')
    ufom__ndirw = c.pyapi.object_getattr_string(val, 'microsecond')
    mof__fyb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mof__fyb.year = c.pyapi.long_as_longlong(nkshp__glw)
    mof__fyb.month = c.pyapi.long_as_longlong(rgl__dtbr)
    mof__fyb.day = c.pyapi.long_as_longlong(xoqjn__kml)
    mof__fyb.hour = c.pyapi.long_as_longlong(hcjmr__mvf)
    mof__fyb.minute = c.pyapi.long_as_longlong(yywsf__kywo)
    mof__fyb.second = c.pyapi.long_as_longlong(kgn__euk)
    mof__fyb.microsecond = c.pyapi.long_as_longlong(ufom__ndirw)
    c.pyapi.decref(nkshp__glw)
    c.pyapi.decref(rgl__dtbr)
    c.pyapi.decref(xoqjn__kml)
    c.pyapi.decref(hcjmr__mvf)
    c.pyapi.decref(yywsf__kywo)
    c.pyapi.decref(kgn__euk)
    c.pyapi.decref(ufom__ndirw)
    gdjv__brhc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mof__fyb._getvalue(), is_error=gdjv__brhc)


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
        mof__fyb = cgutils.create_struct_proxy(typ)(context, builder)
        mof__fyb.year = args[0]
        mof__fyb.month = args[1]
        mof__fyb.day = args[2]
        mof__fyb.hour = args[3]
        mof__fyb.minute = args[4]
        mof__fyb.second = args[5]
        mof__fyb.microsecond = args[6]
        return mof__fyb._getvalue()
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
                y, eknd__adutw = lhs.year, rhs.year
                dwxf__dwvu, njgzi__bis = lhs.month, rhs.month
                d, baltx__dvfml = lhs.day, rhs.day
                vxi__vsf, xuuic__wwj = lhs.hour, rhs.hour
                dwll__uxbvm, zbd__vpoj = lhs.minute, rhs.minute
                eyait__ahs, gmacc__wclq = lhs.second, rhs.second
                xjplg__gfefa, tda__oyr = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, dwxf__dwvu, d, vxi__vsf, dwll__uxbvm,
                    eyait__ahs, xjplg__gfefa), (eknd__adutw, njgzi__bis,
                    baltx__dvfml, xuuic__wwj, zbd__vpoj, gmacc__wclq,
                    tda__oyr)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            svic__giat = lhs.toordinal()
            epx__ldcay = rhs.toordinal()
            jfzf__rpc = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            mmuu__uqdj = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            itku__inqtg = datetime.timedelta(svic__giat - epx__ldcay, 
                jfzf__rpc - mmuu__uqdj, lhs.microsecond - rhs.microsecond)
            return itku__inqtg
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    pfaf__gjt = context.make_helper(builder, fromty, value=val)
    xlj__zcrw = cgutils.as_bool_bit(builder, pfaf__gjt.valid)
    with builder.if_else(xlj__zcrw) as (then, orelse):
        with then:
            saw__arb = context.cast(builder, pfaf__gjt.data, fromty.type, toty)
            yinjd__gbuhm = builder.block
        with orelse:
            sids__dmfp = numba.np.npdatetime.NAT
            rtxj__llkrl = builder.block
    icebr__mjn = builder.phi(saw__arb.type)
    icebr__mjn.add_incoming(saw__arb, yinjd__gbuhm)
    icebr__mjn.add_incoming(sids__dmfp, rtxj__llkrl)
    return icebr__mjn
