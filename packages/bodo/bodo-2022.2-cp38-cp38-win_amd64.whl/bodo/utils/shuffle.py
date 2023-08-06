"""
helper data structures and functions for shuffle (alltoall).
"""
import os
from collections import namedtuple
import numba
import numpy as np
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, convert_len_arr_to_offset32, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, get_str_arr_item_length, num_total_chars, print_str_arr, set_bit_to, string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.utils.utils import alloc_arr_tup, get_ctypes_ptr, numba_to_c_type
PreShuffleMeta = namedtuple('PreShuffleMeta',
    'send_counts, send_counts_char_tup, send_arr_lens_tup, send_arr_nulls_tup')
ShuffleMeta = namedtuple('ShuffleMeta',
    'send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, send_buff_tup, out_arr_tup, send_counts_char_tup, recv_counts_char_tup, send_arr_lens_tup, send_arr_nulls_tup, send_arr_chars_tup, send_disp_char_tup, recv_disp_char_tup, tmp_offset_char_tup, send_arr_chars_arr_tup'
    )


def alloc_pre_shuffle_metadata(arr, data, n_pes, is_contig):
    return PreShuffleMeta(np.zeros(n_pes, np.int32), ())


@overload(alloc_pre_shuffle_metadata, no_unliteral=True)
def alloc_pre_shuffle_metadata_overload(key_arrs, data, n_pes, is_contig):
    lomxd__vgmc = 'def f(key_arrs, data, n_pes, is_contig):\n'
    lomxd__vgmc += '  send_counts = np.zeros(n_pes, np.int32)\n'
    qawmr__vohrs = len(key_arrs.types)
    degac__jfzw = qawmr__vohrs + len(data.types)
    for i, gpgkc__tkmr in enumerate(key_arrs.types + data.types):
        lomxd__vgmc += '  arr = key_arrs[{}]\n'.format(i
            ) if i < qawmr__vohrs else """  arr = data[{}]
""".format(i -
            qawmr__vohrs)
        if gpgkc__tkmr in [string_array_type, binary_array_type]:
            lomxd__vgmc += (
                '  send_counts_char_{} = np.zeros(n_pes, np.int32)\n'.format(i)
                )
            lomxd__vgmc += ('  send_arr_lens_{} = np.empty(0, np.uint32)\n'
                .format(i))
            lomxd__vgmc += '  if is_contig:\n'
            lomxd__vgmc += (
                '    send_arr_lens_{} = np.empty(len(arr), np.uint32)\n'.
                format(i))
        else:
            lomxd__vgmc += '  send_counts_char_{} = None\n'.format(i)
            lomxd__vgmc += '  send_arr_lens_{} = None\n'.format(i)
        if is_null_masked_type(gpgkc__tkmr):
            lomxd__vgmc += ('  send_arr_nulls_{} = np.empty(0, np.uint8)\n'
                .format(i))
            lomxd__vgmc += '  if is_contig:\n'
            lomxd__vgmc += '    n_bytes = (len(arr) + 7) >> 3\n'
            lomxd__vgmc += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            lomxd__vgmc += '  send_arr_nulls_{} = None\n'.format(i)
    jlt__fssqo = ', '.join('send_counts_char_{}'.format(i) for i in range(
        degac__jfzw))
    cuoa__nbak = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        degac__jfzw))
    genhi__ica = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        degac__jfzw))
    hro__bbt = ',' if degac__jfzw == 1 else ''
    lomxd__vgmc += (
        '  return PreShuffleMeta(send_counts, ({}{}), ({}{}), ({}{}))\n'.
        format(jlt__fssqo, hro__bbt, cuoa__nbak, hro__bbt, genhi__ica,
        hro__bbt))
    fqa__xqop = {}
    exec(lomxd__vgmc, {'np': np, 'PreShuffleMeta': PreShuffleMeta}, fqa__xqop)
    bnpl__lepz = fqa__xqop['f']
    return bnpl__lepz


def update_shuffle_meta(pre_shuffle_meta, node_id, ind, key_arrs, data,
    is_contig=True, padded_bits=0):
    pre_shuffle_meta.send_counts[node_id] += 1


@overload(update_shuffle_meta, no_unliteral=True)
def update_shuffle_meta_overload(pre_shuffle_meta, node_id, ind, key_arrs,
    data, is_contig=True, padded_bits=0):
    pirh__ujkni = 'BODO_DEBUG_LEVEL'
    cpxou__dbi = 0
    try:
        cpxou__dbi = int(os.environ[pirh__ujkni])
    except:
        pass
    lomxd__vgmc = """def f(pre_shuffle_meta, node_id, ind, key_arrs, data, is_contig=True, padded_bits=0):
"""
    lomxd__vgmc += '  pre_shuffle_meta.send_counts[node_id] += 1\n'
    if cpxou__dbi > 0:
        lomxd__vgmc += ('  if pre_shuffle_meta.send_counts[node_id] >= {}:\n'
            .format(bodo.libs.distributed_api.INT_MAX))
        lomxd__vgmc += "    print('large shuffle error')\n"
    qawmr__vohrs = len(key_arrs.types)
    for i, gpgkc__tkmr in enumerate(key_arrs.types + data.types):
        if gpgkc__tkmr in (string_type, string_array_type, bytes_type,
            binary_array_type):
            arr = 'key_arrs[{}]'.format(i
                ) if i < qawmr__vohrs else 'data[{}]'.format(i - qawmr__vohrs)
            lomxd__vgmc += ('  n_chars = get_str_arr_item_length({}, ind)\n'
                .format(arr))
            lomxd__vgmc += (
                '  pre_shuffle_meta.send_counts_char_tup[{}][node_id] += n_chars\n'
                .format(i))
            if cpxou__dbi > 0:
                lomxd__vgmc += (
                    '  if pre_shuffle_meta.send_counts_char_tup[{}][node_id] >= {}:\n'
                    .format(i, bodo.libs.distributed_api.INT_MAX))
                lomxd__vgmc += "    print('large shuffle error')\n"
            lomxd__vgmc += '  if is_contig:\n'
            lomxd__vgmc += (
                '    pre_shuffle_meta.send_arr_lens_tup[{}][ind] = n_chars\n'
                .format(i))
        if is_null_masked_type(gpgkc__tkmr):
            lomxd__vgmc += '  if is_contig:\n'
            lomxd__vgmc += (
                '    out_bitmap = pre_shuffle_meta.send_arr_nulls_tup[{}].ctypes\n'
                .format(i))
            if i < qawmr__vohrs:
                lomxd__vgmc += (
                    '    bit_val = get_mask_bit(key_arrs[{}], ind)\n'.format(i)
                    )
            else:
                lomxd__vgmc += ('    bit_val = get_mask_bit(data[{}], ind)\n'
                    .format(i - qawmr__vohrs))
            lomxd__vgmc += (
                '    set_bit_to(out_bitmap, padded_bits + ind, bit_val)\n')
    fqa__xqop = {}
    exec(lomxd__vgmc, {'set_bit_to': set_bit_to, 'get_bit_bitmap':
        get_bit_bitmap, 'get_null_bitmap_ptr': get_null_bitmap_ptr,
        'getitem_arr_tup': getitem_arr_tup, 'get_mask_bit': get_mask_bit,
        'get_str_arr_item_length': get_str_arr_item_length}, fqa__xqop)
    bjtb__cpqjp = fqa__xqop['f']
    return bjtb__cpqjp


@numba.njit
def calc_disp_nulls(arr):
    ohs__oxj = np.empty_like(arr)
    ohs__oxj[0] = 0
    for i in range(1, len(arr)):
        dogib__fpnf = arr[i - 1] + 7 >> 3
        ohs__oxj[i] = ohs__oxj[i - 1] + dogib__fpnf
    return ohs__oxj


def finalize_shuffle_meta(arrs, data, pre_shuffle_meta, n_pes, is_contig,
    init_vals=()):
    return ShuffleMeta()


@overload(finalize_shuffle_meta, no_unliteral=True)
def finalize_shuffle_meta_overload(key_arrs, data, pre_shuffle_meta, n_pes,
    is_contig, init_vals=()):
    lomxd__vgmc = (
        'def f(key_arrs, data, pre_shuffle_meta, n_pes, is_contig, init_vals=()):\n'
        )
    lomxd__vgmc += '  send_counts = pre_shuffle_meta.send_counts\n'
    lomxd__vgmc += '  recv_counts = np.empty(n_pes, np.int32)\n'
    lomxd__vgmc += '  tmp_offset = np.zeros(n_pes, np.int32)\n'
    lomxd__vgmc += (
        '  bodo.libs.distributed_api.alltoall(send_counts, recv_counts, 1)\n')
    lomxd__vgmc += '  n_out = recv_counts.sum()\n'
    lomxd__vgmc += '  n_send = send_counts.sum()\n'
    lomxd__vgmc += '  send_disp = bodo.ir.join.calc_disp(send_counts)\n'
    lomxd__vgmc += '  recv_disp = bodo.ir.join.calc_disp(recv_counts)\n'
    lomxd__vgmc += '  send_disp_nulls = calc_disp_nulls(send_counts)\n'
    lomxd__vgmc += '  recv_disp_nulls = calc_disp_nulls(recv_counts)\n'
    qawmr__vohrs = len(key_arrs.types)
    degac__jfzw = len(key_arrs.types + data.types)
    for i, gpgkc__tkmr in enumerate(key_arrs.types + data.types):
        lomxd__vgmc += '  arr = key_arrs[{}]\n'.format(i
            ) if i < qawmr__vohrs else """  arr = data[{}]
""".format(i -
            qawmr__vohrs)
        if gpgkc__tkmr in [string_array_type, binary_array_type]:
            if gpgkc__tkmr == string_array_type:
                ciwcj__kfr = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
            else:
                ciwcj__kfr = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
            lomxd__vgmc += '  send_buff_{} = None\n'.format(i)
            lomxd__vgmc += (
                '  send_counts_char_{} = pre_shuffle_meta.send_counts_char_tup[{}]\n'
                .format(i, i))
            lomxd__vgmc += (
                '  recv_counts_char_{} = np.empty(n_pes, np.int32)\n'.format(i)
                )
            lomxd__vgmc += (
                """  bodo.libs.distributed_api.alltoall(send_counts_char_{}, recv_counts_char_{}, 1)
"""
                .format(i, i))
            lomxd__vgmc += ('  n_all_chars = recv_counts_char_{}.sum()\n'.
                format(i))
            lomxd__vgmc += '  out_arr_{} = {}(n_out, n_all_chars)\n'.format(i,
                ciwcj__kfr)
            lomxd__vgmc += (
                '  send_disp_char_{} = bodo.ir.join.calc_disp(send_counts_char_{})\n'
                .format(i, i))
            lomxd__vgmc += (
                '  recv_disp_char_{} = bodo.ir.join.calc_disp(recv_counts_char_{})\n'
                .format(i, i))
            lomxd__vgmc += (
                '  tmp_offset_char_{} = np.zeros(n_pes, np.int32)\n'.format(i))
            lomxd__vgmc += (
                '  send_arr_lens_{} = pre_shuffle_meta.send_arr_lens_tup[{}]\n'
                .format(i, i))
            lomxd__vgmc += ('  send_arr_chars_arr_{} = np.empty(0, np.uint8)\n'
                .format(i))
            lomxd__vgmc += (
                '  send_arr_chars_{} = get_ctypes_ptr(get_data_ptr(arr))\n'
                .format(i))
            lomxd__vgmc += '  if not is_contig:\n'
            lomxd__vgmc += (
                '    send_arr_lens_{} = np.empty(n_send, np.uint32)\n'.
                format(i))
            lomxd__vgmc += ('    s_n_all_chars = send_counts_char_{}.sum()\n'
                .format(i))
            lomxd__vgmc += (
                '    send_arr_chars_arr_{} = np.empty(s_n_all_chars, np.uint8)\n'
                .format(i))
            lomxd__vgmc += (
                '    send_arr_chars_{} = get_ctypes_ptr(send_arr_chars_arr_{}.ctypes)\n'
                .format(i, i))
        else:
            assert isinstance(gpgkc__tkmr, (types.Array, IntegerArrayType,
                BooleanArrayType, bodo.CategoricalArrayType))
            lomxd__vgmc += (
                '  out_arr_{} = bodo.utils.utils.alloc_type(n_out, arr)\n'.
                format(i))
            lomxd__vgmc += '  send_buff_{} = arr\n'.format(i)
            lomxd__vgmc += '  if not is_contig:\n'
            if i >= qawmr__vohrs and init_vals != ():
                lomxd__vgmc += (
                    """    send_buff_{} = bodo.utils.utils.full_type(n_send, init_vals[{}], arr)
"""
                    .format(i, i - qawmr__vohrs))
            else:
                lomxd__vgmc += (
                    '    send_buff_{} = bodo.utils.utils.alloc_type(n_send, arr)\n'
                    .format(i))
            lomxd__vgmc += '  send_counts_char_{} = None\n'.format(i)
            lomxd__vgmc += '  recv_counts_char_{} = None\n'.format(i)
            lomxd__vgmc += '  send_arr_lens_{} = None\n'.format(i)
            lomxd__vgmc += '  send_arr_chars_{} = None\n'.format(i)
            lomxd__vgmc += '  send_disp_char_{} = None\n'.format(i)
            lomxd__vgmc += '  recv_disp_char_{} = None\n'.format(i)
            lomxd__vgmc += '  tmp_offset_char_{} = None\n'.format(i)
            lomxd__vgmc += '  send_arr_chars_arr_{} = None\n'.format(i)
        if is_null_masked_type(gpgkc__tkmr):
            lomxd__vgmc += (
                '  send_arr_nulls_{} = pre_shuffle_meta.send_arr_nulls_tup[{}]\n'
                .format(i, i))
            lomxd__vgmc += '  if not is_contig:\n'
            lomxd__vgmc += '    n_bytes = (n_send + 7) >> 3\n'
            lomxd__vgmc += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            lomxd__vgmc += '  send_arr_nulls_{} = None\n'.format(i)
    kxm__yytz = ', '.join('send_buff_{}'.format(i) for i in range(degac__jfzw))
    dcy__dcya = ', '.join('out_arr_{}'.format(i) for i in range(degac__jfzw))
    wqj__resbl = ',' if degac__jfzw == 1 else ''
    jwwka__mxr = ', '.join('send_counts_char_{}'.format(i) for i in range(
        degac__jfzw))
    duxhc__xbtk = ', '.join('recv_counts_char_{}'.format(i) for i in range(
        degac__jfzw))
    prj__wnndm = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        degac__jfzw))
    eph__csx = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        degac__jfzw))
    vltaj__den = ', '.join('send_arr_chars_{}'.format(i) for i in range(
        degac__jfzw))
    gcznu__zjnsu = ', '.join('send_disp_char_{}'.format(i) for i in range(
        degac__jfzw))
    qbbfu__lunsp = ', '.join('recv_disp_char_{}'.format(i) for i in range(
        degac__jfzw))
    shxoh__oas = ', '.join('tmp_offset_char_{}'.format(i) for i in range(
        degac__jfzw))
    zsw__yfux = ', '.join('send_arr_chars_arr_{}'.format(i) for i in range(
        degac__jfzw))
    lomxd__vgmc += (
        """  return ShuffleMeta(send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), )
"""
        .format(kxm__yytz, wqj__resbl, dcy__dcya, wqj__resbl, jwwka__mxr,
        wqj__resbl, duxhc__xbtk, wqj__resbl, prj__wnndm, wqj__resbl,
        eph__csx, wqj__resbl, vltaj__den, wqj__resbl, gcznu__zjnsu,
        wqj__resbl, qbbfu__lunsp, wqj__resbl, shxoh__oas, wqj__resbl,
        zsw__yfux, wqj__resbl))
    fqa__xqop = {}
    exec(lomxd__vgmc, {'np': np, 'bodo': bodo, 'num_total_chars':
        num_total_chars, 'get_data_ptr': get_data_ptr, 'ShuffleMeta':
        ShuffleMeta, 'get_ctypes_ptr': get_ctypes_ptr, 'calc_disp_nulls':
        calc_disp_nulls}, fqa__xqop)
    wkdcl__wltz = fqa__xqop['f']
    return wkdcl__wltz


def alltoallv_tup(arrs, shuffle_meta, key_arrs):
    return arrs


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(arrs, meta, key_arrs):
    qawmr__vohrs = len(key_arrs.types)
    lomxd__vgmc = 'def f(arrs, meta, key_arrs):\n'
    if any(is_null_masked_type(t) for t in arrs.types):
        lomxd__vgmc += (
            '  send_counts_nulls = np.empty(len(meta.send_counts), np.int32)\n'
            )
        lomxd__vgmc += '  for i in range(len(meta.send_counts)):\n'
        lomxd__vgmc += (
            '    send_counts_nulls[i] = (meta.send_counts[i] + 7) >> 3\n')
        lomxd__vgmc += (
            '  recv_counts_nulls = np.empty(len(meta.recv_counts), np.int32)\n'
            )
        lomxd__vgmc += '  for i in range(len(meta.recv_counts)):\n'
        lomxd__vgmc += (
            '    recv_counts_nulls[i] = (meta.recv_counts[i] + 7) >> 3\n')
        lomxd__vgmc += (
            '  tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)\n')
    lomxd__vgmc += '  lens = np.empty(meta.n_out, np.uint32)\n'
    for i, gpgkc__tkmr in enumerate(arrs.types):
        if isinstance(gpgkc__tkmr, (types.Array, IntegerArrayType,
            BooleanArrayType, bodo.CategoricalArrayType)):
            lomxd__vgmc += (
                """  bodo.libs.distributed_api.alltoallv(meta.send_buff_tup[{}], meta.out_arr_tup[{}], meta.send_counts,meta.recv_counts, meta.send_disp, meta.recv_disp)
"""
                .format(i, i))
        else:
            assert gpgkc__tkmr in [string_array_type, binary_array_type]
            lomxd__vgmc += (
                '  offset_ptr_{} = get_offset_ptr(meta.out_arr_tup[{}])\n'.
                format(i, i))
            if offset_type.bitwidth == 32:
                lomxd__vgmc += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, offset_ptr_{}, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i, i))
            else:
                lomxd__vgmc += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, lens.ctypes, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i))
            lomxd__vgmc += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_chars_tup[{}], get_data_ptr(meta.out_arr_tup[{}]), meta.send_counts_char_tup[{}].ctypes,meta.recv_counts_char_tup[{}].ctypes, meta.send_disp_char_tup[{}].ctypes,meta.recv_disp_char_tup[{}].ctypes, char_typ_enum)
"""
                .format(i, i, i, i, i, i))
            if offset_type.bitwidth == 32:
                lomxd__vgmc += (
                    '  convert_len_arr_to_offset32(offset_ptr_{}, meta.n_out)\n'
                    .format(i))
            else:
                lomxd__vgmc += (
                    """  convert_len_arr_to_offset(lens.ctypes, offset_ptr_{}, meta.n_out)
"""
                    .format(i))
        if is_null_masked_type(gpgkc__tkmr):
            lomxd__vgmc += (
                '  null_bitmap_ptr_{} = get_arr_null_ptr(meta.out_arr_tup[{}])\n'
                .format(i, i))
            lomxd__vgmc += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_nulls_tup[{}].ctypes, tmp_null_bytes.ctypes, send_counts_nulls.ctypes, recv_counts_nulls.ctypes, meta.send_disp_nulls.ctypes, meta.recv_disp_nulls.ctypes, char_typ_enum)
"""
                .format(i))
            lomxd__vgmc += (
                """  copy_gathered_null_bytes(null_bitmap_ptr_{}, tmp_null_bytes, recv_counts_nulls, meta.recv_counts)
"""
                .format(i))
    lomxd__vgmc += '  return ({}{})\n'.format(','.join([
        'meta.out_arr_tup[{}]'.format(i) for i in range(arrs.count)]), ',' if
        arrs.count == 1 else '')
    prrn__rms = np.int32(numba_to_c_type(types.int32))
    bvwsm__gxzcv = np.int32(numba_to_c_type(types.uint8))
    fqa__xqop = {}
    exec(lomxd__vgmc, {'np': np, 'bodo': bodo, 'get_offset_ptr':
        get_offset_ptr, 'get_data_ptr': get_data_ptr, 'int32_typ_enum':
        prrn__rms, 'char_typ_enum': bvwsm__gxzcv,
        'convert_len_arr_to_offset': convert_len_arr_to_offset,
        'convert_len_arr_to_offset32': convert_len_arr_to_offset32,
        'copy_gathered_null_bytes': bodo.libs.distributed_api.
        copy_gathered_null_bytes, 'get_arr_null_ptr': get_arr_null_ptr,
        'print_str_arr': print_str_arr}, fqa__xqop)
    qett__jwkqv = fqa__xqop['f']
    return qett__jwkqv


def shuffle_with_index_impl(key_arrs, node_arr, data):
    n_pes = bodo.libs.distributed_api.get_size()
    pre_shuffle_meta = alloc_pre_shuffle_metadata(key_arrs, data, n_pes, False)
    zaalu__kqa = len(key_arrs[0])
    orig_indices = np.arange(zaalu__kqa)
    jgn__ubcvy = np.empty(zaalu__kqa, np.int32)
    for i in range(zaalu__kqa):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = node_arr[i]
        jgn__ubcvy[i] = node_id
        update_shuffle_meta(pre_shuffle_meta, node_id, i, key_arrs, data, False
            )
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, pre_shuffle_meta,
        n_pes, False)
    for i in range(zaalu__kqa):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = jgn__ubcvy[i]
        unb__qvwaz = bodo.ir.join.write_send_buff(shuffle_meta, node_id, i,
            key_arrs, data)
        orig_indices[unb__qvwaz] = i
        shuffle_meta.tmp_offset[node_id] += 1
    recvs = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    crqc__sgchp = _get_keys_tup(recvs, key_arrs)
    hgjzi__feq = _get_data_tup(recvs, key_arrs)
    return crqc__sgchp, hgjzi__feq, orig_indices, shuffle_meta


@generated_jit(nopython=True, cache=True)
def shuffle_with_index(key_arrs, node_arr, data):
    return shuffle_with_index_impl


@numba.njit(cache=True)
def reverse_shuffle(data, orig_indices, shuffle_meta):
    dcy__dcya = alloc_arr_tup(shuffle_meta.n_send, data)
    sdef__fkz = ShuffleMeta(shuffle_meta.recv_counts, shuffle_meta.
        send_counts, shuffle_meta.n_out, shuffle_meta.n_send, shuffle_meta.
        recv_disp, shuffle_meta.send_disp, shuffle_meta.recv_disp_nulls,
        shuffle_meta.send_disp_nulls, shuffle_meta.tmp_offset, data,
        dcy__dcya, shuffle_meta.recv_counts_char_tup, shuffle_meta.
        send_counts_char_tup, shuffle_meta.send_arr_lens_tup, shuffle_meta.
        send_arr_nulls_tup, shuffle_meta.send_arr_chars_tup, shuffle_meta.
        recv_disp_char_tup, shuffle_meta.send_disp_char_tup, shuffle_meta.
        tmp_offset_char_tup, shuffle_meta.send_arr_chars_arr_tup)
    dcy__dcya = alltoallv_tup(data, sdef__fkz, ())
    rbr__iqdp = alloc_arr_tup(shuffle_meta.n_send, data)
    for i in range(len(orig_indices)):
        setitem_arr_tup(rbr__iqdp, orig_indices[i], getitem_arr_tup(
            dcy__dcya, i))
    return rbr__iqdp


def _get_keys_tup(recvs, key_arrs):
    return recvs[:len(key_arrs)]


@overload(_get_keys_tup, no_unliteral=True)
def _get_keys_tup_overload(recvs, key_arrs):
    qawmr__vohrs = len(key_arrs.types)
    lomxd__vgmc = 'def f(recvs, key_arrs):\n'
    ydfz__gtug = ','.join('recvs[{}]'.format(i) for i in range(qawmr__vohrs))
    lomxd__vgmc += '  return ({}{})\n'.format(ydfz__gtug, ',' if 
        qawmr__vohrs == 1 else '')
    fqa__xqop = {}
    exec(lomxd__vgmc, {}, fqa__xqop)
    ocyc__blqj = fqa__xqop['f']
    return ocyc__blqj


def _get_data_tup(recvs, key_arrs):
    return recvs[len(key_arrs):]


@overload(_get_data_tup, no_unliteral=True)
def _get_data_tup_overload(recvs, key_arrs):
    qawmr__vohrs = len(key_arrs.types)
    degac__jfzw = len(recvs.types)
    qjbw__zxqkm = degac__jfzw - qawmr__vohrs
    lomxd__vgmc = 'def f(recvs, key_arrs):\n'
    ydfz__gtug = ','.join('recvs[{}]'.format(i) for i in range(qawmr__vohrs,
        degac__jfzw))
    lomxd__vgmc += '  return ({}{})\n'.format(ydfz__gtug, ',' if 
        qjbw__zxqkm == 1 else '')
    fqa__xqop = {}
    exec(lomxd__vgmc, {}, fqa__xqop)
    ocyc__blqj = fqa__xqop['f']
    return ocyc__blqj


def getitem_arr_tup_single(arrs, i):
    return arrs[0][i]


@overload(getitem_arr_tup_single, no_unliteral=True)
def getitem_arr_tup_single_overload(arrs, i):
    if len(arrs.types) == 1:
        return lambda arrs, i: arrs[0][i]
    return lambda arrs, i: getitem_arr_tup(arrs, i)


def val_to_tup(val):
    return val,


@overload(val_to_tup, no_unliteral=True)
def val_to_tup_overload(val):
    if isinstance(val, types.BaseTuple):
        return lambda val: val
    return lambda val: (val,)


def is_null_masked_type(t):
    return t in (string_type, string_array_type, bytes_type,
        binary_array_type, boolean_array) or isinstance(t, IntegerArrayType)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_mask_bit(arr, i):
    if arr in [string_array_type, binary_array_type]:
        return lambda arr, i: get_bit_bitmap(get_null_bitmap_ptr(arr), i)
    assert isinstance(arr, IntegerArrayType) or arr == boolean_array
    return lambda arr, i: bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
        _null_bitmap, i)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_arr_null_ptr(arr):
    if arr in [string_array_type, binary_array_type]:
        return lambda arr: get_null_bitmap_ptr(arr)
    assert isinstance(arr, IntegerArrayType) or arr == boolean_array
    return lambda arr: arr._null_bitmap.ctypes
