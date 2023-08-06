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
        ryur__fdjy = lhs.data if isinstance(lhs, SeriesType) else lhs
        alhfj__hla = rhs.data if isinstance(rhs, SeriesType) else rhs
        if ryur__fdjy in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and alhfj__hla.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            ryur__fdjy = alhfj__hla.dtype
        elif alhfj__hla in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and ryur__fdjy.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            alhfj__hla = ryur__fdjy.dtype
        jshq__lkup = ryur__fdjy, alhfj__hla
        izl__oph = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            eje__fvv = self.context.resolve_function_type(self.key,
                jshq__lkup, {}).return_type
        except Exception as vmb__gghw:
            raise BodoError(izl__oph)
        if is_overload_bool(eje__fvv):
            raise BodoError(izl__oph)
        okcn__ydi = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        pfa__vfrh = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        kmbt__ukl = types.bool_
        hmpoh__weu = SeriesType(kmbt__ukl, eje__fvv, okcn__ydi, pfa__vfrh)
        return hmpoh__weu(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        nqe__fzep = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if nqe__fzep is None:
            nqe__fzep = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, nqe__fzep, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        ryur__fdjy = lhs.data if isinstance(lhs, SeriesType) else lhs
        alhfj__hla = rhs.data if isinstance(rhs, SeriesType) else rhs
        jshq__lkup = ryur__fdjy, alhfj__hla
        izl__oph = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            eje__fvv = self.context.resolve_function_type(self.key,
                jshq__lkup, {}).return_type
        except Exception as prdyi__mztj:
            raise BodoError(izl__oph)
        okcn__ydi = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        pfa__vfrh = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        kmbt__ukl = eje__fvv.dtype
        hmpoh__weu = SeriesType(kmbt__ukl, eje__fvv, okcn__ydi, pfa__vfrh)
        return hmpoh__weu(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        nqe__fzep = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if nqe__fzep is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                nqe__fzep = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, nqe__fzep, sig, args)
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
            nqe__fzep = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return nqe__fzep(lhs, rhs)
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
            nqe__fzep = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return nqe__fzep(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    jsoo__nzke = lhs == datetime_timedelta_type and rhs == datetime_date_type
    xey__odfnz = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return jsoo__nzke or xey__odfnz


def add_timestamp(lhs, rhs):
    vxu__tfiaw = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    gtte__gst = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return vxu__tfiaw or gtte__gst


def add_datetime_and_timedeltas(lhs, rhs):
    zmrgu__dulh = [datetime_timedelta_type, pd_timedelta_type]
    okeyj__nkqyq = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    wigv__uhn = lhs in zmrgu__dulh and rhs in zmrgu__dulh
    ueoct__ojtjq = (lhs == datetime_datetime_type and rhs in zmrgu__dulh or
        rhs == datetime_datetime_type and lhs in zmrgu__dulh)
    return wigv__uhn or ueoct__ojtjq


def mul_string_arr_and_int(lhs, rhs):
    alhfj__hla = isinstance(lhs, types.Integer) and rhs == string_array_type
    ryur__fdjy = lhs == string_array_type and isinstance(rhs, types.Integer)
    return alhfj__hla or ryur__fdjy


def mul_timedelta_and_int(lhs, rhs):
    jsoo__nzke = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    xey__odfnz = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return jsoo__nzke or xey__odfnz


def mul_date_offset_and_int(lhs, rhs):
    nui__tqe = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    rcg__ltq = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return nui__tqe or rcg__ltq


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    uad__cdf = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    anehm__cndeh = [date_offset_type, month_begin_type, month_end_type,
        week_type]
    return rhs in anehm__cndeh and lhs in uad__cdf


def sub_dt_index_and_timestamp(lhs, rhs):
    cnu__bcf = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    ibgxg__xfjru = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return cnu__bcf or ibgxg__xfjru


def sub_dt_or_td(lhs, rhs):
    rsrp__dpjj = lhs == datetime_date_type and rhs == datetime_timedelta_type
    qjld__lywoa = lhs == datetime_date_type and rhs == datetime_date_type
    eel__lig = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return rsrp__dpjj or qjld__lywoa or eel__lig


def sub_datetime_and_timedeltas(lhs, rhs):
    tksj__zvwv = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    rdpr__gyc = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return tksj__zvwv or rdpr__gyc


def div_timedelta_and_int(lhs, rhs):
    wigv__uhn = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    pqdb__cwcgo = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return wigv__uhn or pqdb__cwcgo


def div_datetime_timedelta(lhs, rhs):
    wigv__uhn = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    pqdb__cwcgo = lhs == datetime_timedelta_type and rhs == types.int64
    return wigv__uhn or pqdb__cwcgo


def mod_timedeltas(lhs, rhs):
    cgpbf__qsdyz = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    kpui__wnqj = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return cgpbf__qsdyz or kpui__wnqj


def cmp_dt_index_to_string(lhs, rhs):
    cnu__bcf = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    ibgxg__xfjru = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return cnu__bcf or ibgxg__xfjru


def cmp_timestamp_or_date(lhs, rhs):
    pcx__mremo = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    zjzjt__iuh = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    opur__wtsd = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    tldea__dfb = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    hfb__iknm = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return pcx__mremo or zjzjt__iuh or opur__wtsd or tldea__dfb or hfb__iknm


def cmp_timeseries(lhs, rhs):
    bms__kqyzr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    wif__vtiwu = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    cgsrx__bqolp = bms__kqyzr or wif__vtiwu
    qmbiw__iztnc = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    igyg__wrotv = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    tlgc__bemk = qmbiw__iztnc or igyg__wrotv
    return cgsrx__bqolp or tlgc__bemk


def cmp_timedeltas(lhs, rhs):
    wigv__uhn = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in wigv__uhn and rhs in wigv__uhn


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    cptyy__thos = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return cptyy__thos


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    wlxgc__bksri = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    joc__recju = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    psvi__obxf = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    kjdiq__wjqy = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return wlxgc__bksri or joc__recju or psvi__obxf or kjdiq__wjqy


def args_td_and_int_array(lhs, rhs):
    kxtk__rkgu = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    vrmrz__rxsys = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return kxtk__rkgu and vrmrz__rxsys


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        xey__odfnz = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        jsoo__nzke = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        edwyf__cro = xey__odfnz or jsoo__nzke
        lnzxd__chk = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        ewv__yzmrq = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        yudwc__nxqmu = lnzxd__chk or ewv__yzmrq
        vvxyo__vaxnl = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        uwvs__icfmn = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        kpmuk__pcdct = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ltqb__efge = vvxyo__vaxnl or uwvs__icfmn or kpmuk__pcdct
        yxn__rmt = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        yul__naub = isinstance(lhs, tys) or isinstance(rhs, tys)
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (edwyf__cro or yudwc__nxqmu or ltqb__efge or yxn__rmt or
            yul__naub or cpfar__yach)
    if op == operator.pow:
        vlsin__jqg = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        svjfg__sxm = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        kpmuk__pcdct = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return vlsin__jqg or svjfg__sxm or kpmuk__pcdct or cpfar__yach
    if op == operator.floordiv:
        uwvs__icfmn = lhs in types.real_domain and rhs in types.real_domain
        vvxyo__vaxnl = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ckt__ofllk = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        wigv__uhn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (uwvs__icfmn or vvxyo__vaxnl or ckt__ofllk or wigv__uhn or
            cpfar__yach)
    if op == operator.truediv:
        xqkco__gatab = lhs in machine_ints and rhs in machine_ints
        uwvs__icfmn = lhs in types.real_domain and rhs in types.real_domain
        kpmuk__pcdct = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        vvxyo__vaxnl = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ckt__ofllk = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        ubqmf__luax = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wigv__uhn = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (xqkco__gatab or uwvs__icfmn or kpmuk__pcdct or vvxyo__vaxnl or
            ckt__ofllk or ubqmf__luax or wigv__uhn or cpfar__yach)
    if op == operator.mod:
        xqkco__gatab = lhs in machine_ints and rhs in machine_ints
        uwvs__icfmn = lhs in types.real_domain and rhs in types.real_domain
        vvxyo__vaxnl = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        ckt__ofllk = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (xqkco__gatab or uwvs__icfmn or vvxyo__vaxnl or ckt__ofllk or
            cpfar__yach)
    if op == operator.add or op == operator.sub:
        edwyf__cro = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        voe__rpq = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        gpc__wztiy = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        nluk__sos = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        vvxyo__vaxnl = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        uwvs__icfmn = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        kpmuk__pcdct = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ltqb__efge = vvxyo__vaxnl or uwvs__icfmn or kpmuk__pcdct
        cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        zefz__mxprf = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        yxn__rmt = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        eyp__drq = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        fue__ari = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        aka__cmwa = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        ommy__xjjg = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        fdb__hei = eyp__drq or fue__ari or aka__cmwa or ommy__xjjg
        yudwc__nxqmu = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        ndpf__ofn = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        bji__zwpv = yudwc__nxqmu or ndpf__ofn
        esi__rrduj = lhs == types.NPTimedelta and rhs == types.NPDatetime
        vqace__lxf = (zefz__mxprf or yxn__rmt or fdb__hei or bji__zwpv or
            esi__rrduj)
        znd__mhcl = op == operator.add and vqace__lxf
        return (edwyf__cro or voe__rpq or gpc__wztiy or nluk__sos or
            ltqb__efge or cpfar__yach or znd__mhcl)


def cmp_op_supported_by_numba(lhs, rhs):
    cpfar__yach = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    yxn__rmt = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    edwyf__cro = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    hmkw__phlkg = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    yudwc__nxqmu = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    zefz__mxprf = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    nluk__sos = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    ltqb__efge = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    ryur__eff = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    bzgzo__aowdo = isinstance(lhs, types.NoneType) or isinstance(rhs, types
        .NoneType)
    gxs__nouak = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    gio__ese = isinstance(lhs, types.EnumMember) and isinstance(rhs, types.
        EnumMember)
    zefj__grbi = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (yxn__rmt or edwyf__cro or hmkw__phlkg or yudwc__nxqmu or
        zefz__mxprf or nluk__sos or ltqb__efge or ryur__eff or bzgzo__aowdo or
        gxs__nouak or cpfar__yach or gio__ese or zefj__grbi)


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
        scj__akx = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(scj__akx)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        scj__akx = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(scj__akx)


install_arith_ops()
