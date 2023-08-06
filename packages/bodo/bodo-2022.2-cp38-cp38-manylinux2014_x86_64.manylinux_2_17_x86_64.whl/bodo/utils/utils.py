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
    snb__ijm = guard(get_definition, func_ir, var)
    if snb__ijm is None:
        return default
    if isinstance(snb__ijm, ir.Const):
        return snb__ijm.value
    if isinstance(snb__ijm, ir.Var):
        return get_constant(func_ir, snb__ijm, default)
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
    bvqn__ytvpa = get_definition(func_ir, var)
    require(isinstance(bvqn__ytvpa, ir.Expr))
    require(bvqn__ytvpa.op == 'build_tuple')
    return bvqn__ytvpa.items


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
    for zie__xyqat, val in enumerate(args):
        typ = sig.args[zie__xyqat]
        if isinstance(typ, types.ArrayCTypes):
            cgutils.printf(builder, '%p ', val)
            continue
        flxvy__bjn = typ_to_format[typ]
        cgutils.printf(builder, '%{} '.format(flxvy__bjn), val)
    cgutils.printf(builder, '\n')
    return context.get_dummy_value()


def is_whole_slice(typemap, func_ir, var, accept_stride=False):
    require(typemap[var.name] == types.slice2_type or accept_stride and 
        typemap[var.name] == types.slice3_type)
    byp__bbx = get_definition(func_ir, var)
    require(isinstance(byp__bbx, ir.Expr) and byp__bbx.op == 'call')
    assert len(byp__bbx.args) == 2 or accept_stride and len(byp__bbx.args) == 3
    assert find_callname(func_ir, byp__bbx) == ('slice', 'builtins')
    dudsb__biex = get_definition(func_ir, byp__bbx.args[0])
    rcufo__vrof = get_definition(func_ir, byp__bbx.args[1])
    require(isinstance(dudsb__biex, ir.Const) and dudsb__biex.value == None)
    require(isinstance(rcufo__vrof, ir.Const) and rcufo__vrof.value == None)
    return True


def is_slice_equiv_arr(arr_var, index_var, func_ir, equiv_set,
    accept_stride=False):
    gag__hbsvr = get_definition(func_ir, index_var)
    require(find_callname(func_ir, gag__hbsvr) == ('slice', 'builtins'))
    require(len(gag__hbsvr.args) in (2, 3))
    require(find_const(func_ir, gag__hbsvr.args[0]) in (0, None))
    require(equiv_set.is_equiv(gag__hbsvr.args[1], arr_var.name + '#0'))
    require(accept_stride or len(gag__hbsvr.args) == 2 or find_const(
        func_ir, gag__hbsvr.args[2]) == 1)
    return True


def get_slice_step(typemap, func_ir, var):
    require(typemap[var.name] == types.slice3_type)
    byp__bbx = get_definition(func_ir, var)
    require(isinstance(byp__bbx, ir.Expr) and byp__bbx.op == 'call')
    assert len(byp__bbx.args) == 3
    return byp__bbx.args[2]


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
        xdudc__fnule = False
        for zie__xyqat in range(len(A)):
            if bodo.libs.array_kernels.isna(A, zie__xyqat):
                xdudc__fnule = True
                continue
            s[A[zie__xyqat]] = 0
        return s, xdudc__fnule
    return impl


@numba.generated_jit(nopython=True, cache=True)
def build_set(A):
    if isinstance(A, IntegerArrayType) or A in (string_array_type,
        boolean_array):

        def impl_int_arr(A):
            s = dict()
            for zie__xyqat in range(len(A)):
                if not bodo.libs.array_kernels.isna(A, zie__xyqat):
                    s[A[zie__xyqat]] = 0
            return s
        return impl_int_arr
    else:

        def impl(A):
            s = dict()
            for zie__xyqat in range(len(A)):
                s[A[zie__xyqat]] = 0
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
            zie__xyqat = 0
            for v in A.keys():
                arr[zie__xyqat] = v
                zie__xyqat += 1
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
        psng__itl = arr.dtype

        def empty_like_type_int_arr(n, arr):
            return bodo.libs.int_arr_ext.alloc_int_array(n, psng__itl)
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
        nvzun__irkpp = 20
        if len(arr) != 0:
            nvzun__irkpp = num_total_chars(arr) // len(arr)
        return pre_alloc_string_array(n, n * nvzun__irkpp)
    return empty_like_type_str_arr


def _empty_nd_impl(context, builder, arrtype, shapes):
    jli__gfhxz = make_array(arrtype)
    zlfez__eqrcv = jli__gfhxz(context, builder)
    xpue__uew = context.get_data_type(arrtype.dtype)
    wyyzb__xwjg = context.get_constant(types.intp, get_itemsize(context,
        arrtype))
    nxht__yrjz = context.get_constant(types.intp, 1)
    vnq__hjw = lir.Constant(lir.IntType(1), 0)
    for s in shapes:
        ixt__sxy = builder.smul_with_overflow(nxht__yrjz, s)
        nxht__yrjz = builder.extract_value(ixt__sxy, 0)
        vnq__hjw = builder.or_(vnq__hjw, builder.extract_value(ixt__sxy, 1))
    if arrtype.ndim == 0:
        zuz__lhmj = ()
    elif arrtype.layout == 'C':
        zuz__lhmj = [wyyzb__xwjg]
        for fhner__svi in reversed(shapes[1:]):
            zuz__lhmj.append(builder.mul(zuz__lhmj[-1], fhner__svi))
        zuz__lhmj = tuple(reversed(zuz__lhmj))
    elif arrtype.layout == 'F':
        zuz__lhmj = [wyyzb__xwjg]
        for fhner__svi in shapes[:-1]:
            zuz__lhmj.append(builder.mul(zuz__lhmj[-1], fhner__svi))
        zuz__lhmj = tuple(zuz__lhmj)
    else:
        raise NotImplementedError(
            "Don't know how to allocate array with layout '{0}'.".format(
            arrtype.layout))
    zuzz__dqvey = builder.smul_with_overflow(nxht__yrjz, wyyzb__xwjg)
    jvv__qhiv = builder.extract_value(zuzz__dqvey, 0)
    vnq__hjw = builder.or_(vnq__hjw, builder.extract_value(zuzz__dqvey, 1))
    with builder.if_then(vnq__hjw, likely=False):
        cgutils.printf(builder,
            'array is too big; `arr.size * arr.dtype.itemsize` is larger than the maximum possible size.'
            )
    dtype = arrtype.dtype
    domsg__mtyln = context.get_preferred_array_alignment(dtype)
    jpkvq__entjn = context.get_constant(types.uint32, domsg__mtyln)
    dzts__zqjde = context.nrt.meminfo_alloc_aligned(builder, size=jvv__qhiv,
        align=jpkvq__entjn)
    data = context.nrt.meminfo_data(builder, dzts__zqjde)
    relcv__mrkb = context.get_value_type(types.intp)
    qfkm__qng = cgutils.pack_array(builder, shapes, ty=relcv__mrkb)
    gvzx__bazfu = cgutils.pack_array(builder, zuz__lhmj, ty=relcv__mrkb)
    populate_array(zlfez__eqrcv, data=builder.bitcast(data, xpue__uew.
        as_pointer()), shape=qfkm__qng, strides=gvzx__bazfu, itemsize=
        wyyzb__xwjg, meminfo=dzts__zqjde)
    return zlfez__eqrcv


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.np.arrayobj._empty_nd_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b6a998927680caa35917a553c79704e9d813d8f1873d83a5f8513837c159fa29':
        warnings.warn('numba.np.arrayobj._empty_nd_impl has changed')


def alloc_arr_tup(n, arr_tup, init_vals=()):
    druzq__pxw = []
    for tzhi__zzuw in arr_tup:
        druzq__pxw.append(np.empty(n, tzhi__zzuw.dtype))
    return tuple(druzq__pxw)


@overload(alloc_arr_tup, no_unliteral=True)
def alloc_arr_tup_overload(n, data, init_vals=()):
    jdh__xdug = data.count
    umc__ztb = ','.join(['empty_like_type(n, data[{}])'.format(zie__xyqat) for
        zie__xyqat in range(jdh__xdug)])
    if init_vals != ():
        umc__ztb = ','.join(['np.full(n, init_vals[{}], data[{}].dtype)'.
            format(zie__xyqat, zie__xyqat) for zie__xyqat in range(jdh__xdug)])
    zbq__tiu = 'def f(n, data, init_vals=()):\n'
    zbq__tiu += '  return ({}{})\n'.format(umc__ztb, ',' if jdh__xdug == 1 else
        '')
    arcr__eqwr = {}
    exec(zbq__tiu, {'empty_like_type': empty_like_type, 'np': np}, arcr__eqwr)
    cns__trcdu = arcr__eqwr['f']
    return cns__trcdu


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
            prnm__jroxg = n * len(val)
            A = pre_alloc_string_array(n, prnm__jroxg)
            for zie__xyqat in range(n):
                A[zie__xyqat] = val
            return A
        return impl_str

    def impl(n, val, t):
        A = alloc_type(n, typ, (-1,))
        for zie__xyqat in range(n):
            A[zie__xyqat] = val
        return A
    return impl


@intrinsic
def get_ctypes_ptr(typingctx, ctypes_typ=None):
    assert isinstance(ctypes_typ, types.ArrayCTypes)

    def codegen(context, builder, sig, args):
        vipyg__ixwgz, = args
        vkv__lxkrq = context.make_helper(builder, sig.args[0], vipyg__ixwgz)
        return vkv__lxkrq.data
    return types.voidptr(ctypes_typ), codegen


@intrinsic
def is_null_pointer(typingctx, ptr_typ=None):

    def codegen(context, builder, signature, args):
        qkn__xqdej, = args
        nwzho__wkye = context.get_constant_null(ptr_typ)
        return builder.icmp_unsigned('==', qkn__xqdej, nwzho__wkye)
    return types.bool_(ptr_typ), codegen


@intrinsic
def is_null_value(typingctx, val_typ=None):

    def codegen(context, builder, signature, args):
        val, = args
        cxnn__uultl = cgutils.alloca_once_value(builder, val)
        gcd__iiak = cgutils.alloca_once_value(builder, context.
            get_constant_null(val_typ))
        return is_ll_eq(builder, cxnn__uultl, gcd__iiak)
    return types.bool_(val_typ), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def tuple_list_to_array(A, data, elem_type):
    elem_type = elem_type.instance_type if isinstance(elem_type, types.TypeRef
        ) else elem_type
    zbq__tiu = 'def impl(A, data, elem_type):\n'
    zbq__tiu += '  for i, d in enumerate(data):\n'
    if elem_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        zbq__tiu += '    A[i] = bodo.utils.conversion.unbox_if_timestamp(d)\n'
    else:
        zbq__tiu += '    A[i] = d\n'
    arcr__eqwr = {}
    exec(zbq__tiu, {'bodo': bodo}, arcr__eqwr)
    impl = arcr__eqwr['impl']
    return impl


def object_length(c, obj):
    bmcag__slqlk = c.context.get_argument_type(types.pyobject)
    kczv__ewu = lir.FunctionType(lir.IntType(64), [bmcag__slqlk])
    jwu__ltqyw = cgutils.get_or_insert_function(c.builder.module, kczv__ewu,
        name='PyObject_Length')
    return c.builder.call(jwu__ltqyw, (obj,))


def sequence_getitem(c, obj, ind):
    bmcag__slqlk = c.context.get_argument_type(types.pyobject)
    kczv__ewu = lir.FunctionType(bmcag__slqlk, [bmcag__slqlk, lir.IntType(64)])
    jwu__ltqyw = cgutils.get_or_insert_function(c.builder.module, kczv__ewu,
        name='PySequence_GetItem')
    return c.builder.call(jwu__ltqyw, (obj, ind))


@intrinsic
def incref(typingctx, data=None):

    def codegen(context, builder, signature, args):
        zclxo__cpp, = args
        context.nrt.incref(builder, signature.args[0], zclxo__cpp)
    return types.void(data), codegen


def gen_getitem(out_var, in_var, ind, calltypes, nodes):
    pytr__tlfgn = out_var.loc
    ofeqv__hbssa = ir.Expr.static_getitem(in_var, ind, None, pytr__tlfgn)
    calltypes[ofeqv__hbssa] = None
    nodes.append(ir.Assign(ofeqv__hbssa, out_var, pytr__tlfgn))


def is_static_getsetitem(node):
    return is_expr(node, 'static_getitem') or isinstance(node, ir.StaticSetItem
        )


def get_getsetitem_index_var(node, typemap, nodes):
    index_var = node.index_var if is_static_getsetitem(node) else node.index
    if index_var is None:
        assert is_static_getsetitem(node)
        try:
            imo__kofim = types.literal(node.index)
        except:
            imo__kofim = numba.typeof(node.index)
        index_var = ir.Var(node.value.scope, ir_utils.mk_unique_var(
            'dummy_index'), node.loc)
        typemap[index_var.name] = imo__kofim
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
    bskp__beb = re.sub('\\W+', '_', varname)
    if not bskp__beb or not bskp__beb[0].isalpha():
        bskp__beb = '_' + bskp__beb
    if not bskp__beb.isidentifier() or keyword.iskeyword(bskp__beb):
        bskp__beb = mk_unique_var('new_name').replace('.', '_')
    return bskp__beb


def dump_node_list(node_list):
    for n in node_list:
        print('   ', n)


def debug_prints():
    return numba.core.config.DEBUG_ARRAY_OPT == 1


@overload(reversed)
def list_reverse(A):
    if isinstance(A, types.List):

        def impl_reversed(A):
            dseqx__xhv = len(A)
            for zie__xyqat in range(dseqx__xhv):
                yield A[dseqx__xhv - 1 - zie__xyqat]
        return impl_reversed


@numba.njit()
def count_nonnan(a):
    return np.count_nonzero(~np.isnan(a))


@numba.njit()
def nanvar_ddof1(a):
    cgjn__hlus = count_nonnan(a)
    if cgjn__hlus <= 1:
        return np.nan
    return np.nanvar(a) * (cgjn__hlus / (cgjn__hlus - 1))


@numba.njit()
def nanstd_ddof1(a):
    return np.sqrt(nanvar_ddof1(a))


def has_supported_h5py():
    try:
        import h5py
        from bodo.io import _hdf5
    except ImportError as org__zxdea:
        wxxpz__lymfs = False
    else:
        wxxpz__lymfs = h5py.version.hdf5_version_tuple[1] == 10
    return wxxpz__lymfs


def check_h5py():
    if not has_supported_h5py():
        raise BodoError("install 'h5py' package to enable hdf5 support")


def has_pyarrow():
    try:
        import pyarrow
    except ImportError as org__zxdea:
        ufxq__brha = False
    else:
        ufxq__brha = True
    return ufxq__brha


def has_scipy():
    try:
        import scipy
    except ImportError as org__zxdea:
        uvd__yqc = False
    else:
        uvd__yqc = True
    return uvd__yqc


@intrinsic
def check_and_propagate_cpp_exception(typingctx):

    def codegen(context, builder, sig, args):
        gqj__xfh = context.get_python_api(builder)
        enetc__ufzb = gqj__xfh.err_occurred()
        qvyn__lsphf = cgutils.is_not_null(builder, enetc__ufzb)
        with builder.if_then(qvyn__lsphf):
            builder.ret(numba.core.callconv.RETCODE_EXC)
    return types.void(), codegen


def inlined_check_and_propagate_cpp_exception(context, builder):
    gqj__xfh = context.get_python_api(builder)
    enetc__ufzb = gqj__xfh.err_occurred()
    qvyn__lsphf = cgutils.is_not_null(builder, enetc__ufzb)
    with builder.if_then(qvyn__lsphf):
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
        uelhn__fbmf = (
            "Java not found. Make sure openjdk is installed for hdfs. openjdk can be installed by calling 'conda install openjdk=8 -c conda-forge'."
            )
        raise BodoError(uelhn__fbmf)


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
    bsms__zoldw = []
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in list must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
        bsms__zoldw.append(context.get_constant_generic(builder, typ.dtype, a))
    agkd__ygo = context.get_constant_generic(builder, types.int64, len(pyval))
    qbg__auo = context.get_constant_generic(builder, types.bool_, False)
    qccqq__ypakg = context.get_constant_null(types.pyobject)
    bxce__umckw = lir.Constant.literal_struct([agkd__ygo, agkd__ygo,
        qbg__auo] + bsms__zoldw)
    bxce__umckw = cgutils.global_constant(builder, '.const.payload',
        bxce__umckw).bitcast(cgutils.voidptr_t)
    sqm__kafm = context.get_constant(types.int64, -1)
    ekfa__tyqqo = context.get_constant_null(types.voidptr)
    dzts__zqjde = lir.Constant.literal_struct([sqm__kafm, ekfa__tyqqo,
        ekfa__tyqqo, bxce__umckw, sqm__kafm])
    dzts__zqjde = cgutils.global_constant(builder, '.const.meminfo',
        dzts__zqjde).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([dzts__zqjde, qccqq__ypakg])


@lower_constant(types.Set)
def lower_constant_set(context, builder, typ, pyval):
    for a in pyval:
        if bodo.typeof(a) != typ.dtype:
            raise BodoError(
                f'Values in set must have the same data type for type stability. Expected: {typ.dtype}, Actual: {bodo.typeof(a)}'
                )
    bsh__ygim = types.List(typ.dtype)
    udxl__byjj = context.get_constant_generic(builder, bsh__ygim, list(pyval))
    fmi__cwcf = context.compile_internal(builder, lambda l: set(l), types.
        Set(typ.dtype)(bsh__ygim), [udxl__byjj])
    return fmi__cwcf


def lower_const_dict_fast_path(context, builder, typ, pyval):
    from bodo.utils.typing import can_replace
    kvf__djja = pd.Series(pyval.keys()).values
    tdsea__jlw = pd.Series(pyval.values()).values
    umakz__hbj = bodo.typeof(kvf__djja)
    cwck__cuby = bodo.typeof(tdsea__jlw)
    require(umakz__hbj.dtype == typ.key_type or can_replace(typ.key_type,
        umakz__hbj.dtype))
    require(cwck__cuby.dtype == typ.value_type or can_replace(typ.
        value_type, cwck__cuby.dtype))
    hma__xudc = context.get_constant_generic(builder, umakz__hbj, kvf__djja)
    cnol__wkj = context.get_constant_generic(builder, cwck__cuby, tdsea__jlw)

    def create_dict(keys, vals):
        twqtr__zwsp = {}
        for k, v in zip(keys, vals):
            twqtr__zwsp[k] = v
        return twqtr__zwsp
    niybg__jvfr = context.compile_internal(builder, create_dict, typ(
        umakz__hbj, cwck__cuby), [hma__xudc, cnol__wkj])
    return niybg__jvfr


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
    kvbu__sqnm = typ.key_type
    wdqne__jbzp = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(kvbu__sqnm, wdqne__jbzp)
    niybg__jvfr = context.compile_internal(builder, make_dict, typ(), [])

    def set_dict_val(d, k, v):
        d[k] = v
    for k, v in pyval.items():
        moz__flgp = context.get_constant_generic(builder, kvbu__sqnm, k)
        ydtw__xlju = context.get_constant_generic(builder, wdqne__jbzp, v)
        context.compile_internal(builder, set_dict_val, types.none(typ,
            kvbu__sqnm, wdqne__jbzp), [niybg__jvfr, moz__flgp, ydtw__xlju])
    return niybg__jvfr
