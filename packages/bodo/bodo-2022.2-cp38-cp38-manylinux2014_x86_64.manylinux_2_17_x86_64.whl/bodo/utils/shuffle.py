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
    whi__qtib = 'def f(key_arrs, data, n_pes, is_contig):\n'
    whi__qtib += '  send_counts = np.zeros(n_pes, np.int32)\n'
    nsxk__gge = len(key_arrs.types)
    judy__zwq = nsxk__gge + len(data.types)
    for i, hefft__dfifj in enumerate(key_arrs.types + data.types):
        whi__qtib += '  arr = key_arrs[{}]\n'.format(i
            ) if i < nsxk__gge else '  arr = data[{}]\n'.format(i - nsxk__gge)
        if hefft__dfifj in [string_array_type, binary_array_type]:
            whi__qtib += ('  send_counts_char_{} = np.zeros(n_pes, np.int32)\n'
                .format(i))
            whi__qtib += ('  send_arr_lens_{} = np.empty(0, np.uint32)\n'.
                format(i))
            whi__qtib += '  if is_contig:\n'
            whi__qtib += (
                '    send_arr_lens_{} = np.empty(len(arr), np.uint32)\n'.
                format(i))
        else:
            whi__qtib += '  send_counts_char_{} = None\n'.format(i)
            whi__qtib += '  send_arr_lens_{} = None\n'.format(i)
        if is_null_masked_type(hefft__dfifj):
            whi__qtib += ('  send_arr_nulls_{} = np.empty(0, np.uint8)\n'.
                format(i))
            whi__qtib += '  if is_contig:\n'
            whi__qtib += '    n_bytes = (len(arr) + 7) >> 3\n'
            whi__qtib += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            whi__qtib += '  send_arr_nulls_{} = None\n'.format(i)
    itxi__mqzr = ', '.join('send_counts_char_{}'.format(i) for i in range(
        judy__zwq))
    ctsv__hbpp = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        judy__zwq))
    bwlb__qsa = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        judy__zwq))
    uqdar__meyk = ',' if judy__zwq == 1 else ''
    whi__qtib += (
        '  return PreShuffleMeta(send_counts, ({}{}), ({}{}), ({}{}))\n'.
        format(itxi__mqzr, uqdar__meyk, ctsv__hbpp, uqdar__meyk, bwlb__qsa,
        uqdar__meyk))
    lilv__huinq = {}
    exec(whi__qtib, {'np': np, 'PreShuffleMeta': PreShuffleMeta}, lilv__huinq)
    yuo__svk = lilv__huinq['f']
    return yuo__svk


def update_shuffle_meta(pre_shuffle_meta, node_id, ind, key_arrs, data,
    is_contig=True, padded_bits=0):
    pre_shuffle_meta.send_counts[node_id] += 1


@overload(update_shuffle_meta, no_unliteral=True)
def update_shuffle_meta_overload(pre_shuffle_meta, node_id, ind, key_arrs,
    data, is_contig=True, padded_bits=0):
    bmajm__fdo = 'BODO_DEBUG_LEVEL'
    oxh__fnxp = 0
    try:
        oxh__fnxp = int(os.environ[bmajm__fdo])
    except:
        pass
    whi__qtib = """def f(pre_shuffle_meta, node_id, ind, key_arrs, data, is_contig=True, padded_bits=0):
"""
    whi__qtib += '  pre_shuffle_meta.send_counts[node_id] += 1\n'
    if oxh__fnxp > 0:
        whi__qtib += ('  if pre_shuffle_meta.send_counts[node_id] >= {}:\n'
            .format(bodo.libs.distributed_api.INT_MAX))
        whi__qtib += "    print('large shuffle error')\n"
    nsxk__gge = len(key_arrs.types)
    for i, hefft__dfifj in enumerate(key_arrs.types + data.types):
        if hefft__dfifj in (string_type, string_array_type, bytes_type,
            binary_array_type):
            arr = 'key_arrs[{}]'.format(i
                ) if i < nsxk__gge else 'data[{}]'.format(i - nsxk__gge)
            whi__qtib += ('  n_chars = get_str_arr_item_length({}, ind)\n'.
                format(arr))
            whi__qtib += (
                '  pre_shuffle_meta.send_counts_char_tup[{}][node_id] += n_chars\n'
                .format(i))
            if oxh__fnxp > 0:
                whi__qtib += (
                    '  if pre_shuffle_meta.send_counts_char_tup[{}][node_id] >= {}:\n'
                    .format(i, bodo.libs.distributed_api.INT_MAX))
                whi__qtib += "    print('large shuffle error')\n"
            whi__qtib += '  if is_contig:\n'
            whi__qtib += (
                '    pre_shuffle_meta.send_arr_lens_tup[{}][ind] = n_chars\n'
                .format(i))
        if is_null_masked_type(hefft__dfifj):
            whi__qtib += '  if is_contig:\n'
            whi__qtib += (
                '    out_bitmap = pre_shuffle_meta.send_arr_nulls_tup[{}].ctypes\n'
                .format(i))
            if i < nsxk__gge:
                whi__qtib += ('    bit_val = get_mask_bit(key_arrs[{}], ind)\n'
                    .format(i))
            else:
                whi__qtib += ('    bit_val = get_mask_bit(data[{}], ind)\n'
                    .format(i - nsxk__gge))
            whi__qtib += (
                '    set_bit_to(out_bitmap, padded_bits + ind, bit_val)\n')
    lilv__huinq = {}
    exec(whi__qtib, {'set_bit_to': set_bit_to, 'get_bit_bitmap':
        get_bit_bitmap, 'get_null_bitmap_ptr': get_null_bitmap_ptr,
        'getitem_arr_tup': getitem_arr_tup, 'get_mask_bit': get_mask_bit,
        'get_str_arr_item_length': get_str_arr_item_length}, lilv__huinq)
    rgih__zmyp = lilv__huinq['f']
    return rgih__zmyp


@numba.njit
def calc_disp_nulls(arr):
    smqx__qhier = np.empty_like(arr)
    smqx__qhier[0] = 0
    for i in range(1, len(arr)):
        jxqm__gfnv = arr[i - 1] + 7 >> 3
        smqx__qhier[i] = smqx__qhier[i - 1] + jxqm__gfnv
    return smqx__qhier


def finalize_shuffle_meta(arrs, data, pre_shuffle_meta, n_pes, is_contig,
    init_vals=()):
    return ShuffleMeta()


@overload(finalize_shuffle_meta, no_unliteral=True)
def finalize_shuffle_meta_overload(key_arrs, data, pre_shuffle_meta, n_pes,
    is_contig, init_vals=()):
    whi__qtib = (
        'def f(key_arrs, data, pre_shuffle_meta, n_pes, is_contig, init_vals=()):\n'
        )
    whi__qtib += '  send_counts = pre_shuffle_meta.send_counts\n'
    whi__qtib += '  recv_counts = np.empty(n_pes, np.int32)\n'
    whi__qtib += '  tmp_offset = np.zeros(n_pes, np.int32)\n'
    whi__qtib += (
        '  bodo.libs.distributed_api.alltoall(send_counts, recv_counts, 1)\n')
    whi__qtib += '  n_out = recv_counts.sum()\n'
    whi__qtib += '  n_send = send_counts.sum()\n'
    whi__qtib += '  send_disp = bodo.ir.join.calc_disp(send_counts)\n'
    whi__qtib += '  recv_disp = bodo.ir.join.calc_disp(recv_counts)\n'
    whi__qtib += '  send_disp_nulls = calc_disp_nulls(send_counts)\n'
    whi__qtib += '  recv_disp_nulls = calc_disp_nulls(recv_counts)\n'
    nsxk__gge = len(key_arrs.types)
    judy__zwq = len(key_arrs.types + data.types)
    for i, hefft__dfifj in enumerate(key_arrs.types + data.types):
        whi__qtib += '  arr = key_arrs[{}]\n'.format(i
            ) if i < nsxk__gge else '  arr = data[{}]\n'.format(i - nsxk__gge)
        if hefft__dfifj in [string_array_type, binary_array_type]:
            if hefft__dfifj == string_array_type:
                bihdr__uwxli = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
            else:
                bihdr__uwxli = (
                    'bodo.libs.binary_arr_ext.pre_alloc_binary_array')
            whi__qtib += '  send_buff_{} = None\n'.format(i)
            whi__qtib += (
                '  send_counts_char_{} = pre_shuffle_meta.send_counts_char_tup[{}]\n'
                .format(i, i))
            whi__qtib += ('  recv_counts_char_{} = np.empty(n_pes, np.int32)\n'
                .format(i))
            whi__qtib += (
                """  bodo.libs.distributed_api.alltoall(send_counts_char_{}, recv_counts_char_{}, 1)
"""
                .format(i, i))
            whi__qtib += '  n_all_chars = recv_counts_char_{}.sum()\n'.format(i
                )
            whi__qtib += '  out_arr_{} = {}(n_out, n_all_chars)\n'.format(i,
                bihdr__uwxli)
            whi__qtib += (
                '  send_disp_char_{} = bodo.ir.join.calc_disp(send_counts_char_{})\n'
                .format(i, i))
            whi__qtib += (
                '  recv_disp_char_{} = bodo.ir.join.calc_disp(recv_counts_char_{})\n'
                .format(i, i))
            whi__qtib += ('  tmp_offset_char_{} = np.zeros(n_pes, np.int32)\n'
                .format(i))
            whi__qtib += (
                '  send_arr_lens_{} = pre_shuffle_meta.send_arr_lens_tup[{}]\n'
                .format(i, i))
            whi__qtib += ('  send_arr_chars_arr_{} = np.empty(0, np.uint8)\n'
                .format(i))
            whi__qtib += (
                '  send_arr_chars_{} = get_ctypes_ptr(get_data_ptr(arr))\n'
                .format(i))
            whi__qtib += '  if not is_contig:\n'
            whi__qtib += (
                '    send_arr_lens_{} = np.empty(n_send, np.uint32)\n'.
                format(i))
            whi__qtib += ('    s_n_all_chars = send_counts_char_{}.sum()\n'
                .format(i))
            whi__qtib += (
                '    send_arr_chars_arr_{} = np.empty(s_n_all_chars, np.uint8)\n'
                .format(i))
            whi__qtib += (
                '    send_arr_chars_{} = get_ctypes_ptr(send_arr_chars_arr_{}.ctypes)\n'
                .format(i, i))
        else:
            assert isinstance(hefft__dfifj, (types.Array, IntegerArrayType,
                BooleanArrayType, bodo.CategoricalArrayType))
            whi__qtib += (
                '  out_arr_{} = bodo.utils.utils.alloc_type(n_out, arr)\n'.
                format(i))
            whi__qtib += '  send_buff_{} = arr\n'.format(i)
            whi__qtib += '  if not is_contig:\n'
            if i >= nsxk__gge and init_vals != ():
                whi__qtib += (
                    """    send_buff_{} = bodo.utils.utils.full_type(n_send, init_vals[{}], arr)
"""
                    .format(i, i - nsxk__gge))
            else:
                whi__qtib += (
                    '    send_buff_{} = bodo.utils.utils.alloc_type(n_send, arr)\n'
                    .format(i))
            whi__qtib += '  send_counts_char_{} = None\n'.format(i)
            whi__qtib += '  recv_counts_char_{} = None\n'.format(i)
            whi__qtib += '  send_arr_lens_{} = None\n'.format(i)
            whi__qtib += '  send_arr_chars_{} = None\n'.format(i)
            whi__qtib += '  send_disp_char_{} = None\n'.format(i)
            whi__qtib += '  recv_disp_char_{} = None\n'.format(i)
            whi__qtib += '  tmp_offset_char_{} = None\n'.format(i)
            whi__qtib += '  send_arr_chars_arr_{} = None\n'.format(i)
        if is_null_masked_type(hefft__dfifj):
            whi__qtib += (
                '  send_arr_nulls_{} = pre_shuffle_meta.send_arr_nulls_tup[{}]\n'
                .format(i, i))
            whi__qtib += '  if not is_contig:\n'
            whi__qtib += '    n_bytes = (n_send + 7) >> 3\n'
            whi__qtib += (
                '    send_arr_nulls_{} = np.full(n_bytes + 2 * n_pes, 255, np.uint8)\n'
                .format(i))
        else:
            whi__qtib += '  send_arr_nulls_{} = None\n'.format(i)
    ojyav__soaoq = ', '.join('send_buff_{}'.format(i) for i in range(judy__zwq)
        )
    vccyg__gzh = ', '.join('out_arr_{}'.format(i) for i in range(judy__zwq))
    ykn__crgaq = ',' if judy__zwq == 1 else ''
    cjlse__tjxs = ', '.join('send_counts_char_{}'.format(i) for i in range(
        judy__zwq))
    jec__yai = ', '.join('recv_counts_char_{}'.format(i) for i in range(
        judy__zwq))
    veoh__uuj = ', '.join('send_arr_lens_{}'.format(i) for i in range(
        judy__zwq))
    pmnfv__joof = ', '.join('send_arr_nulls_{}'.format(i) for i in range(
        judy__zwq))
    jmdo__zva = ', '.join('send_arr_chars_{}'.format(i) for i in range(
        judy__zwq))
    ravek__yir = ', '.join('send_disp_char_{}'.format(i) for i in range(
        judy__zwq))
    xpi__skzi = ', '.join('recv_disp_char_{}'.format(i) for i in range(
        judy__zwq))
    cgwpt__juipm = ', '.join('tmp_offset_char_{}'.format(i) for i in range(
        judy__zwq))
    fuifu__csmwq = ', '.join('send_arr_chars_arr_{}'.format(i) for i in
        range(judy__zwq))
    whi__qtib += (
        """  return ShuffleMeta(send_counts, recv_counts, n_send, n_out, send_disp, recv_disp, send_disp_nulls, recv_disp_nulls, tmp_offset, ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), ({}{}), )
"""
        .format(ojyav__soaoq, ykn__crgaq, vccyg__gzh, ykn__crgaq,
        cjlse__tjxs, ykn__crgaq, jec__yai, ykn__crgaq, veoh__uuj,
        ykn__crgaq, pmnfv__joof, ykn__crgaq, jmdo__zva, ykn__crgaq,
        ravek__yir, ykn__crgaq, xpi__skzi, ykn__crgaq, cgwpt__juipm,
        ykn__crgaq, fuifu__csmwq, ykn__crgaq))
    lilv__huinq = {}
    exec(whi__qtib, {'np': np, 'bodo': bodo, 'num_total_chars':
        num_total_chars, 'get_data_ptr': get_data_ptr, 'ShuffleMeta':
        ShuffleMeta, 'get_ctypes_ptr': get_ctypes_ptr, 'calc_disp_nulls':
        calc_disp_nulls}, lilv__huinq)
    teus__drkn = lilv__huinq['f']
    return teus__drkn


def alltoallv_tup(arrs, shuffle_meta, key_arrs):
    return arrs


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(arrs, meta, key_arrs):
    nsxk__gge = len(key_arrs.types)
    whi__qtib = 'def f(arrs, meta, key_arrs):\n'
    if any(is_null_masked_type(t) for t in arrs.types):
        whi__qtib += (
            '  send_counts_nulls = np.empty(len(meta.send_counts), np.int32)\n'
            )
        whi__qtib += '  for i in range(len(meta.send_counts)):\n'
        whi__qtib += (
            '    send_counts_nulls[i] = (meta.send_counts[i] + 7) >> 3\n')
        whi__qtib += (
            '  recv_counts_nulls = np.empty(len(meta.recv_counts), np.int32)\n'
            )
        whi__qtib += '  for i in range(len(meta.recv_counts)):\n'
        whi__qtib += (
            '    recv_counts_nulls[i] = (meta.recv_counts[i] + 7) >> 3\n')
        whi__qtib += (
            '  tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)\n')
    whi__qtib += '  lens = np.empty(meta.n_out, np.uint32)\n'
    for i, hefft__dfifj in enumerate(arrs.types):
        if isinstance(hefft__dfifj, (types.Array, IntegerArrayType,
            BooleanArrayType, bodo.CategoricalArrayType)):
            whi__qtib += (
                """  bodo.libs.distributed_api.alltoallv(meta.send_buff_tup[{}], meta.out_arr_tup[{}], meta.send_counts,meta.recv_counts, meta.send_disp, meta.recv_disp)
"""
                .format(i, i))
        else:
            assert hefft__dfifj in [string_array_type, binary_array_type]
            whi__qtib += (
                '  offset_ptr_{} = get_offset_ptr(meta.out_arr_tup[{}])\n'.
                format(i, i))
            if offset_type.bitwidth == 32:
                whi__qtib += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, offset_ptr_{}, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i, i))
            else:
                whi__qtib += (
                    """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_lens_tup[{}].ctypes, lens.ctypes, meta.send_counts.ctypes, meta.recv_counts.ctypes, meta.send_disp.ctypes, meta.recv_disp.ctypes, int32_typ_enum)
"""
                    .format(i))
            whi__qtib += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_chars_tup[{}], get_data_ptr(meta.out_arr_tup[{}]), meta.send_counts_char_tup[{}].ctypes,meta.recv_counts_char_tup[{}].ctypes, meta.send_disp_char_tup[{}].ctypes,meta.recv_disp_char_tup[{}].ctypes, char_typ_enum)
"""
                .format(i, i, i, i, i, i))
            if offset_type.bitwidth == 32:
                whi__qtib += (
                    '  convert_len_arr_to_offset32(offset_ptr_{}, meta.n_out)\n'
                    .format(i))
            else:
                whi__qtib += (
                    """  convert_len_arr_to_offset(lens.ctypes, offset_ptr_{}, meta.n_out)
"""
                    .format(i))
        if is_null_masked_type(hefft__dfifj):
            whi__qtib += (
                '  null_bitmap_ptr_{} = get_arr_null_ptr(meta.out_arr_tup[{}])\n'
                .format(i, i))
            whi__qtib += (
                """  bodo.libs.distributed_api.c_alltoallv(meta.send_arr_nulls_tup[{}].ctypes, tmp_null_bytes.ctypes, send_counts_nulls.ctypes, recv_counts_nulls.ctypes, meta.send_disp_nulls.ctypes, meta.recv_disp_nulls.ctypes, char_typ_enum)
"""
                .format(i))
            whi__qtib += (
                """  copy_gathered_null_bytes(null_bitmap_ptr_{}, tmp_null_bytes, recv_counts_nulls, meta.recv_counts)
"""
                .format(i))
    whi__qtib += '  return ({}{})\n'.format(','.join([
        'meta.out_arr_tup[{}]'.format(i) for i in range(arrs.count)]), ',' if
        arrs.count == 1 else '')
    nwnq__cofjg = np.int32(numba_to_c_type(types.int32))
    xrqdb__byb = np.int32(numba_to_c_type(types.uint8))
    lilv__huinq = {}
    exec(whi__qtib, {'np': np, 'bodo': bodo, 'get_offset_ptr':
        get_offset_ptr, 'get_data_ptr': get_data_ptr, 'int32_typ_enum':
        nwnq__cofjg, 'char_typ_enum': xrqdb__byb,
        'convert_len_arr_to_offset': convert_len_arr_to_offset,
        'convert_len_arr_to_offset32': convert_len_arr_to_offset32,
        'copy_gathered_null_bytes': bodo.libs.distributed_api.
        copy_gathered_null_bytes, 'get_arr_null_ptr': get_arr_null_ptr,
        'print_str_arr': print_str_arr}, lilv__huinq)
    mcfzq__vaw = lilv__huinq['f']
    return mcfzq__vaw


def shuffle_with_index_impl(key_arrs, node_arr, data):
    n_pes = bodo.libs.distributed_api.get_size()
    pre_shuffle_meta = alloc_pre_shuffle_metadata(key_arrs, data, n_pes, False)
    izfut__mggi = len(key_arrs[0])
    orig_indices = np.arange(izfut__mggi)
    synd__kasd = np.empty(izfut__mggi, np.int32)
    for i in range(izfut__mggi):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = node_arr[i]
        synd__kasd[i] = node_id
        update_shuffle_meta(pre_shuffle_meta, node_id, i, key_arrs, data, False
            )
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, pre_shuffle_meta,
        n_pes, False)
    for i in range(izfut__mggi):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = synd__kasd[i]
        xri__mrrt = bodo.ir.join.write_send_buff(shuffle_meta, node_id, i,
            key_arrs, data)
        orig_indices[xri__mrrt] = i
        shuffle_meta.tmp_offset[node_id] += 1
    recvs = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    yajnd__mej = _get_keys_tup(recvs, key_arrs)
    bxpk__bor = _get_data_tup(recvs, key_arrs)
    return yajnd__mej, bxpk__bor, orig_indices, shuffle_meta


@generated_jit(nopython=True, cache=True)
def shuffle_with_index(key_arrs, node_arr, data):
    return shuffle_with_index_impl


@numba.njit(cache=True)
def reverse_shuffle(data, orig_indices, shuffle_meta):
    vccyg__gzh = alloc_arr_tup(shuffle_meta.n_send, data)
    odhqq__wrt = ShuffleMeta(shuffle_meta.recv_counts, shuffle_meta.
        send_counts, shuffle_meta.n_out, shuffle_meta.n_send, shuffle_meta.
        recv_disp, shuffle_meta.send_disp, shuffle_meta.recv_disp_nulls,
        shuffle_meta.send_disp_nulls, shuffle_meta.tmp_offset, data,
        vccyg__gzh, shuffle_meta.recv_counts_char_tup, shuffle_meta.
        send_counts_char_tup, shuffle_meta.send_arr_lens_tup, shuffle_meta.
        send_arr_nulls_tup, shuffle_meta.send_arr_chars_tup, shuffle_meta.
        recv_disp_char_tup, shuffle_meta.send_disp_char_tup, shuffle_meta.
        tmp_offset_char_tup, shuffle_meta.send_arr_chars_arr_tup)
    vccyg__gzh = alltoallv_tup(data, odhqq__wrt, ())
    kdvs__pvv = alloc_arr_tup(shuffle_meta.n_send, data)
    for i in range(len(orig_indices)):
        setitem_arr_tup(kdvs__pvv, orig_indices[i], getitem_arr_tup(
            vccyg__gzh, i))
    return kdvs__pvv


def _get_keys_tup(recvs, key_arrs):
    return recvs[:len(key_arrs)]


@overload(_get_keys_tup, no_unliteral=True)
def _get_keys_tup_overload(recvs, key_arrs):
    nsxk__gge = len(key_arrs.types)
    whi__qtib = 'def f(recvs, key_arrs):\n'
    pla__jzwqz = ','.join('recvs[{}]'.format(i) for i in range(nsxk__gge))
    whi__qtib += '  return ({}{})\n'.format(pla__jzwqz, ',' if nsxk__gge ==
        1 else '')
    lilv__huinq = {}
    exec(whi__qtib, {}, lilv__huinq)
    terty__gfv = lilv__huinq['f']
    return terty__gfv


def _get_data_tup(recvs, key_arrs):
    return recvs[len(key_arrs):]


@overload(_get_data_tup, no_unliteral=True)
def _get_data_tup_overload(recvs, key_arrs):
    nsxk__gge = len(key_arrs.types)
    judy__zwq = len(recvs.types)
    bnth__meke = judy__zwq - nsxk__gge
    whi__qtib = 'def f(recvs, key_arrs):\n'
    pla__jzwqz = ','.join('recvs[{}]'.format(i) for i in range(nsxk__gge,
        judy__zwq))
    whi__qtib += '  return ({}{})\n'.format(pla__jzwqz, ',' if bnth__meke ==
        1 else '')
    lilv__huinq = {}
    exec(whi__qtib, {}, lilv__huinq)
    terty__gfv = lilv__huinq['f']
    return terty__gfv


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
