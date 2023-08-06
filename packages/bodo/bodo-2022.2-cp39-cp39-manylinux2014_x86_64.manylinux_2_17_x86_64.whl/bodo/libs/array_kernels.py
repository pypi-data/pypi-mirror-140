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
        tytp__wlh = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = tytp__wlh
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
            nget__rie = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            nget__rie[ind + 1] = nget__rie[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            nget__rie = bodo.libs.array_item_arr_ext.get_offsets(arr)
            nget__rie[ind + 1] = nget__rie[ind]
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
    gts__iwprf = arr_tup.count
    iagx__akx = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(gts__iwprf):
        iagx__akx += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    iagx__akx += '  return\n'
    qpkg__ugvi = {}
    exec(iagx__akx, {'setna': setna}, qpkg__ugvi)
    impl = qpkg__ugvi['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        mtclm__lbq = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(mtclm__lbq.start, mtclm__lbq.stop, mtclm__lbq.step):
            setna(arr, i)
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    ffef__wgk = array_to_info(arr)
    _median_series_computation(res, ffef__wgk, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ffef__wgk)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    ffef__wgk = array_to_info(arr)
    _autocorr_series_computation(res, ffef__wgk, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ffef__wgk)


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
    ffef__wgk = array_to_info(arr)
    _compute_series_monotonicity(res, ffef__wgk, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(ffef__wgk)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    guzkm__unf = res[0] > 0.5
    return guzkm__unf


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        qign__ubm = '-'
        avgb__gudwi = 'index_arr[0] > threshhold_date'
        vygua__pxejl = '1, n+1'
        jyfyt__sbu = 'index_arr[-i] <= threshhold_date'
        vhln__rtlny = 'i - 1'
    else:
        qign__ubm = '+'
        avgb__gudwi = 'index_arr[-1] < threshhold_date'
        vygua__pxejl = 'n'
        jyfyt__sbu = 'index_arr[i] >= threshhold_date'
        vhln__rtlny = 'i'
    iagx__akx = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        iagx__akx += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        iagx__akx += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            iagx__akx += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            iagx__akx += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            iagx__akx += '    else:\n'
            iagx__akx += '      threshhold_date = initial_date + date_offset\n'
        else:
            iagx__akx += (
                f'    threshhold_date = initial_date {qign__ubm} date_offset\n'
                )
    else:
        iagx__akx += f'  threshhold_date = initial_date {qign__ubm} offset\n'
    iagx__akx += '  local_valid = 0\n'
    iagx__akx += f'  n = len(index_arr)\n'
    iagx__akx += f'  if n:\n'
    iagx__akx += f'    if {avgb__gudwi}:\n'
    iagx__akx += '      loc_valid = n\n'
    iagx__akx += '    else:\n'
    iagx__akx += f'      for i in range({vygua__pxejl}):\n'
    iagx__akx += f'        if {jyfyt__sbu}:\n'
    iagx__akx += f'          loc_valid = {vhln__rtlny}\n'
    iagx__akx += '          break\n'
    iagx__akx += '  if is_parallel:\n'
    iagx__akx += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    iagx__akx += '    return total_valid\n'
    iagx__akx += '  else:\n'
    iagx__akx += '    return loc_valid\n'
    qpkg__ugvi = {}
    exec(iagx__akx, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, qpkg__ugvi)
    return qpkg__ugvi['impl']


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
    ann__smez = numba_to_c_type(sig.args[0].dtype)
    errwh__cspzn = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), ann__smez))
    vemv__swri = args[0]
    qkbz__nmby = sig.args[0]
    if isinstance(qkbz__nmby, (IntegerArrayType, BooleanArrayType)):
        vemv__swri = cgutils.create_struct_proxy(qkbz__nmby)(context,
            builder, vemv__swri).data
        qkbz__nmby = types.Array(qkbz__nmby.dtype, 1, 'C')
    assert qkbz__nmby.ndim == 1
    arr = make_array(qkbz__nmby)(context, builder, vemv__swri)
    ddr__vdvu = builder.extract_value(arr.shape, 0)
    mvfl__ymh = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ddr__vdvu, args[1], builder.load(errwh__cspzn)]
    del__ftn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    fjuiy__ntyqn = lir.FunctionType(lir.DoubleType(), del__ftn)
    kmank__hme = cgutils.get_or_insert_function(builder.module,
        fjuiy__ntyqn, name='quantile_sequential')
    ayj__ewsm = builder.call(kmank__hme, mvfl__ymh)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return ayj__ewsm


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    ann__smez = numba_to_c_type(sig.args[0].dtype)
    errwh__cspzn = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), ann__smez))
    vemv__swri = args[0]
    qkbz__nmby = sig.args[0]
    if isinstance(qkbz__nmby, (IntegerArrayType, BooleanArrayType)):
        vemv__swri = cgutils.create_struct_proxy(qkbz__nmby)(context,
            builder, vemv__swri).data
        qkbz__nmby = types.Array(qkbz__nmby.dtype, 1, 'C')
    assert qkbz__nmby.ndim == 1
    arr = make_array(qkbz__nmby)(context, builder, vemv__swri)
    ddr__vdvu = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        houif__surk = args[2]
    else:
        houif__surk = ddr__vdvu
    mvfl__ymh = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ddr__vdvu, houif__surk, args[1], builder.load(errwh__cspzn)]
    del__ftn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    fjuiy__ntyqn = lir.FunctionType(lir.DoubleType(), del__ftn)
    kmank__hme = cgutils.get_or_insert_function(builder.module,
        fjuiy__ntyqn, name='quantile_parallel')
    ayj__ewsm = builder.call(kmank__hme, mvfl__ymh)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return ayj__ewsm


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    tyjn__umm = start
    wxymr__lib = 2 * start + 1
    inso__hdxd = 2 * start + 2
    if wxymr__lib < n and not cmp_f(arr[wxymr__lib], arr[tyjn__umm]):
        tyjn__umm = wxymr__lib
    if inso__hdxd < n and not cmp_f(arr[inso__hdxd], arr[tyjn__umm]):
        tyjn__umm = inso__hdxd
    if tyjn__umm != start:
        arr[start], arr[tyjn__umm] = arr[tyjn__umm], arr[start]
        ind_arr[start], ind_arr[tyjn__umm] = ind_arr[tyjn__umm], ind_arr[start]
        min_heapify(arr, ind_arr, n, tyjn__umm, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        ktan__zugj = np.empty(k, A.dtype)
        elh__tlpu = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                ktan__zugj[ind] = A[i]
                elh__tlpu[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            ktan__zugj = ktan__zugj[:ind]
            elh__tlpu = elh__tlpu[:ind]
        return ktan__zugj, elh__tlpu, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        lgbah__vjh = np.sort(A)
        rtpzr__nemey = index_arr[np.argsort(A)]
        eydpi__owrh = pd.Series(lgbah__vjh).notna().values
        lgbah__vjh = lgbah__vjh[eydpi__owrh]
        rtpzr__nemey = rtpzr__nemey[eydpi__owrh]
        if is_largest:
            lgbah__vjh = lgbah__vjh[::-1]
            rtpzr__nemey = rtpzr__nemey[::-1]
        return np.ascontiguousarray(lgbah__vjh), np.ascontiguousarray(
            rtpzr__nemey)
    ktan__zugj, elh__tlpu, start = select_k_nonan(A, index_arr, m, k)
    elh__tlpu = elh__tlpu[ktan__zugj.argsort()]
    ktan__zugj.sort()
    if not is_largest:
        ktan__zugj = np.ascontiguousarray(ktan__zugj[::-1])
        elh__tlpu = np.ascontiguousarray(elh__tlpu[::-1])
    for i in range(start, m):
        if cmp_f(A[i], ktan__zugj[0]):
            ktan__zugj[0] = A[i]
            elh__tlpu[0] = index_arr[i]
            min_heapify(ktan__zugj, elh__tlpu, k, 0, cmp_f)
    elh__tlpu = elh__tlpu[ktan__zugj.argsort()]
    ktan__zugj.sort()
    if is_largest:
        ktan__zugj = ktan__zugj[::-1]
        elh__tlpu = elh__tlpu[::-1]
    return np.ascontiguousarray(ktan__zugj), np.ascontiguousarray(elh__tlpu)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    ycn__khaof = bodo.libs.distributed_api.get_rank()
    qxbfm__ocv, rakf__fxa = nlargest(A, I, k, is_largest, cmp_f)
    nhrds__tpa = bodo.libs.distributed_api.gatherv(qxbfm__ocv)
    qdpvh__bmgsb = bodo.libs.distributed_api.gatherv(rakf__fxa)
    if ycn__khaof == MPI_ROOT:
        res, zvtx__jzrei = nlargest(nhrds__tpa, qdpvh__bmgsb, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        zvtx__jzrei = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(zvtx__jzrei)
    return res, zvtx__jzrei


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    aojk__aseta, drs__lueo = mat.shape
    tcf__jjnr = np.empty((drs__lueo, drs__lueo), dtype=np.float64)
    for ssmbc__ush in range(drs__lueo):
        for pzgcp__hlyvf in range(ssmbc__ush + 1):
            uam__hltq = 0
            yfum__krxw = lcwwa__tujw = qgdb__ukwzr = mhe__kwjzy = 0.0
            for i in range(aojk__aseta):
                if np.isfinite(mat[i, ssmbc__ush]) and np.isfinite(mat[i,
                    pzgcp__hlyvf]):
                    ihgm__pmfl = mat[i, ssmbc__ush]
                    ohcx__ahegn = mat[i, pzgcp__hlyvf]
                    uam__hltq += 1
                    qgdb__ukwzr += ihgm__pmfl
                    mhe__kwjzy += ohcx__ahegn
            if parallel:
                uam__hltq = bodo.libs.distributed_api.dist_reduce(uam__hltq,
                    sum_op)
                qgdb__ukwzr = bodo.libs.distributed_api.dist_reduce(qgdb__ukwzr
                    , sum_op)
                mhe__kwjzy = bodo.libs.distributed_api.dist_reduce(mhe__kwjzy,
                    sum_op)
            if uam__hltq < minpv:
                tcf__jjnr[ssmbc__ush, pzgcp__hlyvf] = tcf__jjnr[
                    pzgcp__hlyvf, ssmbc__ush] = np.nan
            else:
                iskr__mlv = qgdb__ukwzr / uam__hltq
                cvgw__zbd = mhe__kwjzy / uam__hltq
                qgdb__ukwzr = 0.0
                for i in range(aojk__aseta):
                    if np.isfinite(mat[i, ssmbc__ush]) and np.isfinite(mat[
                        i, pzgcp__hlyvf]):
                        ihgm__pmfl = mat[i, ssmbc__ush] - iskr__mlv
                        ohcx__ahegn = mat[i, pzgcp__hlyvf] - cvgw__zbd
                        qgdb__ukwzr += ihgm__pmfl * ohcx__ahegn
                        yfum__krxw += ihgm__pmfl * ihgm__pmfl
                        lcwwa__tujw += ohcx__ahegn * ohcx__ahegn
                if parallel:
                    qgdb__ukwzr = bodo.libs.distributed_api.dist_reduce(
                        qgdb__ukwzr, sum_op)
                    yfum__krxw = bodo.libs.distributed_api.dist_reduce(
                        yfum__krxw, sum_op)
                    lcwwa__tujw = bodo.libs.distributed_api.dist_reduce(
                        lcwwa__tujw, sum_op)
                vxn__mchn = uam__hltq - 1.0 if cov else sqrt(yfum__krxw *
                    lcwwa__tujw)
                if vxn__mchn != 0.0:
                    tcf__jjnr[ssmbc__ush, pzgcp__hlyvf] = tcf__jjnr[
                        pzgcp__hlyvf, ssmbc__ush] = qgdb__ukwzr / vxn__mchn
                else:
                    tcf__jjnr[ssmbc__ush, pzgcp__hlyvf] = tcf__jjnr[
                        pzgcp__hlyvf, ssmbc__ush] = np.nan
    return tcf__jjnr


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    eizld__ryu = n != 1
    iagx__akx = 'def impl(data, parallel=False):\n'
    iagx__akx += '  if parallel:\n'
    fzvy__upie = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    iagx__akx += f'    cpp_table = arr_info_list_to_table([{fzvy__upie}])\n'
    iagx__akx += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    yqnxa__bejbn = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    iagx__akx += f'    data = ({yqnxa__bejbn},)\n'
    iagx__akx += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    iagx__akx += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    iagx__akx += '    bodo.libs.array.delete_table(cpp_table)\n'
    iagx__akx += (
        '  data = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data)\n')
    iagx__akx += '  n = len(data[0])\n'
    iagx__akx += '  out = np.empty(n, np.bool_)\n'
    iagx__akx += '  uniqs = dict()\n'
    if eizld__ryu:
        iagx__akx += '  for i in range(n):\n'
        pzhol__oyrqq = ', '.join(f'data[{i}][i]' for i in range(n))
        exusg__oib = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        iagx__akx += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({pzhol__oyrqq},), ({exusg__oib},))
"""
        iagx__akx += '    if val in uniqs:\n'
        iagx__akx += '      out[i] = True\n'
        iagx__akx += '    else:\n'
        iagx__akx += '      out[i] = False\n'
        iagx__akx += '      uniqs[val] = 0\n'
    else:
        iagx__akx += '  data = data[0]\n'
        iagx__akx += '  hasna = False\n'
        iagx__akx += '  for i in range(n):\n'
        iagx__akx += '    if bodo.libs.array_kernels.isna(data, i):\n'
        iagx__akx += '      out[i] = hasna\n'
        iagx__akx += '      hasna = True\n'
        iagx__akx += '    else:\n'
        iagx__akx += '      val = data[i]\n'
        iagx__akx += '      if val in uniqs:\n'
        iagx__akx += '        out[i] = True\n'
        iagx__akx += '      else:\n'
        iagx__akx += '        out[i] = False\n'
        iagx__akx += '        uniqs[val] = 0\n'
    iagx__akx += '  if parallel:\n'
    iagx__akx += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    iagx__akx += '  return out\n'
    qpkg__ugvi = {}
    exec(iagx__akx, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, qpkg__ugvi)
    impl = qpkg__ugvi['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    gts__iwprf = len(data)
    iagx__akx = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    iagx__akx += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        gts__iwprf)))
    iagx__akx += '  table_total = arr_info_list_to_table(info_list_total)\n'
    iagx__akx += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(gts__iwprf))
    for xbbt__jcv in range(gts__iwprf):
        iagx__akx += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xbbt__jcv, xbbt__jcv, xbbt__jcv))
    iagx__akx += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(gts__iwprf))
    iagx__akx += '  delete_table(out_table)\n'
    iagx__akx += '  delete_table(table_total)\n'
    iagx__akx += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(gts__iwprf)))
    qpkg__ugvi = {}
    exec(iagx__akx, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, qpkg__ugvi)
    impl = qpkg__ugvi['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    gts__iwprf = len(data)
    iagx__akx = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    iagx__akx += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        gts__iwprf)))
    iagx__akx += '  table_total = arr_info_list_to_table(info_list_total)\n'
    iagx__akx += '  keep_i = 0\n'
    iagx__akx += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False)
"""
    for xbbt__jcv in range(gts__iwprf):
        iagx__akx += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xbbt__jcv, xbbt__jcv, xbbt__jcv))
    iagx__akx += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(gts__iwprf))
    iagx__akx += '  delete_table(out_table)\n'
    iagx__akx += '  delete_table(table_total)\n'
    iagx__akx += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(gts__iwprf)))
    qpkg__ugvi = {}
    exec(iagx__akx, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, qpkg__ugvi)
    impl = qpkg__ugvi['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        fznyn__icjhc = [array_to_info(data_arr)]
        utll__hshl = arr_info_list_to_table(fznyn__icjhc)
        zjcc__spnon = 0
        szzo__unps = drop_duplicates_table(utll__hshl, parallel, 1,
            zjcc__spnon, False)
        nwm__kthje = info_to_array(info_from_table(szzo__unps, 0), data_arr)
        delete_table(szzo__unps)
        delete_table(utll__hshl)
        return nwm__kthje
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    ompzd__gexs = len(data.types)
    gnxyp__dlnoq = [('out' + str(i)) for i in range(ompzd__gexs)]
    npvi__ncmnv = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    xlb__jyf = ['isna(data[{}], i)'.format(i) for i in npvi__ncmnv]
    hktd__tmp = 'not ({})'.format(' or '.join(xlb__jyf))
    if not is_overload_none(thresh):
        hktd__tmp = '(({}) <= ({}) - thresh)'.format(' + '.join(xlb__jyf), 
            ompzd__gexs - 1)
    elif how == 'all':
        hktd__tmp = 'not ({})'.format(' and '.join(xlb__jyf))
    iagx__akx = 'def _dropna_imp(data, how, thresh, subset):\n'
    iagx__akx += '  old_len = len(data[0])\n'
    iagx__akx += '  new_len = 0\n'
    iagx__akx += '  for i in range(old_len):\n'
    iagx__akx += '    if {}:\n'.format(hktd__tmp)
    iagx__akx += '      new_len += 1\n'
    for i, out in enumerate(gnxyp__dlnoq):
        if isinstance(data[i], bodo.CategoricalArrayType):
            iagx__akx += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            iagx__akx += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    iagx__akx += '  curr_ind = 0\n'
    iagx__akx += '  for i in range(old_len):\n'
    iagx__akx += '    if {}:\n'.format(hktd__tmp)
    for i in range(ompzd__gexs):
        iagx__akx += '      if isna(data[{}], i):\n'.format(i)
        iagx__akx += '        setna({}, curr_ind)\n'.format(gnxyp__dlnoq[i])
        iagx__akx += '      else:\n'
        iagx__akx += '        {}[curr_ind] = data[{}][i]\n'.format(gnxyp__dlnoq
            [i], i)
    iagx__akx += '      curr_ind += 1\n'
    iagx__akx += '  return {}\n'.format(', '.join(gnxyp__dlnoq))
    qpkg__ugvi = {}
    ihyf__ntlyg = {'t{}'.format(i): tsmg__jfpx for i, tsmg__jfpx in
        enumerate(data.types)}
    ihyf__ntlyg.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(iagx__akx, ihyf__ntlyg, qpkg__ugvi)
    frk__mwksa = qpkg__ugvi['_dropna_imp']
    return frk__mwksa


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        qkbz__nmby = arr.dtype
        len__ejr = qkbz__nmby.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            rvnwx__ikhlf = init_nested_counts(len__ejr)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                rvnwx__ikhlf = add_nested_counts(rvnwx__ikhlf, val[ind])
            nwm__kthje = bodo.utils.utils.alloc_type(n, qkbz__nmby,
                rvnwx__ikhlf)
            for zll__spj in range(n):
                if bodo.libs.array_kernels.isna(arr, zll__spj):
                    setna(nwm__kthje, zll__spj)
                    continue
                val = arr[zll__spj]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(nwm__kthje, zll__spj)
                    continue
                nwm__kthje[zll__spj] = val[ind]
            return nwm__kthje
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    uthx__kgerd = _to_readonly(arr_types.types[0])
    return all(isinstance(tsmg__jfpx, CategoricalArrayType) and 
        _to_readonly(tsmg__jfpx) == uthx__kgerd for tsmg__jfpx in arr_types
        .types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        kyvwg__zlmgu = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            xhdv__ewyu = 0
            xfkgn__mbmxe = []
            for A in arr_list:
                eit__nxkye = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                xfkgn__mbmxe.append(bodo.libs.array_item_arr_ext.get_data(A))
                xhdv__ewyu += eit__nxkye
            zctbl__xavqa = np.empty(xhdv__ewyu + 1, offset_type)
            ucg__jcu = bodo.libs.array_kernels.concat(xfkgn__mbmxe)
            ygq__dya = np.empty(xhdv__ewyu + 7 >> 3, np.uint8)
            foj__zxnj = 0
            aylsi__zsgss = 0
            for A in arr_list:
                xxawe__ehi = bodo.libs.array_item_arr_ext.get_offsets(A)
                eji__emuey = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                eit__nxkye = len(A)
                ntpjq__tcbrm = xxawe__ehi[eit__nxkye]
                for i in range(eit__nxkye):
                    zctbl__xavqa[i + foj__zxnj] = xxawe__ehi[i] + aylsi__zsgss
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        eji__emuey, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ygq__dya, i +
                        foj__zxnj, oev__hdd)
                foj__zxnj += eit__nxkye
                aylsi__zsgss += ntpjq__tcbrm
            zctbl__xavqa[foj__zxnj] = aylsi__zsgss
            nwm__kthje = bodo.libs.array_item_arr_ext.init_array_item_array(
                xhdv__ewyu, ucg__jcu, zctbl__xavqa, ygq__dya)
            return nwm__kthje
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        oyd__fhiyu = arr_list.dtype.names
        iagx__akx = 'def struct_array_concat_impl(arr_list):\n'
        iagx__akx += f'    n_all = 0\n'
        for i in range(len(oyd__fhiyu)):
            iagx__akx += f'    concat_list{i} = []\n'
        iagx__akx += '    for A in arr_list:\n'
        iagx__akx += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(oyd__fhiyu)):
            iagx__akx += f'        concat_list{i}.append(data_tuple[{i}])\n'
        iagx__akx += '        n_all += len(A)\n'
        iagx__akx += '    n_bytes = (n_all + 7) >> 3\n'
        iagx__akx += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        iagx__akx += '    curr_bit = 0\n'
        iagx__akx += '    for A in arr_list:\n'
        iagx__akx += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        iagx__akx += '        for j in range(len(A)):\n'
        iagx__akx += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        iagx__akx += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        iagx__akx += '            curr_bit += 1\n'
        iagx__akx += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        yfj__utgj = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(oyd__fhiyu))])
        iagx__akx += f'        ({yfj__utgj},),\n'
        iagx__akx += '        new_mask,\n'
        iagx__akx += f'        {oyd__fhiyu},\n'
        iagx__akx += '    )\n'
        qpkg__ugvi = {}
        exec(iagx__akx, {'bodo': bodo, 'np': np}, qpkg__ugvi)
        return qpkg__ugvi['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            ggs__hqmd = 0
            for A in arr_list:
                ggs__hqmd += len(A)
            lgfmc__ehptk = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(ggs__hqmd))
            hkk__ezpf = 0
            for A in arr_list:
                for i in range(len(A)):
                    lgfmc__ehptk._data[i + hkk__ezpf] = A._data[i]
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lgfmc__ehptk.
                        _null_bitmap, i + hkk__ezpf, oev__hdd)
                hkk__ezpf += len(A)
            return lgfmc__ehptk
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            ggs__hqmd = 0
            for A in arr_list:
                ggs__hqmd += len(A)
            lgfmc__ehptk = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(ggs__hqmd))
            hkk__ezpf = 0
            for A in arr_list:
                for i in range(len(A)):
                    lgfmc__ehptk._days_data[i + hkk__ezpf] = A._days_data[i]
                    lgfmc__ehptk._seconds_data[i + hkk__ezpf
                        ] = A._seconds_data[i]
                    lgfmc__ehptk._microseconds_data[i + hkk__ezpf
                        ] = A._microseconds_data[i]
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lgfmc__ehptk.
                        _null_bitmap, i + hkk__ezpf, oev__hdd)
                hkk__ezpf += len(A)
            return lgfmc__ehptk
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        uio__afet = arr_list.dtype.precision
        ocewd__naa = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            ggs__hqmd = 0
            for A in arr_list:
                ggs__hqmd += len(A)
            lgfmc__ehptk = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                ggs__hqmd, uio__afet, ocewd__naa)
            hkk__ezpf = 0
            for A in arr_list:
                for i in range(len(A)):
                    lgfmc__ehptk._data[i + hkk__ezpf] = A._data[i]
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lgfmc__ehptk.
                        _null_bitmap, i + hkk__ezpf, oev__hdd)
                hkk__ezpf += len(A)
            return lgfmc__ehptk
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype in [string_array_type, bodo.binary_array_type]:
        if arr_list.dtype == bodo.binary_array_type:
            gfj__xdqb = 'bodo.libs.str_arr_ext.pre_alloc_binary_array'
        elif arr_list.dtype == string_array_type:
            gfj__xdqb = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        iagx__akx = 'def impl(arr_list):  # pragma: no cover\n'
        iagx__akx += '    # preallocate the output\n'
        iagx__akx += '    num_strs = 0\n'
        iagx__akx += '    num_chars = 0\n'
        iagx__akx += '    for A in arr_list:\n'
        iagx__akx += '        arr = A\n'
        iagx__akx += '        num_strs += len(arr)\n'
        iagx__akx += '        # this should work for both binary and string\n'
        iagx__akx += (
            '        num_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        iagx__akx += f'    out_arr = {gfj__xdqb}(\n'
        iagx__akx += '        num_strs, num_chars\n'
        iagx__akx += '    )\n'
        iagx__akx += (
            '    bodo.libs.str_arr_ext.set_null_bits_to_value(out_arr, -1)\n')
        iagx__akx += '    # copy data to output\n'
        iagx__akx += '    curr_str_ind = 0\n'
        iagx__akx += '    curr_chars_ind = 0\n'
        iagx__akx += '    for A in arr_list:\n'
        iagx__akx += '        arr = A\n'
        iagx__akx += '        # This will probably need to be extended\n'
        iagx__akx += '        bodo.libs.str_arr_ext.set_string_array_range(\n'
        iagx__akx += '            out_arr, arr, curr_str_ind, curr_chars_ind\n'
        iagx__akx += '        )\n'
        iagx__akx += '        curr_str_ind += len(arr)\n'
        iagx__akx += '        # this should work for both binary and string\n'
        iagx__akx += (
            '        curr_chars_ind += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        iagx__akx += '    return out_arr\n'
        arews__gwc = dict()
        exec(iagx__akx, {'bodo': bodo}, arews__gwc)
        noomk__mccb = arews__gwc['impl']
        return noomk__mccb
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(tsmg__jfpx.dtype, types.Integer) for
        tsmg__jfpx in arr_list.types) and any(isinstance(tsmg__jfpx,
        IntegerArrayType) for tsmg__jfpx in arr_list.types):

        def impl_int_arr_list(arr_list):
            kst__kmry = convert_to_nullable_tup(arr_list)
            pxfed__zzan = []
            bhk__fpbrg = 0
            for A in kst__kmry:
                pxfed__zzan.append(A._data)
                bhk__fpbrg += len(A)
            ucg__jcu = bodo.libs.array_kernels.concat(pxfed__zzan)
            ackbn__ebdmx = bhk__fpbrg + 7 >> 3
            ayqm__kyaq = np.empty(ackbn__ebdmx, np.uint8)
            aaerj__izpi = 0
            for A in kst__kmry:
                yqboo__pxc = A._null_bitmap
                for zll__spj in range(len(A)):
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        yqboo__pxc, zll__spj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ayqm__kyaq,
                        aaerj__izpi, oev__hdd)
                    aaerj__izpi += 1
            return bodo.libs.int_arr_ext.init_integer_array(ucg__jcu,
                ayqm__kyaq)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(tsmg__jfpx.dtype == types.bool_ for tsmg__jfpx in
        arr_list.types) and any(tsmg__jfpx == boolean_array for tsmg__jfpx in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            kst__kmry = convert_to_nullable_tup(arr_list)
            pxfed__zzan = []
            bhk__fpbrg = 0
            for A in kst__kmry:
                pxfed__zzan.append(A._data)
                bhk__fpbrg += len(A)
            ucg__jcu = bodo.libs.array_kernels.concat(pxfed__zzan)
            ackbn__ebdmx = bhk__fpbrg + 7 >> 3
            ayqm__kyaq = np.empty(ackbn__ebdmx, np.uint8)
            aaerj__izpi = 0
            for A in kst__kmry:
                yqboo__pxc = A._null_bitmap
                for zll__spj in range(len(A)):
                    oev__hdd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        yqboo__pxc, zll__spj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ayqm__kyaq,
                        aaerj__izpi, oev__hdd)
                    aaerj__izpi += 1
            return bodo.libs.bool_arr_ext.init_bool_array(ucg__jcu, ayqm__kyaq)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            ouvtc__rho = []
            for A in arr_list:
                ouvtc__rho.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                ouvtc__rho), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        vjfw__lfr = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        iagx__akx = 'def impl(arr_list):\n'
        iagx__akx += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({vjfw__lfr},)), arr_list[0].dtype)
"""
        arews__gwc = {}
        exec(iagx__akx, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, arews__gwc)
        return arews__gwc['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            bhk__fpbrg = 0
            for A in arr_list:
                bhk__fpbrg += len(A)
            nwm__kthje = np.empty(bhk__fpbrg, dtype)
            grb__sxxlh = 0
            for A in arr_list:
                n = len(A)
                nwm__kthje[grb__sxxlh:grb__sxxlh + n] = A
                grb__sxxlh += n
            return nwm__kthje
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(tsmg__jfpx,
        (types.Array, IntegerArrayType)) and isinstance(tsmg__jfpx.dtype,
        types.Integer) for tsmg__jfpx in arr_list.types) and any(isinstance
        (tsmg__jfpx, types.Array) and isinstance(tsmg__jfpx.dtype, types.
        Float) for tsmg__jfpx in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            jywm__cjnnc = []
            for A in arr_list:
                jywm__cjnnc.append(A._data)
            xkjs__qifir = bodo.libs.array_kernels.concat(jywm__cjnnc)
            tcf__jjnr = bodo.libs.map_arr_ext.init_map_arr(xkjs__qifir)
            return tcf__jjnr
        return impl_map_arr_list
    for xelyr__dhqes in arr_list:
        if not isinstance(xelyr__dhqes, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(tsmg__jfpx.astype(np.float64) for tsmg__jfpx in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    gts__iwprf = len(arr_tup.types)
    iagx__akx = 'def f(arr_tup):\n'
    iagx__akx += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        gts__iwprf)), ',' if gts__iwprf == 1 else '')
    qpkg__ugvi = {}
    exec(iagx__akx, {'np': np}, qpkg__ugvi)
    xes__dvtf = qpkg__ugvi['f']
    return xes__dvtf


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    gts__iwprf = len(arr_tup.types)
    gayy__jqefm = find_common_np_dtype(arr_tup.types)
    len__ejr = None
    dqkq__ulor = ''
    if isinstance(gayy__jqefm, types.Integer):
        len__ejr = bodo.libs.int_arr_ext.IntDtype(gayy__jqefm)
        dqkq__ulor = '.astype(out_dtype, False)'
    iagx__akx = 'def f(arr_tup):\n'
    iagx__akx += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, dqkq__ulor) for i in range(gts__iwprf)), ',' if 
        gts__iwprf == 1 else '')
    qpkg__ugvi = {}
    exec(iagx__akx, {'bodo': bodo, 'out_dtype': len__ejr}, qpkg__ugvi)
    cth__jauia = qpkg__ugvi['f']
    return cth__jauia


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, xluc__llex = build_set_seen_na(A)
        return len(s) + int(not dropna and xluc__llex)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        cxno__lzdqa = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        nzyv__bafyo = len(cxno__lzdqa)
        return bodo.libs.distributed_api.dist_reduce(nzyv__bafyo, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([dwbfo__ilju for dwbfo__ilju in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        sbvd__nbxf = np.finfo(A.dtype(1).dtype).max
    else:
        sbvd__nbxf = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        nwm__kthje = np.empty(n, A.dtype)
        htf__kbsew = sbvd__nbxf
        for i in range(n):
            htf__kbsew = min(htf__kbsew, A[i])
            nwm__kthje[i] = htf__kbsew
        return nwm__kthje
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        sbvd__nbxf = np.finfo(A.dtype(1).dtype).min
    else:
        sbvd__nbxf = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        nwm__kthje = np.empty(n, A.dtype)
        htf__kbsew = sbvd__nbxf
        for i in range(n):
            htf__kbsew = max(htf__kbsew, A[i])
            nwm__kthje[i] = htf__kbsew
        return nwm__kthje
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        xoorz__pux = arr_info_list_to_table([array_to_info(A)])
        gcri__bqbgm = 1
        zjcc__spnon = 0
        szzo__unps = drop_duplicates_table(xoorz__pux, parallel,
            gcri__bqbgm, zjcc__spnon, dropna)
        nwm__kthje = info_to_array(info_from_table(szzo__unps, 0), A)
        delete_table(xoorz__pux)
        delete_table(szzo__unps)
        return nwm__kthje
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    kyvwg__zlmgu = bodo.utils.typing.to_nullable_type(arr.dtype)
    vglcd__mjv = index_arr
    iieme__fkwyi = vglcd__mjv.dtype

    def impl(arr, index_arr):
        n = len(arr)
        rvnwx__ikhlf = init_nested_counts(kyvwg__zlmgu)
        jwgfg__gkruf = init_nested_counts(iieme__fkwyi)
        for i in range(n):
            emc__kjnj = index_arr[i]
            if isna(arr, i):
                rvnwx__ikhlf = (rvnwx__ikhlf[0] + 1,) + rvnwx__ikhlf[1:]
                jwgfg__gkruf = add_nested_counts(jwgfg__gkruf, emc__kjnj)
                continue
            fdhvi__qvl = arr[i]
            if len(fdhvi__qvl) == 0:
                rvnwx__ikhlf = (rvnwx__ikhlf[0] + 1,) + rvnwx__ikhlf[1:]
                jwgfg__gkruf = add_nested_counts(jwgfg__gkruf, emc__kjnj)
                continue
            rvnwx__ikhlf = add_nested_counts(rvnwx__ikhlf, fdhvi__qvl)
            for ftyn__zbjkg in range(len(fdhvi__qvl)):
                jwgfg__gkruf = add_nested_counts(jwgfg__gkruf, emc__kjnj)
        nwm__kthje = bodo.utils.utils.alloc_type(rvnwx__ikhlf[0],
            kyvwg__zlmgu, rvnwx__ikhlf[1:])
        hxmqk__yzm = bodo.utils.utils.alloc_type(rvnwx__ikhlf[0],
            vglcd__mjv, jwgfg__gkruf)
        aylsi__zsgss = 0
        for i in range(n):
            if isna(arr, i):
                setna(nwm__kthje, aylsi__zsgss)
                hxmqk__yzm[aylsi__zsgss] = index_arr[i]
                aylsi__zsgss += 1
                continue
            fdhvi__qvl = arr[i]
            ntpjq__tcbrm = len(fdhvi__qvl)
            if ntpjq__tcbrm == 0:
                setna(nwm__kthje, aylsi__zsgss)
                hxmqk__yzm[aylsi__zsgss] = index_arr[i]
                aylsi__zsgss += 1
                continue
            nwm__kthje[aylsi__zsgss:aylsi__zsgss + ntpjq__tcbrm] = fdhvi__qvl
            hxmqk__yzm[aylsi__zsgss:aylsi__zsgss + ntpjq__tcbrm] = index_arr[i]
            aylsi__zsgss += ntpjq__tcbrm
        return nwm__kthje, hxmqk__yzm
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    kyvwg__zlmgu = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        rvnwx__ikhlf = init_nested_counts(kyvwg__zlmgu)
        for i in range(n):
            if isna(arr, i):
                rvnwx__ikhlf = (rvnwx__ikhlf[0] + 1,) + rvnwx__ikhlf[1:]
                jpi__plgoy = 1
            else:
                fdhvi__qvl = arr[i]
                qklff__hdv = len(fdhvi__qvl)
                if qklff__hdv == 0:
                    rvnwx__ikhlf = (rvnwx__ikhlf[0] + 1,) + rvnwx__ikhlf[1:]
                    jpi__plgoy = 1
                    continue
                else:
                    rvnwx__ikhlf = add_nested_counts(rvnwx__ikhlf, fdhvi__qvl)
                    jpi__plgoy = qklff__hdv
            if counts[i] != jpi__plgoy:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        nwm__kthje = bodo.utils.utils.alloc_type(rvnwx__ikhlf[0],
            kyvwg__zlmgu, rvnwx__ikhlf[1:])
        aylsi__zsgss = 0
        for i in range(n):
            if isna(arr, i):
                setna(nwm__kthje, aylsi__zsgss)
                aylsi__zsgss += 1
                continue
            fdhvi__qvl = arr[i]
            ntpjq__tcbrm = len(fdhvi__qvl)
            if ntpjq__tcbrm == 0:
                setna(nwm__kthje, aylsi__zsgss)
                aylsi__zsgss += 1
                continue
            nwm__kthje[aylsi__zsgss:aylsi__zsgss + ntpjq__tcbrm] = fdhvi__qvl
            aylsi__zsgss += ntpjq__tcbrm
        return nwm__kthje
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(fkfz__qfa) for fkfz__qfa in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or arr == string_array_type and not na_empty_as_one
    if na_empty_as_one:
        rkz__xdd = 'np.empty(n, np.int64)'
        pzpi__aqqhm = 'out_arr[i] = 1'
        ira__jpzt = 'max(len(arr[i]), 1)'
    else:
        rkz__xdd = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        pzpi__aqqhm = 'bodo.libs.array_kernels.setna(out_arr, i)'
        ira__jpzt = 'len(arr[i])'
    iagx__akx = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {rkz__xdd}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {pzpi__aqqhm}
        else:
            out_arr[i] = {ira__jpzt}
    return out_arr
    """
    qpkg__ugvi = {}
    exec(iagx__akx, {'bodo': bodo, 'numba': numba, 'np': np}, qpkg__ugvi)
    impl = qpkg__ugvi['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert arr == string_array_type
    vglcd__mjv = index_arr
    iieme__fkwyi = vglcd__mjv.dtype

    def impl(arr, pat, n, index_arr):
        yznod__axnzx = pat is not None and len(pat) > 1
        if yznod__axnzx:
            alr__jyte = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        swkog__brk = len(arr)
        bmk__nhgja = 0
        bauag__fac = 0
        jwgfg__gkruf = init_nested_counts(iieme__fkwyi)
        for i in range(swkog__brk):
            emc__kjnj = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                bmk__nhgja += 1
                jwgfg__gkruf = add_nested_counts(jwgfg__gkruf, emc__kjnj)
                continue
            if yznod__axnzx:
                paj__cagr = alr__jyte.split(arr[i], maxsplit=n)
            else:
                paj__cagr = arr[i].split(pat, n)
            bmk__nhgja += len(paj__cagr)
            for s in paj__cagr:
                jwgfg__gkruf = add_nested_counts(jwgfg__gkruf, emc__kjnj)
                bauag__fac += bodo.libs.str_arr_ext.get_utf8_size(s)
        nwm__kthje = bodo.libs.str_arr_ext.pre_alloc_string_array(bmk__nhgja,
            bauag__fac)
        hxmqk__yzm = bodo.utils.utils.alloc_type(bmk__nhgja, vglcd__mjv,
            jwgfg__gkruf)
        beb__pwb = 0
        for zll__spj in range(swkog__brk):
            if isna(arr, zll__spj):
                nwm__kthje[beb__pwb] = ''
                bodo.libs.array_kernels.setna(nwm__kthje, beb__pwb)
                hxmqk__yzm[beb__pwb] = index_arr[zll__spj]
                beb__pwb += 1
                continue
            if yznod__axnzx:
                paj__cagr = alr__jyte.split(arr[zll__spj], maxsplit=n)
            else:
                paj__cagr = arr[zll__spj].split(pat, n)
            wcow__voopg = len(paj__cagr)
            nwm__kthje[beb__pwb:beb__pwb + wcow__voopg] = paj__cagr
            hxmqk__yzm[beb__pwb:beb__pwb + wcow__voopg] = index_arr[zll__spj]
            beb__pwb += wcow__voopg
        return nwm__kthje, hxmqk__yzm
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
            nwm__kthje = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                nwm__kthje[i] = np.nan
            return nwm__kthje
        return impl_float

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        nwm__kthje = bodo.utils.utils.alloc_type(n, arr, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(nwm__kthje, i)
        return nwm__kthje
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
    lydhg__hjikj = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            nwm__kthje = bodo.utils.utils.alloc_type(new_len, lydhg__hjikj)
            bodo.libs.str_arr_ext.str_copy_ptr(nwm__kthje.ctypes, 0, A.
                ctypes, old_size)
            return nwm__kthje
        return impl_char

    def impl(A, old_size, new_len):
        nwm__kthje = bodo.utils.utils.alloc_type(new_len, lydhg__hjikj, (-1,))
        nwm__kthje[:old_size] = A[:old_size]
        return nwm__kthje
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    hqw__forc = math.ceil((stop - start) / step)
    return int(max(hqw__forc, 0))


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
    if any(isinstance(dwbfo__ilju, types.Complex) for dwbfo__ilju in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            ddpp__wcxmf = (stop - start) / step
            hqw__forc = math.ceil(ddpp__wcxmf.real)
            nnu__pwy = math.ceil(ddpp__wcxmf.imag)
            rwarx__rzlpf = int(max(min(nnu__pwy, hqw__forc), 0))
            arr = np.empty(rwarx__rzlpf, dtype)
            for i in numba.parfors.parfor.internal_prange(rwarx__rzlpf):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            rwarx__rzlpf = bodo.libs.array_kernels.calc_nitems(start, stop,
                step)
            arr = np.empty(rwarx__rzlpf, dtype)
            for i in numba.parfors.parfor.internal_prange(rwarx__rzlpf):
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
        pkje__uqhm = arr,
        if not inplace:
            pkje__uqhm = arr.copy(),
        pulj__sfb = bodo.libs.str_arr_ext.to_list_if_immutable_arr(pkje__uqhm)
        hpbq__shebx = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True
            )
        bodo.libs.timsort.sort(pulj__sfb, 0, n, hpbq__shebx)
        if not ascending:
            bodo.libs.timsort.reverseRange(pulj__sfb, 0, n, hpbq__shebx)
        bodo.libs.str_arr_ext.cp_str_list_to_array(pkje__uqhm, pulj__sfb)
        return pkje__uqhm[0]
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
        tcf__jjnr = []
        for i in range(n):
            if A[i]:
                tcf__jjnr.append(i + offset)
        return np.array(tcf__jjnr, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    lydhg__hjikj = element_type(A)
    if lydhg__hjikj == types.unicode_type:
        null_value = '""'
    elif lydhg__hjikj == types.bool_:
        null_value = 'False'
    elif lydhg__hjikj == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif lydhg__hjikj == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    beb__pwb = 'i'
    idfob__eohlm = False
    jny__pauia = get_overload_const_str(method)
    if jny__pauia in ('ffill', 'pad'):
        lfydc__mgun = 'n'
        send_right = True
    elif jny__pauia in ('backfill', 'bfill'):
        lfydc__mgun = 'n-1, -1, -1'
        send_right = False
        if lydhg__hjikj == types.unicode_type:
            beb__pwb = '(n - 1) - i'
            idfob__eohlm = True
    iagx__akx = 'def impl(A, method, parallel=False):\n'
    iagx__akx += '  has_last_value = False\n'
    iagx__akx += f'  last_value = {null_value}\n'
    iagx__akx += '  if parallel:\n'
    iagx__akx += '    rank = bodo.libs.distributed_api.get_rank()\n'
    iagx__akx += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    iagx__akx += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    iagx__akx += '  n = len(A)\n'
    iagx__akx += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    iagx__akx += f'  for i in range({lfydc__mgun}):\n'
    iagx__akx += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    iagx__akx += f'      bodo.libs.array_kernels.setna(out_arr, {beb__pwb})\n'
    iagx__akx += '      continue\n'
    iagx__akx += '    s = A[i]\n'
    iagx__akx += '    if bodo.libs.array_kernels.isna(A, i):\n'
    iagx__akx += '      s = last_value\n'
    iagx__akx += f'    out_arr[{beb__pwb}] = s\n'
    iagx__akx += '    last_value = s\n'
    iagx__akx += '    has_last_value = True\n'
    if idfob__eohlm:
        iagx__akx += '  return out_arr[::-1]\n'
    else:
        iagx__akx += '  return out_arr\n'
    rio__joj = {}
    exec(iagx__akx, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm}, rio__joj)
    impl = rio__joj['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        xyeya__ikfj = 0
        rupi__ljipa = n_pes - 1
        kcxp__wqcq = np.int32(rank + 1)
        lukwj__jpesj = np.int32(rank - 1)
        tqfs__upq = len(in_arr) - 1
        ubzj__fix = -1
        rsi__gtk = -1
    else:
        xyeya__ikfj = n_pes - 1
        rupi__ljipa = 0
        kcxp__wqcq = np.int32(rank - 1)
        lukwj__jpesj = np.int32(rank + 1)
        tqfs__upq = 0
        ubzj__fix = len(in_arr)
        rsi__gtk = 1
    mwfuo__drfd = np.int32(bodo.hiframes.rolling.comm_border_tag)
    kyjfq__bltuj = np.empty(1, dtype=np.bool_)
    svpjk__nqv = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    oxu__measq = np.empty(1, dtype=np.bool_)
    edi__gqr = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    akwe__ppyx = False
    vabxy__fkic = null_value
    for i in range(tqfs__upq, ubzj__fix, rsi__gtk):
        if not isna(in_arr, i):
            akwe__ppyx = True
            vabxy__fkic = in_arr[i]
            break
    if rank != xyeya__ikfj:
        vex__zytrx = bodo.libs.distributed_api.irecv(kyjfq__bltuj, 1,
            lukwj__jpesj, mwfuo__drfd, True)
        bodo.libs.distributed_api.wait(vex__zytrx, True)
        ztkgb__mbg = bodo.libs.distributed_api.irecv(svpjk__nqv, 1,
            lukwj__jpesj, mwfuo__drfd, True)
        bodo.libs.distributed_api.wait(ztkgb__mbg, True)
        rnlq__tjkk = kyjfq__bltuj[0]
        owa__wlfyc = svpjk__nqv[0]
    else:
        rnlq__tjkk = False
        owa__wlfyc = null_value
    if akwe__ppyx:
        oxu__measq[0] = akwe__ppyx
        edi__gqr[0] = vabxy__fkic
    else:
        oxu__measq[0] = rnlq__tjkk
        edi__gqr[0] = owa__wlfyc
    if rank != rupi__ljipa:
        mxr__wwwl = bodo.libs.distributed_api.isend(oxu__measq, 1,
            kcxp__wqcq, mwfuo__drfd, True)
        suwt__ncfm = bodo.libs.distributed_api.isend(edi__gqr, 1,
            kcxp__wqcq, mwfuo__drfd, True)
    return rnlq__tjkk, owa__wlfyc


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    qewm__zkm = {'axis': axis, 'kind': kind, 'order': order}
    haph__rleti = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', qewm__zkm, haph__rleti, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    lydhg__hjikj = A
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            swkog__brk = len(A)
            nwm__kthje = bodo.utils.utils.alloc_type(swkog__brk * repeats,
                lydhg__hjikj, (-1,))
            for i in range(swkog__brk):
                beb__pwb = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for zll__spj in range(repeats):
                        bodo.libs.array_kernels.setna(nwm__kthje, beb__pwb +
                            zll__spj)
                else:
                    nwm__kthje[beb__pwb:beb__pwb + repeats] = A[i]
            return nwm__kthje
        return impl_int

    def impl_arr(A, repeats):
        swkog__brk = len(A)
        nwm__kthje = bodo.utils.utils.alloc_type(repeats.sum(),
            lydhg__hjikj, (-1,))
        beb__pwb = 0
        for i in range(swkog__brk):
            sba__yicq = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for zll__spj in range(sba__yicq):
                    bodo.libs.array_kernels.setna(nwm__kthje, beb__pwb +
                        zll__spj)
            else:
                nwm__kthje[beb__pwb:beb__pwb + sba__yicq] = A[i]
            beb__pwb += sba__yicq
        return nwm__kthje
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
        rksba__ylnb = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(rksba__ylnb, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        fic__huivj = bodo.libs.array_kernels.concat([A1, A2])
        happu__gpfu = bodo.libs.array_kernels.unique(fic__huivj)
        return pd.Series(happu__gpfu).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    qewm__zkm = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    haph__rleti = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', qewm__zkm, haph__rleti, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        cepu__msvj = bodo.libs.array_kernels.unique(A1)
        qan__nqi = bodo.libs.array_kernels.unique(A2)
        fic__huivj = bodo.libs.array_kernels.concat([cepu__msvj, qan__nqi])
        fym__toxi = pd.Series(fic__huivj).sort_values().values
        return slice_array_intersect1d(fym__toxi)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    eydpi__owrh = arr[1:] == arr[:-1]
    return arr[:-1][eydpi__owrh]


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    qewm__zkm = {'assume_unique': assume_unique}
    haph__rleti = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', qewm__zkm, haph__rleti, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        cepu__msvj = bodo.libs.array_kernels.unique(A1)
        qan__nqi = bodo.libs.array_kernels.unique(A2)
        eydpi__owrh = calculate_mask_setdiff1d(cepu__msvj, qan__nqi)
        return pd.Series(cepu__msvj[eydpi__owrh]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    eydpi__owrh = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        eydpi__owrh &= A1 != A2[i]
    return eydpi__owrh


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    qewm__zkm = {'retstep': retstep, 'axis': axis}
    haph__rleti = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', qewm__zkm, haph__rleti, 'numpy')
    epsox__igbz = False
    if is_overload_none(dtype):
        lydhg__hjikj = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            epsox__igbz = True
        lydhg__hjikj = numba.np.numpy_support.as_dtype(dtype).type
    if epsox__igbz:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            uno__ivkn = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            nwm__kthje = np.empty(num, lydhg__hjikj)
            for i in numba.parfors.parfor.internal_prange(num):
                nwm__kthje[i] = lydhg__hjikj(np.floor(start + i * uno__ivkn))
            return nwm__kthje
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            uno__ivkn = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            nwm__kthje = np.empty(num, lydhg__hjikj)
            for i in numba.parfors.parfor.internal_prange(num):
                nwm__kthje[i] = lydhg__hjikj(start + i * uno__ivkn)
            return nwm__kthje
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
        gts__iwprf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                gts__iwprf += A[i] == val
        return gts__iwprf > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    qewm__zkm = {'axis': axis, 'out': out, 'keepdims': keepdims}
    haph__rleti = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', qewm__zkm, haph__rleti, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        gts__iwprf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                gts__iwprf += int(bool(A[i]))
        return gts__iwprf > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    qewm__zkm = {'axis': axis, 'out': out, 'keepdims': keepdims}
    haph__rleti = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', qewm__zkm, haph__rleti, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        gts__iwprf = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                gts__iwprf += int(bool(A[i]))
        return gts__iwprf == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    qewm__zkm = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    haph__rleti = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', qewm__zkm, haph__rleti, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        vuw__xxi = np.promote_types(numba.np.numpy_support.as_dtype(A.dtype
            ), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            nwm__kthje = np.empty(n, vuw__xxi)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(nwm__kthje, i)
                    continue
                nwm__kthje[i] = np_cbrt_scalar(A[i], vuw__xxi)
            return nwm__kthje
        return impl_arr
    vuw__xxi = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, vuw__xxi)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    ywa__dsm = x < 0
    if ywa__dsm:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if ywa__dsm:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    otv__wfk = isinstance(tup, (types.BaseTuple, types.List))
    tfx__lab = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for xelyr__dhqes in tup.types:
            otv__wfk = otv__wfk and bodo.utils.utils.is_array_typ(xelyr__dhqes,
                False)
    elif isinstance(tup, types.List):
        otv__wfk = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif tfx__lab:
        frvs__nqied = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for xelyr__dhqes in frvs__nqied.types:
            tfx__lab = tfx__lab and bodo.utils.utils.is_array_typ(xelyr__dhqes,
                False)
    if not (otv__wfk or tfx__lab):
        return
    if tfx__lab:

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
    qewm__zkm = {'check_valid': check_valid, 'tol': tol}
    haph__rleti = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', qewm__zkm,
        haph__rleti, 'numpy')
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
        aojk__aseta = mean.shape[0]
        ljl__srarx = size, aojk__aseta
        qhayn__kon = np.random.standard_normal(ljl__srarx)
        cov = cov.astype(np.float64)
        sjmq__dclm, s, skw__xym = np.linalg.svd(cov)
        res = np.dot(qhayn__kon, np.sqrt(s).reshape(aojk__aseta, 1) * skw__xym)
        pbd__mgd = res + mean
        return pbd__mgd
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
            zcslh__lkdyq = bodo.hiframes.series_kernels._get_type_max_value(arr
                )
            bww__ofzl = typing.builtins.IndexValue(-1, zcslh__lkdyq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mkow__srlm = typing.builtins.IndexValue(i, arr[i])
                bww__ofzl = min(bww__ofzl, mkow__srlm)
            return bww__ofzl.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        goc__gvn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            fio__rvjlx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            zcslh__lkdyq = goc__gvn(len(arr.dtype.categories) + 1)
            bww__ofzl = typing.builtins.IndexValue(-1, zcslh__lkdyq)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mkow__srlm = typing.builtins.IndexValue(i, fio__rvjlx[i])
                bww__ofzl = min(bww__ofzl, mkow__srlm)
            return bww__ofzl.index
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
            zcslh__lkdyq = bodo.hiframes.series_kernels._get_type_min_value(arr
                )
            bww__ofzl = typing.builtins.IndexValue(-1, zcslh__lkdyq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mkow__srlm = typing.builtins.IndexValue(i, arr[i])
                bww__ofzl = max(bww__ofzl, mkow__srlm)
            return bww__ofzl.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        goc__gvn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            fio__rvjlx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            zcslh__lkdyq = goc__gvn(-1)
            bww__ofzl = typing.builtins.IndexValue(-1, zcslh__lkdyq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                mkow__srlm = typing.builtins.IndexValue(i, fio__rvjlx[i])
                bww__ofzl = max(bww__ofzl, mkow__srlm)
            return bww__ofzl.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
