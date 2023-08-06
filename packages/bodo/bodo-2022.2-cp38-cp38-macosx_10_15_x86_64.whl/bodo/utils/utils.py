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
    vndsf__tjnz = guard(get_definition, func_ir, var)
    if vndsf__tjnz is None:
        return default
    if isinstance(vndsf__tjnz, ir.Const):
        return vndsf__tjnz.value
    if isinstance(vndsf__tjnz, ir.Var):
        return get_constant(func_ir, vndsf__tjnz, default)
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
    wdeci__fbaij = get_definition(func_ir, var)
    require(isinstance(wdeci__fbaij, ir.Expr))
    require(wdeci__fbaij.op == 'build_tuple')
    return wdeci__fbaij.items


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
    for dsq__banpz, val in enumerate(args):
        typ = sig.args[dsq__banpz]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        aocb__ejm = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(aocb__ejm), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    gqui__fajxz = get_definition(func_ir, var)
    require(isinstance(gqui__fajxz, ir.Expr) and gqui__fajxz.op == 'call')
    assert len(gqui__fajxz.args) == 2 or accept_stride and len(gqui__fajxz.args
        ) == 3
    assert find_callname(func_ir, gqui__fajxz) == ('slice', 'builtins')
    vkqhh__rkp = get_definition(func_ir, gqui__fajxz.args[0])
    wgr__djfhb = get_definition(func_ir, gqui__fajxz.args[1])
    require(isinstance(vkqhh__rkp, ir.Const) and vkqhh__rkp.value == None)
    require(isinstance(wgr__djfhb, ir.Const) and wgr__djfhb.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    drrp__sunzn = get_definition(func_ir, index_var)
    require(find_callname(func_ir, drrp__sunzn) == ('slice', 'builtins'))
    require(len(drrp__sunzn.args) in (2, 3))
    require(find_const(func_ir, drrp__sunzn.args[0]) in (0, None))
    require(equiv_set.is_equiv(drrp__sunzn.args[1], arr_var.name + '#0'))
    require(accept_stride or len(drrp__sunzn.args) == 2 or find_const(
        func_ir, drrp__sunzn.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    gqui__fajxz = get_definition(func_ir, var)
    require(isinstance(gqui__fajxz, ir.Expr) and gqui__fajxz.op == 'call')
    assert len(gqui__fajxz.args) == 3
    return gqui__fajxz.args[2]


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
        bxrgh__hadr = False
        for dsq__banpz in range(len(A)):
            if bodo.libs.array_kernels.isna(A, dsq__banpz):
                bxrgh__hadr = True
                continue
            s[A[dsq__banpz]] = 0
        return s, bxrgh__hadr
    return impl


@numba.generated_jit(nopython=True, cache=True)
def build_set(A):
    if isinstance(A, IntegerArrayType) or A in (string_array_type,
        boolean_array):

        def impl_int_arr(A):
            s = dict()
            for dsq__banpz in range(len(A)):
                if not bodo.libs.array_kernels.isna(A, dsq__banpz):
                    s[A[dsq__banpz]] = 0
            return s
        return impl_int_arr
    else:

        def impl(A):
            s = dict()
            for dsq__banpz in range(len(A)):
                s[A[dsq__banpz]] = 0
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
            dsq__banpz = 0
            for v in A.keys():
                arr[dsq__banpz] = v
                dsq__banpz += 1
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
        ywjl__zixh = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, ywjl__zixh)
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
        cmw__ekz = 20
        if len(arr) != 0:
            cmw__ekz = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * cmw__ekz)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    pex__kad = make_array(arrtype)
    gdddr__mve = pex__kad(context, builder)
    iahzp__jtfqk = context.get_data_type(arrtype.dtype)
    kuouq__wzwuz = context.get_constant(types.intp, get_itemsize(context,
        arrtype))
    xad__yav = context.get_constant(types.intp, 1)
    jiuwh__clg = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        hfzsi__vdllr = builder.smul_with_overflow(xad__yav, s)
        xad__yav = builder.extract_value(hfzsi__vdllr, 0)
        jiuwh__clg = builder.or_(jiuwh__clg, builder.extract_value(
            hfzsi__vdllr, 1))
    if arrtype.ndim == 0:
        bkca__vkyvk = ()
    elif arrtype.layout == 'C':
        bkca__vkyvk = [kuouq__wzwuz]
        for qlu__xrwo in reversed(shapes[1:]):
            bkca__vkyvk.append(builder.mul(bkca__vkyvk[-1], qlu__xrwo))
        bkca__vkyvk = tuple(reversed(bkca__vkyvk))
    elif arrtype.layout == 'F':
        bkca__vkyvk = [kuouq__wzwuz]
        for qlu__xrwo in shapes[:-1]:
            bkca__vkyvk.append(builder.mul(bkca__vkyvk[-1], qlu__xrwo))
        bkca__vkyvk = tuple(bkca__vkyvk)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    oazlx__ochtu = builder.smul_with_overflow(xad__yav, kuouq__wzwuz)
    zfbnz__zbj = builder.extract_value(oazlx__ochtu, 0)
    jiuwh__clg = builder.or_(jiuwh__clg, builder.extract_value(oazlx__ochtu, 1)
        )
    with builder.if_then(jiuwh__clg, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    mndx__tcb = context.get_preferred_array_alignment(dtype)
    rhw__neh = context.get_constant(types.uint32, mndx__tcb)
    qkfyp__bqn = context.nrt.meminfo_alloc_aligned(builder, size=zfbnz__zbj,
        align=rhw__neh)
    data = context.nrt.meminfo_data(builder, qkfyp__bqn)
    jfc__cwo = context.get_value_type(types.intp)
    xivk__fybgj = cgutils.pack_array(builder, shapes, ty=jfc__cwo)
    broi__neli = cgutils.pack_array(builder, bkca__vkyvk, ty=jfc__cwo)
    populate_array(gdddr__mve, data=builder.bitcast(data, iahzp__jtfqk.
        as_pointer()), shape=xivk__fybgj, strides=broi__neli, itemsize=
        kuouq__wzwuz, meminfo=qkfyp__bqn)
    return gdddr__mve


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    taii__ggji = []
    for hwamh__itd in arr_tup:
        taii__ggji.append(np.empty(n, hwamh__itd.dtype))
    return tuple(taii__ggji)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    iqc__nwwp = data.count
    lflsb__crklg = ','.join(['empty_like_type(n, data[{}])'.format(
        dsq__banpz) for dsq__banpz in range(iqc__nwwp)])
    if init_vals != ():
        lflsb__crklg = ','.join([
            'np.full(n, init_vals[{}], data[{}].dtype)'.format(dsq__banpz,
            dsq__banpz) for dsq__banpz in range(iqc__nwwp)])
    nccvr__axg = 'def f(n, data, init_vals=()):\n'
    nccvr__axg += '  return ({}{})\n'.format(lflsb__crklg, ',' if iqc__nwwp ==
        1 else '')
    myx__fab = {}
    exec(nccvr__axg, {'empty_like_type': empty_like_type, 'np': np}, myx__fab)
    vrgst__ipte = myx__fab['f']
    return vrgst__ipte


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
            lti__zrk = n * len(val)
            A = pre_alloc_string_array(n, lti__zrk)
            for dsq__banpz in range(n):
                A[dsq__banpz] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for dsq__banpz in range(n):
            A[dsq__banpz] = val
        return A
    return impl


@intrinsic
def get_ctypes_ptr(typingctx, ctypes_typ=None):
    assert isinstance(ctypes_typ, types.ArrayCTypes)

    def codegen(context, builder, sig, args):
        tzv__wft, = args
        cvwj__stnv = context.make_helper(builder, sig.args[0], tzv__wft)
        return cvwj__stnv.data
    return types.voidptr(ctypes_typ), codegen


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        zsf__kjkj, = args
        gksy__xqh = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', zsf__kjkj, gksy__xqh)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        bhhyk__teome = cgutils.alloca_once_value(builder, val)
        macw__hrb = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, bhhyk__teome, macw__hrb)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    nccvr__axg = 'def impl(A, data, elem_type):\n'
    nccvr__axg += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        nccvr__axg += (
            '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n')
    else:
        nccvr__axg += '    A[i] = d\n'
    myx__fab = {}
    exec(nccvr__axg, {'bodo': bodo}, myx__fab)
    impl = myx__fab['impl']
    return impl


def object_length(c, obj):
    pxy__dzt = c.context.get_argument_type(types.pyobject)
    jji__zcit = lir.FunctionType(lir.IntType(64), [pxy__dzt])
    mnnrz__rqj = cgutils.get_or_insert_function(c.builder.module, jji__zcit,
        name='PyObject_Length')
    return c.builder.call(mnnrz__rqj, (obj,))


def sequence_getitem(c, obj, ind):
    pxy__dzt = c.context.get_argument_type(types.pyobject)
    jji__zcit = lir.FunctionType(pxy__dzt, [pxy__dzt, lir.IntType(64)])
    mnnrz__rqj = cgutils.get_or_insert_function(c.builder.module, jji__zcit,
        name='PySequence_GetItem')
    return c.builder.call(mnnrz__rqj, (obj, ind))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        kce__bssr, = args
        context.nrt.incref(builder, signature.args[0], kce__bssr)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    kabso__hyy = out_var.loc
    dkk__kakmz = ir.Expr.static_getitem(in_var, ind, None, kabso__hyy)
    calltypes[dkk__kakmz] = None
    nodes.append(ir.Assign(dkk__kakmz, out_var, kabso__hyy))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            ywvm__shir = types.literal(node.index)
        except:
            ywvm__shir = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = ywvm__shir
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
    iev__xtj = re.sub('\\W+', '_', varname)
    if not iev__xtj or not iev__xtj[0].isalpha():
        iev__xtj = '_' + iev__xtj
    if not iev__xtj.isidentifier() or keyword.iskeyword(iev__xtj):
        iev__xtj = mk_unique_var('new_name').replace('.', '_')
    return iev__xtj


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            leso__hjl = len(A)
            for dsq__banpz in range(leso__hjl):
                yield A[leso__hjl - 1 - dsq__banpz]
        return impl_reversed


@numba.njit()
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit()
def nanvar_ddof1(a):
    pcwz__rog = count_nonnan(a)
    if pcwz__rog <= 1:
        return np.nan
    return np.nanvar(a) * (pcwz__rog / (pcwz__rog - 1))


@numba.njit()
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as egwtn__jak:
        iiosh__yrfz = False
    else:
        iiosh__yrfz = h5py.version.hdf5_version_tuple[1] == 10
    return iiosh__yrfz


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as egwtn__jak:
        ssgl__pvhet = False
    else:
        ssgl__pvhet = True
    return ssgl__pvhet


def has_scipy():
    try:
        import scipy
    except ImportError as egwtn__jak:
        vekic__eut = False
    else:
        vekic__eut = True
    return vekic__eut


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        slf__xoca = context.get_python_api(builder)
        phv__fhnl = slf__xoca.err_occurred()
        ikt__ubgbi = cgutils.is_not_null(builder, phv__fhnl)
        with builder.if_then(ikt__ubgbi):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    slf__xoca = context.get_python_api(builder)
    phv__fhnl = slf__xoca.err_occurred()
    ikt__ubgbi = cgutils.is_not_null(builder, phv__fhnl)
    with builder.if_then(ikt__ubgbi):
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
        vac__yovg = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install openjdk=8 -c conda-forge'."
            )
        raise BodoError(vac__yovg)


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
    inn__hmvgh = []
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in list must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
        inn__hmvgh.append(context.get_constant_generic(builder, typ.dtype, a))
    ivhaw__tnqn = context.get_constant_generic(builder, types.int64, len(pyval)
        )
    zeakb__obvkg = context.get_constant_generic(builder, types.bool_, False)
    zlg__xpze = context.get_constant_null(types.pyobject)
    gogyd__jjgoe = lir.Constant.literal_struct([ivhaw__tnqn, ivhaw__tnqn,
        zeakb__obvkg] + inn__hmvgh)
    gogyd__jjgoe = cgutils.global_constant(builder, '.const.payload',
        gogyd__jjgoe).bitcast(cgutils.voidptr_t)
    ctr__uqi = context.get_constant(types.int64, -1)
    lihdx__nxwp = context.get_constant_null(types.voidptr)
    qkfyp__bqn = lir.Constant.literal_struct([ctr__uqi, lihdx__nxwp,
        lihdx__nxwp, gogyd__jjgoe, ctr__uqi])
    qkfyp__bqn = cgutils.global_constant(builder, '.const.meminfo', qkfyp__bqn
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([qkfyp__bqn, zlg__xpze])


@lower_constant(types.Set)
def lower_constant_set(context, builder, typ, pyval):
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in set must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
    qqgfw__frcp = types.List(typ.dtype)
    fvwoq__klqgr = context.get_constant_generic(builder, qqgfw__frcp, list(
        pyval))
    vao__giv = context.compile_internal(builder, lambda l: set(l), types.
        Set(typ.dtype)(qqgfw__frcp), [fvwoq__klqgr])
    return vao__giv


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    fnzp__kzf = pd.Series(pyval.keys()).values
    arqq__hlv = pd.Series(pyval.values()).values
    bun__fumtj = bodo.typeof(fnzp__kzf)
    dkkdd__adgo = bodo.typeof(arqq__hlv)
    require(bun__fumtj.dtype == typ.key_type or can_replace(typ.key_type,
        bun__fumtj.dtype))
    require(dkkdd__adgo.dtype == typ.value_type or can_replace(typ.
        value_type, dkkdd__adgo.dtype))
    qcdh__whv = context.get_constant_generic(builder, bun__fumtj, fnzp__kzf)
    tlpz__hff = context.get_constant_generic(builder, dkkdd__adgo, arqq__hlv)

    def create_dict(keys, vals):
        wjskz__mfow = {}
        for k, v in zip(keys, vals):
            wjskz__mfow[k] = v
        return wjskz__mfow
    ftd__bot = context.compile_internal(builder, create_dict, typ(
        bun__fumtj, dkkdd__adgo), [qcdh__whv, tlpz__hff])
    return ftd__bot


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
    hnq__cpr = typ.key_type
    tbxa__hmgs = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(hnq__cpr, tbxa__hmgs)
    ftd__bot = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        gpbbt__kwfhv = context.get_constant_generic(builder, hnq__cpr, k)
        ico__njjy = context.get_constant_generic(builder, tbxa__hmgs, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            hnq__cpr, tbxa__hmgs), [ftd__bot, gpbbt__kwfhv, ico__njjy])
    return ftd__bot
