"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vkudn__debi = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, vkudn__debi)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        kri__fckwe, nbki__wam = args
        nole__zvhsb = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        nole__zvhsb.left = kri__fckwe
        nole__zvhsb.right = nbki__wam
        context.nrt.incref(builder, signature.args[0], kri__fckwe)
        context.nrt.incref(builder, signature.args[1], nbki__wam)
        return nole__zvhsb._getvalue()
    tifco__vaew = IntervalArrayType(left)
    xxlc__dmwyj = tifco__vaew(left, right)
    return xxlc__dmwyj, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    pbx__zirv = []
    for dxta__xxs in args:
        nzuv__ecuey = equiv_set.get_shape(dxta__xxs)
        if nzuv__ecuey is not None:
            pbx__zirv.append(nzuv__ecuey[0])
    if len(pbx__zirv) > 1:
        equiv_set.insert_equiv(*pbx__zirv)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    nole__zvhsb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, nole__zvhsb.left)
    gvuwn__lbin = c.pyapi.from_native_value(typ.arr_type, nole__zvhsb.left,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, nole__zvhsb.right)
    nqjq__pvmi = c.pyapi.from_native_value(typ.arr_type, nole__zvhsb.right,
        c.env_manager)
    jvncz__qirx = c.context.insert_const_string(c.builder.module, 'pandas')
    wpx__yrk = c.pyapi.import_module_noblock(jvncz__qirx)
    wmfp__ddfh = c.pyapi.object_getattr_string(wpx__yrk, 'arrays')
    vdv__jfrll = c.pyapi.object_getattr_string(wmfp__ddfh, 'IntervalArray')
    vpq__sst = c.pyapi.call_method(vdv__jfrll, 'from_arrays', (gvuwn__lbin,
        nqjq__pvmi))
    c.pyapi.decref(gvuwn__lbin)
    c.pyapi.decref(nqjq__pvmi)
    c.pyapi.decref(wpx__yrk)
    c.pyapi.decref(wmfp__ddfh)
    c.pyapi.decref(vdv__jfrll)
    c.context.nrt.decref(c.builder, typ, val)
    return vpq__sst


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    gvuwn__lbin = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, gvuwn__lbin).value
    c.pyapi.decref(gvuwn__lbin)
    nqjq__pvmi = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, nqjq__pvmi).value
    c.pyapi.decref(nqjq__pvmi)
    nole__zvhsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nole__zvhsb.left = left
    nole__zvhsb.right = right
    ihe__husqp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nole__zvhsb._getvalue(), is_error=ihe__husqp)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
