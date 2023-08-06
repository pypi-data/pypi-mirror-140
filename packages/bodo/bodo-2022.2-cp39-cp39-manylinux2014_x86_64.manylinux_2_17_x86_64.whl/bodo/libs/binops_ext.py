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
        lvy__vvwp = lhs.data if isinstance(lhs, SeriesType) else lhs
        rcgr__xedt = rhs.data if isinstance(rhs, SeriesType) else rhs
        if lvy__vvwp in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and rcgr__xedt.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            lvy__vvwp = rcgr__xedt.dtype
        elif rcgr__xedt in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and lvy__vvwp.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            rcgr__xedt = lvy__vvwp.dtype
        frhfd__yxfco = lvy__vvwp, rcgr__xedt
        fpqeb__kkmkd = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            web__gqqv = self.context.resolve_function_type(self.key,
                frhfd__yxfco, {}).return_type
        except Exception as lkab__gur:
            raise BodoError(fpqeb__kkmkd)
        if is_overload_bool(web__gqqv):
            raise BodoError(fpqeb__kkmkd)
        vmqr__jbct = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        aldbg__wgtrj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        clp__zor = types.bool_
        ddu__ejk = SeriesType(clp__zor, web__gqqv, vmqr__jbct, aldbg__wgtrj)
        return ddu__ejk(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        qamfm__zdi = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if qamfm__zdi is None:
            qamfm__zdi = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, qamfm__zdi, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        lvy__vvwp = lhs.data if isinstance(lhs, SeriesType) else lhs
        rcgr__xedt = rhs.data if isinstance(rhs, SeriesType) else rhs
        frhfd__yxfco = lvy__vvwp, rcgr__xedt
        fpqeb__kkmkd = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            web__gqqv = self.context.resolve_function_type(self.key,
                frhfd__yxfco, {}).return_type
        except Exception as vne__cpi:
            raise BodoError(fpqeb__kkmkd)
        vmqr__jbct = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        aldbg__wgtrj = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        clp__zor = web__gqqv.dtype
        ddu__ejk = SeriesType(clp__zor, web__gqqv, vmqr__jbct, aldbg__wgtrj)
        return ddu__ejk(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        qamfm__zdi = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if qamfm__zdi is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                qamfm__zdi = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, qamfm__zdi, sig, args)
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
            qamfm__zdi = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return qamfm__zdi(lhs, rhs)
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
            qamfm__zdi = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return qamfm__zdi(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    wfe__wxro = lhs == datetime_timedelta_type and rhs == datetime_date_type
    adzqg__mzpya = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return wfe__wxro or adzqg__mzpya


def add_timestamp(lhs, rhs):
    ejd__rux = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    dsjc__zxje = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return ejd__rux or dsjc__zxje


def add_datetime_and_timedeltas(lhs, rhs):
    wquo__buano = [datetime_timedelta_type, pd_timedelta_type]
    sxo__odc = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    earq__teni = lhs in wquo__buano and rhs in wquo__buano
    gxll__hxo = (lhs == datetime_datetime_type and rhs in wquo__buano or 
        rhs == datetime_datetime_type and lhs in wquo__buano)
    return earq__teni or gxll__hxo


def mul_string_arr_and_int(lhs, rhs):
    rcgr__xedt = isinstance(lhs, types.Integer) and rhs == string_array_type
    lvy__vvwp = lhs == string_array_type and isinstance(rhs, types.Integer)
    return rcgr__xedt or lvy__vvwp


def mul_timedelta_and_int(lhs, rhs):
    wfe__wxro = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    adzqg__mzpya = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return wfe__wxro or adzqg__mzpya


def mul_date_offset_and_int(lhs, rhs):
    qun__trp = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    axhpa__vclgv = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return qun__trp or axhpa__vclgv


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    ini__qaq = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    bswk__ayfy = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in bswk__ayfy and lhs in ini__qaq


def sub_dt_index_and_timestamp(lhs, rhs):
    yuett__cbas = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    nlqr__bdw = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return yuett__cbas or nlqr__bdw


def sub_dt_or_td(lhs, rhs):
    carfq__mquv = lhs == datetime_date_type and rhs == datetime_timedelta_type
    ulmol__wzodw = lhs == datetime_date_type and rhs == datetime_date_type
    dmsq__hlha = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return carfq__mquv or ulmol__wzodw or dmsq__hlha


def sub_datetime_and_timedeltas(lhs, rhs):
    jkfd__yox = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    iykis__gekfs = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return jkfd__yox or iykis__gekfs


def div_timedelta_and_int(lhs, rhs):
    earq__teni = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    zxq__ehit = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return earq__teni or zxq__ehit


def div_datetime_timedelta(lhs, rhs):
    earq__teni = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    zxq__ehit = lhs == datetime_timedelta_type and rhs == types.int64
    return earq__teni or zxq__ehit


def mod_timedeltas(lhs, rhs):
    ampkt__cbe = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    kwjv__hup = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return ampkt__cbe or kwjv__hup


def cmp_dt_index_to_string(lhs, rhs):
    yuett__cbas = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    nlqr__bdw = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return yuett__cbas or nlqr__bdw


def cmp_timestamp_or_date(lhs, rhs):
    dntda__gyhz = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    syihr__jnfy = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    igre__wree = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    sruzd__rrsvb = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    hutod__yjw = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (dntda__gyhz or syihr__jnfy or igre__wree or sruzd__rrsvb or
        hutod__yjw)


def cmp_timeseries(lhs, rhs):
    mxsr__naag = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    iqg__pqd = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    jzsn__jwebx = mxsr__naag or iqg__pqd
    cpxxo__nschq = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    zzj__gihd = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    fpcd__gpo = cpxxo__nschq or zzj__gihd
    return jzsn__jwebx or fpcd__gpo


def cmp_timedeltas(lhs, rhs):
    earq__teni = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in earq__teni and rhs in earq__teni


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    ihnb__lzqtv = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return ihnb__lzqtv


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    qud__vgc = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    rhnq__zkz = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    jzl__bndkr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    dnvie__ozfq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return qud__vgc or rhnq__zkz or jzl__bndkr or dnvie__ozfq


def args_td_and_int_array(lhs, rhs):
    pzyok__krm = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    xvjeo__zela = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return pzyok__krm and xvjeo__zela


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        adzqg__mzpya = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        wfe__wxro = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        jzhjh__pissx = adzqg__mzpya or wfe__wxro
        rmv__xcx = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        jslg__erm = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        gldr__vzapi = rmv__xcx or jslg__erm
        squm__qxsci = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        apwgc__kiwj = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        dvbh__pekt = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        adbxj__ajhje = squm__qxsci or apwgc__kiwj or dvbh__pekt
        pkndg__lvz = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        euei__iyreb = isinstance(lhs, tys) or isinstance(rhs, tys)
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (jzhjh__pissx or gldr__vzapi or adbxj__ajhje or pkndg__lvz or
            euei__iyreb or krc__xvo)
    if op == operator.pow:
        cgqi__kpb = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        xooe__ysmgf = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        dvbh__pekt = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return cgqi__kpb or xooe__ysmgf or dvbh__pekt or krc__xvo
    if op == operator.floordiv:
        apwgc__kiwj = lhs in types.real_domain and rhs in types.real_domain
        squm__qxsci = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ortqh__sst = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        earq__teni = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (apwgc__kiwj or squm__qxsci or ortqh__sst or earq__teni or
            krc__xvo)
    if op == operator.truediv:
        fwrb__hytou = lhs in machine_ints and rhs in machine_ints
        apwgc__kiwj = lhs in types.real_domain and rhs in types.real_domain
        dvbh__pekt = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        squm__qxsci = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ortqh__sst = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        bpt__req = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        earq__teni = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (fwrb__hytou or apwgc__kiwj or dvbh__pekt or squm__qxsci or
            ortqh__sst or bpt__req or earq__teni or krc__xvo)
    if op == operator.mod:
        fwrb__hytou = lhs in machine_ints and rhs in machine_ints
        apwgc__kiwj = lhs in types.real_domain and rhs in types.real_domain
        squm__qxsci = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ortqh__sst = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        return (fwrb__hytou or apwgc__kiwj or squm__qxsci or ortqh__sst or
            krc__xvo)
    if op == operator.add or op == operator.sub:
        jzhjh__pissx = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        axo__tmu = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        ykbg__wwjkg = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        xqfn__vopx = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        squm__qxsci = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        apwgc__kiwj = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        dvbh__pekt = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        adbxj__ajhje = squm__qxsci or apwgc__kiwj or dvbh__pekt
        krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
        law__curae = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        pkndg__lvz = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        cnc__dlse = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        cbump__qcv = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        jeuwb__mto = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        vpfqc__lgzdz = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        nuhi__tce = cnc__dlse or cbump__qcv or jeuwb__mto or vpfqc__lgzdz
        gldr__vzapi = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        kdtzy__lokf = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        gewys__ppt = gldr__vzapi or kdtzy__lokf
        qxiu__zsgx = lhs == types.NPTimedelta and rhs == types.NPDatetime
        rhk__jfklx = (law__curae or pkndg__lvz or nuhi__tce or gewys__ppt or
            qxiu__zsgx)
        crjyi__sntz = op == operator.add and rhk__jfklx
        return (jzhjh__pissx or axo__tmu or ykbg__wwjkg or xqfn__vopx or
            adbxj__ajhje or krc__xvo or crjyi__sntz)


def cmp_op_supported_by_numba(lhs, rhs):
    krc__xvo = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    pkndg__lvz = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    jzhjh__pissx = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    lcgor__nup = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    gldr__vzapi = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    law__curae = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    xqfn__vopx = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    adbxj__ajhje = isinstance(lhs, types.Number) and isinstance(rhs, types.
        Number)
    wjlj__wyl = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    xurgi__rpl = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    hhs__mfqpb = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    iwmze__wnbd = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    sinq__aqbfg = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (pkndg__lvz or jzhjh__pissx or lcgor__nup or gldr__vzapi or
        law__curae or xqfn__vopx or adbxj__ajhje or wjlj__wyl or xurgi__rpl or
        hhs__mfqpb or krc__xvo or iwmze__wnbd or sinq__aqbfg)


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
        ypmaw__vivg = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(ypmaw__vivg)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        ypmaw__vivg = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(ypmaw__vivg)


install_arith_ops()
