"""Array implementation for binary (bytes) objects, which are usually immutable.
It is equivalent to string array, except that it stores a 'bytes' object for each
element instead of 'str'.
"""
import operator
import llvmlite.binding as ll
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.utils.typing import BodoError, is_list_like_index_type
_bytes_fromhex = types.ExternalFunction('bytes_fromhex', types.int64(types.
    voidptr, types.voidptr, types.uint64))
ll.add_symbol('bytes_to_hex', hstr_ext.bytes_to_hex)
ll.add_symbol('bytes_fromhex', hstr_ext.bytes_fromhex)
bytes_type = types.Bytes(types.uint8, 1, 'C', readonly=True)


class BinaryArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BinaryArrayType, self).__init__(name='BinaryArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return bytes_type

    def copy(self):
        return BinaryArrayType()


binary_array_type = BinaryArrayType()


@overload(len, no_unliteral=True)
def bin_arr_len_overload(bin_arr):
    if bin_arr == binary_array_type:
        return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'size')
def bin_arr_size_overload(bin_arr):
    return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'shape')
def bin_arr_shape_overload(bin_arr):
    return lambda bin_arr: (len(bin_arr._data),)


@overload_attribute(BinaryArrayType, 'nbytes')
def bin_arr_nbytes_overload(bin_arr):
    return lambda bin_arr: bin_arr._data.nbytes


@overload_attribute(BinaryArrayType, 'ndim')
def overload_bin_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BinaryArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: np.dtype('O')


@numba.njit
def pre_alloc_binary_array(n_bytestrs, n_chars):
    if n_chars is None:
        n_chars = -1
    bin_arr = init_binary_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_bytestrs), (np.int64(n_chars)
        ,), bodo.libs.str_arr_ext.char_arr_type))
    if n_chars == 0:
        bodo.libs.str_arr_ext.set_all_offsets_to_0(bin_arr)
    return bin_arr


@intrinsic
def init_binary_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, sig, args):
        kwwpi__prwx, = args
        jigh__wzo = context.make_helper(builder, binary_array_type)
        jigh__wzo.data = kwwpi__prwx
        context.nrt.incref(builder, data_typ, kwwpi__prwx)
        return jigh__wzo._getvalue()
    return binary_array_type(data_typ), codegen


@intrinsic
def init_bytes_type(typingctx, data_typ, length_type):
    assert data_typ == types.Array(types.uint8, 1, 'C')
    assert length_type == types.int64

    def codegen(context, builder, sig, args):
        wuboc__eow = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        wcqgp__bgsz = args[1]
        maebc__uuex = cgutils.create_struct_proxy(bytes_type)(context, builder)
        maebc__uuex.meminfo = context.nrt.meminfo_alloc(builder, wcqgp__bgsz)
        maebc__uuex.nitems = wcqgp__bgsz
        maebc__uuex.itemsize = lir.Constant(maebc__uuex.itemsize.type, 1)
        maebc__uuex.data = context.nrt.meminfo_data(builder, maebc__uuex.
            meminfo)
        maebc__uuex.parent = cgutils.get_null_value(maebc__uuex.parent.type)
        maebc__uuex.shape = cgutils.pack_array(builder, [wcqgp__bgsz],
            context.get_value_type(types.intp))
        maebc__uuex.strides = wuboc__eow.strides
        cgutils.memcpy(builder, maebc__uuex.data, wuboc__eow.data, wcqgp__bgsz)
        return maebc__uuex._getvalue()
    return bytes_type(data_typ, length_type), codegen


@intrinsic
def cast_bytes_uint8array(typingctx, data_typ):
    assert data_typ == bytes_type

    def codegen(context, builder, sig, args):
        return impl_ret_borrowed(context, builder, sig.return_type, args[0])
    return types.Array(types.uint8, 1, 'C')(data_typ), codegen


@overload_method(BinaryArrayType, 'copy', no_unliteral=True)
def binary_arr_copy_overload(arr):

    def copy_impl(arr):
        return init_binary_arr(arr._data.copy())
    return copy_impl


@overload_method(types.Bytes, 'hex')
def binary_arr_hex(arr):
    gwv__riky = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def impl(arr):
        wcqgp__bgsz = len(arr) * 2
        output = numba.cpython.unicode._empty_string(gwv__riky, wcqgp__bgsz, 1)
        bytes_to_hex(output, arr)
        return output
    return impl


@lower_cast(types.CPointer(types.uint8), types.voidptr)
def cast_uint8_array_to_voidptr(context, builder, fromty, toty, val):
    return val


make_attribute_wrapper(types.Bytes, 'data', '_data')


@overload_method(types.Bytes, '__hash__')
def bytes_hash(arr):

    def impl(arr):
        return numba.cpython.hashing._Py_HashBytes(arr._data, len(arr))
    return impl


@intrinsic
def bytes_to_hex(typingctx, output, arr):

    def codegen(context, builder, sig, args):
        wuzno__hvbj = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        lhl__alx = cgutils.create_struct_proxy(sig.args[1])(context,
            builder, value=args[1])
        kddij__xxs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(64)])
        cnl__vfa = cgutils.get_or_insert_function(builder.module,
            kddij__xxs, name='bytes_to_hex')
        builder.call(cnl__vfa, (wuzno__hvbj.data, lhl__alx.data, lhl__alx.
            nitems))
    return types.void(output, arr), codegen


@overload(operator.getitem, no_unliteral=True)
def binary_arr_getitem(arr, ind):
    if arr != binary_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl(arr, ind):
            vwf__pmna = arr._data[ind]
            return init_bytes_type(vwf__pmna, len(vwf__pmna))
        return impl
    if is_list_like_index_type(ind) and (ind.dtype == types.bool_ or
        isinstance(ind.dtype, types.Integer)) or isinstance(ind, types.
        SliceType):
        return lambda arr, ind: init_binary_arr(arr._data[ind])
    raise BodoError(
        f'getitem for Binary Array with indexing type {ind} not supported.')


def bytes_fromhex(hex_str):
    pass


@overload(bytes_fromhex)
def overload_bytes_fromhex(hex_str):
    hex_str = types.unliteral(hex_str)
    if hex_str == bodo.string_type:
        gwv__riky = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(hex_str):
            if not hex_str._is_ascii or hex_str._kind != gwv__riky:
                raise TypeError(
                    'bytes.fromhex is only supported on ascii strings')
            kwwpi__prwx = np.empty(len(hex_str) // 2, np.uint8)
            wcqgp__bgsz = _bytes_fromhex(kwwpi__prwx.ctypes, hex_str._data,
                len(hex_str))
            result = init_bytes_type(kwwpi__prwx, wcqgp__bgsz)
            return result
        return impl
    raise BodoError(f'bytes.fromhex not supported with argument type {hex_str}'
        )


@overload(operator.setitem)
def binary_arr_setitem(arr, ind, val):
    if arr != binary_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if val != bytes_type:
        raise BodoError(
            f'setitem for Binary Array only supported with bytes value and integer indexing'
            )
    if isinstance(ind, types.Integer):

        def impl(arr, ind, val):
            arr._data[ind] = bodo.libs.binary_arr_ext.cast_bytes_uint8array(val
                )
        return impl
    raise BodoError(
        f'setitem for Binary Array with indexing type {ind} not supported.')


def create_binary_cmp_op_overload(op):

    def overload_binary_cmp(lhs, rhs):
        zti__hkw = lhs == binary_array_type
        dac__xebh = rhs == binary_array_type
        oskm__nsu = 'lhs' if zti__hkw else 'rhs'
        qfj__oxrkd = 'def impl(lhs, rhs):\n'
        qfj__oxrkd += '  numba.parfors.parfor.init_prange()\n'
        qfj__oxrkd += f'  n = len({oskm__nsu})\n'
        qfj__oxrkd += (
            '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n)\n')
        qfj__oxrkd += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        cyh__cnqmg = []
        if zti__hkw:
            cyh__cnqmg.append('bodo.libs.array_kernels.isna(lhs, i)')
        if dac__xebh:
            cyh__cnqmg.append('bodo.libs.array_kernels.isna(rhs, i)')
        qfj__oxrkd += f"    if {' or '.join(cyh__cnqmg)}:\n"
        qfj__oxrkd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        qfj__oxrkd += '      continue\n'
        cief__yfhb = 'lhs[i]' if zti__hkw else 'lhs'
        xcwgh__iehol = 'rhs[i]' if dac__xebh else 'rhs'
        qfj__oxrkd += f'    out_arr[i] = op({cief__yfhb}, {xcwgh__iehol})\n'
        qfj__oxrkd += '  return out_arr\n'
        eez__ndhh = {}
        exec(qfj__oxrkd, {'bodo': bodo, 'numba': numba, 'op': op}, eez__ndhh)
        return eez__ndhh['impl']
    return overload_binary_cmp


class BinaryArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        rxya__ptvp = 'iter(Bytes)'
        dmyga__ldh = bytes_type
        super(BinaryArrayIterator, self).__init__(rxya__ptvp, dmyga__ldh)


@register_model(BinaryArrayIterator)
class BinaryArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xbjy__mwzl = [('index', types.EphemeralPointer(types.uintp)), (
            'array', binary_array_type)]
        super(BinaryArrayIteratorModel, self).__init__(dmm, fe_type, xbjy__mwzl
            )


lower_builtin('getiter', binary_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', BinaryArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_binary_array(context, builder, sig, args, result):
    [gcxgb__gccgq] = sig.args
    [cabyq__zwxhv] = args
    cbv__suj = context.make_helper(builder, gcxgb__gccgq, value=cabyq__zwxhv)
    thag__dgtf = signature(types.intp, binary_array_type)
    mtlj__ubihj = context.compile_internal(builder, lambda a: len(a),
        thag__dgtf, [cbv__suj.array])
    fxyv__zka = builder.load(cbv__suj.index)
    enbl__plgog = builder.icmp(lc.ICMP_SLT, fxyv__zka, mtlj__ubihj)
    result.set_valid(enbl__plgog)
    with builder.if_then(enbl__plgog):
        lvdzj__fzf = signature(bytes_type, binary_array_type, types.intp)
        acg__arf = context.compile_internal(builder, lambda a, i: a[i],
            lvdzj__fzf, [cbv__suj.array, fxyv__zka])
        result.yield_(acg__arf)
        apyoa__inst = cgutils.increment_index(builder, fxyv__zka)
        builder.store(apyoa__inst, cbv__suj.index)


def pre_alloc_binary_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_binary_arr_ext_pre_alloc_binary_array
    ) = pre_alloc_binary_arr_equiv
