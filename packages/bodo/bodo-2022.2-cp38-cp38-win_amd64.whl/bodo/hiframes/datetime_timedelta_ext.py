"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opb__vid = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, opb__vid)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    msgv__fyplp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mgp__mdxy = c.pyapi.long_from_longlong(msgv__fyplp.value)
    wgkn__moc = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(wgkn__moc, (mgp__mdxy,))
    c.pyapi.decref(mgp__mdxy)
    c.pyapi.decref(wgkn__moc)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    mgp__mdxy = c.pyapi.object_getattr_string(val, 'value')
    blbuq__yzq = c.pyapi.long_as_longlong(mgp__mdxy)
    msgv__fyplp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    msgv__fyplp.value = blbuq__yzq
    c.pyapi.decref(mgp__mdxy)
    rptwz__dpngx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(msgv__fyplp._getvalue(), is_error=rptwz__dpngx)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            jkw__uuf = 1000 * microseconds
            return init_pd_timedelta(jkw__uuf)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            jkw__uuf = 1000 * microseconds
            return init_pd_timedelta(jkw__uuf)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    zmxcq__hhbsc, xmsm__oolir = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * zmxcq__hhbsc)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            zbw__yrmz = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + zbw__yrmz
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            kkwsx__dieie = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = kkwsx__dieie + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            pfpwn__scsw = rhs.toordinal()
            ofu__tybk = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            ooj__qpv = rhs.microsecond
            fip__pnzjl = lhs.value // 1000
            wzyac__phdf = lhs.nanoseconds
            yenpy__ohbk = ooj__qpv + fip__pnzjl
            yyhb__fxvjv = 1000000 * (pfpwn__scsw * 86400 + ofu__tybk
                ) + yenpy__ohbk
            dty__tfsf = wzyac__phdf
            return compute_pd_timestamp(yyhb__fxvjv, dty__tfsf)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            nauvg__jmtfg = datetime.timedelta(rhs.toordinal(), hours=rhs.
                hour, minutes=rhs.minute, seconds=rhs.second, microseconds=
                rhs.microsecond)
            nauvg__jmtfg = nauvg__jmtfg + lhs
            pxcri__kdg, ivvrm__xkla = divmod(nauvg__jmtfg.seconds, 3600)
            tlzt__fdc, cubr__vubn = divmod(ivvrm__xkla, 60)
            if 0 < nauvg__jmtfg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    nauvg__jmtfg.days)
                return datetime.datetime(d.year, d.month, d.day, pxcri__kdg,
                    tlzt__fdc, cubr__vubn, nauvg__jmtfg.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            nauvg__jmtfg = datetime.timedelta(lhs.toordinal(), hours=lhs.
                hour, minutes=lhs.minute, seconds=lhs.second, microseconds=
                lhs.microsecond)
            nauvg__jmtfg = nauvg__jmtfg + rhs
            pxcri__kdg, ivvrm__xkla = divmod(nauvg__jmtfg.seconds, 3600)
            tlzt__fdc, cubr__vubn = divmod(ivvrm__xkla, 60)
            if 0 < nauvg__jmtfg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    nauvg__jmtfg.days)
                return datetime.datetime(d.year, d.month, d.day, pxcri__kdg,
                    tlzt__fdc, cubr__vubn, nauvg__jmtfg.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            xkaq__fgis = lhs.value - rhs.value
            return pd.Timedelta(xkaq__fgis)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            qfv__fkqx = lhs
            numba.parfors.parfor.init_prange()
            n = len(qfv__fkqx)
            A = alloc_datetime_timedelta_array(n)
            for gack__xwre in numba.parfors.parfor.internal_prange(n):
                A[gack__xwre] = qfv__fkqx[gack__xwre] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            emcxb__afzrm = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, emcxb__afzrm)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            kfky__kir, emcxb__afzrm = divmod(lhs.value, rhs.value)
            return kfky__kir, pd.Timedelta(emcxb__afzrm)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opb__vid = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, opb__vid)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    msgv__fyplp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    oeo__xeh = c.pyapi.long_from_longlong(msgv__fyplp.days)
    gkb__spfvo = c.pyapi.long_from_longlong(msgv__fyplp.seconds)
    svsc__dwyg = c.pyapi.long_from_longlong(msgv__fyplp.microseconds)
    wgkn__moc = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(wgkn__moc, (oeo__xeh, gkb__spfvo,
        svsc__dwyg))
    c.pyapi.decref(oeo__xeh)
    c.pyapi.decref(gkb__spfvo)
    c.pyapi.decref(svsc__dwyg)
    c.pyapi.decref(wgkn__moc)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    oeo__xeh = c.pyapi.object_getattr_string(val, 'days')
    gkb__spfvo = c.pyapi.object_getattr_string(val, 'seconds')
    svsc__dwyg = c.pyapi.object_getattr_string(val, 'microseconds')
    katbb__nam = c.pyapi.long_as_longlong(oeo__xeh)
    hwptt__vtp = c.pyapi.long_as_longlong(gkb__spfvo)
    rmi__tzj = c.pyapi.long_as_longlong(svsc__dwyg)
    msgv__fyplp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    msgv__fyplp.days = katbb__nam
    msgv__fyplp.seconds = hwptt__vtp
    msgv__fyplp.microseconds = rmi__tzj
    c.pyapi.decref(oeo__xeh)
    c.pyapi.decref(gkb__spfvo)
    c.pyapi.decref(svsc__dwyg)
    rptwz__dpngx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(msgv__fyplp._getvalue(), is_error=rptwz__dpngx)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    kfky__kir, emcxb__afzrm = divmod(a, b)
    emcxb__afzrm *= 2
    gep__fyir = emcxb__afzrm > b if b > 0 else emcxb__afzrm < b
    if gep__fyir or emcxb__afzrm == b and kfky__kir % 2 == 1:
        kfky__kir += 1
    return kfky__kir


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                mndq__nctu = _cmp(_getstate(lhs), _getstate(rhs))
                return op(mndq__nctu, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            kfky__kir, emcxb__afzrm = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return kfky__kir, datetime.timedelta(0, 0, emcxb__afzrm)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    ujcn__bksm = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != ujcn__bksm
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        opb__vid = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, opb__vid)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    nzn__varjn = types.Array(types.intp, 1, 'C')
    kxb__texez = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nzn__varjn, [n])
    xdzy__zwd = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nzn__varjn, [n])
    dbrl__phsf = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        nzn__varjn, [n])
    ognb__dwmoh = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    kvp__mmh = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types.
        Array(types.uint8, 1, 'C'), [ognb__dwmoh])
    pkivu__kfnnq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    ojsy__csr = cgutils.get_or_insert_function(c.builder.module,
        pkivu__kfnnq, name='unbox_datetime_timedelta_array')
    c.builder.call(ojsy__csr, [val, n, kxb__texez.data, xdzy__zwd.data,
        dbrl__phsf.data, kvp__mmh.data])
    dvuz__donra = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    dvuz__donra.days_data = kxb__texez._getvalue()
    dvuz__donra.seconds_data = xdzy__zwd._getvalue()
    dvuz__donra.microseconds_data = dbrl__phsf._getvalue()
    dvuz__donra.null_bitmap = kvp__mmh._getvalue()
    rptwz__dpngx = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(dvuz__donra._getvalue(), is_error=rptwz__dpngx)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    qfv__fkqx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    kxb__texez = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qfv__fkqx.days_data)
    xdzy__zwd = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qfv__fkqx.seconds_data).data
    dbrl__phsf = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qfv__fkqx.microseconds_data).data
    qsge__gogze = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, qfv__fkqx.null_bitmap).data
    n = c.builder.extract_value(kxb__texez.shape, 0)
    pkivu__kfnnq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    taev__icx = cgutils.get_or_insert_function(c.builder.module,
        pkivu__kfnnq, name='box_datetime_timedelta_array')
    cse__ccuh = c.builder.call(taev__icx, [n, kxb__texez.data, xdzy__zwd,
        dbrl__phsf, qsge__gogze])
    c.context.nrt.decref(c.builder, typ, val)
    return cse__ccuh


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        xvkb__psx, uxu__hblqx, jzf__lwkaw, pwx__tsonk = args
        iicu__kwll = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        iicu__kwll.days_data = xvkb__psx
        iicu__kwll.seconds_data = uxu__hblqx
        iicu__kwll.microseconds_data = jzf__lwkaw
        iicu__kwll.null_bitmap = pwx__tsonk
        context.nrt.incref(builder, signature.args[0], xvkb__psx)
        context.nrt.incref(builder, signature.args[1], uxu__hblqx)
        context.nrt.incref(builder, signature.args[2], jzf__lwkaw)
        context.nrt.incref(builder, signature.args[3], pwx__tsonk)
        return iicu__kwll._getvalue()
    vsugg__lvz = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return vsugg__lvz, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    kxb__texez = np.empty(n, np.int64)
    xdzy__zwd = np.empty(n, np.int64)
    dbrl__phsf = np.empty(n, np.int64)
    oqj__fsbds = np.empty(n + 7 >> 3, np.uint8)
    for gack__xwre, s in enumerate(pyval):
        zvsyv__hov = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(oqj__fsbds, gack__xwre, int(
            not zvsyv__hov))
        if not zvsyv__hov:
            kxb__texez[gack__xwre] = s.days
            xdzy__zwd[gack__xwre] = s.seconds
            dbrl__phsf[gack__xwre] = s.microseconds
    bzecq__xvktf = context.get_constant_generic(builder, days_data_type,
        kxb__texez)
    aiqx__kvh = context.get_constant_generic(builder, seconds_data_type,
        xdzy__zwd)
    qpydk__rhsi = context.get_constant_generic(builder,
        microseconds_data_type, dbrl__phsf)
    koozm__fgk = context.get_constant_generic(builder, nulls_type, oqj__fsbds)
    return lir.Constant.literal_struct([bzecq__xvktf, aiqx__kvh,
        qpydk__rhsi, koozm__fgk])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    kxb__texez = np.empty(n, dtype=np.int64)
    xdzy__zwd = np.empty(n, dtype=np.int64)
    dbrl__phsf = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(kxb__texez, xdzy__zwd, dbrl__phsf,
        nulls)


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            jkiit__sto = bodo.utils.conversion.coerce_to_ndarray(ind)
            fbyjo__lihpx = A._null_bitmap
            roku__xose = A._days_data[jkiit__sto]
            geki__gbfq = A._seconds_data[jkiit__sto]
            cizes__pjia = A._microseconds_data[jkiit__sto]
            n = len(roku__xose)
            kmxv__wgvoa = get_new_null_mask_bool_index(fbyjo__lihpx, ind, n)
            return init_datetime_timedelta_array(roku__xose, geki__gbfq,
                cizes__pjia, kmxv__wgvoa)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            jkiit__sto = bodo.utils.conversion.coerce_to_ndarray(ind)
            fbyjo__lihpx = A._null_bitmap
            roku__xose = A._days_data[jkiit__sto]
            geki__gbfq = A._seconds_data[jkiit__sto]
            cizes__pjia = A._microseconds_data[jkiit__sto]
            n = len(roku__xose)
            kmxv__wgvoa = get_new_null_mask_int_index(fbyjo__lihpx,
                jkiit__sto, n)
            return init_datetime_timedelta_array(roku__xose, geki__gbfq,
                cizes__pjia, kmxv__wgvoa)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            fbyjo__lihpx = A._null_bitmap
            roku__xose = np.ascontiguousarray(A._days_data[ind])
            geki__gbfq = np.ascontiguousarray(A._seconds_data[ind])
            cizes__pjia = np.ascontiguousarray(A._microseconds_data[ind])
            kmxv__wgvoa = get_new_null_mask_slice_index(fbyjo__lihpx, ind, n)
            return init_datetime_timedelta_array(roku__xose, geki__gbfq,
                cizes__pjia, kmxv__wgvoa)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    fkd__lmfk = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(fkd__lmfk)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(fkd__lmfk)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for gack__xwre in range(n):
                    A._days_data[ind[gack__xwre]] = val._days
                    A._seconds_data[ind[gack__xwre]] = val._seconds
                    A._microseconds_data[ind[gack__xwre]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[gack__xwre], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for gack__xwre in range(n):
                    A._days_data[ind[gack__xwre]] = val._days_data[gack__xwre]
                    A._seconds_data[ind[gack__xwre]] = val._seconds_data[
                        gack__xwre]
                    A._microseconds_data[ind[gack__xwre]
                        ] = val._microseconds_data[gack__xwre]
                    hpjj__cyp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, gack__xwre)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[gack__xwre], hpjj__cyp)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for gack__xwre in range(n):
                    if not bodo.libs.array_kernels.isna(ind, gack__xwre
                        ) and ind[gack__xwre]:
                        A._days_data[gack__xwre] = val._days
                        A._seconds_data[gack__xwre] = val._seconds
                        A._microseconds_data[gack__xwre] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            gack__xwre, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                cnd__vrhd = 0
                for gack__xwre in range(n):
                    if not bodo.libs.array_kernels.isna(ind, gack__xwre
                        ) and ind[gack__xwre]:
                        A._days_data[gack__xwre] = val._days_data[cnd__vrhd]
                        A._seconds_data[gack__xwre] = val._seconds_data[
                            cnd__vrhd]
                        A._microseconds_data[gack__xwre
                            ] = val._microseconds_data[cnd__vrhd]
                        hpjj__cyp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, cnd__vrhd)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            gack__xwre, hpjj__cyp)
                        cnd__vrhd += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                ulmre__lhy = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for gack__xwre in range(ulmre__lhy.start, ulmre__lhy.stop,
                    ulmre__lhy.step):
                    A._days_data[gack__xwre] = val._days
                    A._seconds_data[gack__xwre] = val._seconds
                    A._microseconds_data[gack__xwre] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        gack__xwre, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                dkvv__hamc = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, dkvv__hamc,
                    ind, n)
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            qfv__fkqx = arg1
            numba.parfors.parfor.init_prange()
            n = len(qfv__fkqx)
            A = alloc_datetime_timedelta_array(n)
            for gack__xwre in numba.parfors.parfor.internal_prange(n):
                A[gack__xwre] = qfv__fkqx[gack__xwre] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            vplxf__ggiv = True
        else:
            vplxf__ggiv = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                stbc__uis = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for gack__xwre in numba.parfors.parfor.internal_prange(n):
                    iexg__msf = bodo.libs.array_kernels.isna(lhs, gack__xwre)
                    mfz__lrs = bodo.libs.array_kernels.isna(rhs, gack__xwre)
                    if iexg__msf or mfz__lrs:
                        bjf__qua = vplxf__ggiv
                    else:
                        bjf__qua = op(lhs[gack__xwre], rhs[gack__xwre])
                    stbc__uis[gack__xwre] = bjf__qua
                return stbc__uis
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                stbc__uis = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for gack__xwre in numba.parfors.parfor.internal_prange(n):
                    hpjj__cyp = bodo.libs.array_kernels.isna(lhs, gack__xwre)
                    if hpjj__cyp:
                        bjf__qua = vplxf__ggiv
                    else:
                        bjf__qua = op(lhs[gack__xwre], rhs)
                    stbc__uis[gack__xwre] = bjf__qua
                return stbc__uis
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                stbc__uis = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for gack__xwre in numba.parfors.parfor.internal_prange(n):
                    hpjj__cyp = bodo.libs.array_kernels.isna(rhs, gack__xwre)
                    if hpjj__cyp:
                        bjf__qua = vplxf__ggiv
                    else:
                        bjf__qua = op(lhs, rhs[gack__xwre])
                    stbc__uis[gack__xwre] = bjf__qua
                return stbc__uis
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for jeok__taogq in timedelta_unsupported_attrs:
        uoqp__kcw = 'pandas.Timedelta.' + jeok__taogq
        overload_attribute(PDTimeDeltaType, jeok__taogq)(
            create_unsupported_overload(uoqp__kcw))
    for tezy__xgf in timedelta_unsupported_methods:
        uoqp__kcw = 'pandas.Timedelta.' + tezy__xgf
        overload_method(PDTimeDeltaType, tezy__xgf)(create_unsupported_overload
            (uoqp__kcw + '()'))


_intstall_pd_timedelta_unsupported()
