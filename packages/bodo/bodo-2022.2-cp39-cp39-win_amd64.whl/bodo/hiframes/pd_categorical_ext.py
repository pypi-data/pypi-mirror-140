import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        hmb__exbhv = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=hmb__exbhv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    voyqw__hgxcd = tuple(val.categories.values)
    elem_type = None if len(voyqw__hgxcd) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(voyqw__hgxcd, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        efwh__jzz = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, efwh__jzz)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    zerie__yaovy = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    uuuog__yfzp = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, fvgi__alae, fvgi__alae = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    setd__enspb = PDCategoricalDtype(uuuog__yfzp, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, zerie__yaovy)
    return setd__enspb(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sgj__syp = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, sgj__syp).value
    c.pyapi.decref(sgj__syp)
    fwbsh__phn = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, fwbsh__phn).value
    c.pyapi.decref(fwbsh__phn)
    usvbu__pmfb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=usvbu__pmfb)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    sgj__syp = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    mvfi__lkd = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c
        .env_manager)
    sps__omalq = c.context.insert_const_string(c.builder.module, 'pandas')
    zaa__xig = c.pyapi.import_module_noblock(sps__omalq)
    tdngk__oxpqu = c.pyapi.call_method(zaa__xig, 'CategoricalDtype', (
        mvfi__lkd, sgj__syp))
    c.pyapi.decref(sgj__syp)
    c.pyapi.decref(mvfi__lkd)
    c.pyapi.decref(zaa__xig)
    c.context.nrt.decref(c.builder, typ, val)
    return tdngk__oxpqu


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cea__xvh = get_categories_int_type(fe_type.dtype)
        efwh__jzz = [('dtype', fe_type.dtype), ('codes', types.Array(
            cea__xvh, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, efwh__jzz)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    cawv__stzp = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), cawv__stzp
        ).value
    c.pyapi.decref(cawv__stzp)
    tdngk__oxpqu = c.pyapi.object_getattr_string(val, 'dtype')
    izjk__xsvs = c.pyapi.to_native_value(typ.dtype, tdngk__oxpqu).value
    c.pyapi.decref(tdngk__oxpqu)
    pnyuf__sga = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pnyuf__sga.codes = codes
    pnyuf__sga.dtype = izjk__xsvs
    return NativeValue(pnyuf__sga._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    jkyl__txqzf = get_categories_int_type(typ.dtype)
    yrid__izj = context.get_constant_generic(builder, types.Array(
        jkyl__txqzf, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, yrid__izj])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    dohwt__ameme = len(cat_dtype.categories)
    if dohwt__ameme < np.iinfo(np.int8).max:
        dtype = types.int8
    elif dohwt__ameme < np.iinfo(np.int16).max:
        dtype = types.int16
    elif dohwt__ameme < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    sps__omalq = c.context.insert_const_string(c.builder.module, 'pandas')
    zaa__xig = c.pyapi.import_module_noblock(sps__omalq)
    cea__xvh = get_categories_int_type(dtype)
    dipv__fxob = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    oeg__equ = types.Array(cea__xvh, 1, 'C')
    c.context.nrt.incref(c.builder, oeg__equ, dipv__fxob.codes)
    cawv__stzp = c.pyapi.from_native_value(oeg__equ, dipv__fxob.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, dipv__fxob.dtype)
    tdngk__oxpqu = c.pyapi.from_native_value(dtype, dipv__fxob.dtype, c.
        env_manager)
    cri__zzk = c.pyapi.borrow_none()
    zxsqy__iwqfa = c.pyapi.object_getattr_string(zaa__xig, 'Categorical')
    oby__wepqh = c.pyapi.call_method(zxsqy__iwqfa, 'from_codes', (
        cawv__stzp, cri__zzk, cri__zzk, tdngk__oxpqu))
    c.pyapi.decref(zxsqy__iwqfa)
    c.pyapi.decref(cawv__stzp)
    c.pyapi.decref(tdngk__oxpqu)
    c.pyapi.decref(zaa__xig)
    c.context.nrt.decref(c.builder, typ, val)
    return oby__wepqh


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            irr__gumn = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                schl__vostb = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), irr__gumn)
                return schl__vostb
            return impl_lit

        def impl(A, other):
            irr__gumn = get_code_for_value(A.dtype, other)
            schl__vostb = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), irr__gumn)
            return schl__vostb
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        prric__nxx = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(prric__nxx)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    dipv__fxob = cat_dtype.categories
    n = len(dipv__fxob)
    for fvsu__ejyrt in range(n):
        if dipv__fxob[fvsu__ejyrt] == val:
            return fvsu__ejyrt
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    gccx__jceo = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype'
        )
    if gccx__jceo != A.dtype.elem_type and gccx__jceo != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if gccx__jceo == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            schl__vostb = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for fvsu__ejyrt in numba.parfors.parfor.internal_prange(n):
                mpjr__kqich = codes[fvsu__ejyrt]
                if mpjr__kqich == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            schl__vostb, fvsu__ejyrt)
                    else:
                        bodo.libs.array_kernels.setna(schl__vostb, fvsu__ejyrt)
                    continue
                schl__vostb[fvsu__ejyrt] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[mpjr__kqich]))
            return schl__vostb
        return impl
    oeg__equ = dtype_to_array_type(gccx__jceo)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        schl__vostb = bodo.utils.utils.alloc_type(n, oeg__equ, (-1,))
        for fvsu__ejyrt in numba.parfors.parfor.internal_prange(n):
            mpjr__kqich = codes[fvsu__ejyrt]
            if mpjr__kqich == -1:
                bodo.libs.array_kernels.setna(schl__vostb, fvsu__ejyrt)
                continue
            schl__vostb[fvsu__ejyrt
                ] = bodo.utils.conversion.unbox_if_timestamp(categories[
                mpjr__kqich])
        return schl__vostb
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        puc__fbwuu, izjk__xsvs = args
        dipv__fxob = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        dipv__fxob.codes = puc__fbwuu
        dipv__fxob.dtype = izjk__xsvs
        context.nrt.incref(builder, signature.args[0], puc__fbwuu)
        context.nrt.incref(builder, signature.args[1], izjk__xsvs)
        return dipv__fxob._getvalue()
    gwp__xhd = CategoricalArrayType(cat_dtype)
    sig = gwp__xhd(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    xnv__nynps = args[0]
    if equiv_set.has_shape(xnv__nynps):
        return ArrayAnalysis.AnalyzeResult(shape=xnv__nynps, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    cea__xvh = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, cea__xvh)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            kfizk__stfmf = {}
            yrid__izj = np.empty(n + 1, np.int64)
            dvlhg__rsww = {}
            udi__pzfy = []
            yihca__jjr = {}
            for fvsu__ejyrt in range(n):
                yihca__jjr[categories[fvsu__ejyrt]] = fvsu__ejyrt
            for jrimw__qfpsp in to_replace:
                if jrimw__qfpsp != value:
                    if jrimw__qfpsp in yihca__jjr:
                        if value in yihca__jjr:
                            kfizk__stfmf[jrimw__qfpsp] = jrimw__qfpsp
                            hrk__vxk = yihca__jjr[jrimw__qfpsp]
                            dvlhg__rsww[hrk__vxk] = yihca__jjr[value]
                            udi__pzfy.append(hrk__vxk)
                        else:
                            kfizk__stfmf[jrimw__qfpsp] = value
                            yihca__jjr[value] = yihca__jjr[jrimw__qfpsp]
            qtv__twxa = np.sort(np.array(udi__pzfy))
            centt__yba = 0
            lnk__qfth = []
            for mcxli__nzm in range(-1, n):
                while centt__yba < len(qtv__twxa) and mcxli__nzm > qtv__twxa[
                    centt__yba]:
                    centt__yba += 1
                lnk__qfth.append(centt__yba)
            for bdo__lcqm in range(-1, n):
                brihu__mee = bdo__lcqm
                if bdo__lcqm in dvlhg__rsww:
                    brihu__mee = dvlhg__rsww[bdo__lcqm]
                yrid__izj[bdo__lcqm + 1] = brihu__mee - lnk__qfth[
                    brihu__mee + 1]
            return kfizk__stfmf, yrid__izj, len(qtv__twxa)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for fvsu__ejyrt in range(len(new_codes_arr)):
        new_codes_arr[fvsu__ejyrt] = codes_map_arr[old_codes_arr[
            fvsu__ejyrt] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    ywil__btalv = arr.dtype.ordered
    ffxe__rqvha = arr.dtype.elem_type
    lfjau__flc = get_overload_const(to_replace)
    ybc__mam = get_overload_const(value)
    if (arr.dtype.categories is not None and lfjau__flc is not NOT_CONSTANT and
        ybc__mam is not NOT_CONSTANT):
        nknqf__zoz, codes_map_arr, fvgi__alae = python_build_replace_dicts(
            lfjau__flc, ybc__mam, arr.dtype.categories)
        if len(nknqf__zoz) == 0:
            return lambda arr, to_replace, value: arr.copy()
        oud__qgpp = []
        for sanb__nny in arr.dtype.categories:
            if sanb__nny in nknqf__zoz:
                ywt__odwyu = nknqf__zoz[sanb__nny]
                if ywt__odwyu != sanb__nny:
                    oud__qgpp.append(ywt__odwyu)
            else:
                oud__qgpp.append(sanb__nny)
        smbla__qmq = pd.CategoricalDtype(oud__qgpp, ywil__btalv
            ).categories.values
        zzsbm__amk = MetaType(tuple(smbla__qmq))

        def impl_dtype(arr, to_replace, value):
            clg__ayg = init_cat_dtype(bodo.utils.conversion.
                index_from_array(smbla__qmq), ywil__btalv, None, zzsbm__amk)
            dipv__fxob = alloc_categorical_array(len(arr.codes), clg__ayg)
            reassign_codes(dipv__fxob.codes, arr.codes, codes_map_arr)
            return dipv__fxob
        return impl_dtype
    ffxe__rqvha = arr.dtype.elem_type
    if ffxe__rqvha == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            kfizk__stfmf, codes_map_arr, dqkxg__cuiug = build_replace_dicts(
                to_replace, value, categories.values)
            if len(kfizk__stfmf) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), ywil__btalv,
                    None, None))
            n = len(categories)
            smbla__qmq = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                dqkxg__cuiug, -1)
            aqzk__xgl = 0
            for mcxli__nzm in range(n):
                qzw__bdx = categories[mcxli__nzm]
                if qzw__bdx in kfizk__stfmf:
                    xarfh__pgks = kfizk__stfmf[qzw__bdx]
                    if xarfh__pgks != qzw__bdx:
                        smbla__qmq[aqzk__xgl] = xarfh__pgks
                        aqzk__xgl += 1
                else:
                    smbla__qmq[aqzk__xgl] = qzw__bdx
                    aqzk__xgl += 1
            dipv__fxob = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                smbla__qmq), ywil__btalv, None, None))
            reassign_codes(dipv__fxob.codes, arr.codes, codes_map_arr)
            return dipv__fxob
        return impl_str
    wzg__ccvo = dtype_to_array_type(ffxe__rqvha)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        kfizk__stfmf, codes_map_arr, dqkxg__cuiug = build_replace_dicts(
            to_replace, value, categories.values)
        if len(kfizk__stfmf) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), ywil__btalv, None, None))
        n = len(categories)
        smbla__qmq = bodo.utils.utils.alloc_type(n - dqkxg__cuiug,
            wzg__ccvo, None)
        aqzk__xgl = 0
        for fvsu__ejyrt in range(n):
            qzw__bdx = categories[fvsu__ejyrt]
            if qzw__bdx in kfizk__stfmf:
                xarfh__pgks = kfizk__stfmf[qzw__bdx]
                if xarfh__pgks != qzw__bdx:
                    smbla__qmq[aqzk__xgl] = xarfh__pgks
                    aqzk__xgl += 1
            else:
                smbla__qmq[aqzk__xgl] = qzw__bdx
                aqzk__xgl += 1
        dipv__fxob = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(smbla__qmq),
            ywil__btalv, None, None))
        reassign_codes(dipv__fxob.codes, arr.codes, codes_map_arr)
        return dipv__fxob
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    ywdwf__nbwu = dict()
    ivy__esc = 0
    for fvsu__ejyrt in range(len(vals)):
        val = vals[fvsu__ejyrt]
        if val in ywdwf__nbwu:
            continue
        ywdwf__nbwu[val] = ivy__esc
        ivy__esc += 1
    return ywdwf__nbwu


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    ywdwf__nbwu = dict()
    for fvsu__ejyrt in range(len(vals)):
        val = vals[fvsu__ejyrt]
        ywdwf__nbwu[val] = fvsu__ejyrt
    return ywdwf__nbwu


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    lgh__bfui = dict(fastpath=fastpath)
    vxni__ahxix = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', lgh__bfui, vxni__ahxix)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        vbgv__gmgvi = get_overload_const(categories)
        if vbgv__gmgvi is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                gehc__aadmf = False
            else:
                gehc__aadmf = get_overload_const_bool(ordered)
            rqt__aobm = pd.CategoricalDtype(vbgv__gmgvi, gehc__aadmf
                ).categories.values
            glxlm__jkplw = MetaType(tuple(rqt__aobm))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                clg__ayg = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(rqt__aobm), gehc__aadmf, None,
                    glxlm__jkplw)
                return bodo.utils.conversion.fix_arr_dtype(data, clg__ayg)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            voyqw__hgxcd = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                voyqw__hgxcd, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            mdkp__ekyud = arr.codes[ind]
            return arr.dtype.categories[max(mdkp__ekyud, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for fvsu__ejyrt in range(len(arr1)):
        if arr1[fvsu__ejyrt] != arr2[fvsu__ejyrt]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    wtit__gmm = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    pla__awx = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    yoo__toxzp = categorical_arrs_match(arr, val)
    schyz__zcyw = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    hpy__drdjb = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not wtit__gmm:
            raise BodoError(schyz__zcyw)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            mdkp__ekyud = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = mdkp__ekyud
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (wtit__gmm or pla__awx or yoo__toxzp !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(schyz__zcyw)
        if yoo__toxzp == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hpy__drdjb)
        if wtit__gmm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                lvvm__rjab = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for mcxli__nzm in range(n):
                    arr.codes[ind[mcxli__nzm]] = lvvm__rjab
            return impl_scalar
        if yoo__toxzp == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for fvsu__ejyrt in range(n):
                    arr.codes[ind[fvsu__ejyrt]] = val.codes[fvsu__ejyrt]
            return impl_arr_ind_mask
        if yoo__toxzp == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hpy__drdjb)
                n = len(val.codes)
                for fvsu__ejyrt in range(n):
                    arr.codes[ind[fvsu__ejyrt]] = val.codes[fvsu__ejyrt]
            return impl_arr_ind_mask
        if pla__awx:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for mcxli__nzm in range(n):
                    qcck__ekyz = bodo.utils.conversion.unbox_if_timestamp(val
                        [mcxli__nzm])
                    if qcck__ekyz not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    mdkp__ekyud = categories.get_loc(qcck__ekyz)
                    arr.codes[ind[mcxli__nzm]] = mdkp__ekyud
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (wtit__gmm or pla__awx or yoo__toxzp !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(schyz__zcyw)
        if yoo__toxzp == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hpy__drdjb)
        if wtit__gmm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                lvvm__rjab = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for mcxli__nzm in range(n):
                    if ind[mcxli__nzm]:
                        arr.codes[mcxli__nzm] = lvvm__rjab
            return impl_scalar
        if yoo__toxzp == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                pjl__lkth = 0
                for fvsu__ejyrt in range(n):
                    if ind[fvsu__ejyrt]:
                        arr.codes[fvsu__ejyrt] = val.codes[pjl__lkth]
                        pjl__lkth += 1
            return impl_bool_ind_mask
        if yoo__toxzp == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hpy__drdjb)
                n = len(ind)
                pjl__lkth = 0
                for fvsu__ejyrt in range(n):
                    if ind[fvsu__ejyrt]:
                        arr.codes[fvsu__ejyrt] = val.codes[pjl__lkth]
                        pjl__lkth += 1
            return impl_bool_ind_mask
        if pla__awx:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                pjl__lkth = 0
                categories = arr.dtype.categories
                for mcxli__nzm in range(n):
                    if ind[mcxli__nzm]:
                        qcck__ekyz = bodo.utils.conversion.unbox_if_timestamp(
                            val[pjl__lkth])
                        if qcck__ekyz not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        mdkp__ekyud = categories.get_loc(qcck__ekyz)
                        arr.codes[mcxli__nzm] = mdkp__ekyud
                        pjl__lkth += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (wtit__gmm or pla__awx or yoo__toxzp !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(schyz__zcyw)
        if yoo__toxzp == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(hpy__drdjb)
        if wtit__gmm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                lvvm__rjab = arr.dtype.categories.get_loc(val)
                lsw__pgqr = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for mcxli__nzm in range(lsw__pgqr.start, lsw__pgqr.stop,
                    lsw__pgqr.step):
                    arr.codes[mcxli__nzm] = lvvm__rjab
            return impl_scalar
        if yoo__toxzp == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if yoo__toxzp == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(hpy__drdjb)
                arr.codes[ind] = val.codes
            return impl_arr
        if pla__awx:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                lsw__pgqr = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                pjl__lkth = 0
                for mcxli__nzm in range(lsw__pgqr.start, lsw__pgqr.stop,
                    lsw__pgqr.step):
                    qcck__ekyz = bodo.utils.conversion.unbox_if_timestamp(val
                        [pjl__lkth])
                    if qcck__ekyz not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    mdkp__ekyud = categories.get_loc(qcck__ekyz)
                    arr.codes[mcxli__nzm] = mdkp__ekyud
                    pjl__lkth += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
