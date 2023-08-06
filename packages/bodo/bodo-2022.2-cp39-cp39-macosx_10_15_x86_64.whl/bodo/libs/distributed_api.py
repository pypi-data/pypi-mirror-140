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
    sham__kzpto = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, sham__kzpto, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    sham__kzpto = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, sham__kzpto, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            sham__kzpto = get_type_enum(arr)
            return _isend(arr.ctypes, size, sham__kzpto, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        sham__kzpto = np.int32(numba_to_c_type(arr.dtype))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            nrqug__nmrl = size + 7 >> 3
            vpswc__rrpy = _isend(arr._data.ctypes, size, sham__kzpto, pe,
                tag, cond)
            utrp__voimn = _isend(arr._null_bitmap.ctypes, nrqug__nmrl,
                pyf__yvfc, pe, tag, cond)
            return vpswc__rrpy, utrp__voimn
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        hvje__dxx = np.int32(numba_to_c_type(offset_type))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            okfhi__blbww = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(okfhi__blbww, pe, tag - 1)
            nrqug__nmrl = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                hvje__dxx, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), okfhi__blbww,
                pyf__yvfc, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                nrqug__nmrl, pyf__yvfc, pe, tag)
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
            sham__kzpto = get_type_enum(arr)
            return _irecv(arr.ctypes, size, sham__kzpto, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        sham__kzpto = np.int32(numba_to_c_type(arr.dtype))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            nrqug__nmrl = size + 7 >> 3
            vpswc__rrpy = _irecv(arr._data.ctypes, size, sham__kzpto, pe,
                tag, cond)
            utrp__voimn = _irecv(arr._null_bitmap.ctypes, nrqug__nmrl,
                pyf__yvfc, pe, tag, cond)
            return vpswc__rrpy, utrp__voimn
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        hvje__dxx = np.int32(numba_to_c_type(offset_type))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            snz__mgmn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            snz__mgmn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        fzfr__durq = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {snz__mgmn}(size, n_chars)
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
        fyp__aidfh = dict()
        exec(fzfr__durq, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            hvje__dxx, 'char_typ_enum': pyf__yvfc}, fyp__aidfh)
        impl = fyp__aidfh['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    sham__kzpto = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), sham__kzpto)


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
        qam__zaqr = n_pes if rank == root or allgather else 0
        ehgsm__gmqbh = np.empty(qam__zaqr, dtype)
        c_gather_scalar(send.ctypes, ehgsm__gmqbh.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return ehgsm__gmqbh
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
        kky__muxeu = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], kky__muxeu)
        return builder.bitcast(kky__muxeu, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        kky__muxeu = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(kky__muxeu)
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
    lkk__grz = types.unliteral(value)
    if isinstance(lkk__grz, IndexValueType):
        lkk__grz = lkk__grz.val_typ
        uvi__hlvoo = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            uvi__hlvoo.append(types.int64)
            uvi__hlvoo.append(bodo.datetime64ns)
            uvi__hlvoo.append(bodo.timedelta64ns)
            uvi__hlvoo.append(bodo.datetime_date_type)
        if lkk__grz not in uvi__hlvoo:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(lkk__grz))
    typ_enum = np.int32(numba_to_c_type(lkk__grz))

    def impl(value, reduce_op):
        wzftx__hunsn = value_to_ptr(value)
        gka__cptnt = value_to_ptr(value)
        _dist_reduce(wzftx__hunsn, gka__cptnt, reduce_op, typ_enum)
        return load_val_ptr(gka__cptnt, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    lkk__grz = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(lkk__grz))
    ehul__nzjts = lkk__grz(0)

    def impl(value, reduce_op):
        wzftx__hunsn = value_to_ptr(value)
        gka__cptnt = value_to_ptr(ehul__nzjts)
        _dist_exscan(wzftx__hunsn, gka__cptnt, reduce_op, typ_enum)
        return load_val_ptr(gka__cptnt, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    duty__yji = 0
    qgwof__owfu = 0
    for i in range(len(recv_counts)):
        wmsw__iyyc = recv_counts[i]
        nrqug__nmrl = recv_counts_nulls[i]
        gmfl__lvoso = tmp_null_bytes[duty__yji:duty__yji + nrqug__nmrl]
        for ysu__ypu in range(wmsw__iyyc):
            set_bit_to(null_bitmap_ptr, qgwof__owfu, get_bit(gmfl__lvoso,
                ysu__ypu))
            qgwof__owfu += 1
        duty__yji += nrqug__nmrl


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            dmqmo__qhixa = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                dmqmo__qhixa, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            bevz__uawx = data.size
            recv_counts = gather_scalar(np.int32(bevz__uawx), allgather,
                root=root)
            jyh__qnrcd = recv_counts.sum()
            vcdqu__limap = empty_like_type(jyh__qnrcd, data)
            kyg__efll = np.empty(1, np.int32)
            if rank == root or allgather:
                kyg__efll = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(bevz__uawx), vcdqu__limap.
                ctypes, recv_counts.ctypes, kyg__efll.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return vcdqu__limap.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if data == string_array_type:

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            vcdqu__limap = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.str_arr_ext.init_str_arr(vcdqu__limap)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            vcdqu__limap = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.binary_arr_ext.init_binary_arr(vcdqu__limap)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            bevz__uawx = len(data)
            nrqug__nmrl = bevz__uawx + 7 >> 3
            recv_counts = gather_scalar(np.int32(bevz__uawx), allgather,
                root=root)
            jyh__qnrcd = recv_counts.sum()
            vcdqu__limap = empty_like_type(jyh__qnrcd, data)
            kyg__efll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            xcw__hnoln = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kyg__efll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                xcw__hnoln = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(bevz__uawx),
                vcdqu__limap._days_data.ctypes, recv_counts.ctypes,
                kyg__efll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(bevz__uawx),
                vcdqu__limap._seconds_data.ctypes, recv_counts.ctypes,
                kyg__efll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(bevz__uawx),
                vcdqu__limap._microseconds_data.ctypes, recv_counts.ctypes,
                kyg__efll.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(nrqug__nmrl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, xcw__hnoln
                .ctypes, pyf__yvfc, allgather, np.int32(root))
            copy_gathered_null_bytes(vcdqu__limap._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return vcdqu__limap
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            bevz__uawx = len(data)
            nrqug__nmrl = bevz__uawx + 7 >> 3
            recv_counts = gather_scalar(np.int32(bevz__uawx), allgather,
                root=root)
            jyh__qnrcd = recv_counts.sum()
            vcdqu__limap = empty_like_type(jyh__qnrcd, data)
            kyg__efll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            xcw__hnoln = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kyg__efll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                xcw__hnoln = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(bevz__uawx), vcdqu__limap
                ._data.ctypes, recv_counts.ctypes, kyg__efll.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(nrqug__nmrl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, xcw__hnoln
                .ctypes, pyf__yvfc, allgather, np.int32(root))
            copy_gathered_null_bytes(vcdqu__limap._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return vcdqu__limap
        return gatherv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            toano__pbdyk = bodo.gatherv(data._left, allgather, warn_if_rep,
                root)
            trj__gagdr = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(toano__pbdyk,
                trj__gagdr)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pktdq__viyk = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            evykd__dkuf = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                evykd__dkuf, pktdq__viyk)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        nlwa__uynn = np.iinfo(np.int64).max
        iuv__ytw = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            start = data._start
            stop = data._stop
            if len(data) == 0:
                start = nlwa__uynn
                stop = iuv__ytw
            start = bodo.libs.distributed_api.dist_reduce(start, np.int32(
                Reduce_Type.Min.value))
            stop = bodo.libs.distributed_api.dist_reduce(stop, np.int32(
                Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if start == nlwa__uynn and stop == iuv__ytw:
                start = 0
                stop = 0
            ghg__pljb = max(0, -(-(stop - start) // data._step))
            if ghg__pljb < total_len:
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
            gmrdq__xjckv = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, gmrdq__xjckv)
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
            vcdqu__limap = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                vcdqu__limap, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        iwu__qlkkx = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        fzfr__durq = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        fzfr__durq += '  T = data\n'
        fzfr__durq += '  T2 = init_table(T)\n'
        for iykuo__wmyg in data.type_to_blk.values():
            iwu__qlkkx[f'arr_inds_{iykuo__wmyg}'] = np.array(data.
                block_to_arr_ind[iykuo__wmyg], dtype=np.int64)
            fzfr__durq += (
                f'  arr_list_{iykuo__wmyg} = get_table_block(T, {iykuo__wmyg})\n'
                )
            fzfr__durq += f"""  out_arr_list_{iykuo__wmyg} = alloc_list_like(arr_list_{iykuo__wmyg})
"""
            fzfr__durq += f'  for i in range(len(arr_list_{iykuo__wmyg})):\n'
            fzfr__durq += (
                f'    arr_ind_{iykuo__wmyg} = arr_inds_{iykuo__wmyg}[i]\n')
            fzfr__durq += f"""    ensure_column_unboxed(T, arr_list_{iykuo__wmyg}, i, arr_ind_{iykuo__wmyg})
"""
            fzfr__durq += f"""    out_arr_{iykuo__wmyg} = bodo.gatherv(arr_list_{iykuo__wmyg}[i], allgather, warn_if_rep, root)
"""
            fzfr__durq += (
                f'    out_arr_list_{iykuo__wmyg}[i] = out_arr_{iykuo__wmyg}\n')
            fzfr__durq += (
                f'  T2 = set_table_block(T2, out_arr_list_{iykuo__wmyg}, {iykuo__wmyg})\n'
                )
        fzfr__durq += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        fzfr__durq += f'  T2 = set_table_len(T2, length)\n'
        fzfr__durq += f'  return T2\n'
        fyp__aidfh = {}
        exec(fzfr__durq, iwu__qlkkx, fyp__aidfh)
        gmk__lcx = fyp__aidfh['impl_table']
        return gmk__lcx
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ohkhw__vdmv = len(data.columns)
        if ohkhw__vdmv == 0:
            return (lambda data, allgather=False, warn_if_rep=True, root=
                MPI_ROOT: bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data), ()))
        vnq__hho = ', '.join(f'g_data_{i}' for i in range(ohkhw__vdmv))
        doa__rar = bodo.utils.transform.gen_const_tup(data.columns)
        fzfr__durq = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            kskuk__atifd = bodo.hiframes.pd_dataframe_ext.DataFrameType(data
                .data, data.index, data.columns, Distribution.REP, True)
            iwu__qlkkx = {'bodo': bodo, 'df_type': kskuk__atifd}
            vnq__hho = 'T2'
            doa__rar = 'df_type'
            fzfr__durq += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            fzfr__durq += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            iwu__qlkkx = {'bodo': bodo}
            for i in range(ohkhw__vdmv):
                fzfr__durq += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                fzfr__durq += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        fzfr__durq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fzfr__durq += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        fzfr__durq += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(vnq__hho, doa__rar))
        fyp__aidfh = {}
        exec(fzfr__durq, iwu__qlkkx, fyp__aidfh)
        pfvth__icszs = fyp__aidfh['impl_df']
        return pfvth__icszs
    if isinstance(data, ArrayItemArrayType):
        olcv__lyedy = np.int32(numba_to_c_type(types.int32))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            lfy__cijn = bodo.libs.array_item_arr_ext.get_offsets(data)
            tzrsq__mumw = bodo.libs.array_item_arr_ext.get_data(data)
            fyu__rocd = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            bevz__uawx = len(data)
            wueo__mwok = np.empty(bevz__uawx, np.uint32)
            nrqug__nmrl = bevz__uawx + 7 >> 3
            for i in range(bevz__uawx):
                wueo__mwok[i] = lfy__cijn[i + 1] - lfy__cijn[i]
            recv_counts = gather_scalar(np.int32(bevz__uawx), allgather,
                root=root)
            jyh__qnrcd = recv_counts.sum()
            kyg__efll = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            xcw__hnoln = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                kyg__efll = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for urmp__iwia in range(len(recv_counts)):
                    recv_counts_nulls[urmp__iwia] = recv_counts[urmp__iwia
                        ] + 7 >> 3
                xcw__hnoln = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            qxmkj__djoxy = np.empty(jyh__qnrcd + 1, np.uint32)
            bmr__zgi = bodo.gatherv(tzrsq__mumw, allgather, warn_if_rep, root)
            pvdy__yhy = np.empty(jyh__qnrcd + 7 >> 3, np.uint8)
            c_gatherv(wueo__mwok.ctypes, np.int32(bevz__uawx), qxmkj__djoxy
                .ctypes, recv_counts.ctypes, kyg__efll.ctypes, olcv__lyedy,
                allgather, np.int32(root))
            c_gatherv(fyu__rocd.ctypes, np.int32(nrqug__nmrl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, xcw__hnoln
                .ctypes, pyf__yvfc, allgather, np.int32(root))
            dummy_use(data)
            uokb__whth = np.empty(jyh__qnrcd + 1, np.uint64)
            convert_len_arr_to_offset(qxmkj__djoxy.ctypes, uokb__whth.
                ctypes, jyh__qnrcd)
            copy_gathered_null_bytes(pvdy__yhy.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                jyh__qnrcd, bmr__zgi, uokb__whth, pvdy__yhy)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        njwt__dljd = data.names
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            xrmj__atysv = bodo.libs.struct_arr_ext.get_data(data)
            iaq__vwvd = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            pmzgz__knkt = bodo.gatherv(xrmj__atysv, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            bevz__uawx = len(data)
            nrqug__nmrl = bevz__uawx + 7 >> 3
            recv_counts = gather_scalar(np.int32(bevz__uawx), allgather,
                root=root)
            jyh__qnrcd = recv_counts.sum()
            mgf__nch = np.empty(jyh__qnrcd + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            xcw__hnoln = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                xcw__hnoln = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(iaq__vwvd.ctypes, np.int32(nrqug__nmrl),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, xcw__hnoln
                .ctypes, pyf__yvfc, allgather, np.int32(root))
            copy_gathered_null_bytes(mgf__nch.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(pmzgz__knkt,
                mgf__nch, njwt__dljd)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            vcdqu__limap = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.binary_arr_ext.init_binary_arr(vcdqu__limap)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vcdqu__limap = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(vcdqu__limap)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            vcdqu__limap = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.map_arr_ext.init_map_arr(vcdqu__limap)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vcdqu__limap = bodo.gatherv(data.data, allgather, warn_if_rep, root
                )
            sqo__vvjvo = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            qmc__kaskj = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            jlrkd__htuk = gather_scalar(data.shape[0], allgather, root=root)
            ohup__sihmg = jlrkd__htuk.sum()
            ohkhw__vdmv = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            relgk__qhwh = np.empty(ohup__sihmg + 1, np.int64)
            sqo__vvjvo = sqo__vvjvo.astype(np.int64)
            relgk__qhwh[0] = 0
            uqooh__skp = 1
            rqtob__nzr = 0
            for eefy__qrg in jlrkd__htuk:
                for yuap__zqbws in range(eefy__qrg):
                    fkze__stv = qmc__kaskj[rqtob__nzr + 1] - qmc__kaskj[
                        rqtob__nzr]
                    relgk__qhwh[uqooh__skp] = relgk__qhwh[uqooh__skp - 1
                        ] + fkze__stv
                    uqooh__skp += 1
                    rqtob__nzr += 1
                rqtob__nzr += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(vcdqu__limap,
                sqo__vvjvo, relgk__qhwh, (ohup__sihmg, ohkhw__vdmv))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        fzfr__durq = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        fzfr__durq += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        fyp__aidfh = {}
        exec(fzfr__durq, {'bodo': bodo}, fyp__aidfh)
        jggly__uuhcv = fyp__aidfh['impl_tuple']
        return jggly__uuhcv
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    fzfr__durq = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    fzfr__durq += '    if random:\n'
    fzfr__durq += '        if random_seed is None:\n'
    fzfr__durq += '            random = 1\n'
    fzfr__durq += '        else:\n'
    fzfr__durq += '            random = 2\n'
    fzfr__durq += '    if random_seed is None:\n'
    fzfr__durq += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ilwg__bhuga = data
        ohkhw__vdmv = len(ilwg__bhuga.columns)
        for i in range(ohkhw__vdmv):
            fzfr__durq += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        fzfr__durq += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        vnq__hho = ', '.join(f'data_{i}' for i in range(ohkhw__vdmv))
        fzfr__durq += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(nhe__qoxfc) for
            nhe__qoxfc in range(ohkhw__vdmv))))
        fzfr__durq += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        fzfr__durq += '    if dests is None:\n'
        fzfr__durq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fzfr__durq += '    else:\n'
        fzfr__durq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for najdd__aboi in range(ohkhw__vdmv):
            fzfr__durq += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(najdd__aboi))
        fzfr__durq += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(ohkhw__vdmv))
        fzfr__durq += '    delete_table(out_table)\n'
        fzfr__durq += '    if parallel:\n'
        fzfr__durq += '        delete_table(table_total)\n'
        vnq__hho = ', '.join('out_arr_{}'.format(i) for i in range(ohkhw__vdmv)
            )
        doa__rar = bodo.utils.transform.gen_const_tup(ilwg__bhuga.columns)
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        fzfr__durq += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, {})\n'
            .format(vnq__hho, index, doa__rar))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        fzfr__durq += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        fzfr__durq += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        fzfr__durq += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        fzfr__durq += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        fzfr__durq += '    if dests is None:\n'
        fzfr__durq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fzfr__durq += '    else:\n'
        fzfr__durq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        fzfr__durq += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        fzfr__durq += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        fzfr__durq += '    delete_table(out_table)\n'
        fzfr__durq += '    if parallel:\n'
        fzfr__durq += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        fzfr__durq += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        fzfr__durq += '    if not parallel:\n'
        fzfr__durq += '        return data\n'
        fzfr__durq += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        fzfr__durq += '    if dests is None:\n'
        fzfr__durq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        fzfr__durq += '    elif bodo.get_rank() not in dests:\n'
        fzfr__durq += '        dim0_local_size = 0\n'
        fzfr__durq += '    else:\n'
        fzfr__durq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        fzfr__durq += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        fzfr__durq += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        fzfr__durq += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        fzfr__durq += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        fzfr__durq += '    if dests is None:\n'
        fzfr__durq += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fzfr__durq += '    else:\n'
        fzfr__durq += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        fzfr__durq += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        fzfr__durq += '    delete_table(out_table)\n'
        fzfr__durq += '    if parallel:\n'
        fzfr__durq += '        delete_table(table_total)\n'
        fzfr__durq += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    fyp__aidfh = {}
    exec(fzfr__durq, {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table},
        fyp__aidfh)
    impl = fyp__aidfh['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, parallel=False):
    fzfr__durq = 'def impl(data, seed=None, dests=None, parallel=False):\n'
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        fzfr__durq += '    if seed is None:\n'
        fzfr__durq += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        fzfr__durq += '    np.random.seed(seed)\n'
        fzfr__durq += '    if not parallel:\n'
        fzfr__durq += '        data = data.copy()\n'
        fzfr__durq += '        np.random.shuffle(data)\n'
        fzfr__durq += '        return data\n'
        fzfr__durq += '    else:\n'
        fzfr__durq += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        fzfr__durq += '        permutation = np.arange(dim0_global_size)\n'
        fzfr__durq += '        np.random.shuffle(permutation)\n'
        fzfr__durq += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        fzfr__durq += """        output = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        fzfr__durq += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        fzfr__durq += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation))
"""
        fzfr__durq += '        return output\n'
    else:
        fzfr__durq += """    return bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
    fyp__aidfh = {}
    exec(fzfr__durq, {'np': np, 'bodo': bodo}, fyp__aidfh)
    impl = fyp__aidfh['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    pbnyp__jpqo = np.empty(sendcounts_nulls.sum(), np.uint8)
    duty__yji = 0
    qgwof__owfu = 0
    for fzn__iras in range(len(sendcounts)):
        wmsw__iyyc = sendcounts[fzn__iras]
        nrqug__nmrl = sendcounts_nulls[fzn__iras]
        gmfl__lvoso = pbnyp__jpqo[duty__yji:duty__yji + nrqug__nmrl]
        for ysu__ypu in range(wmsw__iyyc):
            set_bit_to_arr(gmfl__lvoso, ysu__ypu, get_bit_bitmap(
                null_bitmap_ptr, qgwof__owfu))
            qgwof__owfu += 1
        duty__yji += nrqug__nmrl
    return pbnyp__jpqo


def _bcast_dtype(data):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    zxvv__unyr = MPI.COMM_WORLD
    data = zxvv__unyr.bcast(data)
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
    tlqg__jpefy = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    lwj__oneg = (0,) * tlqg__jpefy

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        ojlz__dsn = np.ascontiguousarray(data)
        ukhgq__dpkd = data.ctypes
        dzu__vmg = lwj__oneg
        if rank == MPI_ROOT:
            dzu__vmg = ojlz__dsn.shape
        dzu__vmg = bcast_tuple(dzu__vmg)
        hwex__tck = get_tuple_prod(dzu__vmg[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes, dzu__vmg[0]
            )
        send_counts *= hwex__tck
        bevz__uawx = send_counts[rank]
        eum__vtq = np.empty(bevz__uawx, dtype)
        kyg__efll = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(ukhgq__dpkd, send_counts.ctypes, kyg__efll.ctypes,
            eum__vtq.ctypes, np.int32(bevz__uawx), np.int32(typ_val))
        return eum__vtq.reshape((-1,) + dzu__vmg[1:])
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
        vtaae__smbh = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], vtaae__smbh)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        pktdq__viyk = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=pktdq__viyk)
        jlb__jfr = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(jlb__jfr)
        return pd.Index(arr, name=pktdq__viyk)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        pktdq__viyk = _get_name_value_for_type(dtype.name_typ)
        njwt__dljd = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        ghrt__ftsxw = tuple(get_value_for_type(t) for t in dtype.array_types)
        val = pd.MultiIndex.from_arrays(ghrt__ftsxw, names=njwt__dljd)
        val.name = pktdq__viyk
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        pktdq__viyk = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=pktdq__viyk)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ghrt__ftsxw = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({pktdq__viyk: arr for pktdq__viyk, arr in zip(
            dtype.columns, ghrt__ftsxw)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        jlb__jfr = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(jlb__jfr[0], jlb__jfr[0])])
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
        olcv__lyedy = np.int32(numba_to_c_type(types.int32))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            snz__mgmn = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            snz__mgmn = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        fzfr__durq = f"""def impl(
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
            recv_arr = {snz__mgmn}(n_loc, n_loc_char)

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
        fyp__aidfh = dict()
        exec(fzfr__durq, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            olcv__lyedy, 'char_typ_enum': pyf__yvfc}, fyp__aidfh)
        impl = fyp__aidfh['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        olcv__lyedy = np.int32(numba_to_c_type(types.int32))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            eini__mtzzb = bodo.libs.array_item_arr_ext.get_offsets(data)
            spohu__lbrf = bodo.libs.array_item_arr_ext.get_data(data)
            huw__nghkh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            qyptg__jez = bcast_scalar(len(data))
            azmn__loxk = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                azmn__loxk[i] = eini__mtzzb[i + 1] - eini__mtzzb[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                qyptg__jez)
            kyg__efll = bodo.ir.join.calc_disp(send_counts)
            qkzk__akl = np.empty(n_pes, np.int32)
            if rank == 0:
                pjzpj__wswd = 0
                for i in range(n_pes):
                    bugw__cfgq = 0
                    for yuap__zqbws in range(send_counts[i]):
                        bugw__cfgq += azmn__loxk[pjzpj__wswd]
                        pjzpj__wswd += 1
                    qkzk__akl[i] = bugw__cfgq
            bcast(qkzk__akl)
            all__xsrq = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                all__xsrq[i] = send_counts[i] + 7 >> 3
            xcw__hnoln = bodo.ir.join.calc_disp(all__xsrq)
            bevz__uawx = send_counts[rank]
            wln__ggjm = np.empty(bevz__uawx + 1, np_offset_type)
            hrui__jxsls = bodo.libs.distributed_api.scatterv_impl(spohu__lbrf,
                qkzk__akl)
            rnlx__zff = bevz__uawx + 7 >> 3
            htxxx__dwngw = np.empty(rnlx__zff, np.uint8)
            hciv__qovrj = np.empty(bevz__uawx, np.uint32)
            c_scatterv(azmn__loxk.ctypes, send_counts.ctypes, kyg__efll.
                ctypes, hciv__qovrj.ctypes, np.int32(bevz__uawx), olcv__lyedy)
            convert_len_arr_to_offset(hciv__qovrj.ctypes, wln__ggjm.ctypes,
                bevz__uawx)
            jptxc__cru = get_scatter_null_bytes_buff(huw__nghkh.ctypes,
                send_counts, all__xsrq)
            c_scatterv(jptxc__cru.ctypes, all__xsrq.ctypes, xcw__hnoln.
                ctypes, htxxx__dwngw.ctypes, np.int32(rnlx__zff), pyf__yvfc)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                bevz__uawx, hrui__jxsls, wln__ggjm, htxxx__dwngw)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            gnq__qqkou = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            gnq__qqkou = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            gnq__qqkou = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            gnq__qqkou = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            ojlz__dsn = data._data
            iaq__vwvd = data._null_bitmap
            uqmd__icvk = len(ojlz__dsn)
            szatn__rfg = _scatterv_np(ojlz__dsn, send_counts)
            qyptg__jez = bcast_scalar(uqmd__icvk)
            nolrn__kby = len(szatn__rfg) + 7 >> 3
            myt__dngc = np.empty(nolrn__kby, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                qyptg__jez)
            all__xsrq = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                all__xsrq[i] = send_counts[i] + 7 >> 3
            xcw__hnoln = bodo.ir.join.calc_disp(all__xsrq)
            jptxc__cru = get_scatter_null_bytes_buff(iaq__vwvd.ctypes,
                send_counts, all__xsrq)
            c_scatterv(jptxc__cru.ctypes, all__xsrq.ctypes, xcw__hnoln.
                ctypes, myt__dngc.ctypes, np.int32(nolrn__kby), pyf__yvfc)
            return gnq__qqkou(szatn__rfg, myt__dngc)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            iua__sbdf = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            igdd__zuxf = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(iua__sbdf,
                igdd__zuxf)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            ohsrk__kzvd = data._step
            pktdq__viyk = data._name
            pktdq__viyk = bcast_scalar(pktdq__viyk)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            ohsrk__kzvd = bcast_scalar(ohsrk__kzvd)
            anb__awtg = bodo.libs.array_kernels.calc_nitems(start, stop,
                ohsrk__kzvd)
            chunk_start = bodo.libs.distributed_api.get_start(anb__awtg,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(anb__awtg,
                n_pes, rank)
            awu__sbg = start + ohsrk__kzvd * chunk_start
            edchw__tgmyp = start + ohsrk__kzvd * (chunk_start + chunk_count)
            edchw__tgmyp = min(edchw__tgmyp, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(awu__sbg,
                edchw__tgmyp, ohsrk__kzvd, pktdq__viyk)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        gmrdq__xjckv = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            ojlz__dsn = data._data
            pktdq__viyk = data._name
            pktdq__viyk = bcast_scalar(pktdq__viyk)
            arr = bodo.libs.distributed_api.scatterv_impl(ojlz__dsn,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                pktdq__viyk, gmrdq__xjckv)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            ojlz__dsn = data._data
            pktdq__viyk = data._name
            pktdq__viyk = bcast_scalar(pktdq__viyk)
            arr = bodo.libs.distributed_api.scatterv_impl(ojlz__dsn,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, pktdq__viyk)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            vcdqu__limap = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            pktdq__viyk = bcast_scalar(data._name)
            njwt__dljd = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                vcdqu__limap, njwt__dljd, pktdq__viyk)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pktdq__viyk = bodo.hiframes.pd_series_ext.get_series_name(data)
            vutjg__ofu = bcast_scalar(pktdq__viyk)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            evykd__dkuf = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                evykd__dkuf, vutjg__ofu)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ohkhw__vdmv = len(data.columns)
        vnq__hho = ', '.join('g_data_{}'.format(i) for i in range(ohkhw__vdmv))
        doa__rar = bodo.utils.transform.gen_const_tup(data.columns)
        fzfr__durq = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(ohkhw__vdmv):
            fzfr__durq += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            fzfr__durq += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        fzfr__durq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fzfr__durq += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        fzfr__durq += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(vnq__hho, doa__rar))
        fyp__aidfh = {}
        exec(fzfr__durq, {'bodo': bodo}, fyp__aidfh)
        pfvth__icszs = fyp__aidfh['impl_df']
        return pfvth__icszs
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            dmqmo__qhixa = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                dmqmo__qhixa, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        fzfr__durq = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        fzfr__durq += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        fyp__aidfh = {}
        exec(fzfr__durq, {'bodo': bodo}, fyp__aidfh)
        jggly__uuhcv = fyp__aidfh['impl_tuple']
        return jggly__uuhcv
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
        hvje__dxx = np.int32(numba_to_c_type(offset_type))
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data):
            bevz__uawx = len(data)
            fqw__ayi = num_total_chars(data)
            assert bevz__uawx < INT_MAX
            assert fqw__ayi < INT_MAX
            rfns__ejd = get_offset_ptr(data)
            ukhgq__dpkd = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            nrqug__nmrl = bevz__uawx + 7 >> 3
            c_bcast(rfns__ejd, np.int32(bevz__uawx + 1), hvje__dxx, np.
                array([-1]).ctypes, 0)
            c_bcast(ukhgq__dpkd, np.int32(fqw__ayi), pyf__yvfc, np.array([-
                1]).ctypes, 0)
            c_bcast(null_bitmap_ptr, np.int32(nrqug__nmrl), pyf__yvfc, np.
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
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != MPI_ROOT:
                cts__farf = 0
                ozigx__mgg = np.empty(0, np.uint8).ctypes
            else:
                ozigx__mgg, cts__farf = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            cts__farf = bodo.libs.distributed_api.bcast_scalar(cts__farf)
            if rank != MPI_ROOT:
                pvx__rgvzn = np.empty(cts__farf + 1, np.uint8)
                pvx__rgvzn[cts__farf] = 0
                ozigx__mgg = pvx__rgvzn.ctypes
            c_bcast(ozigx__mgg, np.int32(cts__farf), pyf__yvfc, np.array([-
                1]).ctypes, 0)
            return bodo.libs.str_arr_ext.decode_utf8(ozigx__mgg, cts__farf)
        return impl_str
    typ_val = numba_to_c_type(val)
    fzfr__durq = (
        """def bcast_scalar_impl(val):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({}), np.array([-1]).ctypes, 0)
  return send[0]
"""
        .format(typ_val))
    dtype = numba.np.numpy_support.as_dtype(val)
    fyp__aidfh = {}
    exec(fzfr__durq, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, fyp__aidfh)
    zql__jcv = fyp__aidfh['bcast_scalar_impl']
    return zql__jcv


def bcast_tuple(val):
    return val


@overload(bcast_tuple, no_unliteral=True)
def overload_bcast_tuple(val):
    assert isinstance(val, types.BaseTuple)
    quc__ofad = len(val)
    fzfr__durq = 'def bcast_tuple_impl(val):\n'
    fzfr__durq += '  return ({}{})'.format(','.join('bcast_scalar(val[{}])'
        .format(i) for i in range(quc__ofad)), ',' if quc__ofad else '')
    fyp__aidfh = {}
    exec(fzfr__durq, {'bcast_scalar': bcast_scalar}, fyp__aidfh)
    jhy__lkaoh = fyp__aidfh['bcast_tuple_impl']
    return jhy__lkaoh


def prealloc_str_for_bcast(arr):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr):
    if arr == string_array_type:

        def prealloc_impl(arr):
            rank = bodo.libs.distributed_api.get_rank()
            bevz__uawx = bcast_scalar(len(arr))
            ujzqv__ezdos = bcast_scalar(np.int64(num_total_chars(arr)))
            if rank != MPI_ROOT:
                arr = pre_alloc_string_array(bevz__uawx, ujzqv__ezdos)
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
        ohsrk__kzvd = slice_index.step
        gvp__mzh = 0 if ohsrk__kzvd == 1 or start > arr_start else abs(
            ohsrk__kzvd - arr_start % ohsrk__kzvd) % ohsrk__kzvd
        awu__sbg = max(arr_start, slice_index.start) - arr_start + gvp__mzh
        edchw__tgmyp = max(slice_index.stop - arr_start, 0)
        return slice(awu__sbg, edchw__tgmyp, ohsrk__kzvd)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        awb__zlr = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[awb__zlr])
    return getitem_impl


def slice_getitem_from_start(arr, slice_index):
    return arr[slice_index]


@overload(slice_getitem_from_start, no_unliteral=True)
def slice_getitem_from_start_overload(arr, slice_index):
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def getitem_datetime_date_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            urmp__iwia = slice_index.stop
            A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                urmp__iwia)
            if rank == 0:
                A = arr[:urmp__iwia]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_date_impl
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def getitem_datetime_timedelta_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            urmp__iwia = slice_index.stop
            A = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(urmp__iwia))
            if rank == 0:
                A = arr[:urmp__iwia]
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_datetime_timedelta_impl
    if isinstance(arr.dtype, Decimal128Type):
        precision = arr.dtype.precision
        scale = arr.dtype.scale

        def getitem_decimal_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            urmp__iwia = slice_index.stop
            A = bodo.libs.decimal_arr_ext.alloc_decimal_array(urmp__iwia,
                precision, scale)
            if rank == 0:
                for i in range(urmp__iwia):
                    A._data[i] = arr._data[i]
                    wifiz__hqarl = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, i,
                        wifiz__hqarl)
            bodo.libs.distributed_api.bcast(A)
            return A
        return getitem_decimal_impl
    if arr == string_array_type:

        def getitem_str_impl(arr, slice_index):
            rank = bodo.libs.distributed_api.get_rank()
            urmp__iwia = slice_index.stop
            okfhi__blbww = np.uint64(0)
            if rank == 0:
                out_arr = arr[:urmp__iwia]
                okfhi__blbww = num_total_chars(out_arr)
            okfhi__blbww = bcast_scalar(okfhi__blbww)
            if rank != 0:
                out_arr = pre_alloc_string_array(urmp__iwia, okfhi__blbww)
            bodo.libs.distributed_api.bcast(out_arr)
            return out_arr
        return getitem_str_impl
    jlb__jfr = arr

    def getitem_impl(arr, slice_index):
        rank = bodo.libs.distributed_api.get_rank()
        urmp__iwia = slice_index.stop
        out_arr = bodo.utils.utils.alloc_type(tuple_to_scalar((urmp__iwia,) +
            arr.shape[1:]), jlb__jfr)
        if rank == 0:
            out_arr = arr[:urmp__iwia]
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
        ixzzi__age = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        pyf__yvfc = np.int32(numba_to_c_type(types.uint8))
        mnyi__aer = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            enfu__rrkmx = np.int32(10)
            tag = np.int32(11)
            frai__ydo = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                tzrsq__mumw = arr._data
                zlw__zxezw = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    tzrsq__mumw, ind)
                xorin__nrxom = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    tzrsq__mumw, ind + 1)
                length = xorin__nrxom - zlw__zxezw
                kky__muxeu = tzrsq__mumw[ind]
                frai__ydo[0] = length
                isend(frai__ydo, np.int32(1), root, enfu__rrkmx, True)
                isend(kky__muxeu, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(mnyi__aer,
                ixzzi__age, 0, 1)
            ghg__pljb = 0
            if rank == root:
                ghg__pljb = recv(np.int64, ANY_SOURCE, enfu__rrkmx)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    mnyi__aer, ixzzi__age, ghg__pljb, 1)
                ukhgq__dpkd = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(ukhgq__dpkd, np.int32(ghg__pljb), pyf__yvfc,
                    ANY_SOURCE, tag)
            dummy_use(frai__ydo)
            ghg__pljb = bcast_scalar(ghg__pljb)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    mnyi__aer, ixzzi__age, ghg__pljb, 1)
            ukhgq__dpkd = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(ukhgq__dpkd, np.int32(ghg__pljb), pyf__yvfc, np.array([
                -1]).ctypes, 0)
            val = transform_str_getitem_output(val, ghg__pljb)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        mgpve__lspyq = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, mgpve__lspyq)
            if arr_start <= ind < arr_start + len(arr):
                dmqmo__qhixa = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = dmqmo__qhixa[ind - arr_start]
                send_arr = np.full(1, data, mgpve__lspyq)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = mgpve__lspyq(-1)
            if rank == root:
                val = recv(mgpve__lspyq, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            ytdrw__zfrh = arr.dtype.categories[max(val, 0)]
            return ytdrw__zfrh
        return cat_getitem_impl
    enie__oqcay = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, enie__oqcay)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, enie__oqcay)[0]
        if rank == root:
            val = recv(enie__oqcay, ANY_SOURCE, tag)
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
    yga__wxbw = get_type_enum(out_data)
    assert typ_enum == yga__wxbw
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
    fzfr__durq = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        fzfr__durq += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    fzfr__durq += '  return\n'
    fyp__aidfh = {}
    exec(fzfr__durq, {'alltoallv': alltoallv}, fyp__aidfh)
    etwvu__zcuy = fyp__aidfh['f']
    return etwvu__zcuy


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    start = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return start, count


@numba.njit
def get_start(total_size, pes, rank):
    ehgsm__gmqbh = total_size % pes
    pbca__ulvy = (total_size - ehgsm__gmqbh) // pes
    return rank * pbca__ulvy + min(rank, ehgsm__gmqbh)


@numba.njit
def get_end(total_size, pes, rank):
    ehgsm__gmqbh = total_size % pes
    pbca__ulvy = (total_size - ehgsm__gmqbh) // pes
    return (rank + 1) * pbca__ulvy + min(rank + 1, ehgsm__gmqbh)


@numba.njit
def get_node_portion(total_size, pes, rank):
    ehgsm__gmqbh = total_size % pes
    pbca__ulvy = (total_size - ehgsm__gmqbh) // pes
    if rank < ehgsm__gmqbh:
        return pbca__ulvy + 1
    else:
        return pbca__ulvy


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    ehul__nzjts = in_arr.dtype(0)
    tns__dae = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        bugw__cfgq = ehul__nzjts
        for fcs__ubzr in np.nditer(in_arr):
            bugw__cfgq += fcs__ubzr.item()
        cttg__fsl = dist_exscan(bugw__cfgq, tns__dae)
        for i in range(in_arr.size):
            cttg__fsl += in_arr[i]
            out_arr[i] = cttg__fsl
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    ibmgl__fxfc = in_arr.dtype(1)
    tns__dae = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        bugw__cfgq = ibmgl__fxfc
        for fcs__ubzr in np.nditer(in_arr):
            bugw__cfgq *= fcs__ubzr.item()
        cttg__fsl = dist_exscan(bugw__cfgq, tns__dae)
        if get_rank() == 0:
            cttg__fsl = ibmgl__fxfc
        for i in range(in_arr.size):
            cttg__fsl *= in_arr[i]
            out_arr[i] = cttg__fsl
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ibmgl__fxfc = np.finfo(in_arr.dtype(1).dtype).max
    else:
        ibmgl__fxfc = np.iinfo(in_arr.dtype(1).dtype).max
    tns__dae = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        bugw__cfgq = ibmgl__fxfc
        for fcs__ubzr in np.nditer(in_arr):
            bugw__cfgq = min(bugw__cfgq, fcs__ubzr.item())
        cttg__fsl = dist_exscan(bugw__cfgq, tns__dae)
        if get_rank() == 0:
            cttg__fsl = ibmgl__fxfc
        for i in range(in_arr.size):
            cttg__fsl = min(cttg__fsl, in_arr[i])
            out_arr[i] = cttg__fsl
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ibmgl__fxfc = np.finfo(in_arr.dtype(1).dtype).min
    else:
        ibmgl__fxfc = np.iinfo(in_arr.dtype(1).dtype).min
    ibmgl__fxfc = in_arr.dtype(1)
    tns__dae = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        bugw__cfgq = ibmgl__fxfc
        for fcs__ubzr in np.nditer(in_arr):
            bugw__cfgq = max(bugw__cfgq, fcs__ubzr.item())
        cttg__fsl = dist_exscan(bugw__cfgq, tns__dae)
        if get_rank() == 0:
            cttg__fsl = ibmgl__fxfc
        for i in range(in_arr.size):
            cttg__fsl = max(cttg__fsl, in_arr[i])
            out_arr[i] = cttg__fsl
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    sham__kzpto = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), sham__kzpto)


def dist_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    mlskh__dqrsi = args[0]
    if equiv_set.has_shape(mlskh__dqrsi):
        return ArrayAnalysis.AnalyzeResult(shape=mlskh__dqrsi, pre=[])
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
        wgmob__yiow = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        fzfr__durq = 'def f(req, cond=True):\n'
        fzfr__durq += f'  return {wgmob__yiow}\n'
        fyp__aidfh = {}
        exec(fzfr__durq, {'_wait': _wait}, fyp__aidfh)
        impl = fyp__aidfh['f']
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
    awu__sbg = max(start, chunk_start)
    edchw__tgmyp = min(stop, chunk_start + chunk_count)
    ashl__fihzv = awu__sbg - chunk_start
    jcyku__eihxm = edchw__tgmyp - chunk_start
    if ashl__fihzv < 0 or jcyku__eihxm < 0:
        ashl__fihzv = 1
        jcyku__eihxm = 0
    return ashl__fihzv, jcyku__eihxm


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
        ehgsm__gmqbh = 1
        for a in t:
            ehgsm__gmqbh *= a
        return ehgsm__gmqbh
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    gbta__hfl = np.ascontiguousarray(in_arr)
    jzhrx__fxk = get_tuple_prod(gbta__hfl.shape[1:])
    hdrh__dlfxx = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        alz__isag = np.array(dest_ranks, dtype=np.int32)
    else:
        alz__isag = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, gbta__hfl.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * hdrh__dlfxx, dtype_size * jzhrx__fxk, len
        (alz__isag), alz__isag.ctypes)
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
    lvpce__urasc = np.ascontiguousarray(rhs)
    lsqi__pxopi = get_tuple_prod(lvpce__urasc.shape[1:])
    cli__pir = dtype_size * lsqi__pxopi
    permutation_array_index(lhs.ctypes, lhs_len, cli__pir, lvpce__urasc.
        ctypes, lvpce__urasc.shape[0], p.ctypes, p_len)
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
        fzfr__durq = (
            """def bcast_scalar_impl(data, comm_ranks, nranks):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({}), comm_ranks,ctypes, np.int32({}))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        fyp__aidfh = {}
        exec(fzfr__durq, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, fyp__aidfh)
        zql__jcv = fyp__aidfh['bcast_scalar_impl']
        return zql__jcv
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks: _bcast_np(data, comm_ranks,
            nranks)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ohkhw__vdmv = len(data.columns)
        vnq__hho = ', '.join('g_data_{}'.format(i) for i in range(ohkhw__vdmv))
        doa__rar = bodo.utils.transform.gen_const_tup(data.columns)
        fzfr__durq = 'def impl_df(data, comm_ranks, nranks):\n'
        for i in range(ohkhw__vdmv):
            fzfr__durq += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            fzfr__durq += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks)
"""
                .format(i, i))
        fzfr__durq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fzfr__durq += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks)
"""
        fzfr__durq += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, {})
"""
            .format(vnq__hho, doa__rar))
        fyp__aidfh = {}
        exec(fzfr__durq, {'bodo': bodo}, fyp__aidfh)
        pfvth__icszs = fyp__aidfh['impl_df']
        return pfvth__icszs
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            start = data._start
            stop = data._stop
            ohsrk__kzvd = data._step
            pktdq__viyk = data._name
            pktdq__viyk = bcast_scalar(pktdq__viyk)
            start = bcast_scalar(start)
            stop = bcast_scalar(stop)
            ohsrk__kzvd = bcast_scalar(ohsrk__kzvd)
            anb__awtg = bodo.libs.array_kernels.calc_nitems(start, stop,
                ohsrk__kzvd)
            chunk_start = bodo.libs.distributed_api.get_start(anb__awtg,
                n_pes, rank)
            chunk_count = bodo.libs.distributed_api.get_node_portion(anb__awtg,
                n_pes, rank)
            awu__sbg = start + ohsrk__kzvd * chunk_start
            edchw__tgmyp = start + ohsrk__kzvd * (chunk_start + chunk_count)
            edchw__tgmyp = min(edchw__tgmyp, stop)
            return bodo.hiframes.pd_index_ext.init_range_index(awu__sbg,
                edchw__tgmyp, ohsrk__kzvd, pktdq__viyk)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks):
            ojlz__dsn = data._data
            pktdq__viyk = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(ojlz__dsn,
                comm_ranks, nranks)
            return bodo.utils.conversion.index_from_array(arr, pktdq__viyk)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            pktdq__viyk = bodo.hiframes.pd_series_ext.get_series_name(data)
            vutjg__ofu = bodo.libs.distributed_api.bcast_comm_impl(pktdq__viyk,
                comm_ranks, nranks)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks)
            evykd__dkuf = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                evykd__dkuf, vutjg__ofu)
        return impl_series
    if isinstance(data, types.BaseTuple):
        fzfr__durq = 'def impl_tuple(data, comm_ranks, nranks):\n'
        fzfr__durq += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks)'.format(i) for i in
            range(len(data))), ',' if len(data) > 0 else '')
        fyp__aidfh = {}
        exec(fzfr__durq, {'bcast_comm_impl': bcast_comm_impl}, fyp__aidfh)
        jggly__uuhcv = fyp__aidfh['impl_tuple']
        return jggly__uuhcv
    if data is types.none:
        return lambda data, comm_ranks, nranks: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks):
    typ_val = numba_to_c_type(data.dtype)
    tlqg__jpefy = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    lwj__oneg = (0,) * tlqg__jpefy

    def bcast_arr_impl(data, comm_ranks, nranks):
        rank = bodo.libs.distributed_api.get_rank()
        ojlz__dsn = np.ascontiguousarray(data)
        ukhgq__dpkd = data.ctypes
        dzu__vmg = lwj__oneg
        if rank == MPI_ROOT:
            dzu__vmg = ojlz__dsn.shape
        dzu__vmg = bcast_tuple(dzu__vmg)
        hwex__tck = get_tuple_prod(dzu__vmg[1:])
        send_counts = dzu__vmg[0] * hwex__tck
        eum__vtq = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(ukhgq__dpkd, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks))
            return data
        else:
            c_bcast(eum__vtq.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks))
            return eum__vtq.reshape((-1,) + dzu__vmg[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        zxvv__unyr = MPI.COMM_WORLD
        jdokr__irsp = MPI.Get_processor_name()
        eexb__pkvwm = zxvv__unyr.allgather(jdokr__irsp)
        node_ranks = defaultdict(list)
        for i, wnr__fheho in enumerate(eexb__pkvwm):
            node_ranks[wnr__fheho].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    zxvv__unyr = MPI.COMM_WORLD
    gpg__zls = zxvv__unyr.Get_group()
    hgiwl__dsacm = gpg__zls.Incl(comm_ranks)
    scbt__nilis = zxvv__unyr.Create_group(hgiwl__dsacm)
    return scbt__nilis


def get_nodes_first_ranks():
    prmn__kxh = get_host_ranks()
    return np.array([qvzpp__snk[0] for qvzpp__snk in prmn__kxh.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
