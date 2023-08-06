import atexit
import datetime
import operator
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, models, overload, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, is_overload_false, is_overload_none, raise_bodo_error
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, numba_to_c_type, tuple_to_scalar
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('comm_req_alloc', hdist.comm_req_alloc)
ll.add_symbol('comm_req_dealloc', hdist.comm_req_dealloc)
ll.add_symbol('req_array_setitem', hdist.req_array_setitem)
ll.add_symbol('dist_waitall', hdist.dist_waitall)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    ttl__nvil = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, ttl__nvil, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    ttl__nvil = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, ttl__nvil, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            ttl__nvil = get_type_enum(arr)
            return _isend(arr.ctypes, size, ttl__nvil, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        ttl__nvil = np.int32(numba_to_c_type(arr.dtype))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            nrwz__tot = size + 7 >> 3
            pihyj__udtta = _isend(arr._data.ctypes, size, ttl__nvil, pe,
                tag, cond)
            btzs__frg = _isend(arr._null_bitmap.ctypes, nrwz__tot,
                wmzzl__rcl, pe, tag, cond)
            return pihyj__udtta, btzs__frg
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        nzyk__hnr = np.int32(numba_to_c_type(offset_type))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            yblr__mfec = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(yblr__mfec, pe, tag - 1)
            nrwz__tot = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                nzyk__hnr, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), yblr__mfec,
                wmzzl__rcl, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), nrwz__tot,
                wmzzl__rcl, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            ttl__nvil = get_type_enum(arr)
            return _irecv(arr.ctypes, size, ttl__nvil, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        ttl__nvil = np.int32(numba_to_c_type(arr.dtype))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            nrwz__tot = size + 7 >> 3
            pihyj__udtta = _irecv(arr._data.ctypes, size, ttl__nvil, pe,
                tag, cond)
            btzs__frg = _irecv(arr._null_bitmap.ctypes, nrwz__tot,
                wmzzl__rcl, pe, tag, cond)
            return pihyj__udtta, btzs__frg
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        nzyk__hnr = np.int32(numba_to_c_type(offset_type))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            rwal__pkvbm = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rwal__pkvbm = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        vqm__wsxib = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {rwal__pkvbm}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        lzlzt__ktryr = dict()
        exec(vqm__wsxib, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            nzyk__hnr, 'char_typ_enum': wmzzl__rcl}, lzlzt__ktryr)
        impl = lzlzt__ktryr['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    ttl__nvil = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), ttl__nvil)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        rdeg__szqys = n_pes if rank == root or allgather else 0
        aabd__bflxb = np.empty(rdeg__szqys, dtype)
        c_gather_scalar(send.ctypes, aabd__bflxb.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return aabd__bflxb
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        fzocz__khylv = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], fzocz__khylv)
        return builder.bitcast(fzocz__khylv, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        fzocz__khylv = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(fzocz__khylv)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    pevvk__pckcq = types.unliteral(value)
    if isinstance(pevvk__pckcq, IndexValueType):
        pevvk__pckcq = pevvk__pckcq.val_typ
        ncn__fqbiy = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            ncn__fqbiy.append(types.int64)
            ncn__fqbiy.append(bodo.datetime64ns)
            ncn__fqbiy.append(bodo.timedelta64ns)
            ncn__fqbiy.append(bodo.datetime_date_type)
        if pevvk__pckcq not in ncn__fqbiy:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(pevvk__pckcq))
    typ_enum = np.int32(numba_to_c_type(pevvk__pckcq))

    def impl(value, reduce_op):
        utvc__vxwvg = value_to_ptr(value)
        lfi__hzge = value_to_ptr(value)
        _dist_reduce(utvc__vxwvg, lfi__hzge, reduce_op, typ_enum)
        return load_val_ptr(lfi__hzge, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    pevvk__pckcq = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(pevvk__pckcq))
    oqfcp__sxn = pevvk__pckcq(0)

    def impl(value, reduce_op):
        utvc__vxwvg = value_to_ptr(value)
        lfi__hzge = value_to_ptr(oqfcp__sxn)
        _dist_exscan(utvc__vxwvg, lfi__hzge, reduce_op, typ_enum)
        return load_val_ptr(lfi__hzge, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    yzexw__vfx = 0
    ekq__dlop = 0
    for i in range(len(recv_counts)):
        llb__aijlx = recv_counts[i]
        nrwz__tot = recv_counts_nulls[i]
        rsur__smsd = tmp_null_bytes[yzexw__vfx:yzexw__vfx + nrwz__tot]
        for wts__pahv in range(llb__aijlx):
            set_bit_to(null_bitmap_ptr, ekq__dlop, get_bit(rsur__smsd,
                wts__pahv))
            ekq__dlop += 1
        yzexw__vfx += nrwz__tot


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            ebc__zocq = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ebc__zocq, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            pcogn__lqpmq = data.size
            recv_counts = gather_scalar(np.int32(pcogn__lqpmq), allgather,
                root=root)
            ghzt__cefd = recv_counts.sum()
            ackyk__rmhm = empty_like_type(ghzt__cefd, data)
            utc__iecr = np.empty(1, np.int32)
            if rank == root or allgather:
                utc__iecr = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(pcogn__lqpmq), ackyk__rmhm.
                ctypes, recv_counts.ctypes, utc__iecr.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return ackyk__rmhm.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if data == string_array_type:

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.str_arr_ext.init_str_arr(ackyk__rmhm)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(ackyk__rmhm)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            pcogn__lqpmq = len(data)
            nrwz__tot = pcogn__lqpmq + 7 >> 3
            recv_counts = gather_scalar(np.int32(pcogn__lqpmq), allgather,
                root=root)
            ghzt__cefd = recv_counts.sum()
            ackyk__rmhm = empty_like_type(ghzt__cefd, data)
            utc__iecr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            mhkr__armlu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                utc__iecr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                mhkr__armlu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(pcogn__lqpmq),
                ackyk__rmhm._days_data.ctypes, recv_counts.ctypes,
                utc__iecr.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(pcogn__lqpmq),
                ackyk__rmhm._seconds_data.ctypes, recv_counts.ctypes,
                utc__iecr.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(pcogn__lqpmq
                ), ackyk__rmhm._microseconds_data.ctypes, recv_counts.
                ctypes, utc__iecr.ctypes, np.int32(typ_val), allgather, np.
                int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(nrwz__tot),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                mhkr__armlu.ctypes, wmzzl__rcl, allgather, np.int32(root))
            copy_gathered_null_bytes(ackyk__rmhm._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ackyk__rmhm
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            pcogn__lqpmq = len(data)
            nrwz__tot = pcogn__lqpmq + 7 >> 3
            recv_counts = gather_scalar(np.int32(pcogn__lqpmq), allgather,
                root=root)
            ghzt__cefd = recv_counts.sum()
            ackyk__rmhm = empty_like_type(ghzt__cefd, data)
            utc__iecr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            mhkr__armlu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                utc__iecr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                mhkr__armlu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(pcogn__lqpmq),
                ackyk__rmhm._data.ctypes, recv_counts.ctypes, utc__iecr.
                ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(nrwz__tot),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                mhkr__armlu.ctypes, wmzzl__rcl, allgather, np.int32(root))
            copy_gathered_null_bytes(ackyk__rmhm._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return ackyk__rmhm
        return gatherv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            gdjhs__gfvcv = bodo.gatherv(data._left, allgather, warn_if_rep,
                root)
            qifc__gsr = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(gdjhs__gfvcv,
                qifc__gsr)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ccr__vpcyb = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            cvnd__yfc = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cvnd__yfc, ccr__vpcyb)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        rel__nbd = np.iinfo(np.int64).max
        vri__mkmo = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            start = data._start
            stop = data._stop
            if len(data) == 0:
                start = rel__nbd
                stop = vri__mkmo
            start = bodo.libs.distributed_api.dist_reduce(start, np.int32(
                Reduce_Type.Min.value))
            stop = bodo.libs.distributed_api.dist_reduce(stop, np.int32(
                Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if start == rel__nbd and stop == vri__mkmo:
                start = 0
                stop = 0
            sin__nle = max(0, -(-(stop - start) // data._step))
            if sin__nle < total_len:
                stop = start + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                start = 0
                stop = 0
            return bodo.hiframes.pd_index_ext.init_range_index(start, stop,
                data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            dvo__ytmg = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, dvo__ytmg)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                ackyk__rmhm, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        eqt__rre = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        vqm__wsxib = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        vqm__wsxib += '  T = data\n'
        vqm__wsxib += '  T2 = init_table(T)\n'
        for jycb__snz in data.type_to_blk.values():
            eqt__rre[f'arr_inds_{jycb__snz}'] = np.array(data.
                block_to_arr_ind[jycb__snz], dtype=np.int64)
            vqm__wsxib += (
                f'  arr_list_{jycb__snz} = get_table_block(T, {jycb__snz})\n')
            vqm__wsxib += (
                f'  out_arr_list_{jycb__snz} = alloc_list_like(arr_list_{jycb__snz})\n'
                )
            vqm__wsxib += f'  for i in range(len(arr_list_{jycb__snz})):\n'
            vqm__wsxib += (
                f'    arr_ind_{jycb__snz} = arr_inds_{jycb__snz}[i]\n')
            vqm__wsxib += f"""    ensure_column_unboxed(T, arr_list_{jycb__snz}, i, arr_ind_{jycb__snz})
"""
            vqm__wsxib += f"""    out_arr_{jycb__snz} = bodo.gatherv(arr_list_{jycb__snz}[i], allgather, warn_if_rep, root)
"""
            vqm__wsxib += (
                f'    out_arr_list_{jycb__snz}[i] = out_arr_{jycb__snz}\n')
            vqm__wsxib += (
                f'  T2 = set_table_block(T2, out_arr_list_{jycb__snz}, {jycb__snz})\n'
                )
        vqm__wsxib += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        vqm__wsxib += f'  T2 = set_table_len(T2, length)\n'
        vqm__wsxib += f'  return T2\n'
        lzlzt__ktryr = {}
        exec(vqm__wsxib, eqt__rre, lzlzt__ktryr)
        pdsh__hha = lzlzt__ktryr['impl_table']
        return pdsh__hha
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qtc__dtssp = len(data.columns)
        if qtc__dtssp == 0:
            return (lambda data, allgather=False, warn_if_rep=True, root=
                MPI_ROOT: bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data), ()))
        cpopl__ftfnk = ', '.join(f'g_data_{i}' for i in range(qtc__dtssp))
        fhsws__jykae = bodo.utils.transform.gen_const_tup(data.columns)
        vqm__wsxib = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            kbda__vem = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            eqt__rre = {'bodo': bodo, 'df_type': kbda__vem}
            cpopl__ftfnk = 'T2'
            fhsws__jykae = 'df_type'
            vqm__wsxib += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            vqm__wsxib += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            eqt__rre = {'bodo': bodo}
            for i in range(qtc__dtssp):
                vqm__wsxib += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                vqm__wsxib += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        vqm__wsxib += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqm__wsxib += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        vqm__wsxib += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(cpopl__ftfnk, fhsws__jykae))
        lzlzt__ktryr = {}
        exec(vqm__wsxib, eqt__rre, lzlzt__ktryr)
        rtmp__elat = lzlzt__ktryr['impl_df']
        return rtmp__elat
    if isinstance(data, ArrayItemArrayType):
        nrtm__iznay = np.int32(numba_to_c_type(types.int32))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            mjkg__oxr = bodo.libs.array_item_arr_ext.get_offsets(data)
            kvqi__hnhnd = bodo.libs.array_item_arr_ext.get_data(data)
            apq__phdrb = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            pcogn__lqpmq = len(data)
            ynvoh__vksb = np.empty(pcogn__lqpmq, np.uint32)
            nrwz__tot = pcogn__lqpmq + 7 >> 3
            for i in range(pcogn__lqpmq):
                ynvoh__vksb[i] = mjkg__oxr[i + 1] - mjkg__oxr[i]
            recv_counts = gather_scalar(np.int32(pcogn__lqpmq), allgather,
                root=root)
            ghzt__cefd = recv_counts.sum()
            utc__iecr = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            mhkr__armlu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                utc__iecr = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for gyzxx__gwz in range(len(recv_counts)):
                    recv_counts_nulls[gyzxx__gwz] = recv_counts[gyzxx__gwz
                        ] + 7 >> 3
                mhkr__armlu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            cwmy__wqlzu = np.empty(ghzt__cefd + 1, np.uint32)
            ouu__afqwq = bodo.gatherv(kvqi__hnhnd, allgather, warn_if_rep, root
                )
            ofbzd__ukxbv = np.empty(ghzt__cefd + 7 >> 3, np.uint8)
            c_gatherv(ynvoh__vksb.ctypes, np.int32(pcogn__lqpmq),
                cwmy__wqlzu.ctypes, recv_counts.ctypes, utc__iecr.ctypes,
                nrtm__iznay, allgather, np.int32(root))
            c_gatherv(apq__phdrb.ctypes, np.int32(nrwz__tot),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                mhkr__armlu.ctypes, wmzzl__rcl, allgather, np.int32(root))
            dummy_use(data)
            qtalk__blm = np.empty(ghzt__cefd + 1, np.uint64)
            convert_len_arr_to_offset(cwmy__wqlzu.ctypes, qtalk__blm.ctypes,
                ghzt__cefd)
            copy_gathered_null_bytes(ofbzd__ukxbv.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                ghzt__cefd, ouu__afqwq, qtalk__blm, ofbzd__ukxbv)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ijdzz__hxh = data.names
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            qdqa__ccvv = bodo.libs.struct_arr_ext.get_data(data)
            uxrk__lzhqb = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            kaaie__yoccl = bodo.gatherv(qdqa__ccvv, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            pcogn__lqpmq = len(data)
            nrwz__tot = pcogn__lqpmq + 7 >> 3
            recv_counts = gather_scalar(np.int32(pcogn__lqpmq), allgather,
                root=root)
            ghzt__cefd = recv_counts.sum()
            ibc__dfzl = np.empty(ghzt__cefd + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            mhkr__armlu = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                mhkr__armlu = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(uxrk__lzhqb.ctypes, np.int32(nrwz__tot),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                mhkr__armlu.ctypes, wmzzl__rcl, allgather, np.int32(root))
            copy_gathered_null_bytes(ibc__dfzl.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(kaaie__yoccl,
                ibc__dfzl, ijdzz__hxh)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(ackyk__rmhm)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.tuple_arr_ext.init_tuple_arr(ackyk__rmhm)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            ackyk__rmhm = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.map_arr_ext.init_map_arr(ackyk__rmhm)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ackyk__rmhm = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            xhhsp__muq = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            etdq__duz = bodo.gatherv(data.indptr, allgather, warn_if_rep, root)
            pscdj__vhppo = gather_scalar(data.shape[0], allgather, root=root)
            suypu__nzq = pscdj__vhppo.sum()
            qtc__dtssp = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            ndku__xnyte = np.empty(suypu__nzq + 1, np.int64)
            xhhsp__muq = xhhsp__muq.astype(np.int64)
            ndku__xnyte[0] = 0
            rowy__ypu = 1
            naf__ribgn = 0
            for hdqtk__xjss in pscdj__vhppo:
                for izvci__lcism in range(hdqtk__xjss):
                    ixry__soxi = etdq__duz[naf__ribgn + 1] - etdq__duz[
                        naf__ribgn]
                    ndku__xnyte[rowy__ypu] = ndku__xnyte[rowy__ypu - 1
                        ] + ixry__soxi
                    rowy__ypu += 1
                    naf__ribgn += 1
                naf__ribgn += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(ackyk__rmhm,
                xhhsp__muq, ndku__xnyte, (suypu__nzq, qtc__dtssp))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        vqm__wsxib = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        vqm__wsxib += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bodo': bodo}, lzlzt__ktryr)
        xdca__iny = lzlzt__ktryr['impl_tuple']
        return xdca__iny
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    vqm__wsxib = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    vqm__wsxib += '    if random:\n'
    vqm__wsxib += '        if random_seed is None:\n'
    vqm__wsxib += '            random = 1\n'
    vqm__wsxib += '        else:\n'
    vqm__wsxib += '            random = 2\n'
    vqm__wsxib += '    if random_seed is None:\n'
    vqm__wsxib += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        jpav__icx = data
        qtc__dtssp = len(jpav__icx.columns)
        for i in range(qtc__dtssp):
            vqm__wsxib += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        vqm__wsxib += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        cpopl__ftfnk = ', '.join(f'data_{i}' for i in range(qtc__dtssp))
        vqm__wsxib += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(rnrx__ikj) for
            rnrx__ikj in range(qtc__dtssp))))
        vqm__wsxib += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        vqm__wsxib += '    if dests is None:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqm__wsxib += '    else:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for njp__orf in range(qtc__dtssp):
            vqm__wsxib += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(njp__orf))
        vqm__wsxib += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(qtc__dtssp))
        vqm__wsxib += '    delete_table(out_table)\n'
        vqm__wsxib += '    if parallel:\n'
        vqm__wsxib += '        delete_table(table_total)\n'
        cpopl__ftfnk = ', '.join('out_arr_{}'.format(i) for i in range(
            qtc__dtssp))
        fhsws__jykae = bodo.utils.transform.gen_const_tup(jpav__icx.columns)
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        vqm__wsxib += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, {})\n'
            .format(cpopl__ftfnk, index, fhsws__jykae))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        vqm__wsxib += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        vqm__wsxib += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        vqm__wsxib += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        vqm__wsxib += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        vqm__wsxib += '    if dests is None:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqm__wsxib += '    else:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        vqm__wsxib += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        vqm__wsxib += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        vqm__wsxib += '    delete_table(out_table)\n'
        vqm__wsxib += '    if parallel:\n'
        vqm__wsxib += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        vqm__wsxib += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        vqm__wsxib += '    if not parallel:\n'
        vqm__wsxib += '        return data\n'
        vqm__wsxib += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        vqm__wsxib += '    if dests is None:\n'
        vqm__wsxib += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        vqm__wsxib += '    elif bodo.get_rank() not in dests:\n'
        vqm__wsxib += '        dim0_local_size = 0\n'
        vqm__wsxib += '    else:\n'
        vqm__wsxib += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        vqm__wsxib += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        vqm__wsxib += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        vqm__wsxib += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        vqm__wsxib += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        vqm__wsxib += '    if dests is None:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        vqm__wsxib += '    else:\n'
        vqm__wsxib += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        vqm__wsxib += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        vqm__wsxib += '    delete_table(out_table)\n'
        vqm__wsxib += '    if parallel:\n'
        vqm__wsxib += '        delete_table(table_total)\n'
        vqm__wsxib += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    lzlzt__ktryr = {}
    exec(vqm__wsxib, {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table},
        lzlzt__ktryr)
    impl = lzlzt__ktryr['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, parallel=False):
    vqm__wsxib = 'def impl(data, seed=None, dests=None, parallel=False):\n'
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        vqm__wsxib += '    if seed is None:\n'
        vqm__wsxib += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        vqm__wsxib += '    np.random.seed(seed)\n'
        vqm__wsxib += '    if not parallel:\n'
        vqm__wsxib += '        data = data.copy()\n'
        vqm__wsxib += '        np.random.shuffle(data)\n'
        vqm__wsxib += '        return data\n'
        vqm__wsxib += '    else:\n'
        vqm__wsxib += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        vqm__wsxib += '        permutation = np.arange(dim0_global_size)\n'
        vqm__wsxib += '        np.random.shuffle(permutation)\n'
        vqm__wsxib += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        vqm__wsxib += """        output = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        vqm__wsxib += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        vqm__wsxib += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation))
"""
        vqm__wsxib += '        return output\n'
    else:
        vqm__wsxib += """    return bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
    lzlzt__ktryr = {}
    exec(vqm__wsxib, {'np': np, 'bodo': bodo}, lzlzt__ktryr)
    impl = lzlzt__ktryr['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    dpzsd__coeir = np.empty(sendcounts_nulls.sum(), np.uint8)
    yzexw__vfx = 0
    ekq__dlop = 0
    for seirq__epd in range(len(sendcounts)):
        llb__aijlx = sendcounts[seirq__epd]
        nrwz__tot = sendcounts_nulls[seirq__epd]
        rsur__smsd = dpzsd__coeir[yzexw__vfx:yzexw__vfx + nrwz__tot]
        for wts__pahv in range(llb__aijlx):
            set_bit_to_arr(rsur__smsd, wts__pahv, get_bit_bitmap(
                null_bitmap_ptr, ekq__dlop))
            ekq__dlop += 1
        yzexw__vfx += nrwz__tot
    return dpzsd__coeir


def _bcast_dtype(data):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    mwg__sizt = MPI.COMM_WORLD
    data = mwg__sizt.bcast(data)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    imbl__phs = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    vwld__mmoe = (0,) * imbl__phs

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        gexem__ait = np.ascontiguousarray(data)
        pvp__lzzr = data.ctypes
        unask__umook = vwld__mmoe
        if rank == MPI_ROOT:
            unask__umook = gexem__ait.shape
        unask__umook = bcast_tuple(unask__umook)
        bubvx__gda = get_tuple_prod(unask__umook[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            unask__umook[0])
        send_counts *= bubvx__gda
        pcogn__lqpmq = send_counts[rank]
        wls__lozng = np.empty(pcogn__lqpmq, dtype)
        utc__iecr = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(pvp__lzzr, send_counts.ctypes, utc__iecr.ctypes,
            wls__lozng.ctypes, np.int32(pcogn__lqpmq), np.int32(typ_val))
        return wls__lozng.reshape((-1,) + unask__umook[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        tmm__iqd = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], tmm__iqd)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        ccr__vpcyb = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=ccr__vpcyb)
        pjp__pei = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(pjp__pei)
        return pd.Index(arr, name=ccr__vpcyb)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ccr__vpcyb = _get_name_value_for_type(dtype.name_typ)
        ijdzz__hxh = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        hhuhs__sdpv = tuple(get_value_for_type(t) for t in dtype.array_types)
        val = pd.MultiIndex.from_arrays(hhuhs__sdpv, names=ijdzz__hxh)
        val.name = ccr__vpcyb
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        ccr__vpcyb = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=ccr__vpcyb)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hhuhs__sdpv = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({ccr__vpcyb: arr for ccr__vpcyb, arr in zip(
            dtype.columns, hhuhs__sdpv)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        pjp__pei = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(pjp__pei[0], pjp__pei[0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if data in [binary_array_type, string_array_type]:
        nrtm__iznay = np.int32(numba_to_c_type(types.int32))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            rwal__pkvbm = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rwal__pkvbm = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        vqm__wsxib = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {rwal__pkvbm}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        lzlzt__ktryr = dict()
        exec(vqm__wsxib, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            nrtm__iznay, 'char_typ_enum': wmzzl__rcl}, lzlzt__ktryr)
        impl = lzlzt__ktryr['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        nrtm__iznay = np.int32(numba_to_c_type(types.int32))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            yoa__ysb = bodo.libs.array_item_arr_ext.get_offsets(data)
            fyhul__nbx = bodo.libs.array_item_arr_ext.get_data(data)
            bgkd__vewx = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            krb__jnnw = bcast_scalar(len(data))
            wiat__wgvm = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                wiat__wgvm[i] = yoa__ysb[i + 1] - yoa__ysb[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                krb__jnnw)
            utc__iecr = bodo.ir.join.calc_disp(send_counts)
            pfmg__ovgny = np.empty(n_pes, np.int32)
            if rank == 0:
                kpsh__ajzal = 0
                for i in range(n_pes):
                    xeuc__pdfq = 0
                    for izvci__lcism in range(send_counts[i]):
                        xeuc__pdfq += wiat__wgvm[kpsh__ajzal]
                        kpsh__ajzal += 1
                    pfmg__ovgny[i] = xeuc__pdfq
            bcast(pfmg__ovgny)
            npou__lyvei = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                npou__lyvei[i] = send_counts[i] + 7 >> 3
            mhkr__armlu = bodo.ir.join.calc_disp(npou__lyvei)
            pcogn__lqpmq = send_counts[rank]
            adbw__ylm = np.empty(pcogn__lqpmq + 1, np_offset_type)
            hzefe__eadrr = bodo.libs.distributed_api.scatterv_impl(fyhul__nbx,
                pfmg__ovgny)
            xnhtp__nan = pcogn__lqpmq + 7 >> 3
            art__ajxj = np.empty(xnhtp__nan, np.uint8)
            zaxru__djh = np.empty(pcogn__lqpmq, np.uint32)
            c_scatterv(wiat__wgvm.ctypes, send_counts.ctypes, utc__iecr.
                ctypes, zaxru__djh.ctypes, np.int32(pcogn__lqpmq), nrtm__iznay)
            convert_len_arr_to_offset(zaxru__djh.ctypes, adbw__ylm.ctypes,
                pcogn__lqpmq)
            mswm__ldfa = get_scatter_null_bytes_buff(bgkd__vewx.ctypes,
                send_counts, npou__lyvei)
            c_scatterv(mswm__ldfa.ctypes, npou__lyvei.ctypes, mhkr__armlu.
                ctypes, art__ajxj.ctypes, np.int32(xnhtp__nan), wmzzl__rcl)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                pcogn__lqpmq, hzefe__eadrr, adbw__ylm, art__ajxj)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            ibk__fjx = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            ibk__fjx = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            ibk__fjx = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            ibk__fjx = bodo.hiframes.datetime_date_ext.init_datetime_date_array

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            gexem__ait = data._data
            uxrk__lzhqb = data._null_bitmap
            dwcpf__pma = len(gexem__ait)
            prujh__fmg = _scatterv_np(gexem__ait, send_counts)
            krb__jnnw = bcast_scalar(dwcpf__pma)
            iwj__fsd = len(prujh__fmg) + 7 >> 3
            zrun__uenfa = np.empty(iwj__fsd, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                krb__jnnw)
            npou__lyvei = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                npou__lyvei[i] = send_counts[i] + 7 >> 3
            mhkr__armlu = bodo.ir.join.calc_disp(npou__lyvei)
            mswm__ldfa = get_scatter_null_bytes_buff(uxrk__lzhqb.ctypes,
                send_counts, npou__lyvei)
            c_scatterv(mswm__ldfa.ctypes, npou__lyvei.ctypes, mhkr__armlu.
                ctypes, zrun__uenfa.ctypes, np.int32(iwj__fsd), wmzzl__rcl)
            return ibk__fjx(prujh__fmg, zrun__uenfa)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            hgq__kikel = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            qtv__ijmqt = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(hgq__kikel,
                qtv__ijmqt)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            jquct__rsm = data._step
            ccr__vpcyb = data._name
            ccr__vpcyb = bcast_scalar(ccr__vpcyb)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            jquct__rsm = bcast_scalar(jquct__rsm)
            mleax__lwexq = bodo.libs.array_kernels.calc_nitems(start, stop,
                jquct__rsm)
            chunk_start = bodo.libs.distributed_api.get_start(mleax__lwexq,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(
                mleax__lwexq, n_pes, rank)
            lqn__cjq = start + jquct__rsm * chunk_start
            tgiz__kaxuo = start + jquct__rsm * (chunk_start + chunk_count)
            tgiz__kaxuo = min(tgiz__kaxuo, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(lqn__cjq,
                tgiz__kaxuo, jquct__rsm, ccr__vpcyb)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        dvo__ytmg = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            gexem__ait = data._data
            ccr__vpcyb = data._name
            ccr__vpcyb = bcast_scalar(ccr__vpcyb)
            arr = bodo.libs.distributed_api.scatterv_impl(gexem__ait,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                ccr__vpcyb, dvo__ytmg)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            gexem__ait = data._data
            ccr__vpcyb = data._name
            ccr__vpcyb = bcast_scalar(ccr__vpcyb)
            arr = bodo.libs.distributed_api.scatterv_impl(gexem__ait,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, ccr__vpcyb)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            ackyk__rmhm = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            ccr__vpcyb = bcast_scalar(data._name)
            ijdzz__hxh = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                ackyk__rmhm, ijdzz__hxh, ccr__vpcyb)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ccr__vpcyb = bodo.hiframes.pd_series_ext.get_series_name(data)
            hfksn__exm = bcast_scalar(ccr__vpcyb)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            cvnd__yfc = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cvnd__yfc, hfksn__exm)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qtc__dtssp = len(data.columns)
        cpopl__ftfnk = ', '.join('g_data_{}'.format(i) for i in range(
            qtc__dtssp))
        fhsws__jykae = bodo.utils.transform.gen_const_tup(data.columns)
        vqm__wsxib = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(qtc__dtssp):
            vqm__wsxib += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            vqm__wsxib += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        vqm__wsxib += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqm__wsxib += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        vqm__wsxib += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(cpopl__ftfnk, fhsws__jykae))
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bodo': bodo}, lzlzt__ktryr)
        rtmp__elat = lzlzt__ktryr['impl_df']
        return rtmp__elat
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            ebc__zocq = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ebc__zocq, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        vqm__wsxib = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        vqm__wsxib += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bodo': bodo}, lzlzt__ktryr)
        xdca__iny = lzlzt__ktryr['impl_tuple']
        return xdca__iny
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data):
    if isinstance(data, types.Array):

        def bcast_impl(data):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0)
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0)
            bcast(data._null_bitmap)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data):
            bcast(data._data)
            bcast(data._null_bitmap)
            return
        return bcast_impl_int_arr
    if data in [binary_array_type, string_array_type]:
        nzyk__hnr = np.int32(numba_to_c_type(offset_type))
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data):
            pcogn__lqpmq = len(data)
            dphx__ebco = num_total_chars(data)
            assert pcogn__lqpmq < INT_MAX
            assert dphx__ebco < INT_MAX
            dzzek__gho = get_offset_ptr(data)
            pvp__lzzr = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            nrwz__tot = pcogn__lqpmq + 7 >> 3
            c_bcast(dzzek__gho, np.int32(pcogn__lqpmq + 1), nzyk__hnr, np.
                array([-1]).ctypes, 0)
            c_bcast(pvp__lzzr, np.int32(dphx__ebco), wmzzl__rcl, np.array([
                -1]).ctypes, 0)
            c_bcast(null_bitmap_ptr, np.int32(nrwz__tot), wmzzl__rcl, np.
                array([-1]).ctypes, 0)
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32))


def bcast_scalar(val):
    return val


@overload(bcast_scalar, no_unliteral=True)
def bcast_scalar_overload(val):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise_bodo_error(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val: None
    if val == bodo.string_type:
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != MPI_ROOT:
                rbzso__coh = 0
                uyuzb__sec = np.empty(0, np.uint8).ctypes
            else:
                uyuzb__sec, rbzso__coh = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            rbzso__coh = bodo.libs.distributed_api.bcast_scalar(rbzso__coh)
            if rank != MPI_ROOT:
                pyh__pcq = np.empty(rbzso__coh + 1, np.uint8)
                pyh__pcq[rbzso__coh] = 0
                uyuzb__sec = pyh__pcq.ctypes
            c_bcast(uyuzb__sec, np.int32(rbzso__coh), wmzzl__rcl, np.array(
                [-1]).ctypes, 0)
            return bodo.libs.str_arr_ext.decode_utf8(uyuzb__sec, rbzso__coh)
        return impl_str
    typ_val = numba_to_c_type(val)
    vqm__wsxib = (
        """def bcast_scalar_impl(val):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({}), np.array([-1]).ctypes, 0)
  return send[0]
"""
        .format(typ_val))
    dtype = numba.np.numpy_support.as_dtype(val)
    lzlzt__ktryr = {}
    exec(vqm__wsxib, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, lzlzt__ktryr)
    mvq__mahad = lzlzt__ktryr['bcast_scalar_impl']
    return mvq__mahad


def bcast_tuple(val):
    return val


@overload(bcast_tuple, no_unliteral=True)
def overload_bcast_tuple(val):
    assert isinstance(val, types.BaseTuple)
    uirb__dznrt = len(val)
    vqm__wsxib = 'def bcast_tuple_impl(val):\n'
    vqm__wsxib += '  return ({}{})'.format(','.join('bcast_scalar(val[{}])'
        .format(i) for i in range(uirb__dznrt)), ',' if uirb__dznrt else '')
    lzlzt__ktryr = {}
    exec(vqm__wsxib, {'bcast_scalar': bcast_scalar}, lzlzt__ktryr)
    sym__vrxts = lzlzt__ktryr['bcast_tuple_impl']
    return sym__vrxts


def prealloc_str_for_bcast(arr):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr):
    if arr == string_array_type:

        def prealloc_impl(arr):
            rank = bodo.libs.distributed_api.get_rank()
            pcogn__lqpmq = bcast_scalar(len(arr))
            stnc__ngznc = bcast_scalar(np.int64(num_total_chars(arr)))
            if rank != MPI_ROOT:
                arr = pre_alloc_string_array(pcogn__lqpmq, stnc__ngznc)
            return arr
        return prealloc_impl
    return lambda arr: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):

    def impl(idx, arr_start, total_len):
        slice_index = numba.cpython.unicode._normalize_slice(idx, total_len)
        start = slice_index.start
        jquct__rsm = slice_index.step
        jklw__ooiv = 0 if jquct__rsm == 1 or start > arr_start else abs(
            jquct__rsm - arr_start % jquct__rsm) % jquct__rsm
        lqn__cjq = max(arr_start, slice_index.start) - arr_start + jklw__ooiv
        tgiz__kaxuo = max(slice_index.stop - arr_start, 0)
        return slice(lqn__cjq, tgiz__kaxuo, jquct__rsm)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        uxhh__uiwva = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[uxhh__uiwva])
    return getitem_impl


def slice_getitem_from_start(arr, slice_index):
    return arr[slice_index]


@overload(slice_getitem_from_start, no_unliteral=True)
def slice_getitem_from_start_overload(arr, slice_index):
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def getitem_datetime_date_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            gyzxx__gwz = slice_index.stop
            A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                gyzxx__gwz)
            if rank == 0:
                A = arr[:gyzxx__gwz]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_date_impl
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def getitem_datetime_timedelta_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            gyzxx__gwz = slice_index.stop
            A = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(gyzxx__gwz))
            if rank == 0:
                A = arr[:gyzxx__gwz]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_timedelta_impl
    if isinstance(arr.dtype, Decimal128Type):
        precision = arr.dtype.precision
        scale = arr.dtype.scale

        def getitem_decimal_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            gyzxx__gwz = slice_index.stop
            A = bodo.libs.decimal_arr_ext.alloc_decimal_array(gyzxx__gwz,
                precision, scale)
            if rank == 0:
                for i in range(gyzxx__gwz):
                    A._data[i] = arr._data[i]
                    nil__ucqw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, i,
                        nil__ucqw)
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_decimal_impl
    if arr == string_array_type:

        def getitem_str_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            gyzxx__gwz = slice_index.stop
            yblr__mfec = np.uint64(0)
            if rank == 0:
                out_arr = arr[:gyzxx__gwz]
                yblr__mfec = num_total_chars(out_arr)
            yblr__mfec = bcast_scalar(yblr__mfec)
            if rank != 0:
                out_arr = pre_alloc_string_array(gyzxx__gwz, yblr__mfec)
            bodo.libs.distributed_api.bcast(out_arr)
            return out_arr
        return getitem_str_impl
    pjp__pei = arr

    def getitem_impl(arr, slice_index):
        rank = bodo.libs.distributed_api.get_rank()
        gyzxx__gwz = slice_index.stop
        out_arr = bodo.utils.utils.alloc_type(tuple_to_scalar((gyzxx__gwz,) +
            arr.shape[1:]), pjp__pei)
        if rank == 0:
            out_arr = arr[:gyzxx__gwz]
        bodo.libs.distributed_api.bcast(out_arr)
        return out_arr
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if arr in [bodo.binary_array_type, string_array_type]:
        qbzd__vfz = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        wmzzl__rcl = np.int32(numba_to_c_type(types.uint8))
        rvmll__zpi = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            mnaea__fuce = np.int32(10)
            tag = np.int32(11)
            sry__hus = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                kvqi__hnhnd = arr._data
                kkszz__jzxz = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    kvqi__hnhnd, ind)
                wne__jljsu = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    kvqi__hnhnd, ind + 1)
                length = wne__jljsu - kkszz__jzxz
                fzocz__khylv = kvqi__hnhnd[ind]
                sry__hus[0] = length
                isend(sry__hus, np.int32(1), root, mnaea__fuce, True)
                isend(fzocz__khylv, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(rvmll__zpi
                , qbzd__vfz, 0, 1)
            sin__nle = 0
            if rank == root:
                sin__nle = recv(np.int64, ANY_SOURCE, mnaea__fuce)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    rvmll__zpi, qbzd__vfz, sin__nle, 1)
                pvp__lzzr = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(pvp__lzzr, np.int32(sin__nle), wmzzl__rcl, ANY_SOURCE,
                    tag)
            dummy_use(sry__hus)
            sin__nle = bcast_scalar(sin__nle)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    rvmll__zpi, qbzd__vfz, sin__nle, 1)
            pvp__lzzr = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(pvp__lzzr, np.int32(sin__nle), wmzzl__rcl, np.array([-1
                ]).ctypes, 0)
            val = transform_str_getitem_output(val, sin__nle)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        xpkas__zkyaw = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, xpkas__zkyaw)
            if arr_start <= ind < arr_start + len(arr):
                ebc__zocq = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = ebc__zocq[ind - arr_start]
                send_arr = np.full(1, data, xpkas__zkyaw)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = xpkas__zkyaw(-1)
            if rank == root:
                val = recv(xpkas__zkyaw, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            jhoqa__wjuyq = arr.dtype.categories[max(val, 0)]
            return jhoqa__wjuyq
        return cat_getitem_impl
    vnxj__eiv = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, vnxj__eiv)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, vnxj__eiv)[0]
        if rank == root:
            val = recv(vnxj__eiv, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    gqix__ejuvj = get_type_enum(out_data)
    assert typ_enum == gqix__ejuvj
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    vqm__wsxib = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        vqm__wsxib += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    vqm__wsxib += '  return\n'
    lzlzt__ktryr = {}
    exec(vqm__wsxib, {'alltoallv': alltoallv}, lzlzt__ktryr)
    diy__pwm = lzlzt__ktryr['f']
    return diy__pwm


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    start = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return start, count


@numba.njit
def get_start(total_size, pes, rank):
    aabd__bflxb = total_size % pes
    bahi__ctk = (total_size - aabd__bflxb) // pes
    return rank * bahi__ctk + min(rank, aabd__bflxb)


@numba.njit
def get_end(total_size, pes, rank):
    aabd__bflxb = total_size % pes
    bahi__ctk = (total_size - aabd__bflxb) // pes
    return (rank + 1) * bahi__ctk + min(rank + 1, aabd__bflxb)


@numba.njit
def get_node_portion(total_size, pes, rank):
    aabd__bflxb = total_size % pes
    bahi__ctk = (total_size - aabd__bflxb) // pes
    if rank < aabd__bflxb:
        return bahi__ctk + 1
    else:
        return bahi__ctk


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    oqfcp__sxn = in_arr.dtype(0)
    aimbl__sicl = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        xeuc__pdfq = oqfcp__sxn
        for otde__mcd in np.nditer(in_arr):
            xeuc__pdfq += otde__mcd.item()
        qodj__ybagl = dist_exscan(xeuc__pdfq, aimbl__sicl)
        for i in range(in_arr.size):
            qodj__ybagl += in_arr[i]
            out_arr[i] = qodj__ybagl
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    ebsj__gjl = in_arr.dtype(1)
    aimbl__sicl = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        xeuc__pdfq = ebsj__gjl
        for otde__mcd in np.nditer(in_arr):
            xeuc__pdfq *= otde__mcd.item()
        qodj__ybagl = dist_exscan(xeuc__pdfq, aimbl__sicl)
        if get_rank() == 0:
            qodj__ybagl = ebsj__gjl
        for i in range(in_arr.size):
            qodj__ybagl *= in_arr[i]
            out_arr[i] = qodj__ybagl
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ebsj__gjl = np.finfo(in_arr.dtype(1).dtype).max
    else:
        ebsj__gjl = np.iinfo(in_arr.dtype(1).dtype).max
    aimbl__sicl = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        xeuc__pdfq = ebsj__gjl
        for otde__mcd in np.nditer(in_arr):
            xeuc__pdfq = min(xeuc__pdfq, otde__mcd.item())
        qodj__ybagl = dist_exscan(xeuc__pdfq, aimbl__sicl)
        if get_rank() == 0:
            qodj__ybagl = ebsj__gjl
        for i in range(in_arr.size):
            qodj__ybagl = min(qodj__ybagl, in_arr[i])
            out_arr[i] = qodj__ybagl
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ebsj__gjl = np.finfo(in_arr.dtype(1).dtype).min
    else:
        ebsj__gjl = np.iinfo(in_arr.dtype(1).dtype).min
    ebsj__gjl = in_arr.dtype(1)
    aimbl__sicl = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        xeuc__pdfq = ebsj__gjl
        for otde__mcd in np.nditer(in_arr):
            xeuc__pdfq = max(xeuc__pdfq, otde__mcd.item())
        qodj__ybagl = dist_exscan(xeuc__pdfq, aimbl__sicl)
        if get_rank() == 0:
            qodj__ybagl = ebsj__gjl
        for i in range(in_arr.size):
            qodj__ybagl = max(qodj__ybagl, in_arr[i])
            out_arr[i] = qodj__ybagl
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    ttl__nvil = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), ttl__nvil)


def dist_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    pncc__bmxeq = args[0]
    if equiv_set.has_shape(pncc__bmxeq):
        return ArrayAnalysis.AnalyzeResult(shape=pncc__bmxeq, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


@numba.njit(no_cpython_wrapper=True)
def print_if_not_empty(arg):
    if len(arg) != 0 or bodo.get_rank() == 0:
        print(arg)


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        hjtw__ffr = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        vqm__wsxib = 'def f(req, cond=True):\n'
        vqm__wsxib += f'  return {hjtw__ffr}\n'
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'_wait': _wait}, lzlzt__ktryr)
        impl = lzlzt__ktryr['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


class ReqArrayType(types.Type):

    def __init__(self):
        super(ReqArrayType, self).__init__(name='ReqArrayType()')


req_array_type = ReqArrayType()
register_model(ReqArrayType)(models.OpaqueModel)
waitall = types.ExternalFunction('dist_waitall', types.void(types.int32,
    req_array_type))
comm_req_alloc = types.ExternalFunction('comm_req_alloc', req_array_type(
    types.int32))
comm_req_dealloc = types.ExternalFunction('comm_req_dealloc', types.void(
    req_array_type))
req_array_setitem = types.ExternalFunction('req_array_setitem', types.void(
    req_array_type, types.int64, mpi_req_numba_type))


@overload(operator.setitem, no_unliteral=True)
def overload_req_arr_setitem(A, idx, val):
    if A == req_array_type:
        assert val == mpi_req_numba_type
        return lambda A, idx, val: req_array_setitem(A, idx, val)


@numba.njit
def _get_local_range(start, stop, chunk_start, chunk_count):
    assert start >= 0 and stop > 0
    lqn__cjq = max(start, chunk_start)
    tgiz__kaxuo = min(stop, chunk_start + chunk_count)
    pdkug__rmzr = lqn__cjq - chunk_start
    uusf__twr = tgiz__kaxuo - chunk_start
    if pdkug__rmzr < 0 or uusf__twr < 0:
        pdkug__rmzr = 1
        uusf__twr = 0
    return pdkug__rmzr, uusf__twr


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        aabd__bflxb = 1
        for a in t:
            aabd__bflxb *= a
        return aabd__bflxb
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    scs__eewu = np.ascontiguousarray(in_arr)
    rves__fcpyk = get_tuple_prod(scs__eewu.shape[1:])
    gwye__ounlo = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        pse__exby = np.array(dest_ranks, dtype=np.int32)
    else:
        pse__exby = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, scs__eewu.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * gwye__ounlo, dtype_size * rves__fcpyk,
        len(pse__exby), pse__exby.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len):
    wkv__wpc = np.ascontiguousarray(rhs)
    gyx__ganiz = get_tuple_prod(wkv__wpc.shape[1:])
    ewhka__ezk = dtype_size * gyx__ganiz
    permutation_array_index(lhs.ctypes, lhs_len, ewhka__ezk, wkv__wpc.
        ctypes, wkv__wpc.shape[0], p.ctypes, p_len)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks):
    return lambda data, comm_ranks, nranks: bcast_comm_impl(data,
        comm_ranks, nranks)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        vqm__wsxib = (
            """def bcast_scalar_impl(data, comm_ranks, nranks):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({}), comm_ranks,ctypes, np.int32({}))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, lzlzt__ktryr)
        mvq__mahad = lzlzt__ktryr['bcast_scalar_impl']
        return mvq__mahad
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks: _bcast_np(data, comm_ranks,
            nranks)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qtc__dtssp = len(data.columns)
        cpopl__ftfnk = ', '.join('g_data_{}'.format(i) for i in range(
            qtc__dtssp))
        fhsws__jykae = bodo.utils.transform.gen_const_tup(data.columns)
        vqm__wsxib = 'def impl_df(data, comm_ranks, nranks):\n'
        for i in range(qtc__dtssp):
            vqm__wsxib += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            vqm__wsxib += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks)
"""
                .format(i, i))
        vqm__wsxib += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        vqm__wsxib += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks)
"""
        vqm__wsxib += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(cpopl__ftfnk, fhsws__jykae))
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bodo': bodo}, lzlzt__ktryr)
        rtmp__elat = lzlzt__ktryr['impl_df']
        return rtmp__elat
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            jquct__rsm = data._step
            ccr__vpcyb = data._name
            ccr__vpcyb = bcast_scalar(ccr__vpcyb)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            jquct__rsm = bcast_scalar(jquct__rsm)
            mleax__lwexq = bodo.libs.array_kernels.calc_nitems(start, stop,
                jquct__rsm)
            chunk_start = bodo.libs.distributed_api.get_start(mleax__lwexq,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(
                mleax__lwexq, n_pes, rank)
            lqn__cjq = start + jquct__rsm * chunk_start
            tgiz__kaxuo = start + jquct__rsm * (chunk_start + chunk_count)
            tgiz__kaxuo = min(tgiz__kaxuo, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(lqn__cjq,
                tgiz__kaxuo, jquct__rsm, ccr__vpcyb)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks):
            gexem__ait = data._data
            ccr__vpcyb = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(gexem__ait,
                comm_ranks, nranks)
            return bodo.utils.conversion.index_from_array(arr, ccr__vpcyb)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ccr__vpcyb = bodo.hiframes.pd_series_ext.get_series_name(data)
            hfksn__exm = bodo.libs.distributed_api.bcast_comm_impl(ccr__vpcyb,
                comm_ranks, nranks)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks)
            cvnd__yfc = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cvnd__yfc, hfksn__exm)
        return impl_series
    if isinstance(data, types.BaseTuple):
        vqm__wsxib = 'def impl_tuple(data, comm_ranks, nranks):\n'
        vqm__wsxib += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks)'.format(i) for i in
            range(len(data))), ',' if len(data) > 0 else '')
        lzlzt__ktryr = {}
        exec(vqm__wsxib, {'bcast_comm_impl': bcast_comm_impl}, lzlzt__ktryr)
        xdca__iny = lzlzt__ktryr['impl_tuple']
        return xdca__iny
    if data is types.none:
        return lambda data, comm_ranks, nranks: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks):
    typ_val = numba_to_c_type(data.dtype)
    imbl__phs = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    vwld__mmoe = (0,) * imbl__phs

    def bcast_arr_impl(data, comm_ranks, nranks):
        rank = bodo.libs.distributed_api.get_rank()
        gexem__ait = np.ascontiguousarray(data)
        pvp__lzzr = data.ctypes
        unask__umook = vwld__mmoe
        if rank == MPI_ROOT:
            unask__umook = gexem__ait.shape
        unask__umook = bcast_tuple(unask__umook)
        bubvx__gda = get_tuple_prod(unask__umook[1:])
        send_counts = unask__umook[0] * bubvx__gda
        wls__lozng = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(pvp__lzzr, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks))
            return data
        else:
            c_bcast(wls__lozng.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks))
            return wls__lozng.reshape((-1,) + unask__umook[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        mwg__sizt = MPI.COMM_WORLD
        wytez__knsu = MPI.Get_processor_name()
        jhapo__ome = mwg__sizt.allgather(wytez__knsu)
        node_ranks = defaultdict(list)
        for i, feo__thh in enumerate(jhapo__ome):
            node_ranks[feo__thh].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    mwg__sizt = MPI.COMM_WORLD
    vbe__gvb = mwg__sizt.Get_group()
    hawu__eax = vbe__gvb.Incl(comm_ranks)
    xlg__thrth = mwg__sizt.Create_group(hawu__eax)
    return xlg__thrth


def get_nodes_first_ranks():
    yzjpc__jwa = get_host_ranks()
    return np.array([owtzv__hrdta[0] for owtzv__hrdta in yzjpc__jwa.values(
        )], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
