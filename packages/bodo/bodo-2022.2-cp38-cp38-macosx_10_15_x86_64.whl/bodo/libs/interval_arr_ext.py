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
        sgafp__yrmsb = [('left', fe_type.arr_type), ('right', fe_type.arr_type)
            ]
        models.StructModel.__init__(self, dmm, fe_type, sgafp__yrmsb)


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
        hinn__nvxv, qywz__eqzj = args
        ewepd__lsv = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        ewepd__lsv.left = hinn__nvxv
        ewepd__lsv.right = qywz__eqzj
        context.nrt.incref(builder, signature.args[0], hinn__nvxv)
        context.nrt.incref(builder, signature.args[1], qywz__eqzj)
        return ewepd__lsv._getvalue()
    ernh__nmj = IntervalArrayType(left)
    rfm__mhv = ernh__nmj(left, right)
    return rfm__mhv, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zth__aezc = []
    for tuzbx__nhhc in args:
        dgdo__bpocn = equiv_set.get_shape(tuzbx__nhhc)
        if dgdo__bpocn is not None:
            zth__aezc.append(dgdo__bpocn[0])
    if len(zth__aezc) > 1:
        equiv_set.insert_equiv(*zth__aezc)
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
    ewepd__lsv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, ewepd__lsv.left)
    jbyx__hdiv = c.pyapi.from_native_value(typ.arr_type, ewepd__lsv.left, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, ewepd__lsv.right)
    ylada__loem = c.pyapi.from_native_value(typ.arr_type, ewepd__lsv.right,
        c.env_manager)
    cfd__yxtrt = c.context.insert_const_string(c.builder.module, 'pandas')
    trvif__txeol = c.pyapi.import_module_noblock(cfd__yxtrt)
    hghp__ipgd = c.pyapi.object_getattr_string(trvif__txeol, 'arrays')
    qty__rmiqi = c.pyapi.object_getattr_string(hghp__ipgd, 'IntervalArray')
    hyrfy__xuu = c.pyapi.call_method(qty__rmiqi, 'from_arrays', (jbyx__hdiv,
        ylada__loem))
    c.pyapi.decref(jbyx__hdiv)
    c.pyapi.decref(ylada__loem)
    c.pyapi.decref(trvif__txeol)
    c.pyapi.decref(hghp__ipgd)
    c.pyapi.decref(qty__rmiqi)
    c.context.nrt.decref(c.builder, typ, val)
    return hyrfy__xuu


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    jbyx__hdiv = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, jbyx__hdiv).value
    c.pyapi.decref(jbyx__hdiv)
    ylada__loem = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, ylada__loem).value
    c.pyapi.decref(ylada__loem)
    ewepd__lsv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ewepd__lsv.left = left
    ewepd__lsv.right = right
    nzrk__fumwe = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ewepd__lsv._getvalue(), is_error=nzrk__fumwe)


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
