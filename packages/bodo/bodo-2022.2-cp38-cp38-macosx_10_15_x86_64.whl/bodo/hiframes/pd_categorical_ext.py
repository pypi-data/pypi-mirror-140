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
        atw__vwjtc = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=atw__vwjtc)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    teuk__awbg = tuple(val.categories.values)
    elem_type = None if len(teuk__awbg) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(teuk__awbg, elem_type, val.ordered, bodo.
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
        lbh__xbppd = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, lbh__xbppd)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    lvf__gexi = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    jtbq__ozmx = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, eiwpy__lknxl, eiwpy__lknxl = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    gtrnz__rsxhx = PDCategoricalDtype(jtbq__ozmx, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, lvf__gexi)
    return gtrnz__rsxhx(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lmrz__fis = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, lmrz__fis).value
    c.pyapi.decref(lmrz__fis)
    luf__zkbo = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, luf__zkbo).value
    c.pyapi.decref(luf__zkbo)
    jwxx__sodlw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=jwxx__sodlw)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    lmrz__fis = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    bsba__dbifx = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    cpn__kojpm = c.context.insert_const_string(c.builder.module, 'pandas')
    evk__dtwyg = c.pyapi.import_module_noblock(cpn__kojpm)
    yntyu__gms = c.pyapi.call_method(evk__dtwyg, 'CategoricalDtype', (
        bsba__dbifx, lmrz__fis))
    c.pyapi.decref(lmrz__fis)
    c.pyapi.decref(bsba__dbifx)
    c.pyapi.decref(evk__dtwyg)
    c.context.nrt.decref(c.builder, typ, val)
    return yntyu__gms


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
        mry__vxnnk = get_categories_int_type(fe_type.dtype)
        lbh__xbppd = [('dtype', fe_type.dtype), ('codes', types.Array(
            mry__vxnnk, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, lbh__xbppd)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    kqpq__vovit = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), kqpq__vovit
        ).value
    c.pyapi.decref(kqpq__vovit)
    yntyu__gms = c.pyapi.object_getattr_string(val, 'dtype')
    ucxc__rerqq = c.pyapi.to_native_value(typ.dtype, yntyu__gms).value
    c.pyapi.decref(yntyu__gms)
    fvgt__zzfjw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fvgt__zzfjw.codes = codes
    fvgt__zzfjw.dtype = ucxc__rerqq
    return NativeValue(fvgt__zzfjw._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    tknx__txyj = get_categories_int_type(typ.dtype)
    ukneq__edror = context.get_constant_generic(builder, types.Array(
        tknx__txyj, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, ukneq__edror])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    rwch__mysf = len(cat_dtype.categories)
    if rwch__mysf < np.iinfo(np.int8).max:
        dtype = types.int8
    elif rwch__mysf < np.iinfo(np.int16).max:
        dtype = types.int16
    elif rwch__mysf < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    cpn__kojpm = c.context.insert_const_string(c.builder.module, 'pandas')
    evk__dtwyg = c.pyapi.import_module_noblock(cpn__kojpm)
    mry__vxnnk = get_categories_int_type(dtype)
    dltbl__ivuqq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    hbm__sqge = types.Array(mry__vxnnk, 1, 'C')
    c.context.nrt.incref(c.builder, hbm__sqge, dltbl__ivuqq.codes)
    kqpq__vovit = c.pyapi.from_native_value(hbm__sqge, dltbl__ivuqq.codes,
        c.env_manager)
    c.context.nrt.incref(c.builder, dtype, dltbl__ivuqq.dtype)
    yntyu__gms = c.pyapi.from_native_value(dtype, dltbl__ivuqq.dtype, c.
        env_manager)
    uqzi__upt = c.pyapi.borrow_none()
    qoqka__mfll = c.pyapi.object_getattr_string(evk__dtwyg, 'Categorical')
    uckii__ccg = c.pyapi.call_method(qoqka__mfll, 'from_codes', (
        kqpq__vovit, uqzi__upt, uqzi__upt, yntyu__gms))
    c.pyapi.decref(qoqka__mfll)
    c.pyapi.decref(kqpq__vovit)
    c.pyapi.decref(yntyu__gms)
    c.pyapi.decref(evk__dtwyg)
    c.context.nrt.decref(c.builder, typ, val)
    return uckii__ccg


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
            woksk__dowf = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                cufkw__zsqlr = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), woksk__dowf)
                return cufkw__zsqlr
            return impl_lit

        def impl(A, other):
            woksk__dowf = get_code_for_value(A.dtype, other)
            cufkw__zsqlr = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), woksk__dowf)
            return cufkw__zsqlr
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        mdrjm__zzat = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(mdrjm__zzat)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    dltbl__ivuqq = cat_dtype.categories
    n = len(dltbl__ivuqq)
    for nixi__zcfa in range(n):
        if dltbl__ivuqq[nixi__zcfa] == val:
            return nixi__zcfa
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    madbg__sdmez = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (madbg__sdmez != A.dtype.elem_type and madbg__sdmez != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if madbg__sdmez == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            cufkw__zsqlr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for nixi__zcfa in numba.parfors.parfor.internal_prange(n):
                hsuq__gqxgp = codes[nixi__zcfa]
                if hsuq__gqxgp == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            cufkw__zsqlr, nixi__zcfa)
                    else:
                        bodo.libs.array_kernels.setna(cufkw__zsqlr, nixi__zcfa)
                    continue
                cufkw__zsqlr[nixi__zcfa] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[hsuq__gqxgp]))
            return cufkw__zsqlr
        return impl
    hbm__sqge = dtype_to_array_type(madbg__sdmez)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        cufkw__zsqlr = bodo.utils.utils.alloc_type(n, hbm__sqge, (-1,))
        for nixi__zcfa in numba.parfors.parfor.internal_prange(n):
            hsuq__gqxgp = codes[nixi__zcfa]
            if hsuq__gqxgp == -1:
                bodo.libs.array_kernels.setna(cufkw__zsqlr, nixi__zcfa)
                continue
            cufkw__zsqlr[nixi__zcfa
                ] = bodo.utils.conversion.unbox_if_timestamp(categories[
                hsuq__gqxgp])
        return cufkw__zsqlr
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        bllqk__xea, ucxc__rerqq = args
        dltbl__ivuqq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        dltbl__ivuqq.codes = bllqk__xea
        dltbl__ivuqq.dtype = ucxc__rerqq
        context.nrt.incref(builder, signature.args[0], bllqk__xea)
        context.nrt.incref(builder, signature.args[1], ucxc__rerqq)
        return dltbl__ivuqq._getvalue()
    koh__enfnp = CategoricalArrayType(cat_dtype)
    sig = koh__enfnp(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    eod__nwu = args[0]
    if equiv_set.has_shape(eod__nwu):
        return ArrayAnalysis.AnalyzeResult(shape=eod__nwu, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    mry__vxnnk = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, mry__vxnnk)
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
            anh__azhb = {}
            ukneq__edror = np.empty(n + 1, np.int64)
            akrnj__iuao = {}
            uenn__wbud = []
            jox__lzgd = {}
            for nixi__zcfa in range(n):
                jox__lzgd[categories[nixi__zcfa]] = nixi__zcfa
            for nri__igrm in to_replace:
                if nri__igrm != value:
                    if nri__igrm in jox__lzgd:
                        if value in jox__lzgd:
                            anh__azhb[nri__igrm] = nri__igrm
                            stag__rim = jox__lzgd[nri__igrm]
                            akrnj__iuao[stag__rim] = jox__lzgd[value]
                            uenn__wbud.append(stag__rim)
                        else:
                            anh__azhb[nri__igrm] = value
                            jox__lzgd[value] = jox__lzgd[nri__igrm]
            ald__aiil = np.sort(np.array(uenn__wbud))
            rcabf__insw = 0
            rwfw__iaowl = []
            for ztt__uple in range(-1, n):
                while rcabf__insw < len(ald__aiil) and ztt__uple > ald__aiil[
                    rcabf__insw]:
                    rcabf__insw += 1
                rwfw__iaowl.append(rcabf__insw)
            for maqlt__gob in range(-1, n):
                lsj__lsfbh = maqlt__gob
                if maqlt__gob in akrnj__iuao:
                    lsj__lsfbh = akrnj__iuao[maqlt__gob]
                ukneq__edror[maqlt__gob + 1] = lsj__lsfbh - rwfw__iaowl[
                    lsj__lsfbh + 1]
            return anh__azhb, ukneq__edror, len(ald__aiil)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for nixi__zcfa in range(len(new_codes_arr)):
        new_codes_arr[nixi__zcfa] = codes_map_arr[old_codes_arr[nixi__zcfa] + 1
            ]


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
    exe__qud = arr.dtype.ordered
    ewijz__thh = arr.dtype.elem_type
    ddk__lfbsl = get_overload_const(to_replace)
    ccu__rob = get_overload_const(value)
    if (arr.dtype.categories is not None and ddk__lfbsl is not NOT_CONSTANT and
        ccu__rob is not NOT_CONSTANT):
        lmwni__tptfn, codes_map_arr, eiwpy__lknxl = python_build_replace_dicts(
            ddk__lfbsl, ccu__rob, arr.dtype.categories)
        if len(lmwni__tptfn) == 0:
            return lambda arr, to_replace, value: arr.copy()
        ibkhp__meblg = []
        for joapz__noow in arr.dtype.categories:
            if joapz__noow in lmwni__tptfn:
                wgydv__mbhr = lmwni__tptfn[joapz__noow]
                if wgydv__mbhr != joapz__noow:
                    ibkhp__meblg.append(wgydv__mbhr)
            else:
                ibkhp__meblg.append(joapz__noow)
        wtqjw__epo = pd.CategoricalDtype(ibkhp__meblg, exe__qud
            ).categories.values
        zevk__scntl = MetaType(tuple(wtqjw__epo))

        def impl_dtype(arr, to_replace, value):
            tidl__jzcc = init_cat_dtype(bodo.utils.conversion.
                index_from_array(wtqjw__epo), exe__qud, None, zevk__scntl)
            dltbl__ivuqq = alloc_categorical_array(len(arr.codes), tidl__jzcc)
            reassign_codes(dltbl__ivuqq.codes, arr.codes, codes_map_arr)
            return dltbl__ivuqq
        return impl_dtype
    ewijz__thh = arr.dtype.elem_type
    if ewijz__thh == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            anh__azhb, codes_map_arr, ddfhk__wrp = build_replace_dicts(
                to_replace, value, categories.values)
            if len(anh__azhb) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), exe__qud,
                    None, None))
            n = len(categories)
            wtqjw__epo = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                ddfhk__wrp, -1)
            auab__bqg = 0
            for ztt__uple in range(n):
                jvz__tcbj = categories[ztt__uple]
                if jvz__tcbj in anh__azhb:
                    ulvwb__wxzm = anh__azhb[jvz__tcbj]
                    if ulvwb__wxzm != jvz__tcbj:
                        wtqjw__epo[auab__bqg] = ulvwb__wxzm
                        auab__bqg += 1
                else:
                    wtqjw__epo[auab__bqg] = jvz__tcbj
                    auab__bqg += 1
            dltbl__ivuqq = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                wtqjw__epo), exe__qud, None, None))
            reassign_codes(dltbl__ivuqq.codes, arr.codes, codes_map_arr)
            return dltbl__ivuqq
        return impl_str
    zeb__doaev = dtype_to_array_type(ewijz__thh)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        anh__azhb, codes_map_arr, ddfhk__wrp = build_replace_dicts(to_replace,
            value, categories.values)
        if len(anh__azhb) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), exe__qud, None, None))
        n = len(categories)
        wtqjw__epo = bodo.utils.utils.alloc_type(n - ddfhk__wrp, zeb__doaev,
            None)
        auab__bqg = 0
        for nixi__zcfa in range(n):
            jvz__tcbj = categories[nixi__zcfa]
            if jvz__tcbj in anh__azhb:
                ulvwb__wxzm = anh__azhb[jvz__tcbj]
                if ulvwb__wxzm != jvz__tcbj:
                    wtqjw__epo[auab__bqg] = ulvwb__wxzm
                    auab__bqg += 1
            else:
                wtqjw__epo[auab__bqg] = jvz__tcbj
                auab__bqg += 1
        dltbl__ivuqq = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            wtqjw__epo), exe__qud, None, None))
        reassign_codes(dltbl__ivuqq.codes, arr.codes, codes_map_arr)
        return dltbl__ivuqq
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
    vuv__osbu = dict()
    upg__hpiwy = 0
    for nixi__zcfa in range(len(vals)):
        val = vals[nixi__zcfa]
        if val in vuv__osbu:
            continue
        vuv__osbu[val] = upg__hpiwy
        upg__hpiwy += 1
    return vuv__osbu


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    vuv__osbu = dict()
    for nixi__zcfa in range(len(vals)):
        val = vals[nixi__zcfa]
        vuv__osbu[val] = nixi__zcfa
    return vuv__osbu


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    ybb__iikzd = dict(fastpath=fastpath)
    hymae__kwziv = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', ybb__iikzd, hymae__kwziv)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        zbnt__ysae = get_overload_const(categories)
        if zbnt__ysae is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                bixzj__jklm = False
            else:
                bixzj__jklm = get_overload_const_bool(ordered)
            kjwj__fgu = pd.CategoricalDtype(zbnt__ysae, bixzj__jklm
                ).categories.values
            uazup__uzfw = MetaType(tuple(kjwj__fgu))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                tidl__jzcc = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(kjwj__fgu), bixzj__jklm, None, uazup__uzfw
                    )
                return bodo.utils.conversion.fix_arr_dtype(data, tidl__jzcc)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            teuk__awbg = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                teuk__awbg, ordered, None, None)
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
            fea__skv = arr.codes[ind]
            return arr.dtype.categories[max(fea__skv, 0)]
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
    for nixi__zcfa in range(len(arr1)):
        if arr1[nixi__zcfa] != arr2[nixi__zcfa]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ethf__gbc = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    eug__vrid = not isinstance(val, CategoricalArrayType) and is_iterable_type(
        val) and is_common_scalar_dtype([val.dtype, arr.dtype.elem_type]
        ) and not (isinstance(arr.dtype.elem_type, types.Integer) and
        isinstance(val.dtype, types.Float))
    qrzk__cffc = categorical_arrs_match(arr, val)
    stw__dijk = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    stnda__knox = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not ethf__gbc:
            raise BodoError(stw__dijk)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            fea__skv = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = fea__skv
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (ethf__gbc or eug__vrid or qrzk__cffc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(stw__dijk)
        if qrzk__cffc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(stnda__knox)
        if ethf__gbc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ozoq__slg = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for ztt__uple in range(n):
                    arr.codes[ind[ztt__uple]] = ozoq__slg
            return impl_scalar
        if qrzk__cffc == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for nixi__zcfa in range(n):
                    arr.codes[ind[nixi__zcfa]] = val.codes[nixi__zcfa]
            return impl_arr_ind_mask
        if qrzk__cffc == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(stnda__knox)
                n = len(val.codes)
                for nixi__zcfa in range(n):
                    arr.codes[ind[nixi__zcfa]] = val.codes[nixi__zcfa]
            return impl_arr_ind_mask
        if eug__vrid:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for ztt__uple in range(n):
                    tmz__qij = bodo.utils.conversion.unbox_if_timestamp(val
                        [ztt__uple])
                    if tmz__qij not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    fea__skv = categories.get_loc(tmz__qij)
                    arr.codes[ind[ztt__uple]] = fea__skv
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (ethf__gbc or eug__vrid or qrzk__cffc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(stw__dijk)
        if qrzk__cffc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(stnda__knox)
        if ethf__gbc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ozoq__slg = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for ztt__uple in range(n):
                    if ind[ztt__uple]:
                        arr.codes[ztt__uple] = ozoq__slg
            return impl_scalar
        if qrzk__cffc == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                qiz__gjy = 0
                for nixi__zcfa in range(n):
                    if ind[nixi__zcfa]:
                        arr.codes[nixi__zcfa] = val.codes[qiz__gjy]
                        qiz__gjy += 1
            return impl_bool_ind_mask
        if qrzk__cffc == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(stnda__knox)
                n = len(ind)
                qiz__gjy = 0
                for nixi__zcfa in range(n):
                    if ind[nixi__zcfa]:
                        arr.codes[nixi__zcfa] = val.codes[qiz__gjy]
                        qiz__gjy += 1
            return impl_bool_ind_mask
        if eug__vrid:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                qiz__gjy = 0
                categories = arr.dtype.categories
                for ztt__uple in range(n):
                    if ind[ztt__uple]:
                        tmz__qij = bodo.utils.conversion.unbox_if_timestamp(val
                            [qiz__gjy])
                        if tmz__qij not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        fea__skv = categories.get_loc(tmz__qij)
                        arr.codes[ztt__uple] = fea__skv
                        qiz__gjy += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (ethf__gbc or eug__vrid or qrzk__cffc !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(stw__dijk)
        if qrzk__cffc == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(stnda__knox)
        if ethf__gbc:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ozoq__slg = arr.dtype.categories.get_loc(val)
                xyz__qfaty = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for ztt__uple in range(xyz__qfaty.start, xyz__qfaty.stop,
                    xyz__qfaty.step):
                    arr.codes[ztt__uple] = ozoq__slg
            return impl_scalar
        if qrzk__cffc == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if qrzk__cffc == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(stnda__knox)
                arr.codes[ind] = val.codes
            return impl_arr
        if eug__vrid:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                xyz__qfaty = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                qiz__gjy = 0
                for ztt__uple in range(xyz__qfaty.start, xyz__qfaty.stop,
                    xyz__qfaty.step):
                    tmz__qij = bodo.utils.conversion.unbox_if_timestamp(val
                        [qiz__gjy])
                    if tmz__qij not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    fea__skv = categories.get_loc(tmz__qij)
                    arr.codes[ztt__uple] = fea__skv
                    qiz__gjy += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
