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
        gew__dky = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, gew__dky)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    xlzrk__emrz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    chl__ukjyn = c.pyapi.long_from_longlong(xlzrk__emrz.value)
    irrt__lxv = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(irrt__lxv, (chl__ukjyn,))
    c.pyapi.decref(chl__ukjyn)
    c.pyapi.decref(irrt__lxv)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    chl__ukjyn = c.pyapi.object_getattr_string(val, 'value')
    qkwva__xaztc = c.pyapi.long_as_longlong(chl__ukjyn)
    xlzrk__emrz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xlzrk__emrz.value = qkwva__xaztc
    c.pyapi.decref(chl__ukjyn)
    znqp__ndm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xlzrk__emrz._getvalue(), is_error=znqp__ndm)


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
            ehkx__qqtjz = 1000 * microseconds
            return init_pd_timedelta(ehkx__qqtjz)
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
            ehkx__qqtjz = 1000 * microseconds
            return init_pd_timedelta(ehkx__qqtjz)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    qjd__snyo, uwh__pjvc = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * qjd__snyo)
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
            kockd__vnbwj = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + kockd__vnbwj
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            vylmm__dfsp = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = vylmm__dfsp + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            dbrt__jhmkj = rhs.toordinal()
            mqgxq__vbuqt = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            yjark__bvhad = rhs.microsecond
            gei__sgzx = lhs.value // 1000
            rnhi__dkcjl = lhs.nanoseconds
            yar__zyu = yjark__bvhad + gei__sgzx
            gews__igsh = 1000000 * (dbrt__jhmkj * 86400 + mqgxq__vbuqt
                ) + yar__zyu
            mxij__lcic = rnhi__dkcjl
            return compute_pd_timestamp(gews__igsh, mxij__lcic)
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
            mld__rntg = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            mld__rntg = mld__rntg + lhs
            pyidn__fyzc, kfoa__myt = divmod(mld__rntg.seconds, 3600)
            abdw__zsdc, tpxwz__rwpod = divmod(kfoa__myt, 60)
            if 0 < mld__rntg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(mld__rntg
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    pyidn__fyzc, abdw__zsdc, tpxwz__rwpod, mld__rntg.
                    microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            mld__rntg = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            mld__rntg = mld__rntg + rhs
            pyidn__fyzc, kfoa__myt = divmod(mld__rntg.seconds, 3600)
            abdw__zsdc, tpxwz__rwpod = divmod(kfoa__myt, 60)
            if 0 < mld__rntg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(mld__rntg
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    pyidn__fyzc, abdw__zsdc, tpxwz__rwpod, mld__rntg.
                    microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            hhp__qjhwq = lhs.value - rhs.value
            return pd.Timedelta(hhp__qjhwq)
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
            xbpj__toc = lhs
            numba.parfors.parfor.init_prange()
            n = len(xbpj__toc)
            A = alloc_datetime_timedelta_array(n)
            for abypa__ymf in numba.parfors.parfor.internal_prange(n):
                A[abypa__ymf] = xbpj__toc[abypa__ymf] - rhs
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
            gmal__ibvbn = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, gmal__ibvbn)
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
            ooipt__hyiu, gmal__ibvbn = divmod(lhs.value, rhs.value)
            return ooipt__hyiu, pd.Timedelta(gmal__ibvbn)
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
        gew__dky = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, gew__dky)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    xlzrk__emrz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bssk__clh = c.pyapi.long_from_longlong(xlzrk__emrz.days)
    eyy__awh = c.pyapi.long_from_longlong(xlzrk__emrz.seconds)
    obg__spv = c.pyapi.long_from_longlong(xlzrk__emrz.microseconds)
    irrt__lxv = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(irrt__lxv, (bssk__clh, eyy__awh,
        obg__spv))
    c.pyapi.decref(bssk__clh)
    c.pyapi.decref(eyy__awh)
    c.pyapi.decref(obg__spv)
    c.pyapi.decref(irrt__lxv)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    bssk__clh = c.pyapi.object_getattr_string(val, 'days')
    eyy__awh = c.pyapi.object_getattr_string(val, 'seconds')
    obg__spv = c.pyapi.object_getattr_string(val, 'microseconds')
    gzo__liagi = c.pyapi.long_as_longlong(bssk__clh)
    xkcqx__swc = c.pyapi.long_as_longlong(eyy__awh)
    cni__qowk = c.pyapi.long_as_longlong(obg__spv)
    xlzrk__emrz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xlzrk__emrz.days = gzo__liagi
    xlzrk__emrz.seconds = xkcqx__swc
    xlzrk__emrz.microseconds = cni__qowk
    c.pyapi.decref(bssk__clh)
    c.pyapi.decref(eyy__awh)
    c.pyapi.decref(obg__spv)
    znqp__ndm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xlzrk__emrz._getvalue(), is_error=znqp__ndm)


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
    ooipt__hyiu, gmal__ibvbn = divmod(a, b)
    gmal__ibvbn *= 2
    qvsma__atzlm = gmal__ibvbn > b if b > 0 else gmal__ibvbn < b
    if qvsma__atzlm or gmal__ibvbn == b and ooipt__hyiu % 2 == 1:
        ooipt__hyiu += 1
    return ooipt__hyiu


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
                orpb__yetmn = _cmp(_getstate(lhs), _getstate(rhs))
                return op(orpb__yetmn, 0)
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
            ooipt__hyiu, gmal__ibvbn = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return ooipt__hyiu, datetime.timedelta(0, 0, gmal__ibvbn)
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
    zgqqb__yjxs = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != zgqqb__yjxs
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
        gew__dky = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, gew__dky)


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
    ygqjn__hdf = types.Array(types.intp, 1, 'C')
    wocs__xzbmu = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        ygqjn__hdf, [n])
    aek__wam = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        ygqjn__hdf, [n])
    qcs__xlte = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        ygqjn__hdf, [n])
    yqw__fytim = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    nuht__mnjs = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [yqw__fytim])
    fcd__nnibc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    rml__bspo = cgutils.get_or_insert_function(c.builder.module, fcd__nnibc,
        name='unbox_datetime_timedelta_array')
    c.builder.call(rml__bspo, [val, n, wocs__xzbmu.data, aek__wam.data,
        qcs__xlte.data, nuht__mnjs.data])
    mdfp__hytm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mdfp__hytm.days_data = wocs__xzbmu._getvalue()
    mdfp__hytm.seconds_data = aek__wam._getvalue()
    mdfp__hytm.microseconds_data = qcs__xlte._getvalue()
    mdfp__hytm.null_bitmap = nuht__mnjs._getvalue()
    znqp__ndm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mdfp__hytm._getvalue(), is_error=znqp__ndm)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    xbpj__toc = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    wocs__xzbmu = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xbpj__toc.days_data)
    aek__wam = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xbpj__toc.seconds_data).data
    qcs__xlte = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, xbpj__toc.microseconds_data).data
    jlroo__inytn = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, xbpj__toc.null_bitmap).data
    n = c.builder.extract_value(wocs__xzbmu.shape, 0)
    fcd__nnibc = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    ycp__kmkn = cgutils.get_or_insert_function(c.builder.module, fcd__nnibc,
        name='box_datetime_timedelta_array')
    cokx__zzrdv = c.builder.call(ycp__kmkn, [n, wocs__xzbmu.data, aek__wam,
        qcs__xlte, jlroo__inytn])
    c.context.nrt.decref(c.builder, typ, val)
    return cokx__zzrdv


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        xkrdj__bbv, pmc__xysd, tpq__hteb, pwqab__vbegv = args
        dxl__rrk = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        dxl__rrk.days_data = xkrdj__bbv
        dxl__rrk.seconds_data = pmc__xysd
        dxl__rrk.microseconds_data = tpq__hteb
        dxl__rrk.null_bitmap = pwqab__vbegv
        context.nrt.incref(builder, signature.args[0], xkrdj__bbv)
        context.nrt.incref(builder, signature.args[1], pmc__xysd)
        context.nrt.incref(builder, signature.args[2], tpq__hteb)
        context.nrt.incref(builder, signature.args[3], pwqab__vbegv)
        return dxl__rrk._getvalue()
    wolvk__oeupj = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return wolvk__oeupj, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    wocs__xzbmu = np.empty(n, np.int64)
    aek__wam = np.empty(n, np.int64)
    qcs__xlte = np.empty(n, np.int64)
    rjyg__gcz = np.empty(n + 7 >> 3, np.uint8)
    for abypa__ymf, s in enumerate(pyval):
        gdy__nfn = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(rjyg__gcz, abypa__ymf, int(not
            gdy__nfn))
        if not gdy__nfn:
            wocs__xzbmu[abypa__ymf] = s.days
            aek__wam[abypa__ymf] = s.seconds
            qcs__xlte[abypa__ymf] = s.microseconds
    lakjc__hms = context.get_constant_generic(builder, days_data_type,
        wocs__xzbmu)
    zsazn__vdv = context.get_constant_generic(builder, seconds_data_type,
        aek__wam)
    mmm__idwq = context.get_constant_generic(builder,
        microseconds_data_type, qcs__xlte)
    zlvx__fuo = context.get_constant_generic(builder, nulls_type, rjyg__gcz)
    return lir.Constant.literal_struct([lakjc__hms, zsazn__vdv, mmm__idwq,
        zlvx__fuo])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    wocs__xzbmu = np.empty(n, dtype=np.int64)
    aek__wam = np.empty(n, dtype=np.int64)
    qcs__xlte = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(wocs__xzbmu, aek__wam, qcs__xlte,
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
            uwi__bxjae = bodo.utils.conversion.coerce_to_ndarray(ind)
            xkkxe__jqbw = A._null_bitmap
            qmaie__rbo = A._days_data[uwi__bxjae]
            kakz__mdnl = A._seconds_data[uwi__bxjae]
            dfczc__veym = A._microseconds_data[uwi__bxjae]
            n = len(qmaie__rbo)
            iqlci__vrs = get_new_null_mask_bool_index(xkkxe__jqbw, ind, n)
            return init_datetime_timedelta_array(qmaie__rbo, kakz__mdnl,
                dfczc__veym, iqlci__vrs)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            uwi__bxjae = bodo.utils.conversion.coerce_to_ndarray(ind)
            xkkxe__jqbw = A._null_bitmap
            qmaie__rbo = A._days_data[uwi__bxjae]
            kakz__mdnl = A._seconds_data[uwi__bxjae]
            dfczc__veym = A._microseconds_data[uwi__bxjae]
            n = len(qmaie__rbo)
            iqlci__vrs = get_new_null_mask_int_index(xkkxe__jqbw, uwi__bxjae, n
                )
            return init_datetime_timedelta_array(qmaie__rbo, kakz__mdnl,
                dfczc__veym, iqlci__vrs)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            xkkxe__jqbw = A._null_bitmap
            qmaie__rbo = np.ascontiguousarray(A._days_data[ind])
            kakz__mdnl = np.ascontiguousarray(A._seconds_data[ind])
            dfczc__veym = np.ascontiguousarray(A._microseconds_data[ind])
            iqlci__vrs = get_new_null_mask_slice_index(xkkxe__jqbw, ind, n)
            return init_datetime_timedelta_array(qmaie__rbo, kakz__mdnl,
                dfczc__veym, iqlci__vrs)
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
    xfuag__faxsn = (
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
            raise BodoError(xfuag__faxsn)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(xfuag__faxsn)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for abypa__ymf in range(n):
                    A._days_data[ind[abypa__ymf]] = val._days
                    A._seconds_data[ind[abypa__ymf]] = val._seconds
                    A._microseconds_data[ind[abypa__ymf]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[abypa__ymf], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for abypa__ymf in range(n):
                    A._days_data[ind[abypa__ymf]] = val._days_data[abypa__ymf]
                    A._seconds_data[ind[abypa__ymf]] = val._seconds_data[
                        abypa__ymf]
                    A._microseconds_data[ind[abypa__ymf]
                        ] = val._microseconds_data[abypa__ymf]
                    szrj__wtn = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, abypa__ymf)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[abypa__ymf], szrj__wtn)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for abypa__ymf in range(n):
                    if not bodo.libs.array_kernels.isna(ind, abypa__ymf
                        ) and ind[abypa__ymf]:
                        A._days_data[abypa__ymf] = val._days
                        A._seconds_data[abypa__ymf] = val._seconds
                        A._microseconds_data[abypa__ymf] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            abypa__ymf, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                flxav__kwv = 0
                for abypa__ymf in range(n):
                    if not bodo.libs.array_kernels.isna(ind, abypa__ymf
                        ) and ind[abypa__ymf]:
                        A._days_data[abypa__ymf] = val._days_data[flxav__kwv]
                        A._seconds_data[abypa__ymf] = val._seconds_data[
                            flxav__kwv]
                        A._microseconds_data[abypa__ymf
                            ] = val._microseconds_data[flxav__kwv]
                        szrj__wtn = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, flxav__kwv)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            abypa__ymf, szrj__wtn)
                        flxav__kwv += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                obkm__qscib = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for abypa__ymf in range(obkm__qscib.start, obkm__qscib.stop,
                    obkm__qscib.step):
                    A._days_data[abypa__ymf] = val._days
                    A._seconds_data[abypa__ymf] = val._seconds
                    A._microseconds_data[abypa__ymf] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        abypa__ymf, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                nahxs__kqua = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, nahxs__kqua,
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
            xbpj__toc = arg1
            numba.parfors.parfor.init_prange()
            n = len(xbpj__toc)
            A = alloc_datetime_timedelta_array(n)
            for abypa__ymf in numba.parfors.parfor.internal_prange(n):
                A[abypa__ymf] = xbpj__toc[abypa__ymf] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            etg__pnvq = True
        else:
            etg__pnvq = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                xnbqb__unlkj = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for abypa__ymf in numba.parfors.parfor.internal_prange(n):
                    xua__qbft = bodo.libs.array_kernels.isna(lhs, abypa__ymf)
                    fjzi__mhzzi = bodo.libs.array_kernels.isna(rhs, abypa__ymf)
                    if xua__qbft or fjzi__mhzzi:
                        axyvj__onp = etg__pnvq
                    else:
                        axyvj__onp = op(lhs[abypa__ymf], rhs[abypa__ymf])
                    xnbqb__unlkj[abypa__ymf] = axyvj__onp
                return xnbqb__unlkj
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                xnbqb__unlkj = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for abypa__ymf in numba.parfors.parfor.internal_prange(n):
                    szrj__wtn = bodo.libs.array_kernels.isna(lhs, abypa__ymf)
                    if szrj__wtn:
                        axyvj__onp = etg__pnvq
                    else:
                        axyvj__onp = op(lhs[abypa__ymf], rhs)
                    xnbqb__unlkj[abypa__ymf] = axyvj__onp
                return xnbqb__unlkj
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                xnbqb__unlkj = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for abypa__ymf in numba.parfors.parfor.internal_prange(n):
                    szrj__wtn = bodo.libs.array_kernels.isna(rhs, abypa__ymf)
                    if szrj__wtn:
                        axyvj__onp = etg__pnvq
                    else:
                        axyvj__onp = op(lhs, rhs[abypa__ymf])
                    xnbqb__unlkj[abypa__ymf] = axyvj__onp
                return xnbqb__unlkj
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for yda__trtc in timedelta_unsupported_attrs:
        emdt__kpohe = 'pandas.Timedelta.' + yda__trtc
        overload_attribute(PDTimeDeltaType, yda__trtc)(
            create_unsupported_overload(emdt__kpohe))
    for msibg__pymnk in timedelta_unsupported_methods:
        emdt__kpohe = 'pandas.Timedelta.' + msibg__pymnk
        overload_method(PDTimeDeltaType, msibg__pymnk)(
            create_unsupported_overload(emdt__kpohe + '()'))


_intstall_pd_timedelta_unsupported()
