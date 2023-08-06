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
        hnn__sgdje = [('data', _dt_index_data_typ), ('name', fe_type.
            name_typ), ('dict', types.DictType(_dt_index_data_typ.dtype,
            types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    zpxqr__whjov = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()'
        )
    check_unsupported_args('copy', lfx__toe, idx_cpy_arg_defaults, fn_str=
        zpxqr__whjov, package_name='pandas', module_name='Index')
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
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    urth__kyh = c.pyapi.import_module_noblock(tzch__qgs)
    pof__bfq = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, _dt_index_data_typ, pof__bfq.data)
    tgi__hon = c.pyapi.from_native_value(_dt_index_data_typ, pof__bfq.data,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, pof__bfq.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, pof__bfq.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([tgi__hon])
    kws = c.pyapi.dict_pack([('name', qqom__ijru)])
    fvjf__ybxz = c.pyapi.object_getattr_string(urth__kyh, 'DatetimeIndex')
    suct__svq = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(tgi__hon)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(urth__kyh)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return suct__svq


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_dt_index_data_typ, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    dtype = _dt_index_data_typ.dtype
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        ztso__thazw, yne__ddo = args
        pof__bfq = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        pof__bfq.data = ztso__thazw
        pof__bfq.name = yne__ddo
        context.nrt.incref(builder, signature.args[0], ztso__thazw)
        context.nrt.incref(builder, signature.args[1], yne__ddo)
        dtype = _dt_index_data_typ.dtype
        pof__bfq.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return pof__bfq._getvalue()
    xriv__bppk = DatetimeIndexType(name)
    sig = signature(xriv__bppk, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    jioz__tfy = args[0]
    if equiv_set.has_shape(jioz__tfy):
        return ArrayAnalysis.AnalyzeResult(shape=jioz__tfy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    edmns__ylsl = 'def impl(dti):\n'
    edmns__ylsl += '    numba.parfors.parfor.init_prange()\n'
    edmns__ylsl += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    edmns__ylsl += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n')
    edmns__ylsl += '    n = len(A)\n'
    edmns__ylsl += '    S = np.empty(n, np.int64)\n'
    edmns__ylsl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    edmns__ylsl += (
        '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])\n'
        )
    edmns__ylsl += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
    if field in ['weekday']:
        edmns__ylsl += '        S[i] = ts.' + field + '()\n'
    else:
        edmns__ylsl += '        S[i] = ts.' + field + '\n'
    edmns__ylsl += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'numba': numba, 'np': np, 'bodo': bodo}, fmdbe__xdgp)
    impl = fmdbe__xdgp['impl']
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
        avts__qhhc = len(A)
        S = np.empty(avts__qhhc, np.bool_)
        for i in numba.parfors.parfor.internal_prange(avts__qhhc):
            hvdb__uip = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            oamt__rpbq = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(hvdb__uip))
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(oamt__rpbq.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        avts__qhhc = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            avts__qhhc)
        for i in numba.parfors.parfor.internal_prange(avts__qhhc):
            hvdb__uip = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(A[i])
            oamt__rpbq = (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(hvdb__uip))
            S[i] = datetime.date(oamt__rpbq.year, oamt__rpbq.month,
                oamt__rpbq.day)
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
    lxdac__mfif = dict(axis=axis, skipna=skipna)
    lnu__vnqu = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        hnz__wwxi = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(hnz__wwxi)):
            if not bodo.libs.array_kernels.isna(hnz__wwxi, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(hnz__wwxi
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    lxdac__mfif = dict(axis=axis, skipna=skipna)
    lnu__vnqu = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        hnz__wwxi = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(hnz__wwxi)):
            if not bodo.libs.array_kernels.isna(hnz__wwxi, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(hnz__wwxi
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
    lxdac__mfif = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    lnu__vnqu = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        zmii__tyn = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(zmii__tyn)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        keevb__lvkem = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            hnz__wwxi = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            avts__qhhc = len(hnz__wwxi)
            S = np.empty(avts__qhhc, keevb__lvkem)
            luif__cjzqi = rhs.value
            for i in numba.parfors.parfor.internal_prange(avts__qhhc):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hnz__wwxi[i]) - luif__cjzqi)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        keevb__lvkem = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            hnz__wwxi = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            avts__qhhc = len(hnz__wwxi)
            S = np.empty(avts__qhhc, keevb__lvkem)
            luif__cjzqi = lhs.value
            for i in numba.parfors.parfor.internal_prange(avts__qhhc):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    luif__cjzqi - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(hnz__wwxi[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    sxnbu__pfm = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    edmns__ylsl = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        edmns__ylsl += '  dt_index, _str = lhs, rhs\n'
        bas__oiic = 'arr[i] {} other'.format(sxnbu__pfm)
    else:
        edmns__ylsl += '  dt_index, _str = rhs, lhs\n'
        bas__oiic = 'other {} arr[i]'.format(sxnbu__pfm)
    edmns__ylsl += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    edmns__ylsl += '  l = len(arr)\n'
    edmns__ylsl += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    edmns__ylsl += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    edmns__ylsl += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    edmns__ylsl += '    S[i] = {}\n'.format(bas__oiic)
    edmns__ylsl += '  return S\n'
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'bodo': bodo, 'numba': numba, 'np': np}, fmdbe__xdgp)
    impl = fmdbe__xdgp['impl']
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
    qwpb__rpy = getattr(data, 'dtype', None)
    if not is_overload_none(dtype):
        ohqol__sal = parse_dtype(dtype, 'pandas.Index')
    else:
        ohqol__sal = qwpb__rpy
    if isinstance(ohqol__sal, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or ohqol__sal == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or ohqol__sal == types.NPTimedelta('ns'):

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
        if isinstance(ohqol__sal, (types.Integer, types.Float, types.Boolean)):

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                zmii__tyn = bodo.utils.conversion.coerce_to_array(data)
                vzqi__dkod = bodo.utils.conversion.fix_arr_dtype(zmii__tyn,
                    ohqol__sal)
                return bodo.hiframes.pd_index_ext.init_numeric_index(vzqi__dkod
                    , name)
        elif ohqol__sal in [types.string, bytes_type]:

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
                exx__srj = bodo.hiframes.pd_index_ext.get_index_data(dti)
                hvdb__uip = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    exx__srj[ind])
                return (bodo.hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(hvdb__uip))
            return impl
        else:

            def impl(dti, ind):
                exx__srj = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                yuckn__uxil = exx__srj[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(
                    yuckn__uxil, name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            robr__rpite = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(robr__rpite[ind])
        return impl

    def impl(I, ind):
        robr__rpite = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        yuckn__uxil = robr__rpite[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(yuckn__uxil,
            name)
    return impl


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    vnyg__jbx = False
    ujq__alt = False
    if closed is None:
        vnyg__jbx = True
        ujq__alt = True
    elif closed == 'left':
        vnyg__jbx = True
    elif closed == 'right':
        ujq__alt = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return vnyg__jbx, ujq__alt


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
    lxdac__mfif = dict(tz=tz, normalize=normalize)
    lnu__vnqu = dict(tz=None, normalize=False)
    check_unsupported_args('pandas.date_range', lxdac__mfif, lnu__vnqu,
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
        zsdf__dpkao = pd.Timestamp('2018-01-01')
        if start is not None:
            zsdf__dpkao = pd.Timestamp(start)
        oou__xvuke = pd.Timestamp('2018-01-01')
        if end is not None:
            oou__xvuke = pd.Timestamp(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of startand end are defined'
                )
        vnyg__jbx, ujq__alt = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            spcwl__dddj = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = zsdf__dpkao.value
                qic__iovdp = b + (oou__xvuke.value - b
                    ) // spcwl__dddj * spcwl__dddj + spcwl__dddj // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = zsdf__dpkao.value
                pkimq__dvcyr = np.int64(periods) * np.int64(spcwl__dddj)
                qic__iovdp = np.int64(b) + pkimq__dvcyr
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                qic__iovdp = oou__xvuke.value + spcwl__dddj
                pkimq__dvcyr = np.int64(periods) * np.int64(-spcwl__dddj)
                b = np.int64(qic__iovdp) + pkimq__dvcyr
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            vywp__ytdd = np.arange(b, qic__iovdp, spcwl__dddj, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            asm__wybsv = oou__xvuke.value - zsdf__dpkao.value
            step = asm__wybsv / (periods - 1)
            rcjw__mdg = np.arange(0, periods, 1, np.float64)
            rcjw__mdg *= step
            rcjw__mdg += zsdf__dpkao.value
            vywp__ytdd = rcjw__mdg.astype(np.int64)
            vywp__ytdd[-1] = oou__xvuke.value
        if not vnyg__jbx and len(vywp__ytdd) and vywp__ytdd[0
            ] == zsdf__dpkao.value:
            vywp__ytdd = vywp__ytdd[1:]
        if not ujq__alt and len(vywp__ytdd) and vywp__ytdd[-1
            ] == oou__xvuke.value:
            vywp__ytdd = vywp__ytdd[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(vywp__ytdd)
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
        zsdf__dpkao = pd.Timedelta('1 day')
        if start is not None:
            zsdf__dpkao = pd.Timedelta(start)
        oou__xvuke = pd.Timedelta('1 day')
        if end is not None:
            oou__xvuke = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        vnyg__jbx, ujq__alt = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            spcwl__dddj = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = zsdf__dpkao.value
                qic__iovdp = b + (oou__xvuke.value - b
                    ) // spcwl__dddj * spcwl__dddj + spcwl__dddj // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = zsdf__dpkao.value
                pkimq__dvcyr = np.int64(periods) * np.int64(spcwl__dddj)
                qic__iovdp = np.int64(b) + pkimq__dvcyr
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                qic__iovdp = oou__xvuke.value + spcwl__dddj
                pkimq__dvcyr = np.int64(periods) * np.int64(-spcwl__dddj)
                b = np.int64(qic__iovdp) + pkimq__dvcyr
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            vywp__ytdd = np.arange(b, qic__iovdp, spcwl__dddj, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            asm__wybsv = oou__xvuke.value - zsdf__dpkao.value
            step = asm__wybsv / (periods - 1)
            rcjw__mdg = np.arange(0, periods, 1, np.float64)
            rcjw__mdg *= step
            rcjw__mdg += zsdf__dpkao.value
            vywp__ytdd = rcjw__mdg.astype(np.int64)
            vywp__ytdd[-1] = oou__xvuke.value
        if not vnyg__jbx and len(vywp__ytdd) and vywp__ytdd[0
            ] == zsdf__dpkao.value:
            vywp__ytdd = vywp__ytdd[1:]
        if not ujq__alt and len(vywp__ytdd) and vywp__ytdd[-1
            ] == oou__xvuke.value:
            vywp__ytdd = vywp__ytdd[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(vywp__ytdd)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        avts__qhhc = len(A)
        fielw__fvm = bodo.libs.int_arr_ext.alloc_int_array(avts__qhhc, np.
            uint32)
        mqp__taz = bodo.libs.int_arr_ext.alloc_int_array(avts__qhhc, np.uint32)
        eoon__urqeo = bodo.libs.int_arr_ext.alloc_int_array(avts__qhhc, np.
            uint32)
        for i in numba.parfors.parfor.internal_prange(avts__qhhc):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(fielw__fvm, i)
                bodo.libs.array_kernels.setna(mqp__taz, i)
                bodo.libs.array_kernels.setna(eoon__urqeo, i)
                continue
            fielw__fvm[i], mqp__taz[i], eoon__urqeo[i
                ] = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(
                A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((fielw__fvm,
            mqp__taz, eoon__urqeo), idx, ('year', 'week', 'day'))
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
        hnn__sgdje = [('data', _timedelta_index_data_typ), ('name', fe_type
            .name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, hnn__sgdje)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    urth__kyh = c.pyapi.import_module_noblock(tzch__qgs)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    tgi__hon = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([tgi__hon])
    kws = c.pyapi.dict_pack([('name', qqom__ijru)])
    fvjf__ybxz = c.pyapi.object_getattr_string(urth__kyh, 'TimedeltaIndex')
    suct__svq = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(tgi__hon)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(urth__kyh)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return suct__svq


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    dtype = _timedelta_index_data_typ.dtype
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        ztso__thazw, yne__ddo = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = ztso__thazw
        timedelta_index.name = yne__ddo
        context.nrt.incref(builder, signature.args[0], ztso__thazw)
        context.nrt.incref(builder, signature.args[1], yne__ddo)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    xriv__bppk = TimedeltaIndexType(name)
    sig = signature(xriv__bppk, data, name)
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
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    zpxqr__whjov = idx_typ_to_format_str_map[TimedeltaIndexType].format(
        'copy()')
    check_unsupported_args('TimedeltaIndex.copy', lfx__toe,
        idx_cpy_arg_defaults, fn_str=zpxqr__whjov, package_name='pandas',
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
    lxdac__mfif = dict(axis=axis, skipna=skipna)
    lnu__vnqu = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        avts__qhhc = len(data)
        fccy__xdln = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(avts__qhhc):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            fccy__xdln = min(fccy__xdln, val)
        dhmvz__ngv = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            fccy__xdln)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(dhmvz__ngv, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    lxdac__mfif = dict(axis=axis, skipna=skipna)
    lnu__vnqu = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        avts__qhhc = len(data)
        mspz__tgxr = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(avts__qhhc):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            mspz__tgxr = max(mspz__tgxr, val)
        dhmvz__ngv = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            mspz__tgxr)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(dhmvz__ngv, count)
    return impl


def gen_tdi_field_impl(field):
    edmns__ylsl = 'def impl(tdi):\n'
    edmns__ylsl += '    numba.parfors.parfor.init_prange()\n'
    edmns__ylsl += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    edmns__ylsl += (
        '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n')
    edmns__ylsl += '    n = len(A)\n'
    edmns__ylsl += '    S = np.empty(n, np.int64)\n'
    edmns__ylsl += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    edmns__ylsl += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        edmns__ylsl += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        edmns__ylsl += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        edmns__ylsl += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        edmns__ylsl += (
            '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
    else:
        assert False, 'invalid timedelta field'
    edmns__ylsl += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'numba': numba, 'np': np, 'bodo': bodo}, fmdbe__xdgp)
    impl = fmdbe__xdgp['impl']
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
    lxdac__mfif = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    lnu__vnqu = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        zmii__tyn = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(zmii__tyn)
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
        hnn__sgdje = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    zpxqr__whjov = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', lfx__toe,
        idx_cpy_arg_defaults, fn_str=zpxqr__whjov, package_name='pandas',
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
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    lsln__uxv = c.pyapi.import_module_noblock(tzch__qgs)
    jha__rngl = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    khvsf__wttvd = c.pyapi.from_native_value(types.int64, jha__rngl.start,
        c.env_manager)
    lwlpe__qmhnp = c.pyapi.from_native_value(types.int64, jha__rngl.stop, c
        .env_manager)
    njei__whon = c.pyapi.from_native_value(types.int64, jha__rngl.step, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, jha__rngl.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, jha__rngl.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([khvsf__wttvd, lwlpe__qmhnp, njei__whon])
    kws = c.pyapi.dict_pack([('name', qqom__ijru)])
    fvjf__ybxz = c.pyapi.object_getattr_string(lsln__uxv, 'RangeIndex')
    sbqp__aaxbh = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(khvsf__wttvd)
    c.pyapi.decref(lwlpe__qmhnp)
    c.pyapi.decref(njei__whon)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(lsln__uxv)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbqp__aaxbh


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        jha__rngl = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jha__rngl.start = args[0]
        jha__rngl.stop = args[1]
        jha__rngl.step = args[2]
        jha__rngl.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return jha__rngl._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, aff__wtn = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    khvsf__wttvd = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, khvsf__wttvd).value
    lwlpe__qmhnp = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, lwlpe__qmhnp).value
    njei__whon = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, njei__whon).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(khvsf__wttvd)
    c.pyapi.decref(lwlpe__qmhnp)
    c.pyapi.decref(njei__whon)
    c.pyapi.decref(qqom__ijru)
    jha__rngl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jha__rngl.start = start
    jha__rngl.stop = stop
    jha__rngl.step = step
    jha__rngl.name = name
    return NativeValue(jha__rngl._getvalue())


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
        mun__fytuk = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(mun__fytuk.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        mun__fytuk = 'RangeIndex(...) must be called with integers'
        raise BodoError(mun__fytuk)
    muph__ojddh = 'start'
    dbm__htp = 'stop'
    eii__jdzpt = 'step'
    if is_overload_none(start):
        muph__ojddh = '0'
    if is_overload_none(stop):
        dbm__htp = 'start'
        muph__ojddh = '0'
    if is_overload_none(step):
        eii__jdzpt = '1'
    edmns__ylsl = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    edmns__ylsl += '  return init_range_index({}, {}, {}, name)\n'.format(
        muph__ojddh, dbm__htp, eii__jdzpt)
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'init_range_index': init_range_index}, fmdbe__xdgp)
    nse__wvuyn = fmdbe__xdgp['_pd_range_index_imp']
    return nse__wvuyn


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
                aunss__gqug = numba.cpython.unicode._normalize_slice(idx,
                    len(I))
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * aunss__gqug.start
                stop = I._start + I._step * aunss__gqug.stop
                step = I._step * aunss__gqug.step
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
        hnn__sgdje = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    zpxqr__whjov = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', lfx__toe,
        idx_cpy_arg_defaults, fn_str=zpxqr__whjov, package_name='pandas',
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
        ztso__thazw, yne__ddo, aff__wtn = args
        tsl__orry = signature.return_type
        mzntz__jib = cgutils.create_struct_proxy(tsl__orry)(context, builder)
        mzntz__jib.data = ztso__thazw
        mzntz__jib.name = yne__ddo
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        mzntz__jib.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(types.int64, types.int64), types.DictType(
            types.int64, types.int64)(), [])
        return mzntz__jib._getvalue()
    nah__shewf = get_overload_const_str(freq)
    xriv__bppk = PeriodIndexType(nah__shewf, name)
    sig = signature(xriv__bppk, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    lsln__uxv = c.pyapi.import_module_noblock(tzch__qgs)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        kmn__bwq.data)
    ytmp__ibkog = c.pyapi.from_native_value(bodo.IntegerArrayType(types.
        int64), kmn__bwq.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, kmn__bwq.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, kmn__bwq.name, c.
        env_manager)
    hvz__wsnq = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', ytmp__ibkog), ('name', qqom__ijru),
        ('freq', hvz__wsnq)])
    fvjf__ybxz = c.pyapi.object_getattr_string(lsln__uxv, 'PeriodIndex')
    sbqp__aaxbh = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(ytmp__ibkog)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(hvz__wsnq)
    c.pyapi.decref(lsln__uxv)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return sbqp__aaxbh


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    ulftr__lcx = c.pyapi.object_getattr_string(val, 'asi8')
    jnath__tvs = c.pyapi.call_method(val, 'isna', ())
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    urth__kyh = c.pyapi.import_module_noblock(tzch__qgs)
    hdkeg__pug = c.pyapi.object_getattr_string(urth__kyh, 'arrays')
    ytmp__ibkog = c.pyapi.call_method(hdkeg__pug, 'IntegerArray', (
        ulftr__lcx, jnath__tvs))
    data = c.pyapi.to_native_value(arr_typ, ytmp__ibkog).value
    c.pyapi.decref(ulftr__lcx)
    c.pyapi.decref(jnath__tvs)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(urth__kyh)
    c.pyapi.decref(hdkeg__pug)
    c.pyapi.decref(ytmp__ibkog)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(types.int64, types.int64), types.DictType(types.int64,
        types.int64)(), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


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
        fde__inisr = get_categories_int_type(fe_type.data.dtype)
        hnn__sgdje = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fde__inisr, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            hnn__sgdje)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    urth__kyh = c.pyapi.import_module_noblock(tzch__qgs)
    lap__llg = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, lap__llg.data)
    tgi__hon = c.pyapi.from_native_value(typ.data, lap__llg.data, c.env_manager
        )
    c.context.nrt.incref(c.builder, typ.name_typ, lap__llg.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, lap__llg.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([tgi__hon])
    kws = c.pyapi.dict_pack([('name', qqom__ijru)])
    fvjf__ybxz = c.pyapi.object_getattr_string(urth__kyh, 'CategoricalIndex')
    suct__svq = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(tgi__hon)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(urth__kyh)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return suct__svq


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        ztso__thazw, yne__ddo = args
        lap__llg = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        lap__llg.data = ztso__thazw
        lap__llg.name = yne__ddo
        context.nrt.incref(builder, signature.args[0], ztso__thazw)
        context.nrt.incref(builder, signature.args[1], yne__ddo)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        lap__llg.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return lap__llg._getvalue()
    xriv__bppk = CategoricalIndexType(data, name)
    sig = signature(xriv__bppk, data, name)
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
    zpxqr__whjov = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', lfx__toe,
        idx_cpy_arg_defaults, fn_str=zpxqr__whjov, package_name='pandas',
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
        hnn__sgdje = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, hnn__sgdje)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    urth__kyh = c.pyapi.import_module_noblock(tzch__qgs)
    stu__upuvz = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, stu__upuvz.data)
    tgi__hon = c.pyapi.from_native_value(typ.data, stu__upuvz.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, stu__upuvz.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, stu__upuvz.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([tgi__hon])
    kws = c.pyapi.dict_pack([('name', qqom__ijru)])
    fvjf__ybxz = c.pyapi.object_getattr_string(urth__kyh, 'IntervalIndex')
    suct__svq = c.pyapi.call(fvjf__ybxz, args, kws)
    c.pyapi.decref(tgi__hon)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(urth__kyh)
    c.pyapi.decref(fvjf__ybxz)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return suct__svq


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        ztso__thazw, yne__ddo = args
        stu__upuvz = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        stu__upuvz.data = ztso__thazw
        stu__upuvz.name = yne__ddo
        context.nrt.incref(builder, signature.args[0], ztso__thazw)
        context.nrt.incref(builder, signature.args[1], yne__ddo)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        stu__upuvz.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return stu__upuvz._getvalue()
    xriv__bppk = IntervalIndexType(data, name)
    sig = signature(xriv__bppk, data, name)
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
        hnn__sgdje = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    zpxqr__whjov = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', lfx__toe, idx_cpy_arg_defaults,
        fn_str=zpxqr__whjov, package_name='pandas', module_name='Index')
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
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    lsln__uxv = c.pyapi.import_module_noblock(tzch__qgs)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, kmn__bwq.data)
    ytmp__ibkog = c.pyapi.from_native_value(typ.data, kmn__bwq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, kmn__bwq.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, kmn__bwq.name, c.
        env_manager)
    yfzsz__zbciw = c.pyapi.make_none()
    vguuf__oreea = c.pyapi.bool_from_bool(c.context.get_constant(types.
        bool_, False))
    sbqp__aaxbh = c.pyapi.call_method(lsln__uxv, 'Index', (ytmp__ibkog,
        yfzsz__zbciw, vguuf__oreea, qqom__ijru))
    c.pyapi.decref(ytmp__ibkog)
    c.pyapi.decref(yfzsz__zbciw)
    c.pyapi.decref(vguuf__oreea)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(lsln__uxv)
    c.context.nrt.decref(c.builder, typ, val)
    return sbqp__aaxbh


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        tsl__orry = signature.return_type
        kmn__bwq = cgutils.create_struct_proxy(tsl__orry)(context, builder)
        kmn__bwq.data = args[0]
        kmn__bwq.name = args[1]
        context.nrt.incref(builder, tsl__orry.data, args[0])
        context.nrt.incref(builder, tsl__orry.name_typ, args[1])
        dtype = tsl__orry.dtype
        kmn__bwq.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return kmn__bwq._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    dtype = typ.dtype
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(dtype, types.int64), types.DictType(dtype, types.int64)(
        ), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        wnit__dvlz = dict(dtype=dtype)
        wsdz__zbx = dict(dtype=None)
        check_unsupported_args(func_str, wnit__dvlz, wsdz__zbx,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                zmii__tyn = bodo.utils.conversion.coerce_to_ndarray(data)
                uss__fpkza = bodo.utils.conversion.fix_arr_dtype(zmii__tyn,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(uss__fpkza
                    , name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                zmii__tyn = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    zmii__tyn = zmii__tyn.copy()
                uss__fpkza = bodo.utils.conversion.fix_arr_dtype(zmii__tyn,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(uss__fpkza
                    , name)
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
        hnn__sgdje = [('data', string_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


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
        hnn__sgdje = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    hzy__drnnr = typ.data
    scalar_type = typ.data.dtype
    qalaa__dse = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(hzy__drnnr, qalaa__dse).value
    qqom__ijru = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, qqom__ijru).value
    c.pyapi.decref(qalaa__dse)
    c.pyapi.decref(qqom__ijru)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kmn__bwq.data = data
    kmn__bwq.name = name
    eiin__tivgi, sxdzn__ukc = c.pyapi.call_jit_code(lambda : numba.typed.
        Dict.empty(scalar_type, types.int64), types.DictType(scalar_type,
        types.int64)(), [])
    kmn__bwq.dict = sxdzn__ukc
    return NativeValue(kmn__bwq._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    hzy__drnnr = typ.data
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    lsln__uxv = c.pyapi.import_module_noblock(tzch__qgs)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, hzy__drnnr, kmn__bwq.data)
    ytmp__ibkog = c.pyapi.from_native_value(hzy__drnnr, kmn__bwq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, kmn__bwq.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, kmn__bwq.name, c.
        env_manager)
    yfzsz__zbciw = c.pyapi.make_none()
    vguuf__oreea = c.pyapi.bool_from_bool(c.context.get_constant(types.
        bool_, False))
    sbqp__aaxbh = c.pyapi.call_method(lsln__uxv, 'Index', (ytmp__ibkog,
        yfzsz__zbciw, vguuf__oreea, qqom__ijru))
    c.pyapi.decref(ytmp__ibkog)
    c.pyapi.decref(yfzsz__zbciw)
    c.pyapi.decref(vguuf__oreea)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(lsln__uxv)
    c.context.nrt.decref(c.builder, typ, val)
    return sbqp__aaxbh


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name)(
        data, name)
    dnflo__ytg = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, dnflo__ytg


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        yivjw__utm = 'binary_array_type'
        ayxpp__hlnoy = 'bytes_type'
    else:
        yivjw__utm = 'string_array_type'
        ayxpp__hlnoy = 'string_type'
    edmns__ylsl = 'def impl(context, builder, signature, args):\n'
    edmns__ylsl += '    assert len(args) == 2\n'
    edmns__ylsl += '    index_typ = signature.return_type\n'
    edmns__ylsl += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    edmns__ylsl += '    index_val.data = args[0]\n'
    edmns__ylsl += '    index_val.name = args[1]\n'
    edmns__ylsl += '    # increase refcount of stored values\n'
    edmns__ylsl += f'    context.nrt.incref(builder, {yivjw__utm}, args[0])\n'
    edmns__ylsl += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    edmns__ylsl += '    # create empty dict for get_loc hashmap\n'
    edmns__ylsl += '    index_val.dict = context.compile_internal(\n'
    edmns__ylsl += '       builder,\n'
    edmns__ylsl += (
        f'       lambda: numba.typed.Dict.empty({ayxpp__hlnoy}, types.int64),\n'
        )
    edmns__ylsl += (
        f'        types.DictType({ayxpp__hlnoy}, types.int64)(), [],)\n')
    edmns__ylsl += '    return index_val._getvalue()\n'
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type, 'string_array_type': string_array_type,
        'binary_array_type': binary_array_type}, fmdbe__xdgp)
    impl = fmdbe__xdgp['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    zpxqr__whjov = idx_typ_to_format_str_map[typ].format('copy()')
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', lfx__toe, idx_cpy_arg_defaults,
        fn_str=zpxqr__whjov, package_name='pandas', module_name='Index')
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
    lxdac__mfif = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    xdss__brqym = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', lxdac__mfif, xdss__brqym,
        package_name='pandas', module_name='Index')
    return lambda I, indices: I[indices]


@numba.njit(no_cpython_wrapper=True)
def _init_engine(I):
    if len(I) > 0 and not I._dict:
        vywp__ytdd = bodo.utils.conversion.coerce_to_array(I)
        for i in range(len(vywp__ytdd)):
            val = vywp__ytdd[i]
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
            mun__fytuk = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(mun__fytuk)
            vywp__ytdd = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(vywp__ytdd)):
                if vywp__ytdd[i] == key:
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
    lxdac__mfif = dict(method=method, tolerance=tolerance)
    lnu__vnqu = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', lxdac__mfif, lnu__vnqu,
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
            mun__fytuk = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(mun__fytuk)
            vywp__ytdd = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(vywp__ytdd)):
                if vywp__ytdd[i] == key:
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
        ufv__ntsgb = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                avts__qhhc = len(I)
                hmzxv__lnfa = np.empty(avts__qhhc, np.bool_)
                for i in numba.parfors.parfor.internal_prange(avts__qhhc):
                    hmzxv__lnfa[i] = not ufv__ntsgb
                return hmzxv__lnfa
            return impl
        edmns__ylsl = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if ufv__ntsgb else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        fmdbe__xdgp = {}
        exec(edmns__ylsl, {'bodo': bodo, 'np': np, 'numba': numba}, fmdbe__xdgp
            )
        impl = fmdbe__xdgp['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for ruz__muyfd in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(ruz__muyfd, overload_name, no_unliteral=True,
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
            vywp__ytdd = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(vywp__ytdd, 1)
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
            vywp__ytdd = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(vywp__ytdd, 2)
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
        vywp__ytdd = bodo.hiframes.pd_index_ext.get_index_data(I)
        hmzxv__lnfa = bodo.libs.array_kernels.duplicated((vywp__ytdd,))
        return hmzxv__lnfa
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
    lxdac__mfif = dict(keep=keep)
    lnu__vnqu = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', lxdac__mfif, lnu__vnqu,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    edmns__ylsl = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        edmns__ylsl += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        edmns__ylsl += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'bodo': bodo}, fmdbe__xdgp)
    impl = fmdbe__xdgp['impl']
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
    jioz__tfy = args[0]
    if isinstance(self.typemap[jioz__tfy.name], HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(jioz__tfy):
        return ArrayAnalysis.AnalyzeResult(shape=jioz__tfy, pre=[])
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
    nfb__dbmrp = numba.core.registry.cpu_target.typing_context
    dszb__oywc = numba.core.registry.cpu_target.target_context
    try:
        jhkw__hwjfy = get_const_func_output_type(mapper, (dtype,), {},
            nfb__dbmrp, dszb__oywc)
    except Exception as qic__iovdp:
        raise_bodo_error(get_udf_error_msg('Index.map()', qic__iovdp))
    pqt__anzlq = get_udf_out_arr_type(jhkw__hwjfy)
    func = get_overload_const_func(mapper, None)
    edmns__ylsl = 'def f(I, mapper, na_action=None):\n'
    edmns__ylsl += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    edmns__ylsl += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    edmns__ylsl += '  numba.parfors.parfor.init_prange()\n'
    edmns__ylsl += '  n = len(A)\n'
    edmns__ylsl += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    edmns__ylsl += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    edmns__ylsl += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    edmns__ylsl += '    v = map_func(t2)\n'
    edmns__ylsl += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    edmns__ylsl += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    ughhs__wlc = bodo.compiler.udf_jit(func)
    fmdbe__xdgp = {}
    exec(edmns__ylsl, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': ughhs__wlc, '_arr_typ': pqt__anzlq,
        'init_nested_counts': bodo.utils.indexing.init_nested_counts,
        'add_nested_counts': bodo.utils.indexing.add_nested_counts,
        'data_arr_type': pqt__anzlq.dtype}, fmdbe__xdgp)
    f = fmdbe__xdgp['f']
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
    yig__yuugi, tkct__sgn = sig.args
    if yig__yuugi != tkct__sgn:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    yig__yuugi, tkct__sgn = sig.args
    if yig__yuugi != tkct__sgn:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):

            def impl(lhs, rhs):
                vywp__ytdd = bodo.utils.conversion.coerce_to_array(lhs)
                tbkh__uyi = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                hmzxv__lnfa = op(vywp__ytdd, tbkh__uyi)
                return hmzxv__lnfa
            return impl
        if is_index_type(rhs):

            def impl2(lhs, rhs):
                vywp__ytdd = bodo.utils.conversion.coerce_to_array(rhs)
                tbkh__uyi = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                hmzxv__lnfa = op(tbkh__uyi, vywp__ytdd)
                return hmzxv__lnfa
            return impl2
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    vywp__ytdd = bodo.utils.conversion.coerce_to_array(data)
                    tbkh__uyi = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    hmzxv__lnfa = op(vywp__ytdd, tbkh__uyi)
                    return hmzxv__lnfa
                return impl3
            count = len(lhs.data.types)
            edmns__ylsl = 'def f(lhs, rhs):\n'
            edmns__ylsl += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            fmdbe__xdgp = {}
            exec(edmns__ylsl, {'op': op, 'np': np}, fmdbe__xdgp)
            impl = fmdbe__xdgp['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    vywp__ytdd = bodo.utils.conversion.coerce_to_array(data)
                    tbkh__uyi = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    hmzxv__lnfa = op(tbkh__uyi, vywp__ytdd)
                    return hmzxv__lnfa
                return impl4
            count = len(rhs.data.types)
            edmns__ylsl = 'def f(lhs, rhs):\n'
            edmns__ylsl += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            fmdbe__xdgp = {}
            exec(edmns__ylsl, {'op': op, 'np': np}, fmdbe__xdgp)
            impl = fmdbe__xdgp['f']
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
        hnn__sgdje = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, hnn__sgdje)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    zpxqr__whjov = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    lfx__toe = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', lfx__toe, idx_cpy_arg_defaults,
        fn_str=zpxqr__whjov, package_name='pandas', module_name='Index')
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
    tzch__qgs = c.context.insert_const_string(c.builder.module, 'pandas')
    lsln__uxv = c.pyapi.import_module_noblock(tzch__qgs)
    kmn__bwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, kmn__bwq.data)
    ytmp__ibkog = c.pyapi.from_native_value(typ.data, kmn__bwq.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, kmn__bwq.name)
    qqom__ijru = c.pyapi.from_native_value(typ.name_typ, kmn__bwq.name, c.
        env_manager)
    yfzsz__zbciw = c.pyapi.make_none()
    vguuf__oreea = c.pyapi.bool_from_bool(c.context.get_constant(types.
        bool_, False))
    sbqp__aaxbh = c.pyapi.call_method(lsln__uxv, 'Index', (ytmp__ibkog,
        yfzsz__zbciw, vguuf__oreea, qqom__ijru))
    c.pyapi.decref(ytmp__ibkog)
    c.pyapi.decref(yfzsz__zbciw)
    c.pyapi.decref(vguuf__oreea)
    c.pyapi.decref(qqom__ijru)
    c.pyapi.decref(lsln__uxv)
    c.context.nrt.decref(c.builder, typ, val)
    return sbqp__aaxbh


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        tsl__orry = signature.return_type
        kmn__bwq = cgutils.create_struct_proxy(tsl__orry)(context, builder)
        kmn__bwq.data = args[0]
        kmn__bwq.name = args[1]
        context.nrt.incref(builder, tsl__orry.data, args[0])
        context.nrt.incref(builder, tsl__orry.name_typ, args[1])
        return kmn__bwq._getvalue()
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
    dtrpp__gsg = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in dtrpp__gsg:
        init_func = dtrpp__gsg[type(I)]
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
    jtv__yee = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, jtv__yee])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    jtv__yee = context.get_constant_null(types.DictType(types.int64, types.
        int64))
    return lir.Constant.literal_struct([data, name, jtv__yee])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    jtv__yee = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, jtv__yee])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    hzy__drnnr = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, hzy__drnnr, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    jtv__yee = context.get_constant_null(types.DictType(scalar_type, types.
        int64))
    return lir.Constant.literal_struct([data, name, jtv__yee])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [yiak__fuydi] = sig.args
    [nah__vuo] = args
    feona__uxjbw = context.make_helper(builder, yiak__fuydi, value=nah__vuo)
    jcv__ubm = context.make_helper(builder, sig.return_type)
    ueanw__grhwn = cgutils.alloca_once_value(builder, feona__uxjbw.start)
    kujb__hba = context.get_constant(types.intp, 0)
    zlh__ihoeu = cgutils.alloca_once_value(builder, kujb__hba)
    jcv__ubm.iter = ueanw__grhwn
    jcv__ubm.stop = feona__uxjbw.stop
    jcv__ubm.step = feona__uxjbw.step
    jcv__ubm.count = zlh__ihoeu
    spke__nzk = builder.sub(feona__uxjbw.stop, feona__uxjbw.start)
    qij__zgf = context.get_constant(types.intp, 1)
    xawmx__rdeb = builder.icmp(lc.ICMP_SGT, spke__nzk, kujb__hba)
    qvi__ftq = builder.icmp(lc.ICMP_SGT, feona__uxjbw.step, kujb__hba)
    ekh__vyp = builder.not_(builder.xor(xawmx__rdeb, qvi__ftq))
    with builder.if_then(ekh__vyp):
        bfwj__srv = builder.srem(spke__nzk, feona__uxjbw.step)
        bfwj__srv = builder.select(xawmx__rdeb, bfwj__srv, builder.neg(
            bfwj__srv))
        fnwhg__xkvih = builder.icmp(lc.ICMP_SGT, bfwj__srv, kujb__hba)
        uprj__clisp = builder.add(builder.sdiv(spke__nzk, feona__uxjbw.step
            ), builder.select(fnwhg__xkvih, qij__zgf, kujb__hba))
        builder.store(uprj__clisp, zlh__ihoeu)
    suct__svq = jcv__ubm._getvalue()
    okp__nexgu = impl_ret_new_ref(context, builder, sig.return_type, suct__svq)
    return okp__nexgu


def getiter_index(context, builder, sig, args):
    [yiak__fuydi] = sig.args
    [nah__vuo] = args
    feona__uxjbw = context.make_helper(builder, yiak__fuydi, value=nah__vuo)
    return numba.np.arrayobj.getiter_array(context, builder, signature(sig.
        return_type, sig.args[0].data), (feona__uxjbw.data,))


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
    for cuqbb__oypbm in index_unsupported_methods:
        for vzg__pflo, typ in index_types:
            overload_method(typ, cuqbb__oypbm, no_unliteral=True)(
                create_unsupported_overload(vzg__pflo.format(cuqbb__oypbm +
                '()')))
    for nudtj__uwf in index_unsupported_atrs:
        for vzg__pflo, typ in index_types:
            overload_attribute(typ, nudtj__uwf, no_unliteral=True)(
                create_unsupported_overload(vzg__pflo.format(nudtj__uwf)))
    ccbvm__lpg = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    hrk__kmrj = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods)]
    for typ, chcms__mdg in hrk__kmrj:
        vzg__pflo = idx_typ_to_format_str_map[typ]
        for kgra__vwvd in chcms__mdg:
            overload_method(typ, kgra__vwvd, no_unliteral=True)(
                create_unsupported_overload(vzg__pflo.format(kgra__vwvd +
                '()')))
    for typ, zhcwm__pqpo in ccbvm__lpg:
        vzg__pflo = idx_typ_to_format_str_map[typ]
        for nudtj__uwf in zhcwm__pqpo:
            overload_attribute(typ, nudtj__uwf, no_unliteral=True)(
                create_unsupported_overload(vzg__pflo.format(nudtj__uwf)))
    for nub__ommu in [RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, MultiIndexType]:
        for kgra__vwvd in ['max', 'min']:
            vzg__pflo = idx_typ_to_format_str_map[nub__ommu]
            overload_method(nub__ommu, kgra__vwvd, no_unliteral=True)(
                create_unsupported_overload(vzg__pflo.format(kgra__vwvd +
                '()')))


_install_index_unsupported()
