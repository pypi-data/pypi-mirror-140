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
        qpvah__aru = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, qpvah__aru)


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
        rdav__ytc, koke__orrly = args
        goki__esxr = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        goki__esxr.left = rdav__ytc
        goki__esxr.right = koke__orrly
        context.nrt.incref(builder, signature.args[0], rdav__ytc)
        context.nrt.incref(builder, signature.args[1], koke__orrly)
        return goki__esxr._getvalue()
    mhqcc__viyc = IntervalArrayType(left)
    ldx__lwrw = mhqcc__viyc(left, right)
    return ldx__lwrw, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    cmwfq__vvrq = []
    for ptyc__jxyq in args:
        cnjn__jlzun = equiv_set.get_shape(ptyc__jxyq)
        if cnjn__jlzun is not None:
            cmwfq__vvrq.append(cnjn__jlzun[0])
    if len(cmwfq__vvrq) > 1:
        equiv_set.insert_equiv(*cmwfq__vvrq)
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
    goki__esxr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, goki__esxr.left)
    yzn__esrpf = c.pyapi.from_native_value(typ.arr_type, goki__esxr.left, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, goki__esxr.right)
    racd__siu = c.pyapi.from_native_value(typ.arr_type, goki__esxr.right, c
        .env_manager)
    tdvq__cvrxs = c.context.insert_const_string(c.builder.module, 'pandas')
    yesx__pnh = c.pyapi.import_module_noblock(tdvq__cvrxs)
    pksch__qrp = c.pyapi.object_getattr_string(yesx__pnh, 'arrays')
    hsi__xkz = c.pyapi.object_getattr_string(pksch__qrp, 'IntervalArray')
    bbt__vve = c.pyapi.call_method(hsi__xkz, 'from_arrays', (yzn__esrpf,
        racd__siu))
    c.pyapi.decref(yzn__esrpf)
    c.pyapi.decref(racd__siu)
    c.pyapi.decref(yesx__pnh)
    c.pyapi.decref(pksch__qrp)
    c.pyapi.decref(hsi__xkz)
    c.context.nrt.decref(c.builder, typ, val)
    return bbt__vve


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    yzn__esrpf = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, yzn__esrpf).value
    c.pyapi.decref(yzn__esrpf)
    racd__siu = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, racd__siu).value
    c.pyapi.decref(racd__siu)
    goki__esxr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    goki__esxr.left = left
    goki__esxr.right = right
    tnl__xhe = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(goki__esxr._getvalue(), is_error=tnl__xhe)


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
