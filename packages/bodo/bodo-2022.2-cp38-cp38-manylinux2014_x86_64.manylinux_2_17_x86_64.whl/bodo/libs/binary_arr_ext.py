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
        ayb__hahy, = args
        ojmm__vgz = context.make_helper(builder, binary_array_type)
        ojmm__vgz.data = ayb__hahy
        context.nrt.incref(builder, data_typ, ayb__hahy)
        return ojmm__vgz._getvalue()
    return binary_array_type(data_typ), codegen


@intrinsic
def init_bytes_type(typingctx, data_typ, length_type):
    assert data_typ == types.Array(types.uint8, 1, 'C')
    assert length_type == types.int64

    def codegen(context, builder, sig, args):
        dqrxe__ufet = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        fxk__ock = args[1]
        qpb__nfr = cgutils.create_struct_proxy(bytes_type)(context, builder)
        qpb__nfr.meminfo = context.nrt.meminfo_alloc(builder, fxk__ock)
        qpb__nfr.nitems = fxk__ock
        qpb__nfr.itemsize = lir.Constant(qpb__nfr.itemsize.type, 1)
        qpb__nfr.data = context.nrt.meminfo_data(builder, qpb__nfr.meminfo)
        qpb__nfr.parent = cgutils.get_null_value(qpb__nfr.parent.type)
        qpb__nfr.shape = cgutils.pack_array(builder, [fxk__ock], context.
            get_value_type(types.intp))
        qpb__nfr.strides = dqrxe__ufet.strides
        cgutils.memcpy(builder, qpb__nfr.data, dqrxe__ufet.data, fxk__ock)
        return qpb__nfr._getvalue()
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
    rfdl__nbno = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def impl(arr):
        fxk__ock = len(arr) * 2
        output = numba.cpython.unicode._empty_string(rfdl__nbno, fxk__ock, 1)
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
        omw__vzdhn = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        mzpqc__amuhb = cgutils.create_struct_proxy(sig.args[1])(context,
            builder, value=args[1])
        vnn__uft = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(64)])
        mzy__utbd = cgutils.get_or_insert_function(builder.module, vnn__uft,
            name='bytes_to_hex')
        builder.call(mzy__utbd, (omw__vzdhn.data, mzpqc__amuhb.data,
            mzpqc__amuhb.nitems))
    return types.void(output, arr), codegen


@overload(operator.getitem, no_unliteral=True)
def binary_arr_getitem(arr, ind):
    if arr != binary_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl(arr, ind):
            bwv__tppqi = arr._data[ind]
            return init_bytes_type(bwv__tppqi, len(bwv__tppqi))
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
        rfdl__nbno = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(hex_str):
            if not hex_str._is_ascii or hex_str._kind != rfdl__nbno:
                raise TypeError(
                    'bytes.fromhex is only supported on ascii strings')
            ayb__hahy = np.empty(len(hex_str) // 2, np.uint8)
            fxk__ock = _bytes_fromhex(ayb__hahy.ctypes, hex_str._data, len(
                hex_str))
            result = init_bytes_type(ayb__hahy, fxk__ock)
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
        axko__calr = lhs == binary_array_type
        wnnu__hjcfw = rhs == binary_array_type
        zfm__tnifv = 'lhs' if axko__calr else 'rhs'
        qeq__awyuo = 'def impl(lhs, rhs):\n'
        qeq__awyuo += '  numba.parfors.parfor.init_prange()\n'
        qeq__awyuo += f'  n = len({zfm__tnifv})\n'
        qeq__awyuo += (
            '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n)\n')
        qeq__awyuo += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        jmaud__ftxgg = []
        if axko__calr:
            jmaud__ftxgg.append('bodo.libs.array_kernels.isna(lhs, i)')
        if wnnu__hjcfw:
            jmaud__ftxgg.append('bodo.libs.array_kernels.isna(rhs, i)')
        qeq__awyuo += f"    if {' or '.join(jmaud__ftxgg)}:\n"
        qeq__awyuo += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        qeq__awyuo += '      continue\n'
        rgyt__ovdnu = 'lhs[i]' if axko__calr else 'lhs'
        ajc__deh = 'rhs[i]' if wnnu__hjcfw else 'rhs'
        qeq__awyuo += f'    out_arr[i] = op({rgyt__ovdnu}, {ajc__deh})\n'
        qeq__awyuo += '  return out_arr\n'
        wgec__zprh = {}
        exec(qeq__awyuo, {'bodo': bodo, 'numba': numba, 'op': op}, wgec__zprh)
        return wgec__zprh['impl']
    return overload_binary_cmp


class BinaryArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        fycw__hcft = 'iter(Bytes)'
        fzkfn__pdy = bytes_type
        super(BinaryArrayIterator, self).__init__(fycw__hcft, fzkfn__pdy)


@register_model(BinaryArrayIterator)
class BinaryArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wcv__xezwg = [('index', types.EphemeralPointer(types.uintp)), (
            'array', binary_array_type)]
        super(BinaryArrayIteratorModel, self).__init__(dmm, fe_type, wcv__xezwg
            )


lower_builtin('getiter', binary_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', BinaryArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_binary_array(context, builder, sig, args, result):
    [occ__btd] = sig.args
    [hppw__taux] = args
    yyzp__krz = context.make_helper(builder, occ__btd, value=hppw__taux)
    ouclf__gcdhl = signature(types.intp, binary_array_type)
    tupku__amr = context.compile_internal(builder, lambda a: len(a),
        ouclf__gcdhl, [yyzp__krz.array])
    yhua__fzxaj = builder.load(yyzp__krz.index)
    pmbn__pcfe = builder.icmp(lc.ICMP_SLT, yhua__fzxaj, tupku__amr)
    result.set_valid(pmbn__pcfe)
    with builder.if_then(pmbn__pcfe):
        oyrb__wzy = signature(bytes_type, binary_array_type, types.intp)
        symt__gui = context.compile_internal(builder, lambda a, i: a[i],
            oyrb__wzy, [yyzp__krz.array, yhua__fzxaj])
        result.yield_(symt__gui)
        fsj__lqi = cgutils.increment_index(builder, yhua__fzxaj)
        builder.store(fsj__lqi, yyzp__krz.index)


def pre_alloc_binary_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_binary_arr_ext_pre_alloc_binary_array
    ) = pre_alloc_binary_arr_equiv
