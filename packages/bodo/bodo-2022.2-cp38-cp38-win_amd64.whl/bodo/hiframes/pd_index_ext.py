import datetime
import operator
import warnings
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        return NumericIndexType(types.int64, get_val_type_maybe_str_literal
            (val.name), IntegerArrayType(types.int64))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.NPDatetime('ns')

    def copy(self):
        return DatetimeIndexType(self.name_typ)

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(_dt_index_data_typ)

    @property
    def pandas_type_name(self):
        return 'datetime64'

    @property
    def numpy_type_name(self):
        return 'datetime64[ns]'


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', _dt_index_data_typ), ('name', fe_type.
            name_typ), ('dict', types.DictType(_dt_index_data_typ.dtype,
            types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    tyiq__tyjd = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', hevr__blzat, idx_cpy_arg_defaults,
        fn_str=tyiq__tyjd, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    tmro__rav = c.pyapi.import_module_noblock(vmffd__loxx)
    xfpm__ran = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, _dt_index_data_typ, xfpm__ran.data)
    xgxix__fbqby = c.pyapi.from_native_value(_dt_index_data_typ, xfpm__ran.
        data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, xfpm__ran.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, xfpm__ran.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([xgxix__fbqby])
    kws = c.pyapi.dict_pack([('name', kyh__qplx)])
    hqq__hqur = c.pyapi.object_getattr_string(tmro__rav, 'DatetimeIndex')
    lze__cuoae = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(xgxix__fbqby)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(tmro__rav)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lze__cuoae


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_dt_index_data_typ, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    dtype = _dt_index_data_typ.dtype
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        rflel__eoe, cjuf__cfci = args
        xfpm__ran = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        xfpm__ran.data = rflel__eoe
        xfpm__ran.name = cjuf__cfci
        context.nrt.incref(builder, signature.args[0], rflel__eoe)
        context.nrt.incref(builder, signature.args[1], cjuf__cfci)
        dtype = _dt_index_data_typ.dtype
        xfpm__ran.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return xfpm__ran._getvalue()
    ihguu__dayp = DatetimeIndexType(name)
    sig = signature(ihguu__dayp, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    effxg__lzy = args[0]
    if equiv_set.has_shape(effxg__lzy):
        return ArrayAnalysis.AnalyzeResult(shape=effxg__lzy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    jbr__hoecj = 'def impl(dti):\n'
    jbr__hoecj += '    numba.parfors.parfor.init_prange()\n'
    jbr__hoecj += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    jbr__hoecj += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    jbr__hoecj += '    n = len(A)\n'
    jbr__hoecj += '    S = np.empty(n, np.int64)\n'
    jbr__hoecj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    jbr__hoecj += (
        '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])\n'
        )
    jbr__hoecj += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
    if field in ['weekday']:
        jbr__hoecj += '        S[i] = ts.' + field + '()\n'
    else:
        jbr__hoecj += '        S[i] = ts.' + field + '\n'
    jbr__hoecj += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'numba': numba, 'np': np, 'bodo': bodo}, xmbha__zqfs)
    impl = xmbha__zqfs['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        aytqn__dymf = len(A)
        S = np.empty(aytqn__dymf, np.bool_)
        for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
            mmifm__ogog = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            nwvn__kqlz = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(mmifm__ogog))
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(nwvn__kqlz.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        aytqn__dymf = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            aytqn__dymf)
        for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
            mmifm__ogog = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            nwvn__kqlz = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(mmifm__ogog))
            S[i] = datetime.date(nwvn__kqlz.year, nwvn__kqlz.month,
                nwvn__kqlz.day)
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    wzxde__qtgni = dict(axis=axis, skipna=skipna)
    vkmp__vxuy = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        hlusm__tks = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(hlusm__tks)):
            if not bodo.libs.array_kernels.isna(hlusm__tks, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(hlusm__tks
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    wzxde__qtgni = dict(axis=axis, skipna=skipna)
    vkmp__vxuy = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        hlusm__tks = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(hlusm__tks)):
            if not bodo.libs.array_kernels.isna(hlusm__tks, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(hlusm__tks
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    wzxde__qtgni = dict(freq=freq, tz=tz, normalize=normalize, closed=
        closed, ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst,
        dtype=dtype, copy=copy)
    vkmp__vxuy = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        wpdro__vig = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(wpdro__vig)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        rapen__vui = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            hlusm__tks = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            aytqn__dymf = len(hlusm__tks)
            S = np.empty(aytqn__dymf, rapen__vui)
            bozwz__kcfll = rhs.value
            for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hlusm__tks[i]) - bozwz__kcfll)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        rapen__vui = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            hlusm__tks = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            aytqn__dymf = len(hlusm__tks)
            S = np.empty(aytqn__dymf, rapen__vui)
            bozwz__kcfll = lhs.value
            for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bozwz__kcfll - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(hlusm__tks[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    dso__uyx = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    jbr__hoecj = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        jbr__hoecj += '  dt_index, _str = lhs, rhs\n'
        dvl__aegpz = 'arr[i] {} other'.format(dso__uyx)
    else:
        jbr__hoecj += '  dt_index, _str = rhs, lhs\n'
        dvl__aegpz = 'other {} arr[i]'.format(dso__uyx)
    jbr__hoecj += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    jbr__hoecj += '  l = len(arr)\n'
    jbr__hoecj += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    jbr__hoecj += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    jbr__hoecj += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    jbr__hoecj += '    S[i] = {}\n'.format(dvl__aegpz)
    jbr__hoecj += '  return S\n'
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'bodo': bodo, 'numba': numba, 'np': np}, xmbha__zqfs)
    impl = xmbha__zqfs['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    dyq__cicod = getattr(data, 'dtype', None)
    if not is_overload_none(dtype):
        dbi__yrf = parse_dtype(dtype, 'pandas.Index')
    else:
        dbi__yrf = dyq__cicod
    if isinstance(dbi__yrf, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or dbi__yrf == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType) or dbi__yrf == types.NPTimedelta(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(dbi__yrf, (types.Integer, types.Float, types.Boolean)):

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                wpdro__vig = bodo.utils.conversion.coerce_to_array(data)
                ykw__kvtz = bodo.utils.conversion.fix_arr_dtype(wpdro__vig,
                    dbi__yrf)
                return bodo.hiframes.pd_index_ext.init_numeric_index(ykw__kvtz,
                    name)
        elif dbi__yrf in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                clgs__jmi = bodo.hiframes.pd_index_ext.get_index_data(dti)
                mmifm__ogog = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    clgs__jmi[ind])
                return (bodo.hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(mmifm__ogog))
            return impl
        else:

            def impl(dti, ind):
                clgs__jmi = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                vhjgm__rytw = clgs__jmi[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    vhjgm__rytw, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            fokyx__ucfdy = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(fokyx__ucfdy[ind])
        return impl

    def impl(I, ind):
        fokyx__ucfdy = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        vhjgm__rytw = fokyx__ucfdy[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(vhjgm__rytw,
            name)
    return impl


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    hlidc__dnyic = False
    koy__oogt = False
    if closed is None:
        hlidc__dnyic = True
        koy__oogt = True
    elif closed == 'left':
        hlidc__dnyic = True
    elif closed == 'right':
        koy__oogt = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return hlidc__dnyic, koy__oogt


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, no_unliteral=True)
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    wzxde__qtgni = dict(tz=tz, normalize=normalize)
    vkmp__vxuy = dict(tz=None, normalize=False)
    check_unsupported_args('pandas.date_range', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise BodoError('pd.date_range(): tz argument not supported yet')
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, tz=None, normalize
        =False, name=None, closed=None):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        xbkmo__gxdkt = pd.Timestamp('2018-01-01')
        if start is not None:
            xbkmo__gxdkt = pd.Timestamp(start)
        kaw__ycjpa = pd.Timestamp('2018-01-01')
        if end is not None:
            kaw__ycjpa = pd.Timestamp(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of startand end are defined'
                )
        hlidc__dnyic, koy__oogt = (bodo.hiframes.pd_index_ext.
            validate_endpoints(closed))
        if freq is not None:
            mvma__jrrq = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = xbkmo__gxdkt.value
                omv__qycun = b + (kaw__ycjpa.value - b
                    ) // mvma__jrrq * mvma__jrrq + mvma__jrrq // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = xbkmo__gxdkt.value
                sed__ptkyr = np.int64(periods) * np.int64(mvma__jrrq)
                omv__qycun = np.int64(b) + sed__ptkyr
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                omv__qycun = kaw__ycjpa.value + mvma__jrrq
                sed__ptkyr = np.int64(periods) * np.int64(-mvma__jrrq)
                b = np.int64(omv__qycun) + sed__ptkyr
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            hjr__krwn = np.arange(b, omv__qycun, mvma__jrrq, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            cqw__npbcn = kaw__ycjpa.value - xbkmo__gxdkt.value
            step = cqw__npbcn / (periods - 1)
            znfic__vmhv = np.arange(0, periods, 1, np.float64)
            znfic__vmhv *= step
            znfic__vmhv += xbkmo__gxdkt.value
            hjr__krwn = znfic__vmhv.astype(np.int64)
            hjr__krwn[-1] = kaw__ycjpa.value
        if not hlidc__dnyic and len(hjr__krwn) and hjr__krwn[0
            ] == xbkmo__gxdkt.value:
            hjr__krwn = hjr__krwn[1:]
        if not koy__oogt and len(hjr__krwn) and hjr__krwn[-1
            ] == kaw__ycjpa.value:
            hjr__krwn = hjr__krwn[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(hjr__krwn)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        xbkmo__gxdkt = pd.Timedelta('1 day')
        if start is not None:
            xbkmo__gxdkt = pd.Timedelta(start)
        kaw__ycjpa = pd.Timedelta('1 day')
        if end is not None:
            kaw__ycjpa = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        hlidc__dnyic, koy__oogt = (bodo.hiframes.pd_index_ext.
            validate_endpoints(closed))
        if freq is not None:
            mvma__jrrq = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = xbkmo__gxdkt.value
                omv__qycun = b + (kaw__ycjpa.value - b
                    ) // mvma__jrrq * mvma__jrrq + mvma__jrrq // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = xbkmo__gxdkt.value
                sed__ptkyr = np.int64(periods) * np.int64(mvma__jrrq)
                omv__qycun = np.int64(b) + sed__ptkyr
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                omv__qycun = kaw__ycjpa.value + mvma__jrrq
                sed__ptkyr = np.int64(periods) * np.int64(-mvma__jrrq)
                b = np.int64(omv__qycun) + sed__ptkyr
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            hjr__krwn = np.arange(b, omv__qycun, mvma__jrrq, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            cqw__npbcn = kaw__ycjpa.value - xbkmo__gxdkt.value
            step = cqw__npbcn / (periods - 1)
            znfic__vmhv = np.arange(0, periods, 1, np.float64)
            znfic__vmhv *= step
            znfic__vmhv += xbkmo__gxdkt.value
            hjr__krwn = znfic__vmhv.astype(np.int64)
            hjr__krwn[-1] = kaw__ycjpa.value
        if not hlidc__dnyic and len(hjr__krwn) and hjr__krwn[0
            ] == xbkmo__gxdkt.value:
            hjr__krwn = hjr__krwn[1:]
        if not koy__oogt and len(hjr__krwn) and hjr__krwn[-1
            ] == kaw__ycjpa.value:
            hjr__krwn = hjr__krwn[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(hjr__krwn)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        aytqn__dymf = len(A)
        riflg__row = bodo.libs.int_arr_ext.alloc_int_array(aytqn__dymf, np.
            uint32)
        owhzb__xder = bodo.libs.int_arr_ext.alloc_int_array(aytqn__dymf, np
            .uint32)
        jlv__qcd = bodo.libs.int_arr_ext.alloc_int_array(aytqn__dymf, np.uint32
            )
        for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(riflg__row, i)
                bodo.libs.array_kernels.setna(owhzb__xder, i)
                bodo.libs.array_kernels.setna(jlv__qcd, i)
                continue
            riflg__row[i], owhzb__xder[i], jlv__qcd[i
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((riflg__row,
            owhzb__xder, jlv__qcd), idx, ('year', 'week', 'day'))
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(_timedelta_index_data_typ)

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', _timedelta_index_data_typ), ('name',
            fe_type.name_typ), ('dict', types.DictType(
            _timedelta_index_data_typ.dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, yoag__zpnzc
            )


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    tmro__rav = c.pyapi.import_module_noblock(vmffd__loxx)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    xgxix__fbqby = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([xgxix__fbqby])
    kws = c.pyapi.dict_pack([('name', kyh__qplx)])
    hqq__hqur = c.pyapi.object_getattr_string(tmro__rav, 'TimedeltaIndex')
    lze__cuoae = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(xgxix__fbqby)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(tmro__rav)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lze__cuoae


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    dtype = _timedelta_index_data_typ.dtype
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        rflel__eoe, cjuf__cfci = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = rflel__eoe
        timedelta_index.name = cjuf__cfci
        context.nrt.incref(builder, signature.args[0], rflel__eoe)
        context.nrt.incref(builder, signature.args[1], cjuf__cfci)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    ihguu__dayp = TimedeltaIndexType(name)
    sig = signature(ihguu__dayp, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    tyiq__tyjd = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', hevr__blzat,
        idx_cpy_arg_defaults, fn_str=tyiq__tyjd, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    wzxde__qtgni = dict(axis=axis, skipna=skipna)
    vkmp__vxuy = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        aytqn__dymf = len(data)
        zsj__vjgow = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            zsj__vjgow = min(zsj__vjgow, val)
        xmhaq__ejpck = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            zsj__vjgow)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(xmhaq__ejpck, count
            )
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    wzxde__qtgni = dict(axis=axis, skipna=skipna)
    vkmp__vxuy = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        aytqn__dymf = len(data)
        rspdp__nir = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            rspdp__nir = max(rspdp__nir, val)
        xmhaq__ejpck = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            rspdp__nir)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(xmhaq__ejpck, count
            )
    return impl


def gen_tdi_field_impl(field):
    jbr__hoecj = 'def impl(tdi):\n'
    jbr__hoecj += '    numba.parfors.parfor.init_prange()\n'
    jbr__hoecj += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    jbr__hoecj += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    jbr__hoecj += '    n = len(A)\n'
    jbr__hoecj += '    S = np.empty(n, np.int64)\n'
    jbr__hoecj += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    jbr__hoecj += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        jbr__hoecj += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        jbr__hoecj += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        jbr__hoecj += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        jbr__hoecj += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    jbr__hoecj += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'numba': numba, 'np': np, 'bodo': bodo}, xmbha__zqfs)
    impl = xmbha__zqfs['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    wzxde__qtgni = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    vkmp__vxuy = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', wzxde__qtgni,
        vkmp__vxuy, package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        wpdro__vig = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(wpdro__vig)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name='RangeIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    tyiq__tyjd = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', hevr__blzat,
        idx_cpy_arg_defaults, fn_str=tyiq__tyjd, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    fuegs__nqyd = c.pyapi.import_module_noblock(vmffd__loxx)
    rpq__gdzlx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    fqryn__jim = c.pyapi.from_native_value(types.int64, rpq__gdzlx.start, c
        .env_manager)
    vyfbj__isp = c.pyapi.from_native_value(types.int64, rpq__gdzlx.stop, c.
        env_manager)
    soeem__fervt = c.pyapi.from_native_value(types.int64, rpq__gdzlx.step,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rpq__gdzlx.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, rpq__gdzlx.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([fqryn__jim, vyfbj__isp, soeem__fervt])
    kws = c.pyapi.dict_pack([('name', kyh__qplx)])
    hqq__hqur = c.pyapi.object_getattr_string(fuegs__nqyd, 'RangeIndex')
    smg__chhze = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(fqryn__jim)
    c.pyapi.decref(vyfbj__isp)
    c.pyapi.decref(soeem__fervt)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(fuegs__nqyd)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return smg__chhze


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        rpq__gdzlx = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        rpq__gdzlx.start = args[0]
        rpq__gdzlx.stop = args[1]
        rpq__gdzlx.step = args[2]
        rpq__gdzlx.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return rpq__gdzlx._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, vkxr__kml = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    fqryn__jim = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, fqryn__jim).value
    vyfbj__isp = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, vyfbj__isp).value
    soeem__fervt = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, soeem__fervt).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(fqryn__jim)
    c.pyapi.decref(vyfbj__isp)
    c.pyapi.decref(soeem__fervt)
    c.pyapi.decref(kyh__qplx)
    rpq__gdzlx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rpq__gdzlx.start = start
    rpq__gdzlx.stop = stop
    rpq__gdzlx.step = step
    rpq__gdzlx.name = name
    return NativeValue(rpq__gdzlx._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        ipb__tdz = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(ipb__tdz.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        ipb__tdz = 'RangeIndex(...) must be called with integers'
        raise BodoError(ipb__tdz)
    zjmy__zaku = 'start'
    jvyr__qmoue = 'stop'
    qhu__dwgo = 'step'
    if is_overload_none(start):
        zjmy__zaku = '0'
    if is_overload_none(stop):
        jvyr__qmoue = 'start'
        zjmy__zaku = '0'
    if is_overload_none(step):
        qhu__dwgo = '1'
    jbr__hoecj = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    jbr__hoecj += '  return init_range_index({}, {}, {}, name)\n'.format(
        zjmy__zaku, jvyr__qmoue, qhu__dwgo)
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'init_range_index': init_range_index}, xmbha__zqfs)
    excr__lkyol = xmbha__zqfs['_pd_range_index_imp']
    return excr__lkyol


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                aetth__hvz = numba.cpython.unicode._normalize_slice(idx, len(I)
                    )
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * aetth__hvz.start
                stop = I._start + I._step * aetth__hvz.stop
                step = I._step * aetth__hvz.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(types.Array(types.int64, 1, 'C'))

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', bodo.IntegerArrayType(types.int64)), (
            'name', fe_type.name_typ), ('dict', types.DictType(types.int64,
            types.int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    tyiq__tyjd = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', hevr__blzat,
        idx_cpy_arg_defaults, fn_str=tyiq__tyjd, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        rflel__eoe, cjuf__cfci, vkxr__kml = args
        dot__ctm = signature.return_type
        lxvls__nls = cgutils.create_struct_proxy(dot__ctm)(context, builder)
        lxvls__nls.data = rflel__eoe
        lxvls__nls.name = cjuf__cfci
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        lxvls__nls.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return lxvls__nls._getvalue()
    hjoc__cqnaw = get_overload_const_str(freq)
    ihguu__dayp = PeriodIndexType(hjoc__cqnaw, name)
    sig = signature(ihguu__dayp, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    fuegs__nqyd = c.pyapi.import_module_noblock(vmffd__loxx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        ssl__hvoo.data)
    zns__abet = c.pyapi.from_native_value(bodo.IntegerArrayType(types.int64
        ), ssl__hvoo.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ssl__hvoo.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, ssl__hvoo.name, c.
        env_manager)
    ubu__has = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', zns__abet), ('name', kyh__qplx), (
        'freq', ubu__has)])
    hqq__hqur = c.pyapi.object_getattr_string(fuegs__nqyd, 'PeriodIndex')
    smg__chhze = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(zns__abet)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(ubu__has)
    c.pyapi.decref(fuegs__nqyd)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return smg__chhze


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    mldub__uinnj = c.pyapi.object_getattr_string(val, 'asi8')
    mtkl__klltn = c.pyapi.call_method(val, 'isna', ())
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    tmro__rav = c.pyapi.import_module_noblock(vmffd__loxx)
    qrxej__dqky = c.pyapi.object_getattr_string(tmro__rav, 'arrays')
    zns__abet = c.pyapi.call_method(qrxej__dqky, 'IntegerArray', (
        mldub__uinnj, mtkl__klltn))
    data = c.pyapi.to_native_value(arr_typ, zns__abet).value
    c.pyapi.decref(mldub__uinnj)
    c.pyapi.decref(mtkl__klltn)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(tmro__rav)
    c.pyapi.decref(qrxej__dqky)
    c.pyapi.decref(zns__abet)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(types.int64, types.int64), types.DictType(types.int64,
        types.int64)(), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


class CategoricalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        udyy__uldm = get_categories_int_type(fe_type.data.dtype)
        yoag__zpnzc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(udyy__uldm, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            yoag__zpnzc)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    tmro__rav = c.pyapi.import_module_noblock(vmffd__loxx)
    joqg__lwbtq = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, joqg__lwbtq.data)
    xgxix__fbqby = c.pyapi.from_native_value(typ.data, joqg__lwbtq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, joqg__lwbtq.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, joqg__lwbtq.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([xgxix__fbqby])
    kws = c.pyapi.dict_pack([('name', kyh__qplx)])
    hqq__hqur = c.pyapi.object_getattr_string(tmro__rav, 'CategoricalIndex')
    lze__cuoae = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(xgxix__fbqby)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(tmro__rav)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lze__cuoae


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        rflel__eoe, cjuf__cfci = args
        joqg__lwbtq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        joqg__lwbtq.data = rflel__eoe
        joqg__lwbtq.name = cjuf__cfci
        context.nrt.incref(builder, signature.args[0], rflel__eoe)
        context.nrt.incref(builder, signature.args[1], cjuf__cfci)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        joqg__lwbtq.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return joqg__lwbtq._getvalue()
    ihguu__dayp = CategoricalIndexType(data, name)
    sig = signature(ihguu__dayp, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    tyiq__tyjd = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', hevr__blzat,
        idx_cpy_arg_defaults, fn_str=tyiq__tyjd, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, yoag__zpnzc)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    tmro__rav = c.pyapi.import_module_noblock(vmffd__loxx)
    vfhqs__gpldc = numba.core.cgutils.create_struct_proxy(typ)(c.context, c
        .builder, val)
    c.context.nrt.incref(c.builder, typ.data, vfhqs__gpldc.data)
    xgxix__fbqby = c.pyapi.from_native_value(typ.data, vfhqs__gpldc.data, c
        .env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, vfhqs__gpldc.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, vfhqs__gpldc.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([xgxix__fbqby])
    kws = c.pyapi.dict_pack([('name', kyh__qplx)])
    hqq__hqur = c.pyapi.object_getattr_string(tmro__rav, 'IntervalIndex')
    lze__cuoae = c.pyapi.call(hqq__hqur, args, kws)
    c.pyapi.decref(xgxix__fbqby)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(tmro__rav)
    c.pyapi.decref(hqq__hqur)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return lze__cuoae


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        rflel__eoe, cjuf__cfci = args
        vfhqs__gpldc = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        vfhqs__gpldc.data = rflel__eoe
        vfhqs__gpldc.name = cjuf__cfci
        context.nrt.incref(builder, signature.args[0], rflel__eoe)
        context.nrt.incref(builder, signature.args[1], cjuf__cfci)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        vfhqs__gpldc.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return vfhqs__gpldc._getvalue()
    ihguu__dayp = IntervalIndexType(data, name)
    sig = signature(ihguu__dayp, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return types.iterators.ArrayIterator(types.Array(self.dtype, 1, 'C'))

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


@typeof_impl.register(pd.Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(pd.UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(pd.Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', fe_type.data), ('name', fe_type.name_typ),
            ('dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    tyiq__tyjd = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hevr__blzat, idx_cpy_arg_defaults,
        fn_str=tyiq__tyjd, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    fuegs__nqyd = c.pyapi.import_module_noblock(vmffd__loxx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ssl__hvoo.data)
    zns__abet = c.pyapi.from_native_value(typ.data, ssl__hvoo.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ssl__hvoo.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, ssl__hvoo.name, c.
        env_manager)
    zyz__cruy = c.pyapi.make_none()
    bcbe__zldi = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    smg__chhze = c.pyapi.call_method(fuegs__nqyd, 'Index', (zns__abet,
        zyz__cruy, bcbe__zldi, kyh__qplx))
    c.pyapi.decref(zns__abet)
    c.pyapi.decref(zyz__cruy)
    c.pyapi.decref(bcbe__zldi)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(fuegs__nqyd)
    c.context.nrt.decref(c.builder, typ, val)
    return smg__chhze


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        dot__ctm = signature.return_type
        ssl__hvoo = cgutils.create_struct_proxy(dot__ctm)(context, builder)
        ssl__hvoo.data = args[0]
        ssl__hvoo.name = args[1]
        context.nrt.incref(builder, dot__ctm.data, args[0])
        context.nrt.incref(builder, dot__ctm.name_typ, args[1])
        dtype = dot__ctm.dtype
        ssl__hvoo.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return ssl__hvoo._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    dtype = typ.dtype
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        ohqkw__uvfep = dict(dtype=dtype)
        cttoz__slx = dict(dtype=None)
        check_unsupported_args(func_str, ohqkw__uvfep, cttoz__slx,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                wpdro__vig = bodo.utils.conversion.coerce_to_ndarray(data)
                qtlsz__eopr = bodo.utils.conversion.fix_arr_dtype(wpdro__vig,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    qtlsz__eopr, name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                wpdro__vig = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    wpdro__vig = wpdro__vig.copy()
                qtlsz__eopr = bodo.utils.conversion.fix_arr_dtype(wpdro__vig,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(
                    qtlsz__eopr, name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((pd.Int64Index,
        'pandas.Int64Index', np.int64), (pd.UInt64Index,
        'pandas.UInt64Index', np.uint64), (pd.Float64Index,
        'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type
        super(StringIndexType, self).__init__(name='StringIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.libs.str_arr_ext.StringArrayIterator()


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', string_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.libs.binary_arr_ext.BinaryArrayIterator()


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    eluxj__gvjp = typ.data
    scalar_type = typ.data.dtype
    xgfhb__wpw = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(eluxj__gvjp, xgfhb__wpw).value
    kyh__qplx = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, kyh__qplx).value
    c.pyapi.decref(xgfhb__wpw)
    c.pyapi.decref(kyh__qplx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ssl__hvoo.data = data
    ssl__hvoo.name = name
    kaczj__dpm, qkqpj__zpldd = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(scalar_type, types.int64), types.DictType(scalar_type,
        types.int64)(), [])
    ssl__hvoo.dict = qkqpj__zpldd
    return NativeValue(ssl__hvoo._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    eluxj__gvjp = typ.data
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    fuegs__nqyd = c.pyapi.import_module_noblock(vmffd__loxx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, eluxj__gvjp, ssl__hvoo.data)
    zns__abet = c.pyapi.from_native_value(eluxj__gvjp, ssl__hvoo.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ssl__hvoo.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, ssl__hvoo.name, c.
        env_manager)
    zyz__cruy = c.pyapi.make_none()
    bcbe__zldi = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    smg__chhze = c.pyapi.call_method(fuegs__nqyd, 'Index', (zns__abet,
        zyz__cruy, bcbe__zldi, kyh__qplx))
    c.pyapi.decref(zns__abet)
    c.pyapi.decref(zyz__cruy)
    c.pyapi.decref(bcbe__zldi)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(fuegs__nqyd)
    c.context.nrt.decref(c.builder, typ, val)
    return smg__chhze


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name)(
        data, name)
    kvmc__lfbgf = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, kvmc__lfbgf


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        qhazz__cbuje = 'binary_array_type'
        godh__yhhtf = 'bytes_type'
    else:
        qhazz__cbuje = 'string_array_type'
        godh__yhhtf = 'string_type'
    jbr__hoecj = 'def impl(context, builder, signature, args):\n'
    jbr__hoecj += '    assert len(args) == 2\n'
    jbr__hoecj += '    index_typ = signature.return_type\n'
    jbr__hoecj += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    jbr__hoecj += '    index_val.data = args[0]\n'
    jbr__hoecj += '    index_val.name = args[1]\n'
    jbr__hoecj += '    # increase refcount of stored values\n'
    jbr__hoecj += f'    context.nrt.incref(builder, {qhazz__cbuje}, args[0])\n'
    jbr__hoecj += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    jbr__hoecj += '    # create empty dict for get_loc hashmap\n'
    jbr__hoecj += '    index_val.dict = context.compile_internal(\n'
    jbr__hoecj += '       builder,\n'
    jbr__hoecj += (
        f'       lambda: numba.typed.Dict.empty({godh__yhhtf}, types.int64),\n'
        )
    jbr__hoecj += (
        f'        types.DictType({godh__yhhtf}, types.int64)(), [],)\n')
    jbr__hoecj += '    return index_val._getvalue()\n'
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type, 'string_array_type': string_array_type,
        'binary_array_type': binary_array_type}, xmbha__zqfs)
    impl = xmbha__zqfs['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    tyiq__tyjd = idx_typ_to_format_str_map[typ].format('copy()')
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hevr__blzat, idx_cpy_arg_defaults,
        fn_str=tyiq__tyjd, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if arr_typ == bodo.string_array_type:
        return StringIndexType(name_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    wzxde__qtgni = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value
        )
    osjh__ceb = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', wzxde__qtgni, osjh__ceb,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


@numba.njit(no_cpython_wrapper=True)
def _init_engine(I):
    if len(I) > 0 and not I._dict:
        hjr__krwn = bodo.utils.conversion.coerce_to_array(I)
        for i in range(len(hjr__krwn)):
            val = hjr__krwn[i]
            if val in I._dict:
                raise ValueError(
                    'Index.get_loc(): non-unique Index not supported yet')
            I._dict[val] = i


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I)
            return key in I._dict
        else:
            ipb__tdz = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(ipb__tdz)
            hjr__krwn = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(hjr__krwn)):
                if hjr__krwn[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    wzxde__qtgni = dict(method=method, tolerance=tolerance)
    vkmp__vxuy = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', wzxde__qtgni, vkmp__vxuy,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            ipb__tdz = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(ipb__tdz)
            hjr__krwn = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(hjr__krwn)):
                if hjr__krwn[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        djgm__rsyb = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                aytqn__dymf = len(I)
                fwbm__fss = np.empty(aytqn__dymf, np.bool_)
                for i in numba.parfors.parfor.internal_prange(aytqn__dymf):
                    fwbm__fss[i] = not djgm__rsyb
                return fwbm__fss
            return impl
        jbr__hoecj = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if djgm__rsyb else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        xmbha__zqfs = {}
        exec(jbr__hoecj, {'bodo': bodo, 'np': np, 'numba': numba}, xmbha__zqfs)
        impl = xmbha__zqfs['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for rboc__cosuw in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(rboc__cosuw, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            hjr__krwn = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(hjr__krwn, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            hjr__krwn = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(hjr__krwn, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        hjr__krwn = bodo.hiframes.pd_index_ext.get_index_data(I)
        fwbm__fss = bodo.libs.array_kernels.duplicated((hjr__krwn,))
        return fwbm__fss
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    wzxde__qtgni = dict(keep=keep)
    vkmp__vxuy = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', wzxde__qtgni,
        vkmp__vxuy, package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    jbr__hoecj = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        jbr__hoecj += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        jbr__hoecj += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'bodo': bodo}, xmbha__zqfs)
    impl = xmbha__zqfs['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    effxg__lzy = args[0]
    if isinstance(self.typemap[effxg__lzy.name], HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(effxg__lzy):
        return ArrayAnalysis.AnalyzeResult(shape=effxg__lzy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    dtype = I.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    yqxh__ntfi = numba.core.registry.cpu_target.typing_context
    nug__narl = numba.core.registry.cpu_target.target_context
    try:
        abld__jgjv = get_const_func_output_type(mapper, (dtype,), {},
            yqxh__ntfi, nug__narl)
    except Exception as omv__qycun:
        raise_bodo_error(get_udf_error_msg('Index.map()', omv__qycun))
    uwgre__stf = get_udf_out_arr_type(abld__jgjv)
    func = get_overload_const_func(mapper, None)
    jbr__hoecj = 'def f(I, mapper, na_action=None):\n'
    jbr__hoecj += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    jbr__hoecj += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    jbr__hoecj += '  numba.parfors.parfor.init_prange()\n'
    jbr__hoecj += '  n = len(A)\n'
    jbr__hoecj += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    jbr__hoecj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    jbr__hoecj += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    jbr__hoecj += '    v = map_func(t2)\n'
    jbr__hoecj += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    jbr__hoecj += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    sttfu__vcbi = bodo.compiler.udf_jit(func)
    xmbha__zqfs = {}
    exec(jbr__hoecj, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': sttfu__vcbi, '_arr_typ': uwgre__stf,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': uwgre__stf.dtype}, xmbha__zqfs)
    f = xmbha__zqfs['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    rqicu__fjrpk, vbky__iex = sig.args
    if rqicu__fjrpk != vbky__iex:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    rqicu__fjrpk, vbky__iex = sig.args
    if rqicu__fjrpk != vbky__iex:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):

            def impl(lhs, rhs):
                hjr__krwn = bodo.utils.conversion.coerce_to_array(lhs)
                mcjf__shpb = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                fwbm__fss = op(hjr__krwn, mcjf__shpb)
                return fwbm__fss
            return impl
        if is_index_type(rhs):

            def impl2(lhs, rhs):
                hjr__krwn = bodo.utils.conversion.coerce_to_array(rhs)
                mcjf__shpb = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                fwbm__fss = op(mcjf__shpb, hjr__krwn)
                return fwbm__fss
            return impl2
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    hjr__krwn = bodo.utils.conversion.coerce_to_array(data)
                    mcjf__shpb = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    fwbm__fss = op(hjr__krwn, mcjf__shpb)
                    return fwbm__fss
                return impl3
            count = len(lhs.data.types)
            jbr__hoecj = 'def f(lhs, rhs):\n'
            jbr__hoecj += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            xmbha__zqfs = {}
            exec(jbr__hoecj, {'op': op, 'np': np}, xmbha__zqfs)
            impl = xmbha__zqfs['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    hjr__krwn = bodo.utils.conversion.coerce_to_array(data)
                    mcjf__shpb = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    fwbm__fss = op(mcjf__shpb, hjr__krwn)
                    return fwbm__fss
                return impl4
            count = len(rhs.data.types)
            jbr__hoecj = 'def f(lhs, rhs):\n'
            jbr__hoecj += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            xmbha__zqfs = {}
            exec(jbr__hoecj, {'op': op, 'np': np}, xmbha__zqfs)
            impl = xmbha__zqfs['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yoag__zpnzc = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, yoag__zpnzc
            )


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    tyiq__tyjd = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    hevr__blzat = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', hevr__blzat, idx_cpy_arg_defaults,
        fn_str=tyiq__tyjd, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    vmffd__loxx = c.context.insert_const_string(c.builder.module, 'pandas')
    fuegs__nqyd = c.pyapi.import_module_noblock(vmffd__loxx)
    ssl__hvoo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, ssl__hvoo.data)
    zns__abet = c.pyapi.from_native_value(typ.data, ssl__hvoo.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ssl__hvoo.name)
    kyh__qplx = c.pyapi.from_native_value(typ.name_typ, ssl__hvoo.name, c.
        env_manager)
    zyz__cruy = c.pyapi.make_none()
    bcbe__zldi = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    smg__chhze = c.pyapi.call_method(fuegs__nqyd, 'Index', (zns__abet,
        zyz__cruy, bcbe__zldi, kyh__qplx))
    c.pyapi.decref(zns__abet)
    c.pyapi.decref(zyz__cruy)
    c.pyapi.decref(bcbe__zldi)
    c.pyapi.decref(kyh__qplx)
    c.pyapi.decref(fuegs__nqyd)
    c.context.nrt.decref(c.builder, typ, val)
    return smg__chhze


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        dot__ctm = signature.return_type
        ssl__hvoo = cgutils.create_struct_proxy(dot__ctm)(context, builder)
        ssl__hvoo.data = args[0]
        ssl__hvoo.name = args[1]
        context.nrt.incref(builder, dot__ctm.data, args[0])
        context.nrt.incref(builder, dot__ctm.name_typ, args[1])
        return ssl__hvoo._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index(I, name)


def init_index(I, name):
    yisbp__twld = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in yisbp__twld:
        init_func = yisbp__twld[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, types.Array(types.int64, 1,
        'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    bcidm__ixhf = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, bcidm__ixhf])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    bcidm__ixhf = context.get_constant_null(types.DictType(types.int64,
        types.int64))
    return lir.Constant.literal_struct([data, name, bcidm__ixhf])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    bcidm__ixhf = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, bcidm__ixhf])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    eluxj__gvjp = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, eluxj__gvjp, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    bcidm__ixhf = context.get_constant_null(types.DictType(scalar_type,
        types.int64))
    return lir.Constant.literal_struct([data, name, bcidm__ixhf])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [orcdu__ylqdl] = sig.args
    [ygzy__vpy] = args
    adpua__xlljw = context.make_helper(builder, orcdu__ylqdl, value=ygzy__vpy)
    vml__kjmnf = context.make_helper(builder, sig.return_type)
    jssgv__gblx = cgutils.alloca_once_value(builder, adpua__xlljw.start)
    kklx__zfdjf = context.get_constant(types.intp, 0)
    wwh__mlxug = cgutils.alloca_once_value(builder, kklx__zfdjf)
    vml__kjmnf.iter = jssgv__gblx
    vml__kjmnf.stop = adpua__xlljw.stop
    vml__kjmnf.step = adpua__xlljw.step
    vml__kjmnf.count = wwh__mlxug
    nez__fawm = builder.sub(adpua__xlljw.stop, adpua__xlljw.start)
    wmm__azq = context.get_constant(types.intp, 1)
    lec__pde = builder.icmp(lc.ICMP_SGT, nez__fawm, kklx__zfdjf)
    fyvq__uzk = builder.icmp(lc.ICMP_SGT, adpua__xlljw.step, kklx__zfdjf)
    nwst__nfk = builder.not_(builder.xor(lec__pde, fyvq__uzk))
    with builder.if_then(nwst__nfk):
        bkyc__vcwj = builder.srem(nez__fawm, adpua__xlljw.step)
        bkyc__vcwj = builder.select(lec__pde, bkyc__vcwj, builder.neg(
            bkyc__vcwj))
        micl__nuu = builder.icmp(lc.ICMP_SGT, bkyc__vcwj, kklx__zfdjf)
        kwx__wux = builder.add(builder.sdiv(nez__fawm, adpua__xlljw.step),
            builder.select(micl__nuu, wmm__azq, kklx__zfdjf))
        builder.store(kwx__wux, wwh__mlxug)
    lze__cuoae = vml__kjmnf._getvalue()
    dzp__ehik = impl_ret_new_ref(context, builder, sig.return_type, lze__cuoae)
    return dzp__ehik


def getiter_index(context, builder, sig, args):
    [orcdu__ylqdl] = sig.args
    [ygzy__vpy] = args
    adpua__xlljw = context.make_helper(builder, orcdu__ylqdl, value=ygzy__vpy)
    return numba.np.arrayobj.getiter_array(context, builder, signature(sig.
        return_type, sig.args[0].data), (adpua__xlljw.data,))


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(getiter_index)


_install_index_getiter()
index_unsupported_methods = ['all', 'any', 'append', 'argmax', 'argmin',
    'argsort', 'asof', 'asof_locs', 'astype', 'delete', 'difference',
    'drop', 'droplevel', 'dropna', 'equals', 'factorize', 'fillna',
    'format', 'get_indexer', 'get_indexer_for', 'get_indexer_non_unique',
    'get_level_values', 'get_slice_bound', 'get_value', 'groupby',
    'holds_integer', 'identical', 'insert', 'intersection', 'is_',
    'is_boolean', 'is_categorical', 'is_floating', 'is_integer',
    'is_interval', 'is_mixed', 'is_numeric', 'is_object',
    'is_type_compatible', 'isin', 'item', 'join', 'memory_usage', 'nunique',
    'putmask', 'ravel', 'reindex', 'repeat', 'searchsorted', 'set_names',
    'set_value', 'shift', 'slice_indexer', 'slice_locs', 'sort',
    'sort_values', 'sortlevel', 'str', 'symmetric_difference',
    'to_flat_index', 'to_frame', 'to_list', 'to_native_types', 'to_numpy',
    'to_series', 'tolist', 'transpose', 'union', 'unique', 'value_counts',
    'view', 'where']
index_unsupported_atrs = ['T', 'array', 'asi8', 'dtype', 'has_duplicates',
    'hasnans', 'inferred_type', 'is_all_dates', 'is_unique', 'ndim',
    'nlevels', 'size', 'names', 'empty']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc']
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'shape', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'shape', 'nbytes', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_convert', 'tz_localize', 'round', 'floor', 'ceil', 'to_period',
    'to_perioddelta', 'to_pydatetime', 'month_name', 'day_name', 'mean',
    'indexer_at_time', 'indexer_between', 'indexer_between_time']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for ateo__rbv in index_unsupported_methods:
        for nuhl__jeo, typ in index_types:
            overload_method(typ, ateo__rbv, no_unliteral=True)(
                create_unsupported_overload(nuhl__jeo.format(ateo__rbv + '()'))
                )
    for txsm__bnudm in index_unsupported_atrs:
        for nuhl__jeo, typ in index_types:
            overload_attribute(typ, txsm__bnudm, no_unliteral=True)(
                create_unsupported_overload(nuhl__jeo.format(txsm__bnudm)))
    ufdb__rqq = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    vsuum__scdv = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods)]
    for typ, crzt__hmctd in vsuum__scdv:
        nuhl__jeo = idx_typ_to_format_str_map[typ]
        for gqs__jsj in crzt__hmctd:
            overload_method(typ, gqs__jsj, no_unliteral=True)(
                create_unsupported_overload(nuhl__jeo.format(gqs__jsj + '()')))
    for typ, noso__hdqcr in ufdb__rqq:
        nuhl__jeo = idx_typ_to_format_str_map[typ]
        for txsm__bnudm in noso__hdqcr:
            overload_attribute(typ, txsm__bnudm, no_unliteral=True)(
                create_unsupported_overload(nuhl__jeo.format(txsm__bnudm)))
    for tyg__hicar in [RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, MultiIndexType]:
        for gqs__jsj in ['max', 'min']:
            nuhl__jeo = idx_typ_to_format_str_map[tyg__hicar]
            overload_method(tyg__hicar, gqs__jsj, no_unliteral=True)(
                create_unsupported_overload(nuhl__jeo.format(gqs__jsj + '()')))


_install_index_unsupported()
