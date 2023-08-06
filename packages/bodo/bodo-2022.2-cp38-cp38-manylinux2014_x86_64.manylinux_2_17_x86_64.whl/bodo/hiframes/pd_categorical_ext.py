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
        jul__jsio = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=jul__jsio)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    rgej__jsi = tuple(val.categories.values)
    elem_type = None if len(rgej__jsi) == 0 else bodo.typeof(val.categories
        .values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(rgej__jsi, elem_type, val.ordered, bodo.
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
        nulp__yrv = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, nulp__yrv)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    zjhmr__soot = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    fruzr__qvmfe = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, idc__vrxgb, idc__vrxgb = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    flxed__kdrly = PDCategoricalDtype(fruzr__qvmfe, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, zjhmr__soot)
    return flxed__kdrly(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jwoj__kivca = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, jwoj__kivca).value
    c.pyapi.decref(jwoj__kivca)
    ovfj__nwnc = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, ovfj__nwnc).value
    c.pyapi.decref(ovfj__nwnc)
    wzkvk__ufm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=wzkvk__ufm)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    jwoj__kivca = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    aytr__trk = c.pyapi.from_native_value(typ.data, cat_dtype.categories, c
        .env_manager)
    bsmum__mcfx = c.context.insert_const_string(c.builder.module, 'pandas')
    ekge__alm = c.pyapi.import_module_noblock(bsmum__mcfx)
    kcmd__snhh = c.pyapi.call_method(ekge__alm, 'CategoricalDtype', (
        aytr__trk, jwoj__kivca))
    c.pyapi.decref(jwoj__kivca)
    c.pyapi.decref(aytr__trk)
    c.pyapi.decref(ekge__alm)
    c.context.nrt.decref(c.builder, typ, val)
    return kcmd__snhh


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
        rdsi__vqbz = get_categories_int_type(fe_type.dtype)
        nulp__yrv = [('dtype', fe_type.dtype), ('codes', types.Array(
            rdsi__vqbz, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, nulp__yrv)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    yjh__xmep = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), yjh__xmep
        ).value
    c.pyapi.decref(yjh__xmep)
    kcmd__snhh = c.pyapi.object_getattr_string(val, 'dtype')
    ply__wshyd = c.pyapi.to_native_value(typ.dtype, kcmd__snhh).value
    c.pyapi.decref(kcmd__snhh)
    xxgnn__vebd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xxgnn__vebd.codes = codes
    xxgnn__vebd.dtype = ply__wshyd
    return NativeValue(xxgnn__vebd._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    gxhzt__jfd = get_categories_int_type(typ.dtype)
    oehi__jrgh = context.get_constant_generic(builder, types.Array(
        gxhzt__jfd, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, oehi__jrgh])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    hjvd__maa = len(cat_dtype.categories)
    if hjvd__maa < np.iinfo(np.int8).max:
        dtype = types.int8
    elif hjvd__maa < np.iinfo(np.int16).max:
        dtype = types.int16
    elif hjvd__maa < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    bsmum__mcfx = c.context.insert_const_string(c.builder.module, 'pandas')
    ekge__alm = c.pyapi.import_module_noblock(bsmum__mcfx)
    rdsi__vqbz = get_categories_int_type(dtype)
    mrmqk__gwcw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    rux__aeo = types.Array(rdsi__vqbz, 1, 'C')
    c.context.nrt.incref(c.builder, rux__aeo, mrmqk__gwcw.codes)
    yjh__xmep = c.pyapi.from_native_value(rux__aeo, mrmqk__gwcw.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, mrmqk__gwcw.dtype)
    kcmd__snhh = c.pyapi.from_native_value(dtype, mrmqk__gwcw.dtype, c.
        env_manager)
    qfu__tmrt = c.pyapi.borrow_none()
    yqc__hlra = c.pyapi.object_getattr_string(ekge__alm, 'Categorical')
    fwjk__haf = c.pyapi.call_method(yqc__hlra, 'from_codes', (yjh__xmep,
        qfu__tmrt, qfu__tmrt, kcmd__snhh))
    c.pyapi.decref(yqc__hlra)
    c.pyapi.decref(yjh__xmep)
    c.pyapi.decref(kcmd__snhh)
    c.pyapi.decref(ekge__alm)
    c.context.nrt.decref(c.builder, typ, val)
    return fwjk__haf


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
            hudcp__hxkp = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                yspj__sqaa = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), hudcp__hxkp)
                return yspj__sqaa
            return impl_lit

        def impl(A, other):
            hudcp__hxkp = get_code_for_value(A.dtype, other)
            yspj__sqaa = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), hudcp__hxkp)
            return yspj__sqaa
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        uciko__cre = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(uciko__cre)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    mrmqk__gwcw = cat_dtype.categories
    n = len(mrmqk__gwcw)
    for wtcuu__ovma in range(n):
        if mrmqk__gwcw[wtcuu__ovma] == val:
            return wtcuu__ovma
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    yxv__thjbc = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype'
        )
    if yxv__thjbc != A.dtype.elem_type and yxv__thjbc != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if yxv__thjbc == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            yspj__sqaa = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for wtcuu__ovma in numba.parfors.parfor.internal_prange(n):
                aoh__nxd = codes[wtcuu__ovma]
                if aoh__nxd == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(yspj__sqaa
                            , wtcuu__ovma)
                    else:
                        bodo.libs.array_kernels.setna(yspj__sqaa, wtcuu__ovma)
                    continue
                yspj__sqaa[wtcuu__ovma] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[aoh__nxd]))
            return yspj__sqaa
        return impl
    rux__aeo = dtype_to_array_type(yxv__thjbc)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        yspj__sqaa = bodo.utils.utils.alloc_type(n, rux__aeo, (-1,))
        for wtcuu__ovma in numba.parfors.parfor.internal_prange(n):
            aoh__nxd = codes[wtcuu__ovma]
            if aoh__nxd == -1:
                bodo.libs.array_kernels.setna(yspj__sqaa, wtcuu__ovma)
                continue
            yspj__sqaa[wtcuu__ovma] = bodo.utils.conversion.unbox_if_timestamp(
                categories[aoh__nxd])
        return yspj__sqaa
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        gucx__cqgmb, ply__wshyd = args
        mrmqk__gwcw = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        mrmqk__gwcw.codes = gucx__cqgmb
        mrmqk__gwcw.dtype = ply__wshyd
        context.nrt.incref(builder, signature.args[0], gucx__cqgmb)
        context.nrt.incref(builder, signature.args[1], ply__wshyd)
        return mrmqk__gwcw._getvalue()
    hvx__qcryc = CategoricalArrayType(cat_dtype)
    sig = hvx__qcryc(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qhoz__dco = args[0]
    if equiv_set.has_shape(qhoz__dco):
        return ArrayAnalysis.AnalyzeResult(shape=qhoz__dco, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    rdsi__vqbz = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, rdsi__vqbz)
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
            efz__shnw = {}
            oehi__jrgh = np.empty(n + 1, np.int64)
            mkw__uyp = {}
            wzdt__irdut = []
            xegp__cnu = {}
            for wtcuu__ovma in range(n):
                xegp__cnu[categories[wtcuu__ovma]] = wtcuu__ovma
            for nca__qstm in to_replace:
                if nca__qstm != value:
                    if nca__qstm in xegp__cnu:
                        if value in xegp__cnu:
                            efz__shnw[nca__qstm] = nca__qstm
                            lof__kjdd = xegp__cnu[nca__qstm]
                            mkw__uyp[lof__kjdd] = xegp__cnu[value]
                            wzdt__irdut.append(lof__kjdd)
                        else:
                            efz__shnw[nca__qstm] = value
                            xegp__cnu[value] = xegp__cnu[nca__qstm]
            xnvf__xgspa = np.sort(np.array(wzdt__irdut))
            gjpm__zuuo = 0
            gytbs__huzxu = []
            for odq__dphp in range(-1, n):
                while gjpm__zuuo < len(xnvf__xgspa
                    ) and odq__dphp > xnvf__xgspa[gjpm__zuuo]:
                    gjpm__zuuo += 1
                gytbs__huzxu.append(gjpm__zuuo)
            for eyi__xyob in range(-1, n):
                sljf__vwivi = eyi__xyob
                if eyi__xyob in mkw__uyp:
                    sljf__vwivi = mkw__uyp[eyi__xyob]
                oehi__jrgh[eyi__xyob + 1] = sljf__vwivi - gytbs__huzxu[
                    sljf__vwivi + 1]
            return efz__shnw, oehi__jrgh, len(xnvf__xgspa)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for wtcuu__ovma in range(len(new_codes_arr)):
        new_codes_arr[wtcuu__ovma] = codes_map_arr[old_codes_arr[
            wtcuu__ovma] + 1]


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
    ljv__fcy = arr.dtype.ordered
    hook__edbch = arr.dtype.elem_type
    vvf__znedt = get_overload_const(to_replace)
    aodb__mzzhc = get_overload_const(value)
    if (arr.dtype.categories is not None and vvf__znedt is not NOT_CONSTANT and
        aodb__mzzhc is not NOT_CONSTANT):
        apuwk__dabsv, codes_map_arr, idc__vrxgb = python_build_replace_dicts(
            vvf__znedt, aodb__mzzhc, arr.dtype.categories)
        if len(apuwk__dabsv) == 0:
            return lambda arr, to_replace, value: arr.copy()
        uzg__oirg = []
        for kbkwi__dbd in arr.dtype.categories:
            if kbkwi__dbd in apuwk__dabsv:
                vllo__gjql = apuwk__dabsv[kbkwi__dbd]
                if vllo__gjql != kbkwi__dbd:
                    uzg__oirg.append(vllo__gjql)
            else:
                uzg__oirg.append(kbkwi__dbd)
        orm__epfkf = pd.CategoricalDtype(uzg__oirg, ljv__fcy).categories.values
        tum__cfjkz = MetaType(tuple(orm__epfkf))

        def impl_dtype(arr, to_replace, value):
            sony__bivly = init_cat_dtype(bodo.utils.conversion.
                index_from_array(orm__epfkf), ljv__fcy, None, tum__cfjkz)
            mrmqk__gwcw = alloc_categorical_array(len(arr.codes), sony__bivly)
            reassign_codes(mrmqk__gwcw.codes, arr.codes, codes_map_arr)
            return mrmqk__gwcw
        return impl_dtype
    hook__edbch = arr.dtype.elem_type
    if hook__edbch == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            efz__shnw, codes_map_arr, snf__hyo = build_replace_dicts(to_replace
                , value, categories.values)
            if len(efz__shnw) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), ljv__fcy,
                    None, None))
            n = len(categories)
            orm__epfkf = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                snf__hyo, -1)
            tiy__ctrd = 0
            for odq__dphp in range(n):
                tvx__kpi = categories[odq__dphp]
                if tvx__kpi in efz__shnw:
                    uqkw__snxy = efz__shnw[tvx__kpi]
                    if uqkw__snxy != tvx__kpi:
                        orm__epfkf[tiy__ctrd] = uqkw__snxy
                        tiy__ctrd += 1
                else:
                    orm__epfkf[tiy__ctrd] = tvx__kpi
                    tiy__ctrd += 1
            mrmqk__gwcw = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                orm__epfkf), ljv__fcy, None, None))
            reassign_codes(mrmqk__gwcw.codes, arr.codes, codes_map_arr)
            return mrmqk__gwcw
        return impl_str
    hygqk__ricql = dtype_to_array_type(hook__edbch)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        efz__shnw, codes_map_arr, snf__hyo = build_replace_dicts(to_replace,
            value, categories.values)
        if len(efz__shnw) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), ljv__fcy, None, None))
        n = len(categories)
        orm__epfkf = bodo.utils.utils.alloc_type(n - snf__hyo, hygqk__ricql,
            None)
        tiy__ctrd = 0
        for wtcuu__ovma in range(n):
            tvx__kpi = categories[wtcuu__ovma]
            if tvx__kpi in efz__shnw:
                uqkw__snxy = efz__shnw[tvx__kpi]
                if uqkw__snxy != tvx__kpi:
                    orm__epfkf[tiy__ctrd] = uqkw__snxy
                    tiy__ctrd += 1
            else:
                orm__epfkf[tiy__ctrd] = tvx__kpi
                tiy__ctrd += 1
        mrmqk__gwcw = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            orm__epfkf), ljv__fcy, None, None))
        reassign_codes(mrmqk__gwcw.codes, arr.codes, codes_map_arr)
        return mrmqk__gwcw
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
    heiq__aujts = dict()
    kybxd__xkl = 0
    for wtcuu__ovma in range(len(vals)):
        val = vals[wtcuu__ovma]
        if val in heiq__aujts:
            continue
        heiq__aujts[val] = kybxd__xkl
        kybxd__xkl += 1
    return heiq__aujts


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    heiq__aujts = dict()
    for wtcuu__ovma in range(len(vals)):
        val = vals[wtcuu__ovma]
        heiq__aujts[val] = wtcuu__ovma
    return heiq__aujts


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    eqcyn__kmn = dict(fastpath=fastpath)
    zxy__ujxbj = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', eqcyn__kmn, zxy__ujxbj)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        eefst__ikt = get_overload_const(categories)
        if eefst__ikt is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                txrsj__awylq = False
            else:
                txrsj__awylq = get_overload_const_bool(ordered)
            euhrv__uimi = pd.CategoricalDtype(eefst__ikt, txrsj__awylq
                ).categories.values
            exya__fiq = MetaType(tuple(euhrv__uimi))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                sony__bivly = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(euhrv__uimi), txrsj__awylq, None,
                    exya__fiq)
                return bodo.utils.conversion.fix_arr_dtype(data, sony__bivly)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            rgej__jsi = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                rgej__jsi, ordered, None, None)
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
            iutzk__krr = arr.codes[ind]
            return arr.dtype.categories[max(iutzk__krr, 0)]
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
    for wtcuu__ovma in range(len(arr1)):
        if arr1[wtcuu__ovma] != arr2[wtcuu__ovma]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    acqo__otxst = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    yrerf__ujo = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    rula__ags = categorical_arrs_match(arr, val)
    acxgc__llnfe = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    mlvx__ypipj = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not acqo__otxst:
            raise BodoError(acxgc__llnfe)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            iutzk__krr = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = iutzk__krr
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (acqo__otxst or yrerf__ujo or rula__ags !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(acxgc__llnfe)
        if rula__ags == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mlvx__ypipj)
        if acqo__otxst:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ipv__dicp = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for odq__dphp in range(n):
                    arr.codes[ind[odq__dphp]] = ipv__dicp
            return impl_scalar
        if rula__ags == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for wtcuu__ovma in range(n):
                    arr.codes[ind[wtcuu__ovma]] = val.codes[wtcuu__ovma]
            return impl_arr_ind_mask
        if rula__ags == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mlvx__ypipj)
                n = len(val.codes)
                for wtcuu__ovma in range(n):
                    arr.codes[ind[wtcuu__ovma]] = val.codes[wtcuu__ovma]
            return impl_arr_ind_mask
        if yrerf__ujo:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for odq__dphp in range(n):
                    vucl__rug = bodo.utils.conversion.unbox_if_timestamp(val
                        [odq__dphp])
                    if vucl__rug not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    iutzk__krr = categories.get_loc(vucl__rug)
                    arr.codes[ind[odq__dphp]] = iutzk__krr
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (acqo__otxst or yrerf__ujo or rula__ags !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(acxgc__llnfe)
        if rula__ags == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mlvx__ypipj)
        if acqo__otxst:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ipv__dicp = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for odq__dphp in range(n):
                    if ind[odq__dphp]:
                        arr.codes[odq__dphp] = ipv__dicp
            return impl_scalar
        if rula__ags == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                iambh__cajcx = 0
                for wtcuu__ovma in range(n):
                    if ind[wtcuu__ovma]:
                        arr.codes[wtcuu__ovma] = val.codes[iambh__cajcx]
                        iambh__cajcx += 1
            return impl_bool_ind_mask
        if rula__ags == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mlvx__ypipj)
                n = len(ind)
                iambh__cajcx = 0
                for wtcuu__ovma in range(n):
                    if ind[wtcuu__ovma]:
                        arr.codes[wtcuu__ovma] = val.codes[iambh__cajcx]
                        iambh__cajcx += 1
            return impl_bool_ind_mask
        if yrerf__ujo:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                iambh__cajcx = 0
                categories = arr.dtype.categories
                for odq__dphp in range(n):
                    if ind[odq__dphp]:
                        vucl__rug = bodo.utils.conversion.unbox_if_timestamp(
                            val[iambh__cajcx])
                        if vucl__rug not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        iutzk__krr = categories.get_loc(vucl__rug)
                        arr.codes[odq__dphp] = iutzk__krr
                        iambh__cajcx += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (acqo__otxst or yrerf__ujo or rula__ags !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(acxgc__llnfe)
        if rula__ags == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mlvx__ypipj)
        if acqo__otxst:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ipv__dicp = arr.dtype.categories.get_loc(val)
                mqqq__dfngf = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for odq__dphp in range(mqqq__dfngf.start, mqqq__dfngf.stop,
                    mqqq__dfngf.step):
                    arr.codes[odq__dphp] = ipv__dicp
            return impl_scalar
        if rula__ags == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if rula__ags == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mlvx__ypipj)
                arr.codes[ind] = val.codes
            return impl_arr
        if yrerf__ujo:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                mqqq__dfngf = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                iambh__cajcx = 0
                for odq__dphp in range(mqqq__dfngf.start, mqqq__dfngf.stop,
                    mqqq__dfngf.step):
                    vucl__rug = bodo.utils.conversion.unbox_if_timestamp(val
                        [iambh__cajcx])
                    if vucl__rug not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    iutzk__krr = categories.get_loc(vucl__rug)
                    arr.codes[odq__dphp] = iutzk__krr
                    iambh__cajcx += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
