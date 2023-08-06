""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        rxtaf__usyr = lhs.data if isinstance(lhs, SeriesType) else lhs
        obnc__ttz = rhs.data if isinstance(rhs, SeriesType) else rhs
        if rxtaf__usyr in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and obnc__ttz.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            rxtaf__usyr = obnc__ttz.dtype
        elif obnc__ttz in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and rxtaf__usyr.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            obnc__ttz = rxtaf__usyr.dtype
        xwa__suy = rxtaf__usyr, obnc__ttz
        diz__kko = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            orn__fsqjf = self.context.resolve_function_type(self.key,
                xwa__suy, {}).return_type
        except Exception as nqx__fugsx:
            raise BodoError(diz__kko)
        if is_overload_bool(orn__fsqjf):
            raise BodoError(diz__kko)
        odtqz__qsm = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        fogfp__twiv = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        imig__jtfm = types.bool_
        kwpaw__inpm = SeriesType(imig__jtfm, orn__fsqjf, odtqz__qsm,
            fogfp__twiv)
        return kwpaw__inpm(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        pnbq__eqymk = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if pnbq__eqymk is None:
            pnbq__eqymk = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, pnbq__eqymk, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        rxtaf__usyr = lhs.data if isinstance(lhs, SeriesType) else lhs
        obnc__ttz = rhs.data if isinstance(rhs, SeriesType) else rhs
        xwa__suy = rxtaf__usyr, obnc__ttz
        diz__kko = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            orn__fsqjf = self.context.resolve_function_type(self.key,
                xwa__suy, {}).return_type
        except Exception as rhus__ezg:
            raise BodoError(diz__kko)
        odtqz__qsm = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        fogfp__twiv = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        imig__jtfm = orn__fsqjf.dtype
        kwpaw__inpm = SeriesType(imig__jtfm, orn__fsqjf, odtqz__qsm,
            fogfp__twiv)
        return kwpaw__inpm(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        pnbq__eqymk = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if pnbq__eqymk is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                pnbq__eqymk = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, pnbq__eqymk, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (lhs == string_array_type or types.
            unliteral(lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            pnbq__eqymk = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return pnbq__eqymk(lhs, rhs)
        if lhs == string_array_type or rhs == string_array_type:
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            pnbq__eqymk = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return pnbq__eqymk(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    iprcg__boh = lhs == datetime_timedelta_type and rhs == datetime_date_type
    ngnck__xhby = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return iprcg__boh or ngnck__xhby


def add_timestamp(lhs, rhs):
    rpt__ikyri = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    cipsd__teti = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return rpt__ikyri or cipsd__teti


def add_datetime_and_timedeltas(lhs, rhs):
    xovo__wonic = [datetime_timedelta_type, pd_timedelta_type]
    npn__gwaij = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    wduyp__lls = lhs in xovo__wonic and rhs in xovo__wonic
    ofsrv__xtenu = (lhs == datetime_datetime_type and rhs in xovo__wonic or
        rhs == datetime_datetime_type and lhs in xovo__wonic)
    return wduyp__lls or ofsrv__xtenu


def mul_string_arr_and_int(lhs, rhs):
    obnc__ttz = isinstance(lhs, types.Integer) and rhs == string_array_type
    rxtaf__usyr = lhs == string_array_type and isinstance(rhs, types.Integer)
    return obnc__ttz or rxtaf__usyr


def mul_timedelta_and_int(lhs, rhs):
    iprcg__boh = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    ngnck__xhby = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return iprcg__boh or ngnck__xhby


def mul_date_offset_and_int(lhs, rhs):
    gical__www = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    kkbeh__kxmg = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return gical__www or kkbeh__kxmg


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    wqxx__cwyo = [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ]
    tdve__yzip = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in tdve__yzip and lhs in wqxx__cwyo


def sub_dt_index_and_timestamp(lhs, rhs):
    bxgg__wqly = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    pbws__inygx = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return bxgg__wqly or pbws__inygx


def sub_dt_or_td(lhs, rhs):
    ocybb__ouk = lhs == datetime_date_type and rhs == datetime_timedelta_type
    ihbr__qopea = lhs == datetime_date_type and rhs == datetime_date_type
    ztpsd__nmsih = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return ocybb__ouk or ihbr__qopea or ztpsd__nmsih


def sub_datetime_and_timedeltas(lhs, rhs):
    vek__mlxas = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    lddgl__ukrl = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return vek__mlxas or lddgl__ukrl


def div_timedelta_and_int(lhs, rhs):
    wduyp__lls = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    rvd__tcgpv = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return wduyp__lls or rvd__tcgpv


def div_datetime_timedelta(lhs, rhs):
    wduyp__lls = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    rvd__tcgpv = lhs == datetime_timedelta_type and rhs == types.int64
    return wduyp__lls or rvd__tcgpv


def mod_timedeltas(lhs, rhs):
    zpa__vid = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    jlgxe__pkll = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return zpa__vid or jlgxe__pkll


def cmp_dt_index_to_string(lhs, rhs):
    bxgg__wqly = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    pbws__inygx = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return bxgg__wqly or pbws__inygx


def cmp_timestamp_or_date(lhs, rhs):
    fqlt__dhmmo = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    wfh__vauou = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    txfn__jlrr = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    eid__zguab = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    cxxy__cozwv = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return fqlt__dhmmo or wfh__vauou or txfn__jlrr or eid__zguab or cxxy__cozwv


def cmp_timeseries(lhs, rhs):
    ltg__cra = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    evqad__qtxr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    aoq__hfnoj = ltg__cra or evqad__qtxr
    mfylw__tpop = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    dus__twyy = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    tofax__szp = mfylw__tpop or dus__twyy
    return aoq__hfnoj or tofax__szp


def cmp_timedeltas(lhs, rhs):
    wduyp__lls = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in wduyp__lls and rhs in wduyp__lls


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    xdcm__eybsj = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return xdcm__eybsj


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    inz__szrcp = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    yhpqn__krksv = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    xvyh__ugllz = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    sqvi__wedk = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return inz__szrcp or yhpqn__krksv or xvyh__ugllz or sqvi__wedk


def args_td_and_int_array(lhs, rhs):
    lvnnt__zqvzk = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    cmx__qeq = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return lvnnt__zqvzk and cmx__qeq


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        ngnck__xhby = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        iprcg__boh = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        vsk__frs = ngnck__xhby or iprcg__boh
        qqo__fozj = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        wdrul__tizc = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        nyi__oah = qqo__fozj or wdrul__tizc
        jkcn__mqmok = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        fvvp__ljiu = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        nxl__xmg = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        egd__fks = jkcn__mqmok or fvvp__ljiu or nxl__xmg
        saf__vixu = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        ifxof__naoo = isinstance(lhs, tys) or isinstance(rhs, tys)
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (vsk__frs or nyi__oah or egd__fks or saf__vixu or
            ifxof__naoo or dcknb__nkfh)
    if op == operator.pow:
        nxc__hygka = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        vhaia__wjkr = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        nxl__xmg = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return nxc__hygka or vhaia__wjkr or nxl__xmg or dcknb__nkfh
    if op == operator.floordiv:
        fvvp__ljiu = lhs in types.real_domain and rhs in types.real_domain
        jkcn__mqmok = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        pmfak__yxz = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        wduyp__lls = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (fvvp__ljiu or jkcn__mqmok or pmfak__yxz or wduyp__lls or
            dcknb__nkfh)
    if op == operator.truediv:
        ijf__dhl = lhs in machine_ints and rhs in machine_ints
        fvvp__ljiu = lhs in types.real_domain and rhs in types.real_domain
        nxl__xmg = lhs in types.complex_domain and rhs in types.complex_domain
        jkcn__mqmok = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        pmfak__yxz = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        izpv__pxd = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wduyp__lls = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (ijf__dhl or fvvp__ljiu or nxl__xmg or jkcn__mqmok or
            pmfak__yxz or izpv__pxd or wduyp__lls or dcknb__nkfh)
    if op == operator.mod:
        ijf__dhl = lhs in machine_ints and rhs in machine_ints
        fvvp__ljiu = lhs in types.real_domain and rhs in types.real_domain
        jkcn__mqmok = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        pmfak__yxz = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (ijf__dhl or fvvp__ljiu or jkcn__mqmok or pmfak__yxz or
            dcknb__nkfh)
    if op == operator.add or op == operator.sub:
        vsk__frs = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        vold__aoq = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        fyo__jyg = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        fetyn__nry = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        jkcn__mqmok = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        fvvp__ljiu = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        nxl__xmg = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        egd__fks = jkcn__mqmok or fvvp__ljiu or nxl__xmg
        dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        msi__fiaxf = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        saf__vixu = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        kehmr__qhuy = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        lhj__onex = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        hmeog__mrxjv = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeCharSeq)
        gljn__syja = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        ndpx__lcw = kehmr__qhuy or lhj__onex or hmeog__mrxjv or gljn__syja
        nyi__oah = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        syh__vcc = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        qbqk__viuit = nyi__oah or syh__vcc
        scyoq__dxe = lhs == types.NPTimedelta and rhs == types.NPDatetime
        qsxfc__oamjy = (msi__fiaxf or saf__vixu or ndpx__lcw or qbqk__viuit or
            scyoq__dxe)
        izi__ftfn = op == operator.add and qsxfc__oamjy
        return (vsk__frs or vold__aoq or fyo__jyg or fetyn__nry or egd__fks or
            dcknb__nkfh or izi__ftfn)


def cmp_op_supported_by_numba(lhs, rhs):
    dcknb__nkfh = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    saf__vixu = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    vsk__frs = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, types
        .NPTimedelta)
    pge__cuudw = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    nyi__oah = isinstance(lhs, unicode_types) and isinstance(rhs, unicode_types
        )
    msi__fiaxf = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    fetyn__nry = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    egd__fks = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    kyx__litw = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    tpq__jsr = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    icw__vtwbz = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    xhefn__cuuh = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    zufq__musa = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (saf__vixu or vsk__frs or pge__cuudw or nyi__oah or msi__fiaxf or
        fetyn__nry or egd__fks or kyx__litw or tpq__jsr or icw__vtwbz or
        dcknb__nkfh or xhefn__cuuh or zufq__musa)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        iqy__yxtd = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(iqy__yxtd)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        iqy__yxtd = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(iqy__yxtd)


install_arith_ops()
