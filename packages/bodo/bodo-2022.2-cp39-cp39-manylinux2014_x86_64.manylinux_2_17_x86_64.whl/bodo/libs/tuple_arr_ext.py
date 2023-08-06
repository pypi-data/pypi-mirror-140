"""Array of tuple values, implemented by reusing array of structs implementation.
"""
import operator
import numba
import numpy as np
from numba.core import types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.struct_arr_ext import StructArrayType, box_struct_arr, unbox_struct_array


class TupleArrayType(types.ArrayCompatible):

    def __init__(self, data):
        self.data = data
        super(TupleArrayType, self).__init__(name='TupleArrayType({})'.
            format(data))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.BaseTuple.from_types(tuple(zqs__tisrv.dtype for
            zqs__tisrv in self.data))

    def copy(self):
        return TupleArrayType(self.data)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(TupleArrayType)
class TupleArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hdno__okb = [('data', StructArrayType(fe_type.data))]
        models.StructModel.__init__(self, dmm, fe_type, hdno__okb)


make_attribute_wrapper(TupleArrayType, 'data', '_data')


@intrinsic
def init_tuple_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, StructArrayType)
    auu__fscui = TupleArrayType(data_typ.data)

    def codegen(context, builder, sig, args):
        uhwa__yqt, = args
        bsv__mqxzz = context.make_helper(builder, auu__fscui)
        bsv__mqxzz.data = uhwa__yqt
        context.nrt.incref(builder, data_typ, uhwa__yqt)
        return bsv__mqxzz._getvalue()
    return auu__fscui(data_typ), codegen


@unbox(TupleArrayType)
def unbox_tuple_array(typ, val, c):
    data_typ = StructArrayType(typ.data)
    olve__jfdov = unbox_struct_array(data_typ, val, c, is_tuple_array=True)
    uhwa__yqt = olve__jfdov.value
    bsv__mqxzz = c.context.make_helper(c.builder, typ)
    bsv__mqxzz.data = uhwa__yqt
    iexnx__qbwd = olve__jfdov.is_error
    return NativeValue(bsv__mqxzz._getvalue(), is_error=iexnx__qbwd)


@box(TupleArrayType)
def box_tuple_arr(typ, val, c):
    data_typ = StructArrayType(typ.data)
    bsv__mqxzz = c.context.make_helper(c.builder, typ, val)
    arr = box_struct_arr(data_typ, bsv__mqxzz.data, c, is_tuple_array=True)
    return arr


@numba.njit
def pre_alloc_tuple_array(n, nested_counts, dtypes):
    return init_tuple_arr(bodo.libs.struct_arr_ext.pre_alloc_struct_array(n,
        nested_counts, dtypes, None))


def pre_alloc_tuple_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_tuple_arr_ext_pre_alloc_tuple_array
    ) = pre_alloc_tuple_array_equiv


@overload(operator.getitem, no_unliteral=True)
def tuple_arr_getitem(arr, ind):
    if not isinstance(arr, TupleArrayType):
        return
    if isinstance(ind, types.Integer):
        ajadj__gnuk = 'def impl(arr, ind):\n'
        lwh__swqu = ','.join(f'get_data(arr._data)[{djhyp__kzm}][ind]' for
            djhyp__kzm in range(len(arr.data)))
        ajadj__gnuk += f'  return ({lwh__swqu})\n'
        spme__dius = {}
        exec(ajadj__gnuk, {'get_data': bodo.libs.struct_arr_ext.get_data},
            spme__dius)
        rby__fqv = spme__dius['impl']
        return rby__fqv

    def impl_arr(arr, ind):
        return init_tuple_arr(arr._data[ind])
    return impl_arr


@overload(operator.setitem, no_unliteral=True)
def tuple_arr_setitem(arr, ind, val):
    if not isinstance(arr, TupleArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        esnz__ugbey = len(arr.data)
        ajadj__gnuk = 'def impl(arr, ind, val):\n'
        ajadj__gnuk += '  data = get_data(arr._data)\n'
        ajadj__gnuk += '  null_bitmap = get_null_bitmap(arr._data)\n'
        ajadj__gnuk += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for djhyp__kzm in range(esnz__ugbey):
            ajadj__gnuk += f'  data[{djhyp__kzm}][ind] = val[{djhyp__kzm}]\n'
        spme__dius = {}
        exec(ajadj__gnuk, {'get_data': bodo.libs.struct_arr_ext.get_data,
            'get_null_bitmap': bodo.libs.struct_arr_ext.get_null_bitmap,
            'set_bit_to_arr': bodo.libs.int_arr_ext.set_bit_to_arr}, spme__dius
            )
        rby__fqv = spme__dius['impl']
        return rby__fqv

    def impl_arr(arr, ind, val):
        val = bodo.utils.conversion.coerce_to_array(val, use_nullable_array
            =True)
        arr._data[ind] = val._data
    return impl_arr


@overload(len, no_unliteral=True)
def overload_tuple_arr_len(A):
    if isinstance(A, TupleArrayType):
        return lambda A: len(A._data)


@overload_attribute(TupleArrayType, 'shape')
def overload_tuple_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(TupleArrayType, 'dtype')
def overload_tuple_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(TupleArrayType, 'ndim')
def overload_tuple_arr_ndim(A):
    return lambda A: 1


@overload_attribute(TupleArrayType, 'nbytes')
def overload_tuple_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(TupleArrayType, 'copy', no_unliteral=True)
def overload_tuple_arr_copy(A):

    def copy_impl(A):
        return init_tuple_arr(A._data.copy())
    return copy_impl
