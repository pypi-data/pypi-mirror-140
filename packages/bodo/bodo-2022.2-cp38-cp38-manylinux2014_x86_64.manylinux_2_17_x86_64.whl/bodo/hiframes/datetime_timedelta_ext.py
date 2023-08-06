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
        bilon__ilpi = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, bilon__ilpi)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    upt__jlqok = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    jnfax__lzrjw = c.pyapi.long_from_longlong(upt__jlqok.value)
    fim__aas = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(fim__aas, (jnfax__lzrjw,))
    c.pyapi.decref(jnfax__lzrjw)
    c.pyapi.decref(fim__aas)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    jnfax__lzrjw = c.pyapi.object_getattr_string(val, 'value')
    xntxu__hczz = c.pyapi.long_as_longlong(jnfax__lzrjw)
    upt__jlqok = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    upt__jlqok.value = xntxu__hczz
    c.pyapi.decref(jnfax__lzrjw)
    upjqa__dysfp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(upt__jlqok._getvalue(), is_error=upjqa__dysfp)


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
            uvzg__xcrd = 1000 * microseconds
            return init_pd_timedelta(uvzg__xcrd)
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
            uvzg__xcrd = 1000 * microseconds
            return init_pd_timedelta(uvzg__xcrd)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    ceygt__ulr, qqge__okehu = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * ceygt__ulr)
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
            qlyvp__qad = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + qlyvp__qad
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            azkgs__xsqxo = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = azkgs__xsqxo + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            icw__uobf = rhs.toordinal()
            dolh__duft = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            yplle__tsu = rhs.microsecond
            zql__odofl = lhs.value // 1000
            lyhct__nhd = lhs.nanoseconds
            jqx__qjzw = yplle__tsu + zql__odofl
            zvcdw__htvoh = 1000000 * (icw__uobf * 86400 + dolh__duft
                ) + jqx__qjzw
            jjlq__hwel = lyhct__nhd
            return compute_pd_timestamp(zvcdw__htvoh, jjlq__hwel)
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
            bgul__ledx = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            bgul__ledx = bgul__ledx + lhs
            xjm__ehsj, ycft__vor = divmod(bgul__ledx.seconds, 3600)
            fky__vxroe, tknn__pslg = divmod(ycft__vor, 60)
            if 0 < bgul__ledx.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(bgul__ledx
                    .days)
                return datetime.datetime(d.year, d.month, d.day, xjm__ehsj,
                    fky__vxroe, tknn__pslg, bgul__ledx.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            bgul__ledx = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            bgul__ledx = bgul__ledx + rhs
            xjm__ehsj, ycft__vor = divmod(bgul__ledx.seconds, 3600)
            fky__vxroe, tknn__pslg = divmod(ycft__vor, 60)
            if 0 < bgul__ledx.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(bgul__ledx
                    .days)
                return datetime.datetime(d.year, d.month, d.day, xjm__ehsj,
                    fky__vxroe, tknn__pslg, bgul__ledx.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            tme__ebuc = lhs.value - rhs.value
            return pd.Timedelta(tme__ebuc)
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
            tflfa__hqba = lhs
            numba.parfors.parfor.init_prange()
            n = len(tflfa__hqba)
            A = alloc_datetime_timedelta_array(n)
            for saql__xjly in numba.parfors.parfor.internal_prange(n):
                A[saql__xjly] = tflfa__hqba[saql__xjly] - rhs
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
            uhbv__sau = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, uhbv__sau)
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
            fdd__jprzo, uhbv__sau = divmod(lhs.value, rhs.value)
            return fdd__jprzo, pd.Timedelta(uhbv__sau)
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
        bilon__ilpi = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, bilon__ilpi)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    upt__jlqok = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    sscl__nwcc = c.pyapi.long_from_longlong(upt__jlqok.days)
    our__zqb = c.pyapi.long_from_longlong(upt__jlqok.seconds)
    lpd__fcvl = c.pyapi.long_from_longlong(upt__jlqok.microseconds)
    fim__aas = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.timedelta)
        )
    res = c.pyapi.call_function_objargs(fim__aas, (sscl__nwcc, our__zqb,
        lpd__fcvl))
    c.pyapi.decref(sscl__nwcc)
    c.pyapi.decref(our__zqb)
    c.pyapi.decref(lpd__fcvl)
    c.pyapi.decref(fim__aas)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    sscl__nwcc = c.pyapi.object_getattr_string(val, 'days')
    our__zqb = c.pyapi.object_getattr_string(val, 'seconds')
    lpd__fcvl = c.pyapi.object_getattr_string(val, 'microseconds')
    fwbx__jwjcc = c.pyapi.long_as_longlong(sscl__nwcc)
    gsrnt__ezozo = c.pyapi.long_as_longlong(our__zqb)
    swu__ugm = c.pyapi.long_as_longlong(lpd__fcvl)
    upt__jlqok = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    upt__jlqok.days = fwbx__jwjcc
    upt__jlqok.seconds = gsrnt__ezozo
    upt__jlqok.microseconds = swu__ugm
    c.pyapi.decref(sscl__nwcc)
    c.pyapi.decref(our__zqb)
    c.pyapi.decref(lpd__fcvl)
    upjqa__dysfp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(upt__jlqok._getvalue(), is_error=upjqa__dysfp)


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
    fdd__jprzo, uhbv__sau = divmod(a, b)
    uhbv__sau *= 2
    zdost__siovk = uhbv__sau > b if b > 0 else uhbv__sau < b
    if zdost__siovk or uhbv__sau == b and fdd__jprzo % 2 == 1:
        fdd__jprzo += 1
    return fdd__jprzo


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
                vqidg__fdx = _cmp(_getstate(lhs), _getstate(rhs))
                return op(vqidg__fdx, 0)
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
            fdd__jprzo, uhbv__sau = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return fdd__jprzo, datetime.timedelta(0, 0, uhbv__sau)
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
    qov__tdk = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != qov__tdk
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
        bilon__ilpi = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, bilon__ilpi)


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
    eyar__btpt = types.Array(types.intp, 1, 'C')
    bet__yxy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        eyar__btpt, [n])
    chfz__nuj = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        eyar__btpt, [n])
    dqu__phkv = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        eyar__btpt, [n])
    foxg__ndton = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ndxv__bkm = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [foxg__ndton])
    blrr__wen = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer()])
    fkk__tqgp = cgutils.get_or_insert_function(c.builder.module, blrr__wen,
        name='unbox_datetime_timedelta_array')
    c.builder.call(fkk__tqgp, [val, n, bet__yxy.data, chfz__nuj.data,
        dqu__phkv.data, ndxv__bkm.data])
    tgmx__xocj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tgmx__xocj.days_data = bet__yxy._getvalue()
    tgmx__xocj.seconds_data = chfz__nuj._getvalue()
    tgmx__xocj.microseconds_data = dqu__phkv._getvalue()
    tgmx__xocj.null_bitmap = ndxv__bkm._getvalue()
    upjqa__dysfp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tgmx__xocj._getvalue(), is_error=upjqa__dysfp)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    tflfa__hqba = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    bet__yxy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, tflfa__hqba.days_data)
    chfz__nuj = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, tflfa__hqba.seconds_data).data
    dqu__phkv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, tflfa__hqba.microseconds_data).data
    wbl__ylyuq = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, tflfa__hqba.null_bitmap).data
    n = c.builder.extract_value(bet__yxy.shape, 0)
    blrr__wen = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    kbbgo__lfz = cgutils.get_or_insert_function(c.builder.module, blrr__wen,
        name='box_datetime_timedelta_array')
    gmxzr__tteo = c.builder.call(kbbgo__lfz, [n, bet__yxy.data, chfz__nuj,
        dqu__phkv, wbl__ylyuq])
    c.context.nrt.decref(c.builder, typ, val)
    return gmxzr__tteo


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        jju__qplm, cbs__cmcij, iup__rlqxw, jcdlq__swzgs = args
        ntr__mmnl = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ntr__mmnl.days_data = jju__qplm
        ntr__mmnl.seconds_data = cbs__cmcij
        ntr__mmnl.microseconds_data = iup__rlqxw
        ntr__mmnl.null_bitmap = jcdlq__swzgs
        context.nrt.incref(builder, signature.args[0], jju__qplm)
        context.nrt.incref(builder, signature.args[1], cbs__cmcij)
        context.nrt.incref(builder, signature.args[2], iup__rlqxw)
        context.nrt.incref(builder, signature.args[3], jcdlq__swzgs)
        return ntr__mmnl._getvalue()
    ouexs__snx = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return ouexs__snx, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    bet__yxy = np.empty(n, np.int64)
    chfz__nuj = np.empty(n, np.int64)
    dqu__phkv = np.empty(n, np.int64)
    oeexg__dcutu = np.empty(n + 7 >> 3, np.uint8)
    for saql__xjly, s in enumerate(pyval):
        xcjff__dfm = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(oeexg__dcutu, saql__xjly, int(
            not xcjff__dfm))
        if not xcjff__dfm:
            bet__yxy[saql__xjly] = s.days
            chfz__nuj[saql__xjly] = s.seconds
            dqu__phkv[saql__xjly] = s.microseconds
    jxlry__spm = context.get_constant_generic(builder, days_data_type, bet__yxy
        )
    zrye__scd = context.get_constant_generic(builder, seconds_data_type,
        chfz__nuj)
    osn__lqn = context.get_constant_generic(builder, microseconds_data_type,
        dqu__phkv)
    cykz__vmx = context.get_constant_generic(builder, nulls_type, oeexg__dcutu)
    return lir.Constant.literal_struct([jxlry__spm, zrye__scd, osn__lqn,
        cykz__vmx])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    bet__yxy = np.empty(n, dtype=np.int64)
    chfz__nuj = np.empty(n, dtype=np.int64)
    dqu__phkv = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(bet__yxy, chfz__nuj, dqu__phkv, nulls)


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
            jgke__dvi = bodo.utils.conversion.coerce_to_ndarray(ind)
            iby__tad = A._null_bitmap
            jin__ewluk = A._days_data[jgke__dvi]
            krbg__uxdop = A._seconds_data[jgke__dvi]
            smlfr__adeus = A._microseconds_data[jgke__dvi]
            n = len(jin__ewluk)
            fdm__pit = get_new_null_mask_bool_index(iby__tad, ind, n)
            return init_datetime_timedelta_array(jin__ewluk, krbg__uxdop,
                smlfr__adeus, fdm__pit)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            jgke__dvi = bodo.utils.conversion.coerce_to_ndarray(ind)
            iby__tad = A._null_bitmap
            jin__ewluk = A._days_data[jgke__dvi]
            krbg__uxdop = A._seconds_data[jgke__dvi]
            smlfr__adeus = A._microseconds_data[jgke__dvi]
            n = len(jin__ewluk)
            fdm__pit = get_new_null_mask_int_index(iby__tad, jgke__dvi, n)
            return init_datetime_timedelta_array(jin__ewluk, krbg__uxdop,
                smlfr__adeus, fdm__pit)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            iby__tad = A._null_bitmap
            jin__ewluk = np.ascontiguousarray(A._days_data[ind])
            krbg__uxdop = np.ascontiguousarray(A._seconds_data[ind])
            smlfr__adeus = np.ascontiguousarray(A._microseconds_data[ind])
            fdm__pit = get_new_null_mask_slice_index(iby__tad, ind, n)
            return init_datetime_timedelta_array(jin__ewluk, krbg__uxdop,
                smlfr__adeus, fdm__pit)
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
    ckhsd__fciba = (
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
            raise BodoError(ckhsd__fciba)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(ckhsd__fciba)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for saql__xjly in range(n):
                    A._days_data[ind[saql__xjly]] = val._days
                    A._seconds_data[ind[saql__xjly]] = val._seconds
                    A._microseconds_data[ind[saql__xjly]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[saql__xjly], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for saql__xjly in range(n):
                    A._days_data[ind[saql__xjly]] = val._days_data[saql__xjly]
                    A._seconds_data[ind[saql__xjly]] = val._seconds_data[
                        saql__xjly]
                    A._microseconds_data[ind[saql__xjly]
                        ] = val._microseconds_data[saql__xjly]
                    vtw__ftl = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, saql__xjly)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[saql__xjly], vtw__ftl)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for saql__xjly in range(n):
                    if not bodo.libs.array_kernels.isna(ind, saql__xjly
                        ) and ind[saql__xjly]:
                        A._days_data[saql__xjly] = val._days
                        A._seconds_data[saql__xjly] = val._seconds
                        A._microseconds_data[saql__xjly] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            saql__xjly, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                bqv__vipwo = 0
                for saql__xjly in range(n):
                    if not bodo.libs.array_kernels.isna(ind, saql__xjly
                        ) and ind[saql__xjly]:
                        A._days_data[saql__xjly] = val._days_data[bqv__vipwo]
                        A._seconds_data[saql__xjly] = val._seconds_data[
                            bqv__vipwo]
                        A._microseconds_data[saql__xjly
                            ] = val._microseconds_data[bqv__vipwo]
                        vtw__ftl = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                            ._null_bitmap, bqv__vipwo)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            saql__xjly, vtw__ftl)
                        bqv__vipwo += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                ijipm__mln = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for saql__xjly in range(ijipm__mln.start, ijipm__mln.stop,
                    ijipm__mln.step):
                    A._days_data[saql__xjly] = val._days
                    A._seconds_data[saql__xjly] = val._seconds
                    A._microseconds_data[saql__xjly] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        saql__xjly, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                hru__czdhz = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, hru__czdhz,
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
            tflfa__hqba = arg1
            numba.parfors.parfor.init_prange()
            n = len(tflfa__hqba)
            A = alloc_datetime_timedelta_array(n)
            for saql__xjly in numba.parfors.parfor.internal_prange(n):
                A[saql__xjly] = tflfa__hqba[saql__xjly] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            jhp__clsok = True
        else:
            jhp__clsok = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                wkjuj__kvmg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for saql__xjly in numba.parfors.parfor.internal_prange(n):
                    isiz__yqa = bodo.libs.array_kernels.isna(lhs, saql__xjly)
                    nincl__osg = bodo.libs.array_kernels.isna(rhs, saql__xjly)
                    if isiz__yqa or nincl__osg:
                        tikxw__erqwh = jhp__clsok
                    else:
                        tikxw__erqwh = op(lhs[saql__xjly], rhs[saql__xjly])
                    wkjuj__kvmg[saql__xjly] = tikxw__erqwh
                return wkjuj__kvmg
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                wkjuj__kvmg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for saql__xjly in numba.parfors.parfor.internal_prange(n):
                    vtw__ftl = bodo.libs.array_kernels.isna(lhs, saql__xjly)
                    if vtw__ftl:
                        tikxw__erqwh = jhp__clsok
                    else:
                        tikxw__erqwh = op(lhs[saql__xjly], rhs)
                    wkjuj__kvmg[saql__xjly] = tikxw__erqwh
                return wkjuj__kvmg
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                wkjuj__kvmg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for saql__xjly in numba.parfors.parfor.internal_prange(n):
                    vtw__ftl = bodo.libs.array_kernels.isna(rhs, saql__xjly)
                    if vtw__ftl:
                        tikxw__erqwh = jhp__clsok
                    else:
                        tikxw__erqwh = op(lhs, rhs[saql__xjly])
                    wkjuj__kvmg[saql__xjly] = tikxw__erqwh
                return wkjuj__kvmg
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for nww__eplr in timedelta_unsupported_attrs:
        ktqbc__caen = 'pandas.Timedelta.' + nww__eplr
        overload_attribute(PDTimeDeltaType, nww__eplr)(
            create_unsupported_overload(ktqbc__caen))
    for jlgg__ujgq in timedelta_unsupported_methods:
        ktqbc__caen = 'pandas.Timedelta.' + jlgg__ujgq
        overload_method(PDTimeDeltaType, jlgg__ujgq)(
            create_unsupported_overload(ktqbc__caen + '()'))


_intstall_pd_timedelta_unsupported()
