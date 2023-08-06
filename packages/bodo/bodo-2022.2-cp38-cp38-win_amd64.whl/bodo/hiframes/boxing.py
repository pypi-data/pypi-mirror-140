"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    kbz__ijfse = tuple(val.columns.to_list())
    hbzxd__qsyx = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        bisf__nso = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        bisf__nso = numba.typeof(val.index)
    pxr__lanvo = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    dlonx__szenj = len(hbzxd__qsyx) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(hbzxd__qsyx, bisf__nso, kbz__ijfse, pxr__lanvo,
        is_table_format=dlonx__szenj)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    pxr__lanvo = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        yxqa__kbnwu = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        yxqa__kbnwu = numba.typeof(val.index)
    return SeriesType(_infer_series_dtype(val), index=yxqa__kbnwu, name_typ
        =numba.typeof(val.name), dist=pxr__lanvo)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    khmuq__jmbu = c.pyapi.object_getattr_string(val, 'index')
    kxzq__zxzz = c.pyapi.to_native_value(typ.index, khmuq__jmbu).value
    c.pyapi.decref(khmuq__jmbu)
    if typ.is_table_format:
        tzx__ahkmf = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        tzx__ahkmf.parent = val
        for tuy__hmwfs, rxrj__fvia in typ.table_type.type_to_blk.items():
            spsl__olf = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[rxrj__fvia]))
            qvwup__vqwvl, hdp__eyk = ListInstance.allocate_ex(c.context, c.
                builder, types.List(tuy__hmwfs), spsl__olf)
            hdp__eyk.size = spsl__olf
            setattr(tzx__ahkmf, f'block_{rxrj__fvia}', hdp__eyk.value)
        pdoc__tmlk = c.pyapi.call_method(val, '__len__', ())
        voyg__nmt = c.pyapi.long_as_longlong(pdoc__tmlk)
        c.pyapi.decref(pdoc__tmlk)
        tzx__ahkmf.len = voyg__nmt
        nhbwt__iatiq = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [tzx__ahkmf._getvalue()])
    else:
        grsyw__bjln = [c.context.get_constant_null(tuy__hmwfs) for
            tuy__hmwfs in typ.data]
        nhbwt__iatiq = c.context.make_tuple(c.builder, types.Tuple(typ.data
            ), grsyw__bjln)
    cswix__mnzcn = construct_dataframe(c.context, c.builder, typ,
        nhbwt__iatiq, kxzq__zxzz, val, None)
    return NativeValue(cswix__mnzcn)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        moe__rfyp = df._bodo_meta['type_metadata'][1]
    else:
        moe__rfyp = [None] * len(df.columns)
    pns__lrab = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=moe__rfyp[i])) for i in range(len(df.columns))]
    return tuple(pns__lrab)


class SeriesDtypeEnum(Enum):
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
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    mjvy__gopf, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(mjvy__gopf) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {mjvy__gopf}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        pxrq__duj, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return pxrq__duj, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        pxrq__duj, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return pxrq__duj, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        wgtdo__itgsi = typ_enum_list[1]
        uss__ceh = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(wgtdo__itgsi, uss__ceh)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        afud__xmawl = typ_enum_list[1]
        hadz__psry = tuple(typ_enum_list[2:2 + afud__xmawl])
        brjs__zanw = typ_enum_list[2 + afud__xmawl:]
        igz__adar = []
        for i in range(afud__xmawl):
            brjs__zanw, aamf__cgpx = _dtype_from_type_enum_list_recursor(
                brjs__zanw)
            igz__adar.append(aamf__cgpx)
        return brjs__zanw, StructType(tuple(igz__adar), hadz__psry)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        mpe__ztfp = typ_enum_list[1]
        brjs__zanw = typ_enum_list[2:]
        return brjs__zanw, mpe__ztfp
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        mpe__ztfp = typ_enum_list[1]
        brjs__zanw = typ_enum_list[2:]
        return brjs__zanw, numba.types.literal(mpe__ztfp)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        brjs__zanw, xrkl__ifg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        brjs__zanw, vlyp__anca = _dtype_from_type_enum_list_recursor(brjs__zanw
            )
        brjs__zanw, fhc__hsegb = _dtype_from_type_enum_list_recursor(brjs__zanw
            )
        brjs__zanw, bbmlv__ean = _dtype_from_type_enum_list_recursor(brjs__zanw
            )
        brjs__zanw, xxvnk__apg = _dtype_from_type_enum_list_recursor(brjs__zanw
            )
        return brjs__zanw, PDCategoricalDtype(xrkl__ifg, vlyp__anca,
            fhc__hsegb, bbmlv__ean, xxvnk__apg)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return brjs__zanw, DatetimeIndexType(yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        brjs__zanw, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            brjs__zanw)
        brjs__zanw, bbmlv__ean = _dtype_from_type_enum_list_recursor(brjs__zanw
            )
        return brjs__zanw, NumericIndexType(dtype, yuhn__pyvvq, bbmlv__ean)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        brjs__zanw, gwgli__tekhc = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            brjs__zanw)
        return brjs__zanw, PeriodIndexType(gwgli__tekhc, yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        brjs__zanw, bbmlv__ean = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            brjs__zanw)
        return brjs__zanw, CategoricalIndexType(bbmlv__ean, yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return brjs__zanw, RangeIndexType(yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return brjs__zanw, StringIndexType(yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return brjs__zanw, BinaryIndexType(yuhn__pyvvq)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        brjs__zanw, yuhn__pyvvq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return brjs__zanw, TimedeltaIndexType(yuhn__pyvvq)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        usy__dbod = get_overload_const_int(typ)
        if numba.types.maybe_literal(usy__dbod) == typ:
            return [SeriesDtypeEnum.LiteralType.value, usy__dbod]
    elif is_overload_constant_str(typ):
        usy__dbod = get_overload_const_str(typ)
        if numba.types.maybe_literal(usy__dbod) == typ:
            return [SeriesDtypeEnum.LiteralType.value, usy__dbod]
    elif is_overload_constant_bool(typ):
        usy__dbod = get_overload_const_bool(typ)
        if numba.types.maybe_literal(usy__dbod) == typ:
            return [SeriesDtypeEnum.LiteralType.value, usy__dbod]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        bieb__mjct = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for wrhil__kquej in typ.names:
            bieb__mjct.append(wrhil__kquej)
        for uhou__wzmzr in typ.data:
            bieb__mjct += _dtype_to_type_enum_list_recursor(uhou__wzmzr)
        return bieb__mjct
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        dyrd__lwj = _dtype_to_type_enum_list_recursor(typ.categories)
        vgznt__ugxt = _dtype_to_type_enum_list_recursor(typ.elem_type)
        xug__ejorn = _dtype_to_type_enum_list_recursor(typ.ordered)
        bfc__bcbcx = _dtype_to_type_enum_list_recursor(typ.data)
        nvhuo__fto = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + dyrd__lwj + vgznt__ugxt + xug__ejorn + bfc__bcbcx + nvhuo__fto
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                rsq__zntq = types.float64
                blgay__bdzov = types.Array(rsq__zntq, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                rsq__zntq = types.int64
                blgay__bdzov = types.Array(rsq__zntq, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                rsq__zntq = types.uint64
                blgay__bdzov = types.Array(rsq__zntq, 1, 'C')
            elif typ.dtype == types.bool_:
                rsq__zntq = typ.dtype
                blgay__bdzov = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(rsq__zntq
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(blgay__bdzov)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0:
            if (hasattr(S, '_bodo_meta') and S._bodo_meta is not None and 
                'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None):
                qozst__wll = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(qozst__wll)
            elif array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        raise BodoError('Timezone-aware datetime data type not supported yet')
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    jqbdv__tfcsw = cgutils.is_not_null(builder, parent_obj)
    arzz__sos = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(jqbdv__tfcsw):
        auosq__ohhtd = pyapi.object_getattr_string(parent_obj, 'columns')
        pdoc__tmlk = pyapi.call_method(auosq__ohhtd, '__len__', ())
        builder.store(pyapi.long_as_longlong(pdoc__tmlk), arzz__sos)
        pyapi.decref(pdoc__tmlk)
        pyapi.decref(auosq__ohhtd)
    use_parent_obj = builder.and_(jqbdv__tfcsw, builder.icmp_unsigned('==',
        builder.load(arzz__sos), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        tpqg__odiqg = df_typ.runtime_colname_typ
        context.nrt.incref(builder, tpqg__odiqg, dataframe_payload.columns)
        return pyapi.from_native_value(tpqg__odiqg, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, int) for c in df_typ.columns):
        nswwy__yfdvq = np.array(df_typ.columns, 'int64')
    elif all(isinstance(c, str) for c in df_typ.columns):
        nswwy__yfdvq = pd.array(df_typ.columns, 'string')
    else:
        nswwy__yfdvq = df_typ.columns
    ehyo__uxo = numba.typeof(nswwy__yfdvq)
    geki__bvft = context.get_constant_generic(builder, ehyo__uxo, nswwy__yfdvq)
    cpdbr__fjhtz = pyapi.from_native_value(ehyo__uxo, geki__bvft, c.env_manager
        )
    return cpdbr__fjhtz


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (use_parent, otherwise):
        with use_parent:
            pyapi.incref(obj)
            iizs__lpp = context.insert_const_string(c.builder.module, 'numpy')
            swsl__rui = pyapi.import_module_noblock(iizs__lpp)
            if df_typ.has_runtime_cols:
                waq__qkcg = 0
            else:
                waq__qkcg = len(df_typ.columns)
            ncj__wto = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), waq__qkcg))
            edcj__nmyf = pyapi.call_method(swsl__rui, 'arange', (ncj__wto,))
            pyapi.object_setattr_string(obj, 'columns', edcj__nmyf)
            pyapi.decref(swsl__rui)
            pyapi.decref(edcj__nmyf)
            pyapi.decref(ncj__wto)
        with otherwise:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            dhyia__jlr = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            iizs__lpp = context.insert_const_string(c.builder.module, 'pandas')
            swsl__rui = pyapi.import_module_noblock(iizs__lpp)
            df_obj = pyapi.call_method(swsl__rui, 'DataFrame', (pyapi.
                borrow_none(), dhyia__jlr))
            pyapi.decref(swsl__rui)
            pyapi.decref(dhyia__jlr)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    pbjx__chfbp = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = pbjx__chfbp.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        tpvky__mknsm = typ.table_type
        tzx__ahkmf = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, tpvky__mknsm, tzx__ahkmf)
        wpvzp__ssub = box_table(tpvky__mknsm, tzx__ahkmf, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (then, orelse):
            with then:
                dowy__kdxme = pyapi.object_getattr_string(wpvzp__ssub, 'arrays'
                    )
                husk__ifdb = c.pyapi.make_none()
                if n_cols is None:
                    pdoc__tmlk = pyapi.call_method(dowy__kdxme, '__len__', ())
                    spsl__olf = pyapi.long_as_longlong(pdoc__tmlk)
                    pyapi.decref(pdoc__tmlk)
                else:
                    spsl__olf = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, spsl__olf) as loop:
                    i = loop.index
                    rsscr__hwpb = pyapi.list_getitem(dowy__kdxme, i)
                    dpn__krft = c.builder.icmp_unsigned('!=', rsscr__hwpb,
                        husk__ifdb)
                    with builder.if_then(dpn__krft):
                        kysk__pey = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, kysk__pey, rsscr__hwpb)
                        pyapi.decref(kysk__pey)
                pyapi.decref(dowy__kdxme)
                pyapi.decref(husk__ifdb)
            with orelse:
                df_obj = builder.load(res)
                dhyia__jlr = pyapi.object_getattr_string(df_obj, 'index')
                xirsb__nhz = c.pyapi.call_method(wpvzp__ssub, 'to_pandas',
                    (dhyia__jlr,))
                builder.store(xirsb__nhz, res)
                pyapi.decref(df_obj)
                pyapi.decref(dhyia__jlr)
        pyapi.decref(wpvzp__ssub)
    else:
        vkxcs__qxha = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        yam__kenu = typ.data
        for i, upwfy__lrdn, nab__nppm in zip(range(n_cols), vkxcs__qxha,
            yam__kenu):
            guu__tsww = cgutils.alloca_once_value(builder, upwfy__lrdn)
            eswwt__myq = cgutils.alloca_once_value(builder, context.
                get_constant_null(nab__nppm))
            dpn__krft = builder.not_(is_ll_eq(builder, guu__tsww, eswwt__myq))
            qzybu__edyra = builder.or_(builder.not_(use_parent_obj),
                builder.and_(use_parent_obj, dpn__krft))
            with builder.if_then(qzybu__edyra):
                kysk__pey = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, nab__nppm, upwfy__lrdn)
                arr_obj = pyapi.from_native_value(nab__nppm, upwfy__lrdn, c
                    .env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, kysk__pey, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(kysk__pey)
    df_obj = builder.load(res)
    cpdbr__fjhtz = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', cpdbr__fjhtz)
    pyapi.decref(cpdbr__fjhtz)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    husk__ifdb = pyapi.borrow_none()
    ugqt__oobu = pyapi.unserialize(pyapi.serialize_object(slice))
    epxt__atgse = pyapi.call_function_objargs(ugqt__oobu, [husk__ifdb])
    lhrzs__nlui = pyapi.long_from_longlong(col_ind)
    uie__pybnl = pyapi.tuple_pack([epxt__atgse, lhrzs__nlui])
    tnhcc__wjx = pyapi.object_getattr_string(df_obj, 'iloc')
    vvyh__pxzut = pyapi.object_getitem(tnhcc__wjx, uie__pybnl)
    uyjz__ywrs = pyapi.object_getattr_string(vvyh__pxzut, 'values')
    if isinstance(data_typ, types.Array):
        dsi__cuvuw = context.insert_const_string(builder.module, 'numpy')
        pxor__aamlj = pyapi.import_module_noblock(dsi__cuvuw)
        arr_obj = pyapi.call_method(pxor__aamlj, 'ascontiguousarray', (
            uyjz__ywrs,))
        pyapi.decref(uyjz__ywrs)
        pyapi.decref(pxor__aamlj)
    else:
        arr_obj = uyjz__ywrs
    pyapi.decref(ugqt__oobu)
    pyapi.decref(epxt__atgse)
    pyapi.decref(lhrzs__nlui)
    pyapi.decref(uie__pybnl)
    pyapi.decref(tnhcc__wjx)
    pyapi.decref(vvyh__pxzut)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        pbjx__chfbp = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            pbjx__chfbp.parent, args[1], data_typ)
        hlh__zfimf = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            tzx__ahkmf = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            rxrj__fvia = df_typ.table_type.type_to_blk[data_typ]
            etu__rzo = getattr(tzx__ahkmf, f'block_{rxrj__fvia}')
            yqkd__efoz = ListInstance(c.context, c.builder, types.List(
                data_typ), etu__rzo)
            rrqdx__jud = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            yqkd__efoz.inititem(rrqdx__jud, hlh__zfimf.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, hlh__zfimf.value, col_ind)
        isc__ivjv = DataFramePayloadType(df_typ)
        dqmo__fgxab = context.nrt.meminfo_data(builder, pbjx__chfbp.meminfo)
        zvf__auj = context.get_value_type(isc__ivjv).as_pointer()
        dqmo__fgxab = builder.bitcast(dqmo__fgxab, zvf__auj)
        builder.store(dataframe_payload._getvalue(), dqmo__fgxab)
    return signature(types.none, df, i), codegen


@unbox(SeriesType)
def unbox_series(typ, val, c):
    uyjz__ywrs = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        dsi__cuvuw = c.context.insert_const_string(c.builder.module, 'numpy')
        pxor__aamlj = c.pyapi.import_module_noblock(dsi__cuvuw)
        arr_obj = c.pyapi.call_method(pxor__aamlj, 'ascontiguousarray', (
            uyjz__ywrs,))
        c.pyapi.decref(uyjz__ywrs)
        c.pyapi.decref(pxor__aamlj)
    else:
        arr_obj = uyjz__ywrs
    iqrr__pmwu = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    dhyia__jlr = c.pyapi.object_getattr_string(val, 'index')
    kxzq__zxzz = c.pyapi.to_native_value(typ.index, dhyia__jlr).value
    yyrgk__ffeg = c.pyapi.object_getattr_string(val, 'name')
    jft__hhtvz = c.pyapi.to_native_value(typ.name_typ, yyrgk__ffeg).value
    ufmcp__cjmdr = bodo.hiframes.pd_series_ext.construct_series(c.context,
        c.builder, typ, iqrr__pmwu, kxzq__zxzz, jft__hhtvz)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(dhyia__jlr)
    c.pyapi.decref(yyrgk__ffeg)
    return NativeValue(ufmcp__cjmdr)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        zbx__yqpmh = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(zbx__yqpmh._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    iizs__lpp = c.context.insert_const_string(c.builder.module, 'pandas')
    kehp__njqwx = c.pyapi.import_module_noblock(iizs__lpp)
    kxvlu__fzlr = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, kxvlu__fzlr.data)
    c.context.nrt.incref(c.builder, typ.index, kxvlu__fzlr.index)
    c.context.nrt.incref(c.builder, typ.name_typ, kxvlu__fzlr.name)
    arr_obj = c.pyapi.from_native_value(typ.data, kxvlu__fzlr.data, c.
        env_manager)
    dhyia__jlr = c.pyapi.from_native_value(typ.index, kxvlu__fzlr.index, c.
        env_manager)
    yyrgk__ffeg = c.pyapi.from_native_value(typ.name_typ, kxvlu__fzlr.name,
        c.env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(kehp__njqwx, 'Series', (arr_obj, dhyia__jlr,
        dtype, yyrgk__ffeg))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(dhyia__jlr)
    c.pyapi.decref(yyrgk__ffeg)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(kehp__njqwx)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    ltto__fcq = []
    for sbvi__ojft in typ_list:
        if isinstance(sbvi__ojft, int) and not isinstance(sbvi__ojft, bool):
            lxx__jwe = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), sbvi__ojft))
        else:
            hfu__iglmm = numba.typeof(sbvi__ojft)
            wkhfl__ehke = context.get_constant_generic(builder, hfu__iglmm,
                sbvi__ojft)
            lxx__jwe = pyapi.from_native_value(hfu__iglmm, wkhfl__ehke,
                env_manager)
        ltto__fcq.append(lxx__jwe)
    bdmd__gsbjs = pyapi.list_pack(ltto__fcq)
    for val in ltto__fcq:
        pyapi.decref(val)
    return bdmd__gsbjs


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    nrrdq__exlk = not typ.has_runtime_cols and (not typ.is_table_format or 
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    bcfq__mmg = 2 if nrrdq__exlk else 1
    aowj__tdmt = pyapi.dict_new(bcfq__mmg)
    eeoe__nho = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    pyapi.dict_setitem_string(aowj__tdmt, 'dist', eeoe__nho)
    pyapi.decref(eeoe__nho)
    if nrrdq__exlk:
        zqs__axa = _dtype_to_type_enum_list(typ.index)
        if zqs__axa != None:
            ddpi__jup = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, zqs__axa)
        else:
            ddpi__jup = pyapi.make_none()
        bbdf__hhm = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                bdmd__gsbjs = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                bdmd__gsbjs = pyapi.make_none()
            bbdf__hhm.append(bdmd__gsbjs)
        tgor__tcqy = pyapi.list_pack(bbdf__hhm)
        jwrv__xev = pyapi.list_pack([ddpi__jup, tgor__tcqy])
        for val in bbdf__hhm:
            pyapi.decref(val)
        pyapi.dict_setitem_string(aowj__tdmt, 'type_metadata', jwrv__xev)
    pyapi.object_setattr_string(obj, '_bodo_meta', aowj__tdmt)
    pyapi.decref(aowj__tdmt)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    aowj__tdmt = pyapi.dict_new(2)
    eeoe__nho = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    zqs__axa = _dtype_to_type_enum_list(typ.index)
    if zqs__axa != None:
        ddpi__jup = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, zqs__axa)
    else:
        ddpi__jup = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            zufqd__xrpvm = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            zufqd__xrpvm = pyapi.make_none()
    else:
        zufqd__xrpvm = pyapi.make_none()
    yewoq__yib = pyapi.list_pack([ddpi__jup, zufqd__xrpvm])
    pyapi.dict_setitem_string(aowj__tdmt, 'type_metadata', yewoq__yib)
    pyapi.decref(yewoq__yib)
    pyapi.dict_setitem_string(aowj__tdmt, 'dist', eeoe__nho)
    pyapi.object_setattr_string(obj, '_bodo_meta', aowj__tdmt)
    pyapi.decref(aowj__tdmt)
    pyapi.decref(eeoe__nho)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as dhi__poyu:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    usj__rtds = numba.np.numpy_support.map_layout(val)
    qzd__hau = not val.flags.writeable
    return types.Array(dtype, val.ndim, usj__rtds, readonly=qzd__hau)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    defp__yxj = val[i]
    if isinstance(defp__yxj, str):
        return string_array_type
    elif isinstance(defp__yxj, bytes):
        return binary_array_type
    elif isinstance(defp__yxj, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(defp__yxj, (int, np.int32, np.int64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(defp__yxj))
    elif isinstance(defp__yxj, (dict, Dict)) and all(isinstance(owyyx__qrz,
        str) for owyyx__qrz in defp__yxj.keys()):
        hadz__psry = tuple(defp__yxj.keys())
        lghrq__ritye = tuple(_get_struct_value_arr_type(v) for v in
            defp__yxj.values())
        return StructArrayType(lghrq__ritye, hadz__psry)
    elif isinstance(defp__yxj, (dict, Dict)):
        bic__vwkuh = numba.typeof(_value_to_array(list(defp__yxj.keys())))
        kxvjg__eezat = numba.typeof(_value_to_array(list(defp__yxj.values())))
        return MapArrayType(bic__vwkuh, kxvjg__eezat)
    elif isinstance(defp__yxj, tuple):
        lghrq__ritye = tuple(_get_struct_value_arr_type(v) for v in defp__yxj)
        return TupleArrayType(lghrq__ritye)
    if isinstance(defp__yxj, (list, np.ndarray, pd.arrays.BooleanArray, pd.
        arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(defp__yxj, list):
            defp__yxj = _value_to_array(defp__yxj)
        nyeoz__lxc = numba.typeof(defp__yxj)
        return ArrayItemArrayType(nyeoz__lxc)
    if isinstance(defp__yxj, datetime.date):
        return datetime_date_array_type
    if isinstance(defp__yxj, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(defp__yxj, decimal.Decimal):
        return DecimalArrayType(38, 18)
    raise BodoError('Unsupported object array with first value: {}'.format(
        defp__yxj))


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    axq__dsna = val.copy()
    axq__dsna.append(None)
    upwfy__lrdn = np.array(axq__dsna, np.object_)
    if len(val) and isinstance(val[0], float):
        upwfy__lrdn = np.array(val, np.float64)
    return upwfy__lrdn


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    nab__nppm = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        nab__nppm = to_nullable_type(nab__nppm)
    return nab__nppm
