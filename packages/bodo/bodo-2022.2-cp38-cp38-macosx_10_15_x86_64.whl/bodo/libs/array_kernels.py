"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_none, raise_bodo_error
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    assert isinstance(arr, types.Array)
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        rsw__nepat = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = rsw__nepat
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            dzw__dkki = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            dzw__dkki[ind + 1] = dzw__dkki[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            dzw__dkki = bodo.libs.array_item_arr_ext.get_offsets(arr)
            dzw__dkki[ind + 1] = dzw__dkki[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    rcwn__hex = arr_tup.count
    obie__lhf = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(rcwn__hex):
        obie__lhf += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    obie__lhf += '  return\n'
    zdkd__zndeg = {}
    exec(obie__lhf, {'setna': setna}, zdkd__zndeg)
    impl = zdkd__zndeg['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        wrv__boyhz = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(wrv__boyhz.start, wrv__boyhz.stop, wrv__boyhz.step):
            setna(arr, i)
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    dvd__grfwx = array_to_info(arr)
    _median_series_computation(res, dvd__grfwx, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(dvd__grfwx)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    dvd__grfwx = array_to_info(arr)
    _autocorr_series_computation(res, dvd__grfwx, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(dvd__grfwx)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    dvd__grfwx = array_to_info(arr)
    _compute_series_monotonicity(res, dvd__grfwx, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(dvd__grfwx)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    grly__ihz = res[0] > 0.5
    return grly__ihz


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        cqka__vgec = '-'
        garf__khgb = 'index_arr[0] > threshhold_date'
        hgp__pmq = '1, n+1'
        jkh__rtgb = 'index_arr[-i] <= threshhold_date'
        hdz__zllv = 'i - 1'
    else:
        cqka__vgec = '+'
        garf__khgb = 'index_arr[-1] < threshhold_date'
        hgp__pmq = 'n'
        jkh__rtgb = 'index_arr[i] >= threshhold_date'
        hdz__zllv = 'i'
    obie__lhf = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        obie__lhf += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        obie__lhf += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            obie__lhf += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            obie__lhf += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            obie__lhf += '    else:\n'
            obie__lhf += '      threshhold_date = initial_date + date_offset\n'
        else:
            obie__lhf += (
                f'    threshhold_date = initial_date {cqka__vgec} date_offset\n'
                )
    else:
        obie__lhf += f'  threshhold_date = initial_date {cqka__vgec} offset\n'
    obie__lhf += '  local_valid = 0\n'
    obie__lhf += f'  n = len(index_arr)\n'
    obie__lhf += f'  if n:\n'
    obie__lhf += f'    if {garf__khgb}:\n'
    obie__lhf += '      loc_valid = n\n'
    obie__lhf += '    else:\n'
    obie__lhf += f'      for i in range({hgp__pmq}):\n'
    obie__lhf += f'        if {jkh__rtgb}:\n'
    obie__lhf += f'          loc_valid = {hdz__zllv}\n'
    obie__lhf += '          break\n'
    obie__lhf += '  if is_parallel:\n'
    obie__lhf += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    obie__lhf += '    return total_valid\n'
    obie__lhf += '  else:\n'
    obie__lhf += '    return loc_valid\n'
    zdkd__zndeg = {}
    exec(obie__lhf, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, zdkd__zndeg)
    return zdkd__zndeg['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    zzfkg__qyh = numba_to_c_type(sig.args[0].dtype)
    suiaf__snc = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), zzfkg__qyh))
    lkn__cvkc = args[0]
    evvca__yhovj = sig.args[0]
    if isinstance(evvca__yhovj, (IntegerArrayType, BooleanArrayType)):
        lkn__cvkc = cgutils.create_struct_proxy(evvca__yhovj)(context,
            builder, lkn__cvkc).data
        evvca__yhovj = types.Array(evvca__yhovj.dtype, 1, 'C')
    assert evvca__yhovj.ndim == 1
    arr = make_array(evvca__yhovj)(context, builder, lkn__cvkc)
    iwap__ozlx = builder.extract_value(arr.shape, 0)
    xtlvq__hlp = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        iwap__ozlx, args[1], builder.load(suiaf__snc)]
    zwxq__svu = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    ftdqo__trznc = lir.FunctionType(lir.DoubleType(), zwxq__svu)
    ynf__omtv = cgutils.get_or_insert_function(builder.module, ftdqo__trznc,
        name='quantile_sequential')
    pfiw__ggumo = builder.call(ynf__omtv, xtlvq__hlp)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return pfiw__ggumo


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    zzfkg__qyh = numba_to_c_type(sig.args[0].dtype)
    suiaf__snc = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), zzfkg__qyh))
    lkn__cvkc = args[0]
    evvca__yhovj = sig.args[0]
    if isinstance(evvca__yhovj, (IntegerArrayType, BooleanArrayType)):
        lkn__cvkc = cgutils.create_struct_proxy(evvca__yhovj)(context,
            builder, lkn__cvkc).data
        evvca__yhovj = types.Array(evvca__yhovj.dtype, 1, 'C')
    assert evvca__yhovj.ndim == 1
    arr = make_array(evvca__yhovj)(context, builder, lkn__cvkc)
    iwap__ozlx = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        dqoic__dvy = args[2]
    else:
        dqoic__dvy = iwap__ozlx
    xtlvq__hlp = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        iwap__ozlx, dqoic__dvy, args[1], builder.load(suiaf__snc)]
    zwxq__svu = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    ftdqo__trznc = lir.FunctionType(lir.DoubleType(), zwxq__svu)
    ynf__omtv = cgutils.get_or_insert_function(builder.module, ftdqo__trznc,
        name='quantile_parallel')
    pfiw__ggumo = builder.call(ynf__omtv, xtlvq__hlp)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return pfiw__ggumo


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    cql__qhf = start
    lmrm__qfmb = 2 * start + 1
    gqqf__xda = 2 * start + 2
    if lmrm__qfmb < n and not cmp_f(arr[lmrm__qfmb], arr[cql__qhf]):
        cql__qhf = lmrm__qfmb
    if gqqf__xda < n and not cmp_f(arr[gqqf__xda], arr[cql__qhf]):
        cql__qhf = gqqf__xda
    if cql__qhf != start:
        arr[start], arr[cql__qhf] = arr[cql__qhf], arr[start]
        ind_arr[start], ind_arr[cql__qhf] = ind_arr[cql__qhf], ind_arr[start]
        min_heapify(arr, ind_arr, n, cql__qhf, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        wjw__dhf = np.empty(k, A.dtype)
        smw__qnapv = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                wjw__dhf[ind] = A[i]
                smw__qnapv[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            wjw__dhf = wjw__dhf[:ind]
            smw__qnapv = smw__qnapv[:ind]
        return wjw__dhf, smw__qnapv, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        dafpf__rzk = np.sort(A)
        enqjo__ulqzt = index_arr[np.argsort(A)]
        wnm__oeqkp = pd.Series(dafpf__rzk).notna().values
        dafpf__rzk = dafpf__rzk[wnm__oeqkp]
        enqjo__ulqzt = enqjo__ulqzt[wnm__oeqkp]
        if is_largest:
            dafpf__rzk = dafpf__rzk[::-1]
            enqjo__ulqzt = enqjo__ulqzt[::-1]
        return np.ascontiguousarray(dafpf__rzk), np.ascontiguousarray(
            enqjo__ulqzt)
    wjw__dhf, smw__qnapv, start = select_k_nonan(A, index_arr, m, k)
    smw__qnapv = smw__qnapv[wjw__dhf.argsort()]
    wjw__dhf.sort()
    if not is_largest:
        wjw__dhf = np.ascontiguousarray(wjw__dhf[::-1])
        smw__qnapv = np.ascontiguousarray(smw__qnapv[::-1])
    for i in range(start, m):
        if cmp_f(A[i], wjw__dhf[0]):
            wjw__dhf[0] = A[i]
            smw__qnapv[0] = index_arr[i]
            min_heapify(wjw__dhf, smw__qnapv, k, 0, cmp_f)
    smw__qnapv = smw__qnapv[wjw__dhf.argsort()]
    wjw__dhf.sort()
    if is_largest:
        wjw__dhf = wjw__dhf[::-1]
        smw__qnapv = smw__qnapv[::-1]
    return np.ascontiguousarray(wjw__dhf), np.ascontiguousarray(smw__qnapv)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    epvt__qcs = bodo.libs.distributed_api.get_rank()
    jzjh__fdq, kpbue__zpyr = nlargest(A, I, k, is_largest, cmp_f)
    pxym__xlqgf = bodo.libs.distributed_api.gatherv(jzjh__fdq)
    lioy__mmbjb = bodo.libs.distributed_api.gatherv(kpbue__zpyr)
    if epvt__qcs == MPI_ROOT:
        res, vdcf__cxf = nlargest(pxym__xlqgf, lioy__mmbjb, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        vdcf__cxf = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(vdcf__cxf)
    return res, vdcf__cxf


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    nty__pphm, redyx__oyqal = mat.shape
    nyib__ysh = np.empty((redyx__oyqal, redyx__oyqal), dtype=np.float64)
    for umtmg__jwxep in range(redyx__oyqal):
        for twwh__nukv in range(umtmg__jwxep + 1):
            qlipg__qwjav = 0
            def__hskaz = rxe__jtp = hrhmt__zkc = rjfeu__rnb = 0.0
            for i in range(nty__pphm):
                if np.isfinite(mat[i, umtmg__jwxep]) and np.isfinite(mat[i,
                    twwh__nukv]):
                    abs__arm = mat[i, umtmg__jwxep]
                    omgl__wpk = mat[i, twwh__nukv]
                    qlipg__qwjav += 1
                    hrhmt__zkc += abs__arm
                    rjfeu__rnb += omgl__wpk
            if parallel:
                qlipg__qwjav = bodo.libs.distributed_api.dist_reduce(
                    qlipg__qwjav, sum_op)
                hrhmt__zkc = bodo.libs.distributed_api.dist_reduce(hrhmt__zkc,
                    sum_op)
                rjfeu__rnb = bodo.libs.distributed_api.dist_reduce(rjfeu__rnb,
                    sum_op)
            if qlipg__qwjav < minpv:
                nyib__ysh[umtmg__jwxep, twwh__nukv] = nyib__ysh[twwh__nukv,
                    umtmg__jwxep] = np.nan
            else:
                tiym__pdwbx = hrhmt__zkc / qlipg__qwjav
                kzqdt__bql = rjfeu__rnb / qlipg__qwjav
                hrhmt__zkc = 0.0
                for i in range(nty__pphm):
                    if np.isfinite(mat[i, umtmg__jwxep]) and np.isfinite(mat
                        [i, twwh__nukv]):
                        abs__arm = mat[i, umtmg__jwxep] - tiym__pdwbx
                        omgl__wpk = mat[i, twwh__nukv] - kzqdt__bql
                        hrhmt__zkc += abs__arm * omgl__wpk
                        def__hskaz += abs__arm * abs__arm
                        rxe__jtp += omgl__wpk * omgl__wpk
                if parallel:
                    hrhmt__zkc = bodo.libs.distributed_api.dist_reduce(
                        hrhmt__zkc, sum_op)
                    def__hskaz = bodo.libs.distributed_api.dist_reduce(
                        def__hskaz, sum_op)
                    rxe__jtp = bodo.libs.distributed_api.dist_reduce(rxe__jtp,
                        sum_op)
                wwa__fevbp = qlipg__qwjav - 1.0 if cov else sqrt(def__hskaz *
                    rxe__jtp)
                if wwa__fevbp != 0.0:
                    nyib__ysh[umtmg__jwxep, twwh__nukv] = nyib__ysh[
                        twwh__nukv, umtmg__jwxep] = hrhmt__zkc / wwa__fevbp
                else:
                    nyib__ysh[umtmg__jwxep, twwh__nukv] = nyib__ysh[
                        twwh__nukv, umtmg__jwxep] = np.nan
    return nyib__ysh


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    ddjhf__vdua = n != 1
    obie__lhf = 'def impl(data, parallel=False):\n'
    obie__lhf += '  if parallel:\n'
    ulwqt__ags = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    obie__lhf += f'    cpp_table = arr_info_list_to_table([{ulwqt__ags}])\n'
    obie__lhf += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    eaxfj__paz = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    obie__lhf += f'    data = ({eaxfj__paz},)\n'
    obie__lhf += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    obie__lhf += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    obie__lhf += '    bodo.libs.array.delete_table(cpp_table)\n'
    obie__lhf += (
        '  data = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data)\n')
    obie__lhf += '  n = len(data[0])\n'
    obie__lhf += '  out = np.empty(n, np.bool_)\n'
    obie__lhf += '  uniqs = dict()\n'
    if ddjhf__vdua:
        obie__lhf += '  for i in range(n):\n'
        mpmd__bzuq = ', '.join(f'data[{i}][i]' for i in range(n))
        shw__bmiu = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        obie__lhf += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({mpmd__bzuq},), ({shw__bmiu},))
"""
        obie__lhf += '    if val in uniqs:\n'
        obie__lhf += '      out[i] = True\n'
        obie__lhf += '    else:\n'
        obie__lhf += '      out[i] = False\n'
        obie__lhf += '      uniqs[val] = 0\n'
    else:
        obie__lhf += '  data = data[0]\n'
        obie__lhf += '  hasna = False\n'
        obie__lhf += '  for i in range(n):\n'
        obie__lhf += '    if bodo.libs.array_kernels.isna(data, i):\n'
        obie__lhf += '      out[i] = hasna\n'
        obie__lhf += '      hasna = True\n'
        obie__lhf += '    else:\n'
        obie__lhf += '      val = data[i]\n'
        obie__lhf += '      if val in uniqs:\n'
        obie__lhf += '        out[i] = True\n'
        obie__lhf += '      else:\n'
        obie__lhf += '        out[i] = False\n'
        obie__lhf += '        uniqs[val] = 0\n'
    obie__lhf += '  if parallel:\n'
    obie__lhf += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    obie__lhf += '  return out\n'
    zdkd__zndeg = {}
    exec(obie__lhf, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, zdkd__zndeg)
    impl = zdkd__zndeg['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    rcwn__hex = len(data)
    obie__lhf = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    obie__lhf += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        rcwn__hex)))
    obie__lhf += '  table_total = arr_info_list_to_table(info_list_total)\n'
    obie__lhf += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(rcwn__hex))
    for iptn__kkcnk in range(rcwn__hex):
        obie__lhf += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(iptn__kkcnk, iptn__kkcnk, iptn__kkcnk))
    obie__lhf += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(rcwn__hex))
    obie__lhf += '  delete_table(out_table)\n'
    obie__lhf += '  delete_table(table_total)\n'
    obie__lhf += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(rcwn__hex)))
    zdkd__zndeg = {}
    exec(obie__lhf, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, zdkd__zndeg)
    impl = zdkd__zndeg['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    rcwn__hex = len(data)
    obie__lhf = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    obie__lhf += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        rcwn__hex)))
    obie__lhf += '  table_total = arr_info_list_to_table(info_list_total)\n'
    obie__lhf += '  keep_i = 0\n'
    obie__lhf += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False)
"""
    for iptn__kkcnk in range(rcwn__hex):
        obie__lhf += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(iptn__kkcnk, iptn__kkcnk, iptn__kkcnk))
    obie__lhf += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(rcwn__hex))
    obie__lhf += '  delete_table(out_table)\n'
    obie__lhf += '  delete_table(table_total)\n'
    obie__lhf += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(rcwn__hex)))
    zdkd__zndeg = {}
    exec(obie__lhf, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zdkd__zndeg)
    impl = zdkd__zndeg['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        vpu__lvmpg = [array_to_info(data_arr)]
        aznll__jnae = arr_info_list_to_table(vpu__lvmpg)
        mun__vcm = 0
        zvlvc__phfh = drop_duplicates_table(aznll__jnae, parallel, 1,
            mun__vcm, False)
        dol__yetx = info_to_array(info_from_table(zvlvc__phfh, 0), data_arr)
        delete_table(zvlvc__phfh)
        delete_table(aznll__jnae)
        return dol__yetx
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    cttj__qst = len(data.types)
    mseq__busnt = [('out' + str(i)) for i in range(cttj__qst)]
    usc__azjy = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    kbah__yqfl = ['isna(data[{}], i)'.format(i) for i in usc__azjy]
    ums__hlbsz = 'not ({})'.format(' or '.join(kbah__yqfl))
    if not is_overload_none(thresh):
        ums__hlbsz = '(({}) <= ({}) - thresh)'.format(' + '.join(kbah__yqfl
            ), cttj__qst - 1)
    elif how == 'all':
        ums__hlbsz = 'not ({})'.format(' and '.join(kbah__yqfl))
    obie__lhf = 'def _dropna_imp(data, how, thresh, subset):\n'
    obie__lhf += '  old_len = len(data[0])\n'
    obie__lhf += '  new_len = 0\n'
    obie__lhf += '  for i in range(old_len):\n'
    obie__lhf += '    if {}:\n'.format(ums__hlbsz)
    obie__lhf += '      new_len += 1\n'
    for i, out in enumerate(mseq__busnt):
        if isinstance(data[i], bodo.CategoricalArrayType):
            obie__lhf += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            obie__lhf += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    obie__lhf += '  curr_ind = 0\n'
    obie__lhf += '  for i in range(old_len):\n'
    obie__lhf += '    if {}:\n'.format(ums__hlbsz)
    for i in range(cttj__qst):
        obie__lhf += '      if isna(data[{}], i):\n'.format(i)
        obie__lhf += '        setna({}, curr_ind)\n'.format(mseq__busnt[i])
        obie__lhf += '      else:\n'
        obie__lhf += '        {}[curr_ind] = data[{}][i]\n'.format(mseq__busnt
            [i], i)
    obie__lhf += '      curr_ind += 1\n'
    obie__lhf += '  return {}\n'.format(', '.join(mseq__busnt))
    zdkd__zndeg = {}
    evywq__yjcd = {'t{}'.format(i): peu__gcua for i, peu__gcua in enumerate
        (data.types)}
    evywq__yjcd.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(obie__lhf, evywq__yjcd, zdkd__zndeg)
    uhq__kcp = zdkd__zndeg['_dropna_imp']
    return uhq__kcp


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        evvca__yhovj = arr.dtype
        hgv__gpb = evvca__yhovj.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            qid__oeevi = init_nested_counts(hgv__gpb)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                qid__oeevi = add_nested_counts(qid__oeevi, val[ind])
            dol__yetx = bodo.utils.utils.alloc_type(n, evvca__yhovj, qid__oeevi
                )
            for qwz__faa in range(n):
                if bodo.libs.array_kernels.isna(arr, qwz__faa):
                    setna(dol__yetx, qwz__faa)
                    continue
                val = arr[qwz__faa]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(dol__yetx, qwz__faa)
                    continue
                dol__yetx[qwz__faa] = val[ind]
            return dol__yetx
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    smgg__hdje = _to_readonly(arr_types.types[0])
    return all(isinstance(peu__gcua, CategoricalArrayType) and _to_readonly
        (peu__gcua) == smgg__hdje for peu__gcua in arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        wmy__ybk = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            raerl__vymau = 0
            oxb__fds = []
            for A in arr_list:
                dsbc__jphay = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                oxb__fds.append(bodo.libs.array_item_arr_ext.get_data(A))
                raerl__vymau += dsbc__jphay
            xyecv__ymdu = np.empty(raerl__vymau + 1, offset_type)
            sdsyl__ztrb = bodo.libs.array_kernels.concat(oxb__fds)
            mutyf__eurt = np.empty(raerl__vymau + 7 >> 3, np.uint8)
            nbwl__tld = 0
            lsw__cqqsx = 0
            for A in arr_list:
                enho__vmdeh = bodo.libs.array_item_arr_ext.get_offsets(A)
                ydvs__awz = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                dsbc__jphay = len(A)
                enwq__buma = enho__vmdeh[dsbc__jphay]
                for i in range(dsbc__jphay):
                    xyecv__ymdu[i + nbwl__tld] = enho__vmdeh[i] + lsw__cqqsx
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ydvs__awz, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mutyf__eurt, i +
                        nbwl__tld, xcq__umstw)
                nbwl__tld += dsbc__jphay
                lsw__cqqsx += enwq__buma
            xyecv__ymdu[nbwl__tld] = lsw__cqqsx
            dol__yetx = bodo.libs.array_item_arr_ext.init_array_item_array(
                raerl__vymau, sdsyl__ztrb, xyecv__ymdu, mutyf__eurt)
            return dol__yetx
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        echpy__apajl = arr_list.dtype.names
        obie__lhf = 'def struct_array_concat_impl(arr_list):\n'
        obie__lhf += f'    n_all = 0\n'
        for i in range(len(echpy__apajl)):
            obie__lhf += f'    concat_list{i} = []\n'
        obie__lhf += '    for A in arr_list:\n'
        obie__lhf += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(echpy__apajl)):
            obie__lhf += f'        concat_list{i}.append(data_tuple[{i}])\n'
        obie__lhf += '        n_all += len(A)\n'
        obie__lhf += '    n_bytes = (n_all + 7) >> 3\n'
        obie__lhf += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        obie__lhf += '    curr_bit = 0\n'
        obie__lhf += '    for A in arr_list:\n'
        obie__lhf += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        obie__lhf += '        for j in range(len(A)):\n'
        obie__lhf += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        obie__lhf += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        obie__lhf += '            curr_bit += 1\n'
        obie__lhf += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        voqkp__rxzwb = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(echpy__apajl))])
        obie__lhf += f'        ({voqkp__rxzwb},),\n'
        obie__lhf += '        new_mask,\n'
        obie__lhf += f'        {echpy__apajl},\n'
        obie__lhf += '    )\n'
        zdkd__zndeg = {}
        exec(obie__lhf, {'bodo': bodo, 'np': np}, zdkd__zndeg)
        return zdkd__zndeg['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            ymhn__yjw = 0
            for A in arr_list:
                ymhn__yjw += len(A)
            vvqp__bjp = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(ymhn__yjw))
            vpqbt__ent = 0
            for A in arr_list:
                for i in range(len(A)):
                    vvqp__bjp._data[i + vpqbt__ent] = A._data[i]
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vvqp__bjp.
                        _null_bitmap, i + vpqbt__ent, xcq__umstw)
                vpqbt__ent += len(A)
            return vvqp__bjp
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            ymhn__yjw = 0
            for A in arr_list:
                ymhn__yjw += len(A)
            vvqp__bjp = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(ymhn__yjw))
            vpqbt__ent = 0
            for A in arr_list:
                for i in range(len(A)):
                    vvqp__bjp._days_data[i + vpqbt__ent] = A._days_data[i]
                    vvqp__bjp._seconds_data[i + vpqbt__ent] = A._seconds_data[i
                        ]
                    vvqp__bjp._microseconds_data[i + vpqbt__ent
                        ] = A._microseconds_data[i]
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vvqp__bjp.
                        _null_bitmap, i + vpqbt__ent, xcq__umstw)
                vpqbt__ent += len(A)
            return vvqp__bjp
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        xwgp__otr = arr_list.dtype.precision
        tbb__rnb = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            ymhn__yjw = 0
            for A in arr_list:
                ymhn__yjw += len(A)
            vvqp__bjp = bodo.libs.decimal_arr_ext.alloc_decimal_array(ymhn__yjw
                , xwgp__otr, tbb__rnb)
            vpqbt__ent = 0
            for A in arr_list:
                for i in range(len(A)):
                    vvqp__bjp._data[i + vpqbt__ent] = A._data[i]
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vvqp__bjp.
                        _null_bitmap, i + vpqbt__ent, xcq__umstw)
                vpqbt__ent += len(A)
            return vvqp__bjp
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype in [string_array_type, bodo.binary_array_type]:
        if arr_list.dtype == bodo.binary_array_type:
            jsu__kslve = 'bodo.libs.str_arr_ext.pre_alloc_binary_array'
        elif arr_list.dtype == string_array_type:
            jsu__kslve = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        obie__lhf = 'def impl(arr_list):  # pragma: no cover\n'
        obie__lhf += '    # preallocate the output\n'
        obie__lhf += '    num_strs = 0\n'
        obie__lhf += '    num_chars = 0\n'
        obie__lhf += '    for A in arr_list:\n'
        obie__lhf += '        arr = A\n'
        obie__lhf += '        num_strs += len(arr)\n'
        obie__lhf += '        # this should work for both binary and string\n'
        obie__lhf += (
            '        num_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        obie__lhf += f'    out_arr = {jsu__kslve}(\n'
        obie__lhf += '        num_strs, num_chars\n'
        obie__lhf += '    )\n'
        obie__lhf += (
            '    bodo.libs.str_arr_ext.set_null_bits_to_value(out_arr, -1)\n')
        obie__lhf += '    # copy data to output\n'
        obie__lhf += '    curr_str_ind = 0\n'
        obie__lhf += '    curr_chars_ind = 0\n'
        obie__lhf += '    for A in arr_list:\n'
        obie__lhf += '        arr = A\n'
        obie__lhf += '        # This will probably need to be extended\n'
        obie__lhf += '        bodo.libs.str_arr_ext.set_string_array_range(\n'
        obie__lhf += '            out_arr, arr, curr_str_ind, curr_chars_ind\n'
        obie__lhf += '        )\n'
        obie__lhf += '        curr_str_ind += len(arr)\n'
        obie__lhf += '        # this should work for both binary and string\n'
        obie__lhf += (
            '        curr_chars_ind += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        obie__lhf += '    return out_arr\n'
        skui__hhhba = dict()
        exec(obie__lhf, {'bodo': bodo}, skui__hhhba)
        pbh__izdlp = skui__hhhba['impl']
        return pbh__izdlp
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(peu__gcua.dtype, types.Integer) for
        peu__gcua in arr_list.types) and any(isinstance(peu__gcua,
        IntegerArrayType) for peu__gcua in arr_list.types):

        def impl_int_arr_list(arr_list):
            dmv__knpq = convert_to_nullable_tup(arr_list)
            egz__cezw = []
            xus__wed = 0
            for A in dmv__knpq:
                egz__cezw.append(A._data)
                xus__wed += len(A)
            sdsyl__ztrb = bodo.libs.array_kernels.concat(egz__cezw)
            ddl__uxy = xus__wed + 7 >> 3
            lslvm__nrspb = np.empty(ddl__uxy, np.uint8)
            miaxm__dkc = 0
            for A in dmv__knpq:
                plq__xlh = A._null_bitmap
                for qwz__faa in range(len(A)):
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        plq__xlh, qwz__faa)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lslvm__nrspb,
                        miaxm__dkc, xcq__umstw)
                    miaxm__dkc += 1
            return bodo.libs.int_arr_ext.init_integer_array(sdsyl__ztrb,
                lslvm__nrspb)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(peu__gcua.dtype == types.bool_ for peu__gcua in
        arr_list.types) and any(peu__gcua == boolean_array for peu__gcua in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            dmv__knpq = convert_to_nullable_tup(arr_list)
            egz__cezw = []
            xus__wed = 0
            for A in dmv__knpq:
                egz__cezw.append(A._data)
                xus__wed += len(A)
            sdsyl__ztrb = bodo.libs.array_kernels.concat(egz__cezw)
            ddl__uxy = xus__wed + 7 >> 3
            lslvm__nrspb = np.empty(ddl__uxy, np.uint8)
            miaxm__dkc = 0
            for A in dmv__knpq:
                plq__xlh = A._null_bitmap
                for qwz__faa in range(len(A)):
                    xcq__umstw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        plq__xlh, qwz__faa)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lslvm__nrspb,
                        miaxm__dkc, xcq__umstw)
                    miaxm__dkc += 1
            return bodo.libs.bool_arr_ext.init_bool_array(sdsyl__ztrb,
                lslvm__nrspb)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            sbs__zeg = []
            for A in arr_list:
                sbs__zeg.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                sbs__zeg), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        zyoc__xsxho = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        obie__lhf = 'def impl(arr_list):\n'
        obie__lhf += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({zyoc__xsxho},)), arr_list[0].dtype)
"""
        skui__hhhba = {}
        exec(obie__lhf, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, skui__hhhba)
        return skui__hhhba['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            xus__wed = 0
            for A in arr_list:
                xus__wed += len(A)
            dol__yetx = np.empty(xus__wed, dtype)
            cwbr__pvysu = 0
            for A in arr_list:
                n = len(A)
                dol__yetx[cwbr__pvysu:cwbr__pvysu + n] = A
                cwbr__pvysu += n
            return dol__yetx
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(peu__gcua,
        (types.Array, IntegerArrayType)) and isinstance(peu__gcua.dtype,
        types.Integer) for peu__gcua in arr_list.types) and any(isinstance(
        peu__gcua, types.Array) and isinstance(peu__gcua.dtype, types.Float
        ) for peu__gcua in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            fmh__edjlp = []
            for A in arr_list:
                fmh__edjlp.append(A._data)
            mhnkj__vqif = bodo.libs.array_kernels.concat(fmh__edjlp)
            nyib__ysh = bodo.libs.map_arr_ext.init_map_arr(mhnkj__vqif)
            return nyib__ysh
        return impl_map_arr_list
    for cgo__ppb in arr_list:
        if not isinstance(cgo__ppb, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(peu__gcua.astype(np.float64) for peu__gcua in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    rcwn__hex = len(arr_tup.types)
    obie__lhf = 'def f(arr_tup):\n'
    obie__lhf += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(rcwn__hex
        )), ',' if rcwn__hex == 1 else '')
    zdkd__zndeg = {}
    exec(obie__lhf, {'np': np}, zdkd__zndeg)
    tbqu__njbgd = zdkd__zndeg['f']
    return tbqu__njbgd


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    rcwn__hex = len(arr_tup.types)
    gdh__pkat = find_common_np_dtype(arr_tup.types)
    hgv__gpb = None
    mza__qrymd = ''
    if isinstance(gdh__pkat, types.Integer):
        hgv__gpb = bodo.libs.int_arr_ext.IntDtype(gdh__pkat)
        mza__qrymd = '.astype(out_dtype, False)'
    obie__lhf = 'def f(arr_tup):\n'
    obie__lhf += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, mza__qrymd) for i in range(rcwn__hex)), ',' if rcwn__hex ==
        1 else '')
    zdkd__zndeg = {}
    exec(obie__lhf, {'bodo': bodo, 'out_dtype': hgv__gpb}, zdkd__zndeg)
    iman__swoku = zdkd__zndeg['f']
    return iman__swoku


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, mwk__cjp = build_set_seen_na(A)
        return len(s) + int(not dropna and mwk__cjp)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        kmde__fzr = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        gszgg__aokdy = len(kmde__fzr)
        return bodo.libs.distributed_api.dist_reduce(gszgg__aokdy, np.int32
            (sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([blh__tpael for blh__tpael in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        nufg__gca = np.finfo(A.dtype(1).dtype).max
    else:
        nufg__gca = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        dol__yetx = np.empty(n, A.dtype)
        eqs__avaif = nufg__gca
        for i in range(n):
            eqs__avaif = min(eqs__avaif, A[i])
            dol__yetx[i] = eqs__avaif
        return dol__yetx
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        nufg__gca = np.finfo(A.dtype(1).dtype).min
    else:
        nufg__gca = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        dol__yetx = np.empty(n, A.dtype)
        eqs__avaif = nufg__gca
        for i in range(n):
            eqs__avaif = max(eqs__avaif, A[i])
            dol__yetx[i] = eqs__avaif
        return dol__yetx
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        gsimi__vesse = arr_info_list_to_table([array_to_info(A)])
        bis__uftzu = 1
        mun__vcm = 0
        zvlvc__phfh = drop_duplicates_table(gsimi__vesse, parallel,
            bis__uftzu, mun__vcm, dropna)
        dol__yetx = info_to_array(info_from_table(zvlvc__phfh, 0), A)
        delete_table(gsimi__vesse)
        delete_table(zvlvc__phfh)
        return dol__yetx
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wmy__ybk = bodo.utils.typing.to_nullable_type(arr.dtype)
    dop__sdy = index_arr
    jxu__yqach = dop__sdy.dtype

    def impl(arr, index_arr):
        n = len(arr)
        qid__oeevi = init_nested_counts(wmy__ybk)
        ceeih__hrz = init_nested_counts(jxu__yqach)
        for i in range(n):
            qbn__zyowc = index_arr[i]
            if isna(arr, i):
                qid__oeevi = (qid__oeevi[0] + 1,) + qid__oeevi[1:]
                ceeih__hrz = add_nested_counts(ceeih__hrz, qbn__zyowc)
                continue
            tze__pqc = arr[i]
            if len(tze__pqc) == 0:
                qid__oeevi = (qid__oeevi[0] + 1,) + qid__oeevi[1:]
                ceeih__hrz = add_nested_counts(ceeih__hrz, qbn__zyowc)
                continue
            qid__oeevi = add_nested_counts(qid__oeevi, tze__pqc)
            for ivki__kcvk in range(len(tze__pqc)):
                ceeih__hrz = add_nested_counts(ceeih__hrz, qbn__zyowc)
        dol__yetx = bodo.utils.utils.alloc_type(qid__oeevi[0], wmy__ybk,
            qid__oeevi[1:])
        wnctl__nhcad = bodo.utils.utils.alloc_type(qid__oeevi[0], dop__sdy,
            ceeih__hrz)
        lsw__cqqsx = 0
        for i in range(n):
            if isna(arr, i):
                setna(dol__yetx, lsw__cqqsx)
                wnctl__nhcad[lsw__cqqsx] = index_arr[i]
                lsw__cqqsx += 1
                continue
            tze__pqc = arr[i]
            enwq__buma = len(tze__pqc)
            if enwq__buma == 0:
                setna(dol__yetx, lsw__cqqsx)
                wnctl__nhcad[lsw__cqqsx] = index_arr[i]
                lsw__cqqsx += 1
                continue
            dol__yetx[lsw__cqqsx:lsw__cqqsx + enwq__buma] = tze__pqc
            wnctl__nhcad[lsw__cqqsx:lsw__cqqsx + enwq__buma] = index_arr[i]
            lsw__cqqsx += enwq__buma
        return dol__yetx, wnctl__nhcad
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wmy__ybk = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        qid__oeevi = init_nested_counts(wmy__ybk)
        for i in range(n):
            if isna(arr, i):
                qid__oeevi = (qid__oeevi[0] + 1,) + qid__oeevi[1:]
                yfa__rkyut = 1
            else:
                tze__pqc = arr[i]
                qljmg__fkt = len(tze__pqc)
                if qljmg__fkt == 0:
                    qid__oeevi = (qid__oeevi[0] + 1,) + qid__oeevi[1:]
                    yfa__rkyut = 1
                    continue
                else:
                    qid__oeevi = add_nested_counts(qid__oeevi, tze__pqc)
                    yfa__rkyut = qljmg__fkt
            if counts[i] != yfa__rkyut:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        dol__yetx = bodo.utils.utils.alloc_type(qid__oeevi[0], wmy__ybk,
            qid__oeevi[1:])
        lsw__cqqsx = 0
        for i in range(n):
            if isna(arr, i):
                setna(dol__yetx, lsw__cqqsx)
                lsw__cqqsx += 1
                continue
            tze__pqc = arr[i]
            enwq__buma = len(tze__pqc)
            if enwq__buma == 0:
                setna(dol__yetx, lsw__cqqsx)
                lsw__cqqsx += 1
                continue
            dol__yetx[lsw__cqqsx:lsw__cqqsx + enwq__buma] = tze__pqc
            lsw__cqqsx += enwq__buma
        return dol__yetx
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(iwo__bzlts) for iwo__bzlts in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or arr == string_array_type and not na_empty_as_one
    if na_empty_as_one:
        dzib__gmqg = 'np.empty(n, np.int64)'
        ifzwn__gxzrd = 'out_arr[i] = 1'
        gnv__xin = 'max(len(arr[i]), 1)'
    else:
        dzib__gmqg = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        ifzwn__gxzrd = 'bodo.libs.array_kernels.setna(out_arr, i)'
        gnv__xin = 'len(arr[i])'
    obie__lhf = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {dzib__gmqg}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {ifzwn__gxzrd}
        else:
            out_arr[i] = {gnv__xin}
    return out_arr
    """
    zdkd__zndeg = {}
    exec(obie__lhf, {'bodo': bodo, 'numba': numba, 'np': np}, zdkd__zndeg)
    impl = zdkd__zndeg['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert arr == string_array_type
    dop__sdy = index_arr
    jxu__yqach = dop__sdy.dtype

    def impl(arr, pat, n, index_arr):
        ecnv__dslu = pat is not None and len(pat) > 1
        if ecnv__dslu:
            zdjpn__ojoj = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        adrqz__yzz = len(arr)
        yvci__ppuhv = 0
        bmahg__omwo = 0
        ceeih__hrz = init_nested_counts(jxu__yqach)
        for i in range(adrqz__yzz):
            qbn__zyowc = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                yvci__ppuhv += 1
                ceeih__hrz = add_nested_counts(ceeih__hrz, qbn__zyowc)
                continue
            if ecnv__dslu:
                jkpfa__uvgv = zdjpn__ojoj.split(arr[i], maxsplit=n)
            else:
                jkpfa__uvgv = arr[i].split(pat, n)
            yvci__ppuhv += len(jkpfa__uvgv)
            for s in jkpfa__uvgv:
                ceeih__hrz = add_nested_counts(ceeih__hrz, qbn__zyowc)
                bmahg__omwo += bodo.libs.str_arr_ext.get_utf8_size(s)
        dol__yetx = bodo.libs.str_arr_ext.pre_alloc_string_array(yvci__ppuhv,
            bmahg__omwo)
        wnctl__nhcad = bodo.utils.utils.alloc_type(yvci__ppuhv, dop__sdy,
            ceeih__hrz)
        yjq__ltil = 0
        for qwz__faa in range(adrqz__yzz):
            if isna(arr, qwz__faa):
                dol__yetx[yjq__ltil] = ''
                bodo.libs.array_kernels.setna(dol__yetx, yjq__ltil)
                wnctl__nhcad[yjq__ltil] = index_arr[qwz__faa]
                yjq__ltil += 1
                continue
            if ecnv__dslu:
                jkpfa__uvgv = zdjpn__ojoj.split(arr[qwz__faa], maxsplit=n)
            else:
                jkpfa__uvgv = arr[qwz__faa].split(pat, n)
            pclf__zkuj = len(jkpfa__uvgv)
            dol__yetx[yjq__ltil:yjq__ltil + pclf__zkuj] = jkpfa__uvgv
            wnctl__nhcad[yjq__ltil:yjq__ltil + pclf__zkuj] = index_arr[qwz__faa
                ]
            yjq__ltil += pclf__zkuj
        return dol__yetx, wnctl__nhcad
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if isinstance(dtype, (types.Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr):
            numba.parfors.parfor.init_prange()
            dol__yetx = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                dol__yetx[i] = np.nan
            return dol__yetx
        return impl_float

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        dol__yetx = bodo.utils.utils.alloc_type(n, arr, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(dol__yetx, i)
        return dol__yetx
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    lnia__pmkyq = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            dol__yetx = bodo.utils.utils.alloc_type(new_len, lnia__pmkyq)
            bodo.libs.str_arr_ext.str_copy_ptr(dol__yetx.ctypes, 0, A.
                ctypes, old_size)
            return dol__yetx
        return impl_char

    def impl(A, old_size, new_len):
        dol__yetx = bodo.utils.utils.alloc_type(new_len, lnia__pmkyq, (-1,))
        dol__yetx[:old_size] = A[:old_size]
        return dol__yetx
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    dlfe__kgssp = math.ceil((stop - start) / step)
    return int(max(dlfe__kgssp, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(blh__tpael, types.Complex) for blh__tpael in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            gjecq__olj = (stop - start) / step
            dlfe__kgssp = math.ceil(gjecq__olj.real)
            yumf__lhl = math.ceil(gjecq__olj.imag)
            efhnq__lcr = int(max(min(yumf__lhl, dlfe__kgssp), 0))
            arr = np.empty(efhnq__lcr, dtype)
            for i in numba.parfors.parfor.internal_prange(efhnq__lcr):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            efhnq__lcr = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(efhnq__lcr, dtype)
            for i in numba.parfors.parfor.internal_prange(efhnq__lcr):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        fnw__qzt = arr,
        if not inplace:
            fnw__qzt = arr.copy(),
        piccr__sxkmt = bodo.libs.str_arr_ext.to_list_if_immutable_arr(fnw__qzt)
        gaz__xikcn = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(piccr__sxkmt, 0, n, gaz__xikcn)
        if not ascending:
            bodo.libs.timsort.reverseRange(piccr__sxkmt, 0, n, gaz__xikcn)
        bodo.libs.str_arr_ext.cp_str_list_to_array(fnw__qzt, piccr__sxkmt)
        return fnw__qzt[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        nyib__ysh = []
        for i in range(n):
            if A[i]:
                nyib__ysh.append(i + offset)
        return np.array(nyib__ysh, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    lnia__pmkyq = element_type(A)
    if lnia__pmkyq == types.unicode_type:
        null_value = '""'
    elif lnia__pmkyq == types.bool_:
        null_value = 'False'
    elif lnia__pmkyq == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif lnia__pmkyq == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    yjq__ltil = 'i'
    acu__xhqs = False
    acwip__mrho = get_overload_const_str(method)
    if acwip__mrho in ('ffill', 'pad'):
        gndd__nclc = 'n'
        send_right = True
    elif acwip__mrho in ('backfill', 'bfill'):
        gndd__nclc = 'n-1, -1, -1'
        send_right = False
        if lnia__pmkyq == types.unicode_type:
            yjq__ltil = '(n - 1) - i'
            acu__xhqs = True
    obie__lhf = 'def impl(A, method, parallel=False):\n'
    obie__lhf += '  has_last_value = False\n'
    obie__lhf += f'  last_value = {null_value}\n'
    obie__lhf += '  if parallel:\n'
    obie__lhf += '    rank = bodo.libs.distributed_api.get_rank()\n'
    obie__lhf += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    obie__lhf += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    obie__lhf += '  n = len(A)\n'
    obie__lhf += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    obie__lhf += f'  for i in range({gndd__nclc}):\n'
    obie__lhf += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    obie__lhf += f'      bodo.libs.array_kernels.setna(out_arr, {yjq__ltil})\n'
    obie__lhf += '      continue\n'
    obie__lhf += '    s = A[i]\n'
    obie__lhf += '    if bodo.libs.array_kernels.isna(A, i):\n'
    obie__lhf += '      s = last_value\n'
    obie__lhf += f'    out_arr[{yjq__ltil}] = s\n'
    obie__lhf += '    last_value = s\n'
    obie__lhf += '    has_last_value = True\n'
    if acu__xhqs:
        obie__lhf += '  return out_arr[::-1]\n'
    else:
        obie__lhf += '  return out_arr\n'
    ttixz__oips = {}
    exec(obie__lhf, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm}, ttixz__oips)
    impl = ttixz__oips['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        egey__dfi = 0
        ghwq__wlnmx = n_pes - 1
        uje__dfdnx = np.int32(rank + 1)
        luf__wqcsh = np.int32(rank - 1)
        pkw__cflsi = len(in_arr) - 1
        iukai__naoov = -1
        ljxr__jlz = -1
    else:
        egey__dfi = n_pes - 1
        ghwq__wlnmx = 0
        uje__dfdnx = np.int32(rank - 1)
        luf__wqcsh = np.int32(rank + 1)
        pkw__cflsi = 0
        iukai__naoov = len(in_arr)
        ljxr__jlz = 1
    ixr__ajg = np.int32(bodo.hiframes.rolling.comm_border_tag)
    ecoe__hbqun = np.empty(1, dtype=np.bool_)
    eamv__qjsu = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    phv__ufajl = np.empty(1, dtype=np.bool_)
    xkmw__zvjp = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ovyu__ulvt = False
    jxkk__mjwa = null_value
    for i in range(pkw__cflsi, iukai__naoov, ljxr__jlz):
        if not isna(in_arr, i):
            ovyu__ulvt = True
            jxkk__mjwa = in_arr[i]
            break
    if rank != egey__dfi:
        exsne__vbl = bodo.libs.distributed_api.irecv(ecoe__hbqun, 1,
            luf__wqcsh, ixr__ajg, True)
        bodo.libs.distributed_api.wait(exsne__vbl, True)
        ttwt__czmhk = bodo.libs.distributed_api.irecv(eamv__qjsu, 1,
            luf__wqcsh, ixr__ajg, True)
        bodo.libs.distributed_api.wait(ttwt__czmhk, True)
        bkj__genxd = ecoe__hbqun[0]
        wtn__himhj = eamv__qjsu[0]
    else:
        bkj__genxd = False
        wtn__himhj = null_value
    if ovyu__ulvt:
        phv__ufajl[0] = ovyu__ulvt
        xkmw__zvjp[0] = jxkk__mjwa
    else:
        phv__ufajl[0] = bkj__genxd
        xkmw__zvjp[0] = wtn__himhj
    if rank != ghwq__wlnmx:
        tdy__tzr = bodo.libs.distributed_api.isend(phv__ufajl, 1,
            uje__dfdnx, ixr__ajg, True)
        hdb__mgv = bodo.libs.distributed_api.isend(xkmw__zvjp, 1,
            uje__dfdnx, ixr__ajg, True)
    return bkj__genxd, wtn__himhj


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    mxllo__flimz = {'axis': axis, 'kind': kind, 'order': order}
    wim__tcdw = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', mxllo__flimz, wim__tcdw, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    lnia__pmkyq = A
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            adrqz__yzz = len(A)
            dol__yetx = bodo.utils.utils.alloc_type(adrqz__yzz * repeats,
                lnia__pmkyq, (-1,))
            for i in range(adrqz__yzz):
                yjq__ltil = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for qwz__faa in range(repeats):
                        bodo.libs.array_kernels.setna(dol__yetx, yjq__ltil +
                            qwz__faa)
                else:
                    dol__yetx[yjq__ltil:yjq__ltil + repeats] = A[i]
            return dol__yetx
        return impl_int

    def impl_arr(A, repeats):
        adrqz__yzz = len(A)
        dol__yetx = bodo.utils.utils.alloc_type(repeats.sum(), lnia__pmkyq,
            (-1,))
        yjq__ltil = 0
        for i in range(adrqz__yzz):
            ouqg__uoj = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for qwz__faa in range(ouqg__uoj):
                    bodo.libs.array_kernels.setna(dol__yetx, yjq__ltil +
                        qwz__faa)
            else:
                dol__yetx[yjq__ltil:yjq__ltil + ouqg__uoj] = A[i]
            yjq__ltil += ouqg__uoj
        return dol__yetx
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        vgcs__sustk = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(vgcs__sustk, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        pqfi__jwgtp = bodo.libs.array_kernels.concat([A1, A2])
        lopp__alwwq = bodo.libs.array_kernels.unique(pqfi__jwgtp)
        return pd.Series(lopp__alwwq).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    mxllo__flimz = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    wim__tcdw = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', mxllo__flimz, wim__tcdw, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        gxsj__zyndj = bodo.libs.array_kernels.unique(A1)
        fveq__jnjh = bodo.libs.array_kernels.unique(A2)
        pqfi__jwgtp = bodo.libs.array_kernels.concat([gxsj__zyndj, fveq__jnjh])
        cfih__jsx = pd.Series(pqfi__jwgtp).sort_values().values
        return slice_array_intersect1d(cfih__jsx)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    wnm__oeqkp = arr[1:] == arr[:-1]
    return arr[:-1][wnm__oeqkp]


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    mxllo__flimz = {'assume_unique': assume_unique}
    wim__tcdw = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', mxllo__flimz, wim__tcdw, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        gxsj__zyndj = bodo.libs.array_kernels.unique(A1)
        fveq__jnjh = bodo.libs.array_kernels.unique(A2)
        wnm__oeqkp = calculate_mask_setdiff1d(gxsj__zyndj, fveq__jnjh)
        return pd.Series(gxsj__zyndj[wnm__oeqkp]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    wnm__oeqkp = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        wnm__oeqkp &= A1 != A2[i]
    return wnm__oeqkp


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    mxllo__flimz = {'retstep': retstep, 'axis': axis}
    wim__tcdw = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', mxllo__flimz, wim__tcdw, 'numpy')
    yaioq__ymy = False
    if is_overload_none(dtype):
        lnia__pmkyq = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            yaioq__ymy = True
        lnia__pmkyq = numba.np.numpy_support.as_dtype(dtype).type
    if yaioq__ymy:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            bpl__ujdfd = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            dol__yetx = np.empty(num, lnia__pmkyq)
            for i in numba.parfors.parfor.internal_prange(num):
                dol__yetx[i] = lnia__pmkyq(np.floor(start + i * bpl__ujdfd))
            return dol__yetx
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            bpl__ujdfd = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            dol__yetx = np.empty(num, lnia__pmkyq)
            for i in numba.parfors.parfor.internal_prange(num):
                dol__yetx[i] = lnia__pmkyq(start + i * bpl__ujdfd)
            return dol__yetx
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        rcwn__hex = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                rcwn__hex += A[i] == val
        return rcwn__hex > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    mxllo__flimz = {'axis': axis, 'out': out, 'keepdims': keepdims}
    wim__tcdw = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', mxllo__flimz, wim__tcdw, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        rcwn__hex = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                rcwn__hex += int(bool(A[i]))
        return rcwn__hex > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    mxllo__flimz = {'axis': axis, 'out': out, 'keepdims': keepdims}
    wim__tcdw = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', mxllo__flimz, wim__tcdw, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        rcwn__hex = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                rcwn__hex += int(bool(A[i]))
        return rcwn__hex == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    mxllo__flimz = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    wim__tcdw = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', mxllo__flimz, wim__tcdw, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        drgsc__xmhqb = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            dol__yetx = np.empty(n, drgsc__xmhqb)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(dol__yetx, i)
                    continue
                dol__yetx[i] = np_cbrt_scalar(A[i], drgsc__xmhqb)
            return dol__yetx
        return impl_arr
    drgsc__xmhqb = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, drgsc__xmhqb)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    cvkt__ksqb = x < 0
    if cvkt__ksqb:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if cvkt__ksqb:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    sheo__qorr = isinstance(tup, (types.BaseTuple, types.List))
    bdxu__lpmxi = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for cgo__ppb in tup.types:
            sheo__qorr = sheo__qorr and bodo.utils.utils.is_array_typ(cgo__ppb,
                False)
    elif isinstance(tup, types.List):
        sheo__qorr = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif bdxu__lpmxi:
        dfbuh__xrlmn = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for cgo__ppb in dfbuh__xrlmn.types:
            bdxu__lpmxi = bdxu__lpmxi and bodo.utils.utils.is_array_typ(
                cgo__ppb, False)
    if not (sheo__qorr or bdxu__lpmxi):
        return
    if bdxu__lpmxi:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    mxllo__flimz = {'check_valid': check_valid, 'tol': tol}
    wim__tcdw = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', mxllo__flimz,
        wim__tcdw, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        nty__pphm = mean.shape[0]
        spv__buttz = size, nty__pphm
        tfs__shb = np.random.standard_normal(spv__buttz)
        cov = cov.astype(np.float64)
        uwfs__tbqed, s, txyi__bnu = np.linalg.svd(cov)
        res = np.dot(tfs__shb, np.sqrt(s).reshape(nty__pphm, 1) * txyi__bnu)
        unky__hkpen = res + mean
        return unky__hkpen
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            zwfh__zjv = bodo.hiframes.series_kernels._get_type_max_value(arr)
            pzol__cgeh = typing.builtins.IndexValue(-1, zwfh__zjv)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mmj__zdlu = typing.builtins.IndexValue(i, arr[i])
                pzol__cgeh = min(pzol__cgeh, mmj__zdlu)
            return pzol__cgeh.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        vmmx__blc = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            gbpd__rtu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            zwfh__zjv = vmmx__blc(len(arr.dtype.categories) + 1)
            pzol__cgeh = typing.builtins.IndexValue(-1, zwfh__zjv)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mmj__zdlu = typing.builtins.IndexValue(i, gbpd__rtu[i])
                pzol__cgeh = min(pzol__cgeh, mmj__zdlu)
            return pzol__cgeh.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            zwfh__zjv = bodo.hiframes.series_kernels._get_type_min_value(arr)
            pzol__cgeh = typing.builtins.IndexValue(-1, zwfh__zjv)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mmj__zdlu = typing.builtins.IndexValue(i, arr[i])
                pzol__cgeh = max(pzol__cgeh, mmj__zdlu)
            return pzol__cgeh.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        vmmx__blc = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            gbpd__rtu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            zwfh__zjv = vmmx__blc(-1)
            pzol__cgeh = typing.builtins.IndexValue(-1, zwfh__zjv)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mmj__zdlu = typing.builtins.IndexValue(i, gbpd__rtu[i])
                pzol__cgeh = max(pzol__cgeh, mmj__zdlu)
            return pzol__cgeh.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
