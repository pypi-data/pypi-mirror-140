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
    nbsv__ybhfd = tuple(val.columns.to_list())
    hez__bwj = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        ltw__cggaz = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        ltw__cggaz = numba.typeof(val.index)
    qtrai__jcm = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    hopfp__uwx = len(hez__bwj) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(hez__bwj, ltw__cggaz, nbsv__ybhfd, qtrai__jcm,
        is_table_format=hopfp__uwx)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    qtrai__jcm = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        azt__zoykg = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        azt__zoykg = numba.typeof(val.index)
    return SeriesType(_infer_series_dtype(val), index=azt__zoykg, name_typ=
        numba.typeof(val.name), dist=qtrai__jcm)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    zcl__gxw = c.pyapi.object_getattr_string(val, 'index')
    wkz__fwx = c.pyapi.to_native_value(typ.index, zcl__gxw).value
    c.pyapi.decref(zcl__gxw)
    if typ.is_table_format:
        yzd__mldgq = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        yzd__mldgq.parent = val
        for ycd__zfnr, tgefu__injo in typ.table_type.type_to_blk.items():
            uszs__kyss = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[tgefu__injo]))
            bjhbt__guff, rehdq__matr = ListInstance.allocate_ex(c.context,
                c.builder, types.List(ycd__zfnr), uszs__kyss)
            rehdq__matr.size = uszs__kyss
            setattr(yzd__mldgq, f'block_{tgefu__injo}', rehdq__matr.value)
        blcx__msw = c.pyapi.call_method(val, '__len__', ())
        cjiw__cbdd = c.pyapi.long_as_longlong(blcx__msw)
        c.pyapi.decref(blcx__msw)
        yzd__mldgq.len = cjiw__cbdd
        fupco__xpvz = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [yzd__mldgq._getvalue()])
    else:
        roxhy__nnni = [c.context.get_constant_null(ycd__zfnr) for ycd__zfnr in
            typ.data]
        fupco__xpvz = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            roxhy__nnni)
    zhzx__akgq = construct_dataframe(c.context, c.builder, typ, fupco__xpvz,
        wkz__fwx, val, None)
    return NativeValue(zhzx__akgq)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        tlte__jgel = df._bodo_meta['type_metadata'][1]
    else:
        tlte__jgel = [None] * len(df.columns)
    fmgdy__vzx = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=tlte__jgel[i])) for i in range(len(df.columns))]
    return tuple(fmgdy__vzx)


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
    uhjz__grtus, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(uhjz__grtus) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {uhjz__grtus}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        hzwd__nxym, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return hzwd__nxym, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        hzwd__nxym, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return hzwd__nxym, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        afid__gfet = typ_enum_list[1]
        stw__ddk = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(afid__gfet, stw__ddk)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        zdk__ghun = typ_enum_list[1]
        yma__dmln = tuple(typ_enum_list[2:2 + zdk__ghun])
        ifa__esdj = typ_enum_list[2 + zdk__ghun:]
        fcbu__rve = []
        for i in range(zdk__ghun):
            ifa__esdj, unt__sjyie = _dtype_from_type_enum_list_recursor(
                ifa__esdj)
            fcbu__rve.append(unt__sjyie)
        return ifa__esdj, StructType(tuple(fcbu__rve), yma__dmln)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        duk__nhwb = typ_enum_list[1]
        ifa__esdj = typ_enum_list[2:]
        return ifa__esdj, duk__nhwb
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        duk__nhwb = typ_enum_list[1]
        ifa__esdj = typ_enum_list[2:]
        return ifa__esdj, numba.types.literal(duk__nhwb)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        ifa__esdj, sysd__obam = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ifa__esdj, hehyo__var = _dtype_from_type_enum_list_recursor(ifa__esdj)
        ifa__esdj, hwas__xhnwh = _dtype_from_type_enum_list_recursor(ifa__esdj)
        ifa__esdj, wty__mqoh = _dtype_from_type_enum_list_recursor(ifa__esdj)
        ifa__esdj, wjfii__cewbv = _dtype_from_type_enum_list_recursor(ifa__esdj
            )
        return ifa__esdj, PDCategoricalDtype(sysd__obam, hehyo__var,
            hwas__xhnwh, wty__mqoh, wjfii__cewbv)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ifa__esdj, DatetimeIndexType(uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        ifa__esdj, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(ifa__esdj)
        ifa__esdj, wty__mqoh = _dtype_from_type_enum_list_recursor(ifa__esdj)
        return ifa__esdj, NumericIndexType(dtype, uei__tfbsj, wty__mqoh)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        ifa__esdj, xzul__gha = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(ifa__esdj)
        return ifa__esdj, PeriodIndexType(xzul__gha, uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        ifa__esdj, wty__mqoh = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(ifa__esdj)
        return ifa__esdj, CategoricalIndexType(wty__mqoh, uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ifa__esdj, RangeIndexType(uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ifa__esdj, StringIndexType(uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ifa__esdj, BinaryIndexType(uei__tfbsj)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        ifa__esdj, uei__tfbsj = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ifa__esdj, TimedeltaIndexType(uei__tfbsj)
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
        nmxer__bvqte = get_overload_const_int(typ)
        if numba.types.maybe_literal(nmxer__bvqte) == typ:
            return [SeriesDtypeEnum.LiteralType.value, nmxer__bvqte]
    elif is_overload_constant_str(typ):
        nmxer__bvqte = get_overload_const_str(typ)
        if numba.types.maybe_literal(nmxer__bvqte) == typ:
            return [SeriesDtypeEnum.LiteralType.value, nmxer__bvqte]
    elif is_overload_constant_bool(typ):
        nmxer__bvqte = get_overload_const_bool(typ)
        if numba.types.maybe_literal(nmxer__bvqte) == typ:
            return [SeriesDtypeEnum.LiteralType.value, nmxer__bvqte]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        ixg__rgjt = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for humi__nan in typ.names:
            ixg__rgjt.append(humi__nan)
        for eunso__asf in typ.data:
            ixg__rgjt += _dtype_to_type_enum_list_recursor(eunso__asf)
        return ixg__rgjt
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        pgn__fob = _dtype_to_type_enum_list_recursor(typ.categories)
        idnt__wmr = _dtype_to_type_enum_list_recursor(typ.elem_type)
        bgq__bqe = _dtype_to_type_enum_list_recursor(typ.ordered)
        ftike__eoezp = _dtype_to_type_enum_list_recursor(typ.data)
        bhbf__fcy = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + pgn__fob + idnt__wmr + bgq__bqe + ftike__eoezp + bhbf__fcy
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                twt__ijnen = types.float64
                gqrpu__oac = types.Array(twt__ijnen, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                twt__ijnen = types.int64
                gqrpu__oac = types.Array(twt__ijnen, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                twt__ijnen = types.uint64
                gqrpu__oac = types.Array(twt__ijnen, 1, 'C')
            elif typ.dtype == types.bool_:
                twt__ijnen = typ.dtype
                gqrpu__oac = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(twt__ijnen
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(gqrpu__oac)
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
                zdmei__pmim = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(zdmei__pmim)
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
    ldfft__ibovt = cgutils.is_not_null(builder, parent_obj)
    dqhjm__vwfpm = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(ldfft__ibovt):
        mxxu__aycrn = pyapi.object_getattr_string(parent_obj, 'columns')
        blcx__msw = pyapi.call_method(mxxu__aycrn, '__len__', ())
        builder.store(pyapi.long_as_longlong(blcx__msw), dqhjm__vwfpm)
        pyapi.decref(blcx__msw)
        pyapi.decref(mxxu__aycrn)
    use_parent_obj = builder.and_(ldfft__ibovt, builder.icmp_unsigned('==',
        builder.load(dqhjm__vwfpm), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        ohxbc__mpg = df_typ.runtime_colname_typ
        context.nrt.incref(builder, ohxbc__mpg, dataframe_payload.columns)
        return pyapi.from_native_value(ohxbc__mpg, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, int) for c in df_typ.columns):
        cvb__jpz = np.array(df_typ.columns, 'int64')
    elif all(isinstance(c, str) for c in df_typ.columns):
        cvb__jpz = pd.array(df_typ.columns, 'string')
    else:
        cvb__jpz = df_typ.columns
    dmm__ymkw = numba.typeof(cvb__jpz)
    wus__cygcn = context.get_constant_generic(builder, dmm__ymkw, cvb__jpz)
    obwyw__shvwt = pyapi.from_native_value(dmm__ymkw, wus__cygcn, c.env_manager
        )
    return obwyw__shvwt


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (use_parent, otherwise):
        with use_parent:
            pyapi.incref(obj)
            qfkws__jguaj = context.insert_const_string(c.builder.module,
                'numpy')
            hsxwd__iguyg = pyapi.import_module_noblock(qfkws__jguaj)
            if df_typ.has_runtime_cols:
                mtnb__bckg = 0
            else:
                mtnb__bckg = len(df_typ.columns)
            gcdb__eigi = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), mtnb__bckg))
            ewp__oujjv = pyapi.call_method(hsxwd__iguyg, 'arange', (
                gcdb__eigi,))
            pyapi.object_setattr_string(obj, 'columns', ewp__oujjv)
            pyapi.decref(hsxwd__iguyg)
            pyapi.decref(ewp__oujjv)
            pyapi.decref(gcdb__eigi)
        with otherwise:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            bntzk__rti = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            qfkws__jguaj = context.insert_const_string(c.builder.module,
                'pandas')
            hsxwd__iguyg = pyapi.import_module_noblock(qfkws__jguaj)
            df_obj = pyapi.call_method(hsxwd__iguyg, 'DataFrame', (pyapi.
                borrow_none(), bntzk__rti))
            pyapi.decref(hsxwd__iguyg)
            pyapi.decref(bntzk__rti)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    ddw__ygsiu = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = ddw__ygsiu.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        sduq__uksfx = typ.table_type
        yzd__mldgq = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, sduq__uksfx, yzd__mldgq)
        cyuzz__smm = box_table(sduq__uksfx, yzd__mldgq, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (then, orelse):
            with then:
                ndnt__biv = pyapi.object_getattr_string(cyuzz__smm, 'arrays')
                nuyb__ozozl = c.pyapi.make_none()
                if n_cols is None:
                    blcx__msw = pyapi.call_method(ndnt__biv, '__len__', ())
                    uszs__kyss = pyapi.long_as_longlong(blcx__msw)
                    pyapi.decref(blcx__msw)
                else:
                    uszs__kyss = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, uszs__kyss) as loop:
                    i = loop.index
                    vcown__nxbq = pyapi.list_getitem(ndnt__biv, i)
                    xsl__hhvt = c.builder.icmp_unsigned('!=', vcown__nxbq,
                        nuyb__ozozl)
                    with builder.if_then(xsl__hhvt):
                        mbpwr__cxy = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, mbpwr__cxy, vcown__nxbq)
                        pyapi.decref(mbpwr__cxy)
                pyapi.decref(ndnt__biv)
                pyapi.decref(nuyb__ozozl)
            with orelse:
                df_obj = builder.load(res)
                bntzk__rti = pyapi.object_getattr_string(df_obj, 'index')
                sjiux__yvcy = c.pyapi.call_method(cyuzz__smm, 'to_pandas',
                    (bntzk__rti,))
                builder.store(sjiux__yvcy, res)
                pyapi.decref(df_obj)
                pyapi.decref(bntzk__rti)
        pyapi.decref(cyuzz__smm)
    else:
        rll__papgh = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        rpju__jqm = typ.data
        for i, vqgyn__opb, gyo__gkzi in zip(range(n_cols), rll__papgh,
            rpju__jqm):
            bvi__hga = cgutils.alloca_once_value(builder, vqgyn__opb)
            uuilr__zjfyo = cgutils.alloca_once_value(builder, context.
                get_constant_null(gyo__gkzi))
            xsl__hhvt = builder.not_(is_ll_eq(builder, bvi__hga, uuilr__zjfyo))
            rfcxx__drox = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, xsl__hhvt))
            with builder.if_then(rfcxx__drox):
                mbpwr__cxy = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, gyo__gkzi, vqgyn__opb)
                arr_obj = pyapi.from_native_value(gyo__gkzi, vqgyn__opb, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, mbpwr__cxy, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(mbpwr__cxy)
    df_obj = builder.load(res)
    obwyw__shvwt = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', obwyw__shvwt)
    pyapi.decref(obwyw__shvwt)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    nuyb__ozozl = pyapi.borrow_none()
    xfnk__uuybt = pyapi.unserialize(pyapi.serialize_object(slice))
    yrz__odisg = pyapi.call_function_objargs(xfnk__uuybt, [nuyb__ozozl])
    auu__dirjp = pyapi.long_from_longlong(col_ind)
    bicz__bztzd = pyapi.tuple_pack([yrz__odisg, auu__dirjp])
    ghdxo__gdcpx = pyapi.object_getattr_string(df_obj, 'iloc')
    luutq__tdz = pyapi.object_getitem(ghdxo__gdcpx, bicz__bztzd)
    nllpm__kjf = pyapi.object_getattr_string(luutq__tdz, 'values')
    if isinstance(data_typ, types.Array):
        bwtwj__kqnwx = context.insert_const_string(builder.module, 'numpy')
        lhws__zmir = pyapi.import_module_noblock(bwtwj__kqnwx)
        arr_obj = pyapi.call_method(lhws__zmir, 'ascontiguousarray', (
            nllpm__kjf,))
        pyapi.decref(nllpm__kjf)
        pyapi.decref(lhws__zmir)
    else:
        arr_obj = nllpm__kjf
    pyapi.decref(xfnk__uuybt)
    pyapi.decref(yrz__odisg)
    pyapi.decref(auu__dirjp)
    pyapi.decref(bicz__bztzd)
    pyapi.decref(ghdxo__gdcpx)
    pyapi.decref(luutq__tdz)
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
        ddw__ygsiu = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            ddw__ygsiu.parent, args[1], data_typ)
        xhtn__iwof = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            yzd__mldgq = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            tgefu__injo = df_typ.table_type.type_to_blk[data_typ]
            ddpzc__vtxfx = getattr(yzd__mldgq, f'block_{tgefu__injo}')
            fnn__rps = ListInstance(c.context, c.builder, types.List(
                data_typ), ddpzc__vtxfx)
            lgvgw__osxhd = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            fnn__rps.inititem(lgvgw__osxhd, xhtn__iwof.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, xhtn__iwof.value, col_ind)
        shqhg__tkfqc = DataFramePayloadType(df_typ)
        ojpow__fxny = context.nrt.meminfo_data(builder, ddw__ygsiu.meminfo)
        kdi__hdkep = context.get_value_type(shqhg__tkfqc).as_pointer()
        ojpow__fxny = builder.bitcast(ojpow__fxny, kdi__hdkep)
        builder.store(dataframe_payload._getvalue(), ojpow__fxny)
    return signature(types.none, df, i), codegen


@unbox(SeriesType)
def unbox_series(typ, val, c):
    nllpm__kjf = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        bwtwj__kqnwx = c.context.insert_const_string(c.builder.module, 'numpy')
        lhws__zmir = c.pyapi.import_module_noblock(bwtwj__kqnwx)
        arr_obj = c.pyapi.call_method(lhws__zmir, 'ascontiguousarray', (
            nllpm__kjf,))
        c.pyapi.decref(nllpm__kjf)
        c.pyapi.decref(lhws__zmir)
    else:
        arr_obj = nllpm__kjf
    fyvc__bqi = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    bntzk__rti = c.pyapi.object_getattr_string(val, 'index')
    wkz__fwx = c.pyapi.to_native_value(typ.index, bntzk__rti).value
    vak__nogky = c.pyapi.object_getattr_string(val, 'name')
    wdgvw__ylu = c.pyapi.to_native_value(typ.name_typ, vak__nogky).value
    meqq__rdfkb = bodo.hiframes.pd_series_ext.construct_series(c.context, c
        .builder, typ, fyvc__bqi, wkz__fwx, wdgvw__ylu)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(bntzk__rti)
    c.pyapi.decref(vak__nogky)
    return NativeValue(meqq__rdfkb)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        agco__lqwg = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(agco__lqwg._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    qfkws__jguaj = c.context.insert_const_string(c.builder.module, 'pandas')
    agr__xznli = c.pyapi.import_module_noblock(qfkws__jguaj)
    kjf__ytt = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c.
        builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, kjf__ytt.data)
    c.context.nrt.incref(c.builder, typ.index, kjf__ytt.index)
    c.context.nrt.incref(c.builder, typ.name_typ, kjf__ytt.name)
    arr_obj = c.pyapi.from_native_value(typ.data, kjf__ytt.data, c.env_manager)
    bntzk__rti = c.pyapi.from_native_value(typ.index, kjf__ytt.index, c.
        env_manager)
    vak__nogky = c.pyapi.from_native_value(typ.name_typ, kjf__ytt.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(agr__xznli, 'Series', (arr_obj, bntzk__rti,
        dtype, vak__nogky))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(bntzk__rti)
    c.pyapi.decref(vak__nogky)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(agr__xznli)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    lqles__cwku = []
    for mtspr__qovcl in typ_list:
        if isinstance(mtspr__qovcl, int) and not isinstance(mtspr__qovcl, bool
            ):
            vklab__xllkp = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), mtspr__qovcl))
        else:
            pdaxc__mvmy = numba.typeof(mtspr__qovcl)
            jktaj__zxt = context.get_constant_generic(builder, pdaxc__mvmy,
                mtspr__qovcl)
            vklab__xllkp = pyapi.from_native_value(pdaxc__mvmy, jktaj__zxt,
                env_manager)
        lqles__cwku.append(vklab__xllkp)
    tkhx__pwvl = pyapi.list_pack(lqles__cwku)
    for val in lqles__cwku:
        pyapi.decref(val)
    return tkhx__pwvl


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    zptg__oja = not typ.has_runtime_cols and (not typ.is_table_format or 
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    bwsov__zwsyj = 2 if zptg__oja else 1
    ldebc__jnn = pyapi.dict_new(bwsov__zwsyj)
    uxf__unur = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    pyapi.dict_setitem_string(ldebc__jnn, 'dist', uxf__unur)
    pyapi.decref(uxf__unur)
    if zptg__oja:
        urt__pgxev = _dtype_to_type_enum_list(typ.index)
        if urt__pgxev != None:
            dcm__tjcma = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, urt__pgxev)
        else:
            dcm__tjcma = pyapi.make_none()
        yssjr__tllbd = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                tkhx__pwvl = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                tkhx__pwvl = pyapi.make_none()
            yssjr__tllbd.append(tkhx__pwvl)
        nrd__xde = pyapi.list_pack(yssjr__tllbd)
        nfykr__tbc = pyapi.list_pack([dcm__tjcma, nrd__xde])
        for val in yssjr__tllbd:
            pyapi.decref(val)
        pyapi.dict_setitem_string(ldebc__jnn, 'type_metadata', nfykr__tbc)
    pyapi.object_setattr_string(obj, '_bodo_meta', ldebc__jnn)
    pyapi.decref(ldebc__jnn)


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
    ldebc__jnn = pyapi.dict_new(2)
    uxf__unur = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    urt__pgxev = _dtype_to_type_enum_list(typ.index)
    if urt__pgxev != None:
        dcm__tjcma = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, urt__pgxev)
    else:
        dcm__tjcma = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            ddiy__htgpe = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            ddiy__htgpe = pyapi.make_none()
    else:
        ddiy__htgpe = pyapi.make_none()
    xuke__dtqg = pyapi.list_pack([dcm__tjcma, ddiy__htgpe])
    pyapi.dict_setitem_string(ldebc__jnn, 'type_metadata', xuke__dtqg)
    pyapi.decref(xuke__dtqg)
    pyapi.dict_setitem_string(ldebc__jnn, 'dist', uxf__unur)
    pyapi.object_setattr_string(obj, '_bodo_meta', ldebc__jnn)
    pyapi.decref(ldebc__jnn)
    pyapi.decref(uxf__unur)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as mlpu__xlafy:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    bnm__mwh = numba.np.numpy_support.map_layout(val)
    bnu__euhjw = not val.flags.writeable
    return types.Array(dtype, val.ndim, bnm__mwh, readonly=bnu__euhjw)


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
    scso__npt = val[i]
    if isinstance(scso__npt, str):
        return string_array_type
    elif isinstance(scso__npt, bytes):
        return binary_array_type
    elif isinstance(scso__npt, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(scso__npt, (int, np.int32, np.int64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(scso__npt))
    elif isinstance(scso__npt, (dict, Dict)) and all(isinstance(
        awpyc__jlghm, str) for awpyc__jlghm in scso__npt.keys()):
        yma__dmln = tuple(scso__npt.keys())
        nfz__eug = tuple(_get_struct_value_arr_type(v) for v in scso__npt.
            values())
        return StructArrayType(nfz__eug, yma__dmln)
    elif isinstance(scso__npt, (dict, Dict)):
        xpsu__xvaad = numba.typeof(_value_to_array(list(scso__npt.keys())))
        mypx__utvmu = numba.typeof(_value_to_array(list(scso__npt.values())))
        return MapArrayType(xpsu__xvaad, mypx__utvmu)
    elif isinstance(scso__npt, tuple):
        nfz__eug = tuple(_get_struct_value_arr_type(v) for v in scso__npt)
        return TupleArrayType(nfz__eug)
    if isinstance(scso__npt, (list, np.ndarray, pd.arrays.BooleanArray, pd.
        arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(scso__npt, list):
            scso__npt = _value_to_array(scso__npt)
        bkd__aszpm = numba.typeof(scso__npt)
        return ArrayItemArrayType(bkd__aszpm)
    if isinstance(scso__npt, datetime.date):
        return datetime_date_array_type
    if isinstance(scso__npt, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(scso__npt, decimal.Decimal):
        return DecimalArrayType(38, 18)
    raise BodoError('Unsupported object array with first value: {}'.format(
        scso__npt))


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    szkvv__yhcm = val.copy()
    szkvv__yhcm.append(None)
    vqgyn__opb = np.array(szkvv__yhcm, np.object_)
    if len(val) and isinstance(val[0], float):
        vqgyn__opb = np.array(val, np.float64)
    return vqgyn__opb


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
    gyo__gkzi = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        gyo__gkzi = to_nullable_type(gyo__gkzi)
    return gyo__gkzi
