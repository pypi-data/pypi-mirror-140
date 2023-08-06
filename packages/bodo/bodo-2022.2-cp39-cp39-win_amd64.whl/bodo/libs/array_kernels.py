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
        qfr__haq = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = qfr__haq
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
            wbc__vwtvm = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            wbc__vwtvm[ind + 1] = wbc__vwtvm[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            wbc__vwtvm = bodo.libs.array_item_arr_ext.get_offsets(arr)
            wbc__vwtvm[ind + 1] = wbc__vwtvm[ind]
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
    geam__waole = arr_tup.count
    zle__lxspi = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(geam__waole):
        zle__lxspi += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    zle__lxspi += '  return\n'
    hmey__dmf = {}
    exec(zle__lxspi, {'setna': setna}, hmey__dmf)
    impl = hmey__dmf['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        wohq__yxvp = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(wohq__yxvp.start, wohq__yxvp.stop, wohq__yxvp.step):
            setna(arr, i)
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    xjnrj__losss = array_to_info(arr)
    _median_series_computation(res, xjnrj__losss, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(xjnrj__losss)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    xjnrj__losss = array_to_info(arr)
    _autocorr_series_computation(res, xjnrj__losss, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(xjnrj__losss)


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
    xjnrj__losss = array_to_info(arr)
    _compute_series_monotonicity(res, xjnrj__losss, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(xjnrj__losss)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    xgqi__zlz = res[0] > 0.5
    return xgqi__zlz


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        jyb__ubek = '-'
        bsfnh__pjb = 'index_arr[0] > threshhold_date'
        ovyf__qwz = '1, n+1'
        djmma__soq = 'index_arr[-i] <= threshhold_date'
        gwozp__izp = 'i - 1'
    else:
        jyb__ubek = '+'
        bsfnh__pjb = 'index_arr[-1] < threshhold_date'
        ovyf__qwz = 'n'
        djmma__soq = 'index_arr[i] >= threshhold_date'
        gwozp__izp = 'i'
    zle__lxspi = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        zle__lxspi += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        zle__lxspi += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            zle__lxspi += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            zle__lxspi += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            zle__lxspi += '    else:\n'
            zle__lxspi += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            zle__lxspi += (
                f'    threshhold_date = initial_date {jyb__ubek} date_offset\n'
                )
    else:
        zle__lxspi += f'  threshhold_date = initial_date {jyb__ubek} offset\n'
    zle__lxspi += '  local_valid = 0\n'
    zle__lxspi += f'  n = len(index_arr)\n'
    zle__lxspi += f'  if n:\n'
    zle__lxspi += f'    if {bsfnh__pjb}:\n'
    zle__lxspi += '      loc_valid = n\n'
    zle__lxspi += '    else:\n'
    zle__lxspi += f'      for i in range({ovyf__qwz}):\n'
    zle__lxspi += f'        if {djmma__soq}:\n'
    zle__lxspi += f'          loc_valid = {gwozp__izp}\n'
    zle__lxspi += '          break\n'
    zle__lxspi += '  if is_parallel:\n'
    zle__lxspi += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    zle__lxspi += '    return total_valid\n'
    zle__lxspi += '  else:\n'
    zle__lxspi += '    return loc_valid\n'
    hmey__dmf = {}
    exec(zle__lxspi, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, hmey__dmf)
    return hmey__dmf['impl']


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
    lqjm__clhfq = numba_to_c_type(sig.args[0].dtype)
    lndkj__urr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), lqjm__clhfq))
    nmk__uvwsr = args[0]
    yqcfs__frgqh = sig.args[0]
    if isinstance(yqcfs__frgqh, (IntegerArrayType, BooleanArrayType)):
        nmk__uvwsr = cgutils.create_struct_proxy(yqcfs__frgqh)(context,
            builder, nmk__uvwsr).data
        yqcfs__frgqh = types.Array(yqcfs__frgqh.dtype, 1, 'C')
    assert yqcfs__frgqh.ndim == 1
    arr = make_array(yqcfs__frgqh)(context, builder, nmk__uvwsr)
    qqqav__ahl = builder.extract_value(arr.shape, 0)
    dzy__tyefr = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        qqqav__ahl, args[1], builder.load(lndkj__urr)]
    xlmpy__apj = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    nhq__obbw = lir.FunctionType(lir.DoubleType(), xlmpy__apj)
    mlwp__diof = cgutils.get_or_insert_function(builder.module, nhq__obbw,
        name='quantile_sequential')
    xmbcm__puea = builder.call(mlwp__diof, dzy__tyefr)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return xmbcm__puea


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    lqjm__clhfq = numba_to_c_type(sig.args[0].dtype)
    lndkj__urr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), lqjm__clhfq))
    nmk__uvwsr = args[0]
    yqcfs__frgqh = sig.args[0]
    if isinstance(yqcfs__frgqh, (IntegerArrayType, BooleanArrayType)):
        nmk__uvwsr = cgutils.create_struct_proxy(yqcfs__frgqh)(context,
            builder, nmk__uvwsr).data
        yqcfs__frgqh = types.Array(yqcfs__frgqh.dtype, 1, 'C')
    assert yqcfs__frgqh.ndim == 1
    arr = make_array(yqcfs__frgqh)(context, builder, nmk__uvwsr)
    qqqav__ahl = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        mbyat__skq = args[2]
    else:
        mbyat__skq = qqqav__ahl
    dzy__tyefr = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        qqqav__ahl, mbyat__skq, args[1], builder.load(lndkj__urr)]
    xlmpy__apj = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    nhq__obbw = lir.FunctionType(lir.DoubleType(), xlmpy__apj)
    mlwp__diof = cgutils.get_or_insert_function(builder.module, nhq__obbw,
        name='quantile_parallel')
    xmbcm__puea = builder.call(mlwp__diof, dzy__tyefr)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return xmbcm__puea


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    mtrx__uvqnf = start
    vlkvn__oopwp = 2 * start + 1
    mgp__ldas = 2 * start + 2
    if vlkvn__oopwp < n and not cmp_f(arr[vlkvn__oopwp], arr[mtrx__uvqnf]):
        mtrx__uvqnf = vlkvn__oopwp
    if mgp__ldas < n and not cmp_f(arr[mgp__ldas], arr[mtrx__uvqnf]):
        mtrx__uvqnf = mgp__ldas
    if mtrx__uvqnf != start:
        arr[start], arr[mtrx__uvqnf] = arr[mtrx__uvqnf], arr[start]
        ind_arr[start], ind_arr[mtrx__uvqnf] = ind_arr[mtrx__uvqnf], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, mtrx__uvqnf, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        shb__qyu = np.empty(k, A.dtype)
        emtg__iynz = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                shb__qyu[ind] = A[i]
                emtg__iynz[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            shb__qyu = shb__qyu[:ind]
            emtg__iynz = emtg__iynz[:ind]
        return shb__qyu, emtg__iynz, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        hoph__kaey = np.sort(A)
        exhje__ajy = index_arr[np.argsort(A)]
        gtql__cfi = pd.Series(hoph__kaey).notna().values
        hoph__kaey = hoph__kaey[gtql__cfi]
        exhje__ajy = exhje__ajy[gtql__cfi]
        if is_largest:
            hoph__kaey = hoph__kaey[::-1]
            exhje__ajy = exhje__ajy[::-1]
        return np.ascontiguousarray(hoph__kaey), np.ascontiguousarray(
            exhje__ajy)
    shb__qyu, emtg__iynz, start = select_k_nonan(A, index_arr, m, k)
    emtg__iynz = emtg__iynz[shb__qyu.argsort()]
    shb__qyu.sort()
    if not is_largest:
        shb__qyu = np.ascontiguousarray(shb__qyu[::-1])
        emtg__iynz = np.ascontiguousarray(emtg__iynz[::-1])
    for i in range(start, m):
        if cmp_f(A[i], shb__qyu[0]):
            shb__qyu[0] = A[i]
            emtg__iynz[0] = index_arr[i]
            min_heapify(shb__qyu, emtg__iynz, k, 0, cmp_f)
    emtg__iynz = emtg__iynz[shb__qyu.argsort()]
    shb__qyu.sort()
    if is_largest:
        shb__qyu = shb__qyu[::-1]
        emtg__iynz = emtg__iynz[::-1]
    return np.ascontiguousarray(shb__qyu), np.ascontiguousarray(emtg__iynz)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    csehb__mdsvc = bodo.libs.distributed_api.get_rank()
    uteq__cnsg, bbfae__tcvt = nlargest(A, I, k, is_largest, cmp_f)
    bfyvj__ylxpf = bodo.libs.distributed_api.gatherv(uteq__cnsg)
    kjxw__jqzg = bodo.libs.distributed_api.gatherv(bbfae__tcvt)
    if csehb__mdsvc == MPI_ROOT:
        res, apkqw__yhiyg = nlargest(bfyvj__ylxpf, kjxw__jqzg, k,
            is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        apkqw__yhiyg = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(apkqw__yhiyg)
    return res, apkqw__yhiyg


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    lzy__bidt, szw__glc = mat.shape
    xqrf__iiqwg = np.empty((szw__glc, szw__glc), dtype=np.float64)
    for kzm__haeh in range(szw__glc):
        for hcju__clqdq in range(kzm__haeh + 1):
            dypt__vfx = 0
            lilwq__mirv = jvk__onjx = crilh__vit = nphl__pylc = 0.0
            for i in range(lzy__bidt):
                if np.isfinite(mat[i, kzm__haeh]) and np.isfinite(mat[i,
                    hcju__clqdq]):
                    yolrc__tfb = mat[i, kzm__haeh]
                    ahsho__biecz = mat[i, hcju__clqdq]
                    dypt__vfx += 1
                    crilh__vit += yolrc__tfb
                    nphl__pylc += ahsho__biecz
            if parallel:
                dypt__vfx = bodo.libs.distributed_api.dist_reduce(dypt__vfx,
                    sum_op)
                crilh__vit = bodo.libs.distributed_api.dist_reduce(crilh__vit,
                    sum_op)
                nphl__pylc = bodo.libs.distributed_api.dist_reduce(nphl__pylc,
                    sum_op)
            if dypt__vfx < minpv:
                xqrf__iiqwg[kzm__haeh, hcju__clqdq] = xqrf__iiqwg[
                    hcju__clqdq, kzm__haeh] = np.nan
            else:
                irvj__zdcb = crilh__vit / dypt__vfx
                lauu__yxt = nphl__pylc / dypt__vfx
                crilh__vit = 0.0
                for i in range(lzy__bidt):
                    if np.isfinite(mat[i, kzm__haeh]) and np.isfinite(mat[i,
                        hcju__clqdq]):
                        yolrc__tfb = mat[i, kzm__haeh] - irvj__zdcb
                        ahsho__biecz = mat[i, hcju__clqdq] - lauu__yxt
                        crilh__vit += yolrc__tfb * ahsho__biecz
                        lilwq__mirv += yolrc__tfb * yolrc__tfb
                        jvk__onjx += ahsho__biecz * ahsho__biecz
                if parallel:
                    crilh__vit = bodo.libs.distributed_api.dist_reduce(
                        crilh__vit, sum_op)
                    lilwq__mirv = bodo.libs.distributed_api.dist_reduce(
                        lilwq__mirv, sum_op)
                    jvk__onjx = bodo.libs.distributed_api.dist_reduce(jvk__onjx
                        , sum_op)
                pka__rze = dypt__vfx - 1.0 if cov else sqrt(lilwq__mirv *
                    jvk__onjx)
                if pka__rze != 0.0:
                    xqrf__iiqwg[kzm__haeh, hcju__clqdq] = xqrf__iiqwg[
                        hcju__clqdq, kzm__haeh] = crilh__vit / pka__rze
                else:
                    xqrf__iiqwg[kzm__haeh, hcju__clqdq] = xqrf__iiqwg[
                        hcju__clqdq, kzm__haeh] = np.nan
    return xqrf__iiqwg


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    ild__unyly = n != 1
    zle__lxspi = 'def impl(data, parallel=False):\n'
    zle__lxspi += '  if parallel:\n'
    exnps__bjda = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    zle__lxspi += f'    cpp_table = arr_info_list_to_table([{exnps__bjda}])\n'
    zle__lxspi += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    mdiua__jsjpt = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    zle__lxspi += f'    data = ({mdiua__jsjpt},)\n'
    zle__lxspi += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    zle__lxspi += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    zle__lxspi += '    bodo.libs.array.delete_table(cpp_table)\n'
    zle__lxspi += (
        '  data = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data)\n')
    zle__lxspi += '  n = len(data[0])\n'
    zle__lxspi += '  out = np.empty(n, np.bool_)\n'
    zle__lxspi += '  uniqs = dict()\n'
    if ild__unyly:
        zle__lxspi += '  for i in range(n):\n'
        cnw__ecb = ', '.join(f'data[{i}][i]' for i in range(n))
        qkks__xdk = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        zle__lxspi += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({cnw__ecb},), ({qkks__xdk},))
"""
        zle__lxspi += '    if val in uniqs:\n'
        zle__lxspi += '      out[i] = True\n'
        zle__lxspi += '    else:\n'
        zle__lxspi += '      out[i] = False\n'
        zle__lxspi += '      uniqs[val] = 0\n'
    else:
        zle__lxspi += '  data = data[0]\n'
        zle__lxspi += '  hasna = False\n'
        zle__lxspi += '  for i in range(n):\n'
        zle__lxspi += '    if bodo.libs.array_kernels.isna(data, i):\n'
        zle__lxspi += '      out[i] = hasna\n'
        zle__lxspi += '      hasna = True\n'
        zle__lxspi += '    else:\n'
        zle__lxspi += '      val = data[i]\n'
        zle__lxspi += '      if val in uniqs:\n'
        zle__lxspi += '        out[i] = True\n'
        zle__lxspi += '      else:\n'
        zle__lxspi += '        out[i] = False\n'
        zle__lxspi += '        uniqs[val] = 0\n'
    zle__lxspi += '  if parallel:\n'
    zle__lxspi += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    zle__lxspi += '  return out\n'
    hmey__dmf = {}
    exec(zle__lxspi, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        hmey__dmf)
    impl = hmey__dmf['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    geam__waole = len(data)
    zle__lxspi = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    zle__lxspi += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        geam__waole)))
    zle__lxspi += '  table_total = arr_info_list_to_table(info_list_total)\n'
    zle__lxspi += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(geam__waole))
    for abcmw__wtosz in range(geam__waole):
        zle__lxspi += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(abcmw__wtosz, abcmw__wtosz, abcmw__wtosz))
    zle__lxspi += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(geam__waole))
    zle__lxspi += '  delete_table(out_table)\n'
    zle__lxspi += '  delete_table(table_total)\n'
    zle__lxspi += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(geam__waole)))
    hmey__dmf = {}
    exec(zle__lxspi, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, hmey__dmf)
    impl = hmey__dmf['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    geam__waole = len(data)
    zle__lxspi = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    zle__lxspi += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        geam__waole)))
    zle__lxspi += '  table_total = arr_info_list_to_table(info_list_total)\n'
    zle__lxspi += '  keep_i = 0\n'
    zle__lxspi += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False)
"""
    for abcmw__wtosz in range(geam__waole):
        zle__lxspi += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(abcmw__wtosz, abcmw__wtosz, abcmw__wtosz))
    zle__lxspi += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(geam__waole))
    zle__lxspi += '  delete_table(out_table)\n'
    zle__lxspi += '  delete_table(table_total)\n'
    zle__lxspi += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(geam__waole)))
    hmey__dmf = {}
    exec(zle__lxspi, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, hmey__dmf)
    impl = hmey__dmf['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        nzk__peeq = [array_to_info(data_arr)]
        mnnsa__hotmq = arr_info_list_to_table(nzk__peeq)
        ptw__ogurx = 0
        kqhhv__vgjva = drop_duplicates_table(mnnsa__hotmq, parallel, 1,
            ptw__ogurx, False)
        hxqd__jleg = info_to_array(info_from_table(kqhhv__vgjva, 0), data_arr)
        delete_table(kqhhv__vgjva)
        delete_table(mnnsa__hotmq)
        return hxqd__jleg
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    kwhv__chgac = len(data.types)
    dhe__sjjds = [('out' + str(i)) for i in range(kwhv__chgac)]
    rusc__btsh = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    fis__mcwws = ['isna(data[{}], i)'.format(i) for i in rusc__btsh]
    pyiad__ucuiz = 'not ({})'.format(' or '.join(fis__mcwws))
    if not is_overload_none(thresh):
        pyiad__ucuiz = '(({}) <= ({}) - thresh)'.format(' + '.join(
            fis__mcwws), kwhv__chgac - 1)
    elif how == 'all':
        pyiad__ucuiz = 'not ({})'.format(' and '.join(fis__mcwws))
    zle__lxspi = 'def _dropna_imp(data, how, thresh, subset):\n'
    zle__lxspi += '  old_len = len(data[0])\n'
    zle__lxspi += '  new_len = 0\n'
    zle__lxspi += '  for i in range(old_len):\n'
    zle__lxspi += '    if {}:\n'.format(pyiad__ucuiz)
    zle__lxspi += '      new_len += 1\n'
    for i, out in enumerate(dhe__sjjds):
        if isinstance(data[i], bodo.CategoricalArrayType):
            zle__lxspi += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            zle__lxspi += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    zle__lxspi += '  curr_ind = 0\n'
    zle__lxspi += '  for i in range(old_len):\n'
    zle__lxspi += '    if {}:\n'.format(pyiad__ucuiz)
    for i in range(kwhv__chgac):
        zle__lxspi += '      if isna(data[{}], i):\n'.format(i)
        zle__lxspi += '        setna({}, curr_ind)\n'.format(dhe__sjjds[i])
        zle__lxspi += '      else:\n'
        zle__lxspi += '        {}[curr_ind] = data[{}][i]\n'.format(dhe__sjjds
            [i], i)
    zle__lxspi += '      curr_ind += 1\n'
    zle__lxspi += '  return {}\n'.format(', '.join(dhe__sjjds))
    hmey__dmf = {}
    bjoq__idsc = {'t{}'.format(i): axr__rneto for i, axr__rneto in
        enumerate(data.types)}
    bjoq__idsc.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(zle__lxspi, bjoq__idsc, hmey__dmf)
    noyfp__yce = hmey__dmf['_dropna_imp']
    return noyfp__yce


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        yqcfs__frgqh = arr.dtype
        jbrs__runnw = yqcfs__frgqh.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            wuvn__dkqcv = init_nested_counts(jbrs__runnw)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                wuvn__dkqcv = add_nested_counts(wuvn__dkqcv, val[ind])
            hxqd__jleg = bodo.utils.utils.alloc_type(n, yqcfs__frgqh,
                wuvn__dkqcv)
            for ptsma__lcrb in range(n):
                if bodo.libs.array_kernels.isna(arr, ptsma__lcrb):
                    setna(hxqd__jleg, ptsma__lcrb)
                    continue
                val = arr[ptsma__lcrb]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(hxqd__jleg, ptsma__lcrb)
                    continue
                hxqd__jleg[ptsma__lcrb] = val[ind]
            return hxqd__jleg
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    yrkaz__fza = _to_readonly(arr_types.types[0])
    return all(isinstance(axr__rneto, CategoricalArrayType) and 
        _to_readonly(axr__rneto) == yrkaz__fza for axr__rneto in arr_types.
        types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        fjc__onhx = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            lqc__jnpg = 0
            tnb__kevg = []
            for A in arr_list:
                rnlq__rws = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                tnb__kevg.append(bodo.libs.array_item_arr_ext.get_data(A))
                lqc__jnpg += rnlq__rws
            vzzt__sopv = np.empty(lqc__jnpg + 1, offset_type)
            isjoi__gvc = bodo.libs.array_kernels.concat(tnb__kevg)
            upoog__vken = np.empty(lqc__jnpg + 7 >> 3, np.uint8)
            ymnln__wcpu = 0
            plwn__wzov = 0
            for A in arr_list:
                ovn__khm = bodo.libs.array_item_arr_ext.get_offsets(A)
                pbd__yybe = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                rnlq__rws = len(A)
                pri__msfl = ovn__khm[rnlq__rws]
                for i in range(rnlq__rws):
                    vzzt__sopv[i + ymnln__wcpu] = ovn__khm[i] + plwn__wzov
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        pbd__yybe, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(upoog__vken, i +
                        ymnln__wcpu, xgxzs__dlq)
                ymnln__wcpu += rnlq__rws
                plwn__wzov += pri__msfl
            vzzt__sopv[ymnln__wcpu] = plwn__wzov
            hxqd__jleg = bodo.libs.array_item_arr_ext.init_array_item_array(
                lqc__jnpg, isjoi__gvc, vzzt__sopv, upoog__vken)
            return hxqd__jleg
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        okdof__qrqig = arr_list.dtype.names
        zle__lxspi = 'def struct_array_concat_impl(arr_list):\n'
        zle__lxspi += f'    n_all = 0\n'
        for i in range(len(okdof__qrqig)):
            zle__lxspi += f'    concat_list{i} = []\n'
        zle__lxspi += '    for A in arr_list:\n'
        zle__lxspi += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(okdof__qrqig)):
            zle__lxspi += f'        concat_list{i}.append(data_tuple[{i}])\n'
        zle__lxspi += '        n_all += len(A)\n'
        zle__lxspi += '    n_bytes = (n_all + 7) >> 3\n'
        zle__lxspi += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        zle__lxspi += '    curr_bit = 0\n'
        zle__lxspi += '    for A in arr_list:\n'
        zle__lxspi += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        zle__lxspi += '        for j in range(len(A)):\n'
        zle__lxspi += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        zle__lxspi += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        zle__lxspi += '            curr_bit += 1\n'
        zle__lxspi += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        ihx__ilb = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(okdof__qrqig))])
        zle__lxspi += f'        ({ihx__ilb},),\n'
        zle__lxspi += '        new_mask,\n'
        zle__lxspi += f'        {okdof__qrqig},\n'
        zle__lxspi += '    )\n'
        hmey__dmf = {}
        exec(zle__lxspi, {'bodo': bodo, 'np': np}, hmey__dmf)
        return hmey__dmf['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            kxrbh__jrm = 0
            for A in arr_list:
                kxrbh__jrm += len(A)
            ktz__cfnxw = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(kxrbh__jrm))
            bcra__nywu = 0
            for A in arr_list:
                for i in range(len(A)):
                    ktz__cfnxw._data[i + bcra__nywu] = A._data[i]
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ktz__cfnxw.
                        _null_bitmap, i + bcra__nywu, xgxzs__dlq)
                bcra__nywu += len(A)
            return ktz__cfnxw
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            kxrbh__jrm = 0
            for A in arr_list:
                kxrbh__jrm += len(A)
            ktz__cfnxw = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(kxrbh__jrm))
            bcra__nywu = 0
            for A in arr_list:
                for i in range(len(A)):
                    ktz__cfnxw._days_data[i + bcra__nywu] = A._days_data[i]
                    ktz__cfnxw._seconds_data[i + bcra__nywu] = A._seconds_data[
                        i]
                    ktz__cfnxw._microseconds_data[i + bcra__nywu
                        ] = A._microseconds_data[i]
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ktz__cfnxw.
                        _null_bitmap, i + bcra__nywu, xgxzs__dlq)
                bcra__nywu += len(A)
            return ktz__cfnxw
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        dap__rmr = arr_list.dtype.precision
        czchb__nhu = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            kxrbh__jrm = 0
            for A in arr_list:
                kxrbh__jrm += len(A)
            ktz__cfnxw = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                kxrbh__jrm, dap__rmr, czchb__nhu)
            bcra__nywu = 0
            for A in arr_list:
                for i in range(len(A)):
                    ktz__cfnxw._data[i + bcra__nywu] = A._data[i]
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ktz__cfnxw.
                        _null_bitmap, i + bcra__nywu, xgxzs__dlq)
                bcra__nywu += len(A)
            return ktz__cfnxw
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype in [string_array_type, bodo.binary_array_type]:
        if arr_list.dtype == bodo.binary_array_type:
            qrc__rpb = 'bodo.libs.str_arr_ext.pre_alloc_binary_array'
        elif arr_list.dtype == string_array_type:
            qrc__rpb = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zle__lxspi = 'def impl(arr_list):  # pragma: no cover\n'
        zle__lxspi += '    # preallocate the output\n'
        zle__lxspi += '    num_strs = 0\n'
        zle__lxspi += '    num_chars = 0\n'
        zle__lxspi += '    for A in arr_list:\n'
        zle__lxspi += '        arr = A\n'
        zle__lxspi += '        num_strs += len(arr)\n'
        zle__lxspi += '        # this should work for both binary and string\n'
        zle__lxspi += (
            '        num_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        zle__lxspi += f'    out_arr = {qrc__rpb}(\n'
        zle__lxspi += '        num_strs, num_chars\n'
        zle__lxspi += '    )\n'
        zle__lxspi += (
            '    bodo.libs.str_arr_ext.set_null_bits_to_value(out_arr, -1)\n')
        zle__lxspi += '    # copy data to output\n'
        zle__lxspi += '    curr_str_ind = 0\n'
        zle__lxspi += '    curr_chars_ind = 0\n'
        zle__lxspi += '    for A in arr_list:\n'
        zle__lxspi += '        arr = A\n'
        zle__lxspi += '        # This will probably need to be extended\n'
        zle__lxspi += '        bodo.libs.str_arr_ext.set_string_array_range(\n'
        zle__lxspi += (
            '            out_arr, arr, curr_str_ind, curr_chars_ind\n')
        zle__lxspi += '        )\n'
        zle__lxspi += '        curr_str_ind += len(arr)\n'
        zle__lxspi += '        # this should work for both binary and string\n'
        zle__lxspi += (
            '        curr_chars_ind += bodo.libs.str_arr_ext.num_total_chars(arr)\n'
            )
        zle__lxspi += '    return out_arr\n'
        xsya__seb = dict()
        exec(zle__lxspi, {'bodo': bodo}, xsya__seb)
        lnt__kdvb = xsya__seb['impl']
        return lnt__kdvb
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(axr__rneto.dtype, types.Integer) for
        axr__rneto in arr_list.types) and any(isinstance(axr__rneto,
        IntegerArrayType) for axr__rneto in arr_list.types):

        def impl_int_arr_list(arr_list):
            zghj__tvi = convert_to_nullable_tup(arr_list)
            cnpe__akur = []
            btpua__rcr = 0
            for A in zghj__tvi:
                cnpe__akur.append(A._data)
                btpua__rcr += len(A)
            isjoi__gvc = bodo.libs.array_kernels.concat(cnpe__akur)
            urzx__jkjq = btpua__rcr + 7 >> 3
            lnk__gaagr = np.empty(urzx__jkjq, np.uint8)
            kksvg__iqgm = 0
            for A in zghj__tvi:
                azw__beke = A._null_bitmap
                for ptsma__lcrb in range(len(A)):
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        azw__beke, ptsma__lcrb)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lnk__gaagr,
                        kksvg__iqgm, xgxzs__dlq)
                    kksvg__iqgm += 1
            return bodo.libs.int_arr_ext.init_integer_array(isjoi__gvc,
                lnk__gaagr)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(axr__rneto.dtype == types.bool_ for axr__rneto in
        arr_list.types) and any(axr__rneto == boolean_array for axr__rneto in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            zghj__tvi = convert_to_nullable_tup(arr_list)
            cnpe__akur = []
            btpua__rcr = 0
            for A in zghj__tvi:
                cnpe__akur.append(A._data)
                btpua__rcr += len(A)
            isjoi__gvc = bodo.libs.array_kernels.concat(cnpe__akur)
            urzx__jkjq = btpua__rcr + 7 >> 3
            lnk__gaagr = np.empty(urzx__jkjq, np.uint8)
            kksvg__iqgm = 0
            for A in zghj__tvi:
                azw__beke = A._null_bitmap
                for ptsma__lcrb in range(len(A)):
                    xgxzs__dlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        azw__beke, ptsma__lcrb)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lnk__gaagr,
                        kksvg__iqgm, xgxzs__dlq)
                    kksvg__iqgm += 1
            return bodo.libs.bool_arr_ext.init_bool_array(isjoi__gvc,
                lnk__gaagr)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            hdkh__caq = []
            for A in arr_list:
                hdkh__caq.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                hdkh__caq), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        gohq__zpwjk = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        zle__lxspi = 'def impl(arr_list):\n'
        zle__lxspi += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({gohq__zpwjk},)), arr_list[0].dtype)
"""
        xsya__seb = {}
        exec(zle__lxspi, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, xsya__seb)
        return xsya__seb['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            btpua__rcr = 0
            for A in arr_list:
                btpua__rcr += len(A)
            hxqd__jleg = np.empty(btpua__rcr, dtype)
            hgfz__tvnv = 0
            for A in arr_list:
                n = len(A)
                hxqd__jleg[hgfz__tvnv:hgfz__tvnv + n] = A
                hgfz__tvnv += n
            return hxqd__jleg
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(axr__rneto,
        (types.Array, IntegerArrayType)) and isinstance(axr__rneto.dtype,
        types.Integer) for axr__rneto in arr_list.types) and any(isinstance
        (axr__rneto, types.Array) and isinstance(axr__rneto.dtype, types.
        Float) for axr__rneto in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            vbam__ekzu = []
            for A in arr_list:
                vbam__ekzu.append(A._data)
            cjo__gzp = bodo.libs.array_kernels.concat(vbam__ekzu)
            xqrf__iiqwg = bodo.libs.map_arr_ext.init_map_arr(cjo__gzp)
            return xqrf__iiqwg
        return impl_map_arr_list
    for dwd__wiiie in arr_list:
        if not isinstance(dwd__wiiie, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(axr__rneto.astype(np.float64) for axr__rneto in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    geam__waole = len(arr_tup.types)
    zle__lxspi = 'def f(arr_tup):\n'
    zle__lxspi += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        geam__waole)), ',' if geam__waole == 1 else '')
    hmey__dmf = {}
    exec(zle__lxspi, {'np': np}, hmey__dmf)
    vgdj__urqs = hmey__dmf['f']
    return vgdj__urqs


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    geam__waole = len(arr_tup.types)
    dnx__aem = find_common_np_dtype(arr_tup.types)
    jbrs__runnw = None
    pim__oyp = ''
    if isinstance(dnx__aem, types.Integer):
        jbrs__runnw = bodo.libs.int_arr_ext.IntDtype(dnx__aem)
        pim__oyp = '.astype(out_dtype, False)'
    zle__lxspi = 'def f(arr_tup):\n'
    zle__lxspi += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, pim__oyp) for i in range(geam__waole)), ',' if 
        geam__waole == 1 else '')
    hmey__dmf = {}
    exec(zle__lxspi, {'bodo': bodo, 'out_dtype': jbrs__runnw}, hmey__dmf)
    dmur__skq = hmey__dmf['f']
    return dmur__skq


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, evdfg__hmd = build_set_seen_na(A)
        return len(s) + int(not dropna and evdfg__hmd)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        acpkl__voop = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        ucwfw__zacl = len(acpkl__voop)
        return bodo.libs.distributed_api.dist_reduce(ucwfw__zacl, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([ilghu__rwi for ilghu__rwi in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        gukn__mpmj = np.finfo(A.dtype(1).dtype).max
    else:
        gukn__mpmj = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        hxqd__jleg = np.empty(n, A.dtype)
        jpz__dtlt = gukn__mpmj
        for i in range(n):
            jpz__dtlt = min(jpz__dtlt, A[i])
            hxqd__jleg[i] = jpz__dtlt
        return hxqd__jleg
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        gukn__mpmj = np.finfo(A.dtype(1).dtype).min
    else:
        gukn__mpmj = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        hxqd__jleg = np.empty(n, A.dtype)
        jpz__dtlt = gukn__mpmj
        for i in range(n):
            jpz__dtlt = max(jpz__dtlt, A[i])
            hxqd__jleg[i] = jpz__dtlt
        return hxqd__jleg
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        zlcl__tdnqv = arr_info_list_to_table([array_to_info(A)])
        ozon__nxnl = 1
        ptw__ogurx = 0
        kqhhv__vgjva = drop_duplicates_table(zlcl__tdnqv, parallel,
            ozon__nxnl, ptw__ogurx, dropna)
        hxqd__jleg = info_to_array(info_from_table(kqhhv__vgjva, 0), A)
        delete_table(zlcl__tdnqv)
        delete_table(kqhhv__vgjva)
        return hxqd__jleg
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    fjc__onhx = bodo.utils.typing.to_nullable_type(arr.dtype)
    fciy__bhius = index_arr
    qqry__hpk = fciy__bhius.dtype

    def impl(arr, index_arr):
        n = len(arr)
        wuvn__dkqcv = init_nested_counts(fjc__onhx)
        qwai__bmcr = init_nested_counts(qqry__hpk)
        for i in range(n):
            rwhp__cofti = index_arr[i]
            if isna(arr, i):
                wuvn__dkqcv = (wuvn__dkqcv[0] + 1,) + wuvn__dkqcv[1:]
                qwai__bmcr = add_nested_counts(qwai__bmcr, rwhp__cofti)
                continue
            rios__xkzz = arr[i]
            if len(rios__xkzz) == 0:
                wuvn__dkqcv = (wuvn__dkqcv[0] + 1,) + wuvn__dkqcv[1:]
                qwai__bmcr = add_nested_counts(qwai__bmcr, rwhp__cofti)
                continue
            wuvn__dkqcv = add_nested_counts(wuvn__dkqcv, rios__xkzz)
            for ilur__pqy in range(len(rios__xkzz)):
                qwai__bmcr = add_nested_counts(qwai__bmcr, rwhp__cofti)
        hxqd__jleg = bodo.utils.utils.alloc_type(wuvn__dkqcv[0], fjc__onhx,
            wuvn__dkqcv[1:])
        dfn__fwu = bodo.utils.utils.alloc_type(wuvn__dkqcv[0], fciy__bhius,
            qwai__bmcr)
        plwn__wzov = 0
        for i in range(n):
            if isna(arr, i):
                setna(hxqd__jleg, plwn__wzov)
                dfn__fwu[plwn__wzov] = index_arr[i]
                plwn__wzov += 1
                continue
            rios__xkzz = arr[i]
            pri__msfl = len(rios__xkzz)
            if pri__msfl == 0:
                setna(hxqd__jleg, plwn__wzov)
                dfn__fwu[plwn__wzov] = index_arr[i]
                plwn__wzov += 1
                continue
            hxqd__jleg[plwn__wzov:plwn__wzov + pri__msfl] = rios__xkzz
            dfn__fwu[plwn__wzov:plwn__wzov + pri__msfl] = index_arr[i]
            plwn__wzov += pri__msfl
        return hxqd__jleg, dfn__fwu
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    fjc__onhx = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        wuvn__dkqcv = init_nested_counts(fjc__onhx)
        for i in range(n):
            if isna(arr, i):
                wuvn__dkqcv = (wuvn__dkqcv[0] + 1,) + wuvn__dkqcv[1:]
                dsef__lihk = 1
            else:
                rios__xkzz = arr[i]
                ldh__etdew = len(rios__xkzz)
                if ldh__etdew == 0:
                    wuvn__dkqcv = (wuvn__dkqcv[0] + 1,) + wuvn__dkqcv[1:]
                    dsef__lihk = 1
                    continue
                else:
                    wuvn__dkqcv = add_nested_counts(wuvn__dkqcv, rios__xkzz)
                    dsef__lihk = ldh__etdew
            if counts[i] != dsef__lihk:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        hxqd__jleg = bodo.utils.utils.alloc_type(wuvn__dkqcv[0], fjc__onhx,
            wuvn__dkqcv[1:])
        plwn__wzov = 0
        for i in range(n):
            if isna(arr, i):
                setna(hxqd__jleg, plwn__wzov)
                plwn__wzov += 1
                continue
            rios__xkzz = arr[i]
            pri__msfl = len(rios__xkzz)
            if pri__msfl == 0:
                setna(hxqd__jleg, plwn__wzov)
                plwn__wzov += 1
                continue
            hxqd__jleg[plwn__wzov:plwn__wzov + pri__msfl] = rios__xkzz
            plwn__wzov += pri__msfl
        return hxqd__jleg
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(ogvfi__dah) for ogvfi__dah in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or arr == string_array_type and not na_empty_as_one
    if na_empty_as_one:
        kdfh__ebxk = 'np.empty(n, np.int64)'
        wouu__qoxhk = 'out_arr[i] = 1'
        mljkr__egvk = 'max(len(arr[i]), 1)'
    else:
        kdfh__ebxk = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        wouu__qoxhk = 'bodo.libs.array_kernels.setna(out_arr, i)'
        mljkr__egvk = 'len(arr[i])'
    zle__lxspi = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {kdfh__ebxk}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {wouu__qoxhk}
        else:
            out_arr[i] = {mljkr__egvk}
    return out_arr
    """
    hmey__dmf = {}
    exec(zle__lxspi, {'bodo': bodo, 'numba': numba, 'np': np}, hmey__dmf)
    impl = hmey__dmf['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert arr == string_array_type
    fciy__bhius = index_arr
    qqry__hpk = fciy__bhius.dtype

    def impl(arr, pat, n, index_arr):
        dsxt__hnjpo = pat is not None and len(pat) > 1
        if dsxt__hnjpo:
            crs__dptea = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        lgpwl__bmo = len(arr)
        fgmbs__miqlw = 0
        znb__sla = 0
        qwai__bmcr = init_nested_counts(qqry__hpk)
        for i in range(lgpwl__bmo):
            rwhp__cofti = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                fgmbs__miqlw += 1
                qwai__bmcr = add_nested_counts(qwai__bmcr, rwhp__cofti)
                continue
            if dsxt__hnjpo:
                rpqad__ztyvp = crs__dptea.split(arr[i], maxsplit=n)
            else:
                rpqad__ztyvp = arr[i].split(pat, n)
            fgmbs__miqlw += len(rpqad__ztyvp)
            for s in rpqad__ztyvp:
                qwai__bmcr = add_nested_counts(qwai__bmcr, rwhp__cofti)
                znb__sla += bodo.libs.str_arr_ext.get_utf8_size(s)
        hxqd__jleg = bodo.libs.str_arr_ext.pre_alloc_string_array(fgmbs__miqlw,
            znb__sla)
        dfn__fwu = bodo.utils.utils.alloc_type(fgmbs__miqlw, fciy__bhius,
            qwai__bmcr)
        fuc__kmed = 0
        for ptsma__lcrb in range(lgpwl__bmo):
            if isna(arr, ptsma__lcrb):
                hxqd__jleg[fuc__kmed] = ''
                bodo.libs.array_kernels.setna(hxqd__jleg, fuc__kmed)
                dfn__fwu[fuc__kmed] = index_arr[ptsma__lcrb]
                fuc__kmed += 1
                continue
            if dsxt__hnjpo:
                rpqad__ztyvp = crs__dptea.split(arr[ptsma__lcrb], maxsplit=n)
            else:
                rpqad__ztyvp = arr[ptsma__lcrb].split(pat, n)
            ovmsd__ifpuy = len(rpqad__ztyvp)
            hxqd__jleg[fuc__kmed:fuc__kmed + ovmsd__ifpuy] = rpqad__ztyvp
            dfn__fwu[fuc__kmed:fuc__kmed + ovmsd__ifpuy] = index_arr[
                ptsma__lcrb]
            fuc__kmed += ovmsd__ifpuy
        return hxqd__jleg, dfn__fwu
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
            hxqd__jleg = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hxqd__jleg[i] = np.nan
            return hxqd__jleg
        return impl_float

    def impl(n, arr):
        numba.parfors.parfor.init_prange()
        hxqd__jleg = bodo.utils.utils.alloc_type(n, arr, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(hxqd__jleg, i)
        return hxqd__jleg
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
    ssdcf__fqm = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            hxqd__jleg = bodo.utils.utils.alloc_type(new_len, ssdcf__fqm)
            bodo.libs.str_arr_ext.str_copy_ptr(hxqd__jleg.ctypes, 0, A.
                ctypes, old_size)
            return hxqd__jleg
        return impl_char

    def impl(A, old_size, new_len):
        hxqd__jleg = bodo.utils.utils.alloc_type(new_len, ssdcf__fqm, (-1,))
        hxqd__jleg[:old_size] = A[:old_size]
        return hxqd__jleg
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    vmi__admc = math.ceil((stop - start) / step)
    return int(max(vmi__admc, 0))


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
    if any(isinstance(ilghu__rwi, types.Complex) for ilghu__rwi in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            wqvjx__svr = (stop - start) / step
            vmi__admc = math.ceil(wqvjx__svr.real)
            xxgj__vgdt = math.ceil(wqvjx__svr.imag)
            oqv__nep = int(max(min(xxgj__vgdt, vmi__admc), 0))
            arr = np.empty(oqv__nep, dtype)
            for i in numba.parfors.parfor.internal_prange(oqv__nep):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            oqv__nep = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(oqv__nep, dtype)
            for i in numba.parfors.parfor.internal_prange(oqv__nep):
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
        ckp__whxwa = arr,
        if not inplace:
            ckp__whxwa = arr.copy(),
        znj__vhr = bodo.libs.str_arr_ext.to_list_if_immutable_arr(ckp__whxwa)
        oheo__sudt = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(znj__vhr, 0, n, oheo__sudt)
        if not ascending:
            bodo.libs.timsort.reverseRange(znj__vhr, 0, n, oheo__sudt)
        bodo.libs.str_arr_ext.cp_str_list_to_array(ckp__whxwa, znj__vhr)
        return ckp__whxwa[0]
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
        xqrf__iiqwg = []
        for i in range(n):
            if A[i]:
                xqrf__iiqwg.append(i + offset)
        return np.array(xqrf__iiqwg, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    ssdcf__fqm = element_type(A)
    if ssdcf__fqm == types.unicode_type:
        null_value = '""'
    elif ssdcf__fqm == types.bool_:
        null_value = 'False'
    elif ssdcf__fqm == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif ssdcf__fqm == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    fuc__kmed = 'i'
    qco__zleb = False
    dee__hmkqn = get_overload_const_str(method)
    if dee__hmkqn in ('ffill', 'pad'):
        eum__kxd = 'n'
        send_right = True
    elif dee__hmkqn in ('backfill', 'bfill'):
        eum__kxd = 'n-1, -1, -1'
        send_right = False
        if ssdcf__fqm == types.unicode_type:
            fuc__kmed = '(n - 1) - i'
            qco__zleb = True
    zle__lxspi = 'def impl(A, method, parallel=False):\n'
    zle__lxspi += '  has_last_value = False\n'
    zle__lxspi += f'  last_value = {null_value}\n'
    zle__lxspi += '  if parallel:\n'
    zle__lxspi += '    rank = bodo.libs.distributed_api.get_rank()\n'
    zle__lxspi += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    zle__lxspi += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    zle__lxspi += '  n = len(A)\n'
    zle__lxspi += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    zle__lxspi += f'  for i in range({eum__kxd}):\n'
    zle__lxspi += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    zle__lxspi += (
        f'      bodo.libs.array_kernels.setna(out_arr, {fuc__kmed})\n')
    zle__lxspi += '      continue\n'
    zle__lxspi += '    s = A[i]\n'
    zle__lxspi += '    if bodo.libs.array_kernels.isna(A, i):\n'
    zle__lxspi += '      s = last_value\n'
    zle__lxspi += f'    out_arr[{fuc__kmed}] = s\n'
    zle__lxspi += '    last_value = s\n'
    zle__lxspi += '    has_last_value = True\n'
    if qco__zleb:
        zle__lxspi += '  return out_arr[::-1]\n'
    else:
        zle__lxspi += '  return out_arr\n'
    aebyl__udie = {}
    exec(zle__lxspi, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm}, aebyl__udie)
    impl = aebyl__udie['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        mdr__ylzy = 0
        xopmx__lspar = n_pes - 1
        krf__xhkzp = np.int32(rank + 1)
        fiv__uavi = np.int32(rank - 1)
        cmncn__npnzw = len(in_arr) - 1
        fijfi__ehsa = -1
        gibr__idx = -1
    else:
        mdr__ylzy = n_pes - 1
        xopmx__lspar = 0
        krf__xhkzp = np.int32(rank - 1)
        fiv__uavi = np.int32(rank + 1)
        cmncn__npnzw = 0
        fijfi__ehsa = len(in_arr)
        gibr__idx = 1
    niufw__bydx = np.int32(bodo.hiframes.rolling.comm_border_tag)
    fnsjl__vuiys = np.empty(1, dtype=np.bool_)
    uew__dsndn = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ggi__htn = np.empty(1, dtype=np.bool_)
    polw__eobj = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    idp__pwce = False
    lsj__pve = null_value
    for i in range(cmncn__npnzw, fijfi__ehsa, gibr__idx):
        if not isna(in_arr, i):
            idp__pwce = True
            lsj__pve = in_arr[i]
            break
    if rank != mdr__ylzy:
        yvy__qwe = bodo.libs.distributed_api.irecv(fnsjl__vuiys, 1,
            fiv__uavi, niufw__bydx, True)
        bodo.libs.distributed_api.wait(yvy__qwe, True)
        uyla__kdlw = bodo.libs.distributed_api.irecv(uew__dsndn, 1,
            fiv__uavi, niufw__bydx, True)
        bodo.libs.distributed_api.wait(uyla__kdlw, True)
        gnd__smyk = fnsjl__vuiys[0]
        wpprt__jnj = uew__dsndn[0]
    else:
        gnd__smyk = False
        wpprt__jnj = null_value
    if idp__pwce:
        ggi__htn[0] = idp__pwce
        polw__eobj[0] = lsj__pve
    else:
        ggi__htn[0] = gnd__smyk
        polw__eobj[0] = wpprt__jnj
    if rank != xopmx__lspar:
        zba__kjak = bodo.libs.distributed_api.isend(ggi__htn, 1, krf__xhkzp,
            niufw__bydx, True)
        wkguc__ycv = bodo.libs.distributed_api.isend(polw__eobj, 1,
            krf__xhkzp, niufw__bydx, True)
    return gnd__smyk, wpprt__jnj


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    gcdg__yuks = {'axis': axis, 'kind': kind, 'order': order}
    mzn__ygfax = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', gcdg__yuks, mzn__ygfax, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    ssdcf__fqm = A
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            lgpwl__bmo = len(A)
            hxqd__jleg = bodo.utils.utils.alloc_type(lgpwl__bmo * repeats,
                ssdcf__fqm, (-1,))
            for i in range(lgpwl__bmo):
                fuc__kmed = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for ptsma__lcrb in range(repeats):
                        bodo.libs.array_kernels.setna(hxqd__jleg, fuc__kmed +
                            ptsma__lcrb)
                else:
                    hxqd__jleg[fuc__kmed:fuc__kmed + repeats] = A[i]
            return hxqd__jleg
        return impl_int

    def impl_arr(A, repeats):
        lgpwl__bmo = len(A)
        hxqd__jleg = bodo.utils.utils.alloc_type(repeats.sum(), ssdcf__fqm,
            (-1,))
        fuc__kmed = 0
        for i in range(lgpwl__bmo):
            yln__ceu = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for ptsma__lcrb in range(yln__ceu):
                    bodo.libs.array_kernels.setna(hxqd__jleg, fuc__kmed +
                        ptsma__lcrb)
            else:
                hxqd__jleg[fuc__kmed:fuc__kmed + yln__ceu] = A[i]
            fuc__kmed += yln__ceu
        return hxqd__jleg
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
        ufce__gyfp = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(ufce__gyfp, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        xbuzp__oucau = bodo.libs.array_kernels.concat([A1, A2])
        dgi__xqifm = bodo.libs.array_kernels.unique(xbuzp__oucau)
        return pd.Series(dgi__xqifm).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    gcdg__yuks = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    mzn__ygfax = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', gcdg__yuks, mzn__ygfax, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        qpga__kuzs = bodo.libs.array_kernels.unique(A1)
        lhtz__xsrra = bodo.libs.array_kernels.unique(A2)
        xbuzp__oucau = bodo.libs.array_kernels.concat([qpga__kuzs, lhtz__xsrra]
            )
        pmpqa__uokww = pd.Series(xbuzp__oucau).sort_values().values
        return slice_array_intersect1d(pmpqa__uokww)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    gtql__cfi = arr[1:] == arr[:-1]
    return arr[:-1][gtql__cfi]


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    gcdg__yuks = {'assume_unique': assume_unique}
    mzn__ygfax = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', gcdg__yuks, mzn__ygfax, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        qpga__kuzs = bodo.libs.array_kernels.unique(A1)
        lhtz__xsrra = bodo.libs.array_kernels.unique(A2)
        gtql__cfi = calculate_mask_setdiff1d(qpga__kuzs, lhtz__xsrra)
        return pd.Series(qpga__kuzs[gtql__cfi]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    gtql__cfi = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        gtql__cfi &= A1 != A2[i]
    return gtql__cfi


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    gcdg__yuks = {'retstep': retstep, 'axis': axis}
    mzn__ygfax = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', gcdg__yuks, mzn__ygfax, 'numpy')
    gqap__hnc = False
    if is_overload_none(dtype):
        ssdcf__fqm = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            gqap__hnc = True
        ssdcf__fqm = numba.np.numpy_support.as_dtype(dtype).type
    if gqap__hnc:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            wvhp__val = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hxqd__jleg = np.empty(num, ssdcf__fqm)
            for i in numba.parfors.parfor.internal_prange(num):
                hxqd__jleg[i] = ssdcf__fqm(np.floor(start + i * wvhp__val))
            return hxqd__jleg
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            wvhp__val = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hxqd__jleg = np.empty(num, ssdcf__fqm)
            for i in numba.parfors.parfor.internal_prange(num):
                hxqd__jleg[i] = ssdcf__fqm(start + i * wvhp__val)
            return hxqd__jleg
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
        geam__waole = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                geam__waole += A[i] == val
        return geam__waole > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    gcdg__yuks = {'axis': axis, 'out': out, 'keepdims': keepdims}
    mzn__ygfax = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', gcdg__yuks, mzn__ygfax, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        geam__waole = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                geam__waole += int(bool(A[i]))
        return geam__waole > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    gcdg__yuks = {'axis': axis, 'out': out, 'keepdims': keepdims}
    mzn__ygfax = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', gcdg__yuks, mzn__ygfax, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        geam__waole = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                geam__waole += int(bool(A[i]))
        return geam__waole == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    gcdg__yuks = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    mzn__ygfax = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', gcdg__yuks, mzn__ygfax, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        gbvx__iqprp = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            hxqd__jleg = np.empty(n, gbvx__iqprp)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(hxqd__jleg, i)
                    continue
                hxqd__jleg[i] = np_cbrt_scalar(A[i], gbvx__iqprp)
            return hxqd__jleg
        return impl_arr
    gbvx__iqprp = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, gbvx__iqprp)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    itdt__pkib = x < 0
    if itdt__pkib:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if itdt__pkib:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    vwe__rmb = isinstance(tup, (types.BaseTuple, types.List))
    dmkat__vxcc = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for dwd__wiiie in tup.types:
            vwe__rmb = vwe__rmb and bodo.utils.utils.is_array_typ(dwd__wiiie,
                False)
    elif isinstance(tup, types.List):
        vwe__rmb = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif dmkat__vxcc:
        twgfr__siyzo = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for dwd__wiiie in twgfr__siyzo.types:
            dmkat__vxcc = dmkat__vxcc and bodo.utils.utils.is_array_typ(
                dwd__wiiie, False)
    if not (vwe__rmb or dmkat__vxcc):
        return
    if dmkat__vxcc:

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
    gcdg__yuks = {'check_valid': check_valid, 'tol': tol}
    mzn__ygfax = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', gcdg__yuks,
        mzn__ygfax, 'numpy')
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
        lzy__bidt = mean.shape[0]
        egkru__ufuk = size, lzy__bidt
        smnd__kdgb = np.random.standard_normal(egkru__ufuk)
        cov = cov.astype(np.float64)
        pvqcg__oyco, s, mhfd__ylwkl = np.linalg.svd(cov)
        res = np.dot(smnd__kdgb, np.sqrt(s).reshape(lzy__bidt, 1) * mhfd__ylwkl
            )
        bfhf__cdm = res + mean
        return bfhf__cdm
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
            dxr__wqgh = bodo.hiframes.series_kernels._get_type_max_value(arr)
            jcwqc__nfn = typing.builtins.IndexValue(-1, dxr__wqgh)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                iam__jnbi = typing.builtins.IndexValue(i, arr[i])
                jcwqc__nfn = min(jcwqc__nfn, iam__jnbi)
            return jcwqc__nfn.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tvgg__myp = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            nslok__qht = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            dxr__wqgh = tvgg__myp(len(arr.dtype.categories) + 1)
            jcwqc__nfn = typing.builtins.IndexValue(-1, dxr__wqgh)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                iam__jnbi = typing.builtins.IndexValue(i, nslok__qht[i])
                jcwqc__nfn = min(jcwqc__nfn, iam__jnbi)
            return jcwqc__nfn.index
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
            dxr__wqgh = bodo.hiframes.series_kernels._get_type_min_value(arr)
            jcwqc__nfn = typing.builtins.IndexValue(-1, dxr__wqgh)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                iam__jnbi = typing.builtins.IndexValue(i, arr[i])
                jcwqc__nfn = max(jcwqc__nfn, iam__jnbi)
            return jcwqc__nfn.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tvgg__myp = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            nslok__qht = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            dxr__wqgh = tvgg__myp(-1)
            jcwqc__nfn = typing.builtins.IndexValue(-1, dxr__wqgh)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                iam__jnbi = typing.builtins.IndexValue(i, nslok__qht[i])
                jcwqc__nfn = max(jcwqc__nfn, iam__jnbi)
            return jcwqc__nfn.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
