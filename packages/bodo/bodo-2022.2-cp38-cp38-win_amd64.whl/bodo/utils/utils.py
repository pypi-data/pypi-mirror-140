"""
Collection of utility functions. Needs to be refactored in separate files.
"""
import hashlib
import inspect
import keyword
import re
import warnings
from enum import Enum
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.ir_utils import find_callname, find_const, get_definition, guard, mk_unique_var, require
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload
from numba.np.arrayobj import get_itemsize, make_array, populate_array
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import num_total_chars, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import NOT_CONSTANT, BodoError, BodoWarning, MetaType
int128_type = types.Integer('int128', 128)


class CTypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Date = 13
    Datetime = 14
    Timedelta = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 20


_numba_to_c_type_map = {types.int8: CTypeEnum.Int8.value, types.uint8:
    CTypeEnum.UInt8.value, types.int32: CTypeEnum.Int32.value, types.uint32:
    CTypeEnum.UInt32.value, types.int64: CTypeEnum.Int64.value, types.
    uint64: CTypeEnum.UInt64.value, types.float32: CTypeEnum.Float32.value,
    types.float64: CTypeEnum.Float64.value, types.NPDatetime('ns'):
    CTypeEnum.Datetime.value, types.NPTimedelta('ns'): CTypeEnum.Timedelta.
    value, types.bool_: CTypeEnum.Bool.value, types.int16: CTypeEnum.Int16.
    value, types.uint16: CTypeEnum.UInt16.value, int128_type: CTypeEnum.
    Int128.value}
numba.core.errors.error_extras = {'unsupported_error': '', 'typing': '',
    'reportable': '', 'interpreter': '', 'constant_inference': ''}
np_alloc_callnames = 'empty', 'zeros', 'ones', 'full'
CONST_DICT_SLOW_WARN_THRESHOLD = 100
CONST_LIST_SLOW_WARN_THRESHOLD = 100000


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


def get_constant(func_ir, var, default=NOT_CONSTANT):
    xfn__yepn = guard(get_definition, func_ir, var)
    if xfn__yepn is None:
        return default
    if isinstance(xfn__yepn, ir.Const):
        return xfn__yepn.value
    if isinstance(xfn__yepn, ir.Var):
        return get_constant(func_ir, xfn__yepn, default)
    return default


def numba_to_c_type(t):
    if isinstance(t, bodo.libs.decimal_arr_ext.Decimal128Type):
        return CTypeEnum.Decimal.value
    if t == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return CTypeEnum.Date.value
    return _numba_to_c_type_map[t]


def is_alloc_callname(func_name, mod_name):
    return isinstance(mod_name, str) and (mod_name == 'numpy' and func_name in
        np_alloc_callnames or func_name == 'empty_inferred' and mod_name in
        ('numba.extending', 'numba.np.unsafe.ndarray') or func_name ==
        'pre_alloc_string_array' and mod_name == 'bodo.libs.str_arr_ext' or
        func_name == 'pre_alloc_binary_array' and mod_name ==
        'bodo.libs.binary_arr_ext' or func_name ==
        'alloc_random_access_string_array' and mod_name ==
        'bodo.libs.str_ext' or func_name == 'pre_alloc_array_item_array' and
        mod_name == 'bodo.libs.array_item_arr_ext' or func_name ==
        'pre_alloc_struct_array' and mod_name == 'bodo.libs.struct_arr_ext' or
        func_name == 'pre_alloc_map_array' and mod_name ==
        'bodo.libs.map_arr_ext' or func_name == 'pre_alloc_tuple_array' and
        mod_name == 'bodo.libs.tuple_arr_ext' or func_name ==
        'alloc_bool_array' and mod_name == 'bodo.libs.bool_arr_ext' or 
        func_name == 'alloc_int_array' and mod_name ==
        'bodo.libs.int_arr_ext' or func_name == 'alloc_datetime_date_array' and
        mod_name == 'bodo.hiframes.datetime_date_ext' or func_name ==
        'alloc_datetime_timedelta_array' and mod_name ==
        'bodo.hiframes.datetime_timedelta_ext' or func_name ==
        'alloc_decimal_array' and mod_name == 'bodo.libs.decimal_arr_ext' or
        func_name == 'alloc_categorical_array' and mod_name ==
        'bodo.hiframes.pd_categorical_ext' or func_name == 'gen_na_array' and
        mod_name == 'bodo.libs.array_kernels')


def find_build_tuple(func_ir, var):
    require(isinstance(var, (ir.Var, str)))
    iso__mrc = get_definition(func_ir, var)
    require(isinstance(iso__mrc, ir.Expr))
    require(iso__mrc.op == 'build_tuple')
    return iso__mrc.items


def cprint(*s):
    print(*s)


@infer_global(cprint)
class CprintInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.none, *unliteral_all(args))


typ_to_format = {types.int32: 'd', types.uint32: 'u', types.int64: 'lld',
    types.uint64: 'llu', types.float32: 'f', types.float64: 'lf', types.
    voidptr: 's'}


@lower_builtin(cprint, types.VarArg(types.Any))
def cprint_lower(context, builder, sig, args):
    for chq__cokig, val in enumerate(args):
        typ = sig.args[chq__cokig]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        llg__esgbq = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(llg__esgbq), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    ojom__xirqx = get_definition(func_ir, var)
    require(isinstance(ojom__xirqx, ir.Expr) and ojom__xirqx.op == 'call')
    assert len(ojom__xirqx.args) == 2 or accept_stride and len(ojom__xirqx.args
        ) == 3
    assert find_callname(func_ir, ojom__xirqx) == ('slice', 'builtins')
    gafe__iudj = get_definition(func_ir, ojom__xirqx.args[0])
    riqfo__kxd = get_definition(func_ir, ojom__xirqx.args[1])
    require(isinstance(gafe__iudj, ir.Const) and gafe__iudj.value == None)
    require(isinstance(riqfo__kxd, ir.Const) and riqfo__kxd.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    lfao__oohy = get_definition(func_ir, index_var)
    require(find_callname(func_ir, lfao__oohy) == ('slice', 'builtins'))
    require(len(lfao__oohy.args) in (2, 3))
    require(find_const(func_ir, lfao__oohy.args[0]) in (0, None))
    require(equiv_set.is_equiv(lfao__oohy.args[1], arr_var.name + '#0'))
    require(accept_stride or len(lfao__oohy.args) == 2 or find_const(
        func_ir, lfao__oohy.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    ojom__xirqx = get_definition(func_ir, var)
    require(isinstance(ojom__xirqx, ir.Expr) and ojom__xirqx.op == 'call')
    assert len(ojom__xirqx.args) == 3
    return ojom__xirqx.args[2]


def is_array_typ(var_typ, include_index_series=True):
    return is_np_array_typ(var_typ) or var_typ in (string_array_type, bodo.
        binary_array_type, bodo.hiframes.split_impl.
        string_array_split_view_type, bodo.hiframes.datetime_date_ext.
        datetime_date_array_type, bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type, boolean_array, bodo.libs.str_ext.
        random_access_string_array) or isinstance(var_typ, (
        IntegerArrayType, bodo.libs.decimal_arr_ext.DecimalArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType, bodo.libs.struct_arr_ext.
        StructArrayType, bodo.libs.interval_arr_ext.IntervalArrayType, bodo
        .libs.tuple_arr_ext.TupleArrayType, bodo.libs.map_arr_ext.
        MapArrayType, bodo.libs.csr_matrix_ext.CSRMatrixType)
        ) or include_index_series and (isinstance(var_typ, (bodo.hiframes.
        pd_series_ext.SeriesType, bodo.hiframes.pd_multi_index_ext.
        MultiIndexType)) or bodo.hiframes.pd_index_ext.is_pd_index_type(
        var_typ))


def is_np_array_typ(var_typ):
    return isinstance(var_typ, types.Array)


def is_distributable_typ(var_typ):
    return is_array_typ(var_typ) or isinstance(var_typ, bodo.hiframes.table
        .TableType) or isinstance(var_typ, bodo.hiframes.pd_dataframe_ext.
        DataFrameType) or isinstance(var_typ, types.List
        ) and is_distributable_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_typ(var_typ.value_type)


def is_distributable_tuple_typ(var_typ):
    return isinstance(var_typ, types.BaseTuple) and any(
        is_distributable_typ(t) or is_distributable_tuple_typ(t) for t in
        var_typ.types) or isinstance(var_typ, types.List
        ) and is_distributable_tuple_typ(var_typ.dtype) or isinstance(var_typ,
        types.DictType) and is_distributable_tuple_typ(var_typ.value_type
        ) or isinstance(var_typ, types.iterators.EnumerateType) and (
        is_distributable_typ(var_typ.yield_type[1]) or
        is_distributable_tuple_typ(var_typ.yield_type[1]))


@numba.generated_jit(nopython=True, cache=True)
def build_set_seen_na(A):

    def impl(A):
        s = dict()
        hxrlb__eedh = False
        for chq__cokig in range(len(A)):
            if bodo.libs.array_kernels.isna(A, chq__cokig):
                hxrlb__eedh = True
                continue
            s[A[chq__cokig]] = 0
        return s, hxrlb__eedh
    return impl


@numba.generated_jit(nopython=True, cache=True)
def build_set(A):
    if isinstance(A, IntegerArrayType) or A in (string_array_type,
        boolean_array):

        def impl_int_arr(A):
            s = dict()
            for chq__cokig in range(len(A)):
                if not bodo.libs.array_kernels.isna(A, chq__cokig):
                    s[A[chq__cokig]] = 0
            return s
        return impl_int_arr
    else:

        def impl(A):
            s = dict()
            for chq__cokig in range(len(A)):
                s[A[chq__cokig]] = 0
            return s
        return impl


def to_array(A):
    return np.array(A)


@overload(to_array, no_unliteral=True)
def to_array_overload(A):
    if isinstance(A, types.DictType):
        dtype = A.key_type

        def impl(A):
            n = len(A)
            arr = alloc_type(n, dtype, (-1,))
            chq__cokig = 0
            for v in A.keys():
                arr[chq__cokig] = v
                chq__cokig += 1
            return arr
        return impl

    def to_array_impl(A):
        return np.array(A)
    try:
        numba.njit(to_array_impl).get_call_template((A,), {})
        return to_array_impl
    except:
        pass


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def unique(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:
        return lambda A: A.unique()
    return lambda A: to_array(build_set(A))


def empty_like_type(n, arr):
    return np.empty(n, arr.dtype)


@overload(empty_like_type, no_unliteral=True)
def empty_like_type_overload(n, arr):
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda n, arr: bodo.hiframes.pd_categorical_ext.
            alloc_categorical_array(n, arr.dtype))
    if isinstance(arr, types.Array):
        return lambda n, arr: np.empty(n, arr.dtype)
    if isinstance(arr, types.List) and arr.dtype == string_type:

        def empty_like_type_str_list(n, arr):
            return [''] * n
        return empty_like_type_str_list
    if isinstance(arr, types.List) and arr.dtype == bytes_type:

        def empty_like_type_binary_list(n, arr):
            return [b''] * n
        return empty_like_type_binary_list
    if isinstance(arr, IntegerArrayType):
        tapmj__lsq = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, tapmj__lsq)
        return empty_like_type_int_arr
    if arr == boolean_array:

        def empty_like_type_bool_arr(n, arr):
            return bodo.libs.bool_arr_ext.alloc_bool_array(n)
        return empty_like_type_bool_arr
    if arr == bodo.hiframes.datetime_date_ext.datetime_date_array_type:

        def empty_like_type_datetime_date_arr(n, arr):
            return bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(n)
        return empty_like_type_datetime_date_arr
    if (arr == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_array_type):

        def empty_like_type_datetime_timedelta_arr(n, arr):
            return (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(n))
        return empty_like_type_datetime_timedelta_arr
    if isinstance(arr, bodo.libs.decimal_arr_ext.DecimalArrayType):
        precision = arr.precision
        scale = arr.scale

        def empty_like_type_decimal_arr(n, arr):
            return bodo.libs.decimal_arr_ext.alloc_decimal_array(n,
                precision, scale)
        return empty_like_type_decimal_arr
    assert arr == string_array_type

    def empty_like_type_str_arr(n, arr):
        hio__gwz = 20
        if len(arr) != 0:
            hio__gwz = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * hio__gwz)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    vcml__wism = make_array(arrtype)
    lkkm__cuk = vcml__wism(context, builder)
    jaki__lghww = context.get_data_type(arrtype.dtype)
    hiygb__uij = context.get_constant(types.intp, get_itemsize(context,
        arrtype))
    oekeq__aid = context.get_constant(types.intp, 1)
    aao__xct = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        bbxib__mpaop = builder.smul_with_overflow(oekeq__aid, s)
        oekeq__aid = builder.extract_value(bbxib__mpaop, 0)
        aao__xct = builder.or_(aao__xct, builder.extract_value(bbxib__mpaop, 1)
            )
    if arrtype.ndim == 0:
        lkm__utuo = ()
    elif arrtype.layout == 'C':
        lkm__utuo = [hiygb__uij]
        for esxjo__krbm in reversed(shapes[1:]):
            lkm__utuo.append(builder.mul(lkm__utuo[-1], esxjo__krbm))
        lkm__utuo = tuple(reversed(lkm__utuo))
    elif arrtype.layout == 'F':
        lkm__utuo = [hiygb__uij]
        for esxjo__krbm in shapes[:-1]:
            lkm__utuo.append(builder.mul(lkm__utuo[-1], esxjo__krbm))
        lkm__utuo = tuple(lkm__utuo)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    thd__sibzg = builder.smul_with_overflow(oekeq__aid, hiygb__uij)
    rbs__vyks = builder.extract_value(thd__sibzg, 0)
    aao__xct = builder.or_(aao__xct, builder.extract_value(thd__sibzg, 1))
    with builder.if_then(aao__xct, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    twcu__hkmj = context.get_preferred_array_alignment(dtype)
    jdhy__epfz = context.get_constant(types.uint32, twcu__hkmj)
    qxei__resqh = context.nrt.meminfo_alloc_aligned(builder, size=rbs__vyks,
        align=jdhy__epfz)
    data = context.nrt.meminfo_data(builder, qxei__resqh)
    ehrn__fkuu = context.get_value_type(types.intp)
    tae__mobrs = cgutils.pack_array(builder, shapes, ty=ehrn__fkuu)
    orng__eri = cgutils.pack_array(builder, lkm__utuo, ty=ehrn__fkuu)
    populate_array(lkkm__cuk, data=builder.bitcast(data, jaki__lghww.
        as_pointer()), shape=tae__mobrs, strides=orng__eri, itemsize=
        hiygb__uij, meminfo=qxei__resqh)
    return lkkm__cuk


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    kpudq__zrlc = []
    for oak__uzlpj in arr_tup:
        kpudq__zrlc.append(np.empty(n, oak__uzlpj.dtype))
    return tuple(kpudq__zrlc)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    tikw__vlu = data.count
    crysz__bpyv = ','.join(['empty_like_type(n, data[{}])'.format(
        chq__cokig) for chq__cokig in range(tikw__vlu)])
    if init_vals != ():
        crysz__bpyv = ','.join(['np.full(n, init_vals[{}], data[{}].dtype)'
            .format(chq__cokig, chq__cokig) for chq__cokig in range(tikw__vlu)]
            )
    otud__cmrny = 'def f(n, data, init_vals=()):\n'
    otud__cmrny += '  return ({}{})\n'.format(crysz__bpyv, ',' if tikw__vlu ==
        1 else '')
    egd__zyrc = {}
    exec(otud__cmrny, {'empty_like_type': empty_like_type, 'np': np}, egd__zyrc
        )
    qifac__bdmsd = egd__zyrc['f']
    return qifac__bdmsd


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_to_scalar(n):
    if isinstance(n, types.BaseTuple) and len(n.types) == 1:
        return lambda n: n[0]
    return lambda n: n


def alloc_type(n, t, s=None):
    return np.empty(n, t.dtype)


@overload(alloc_type)
def overload_alloc_type(n, t, s=None):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if typ == string_array_type:
        return (lambda n, t, s=None: bodo.libs.str_arr_ext.
            pre_alloc_string_array(n, s[0]))
    if typ == bodo.binary_array_type:
        return (lambda n, t, s=None: bodo.libs.binary_arr_ext.
            pre_alloc_binary_array(n, s[0]))
    if isinstance(typ, bodo.libs.array_item_arr_ext.ArrayItemArrayType):
        dtype = typ.dtype
        return (lambda n, t, s=None: bodo.libs.array_item_arr_ext.
            pre_alloc_array_item_array(n, s, dtype))
    if isinstance(typ, bodo.libs.struct_arr_ext.StructArrayType):
        dtypes = typ.data
        names = typ.names
        return (lambda n, t, s=None: bodo.libs.struct_arr_ext.
            pre_alloc_struct_array(n, s, dtypes, names))
    if isinstance(typ, bodo.libs.map_arr_ext.MapArrayType):
        struct_typ = bodo.libs.struct_arr_ext.StructArrayType((typ.
            key_arr_type, typ.value_arr_type), ('key', 'value'))
        return lambda n, t, s=None: bodo.libs.map_arr_ext.pre_alloc_map_array(n
            , s, struct_typ)
    if isinstance(typ, bodo.libs.tuple_arr_ext.TupleArrayType):
        dtypes = typ.data
        return (lambda n, t, s=None: bodo.libs.tuple_arr_ext.
            pre_alloc_tuple_array(n, s, dtypes))
    if isinstance(typ, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        if isinstance(t, types.TypeRef):
            if typ.dtype.categories is None:
                raise BodoError(
                    'UDFs or Groupbys that return Categorical values must have categories known at compile time.'
                    )
            is_ordered = typ.dtype.ordered
            int_type = typ.dtype.int_type
            new_cats_arr = pd.CategoricalDtype(typ.dtype.categories, is_ordered
                ).categories.values
            new_cats_tup = MetaType(tuple(new_cats_arr))
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, bodo.hiframes.pd_categorical_ext
                .init_cat_dtype(bodo.utils.conversion.index_from_array(
                new_cats_arr), is_ordered, int_type, new_cats_tup)))
        else:
            return (lambda n, t, s=None: bodo.hiframes.pd_categorical_ext.
                alloc_categorical_array(n, t.dtype))
    if typ.dtype == bodo.hiframes.datetime_date_ext.datetime_date_type:
        return (lambda n, t, s=None: bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(n))
    if (typ.dtype == bodo.hiframes.datetime_timedelta_ext.
        datetime_timedelta_type):
        return (lambda n, t, s=None: bodo.hiframes.datetime_timedelta_ext.
            alloc_datetime_timedelta_array(n))
    if isinstance(typ, DecimalArrayType):
        precision = typ.dtype.precision
        scale = typ.dtype.scale
        return (lambda n, t, s=None: bodo.libs.decimal_arr_ext.
            alloc_decimal_array(n, precision, scale))
    dtype = numba.np.numpy_support.as_dtype(typ.dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda n, t, s=None: bodo.libs.int_arr_ext.alloc_int_array(n,
            dtype)
    if typ == boolean_array:
        return lambda n, t, s=None: bodo.libs.bool_arr_ext.alloc_bool_array(n)
    return lambda n, t, s=None: np.empty(n, dtype)


def astype(A, t):
    return A.astype(t.dtype)


@overload(astype, no_unliteral=True)
def overload_astype(A, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    dtype = typ.dtype
    if A == typ:
        return lambda A, t: A
    if isinstance(A, (types.Array, IntegerArrayType)) and isinstance(typ,
        types.Array):
        return lambda A, t: A.astype(dtype)
    if isinstance(typ, IntegerArrayType):
        return lambda A, t: bodo.libs.int_arr_ext.init_integer_array(A.
            astype(dtype), np.full(len(A) + 7 >> 3, 255, np.uint8))
    raise BodoError(f'cannot convert array type {A} to {typ}')


def full_type(n, val, t):
    return np.full(n, val, t.dtype)


@overload(full_type, no_unliteral=True)
def overload_full_type(n, val, t):
    typ = t.instance_type if isinstance(t, types.TypeRef) else t
    if isinstance(typ, types.Array):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: np.full(n, val, dtype)
    if isinstance(typ, IntegerArrayType):
        dtype = numba.np.numpy_support.as_dtype(typ.dtype)
        return lambda n, val, t: bodo.libs.int_arr_ext.init_integer_array(np
            .full(n, val, dtype), np.full(tuple_to_scalar(n) + 7 >> 3, 255,
            np.uint8))
    if typ == boolean_array:
        return lambda n, val, t: bodo.libs.bool_arr_ext.init_bool_array(np.
            full(n, val, np.bool_), np.full(tuple_to_scalar(n) + 7 >> 3, 
            255, np.uint8))
    if typ == string_array_type:

        def impl_str(n, val, t):
            jkfiu__wtvx = n * len(val)
            A = pre_alloc_string_array(n, jkfiu__wtvx)
            for chq__cokig in range(n):
                A[chq__cokig] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for chq__cokig in range(n):
            A[chq__cokig] = val
        return A
    return impl


@intrinsic
def get_ctypes_ptr(typingctx, ctypes_typ=None):
    assert isinstance(ctypes_typ, types.ArrayCTypes)

    def codegen(context, builder, sig, args):
        fjr__wrv, = args
        xcbt__vxx = context.make_helper(builder, sig.args[0], fjr__wrv)
        return xcbt__vxx.data
    return types.voidptr(ctypes_typ), codegen


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        veq__bzo, = args
        hppdf__vwqw = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', veq__bzo, hppdf__vwqw)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        ngl__zfa = cgutils.alloca_once_value(builder, val)
        umnas__hbj = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, ngl__zfa, umnas__hbj)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    otud__cmrny = 'def impl(A, data, elem_type):\n'
    otud__cmrny += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        otud__cmrny += (
            '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n')
    else:
        otud__cmrny += '    A[i] = d\n'
    egd__zyrc = {}
    exec(otud__cmrny, {'bodo': bodo}, egd__zyrc)
    impl = egd__zyrc['impl']
    return impl


def object_length(c, obj):
    mbns__wiih = c.context.get_argument_type(types.pyobject)
    dywbg__ztbt = lir.FunctionType(lir.IntType(64), [mbns__wiih])
    auckx__mdbv = cgutils.get_or_insert_function(c.builder.module,
        dywbg__ztbt, name='PyObject_Length')
    return c.builder.call(auckx__mdbv, (obj,))


def sequence_getitem(c, obj, ind):
    mbns__wiih = c.context.get_argument_type(types.pyobject)
    dywbg__ztbt = lir.FunctionType(mbns__wiih, [mbns__wiih, lir.IntType(64)])
    auckx__mdbv = cgutils.get_or_insert_function(c.builder.module,
        dywbg__ztbt, name='PySequence_GetItem')
    return c.builder.call(auckx__mdbv, (obj, ind))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        fatwg__ouk, = args
        context.nrt.incref(builder, signature.args[0], fatwg__ouk)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    ktre__gwh = out_var.loc
    abb__tldgg = ir.Expr.static_getitem(in_var, ind, None, ktre__gwh)
    calltypes[abb__tldgg] = None
    nodes.append(ir.Assign(abb__tldgg, out_var, ktre__gwh))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            yqe__hagpn = types.literal(node.index)
        except:
            yqe__hagpn = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = yqe__hagpn
        nodes.append(ir.Assign(ir.Const(node.index, node.loc), index_var,
            node.loc))
    return index_var


import copy
ir.Const.__deepcopy__ = lambda self, memo: ir.Const(self.value, copy.
    deepcopy(self.loc))


def is_call_assign(stmt):
    return isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
        ) and stmt.value.op == 'call'


def is_call(expr):
    return isinstance(expr, ir.Expr) and expr.op == 'call'


def is_var_assign(inst):
    return isinstance(inst, ir.Assign) and isinstance(inst.value, ir.Var)


def is_assign(inst):
    return isinstance(inst, ir.Assign)


def is_expr(val, op):
    return isinstance(val, ir.Expr) and val.op == op


def sanitize_varname(varname):
    if isinstance(varname, (tuple, list)):
        varname = '_'.join(sanitize_varname(v) for v in varname)
    varname = str(varname)
    rjk__zyup = re.sub('\\W+', '_', varname)
    if not rjk__zyup or not rjk__zyup[0].isalpha():
        rjk__zyup = '_' + rjk__zyup
    if not rjk__zyup.isidentifier() or keyword.iskeyword(rjk__zyup):
        rjk__zyup = mk_unique_var('new_name').replace('.', '_')
    return rjk__zyup


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            pgzk__wuoxy = len(A)
            for chq__cokig in range(pgzk__wuoxy):
                yield A[pgzk__wuoxy - 1 - chq__cokig]
        return impl_reversed


@numba.njit()
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit()
def nanvar_ddof1(a):
    imr__glezo = count_nonnan(a)
    if imr__glezo <= 1:
        return np.nan
    return np.nanvar(a) * (imr__glezo / (imr__glezo - 1))


@numba.njit()
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as hwv__srmq:
        xkf__gghx = False
    else:
        xkf__gghx = h5py.version.hdf5_version_tuple[1] == 10
    return xkf__gghx


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as hwv__srmq:
        xzjts__gulyl = False
    else:
        xzjts__gulyl = True
    return xzjts__gulyl


def has_scipy():
    try:
        import scipy
    except ImportError as hwv__srmq:
        xzrrw__azxk = False
    else:
        xzrrw__azxk = True
    return xzrrw__azxk


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        pdrq__crfrm = context.get_python_api(builder)
        ryqu__zax = pdrq__crfrm.err_occurred()
        pykyq__xlltn = cgutils.is_not_null(builder, ryqu__zax)
        with builder.if_then(pykyq__xlltn):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    pdrq__crfrm = context.get_python_api(builder)
    ryqu__zax = pdrq__crfrm.err_occurred()
    pykyq__xlltn = cgutils.is_not_null(builder, ryqu__zax)
    with builder.if_then(pykyq__xlltn):
        builder.ret(numba.core.callconv.RETCODE_EXC)


@numba.njit
def check_java_installation(fname):
    with numba.objmode():
        check_java_installation_(fname)


def check_java_installation_(fname):
    if not fname.startswith('hdfs://'):
        return
    import shutil
    if not shutil.which('java'):
        kniux__riuuf = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install openjdk=8 -c conda-forge'."
            )
        raise BodoError(kniux__riuuf)


dt_err = """
        If you are trying to set NULL values for timedelta64 in regular Python, 

        consider using np.timedelta64('nat') instead of None
        """


@lower_constant(types.List)
def lower_constant_list(context, builder, typ, pyval):
    if len(pyval) > CONST_LIST_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global lists can result in long compilation times. Please pass large lists as arguments to JIT functions or use arrays.'
            ))
    hmkg__vmlbk = []
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in list must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
        hmkg__vmlbk.append(context.get_constant_generic(builder, typ.dtype, a))
    zso__fsszy = context.get_constant_generic(builder, types.int64, len(pyval))
    njz__zouaa = context.get_constant_generic(builder, types.bool_, False)
    iki__ukfj = context.get_constant_null(types.pyobject)
    foa__dozfx = lir.Constant.literal_struct([zso__fsszy, zso__fsszy,
        njz__zouaa] + hmkg__vmlbk)
    foa__dozfx = cgutils.global_constant(builder, '.const.payload', foa__dozfx
        ).bitcast(cgutils.voidptr_t)
    lmwh__hgfo = context.get_constant(types.int64, -1)
    pxqci__lqlc = context.get_constant_null(types.voidptr)
    qxei__resqh = lir.Constant.literal_struct([lmwh__hgfo, pxqci__lqlc,
        pxqci__lqlc, foa__dozfx, lmwh__hgfo])
    qxei__resqh = cgutils.global_constant(builder, '.const.meminfo',
        qxei__resqh).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([qxei__resqh, iki__ukfj])


@lower_constant(types.Set)
def lower_constant_set(context, builder, typ, pyval):
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in set must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
    duh__vwz = types.List(typ.dtype)
    lfy__jhcog = context.get_constant_generic(builder, duh__vwz, list(pyval))
    cwiui__cczh = context.compile_internal(builder, lambda l: set(l), types
        .Set(typ.dtype)(duh__vwz), [lfy__jhcog])
    return cwiui__cczh


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    birud__tau = pd.Series(pyval.keys()).values
    slyb__ogeq = pd.Series(pyval.values()).values
    ipiy__ymg = bodo.typeof(birud__tau)
    qrtuk__vets = bodo.typeof(slyb__ogeq)
    require(ipiy__ymg.dtype == typ.key_type or can_replace(typ.key_type,
        ipiy__ymg.dtype))
    require(qrtuk__vets.dtype == typ.value_type or can_replace(typ.
        value_type, qrtuk__vets.dtype))
    owbt__qyykd = context.get_constant_generic(builder, ipiy__ymg, birud__tau)
    rir__qkk = context.get_constant_generic(builder, qrtuk__vets, slyb__ogeq)

    def create_dict(keys, vals):
        evqx__psysj = {}
        for k, v in zip(keys, vals):
            evqx__psysj[k] = v
        return evqx__psysj
    cwd__rnr = context.compile_internal(builder, create_dict, typ(ipiy__ymg,
        qrtuk__vets), [owbt__qyykd, rir__qkk])
    return cwd__rnr


@lower_constant(types.DictType)
def lower_constant_dict(context, builder, typ, pyval):
    try:
        return lower_const_dict_fast_path(context, builder, typ, pyval)
    except:
        pass
    if len(pyval) > CONST_DICT_SLOW_WARN_THRESHOLD:
        warnings.warn(BodoWarning(
            'Using large global dictionaries can result in long compilation times. Please pass large dictionaries as arguments to JIT functions.'
            ))
    kxaam__amtdt = typ.key_type
    xsb__zakep = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(kxaam__amtdt, xsb__zakep)
    cwd__rnr = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        plpn__pthjl = context.get_constant_generic(builder, kxaam__amtdt, k)
        hudb__xxqsh = context.get_constant_generic(builder, xsb__zakep, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            kxaam__amtdt, xsb__zakep), [cwd__rnr, plpn__pthjl, hudb__xxqsh])
    return cwd__rnr
