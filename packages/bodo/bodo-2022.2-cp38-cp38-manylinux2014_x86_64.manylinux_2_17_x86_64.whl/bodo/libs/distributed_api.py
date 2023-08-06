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
    bafb__jzea = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, bafb__jzea, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    bafb__jzea = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, bafb__jzea, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            bafb__jzea = get_type_enum(arr)
            return _isend(arr.ctypes, size, bafb__jzea, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        bafb__jzea = np.int32(numba_to_c_type(arr.dtype))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            exsh__zkdw = size + 7 >> 3
            fpdcg__eql = _isend(arr._data.ctypes, size, bafb__jzea, pe, tag,
                cond)
            aoeyb__qeah = _isend(arr._null_bitmap.ctypes, exsh__zkdw,
                jqzwx__rrmn, pe, tag, cond)
            return fpdcg__eql, aoeyb__qeah
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        tjope__wtuan = np.int32(numba_to_c_type(offset_type))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            posl__wsge = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(posl__wsge, pe, tag - 1)
            exsh__zkdw = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                tjope__wtuan, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), posl__wsge,
                jqzwx__rrmn, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                exsh__zkdw, jqzwx__rrmn, pe, tag)
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
            bafb__jzea = get_type_enum(arr)
            return _irecv(arr.ctypes, size, bafb__jzea, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        bafb__jzea = np.int32(numba_to_c_type(arr.dtype))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            exsh__zkdw = size + 7 >> 3
            fpdcg__eql = _irecv(arr._data.ctypes, size, bafb__jzea, pe, tag,
                cond)
            aoeyb__qeah = _irecv(arr._null_bitmap.ctypes, exsh__zkdw,
                jqzwx__rrmn, pe, tag, cond)
            return fpdcg__eql, aoeyb__qeah
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        tjope__wtuan = np.int32(numba_to_c_type(offset_type))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            xcq__tkxn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            xcq__tkxn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        enk__jjbg = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {xcq__tkxn}(size, n_chars)
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
        qzpt__ysn = dict()
        exec(enk__jjbg, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            tjope__wtuan, 'char_typ_enum': jqzwx__rrmn}, qzpt__ysn)
        impl = qzpt__ysn['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    bafb__jzea = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), bafb__jzea)


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
        fzowg__eavu = n_pes if rank == root or allgather else 0
        cjsu__nxh = np.empty(fzowg__eavu, dtype)
        c_gather_scalar(send.ctypes, cjsu__nxh.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return cjsu__nxh
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
        qvbvm__dusyg = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], qvbvm__dusyg)
        return builder.bitcast(qvbvm__dusyg, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        qvbvm__dusyg = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(qvbvm__dusyg)
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
    wcq__dbcw = types.unliteral(value)
    if isinstance(wcq__dbcw, IndexValueType):
        wcq__dbcw = wcq__dbcw.val_typ
        dltqh__yyarc = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            dltqh__yyarc.append(types.int64)
            dltqh__yyarc.append(bodo.datetime64ns)
            dltqh__yyarc.append(bodo.timedelta64ns)
            dltqh__yyarc.append(bodo.datetime_date_type)
        if wcq__dbcw not in dltqh__yyarc:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(wcq__dbcw))
    typ_enum = np.int32(numba_to_c_type(wcq__dbcw))

    def impl(value, reduce_op):
        bffd__skwj = value_to_ptr(value)
        ogyh__acpsa = value_to_ptr(value)
        _dist_reduce(bffd__skwj, ogyh__acpsa, reduce_op, typ_enum)
        return load_val_ptr(ogyh__acpsa, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    wcq__dbcw = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(wcq__dbcw))
    oqmh__rmw = wcq__dbcw(0)

    def impl(value, reduce_op):
        bffd__skwj = value_to_ptr(value)
        ogyh__acpsa = value_to_ptr(oqmh__rmw)
        _dist_exscan(bffd__skwj, ogyh__acpsa, reduce_op, typ_enum)
        return load_val_ptr(ogyh__acpsa, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    vzszn__rdi = 0
    mgudi__luss = 0
    for i in range(len(recv_counts)):
        nbak__dbv = recv_counts[i]
        exsh__zkdw = recv_counts_nulls[i]
        hnfsw__uxyhv = tmp_null_bytes[vzszn__rdi:vzszn__rdi + exsh__zkdw]
        for qah__jwlw in range(nbak__dbv):
            set_bit_to(null_bitmap_ptr, mgudi__luss, get_bit(hnfsw__uxyhv,
                qah__jwlw))
            mgudi__luss += 1
        vzszn__rdi += exsh__zkdw


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            fuwp__ybnw = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                fuwp__ybnw, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            ksyf__chnmn = data.size
            recv_counts = gather_scalar(np.int32(ksyf__chnmn), allgather,
                root=root)
            twsiy__hsjpf = recv_counts.sum()
            rtd__zzg = empty_like_type(twsiy__hsjpf, data)
            lveoe__ymbfn = np.empty(1, np.int32)
            if rank == root or allgather:
                lveoe__ymbfn = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(ksyf__chnmn), rtd__zzg.ctypes,
                recv_counts.ctypes, lveoe__ymbfn.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return rtd__zzg.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if data == string_array_type:

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rtd__zzg = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(rtd__zzg)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rtd__zzg = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(rtd__zzg)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ksyf__chnmn = len(data)
            exsh__zkdw = ksyf__chnmn + 7 >> 3
            recv_counts = gather_scalar(np.int32(ksyf__chnmn), allgather,
                root=root)
            twsiy__hsjpf = recv_counts.sum()
            rtd__zzg = empty_like_type(twsiy__hsjpf, data)
            lveoe__ymbfn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            eml__tcit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lveoe__ymbfn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                eml__tcit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(ksyf__chnmn),
                rtd__zzg._days_data.ctypes, recv_counts.ctypes,
                lveoe__ymbfn.ctypes, np.int32(typ_val), allgather, np.int32
                (root))
            c_gatherv(data._seconds_data.ctypes, np.int32(ksyf__chnmn),
                rtd__zzg._seconds_data.ctypes, recv_counts.ctypes,
                lveoe__ymbfn.ctypes, np.int32(typ_val), allgather, np.int32
                (root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(ksyf__chnmn),
                rtd__zzg._microseconds_data.ctypes, recv_counts.ctypes,
                lveoe__ymbfn.ctypes, np.int32(typ_val), allgather, np.int32
                (root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(exsh__zkdw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, eml__tcit.
                ctypes, jqzwx__rrmn, allgather, np.int32(root))
            copy_gathered_null_bytes(rtd__zzg._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return rtd__zzg
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ksyf__chnmn = len(data)
            exsh__zkdw = ksyf__chnmn + 7 >> 3
            recv_counts = gather_scalar(np.int32(ksyf__chnmn), allgather,
                root=root)
            twsiy__hsjpf = recv_counts.sum()
            rtd__zzg = empty_like_type(twsiy__hsjpf, data)
            lveoe__ymbfn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            eml__tcit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lveoe__ymbfn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                eml__tcit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(ksyf__chnmn), rtd__zzg.
                _data.ctypes, recv_counts.ctypes, lveoe__ymbfn.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(exsh__zkdw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, eml__tcit.
                ctypes, jqzwx__rrmn, allgather, np.int32(root))
            copy_gathered_null_bytes(rtd__zzg._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return rtd__zzg
        return gatherv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            ndfu__hdbi = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            hsz__anoqy = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(ndfu__hdbi,
                hsz__anoqy)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qqi__fdko = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            iqjg__wlv = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                iqjg__wlv, qqi__fdko)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        skivx__hefp = np.iinfo(np.int64).max
        lxmk__magbf = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            start = data._start
            stop = data._stop
            if len(data) == 0:
                start = skivx__hefp
                stop = lxmk__magbf
            start = bodo.libs.distributed_api.dist_reduce(start, np.int32(
                Reduce_Type.Min.value))
            stop = bodo.libs.distributed_api.dist_reduce(stop, np.int32(
                Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if start == skivx__hefp and stop == lxmk__magbf:
                start = 0
                stop = 0
            ddjyh__twngv = max(0, -(-(stop - start) // data._step))
            if ddjyh__twngv < total_len:
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
            xuujg__tky = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, xuujg__tky)
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
            rtd__zzg = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(rtd__zzg,
                data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        fvl__uzhuu = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        enk__jjbg = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        enk__jjbg += '  T = data\n'
        enk__jjbg += '  T2 = init_table(T)\n'
        for ddwt__urygv in data.type_to_blk.values():
            fvl__uzhuu[f'arr_inds_{ddwt__urygv}'] = np.array(data.
                block_to_arr_ind[ddwt__urygv], dtype=np.int64)
            enk__jjbg += (
                f'  arr_list_{ddwt__urygv} = get_table_block(T, {ddwt__urygv})\n'
                )
            enk__jjbg += (
                f'  out_arr_list_{ddwt__urygv} = alloc_list_like(arr_list_{ddwt__urygv})\n'
                )
            enk__jjbg += f'  for i in range(len(arr_list_{ddwt__urygv})):\n'
            enk__jjbg += (
                f'    arr_ind_{ddwt__urygv} = arr_inds_{ddwt__urygv}[i]\n')
            enk__jjbg += f"""    ensure_column_unboxed(T, arr_list_{ddwt__urygv}, i, arr_ind_{ddwt__urygv})
"""
            enk__jjbg += f"""    out_arr_{ddwt__urygv} = bodo.gatherv(arr_list_{ddwt__urygv}[i], allgather, warn_if_rep, root)
"""
            enk__jjbg += (
                f'    out_arr_list_{ddwt__urygv}[i] = out_arr_{ddwt__urygv}\n')
            enk__jjbg += (
                f'  T2 = set_table_block(T2, out_arr_list_{ddwt__urygv}, {ddwt__urygv})\n'
                )
        enk__jjbg += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        enk__jjbg += f'  T2 = set_table_len(T2, length)\n'
        enk__jjbg += f'  return T2\n'
        qzpt__ysn = {}
        exec(enk__jjbg, fvl__uzhuu, qzpt__ysn)
        pxq__jmo = qzpt__ysn['impl_table']
        return pxq__jmo
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hmwh__xxtw = len(data.columns)
        if hmwh__xxtw == 0:
            return (lambda data, allgather=False, warn_if_rep=True, root=
                MPI_ROOT: bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data), ()))
        xgud__gwmcr = ', '.join(f'g_data_{i}' for i in range(hmwh__xxtw))
        mrxl__jser = bodo.utils.transform.gen_const_tup(data.columns)
        enk__jjbg = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            nra__bzri = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            fvl__uzhuu = {'bodo': bodo, 'df_type': nra__bzri}
            xgud__gwmcr = 'T2'
            mrxl__jser = 'df_type'
            enk__jjbg += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            enk__jjbg += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            fvl__uzhuu = {'bodo': bodo}
            for i in range(hmwh__xxtw):
                enk__jjbg += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                enk__jjbg += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        enk__jjbg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        enk__jjbg += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        enk__jjbg += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(xgud__gwmcr, mrxl__jser))
        qzpt__ysn = {}
        exec(enk__jjbg, fvl__uzhuu, qzpt__ysn)
        gaeqg__supw = qzpt__ysn['impl_df']
        return gaeqg__supw
    if isinstance(data, ArrayItemArrayType):
        fwuou__yqp = np.int32(numba_to_c_type(types.int32))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            kmn__jggq = bodo.libs.array_item_arr_ext.get_offsets(data)
            szvn__ngaip = bodo.libs.array_item_arr_ext.get_data(data)
            rqnsc__pfoh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            ksyf__chnmn = len(data)
            yny__dtca = np.empty(ksyf__chnmn, np.uint32)
            exsh__zkdw = ksyf__chnmn + 7 >> 3
            for i in range(ksyf__chnmn):
                yny__dtca[i] = kmn__jggq[i + 1] - kmn__jggq[i]
            recv_counts = gather_scalar(np.int32(ksyf__chnmn), allgather,
                root=root)
            twsiy__hsjpf = recv_counts.sum()
            lveoe__ymbfn = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            eml__tcit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lveoe__ymbfn = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for ooouj__vbj in range(len(recv_counts)):
                    recv_counts_nulls[ooouj__vbj] = recv_counts[ooouj__vbj
                        ] + 7 >> 3
                eml__tcit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            mphc__jclxi = np.empty(twsiy__hsjpf + 1, np.uint32)
            aey__epq = bodo.gatherv(szvn__ngaip, allgather, warn_if_rep, root)
            cse__xfc = np.empty(twsiy__hsjpf + 7 >> 3, np.uint8)
            c_gatherv(yny__dtca.ctypes, np.int32(ksyf__chnmn), mphc__jclxi.
                ctypes, recv_counts.ctypes, lveoe__ymbfn.ctypes, fwuou__yqp,
                allgather, np.int32(root))
            c_gatherv(rqnsc__pfoh.ctypes, np.int32(exsh__zkdw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, eml__tcit.
                ctypes, jqzwx__rrmn, allgather, np.int32(root))
            dummy_use(data)
            ykou__lri = np.empty(twsiy__hsjpf + 1, np.uint64)
            convert_len_arr_to_offset(mphc__jclxi.ctypes, ykou__lri.ctypes,
                twsiy__hsjpf)
            copy_gathered_null_bytes(cse__xfc.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                twsiy__hsjpf, aey__epq, ykou__lri, cse__xfc)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        gpjq__qzw = data.names
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            omczr__aco = bodo.libs.struct_arr_ext.get_data(data)
            ulh__vwaul = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            fukmv__esja = bodo.gatherv(omczr__aco, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            ksyf__chnmn = len(data)
            exsh__zkdw = ksyf__chnmn + 7 >> 3
            recv_counts = gather_scalar(np.int32(ksyf__chnmn), allgather,
                root=root)
            twsiy__hsjpf = recv_counts.sum()
            cfbt__pdbrh = np.empty(twsiy__hsjpf + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            eml__tcit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                eml__tcit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(ulh__vwaul.ctypes, np.int32(exsh__zkdw),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, eml__tcit.
                ctypes, jqzwx__rrmn, allgather, np.int32(root))
            copy_gathered_null_bytes(cfbt__pdbrh.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(fukmv__esja,
                cfbt__pdbrh, gpjq__qzw)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            rtd__zzg = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(rtd__zzg)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            rtd__zzg = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(rtd__zzg)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            rtd__zzg = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(rtd__zzg)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            rtd__zzg = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            qmw__zhnhg = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            lwgtt__tno = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            rhgdc__zrdbj = gather_scalar(data.shape[0], allgather, root=root)
            ppwjv__gke = rhgdc__zrdbj.sum()
            hmwh__xxtw = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            txep__elwcj = np.empty(ppwjv__gke + 1, np.int64)
            qmw__zhnhg = qmw__zhnhg.astype(np.int64)
            txep__elwcj[0] = 0
            fzozz__xdw = 1
            mhsb__fsuqf = 0
            for rqcd__gdej in rhgdc__zrdbj:
                for isbfm__ruv in range(rqcd__gdej):
                    muhy__zcu = lwgtt__tno[mhsb__fsuqf + 1] - lwgtt__tno[
                        mhsb__fsuqf]
                    txep__elwcj[fzozz__xdw] = txep__elwcj[fzozz__xdw - 1
                        ] + muhy__zcu
                    fzozz__xdw += 1
                    mhsb__fsuqf += 1
                mhsb__fsuqf += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(rtd__zzg,
                qmw__zhnhg, txep__elwcj, (ppwjv__gke, hmwh__xxtw))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        enk__jjbg = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        enk__jjbg += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        qzpt__ysn = {}
        exec(enk__jjbg, {'bodo': bodo}, qzpt__ysn)
        kkogp__kjgz = qzpt__ysn['impl_tuple']
        return kkogp__kjgz
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    enk__jjbg = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    enk__jjbg += '    if random:\n'
    enk__jjbg += '        if random_seed is None:\n'
    enk__jjbg += '            random = 1\n'
    enk__jjbg += '        else:\n'
    enk__jjbg += '            random = 2\n'
    enk__jjbg += '    if random_seed is None:\n'
    enk__jjbg += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dcsg__lime = data
        hmwh__xxtw = len(dcsg__lime.columns)
        for i in range(hmwh__xxtw):
            enk__jjbg += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        enk__jjbg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        xgud__gwmcr = ', '.join(f'data_{i}' for i in range(hmwh__xxtw))
        enk__jjbg += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(pjiew__xwf) for
            pjiew__xwf in range(hmwh__xxtw))))
        enk__jjbg += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        enk__jjbg += '    if dests is None:\n'
        enk__jjbg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        enk__jjbg += '    else:\n'
        enk__jjbg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for wuppd__wun in range(hmwh__xxtw):
            enk__jjbg += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(wuppd__wun))
        enk__jjbg += (
            '    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
            .format(hmwh__xxtw))
        enk__jjbg += '    delete_table(out_table)\n'
        enk__jjbg += '    if parallel:\n'
        enk__jjbg += '        delete_table(table_total)\n'
        xgud__gwmcr = ', '.join('out_arr_{}'.format(i) for i in range(
            hmwh__xxtw))
        mrxl__jser = bodo.utils.transform.gen_const_tup(dcsg__lime.columns)
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        enk__jjbg += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, {})\n'
            .format(xgud__gwmcr, index, mrxl__jser))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        enk__jjbg += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        enk__jjbg += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        enk__jjbg += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        enk__jjbg += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        enk__jjbg += '    if dests is None:\n'
        enk__jjbg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        enk__jjbg += '    else:\n'
        enk__jjbg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        enk__jjbg += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        enk__jjbg += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        enk__jjbg += '    delete_table(out_table)\n'
        enk__jjbg += '    if parallel:\n'
        enk__jjbg += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        enk__jjbg += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        enk__jjbg += '    if not parallel:\n'
        enk__jjbg += '        return data\n'
        enk__jjbg += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        enk__jjbg += '    if dests is None:\n'
        enk__jjbg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        enk__jjbg += '    elif bodo.get_rank() not in dests:\n'
        enk__jjbg += '        dim0_local_size = 0\n'
        enk__jjbg += '    else:\n'
        enk__jjbg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        enk__jjbg += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        enk__jjbg += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        enk__jjbg += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        enk__jjbg += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        enk__jjbg += '    if dests is None:\n'
        enk__jjbg += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        enk__jjbg += '    else:\n'
        enk__jjbg += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        enk__jjbg += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        enk__jjbg += '    delete_table(out_table)\n'
        enk__jjbg += '    if parallel:\n'
        enk__jjbg += '        delete_table(table_total)\n'
        enk__jjbg += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    qzpt__ysn = {}
    exec(enk__jjbg, {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}, qzpt__ysn
        )
    impl = qzpt__ysn['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, parallel=False):
    enk__jjbg = 'def impl(data, seed=None, dests=None, parallel=False):\n'
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        enk__jjbg += '    if seed is None:\n'
        enk__jjbg += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        enk__jjbg += '    np.random.seed(seed)\n'
        enk__jjbg += '    if not parallel:\n'
        enk__jjbg += '        data = data.copy()\n'
        enk__jjbg += '        np.random.shuffle(data)\n'
        enk__jjbg += '        return data\n'
        enk__jjbg += '    else:\n'
        enk__jjbg += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        enk__jjbg += '        permutation = np.arange(dim0_global_size)\n'
        enk__jjbg += '        np.random.shuffle(permutation)\n'
        enk__jjbg += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        enk__jjbg += """        output = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        enk__jjbg += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        enk__jjbg += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation))
"""
        enk__jjbg += '        return output\n'
    else:
        enk__jjbg += """    return bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
    qzpt__ysn = {}
    exec(enk__jjbg, {'np': np, 'bodo': bodo}, qzpt__ysn)
    impl = qzpt__ysn['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    dmv__oij = np.empty(sendcounts_nulls.sum(), np.uint8)
    vzszn__rdi = 0
    mgudi__luss = 0
    for ypgcs__jgo in range(len(sendcounts)):
        nbak__dbv = sendcounts[ypgcs__jgo]
        exsh__zkdw = sendcounts_nulls[ypgcs__jgo]
        hnfsw__uxyhv = dmv__oij[vzszn__rdi:vzszn__rdi + exsh__zkdw]
        for qah__jwlw in range(nbak__dbv):
            set_bit_to_arr(hnfsw__uxyhv, qah__jwlw, get_bit_bitmap(
                null_bitmap_ptr, mgudi__luss))
            mgudi__luss += 1
        vzszn__rdi += exsh__zkdw
    return dmv__oij


def _bcast_dtype(data):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    feaa__gas = MPI.COMM_WORLD
    data = feaa__gas.bcast(data)
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
    mafaj__xxsv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    dil__sjnqu = (0,) * mafaj__xxsv

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        qkvc__yykab = np.ascontiguousarray(data)
        rqybt__uhmd = data.ctypes
        uhuo__uimly = dil__sjnqu
        if rank == MPI_ROOT:
            uhuo__uimly = qkvc__yykab.shape
        uhuo__uimly = bcast_tuple(uhuo__uimly)
        daoj__twa = get_tuple_prod(uhuo__uimly[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            uhuo__uimly[0])
        send_counts *= daoj__twa
        ksyf__chnmn = send_counts[rank]
        wyiqs__fvxrk = np.empty(ksyf__chnmn, dtype)
        lveoe__ymbfn = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(rqybt__uhmd, send_counts.ctypes, lveoe__ymbfn.ctypes,
            wyiqs__fvxrk.ctypes, np.int32(ksyf__chnmn), np.int32(typ_val))
        return wyiqs__fvxrk.reshape((-1,) + uhuo__uimly[1:])
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
        jirt__kll = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], jirt__kll)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        qqi__fdko = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=qqi__fdko)
        zkdp__wpugj = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(zkdp__wpugj)
        return pd.Index(arr, name=qqi__fdko)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        qqi__fdko = _get_name_value_for_type(dtype.name_typ)
        gpjq__qzw = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        qil__lynk = tuple(get_value_for_type(t) for t in dtype.array_types)
        val = pd.MultiIndex.from_arrays(qil__lynk, names=gpjq__qzw)
        val.name = qqi__fdko
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        qqi__fdko = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=qqi__fdko)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qil__lynk = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({qqi__fdko: arr for qqi__fdko, arr in zip(dtype
            .columns, qil__lynk)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        zkdp__wpugj = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(zkdp__wpugj[0],
            zkdp__wpugj[0])])
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
        fwuou__yqp = np.int32(numba_to_c_type(types.int32))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            xcq__tkxn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            xcq__tkxn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        enk__jjbg = f"""def impl(
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
            recv_arr = {xcq__tkxn}(n_loc, n_loc_char)

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
        qzpt__ysn = dict()
        exec(enk__jjbg, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            fwuou__yqp, 'char_typ_enum': jqzwx__rrmn}, qzpt__ysn)
        impl = qzpt__ysn['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        fwuou__yqp = np.int32(numba_to_c_type(types.int32))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            rcxsn__qkcv = bodo.libs.array_item_arr_ext.get_offsets(data)
            jwdvl__rjbzi = bodo.libs.array_item_arr_ext.get_data(data)
            vqomo__olakh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ckt__ptg = bcast_scalar(len(data))
            uto__yxxbh = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                uto__yxxbh[i] = rcxsn__qkcv[i + 1] - rcxsn__qkcv[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                ckt__ptg)
            lveoe__ymbfn = bodo.ir.join.calc_disp(send_counts)
            xctkb__hfh = np.empty(n_pes, np.int32)
            if rank == 0:
                khicy__wdf = 0
                for i in range(n_pes):
                    qcubl__zwt = 0
                    for isbfm__ruv in range(send_counts[i]):
                        qcubl__zwt += uto__yxxbh[khicy__wdf]
                        khicy__wdf += 1
                    xctkb__hfh[i] = qcubl__zwt
            bcast(xctkb__hfh)
            xzf__made = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xzf__made[i] = send_counts[i] + 7 >> 3
            eml__tcit = bodo.ir.join.calc_disp(xzf__made)
            ksyf__chnmn = send_counts[rank]
            hws__qok = np.empty(ksyf__chnmn + 1, np_offset_type)
            anu__grb = bodo.libs.distributed_api.scatterv_impl(jwdvl__rjbzi,
                xctkb__hfh)
            mjzne__zyb = ksyf__chnmn + 7 >> 3
            uhmin__ulbg = np.empty(mjzne__zyb, np.uint8)
            dwus__hsxf = np.empty(ksyf__chnmn, np.uint32)
            c_scatterv(uto__yxxbh.ctypes, send_counts.ctypes, lveoe__ymbfn.
                ctypes, dwus__hsxf.ctypes, np.int32(ksyf__chnmn), fwuou__yqp)
            convert_len_arr_to_offset(dwus__hsxf.ctypes, hws__qok.ctypes,
                ksyf__chnmn)
            exm__oge = get_scatter_null_bytes_buff(vqomo__olakh.ctypes,
                send_counts, xzf__made)
            c_scatterv(exm__oge.ctypes, xzf__made.ctypes, eml__tcit.ctypes,
                uhmin__ulbg.ctypes, np.int32(mjzne__zyb), jqzwx__rrmn)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                ksyf__chnmn, anu__grb, hws__qok, uhmin__ulbg)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            qnynd__rghr = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            qnynd__rghr = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            qnynd__rghr = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            qnynd__rghr = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            qkvc__yykab = data._data
            ulh__vwaul = data._null_bitmap
            pkgoc__jjwcq = len(qkvc__yykab)
            ces__ojar = _scatterv_np(qkvc__yykab, send_counts)
            ckt__ptg = bcast_scalar(pkgoc__jjwcq)
            rdvx__zermg = len(ces__ojar) + 7 >> 3
            lkm__zomm = np.empty(rdvx__zermg, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                ckt__ptg)
            xzf__made = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xzf__made[i] = send_counts[i] + 7 >> 3
            eml__tcit = bodo.ir.join.calc_disp(xzf__made)
            exm__oge = get_scatter_null_bytes_buff(ulh__vwaul.ctypes,
                send_counts, xzf__made)
            c_scatterv(exm__oge.ctypes, xzf__made.ctypes, eml__tcit.ctypes,
                lkm__zomm.ctypes, np.int32(rdvx__zermg), jqzwx__rrmn)
            return qnynd__rghr(ces__ojar, lkm__zomm)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            cpnx__wczq = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            jhnhz__vzk = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(cpnx__wczq,
                jhnhz__vzk)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            ujddo__wmc = data._step
            qqi__fdko = data._name
            qqi__fdko = bcast_scalar(qqi__fdko)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            ujddo__wmc = bcast_scalar(ujddo__wmc)
            awu__zgewq = bodo.libs.array_kernels.calc_nitems(start, stop,
                ujddo__wmc)
            chunk_start = bodo.libs.distributed_api.get_start(awu__zgewq,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(awu__zgewq
                , n_pes, rank)
            ezru__skey = start + ujddo__wmc * chunk_start
            vqo__lexc = start + ujddo__wmc * (chunk_start + chunk_count)
            vqo__lexc = min(vqo__lexc, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(ezru__skey,
                vqo__lexc, ujddo__wmc, qqi__fdko)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        xuujg__tky = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            qkvc__yykab = data._data
            qqi__fdko = data._name
            qqi__fdko = bcast_scalar(qqi__fdko)
            arr = bodo.libs.distributed_api.scatterv_impl(qkvc__yykab,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                qqi__fdko, xuujg__tky)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            qkvc__yykab = data._data
            qqi__fdko = data._name
            qqi__fdko = bcast_scalar(qqi__fdko)
            arr = bodo.libs.distributed_api.scatterv_impl(qkvc__yykab,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, qqi__fdko)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            rtd__zzg = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            qqi__fdko = bcast_scalar(data._name)
            gpjq__qzw = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(rtd__zzg,
                gpjq__qzw, qqi__fdko)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qqi__fdko = bodo.hiframes.pd_series_ext.get_series_name(data)
            nsnwp__oah = bcast_scalar(qqi__fdko)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            iqjg__wlv = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                iqjg__wlv, nsnwp__oah)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hmwh__xxtw = len(data.columns)
        xgud__gwmcr = ', '.join('g_data_{}'.format(i) for i in range(
            hmwh__xxtw))
        mrxl__jser = bodo.utils.transform.gen_const_tup(data.columns)
        enk__jjbg = 'def impl_df(data, send_counts=None, warn_if_dist=True):\n'
        for i in range(hmwh__xxtw):
            enk__jjbg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            enk__jjbg += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        enk__jjbg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        enk__jjbg += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        enk__jjbg += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(xgud__gwmcr, mrxl__jser))
        qzpt__ysn = {}
        exec(enk__jjbg, {'bodo': bodo}, qzpt__ysn)
        gaeqg__supw = qzpt__ysn['impl_df']
        return gaeqg__supw
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            fuwp__ybnw = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                fuwp__ybnw, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        enk__jjbg = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        enk__jjbg += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        qzpt__ysn = {}
        exec(enk__jjbg, {'bodo': bodo}, qzpt__ysn)
        kkogp__kjgz = qzpt__ysn['impl_tuple']
        return kkogp__kjgz
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
        tjope__wtuan = np.int32(numba_to_c_type(offset_type))
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data):
            ksyf__chnmn = len(data)
            dms__mzi = num_total_chars(data)
            assert ksyf__chnmn < INT_MAX
            assert dms__mzi < INT_MAX
            zvd__xyunb = get_offset_ptr(data)
            rqybt__uhmd = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            exsh__zkdw = ksyf__chnmn + 7 >> 3
            c_bcast(zvd__xyunb, np.int32(ksyf__chnmn + 1), tjope__wtuan, np
                .array([-1]).ctypes, 0)
            c_bcast(rqybt__uhmd, np.int32(dms__mzi), jqzwx__rrmn, np.array(
                [-1]).ctypes, 0)
            c_bcast(null_bitmap_ptr, np.int32(exsh__zkdw), jqzwx__rrmn, np.
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
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != MPI_ROOT:
                uwjju__wvd = 0
                ekqes__rtjgv = np.empty(0, np.uint8).ctypes
            else:
                ekqes__rtjgv, uwjju__wvd = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            uwjju__wvd = bodo.libs.distributed_api.bcast_scalar(uwjju__wvd)
            if rank != MPI_ROOT:
                cskip__tipl = np.empty(uwjju__wvd + 1, np.uint8)
                cskip__tipl[uwjju__wvd] = 0
                ekqes__rtjgv = cskip__tipl.ctypes
            c_bcast(ekqes__rtjgv, np.int32(uwjju__wvd), jqzwx__rrmn, np.
                array([-1]).ctypes, 0)
            return bodo.libs.str_arr_ext.decode_utf8(ekqes__rtjgv, uwjju__wvd)
        return impl_str
    typ_val = numba_to_c_type(val)
    enk__jjbg = (
        """def bcast_scalar_impl(val):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({}), np.array([-1]).ctypes, 0)
  return send[0]
"""
        .format(typ_val))
    dtype = numba.np.numpy_support.as_dtype(val)
    qzpt__ysn = {}
    exec(enk__jjbg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, qzpt__ysn)
    kzrhd__xuuv = qzpt__ysn['bcast_scalar_impl']
    return kzrhd__xuuv


def bcast_tuple(val):
    return val


@overload(bcast_tuple, no_unliteral=True)
def overload_bcast_tuple(val):
    assert isinstance(val, types.BaseTuple)
    rhszr__yilxx = len(val)
    enk__jjbg = 'def bcast_tuple_impl(val):\n'
    enk__jjbg += '  return ({}{})'.format(','.join('bcast_scalar(val[{}])'.
        format(i) for i in range(rhszr__yilxx)), ',' if rhszr__yilxx else '')
    qzpt__ysn = {}
    exec(enk__jjbg, {'bcast_scalar': bcast_scalar}, qzpt__ysn)
    rbk__tsssb = qzpt__ysn['bcast_tuple_impl']
    return rbk__tsssb


def prealloc_str_for_bcast(arr):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr):
    if arr == string_array_type:

        def prealloc_impl(arr):
            rank = bodo.libs.distributed_api.get_rank()
            ksyf__chnmn = bcast_scalar(len(arr))
            zpgo__xhzm = bcast_scalar(np.int64(num_total_chars(arr)))
            if rank != MPI_ROOT:
                arr = pre_alloc_string_array(ksyf__chnmn, zpgo__xhzm)
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
        ujddo__wmc = slice_index.step
        glpa__keo = 0 if ujddo__wmc == 1 or start > arr_start else abs(
            ujddo__wmc - arr_start % ujddo__wmc) % ujddo__wmc
        ezru__skey = max(arr_start, slice_index.start) - arr_start + glpa__keo
        vqo__lexc = max(slice_index.stop - arr_start, 0)
        return slice(ezru__skey, vqo__lexc, ujddo__wmc)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        eeh__iyo = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[eeh__iyo])
    return getitem_impl


def slice_getitem_from_start(arr, slice_index):
    return arr[slice_index]


@overload(slice_getitem_from_start, no_unliteral=True)
def slice_getitem_from_start_overload(arr, slice_index):
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def getitem_datetime_date_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            ooouj__vbj = slice_index.stop
            A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                ooouj__vbj)
            if rank == 0:
                A = arr[:ooouj__vbj]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_date_impl
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def getitem_datetime_timedelta_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            ooouj__vbj = slice_index.stop
            A = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(ooouj__vbj))
            if rank == 0:
                A = arr[:ooouj__vbj]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_timedelta_impl
    if isinstance(arr.dtype, Decimal128Type):
        precision = arr.dtype.precision
        scale = arr.dtype.scale

        def getitem_decimal_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            ooouj__vbj = slice_index.stop
            A = bodo.libs.decimal_arr_ext.alloc_decimal_array(ooouj__vbj,
                precision, scale)
            if rank == 0:
                for i in range(ooouj__vbj):
                    A._data[i] = arr._data[i]
                    hsrqt__hzct = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, i,
                        hsrqt__hzct)
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_decimal_impl
    if arr == string_array_type:

        def getitem_str_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            ooouj__vbj = slice_index.stop
            posl__wsge = np.uint64(0)
            if rank == 0:
                out_arr = arr[:ooouj__vbj]
                posl__wsge = num_total_chars(out_arr)
            posl__wsge = bcast_scalar(posl__wsge)
            if rank != 0:
                out_arr = pre_alloc_string_array(ooouj__vbj, posl__wsge)
            bodo.libs.distributed_api.bcast(out_arr)
            return out_arr
        return getitem_str_impl
    zkdp__wpugj = arr

    def getitem_impl(arr, slice_index):
        rank = bodo.libs.distributed_api.get_rank()
        ooouj__vbj = slice_index.stop
        out_arr = bodo.utils.utils.alloc_type(tuple_to_scalar((ooouj__vbj,) +
            arr.shape[1:]), zkdp__wpugj)
        if rank == 0:
            out_arr = arr[:ooouj__vbj]
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
        uuhsp__mewx = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        jqzwx__rrmn = np.int32(numba_to_c_type(types.uint8))
        wxybc__ugse = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            ueupu__tkgs = np.int32(10)
            tag = np.int32(11)
            vzwan__nlskh = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                szvn__ngaip = arr._data
                hexdt__ymizt = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    szvn__ngaip, ind)
                eqei__ntsua = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    szvn__ngaip, ind + 1)
                length = eqei__ntsua - hexdt__ymizt
                qvbvm__dusyg = szvn__ngaip[ind]
                vzwan__nlskh[0] = length
                isend(vzwan__nlskh, np.int32(1), root, ueupu__tkgs, True)
                isend(qvbvm__dusyg, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                wxybc__ugse, uuhsp__mewx, 0, 1)
            ddjyh__twngv = 0
            if rank == root:
                ddjyh__twngv = recv(np.int64, ANY_SOURCE, ueupu__tkgs)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    wxybc__ugse, uuhsp__mewx, ddjyh__twngv, 1)
                rqybt__uhmd = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(rqybt__uhmd, np.int32(ddjyh__twngv), jqzwx__rrmn,
                    ANY_SOURCE, tag)
            dummy_use(vzwan__nlskh)
            ddjyh__twngv = bcast_scalar(ddjyh__twngv)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    wxybc__ugse, uuhsp__mewx, ddjyh__twngv, 1)
            rqybt__uhmd = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(rqybt__uhmd, np.int32(ddjyh__twngv), jqzwx__rrmn, np.
                array([-1]).ctypes, 0)
            val = transform_str_getitem_output(val, ddjyh__twngv)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        jit__ehn = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, jit__ehn)
            if arr_start <= ind < arr_start + len(arr):
                fuwp__ybnw = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = fuwp__ybnw[ind - arr_start]
                send_arr = np.full(1, data, jit__ehn)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = jit__ehn(-1)
            if rank == root:
                val = recv(jit__ehn, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            frkz__moon = arr.dtype.categories[max(val, 0)]
            return frkz__moon
        return cat_getitem_impl
    pltkj__mvfmg = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, pltkj__mvfmg)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, pltkj__mvfmg)[0]
        if rank == root:
            val = recv(pltkj__mvfmg, ANY_SOURCE, tag)
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
    siy__gtb = get_type_enum(out_data)
    assert typ_enum == siy__gtb
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
    enk__jjbg = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        enk__jjbg += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    enk__jjbg += '  return\n'
    qzpt__ysn = {}
    exec(enk__jjbg, {'alltoallv': alltoallv}, qzpt__ysn)
    skkux__bob = qzpt__ysn['f']
    return skkux__bob


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    start = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return start, count


@numba.njit
def get_start(total_size, pes, rank):
    cjsu__nxh = total_size % pes
    cyi__atpb = (total_size - cjsu__nxh) // pes
    return rank * cyi__atpb + min(rank, cjsu__nxh)


@numba.njit
def get_end(total_size, pes, rank):
    cjsu__nxh = total_size % pes
    cyi__atpb = (total_size - cjsu__nxh) // pes
    return (rank + 1) * cyi__atpb + min(rank + 1, cjsu__nxh)


@numba.njit
def get_node_portion(total_size, pes, rank):
    cjsu__nxh = total_size % pes
    cyi__atpb = (total_size - cjsu__nxh) // pes
    if rank < cjsu__nxh:
        return cyi__atpb + 1
    else:
        return cyi__atpb


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    oqmh__rmw = in_arr.dtype(0)
    qag__mwi = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        qcubl__zwt = oqmh__rmw
        for cuurz__vqb in np.nditer(in_arr):
            qcubl__zwt += cuurz__vqb.item()
        nqcsm__bkai = dist_exscan(qcubl__zwt, qag__mwi)
        for i in range(in_arr.size):
            nqcsm__bkai += in_arr[i]
            out_arr[i] = nqcsm__bkai
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    bzy__ejpcz = in_arr.dtype(1)
    qag__mwi = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        qcubl__zwt = bzy__ejpcz
        for cuurz__vqb in np.nditer(in_arr):
            qcubl__zwt *= cuurz__vqb.item()
        nqcsm__bkai = dist_exscan(qcubl__zwt, qag__mwi)
        if get_rank() == 0:
            nqcsm__bkai = bzy__ejpcz
        for i in range(in_arr.size):
            nqcsm__bkai *= in_arr[i]
            out_arr[i] = nqcsm__bkai
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        bzy__ejpcz = np.finfo(in_arr.dtype(1).dtype).max
    else:
        bzy__ejpcz = np.iinfo(in_arr.dtype(1).dtype).max
    qag__mwi = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        qcubl__zwt = bzy__ejpcz
        for cuurz__vqb in np.nditer(in_arr):
            qcubl__zwt = min(qcubl__zwt, cuurz__vqb.item())
        nqcsm__bkai = dist_exscan(qcubl__zwt, qag__mwi)
        if get_rank() == 0:
            nqcsm__bkai = bzy__ejpcz
        for i in range(in_arr.size):
            nqcsm__bkai = min(nqcsm__bkai, in_arr[i])
            out_arr[i] = nqcsm__bkai
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        bzy__ejpcz = np.finfo(in_arr.dtype(1).dtype).min
    else:
        bzy__ejpcz = np.iinfo(in_arr.dtype(1).dtype).min
    bzy__ejpcz = in_arr.dtype(1)
    qag__mwi = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        qcubl__zwt = bzy__ejpcz
        for cuurz__vqb in np.nditer(in_arr):
            qcubl__zwt = max(qcubl__zwt, cuurz__vqb.item())
        nqcsm__bkai = dist_exscan(qcubl__zwt, qag__mwi)
        if get_rank() == 0:
            nqcsm__bkai = bzy__ejpcz
        for i in range(in_arr.size):
            nqcsm__bkai = max(nqcsm__bkai, in_arr[i])
            out_arr[i] = nqcsm__bkai
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    bafb__jzea = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), bafb__jzea)


def dist_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    kscdv__ucwpx = args[0]
    if equiv_set.has_shape(kscdv__ucwpx):
        return ArrayAnalysis.AnalyzeResult(shape=kscdv__ucwpx, pre=[])
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
        zwkk__awzy = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        enk__jjbg = 'def f(req, cond=True):\n'
        enk__jjbg += f'  return {zwkk__awzy}\n'
        qzpt__ysn = {}
        exec(enk__jjbg, {'_wait': _wait}, qzpt__ysn)
        impl = qzpt__ysn['f']
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
    ezru__skey = max(start, chunk_start)
    vqo__lexc = min(stop, chunk_start + chunk_count)
    hxkfv__dgz = ezru__skey - chunk_start
    qhpa__bmhaf = vqo__lexc - chunk_start
    if hxkfv__dgz < 0 or qhpa__bmhaf < 0:
        hxkfv__dgz = 1
        qhpa__bmhaf = 0
    return hxkfv__dgz, qhpa__bmhaf


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
        cjsu__nxh = 1
        for a in t:
            cjsu__nxh *= a
        return cjsu__nxh
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    ytfuh__byo = np.ascontiguousarray(in_arr)
    nxw__djrr = get_tuple_prod(ytfuh__byo.shape[1:])
    wokj__ycu = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        ywt__zrxav = np.array(dest_ranks, dtype=np.int32)
    else:
        ywt__zrxav = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, ytfuh__byo.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * wokj__ycu, dtype_size * nxw__djrr, len(
        ywt__zrxav), ywt__zrxav.ctypes)
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
    zpr__dzvm = np.ascontiguousarray(rhs)
    fbv__uhr = get_tuple_prod(zpr__dzvm.shape[1:])
    uje__peam = dtype_size * fbv__uhr
    permutation_array_index(lhs.ctypes, lhs_len, uje__peam, zpr__dzvm.
        ctypes, zpr__dzvm.shape[0], p.ctypes, p_len)
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
        enk__jjbg = (
            """def bcast_scalar_impl(data, comm_ranks, nranks):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({}), comm_ranks,ctypes, np.int32({}))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        qzpt__ysn = {}
        exec(enk__jjbg, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, qzpt__ysn)
        kzrhd__xuuv = qzpt__ysn['bcast_scalar_impl']
        return kzrhd__xuuv
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks: _bcast_np(data, comm_ranks,
            nranks)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hmwh__xxtw = len(data.columns)
        xgud__gwmcr = ', '.join('g_data_{}'.format(i) for i in range(
            hmwh__xxtw))
        mrxl__jser = bodo.utils.transform.gen_const_tup(data.columns)
        enk__jjbg = 'def impl_df(data, comm_ranks, nranks):\n'
        for i in range(hmwh__xxtw):
            enk__jjbg += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            enk__jjbg += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks)
"""
                .format(i, i))
        enk__jjbg += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        enk__jjbg += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks)
"""
        enk__jjbg += (
            '  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})\n'
            .format(xgud__gwmcr, mrxl__jser))
        qzpt__ysn = {}
        exec(enk__jjbg, {'bodo': bodo}, qzpt__ysn)
        gaeqg__supw = qzpt__ysn['impl_df']
        return gaeqg__supw
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            ujddo__wmc = data._step
            qqi__fdko = data._name
            qqi__fdko = bcast_scalar(qqi__fdko)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            ujddo__wmc = bcast_scalar(ujddo__wmc)
            awu__zgewq = bodo.libs.array_kernels.calc_nitems(start, stop,
                ujddo__wmc)
            chunk_start = bodo.libs.distributed_api.get_start(awu__zgewq,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(awu__zgewq
                , n_pes, rank)
            ezru__skey = start + ujddo__wmc * chunk_start
            vqo__lexc = start + ujddo__wmc * (chunk_start + chunk_count)
            vqo__lexc = min(vqo__lexc, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(ezru__skey,
                vqo__lexc, ujddo__wmc, qqi__fdko)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks):
            qkvc__yykab = data._data
            qqi__fdko = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(qkvc__yykab,
                comm_ranks, nranks)
            return bodo.utils.conversion.index_from_array(arr, qqi__fdko)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qqi__fdko = bodo.hiframes.pd_series_ext.get_series_name(data)
            nsnwp__oah = bodo.libs.distributed_api.bcast_comm_impl(qqi__fdko,
                comm_ranks, nranks)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks)
            iqjg__wlv = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                iqjg__wlv, nsnwp__oah)
        return impl_series
    if isinstance(data, types.BaseTuple):
        enk__jjbg = 'def impl_tuple(data, comm_ranks, nranks):\n'
        enk__jjbg += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks)'.format(i) for i in
            range(len(data))), ',' if len(data) > 0 else '')
        qzpt__ysn = {}
        exec(enk__jjbg, {'bcast_comm_impl': bcast_comm_impl}, qzpt__ysn)
        kkogp__kjgz = qzpt__ysn['impl_tuple']
        return kkogp__kjgz
    if data is types.none:
        return lambda data, comm_ranks, nranks: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks):
    typ_val = numba_to_c_type(data.dtype)
    mafaj__xxsv = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    dil__sjnqu = (0,) * mafaj__xxsv

    def bcast_arr_impl(data, comm_ranks, nranks):
        rank = bodo.libs.distributed_api.get_rank()
        qkvc__yykab = np.ascontiguousarray(data)
        rqybt__uhmd = data.ctypes
        uhuo__uimly = dil__sjnqu
        if rank == MPI_ROOT:
            uhuo__uimly = qkvc__yykab.shape
        uhuo__uimly = bcast_tuple(uhuo__uimly)
        daoj__twa = get_tuple_prod(uhuo__uimly[1:])
        send_counts = uhuo__uimly[0] * daoj__twa
        wyiqs__fvxrk = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(rqybt__uhmd, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks))
            return data
        else:
            c_bcast(wyiqs__fvxrk.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks))
            return wyiqs__fvxrk.reshape((-1,) + uhuo__uimly[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        feaa__gas = MPI.COMM_WORLD
        ohtgj__wyff = MPI.Get_processor_name()
        uuaeq__jwwn = feaa__gas.allgather(ohtgj__wyff)
        node_ranks = defaultdict(list)
        for i, fvre__jxm in enumerate(uuaeq__jwwn):
            node_ranks[fvre__jxm].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    feaa__gas = MPI.COMM_WORLD
    lrzn__rzdju = feaa__gas.Get_group()
    eemv__ebh = lrzn__rzdju.Incl(comm_ranks)
    qnsci__qdpz = feaa__gas.Create_group(eemv__ebh)
    return qnsci__qdpz


def get_nodes_first_ranks():
    bradk__hjp = get_host_ranks()
    return np.array([jwfi__xdfc[0] for jwfi__xdfc in bradk__hjp.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
