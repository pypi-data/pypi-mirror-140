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
    xtgr__phe = 'def f(key_arrs, data, n_pes, is_contig):\n'
    xtgr__phe += '  send_counts = np.zeros(n_pes, np.int32)\n'
    foxvb__dlb = len(key_arrs.types)
    hdsrc__zev = foxvb__dlb + len(data.types)
    for i, udwbg__ppho in enumerate(key_arrs.types + data.types):
        xtgr__phe += '  arr = key_arrs[{}]\n'.format(i
            ) if i < foxvb__dlb else """  arr = data[{}]
""".format(i -
            foxvb__dlb)
        if udwbg__ppho in [string_array_type, binary_array_type]:
            xtgr__phe += ('  send_counts_char_{} = np.zeros(n_pes, np.int32)\n'
                .format(i))
            xtgr__phe += ('  send_arr_lens_{} = np.empty(0, np.uint32)\n'.
                format(i))
            xtgr__phe += '  if is_contig:\n'
            xtgr__phe += (
                '    send_arr_lens_{} = np.empty(len(arr), np.uint32)\n'.
                format(i))
        else:
            xtgr__phe += '  send_counts_char_{} = None\n'.format(i)
            xtgr__phe += '  send_arr_lens_{} = None\n'.format(i)
        if is_null_masked_type(udwbg__ppho):
            xtgr__phe += ('  send_arr_nulls_{} = np.empty(0, np.uint8)\n'.
                format(i))
            xtgr__phe += '  if is_contig:\n'
            xtgr__phe += '    n_bytes = (len(arr) + 7) >> 3\n'
            xtgr__phe += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            xtgr__phe += '  send_arr_nulls_{} = None\n'.format(i)
    tgwm__nef = ', '.join('send_counts_char_{}'.format(i) for i in range(
        hdsrc__zev))
    sajg__pzxba = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        hdsrc__zev))
    vjso__ojug = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        hdsrc__zev))
    lczji__boo = ',' if hdsrc__zev == 1 else ''
    xtgr__phe += (
        '  return PreShuffleMeta(send_counts, ({}{}), ({}{}), ({}{}))\n'.
        format(tgwm__nef, lczji__boo, sajg__pzxba, lczji__boo, vjso__ojug,
        lczji__boo))
    bzniv__tft = {}
    exec(xtgr__phe, {'np': np, 'PreShuffleMeta': PreShuffleMeta}, bzniv__tft)
    cuw__ppcl = bzniv__tft['f']
    return cuw__ppcl


def update_shuffle_meta(pre_shuffle_meta, node_id, ind, key_arrs, data,
    is_contig=True, padded_bits=0):
    pre_shuffle_meta.send_counts[node_id] += 1


@overload(update_shuffle_meta, no_unliteral=True)
def update_shuffle_meta_overload(pre_shuffle_meta, node_id, ind, key_arrs,
    data, is_contig=True, padded_bits=0):
    sbtc__axu = 'BODO_DEBUG_LEVEL'
    pkqom__uop = 0
    try:
        pkqom__uop = int(os.environ[sbtc__axu])
    except:
        pass
    xtgr__phe = """def f(pre_shuffle_meta, node_id, ind, key_arrs, data, is_contig=True, padded_bits=0):
"""
    xtgr__phe += '  pre_shuffle_meta.send_counts[node_id] += 1\n'
    if pkqom__uop > 0:
        xtgr__phe += ('  if pre_shuffle_meta.send_counts[node_id] >= {}:\n'
            .format(bodo.libs.distributed_api.INT_MAX))
        xtgr__phe += "    print('large shuffle error')\n"
    foxvb__dlb = len(key_arrs.types)
    for i, udwbg__ppho in enumerate(key_arrs.types + data.types):
        if udwbg__ppho in (string_type, string_array_type, bytes_type,
            binary_array_type):
            arr = 'key_arrs[{}]'.format(i
                ) if i < foxvb__dlb else 'data[{}]'.format(i - foxvb__dlb)
            xtgr__phe += ('  n_chars = get_str_arr_item_length({}, ind)\n'.
                format(arr))
            xtgr__phe += (
                '  pre_shuffle_meta.send_counts_char_tup[{}][node_id] += n_chars\n'
                .format(i))
            if pkqom__uop > 0:
                xtgr__phe += (
                    '  if pre_shuffle_meta.send_counts_char_tup[{}][node_id] >= {}:\n'
                    .format(i, bodo.libs.distributed_api.INT_MAX))
                xtgr__phe += "    print('large shuffle error')\n"
            xtgr__phe += '  if is_contig:\n'
            xtgr__phe += (
                '    pre_shuffle_meta.send_arr_lens_tup[{}][ind] = n_chars\n'
                .format(i))
        if is_null_masked_type(udwbg__ppho):
            xtgr__phe += '  if is_contig:\n'
            xtgr__phe += (
                '    out_bitmap = pre_shuffle_meta.send_arr_nulls_tup[{}].ctypes\n'
                .format(i))
            if i < foxvb__dlb:
                xtgr__phe += ('    bit_val = get_mask_bit(key_arrs[{}], ind)\n'
                    .format(i))
            else:
                xtgr__phe += ('    bit_val = get_mask_bit(data[{}], ind)\n'
                    .format(i - foxvb__dlb))
            xtgr__phe += (
                '    set_bit_to(out_bitmap, padded_bits + ind, bit_val)\n')
    bzniv__tft = {}
    exec(xtgr__phe, {'set_bit_to': set_bit_to, 'get_bit_bitmap':
        get_bit_bitmap, 'get_null_bitmap_ptr': get_null_bitmap_ptr,
        'getitem_arr_tup': getitem_arr_tup, 'get_mask_bit': get_mask_bit,
        'get_str_arr_item_length': get_str_arr_item_length}, bzniv__tft)
    xsp__rlw = bzniv__tft['f']
    return xsp__rlw


@numba.njit
def calc_disp_nulls(arr):
    iib__mmhc = np.empty_like(arr)
    iib__mmhc[0] = 0
    for i in range(1, len(arr)):
        xbpqj__dysp = arr[i - 1] + 7 >> 3
        iib__mmhc[i] = iib__mmhc[i - 1] + xbpqj__dysp
    return iib__mmhc


def finalize_shuffle_meta(arrs, data, pre_shuffle_meta, n_pes, is_contig,
    init_vals=()):
    return ShuffleMeta()


@overload(finalize_shuffle_meta, no_unliteral=True)
def finalize_shuffle_meta_overload(key_arrs, data, pre_shuffle_meta, n_pes,
    is_contig, init_vals=()):
    xtgr__phe = (
        'def f(key_arrs, data, pre_shuffle_meta, n_pes, is_contig, init_vals=()):\n'
        )
    xtgr__phe += '  send_counts = pre_shuffle_meta.send_counts\n'
    xtgr__phe += '  recv_counts = np.empty(n_pes, np.int32)\n'
    xtgr__phe += '  tmp_offset = np.zeros(n_pes, np.int32)\n'
    xtgr__phe += (
        '  bodo.libs.distributed_api.alltoall(send_counts, recv_counts, 1)\n')
    xtgr__phe += '  n_out = recv_counts.sum()\n'
    xtgr__phe += '  n_send = send_counts.sum()\n'
    xtgr__phe += '  send_disp = bodo.ir.join.calc_disp(send_counts)\n'
    xtgr__phe += '  recv_disp = bodo.ir.join.calc_disp(recv_counts)\n'
    xtgr__phe += '  send_disp_nulls = calc_disp_nulls(send_counts)\n'
    xtgr__phe += '  recv_disp_nulls = calc_disp_nulls(recv_counts)\n'
    foxvb__dlb = len(key_arrs.types)
    hdsrc__zev = len(key_arrs.types + data.types)
    for i, udwbg__ppho in enumerate(key_arrs.types + data.types):
        xtgr__phe += '  arr = key_arrs[{}]\n'.format(i
            ) if i < foxvb__dlb else """  arr = data[{}]
""".format(i -
            foxvb__dlb)
        if udwbg__ppho in [string_array_type, binary_array_type]:
            if udwbg__ppho == string_array_type:
                yhle__tuwz = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
            else:
                yhle__tuwz = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
            xtgr__phe += '  send_buff_{} = None\n'.format(i)
            xtgr__phe += (
                '  send_counts_char_{} = pre_shuffle_meta.send_counts_char_tup[{}]\n'
                .format(i, i))
            xtgr__phe += ('  recv_counts_char_{} = np.empty(n_pes, np.int32)\n'
                .format(i))
            xtgr__phe += (
                """  bodo.libs.distributed_api.alltoall(send_counts_char_{}, recv_counts_char_{}, 1)
"""
                .format(i, i))
            xtgr__phe += '  n_all_chars = recv_counts_char_{}.sum()\n'.format(i
                )
            xtgr__phe += '  out_arr_{} = {}(n_out, n_all_chars)\n'.format(i,
                yhle__tuwz)
            xtgr__phe += (
                '  send_disp_char_{} = bodo.ir.join.calc_disp(send_counts_char_{})\n'
                .format(i, i))
            xtgr__phe += (
                '  recv_disp_char_{} = bodo.ir.join.calc_disp(recv_counts_char_{})\n'
                .format(i, i))
            xtgr__phe += ('  tmp_offset_char_{} = np.zeros(n_pes, np.int32)\n'
                .format(i))
            xtgr__phe += (
                '  send_arr_lens_{} = pre_shuffle_meta.send_arr_lens_tup[{}]\n'
                .format(i, i))
            xtgr__phe += ('  send_arr_chars_arr_{} = np.empty(0, np.uint8)\n'
                .format(i))
            xtgr__phe += (
                '  send_arr_chars_{} = get_ctypes_ptr(get_data_ptr(arr))\n'
                .format(i))
            xtgr__phe += '  if not is_contig:\n'
            xtgr__phe += (
                '    send_arr_lens_{} = np.empty(n_send, np.uint32)\n'.
                format(i))
            xtgr__phe += ('    s_n_all_chars = send_counts_char_{}.sum()\n'
                .format(i))
            xtgr__phe += (
                '    send_arr_chars_arr_{} = np.empty(s_n_all_chars, np.uint8)\n'
                .format(i))
            xtgr__phe += (
                '    send_arr_chars_{} = get_ctypes_ptr(send_arr_chars_arr_{}.ctypes)\n'
                .format(i, i))
        else:
            assert isinstance(udwbg__ppho, (types.Array, IntegerArrayType,
                BooleanArrayType, bodo.CategoricalArrayType))
            xtgr__phe += (
                '  out_arr_{} = bodo.utils.utils.alloc_type(n_out, arr)\n'.
                format(i))
            xtgr__phe += '  send_buff_{} = arr\n'.format(i)
            xtgr__phe += '  if not is_contig:\n'
            if i >= foxvb__dlb and init_vals != ():
                xtgr__phe += (
                    """    send_buff_{} = bodo.utils.utils.full_type(n_send, init_vals[{}], arr)
"""
                    .format(i, i - foxvb__dlb))
            else:
                xtgr__phe += (
                    '    send_buff_{} = bodo.utils.utils.alloc_type(n_send, arr)\n'
                    .format(i))
            xtgr__phe += '  send_counts_char_{} = None\n'.format(i)
            xtgr__phe += '  recv_counts_char_{} = None\n'.format(i)
            xtgr__phe += '  send_arr_lens_{} = None\n'.format(i)
            xtgr__phe += '  send_arr_chars_{} = None\n'.format(i)
            xtgr__phe += '  send_disp_char_{} = None\n'.format(i)
            xtgr__phe += '  recv_disp_char_{} = None\n'.format(i)
            xtgr__phe += '  tmp_offset_char_{} = None\n'.format(i)
            xtgr__phe += '  send_arr_chars_arr_{} = None\n'.format(i)
        if is_null_masked_type(udwbg__ppho):
            xtgr__phe += (
                '  send_arr_nulls_{} = pre_shuffle_meta.send_arr_nulls_tup[{}]\n'
                .format(i, i))
            xtgr__phe += '  if not is_contig:\n'
            xtgr__phe += '    n_bytes = (n_send + 7) >> 3\n'
            xtgr__phe += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            xtgr__phe += '  send_arr_nulls_{} = None\n'.format(i)
    priyj__hvb = ', '.join('send_buff_{}'.format(i) for i in range(hdsrc__zev))
    jhvdh__azj = ', '.join('out_arr_{}'.format(i) for i in range(hdsrc__zev))
    vtov__jtk = ',' if hdsrc__zev == 1 else ''
    nrv__dsse = ', '.join('send_counts_char_{}'.format(i) for i in range(
        hdsrc__zev))
    ojbhf__lzb = ', '.join('recv_counts_char_{}'.format(i) for i in range(
        hdsrc__zev))
    wqk__ipbz = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        hdsrc__zev))
    nnssx__scyj = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        hdsrc__zev))
    lgrw__buotq = ', '.join('send_arr_chars_{}'.format(i) for i in range(
        hdsrc__zev))
    ntee__tuzg = ', '.join('send_disp_char_{}'.format(i) for i in range(
        hdsrc__zev))
    ifep__qiaj = ', '.join('recv_disp_char_{}'.format(i) for i in range(
        hdsrc__zev))
    mmj__tet = ', '.join('tmp_offset_char_{}'.format(i) for i in range(
        hdsrc__zev))
    ypj__gor = ', '.join('send_arr_chars_arr_{}'.format(i) for i in range(
        hdsrc__zev))
    xtgr__phe += (
        """  return ShuffleMeta(send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), )
"""
        .format(priyj__hvb, vtov__jtk, jhvdh__azj, vtov__jtk, nrv__dsse,
        vtov__jtk, ojbhf__lzb, vtov__jtk, wqk__ipbz, vtov__jtk, nnssx__scyj,
        vtov__jtk, lgrw__buotq, vtov__jtk, ntee__tuzg, vtov__jtk,
        ifep__qiaj, vtov__jtk, mmj__tet, vtov__jtk, ypj__gor, vtov__jtk))
    bzniv__tft = {}
    exec(xtgr__phe, {'np': np, 'bodo': bodo, 'num_total_chars':
        num_total_chars, 'get_data_ptr': get_data_ptr, 'ShuffleMeta':
        ShuffleMeta, 'get_ctypes_ptr': get_ctypes_ptr, 'calc_disp_nulls':
        calc_disp_nulls}, bzniv__tft)
    owxmf__cnsbi = bzniv__tft['f']
    return owxmf__cnsbi


def alltoallv_tup(arrs, shuffle_meta, key_arrs):
    return arrs


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(arrs, meta, key_arrs):
    foxvb__dlb = len(key_arrs.types)
    xtgr__phe = 'def f(arrs, meta, key_arrs):\n'
    if any(is_null_masked_type(t) for t in arrs.types):
        xtgr__phe += (
            '  send_counts_nulls = np.empty(len(meta.send_counts), np.int32)\n'
            )
        xtgr__phe += '  for i in range(len(meta.send_counts)):\n'
        xtgr__phe += (
            '    send_counts_nulls[i] = (meta.send_counts[i] + 7) >> 3\n')
        xtgr__phe += (
            '  recv_counts_nulls = np.empty(len(meta.recv_counts), np.int32)\n'
            )
        xtgr__phe += '  for i in range(len(meta.recv_counts)):\n'
        xtgr__phe += (
            '    recv_counts_nulls[i] = (meta.recv_counts[i] + 7) >> 3\n')
        xtgr__phe += (
            '  tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)\n')
    xtgr__phe += '  lens = np.empty(meta.n_out, np.uint32)\n'
    for i, udwbg__ppho in enumerate(arrs.types):
        if isinstance(udwbg__ppho, (types.Array, IntegerArrayType,
            BooleanArrayType, bodo.CategoricalArrayType)):
            xtgr__phe += (
                """  bodo.libs.distributed_api.alltoallv(meta.send_buff_tup[{}], meta.out_arr_tup[{}], meta.send_counts,meta.recv_counts, meta.send_disp, meta.recv_disp)
"""
                .format(i, i))
        else:
            assert udwbg__ppho in [string_array_type, binary_array_type]
            xtgr__phe += (
                '  offset_ptr_{} = get_offset_ptr(meta.out_arr_tup[{}])\n'.
                format(i, i))
            if offset_type.bitwidth == 32:
                xtgr__phe += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, offset_ptr_{}, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i, i))
            else:
                xtgr__phe += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, lens.ctypes, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i))
            xtgr__phe += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_chars_tup[{}], get_data_ptr(meta.out_arr_tup[{}]), meta.send_counts_char_tup[{}].ctypes,meta.recv_counts_char_tup[{}].ctypes, meta.send_disp_char_tup[{}].ctypes,meta.recv_disp_char_tup[{}].ctypes, char_typ_enum)
"""
                .format(i, i, i, i, i, i))
            if offset_type.bitwidth == 32:
                xtgr__phe += (
                    '  convert_len_arr_to_offset32(offset_ptr_{}, meta.n_out)\n'
                    .format(i))
            else:
                xtgr__phe += (
                    """  convert_len_arr_to_offset(lens.ctypes, offset_ptr_{}, meta.n_out)
"""
                    .format(i))
        if is_null_masked_type(udwbg__ppho):
            xtgr__phe += (
                '  null_bitmap_ptr_{} = get_arr_null_ptr(meta.out_arr_tup[{}])\n'
                .format(i, i))
            xtgr__phe += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_nulls_tup[{}].ctypes, tmp_null_bytes.ctypes, send_counts_nulls.ctypes, recv_counts_nulls.ctypes, meta.send_disp_nulls.ctypes, meta.recv_disp_nulls.ctypes, char_typ_enum)
"""
                .format(i))
            xtgr__phe += (
                """  copy_gathered_null_bytes(null_bitmap_ptr_{}, tmp_null_bytes, recv_counts_nulls, meta.recv_counts)
"""
                .format(i))
    xtgr__phe += '  return ({}{})\n'.format(','.join([
        'meta.out_arr_tup[{}]'.format(i) for i in range(arrs.count)]), ',' if
        arrs.count == 1 else '')
    gids__bfd = np.int32(numba_to_c_type(types.int32))
    dlm__mie = np.int32(numba_to_c_type(types.uint8))
    bzniv__tft = {}
    exec(xtgr__phe, {'np': np, 'bodo': bodo, 'get_offset_ptr':
        get_offset_ptr, 'get_data_ptr': get_data_ptr, 'int32_typ_enum':
        gids__bfd, 'char_typ_enum': dlm__mie, 'convert_len_arr_to_offset':
        convert_len_arr_to_offset, 'convert_len_arr_to_offset32':
        convert_len_arr_to_offset32, 'copy_gathered_null_bytes': bodo.libs.
        distributed_api.copy_gathered_null_bytes, 'get_arr_null_ptr':
        get_arr_null_ptr, 'print_str_arr': print_str_arr}, bzniv__tft)
    zmdpz__fjx = bzniv__tft['f']
    return zmdpz__fjx


def shuffle_with_index_impl(key_arrs, node_arr, data):
    n_pes = bodo.libs.distributed_api.get_size()
    pre_shuffle_meta = alloc_pre_shuffle_metadata(key_arrs, data, n_pes, False)
    dyd__jqmb = len(key_arrs[0])
    orig_indices = np.arange(dyd__jqmb)
    sldkp__wnifq = np.empty(dyd__jqmb, np.int32)
    for i in range(dyd__jqmb):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = node_arr[i]
        sldkp__wnifq[i] = node_id
        update_shuffle_meta(pre_shuffle_meta, node_id, i, key_arrs, data, False
            )
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, pre_shuffle_meta,
        n_pes, False)
    for i in range(dyd__jqmb):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = sldkp__wnifq[i]
        sgtt__fvztd = bodo.ir.join.write_send_buff(shuffle_meta, node_id, i,
            key_arrs, data)
        orig_indices[sgtt__fvztd] = i
        shuffle_meta.tmp_offset[node_id] += 1
    recvs = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    hlj__kdey = _get_keys_tup(recvs, key_arrs)
    jjshw__vdq = _get_data_tup(recvs, key_arrs)
    return hlj__kdey, jjshw__vdq, orig_indices, shuffle_meta


@generated_jit(nopython=True, cache=True)
def shuffle_with_index(key_arrs, node_arr, data):
    return shuffle_with_index_impl


@numba.njit(cache=True)
def reverse_shuffle(data, orig_indices, shuffle_meta):
    jhvdh__azj = alloc_arr_tup(shuffle_meta.n_send, data)
    oagi__igupz = ShuffleMeta(shuffle_meta.recv_counts, shuffle_meta.
        send_counts, shuffle_meta.n_out, shuffle_meta.n_send, shuffle_meta.
        recv_disp, shuffle_meta.send_disp, shuffle_meta.recv_disp_nulls,
        shuffle_meta.send_disp_nulls, shuffle_meta.tmp_offset, data,
        jhvdh__azj, shuffle_meta.recv_counts_char_tup, shuffle_meta.
        send_counts_char_tup, shuffle_meta.send_arr_lens_tup, shuffle_meta.
        send_arr_nulls_tup, shuffle_meta.send_arr_chars_tup, shuffle_meta.
        recv_disp_char_tup, shuffle_meta.send_disp_char_tup, shuffle_meta.
        tmp_offset_char_tup, shuffle_meta.send_arr_chars_arr_tup)
    jhvdh__azj = alltoallv_tup(data, oagi__igupz, ())
    uwmoy__tdjhn = alloc_arr_tup(shuffle_meta.n_send, data)
    for i in range(len(orig_indices)):
        setitem_arr_tup(uwmoy__tdjhn, orig_indices[i], getitem_arr_tup(
            jhvdh__azj, i))
    return uwmoy__tdjhn


def _get_keys_tup(recvs, key_arrs):
    return recvs[:len(key_arrs)]


@overload(_get_keys_tup, no_unliteral=True)
def _get_keys_tup_overload(recvs, key_arrs):
    foxvb__dlb = len(key_arrs.types)
    xtgr__phe = 'def f(recvs, key_arrs):\n'
    uizi__zafxf = ','.join('recvs[{}]'.format(i) for i in range(foxvb__dlb))
    xtgr__phe += '  return ({}{})\n'.format(uizi__zafxf, ',' if foxvb__dlb ==
        1 else '')
    bzniv__tft = {}
    exec(xtgr__phe, {}, bzniv__tft)
    dflr__gug = bzniv__tft['f']
    return dflr__gug


def _get_data_tup(recvs, key_arrs):
    return recvs[len(key_arrs):]


@overload(_get_data_tup, no_unliteral=True)
def _get_data_tup_overload(recvs, key_arrs):
    foxvb__dlb = len(key_arrs.types)
    hdsrc__zev = len(recvs.types)
    nwtre__jlujh = hdsrc__zev - foxvb__dlb
    xtgr__phe = 'def f(recvs, key_arrs):\n'
    uizi__zafxf = ','.join('recvs[{}]'.format(i) for i in range(foxvb__dlb,
        hdsrc__zev))
    xtgr__phe += '  return ({}{})\n'.format(uizi__zafxf, ',' if 
        nwtre__jlujh == 1 else '')
    bzniv__tft = {}
    exec(xtgr__phe, {}, bzniv__tft)
    dflr__gug = bzniv__tft['f']
    return dflr__gug


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
