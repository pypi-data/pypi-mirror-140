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
    ycz__fdyvt = tuple(val.columns.to_list())
    ihfe__dzsz = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        tdhbt__vfbb = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        tdhbt__vfbb = numba.typeof(val.index)
    taruu__jjtjq = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    dll__rei = len(ihfe__dzsz) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(ihfe__dzsz, tdhbt__vfbb, ycz__fdyvt, taruu__jjtjq,
        is_table_format=dll__rei)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    taruu__jjtjq = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        eqxv__yjhdx = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        eqxv__yjhdx = numba.typeof(val.index)
    return SeriesType(_infer_series_dtype(val), index=eqxv__yjhdx, name_typ
        =numba.typeof(val.name), dist=taruu__jjtjq)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    mbuim__knlvt = c.pyapi.object_getattr_string(val, 'index')
    jirgb__jyqm = c.pyapi.to_native_value(typ.index, mbuim__knlvt).value
    c.pyapi.decref(mbuim__knlvt)
    if typ.is_table_format:
        fxbg__nipka = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        fxbg__nipka.parent = val
        for inp__wae, totar__jin in typ.table_type.type_to_blk.items():
            ijul__zntw = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[totar__jin]))
            qfobk__vab, avcor__dmirn = ListInstance.allocate_ex(c.context,
                c.builder, types.List(inp__wae), ijul__zntw)
            avcor__dmirn.size = ijul__zntw
            setattr(fxbg__nipka, f'block_{totar__jin}', avcor__dmirn.value)
        xxrpu__dlvwg = c.pyapi.call_method(val, '__len__', ())
        jgh__wxyc = c.pyapi.long_as_longlong(xxrpu__dlvwg)
        c.pyapi.decref(xxrpu__dlvwg)
        fxbg__nipka.len = jgh__wxyc
        krkn__jnvam = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [fxbg__nipka._getvalue()])
    else:
        vohcn__sfmx = [c.context.get_constant_null(inp__wae) for inp__wae in
            typ.data]
        krkn__jnvam = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            vohcn__sfmx)
    ldpek__qwn = construct_dataframe(c.context, c.builder, typ, krkn__jnvam,
        jirgb__jyqm, val, None)
    return NativeValue(ldpek__qwn)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        timp__lzoyt = df._bodo_meta['type_metadata'][1]
    else:
        timp__lzoyt = [None] * len(df.columns)
    afqrc__tthv = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=timp__lzoyt[i])) for i in range(len(df.columns))]
    return tuple(afqrc__tthv)


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
    bte__wgs, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(bte__wgs) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {bte__wgs}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        pqn__fbc, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return pqn__fbc, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        pqn__fbc, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return pqn__fbc, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        eas__htl = typ_enum_list[1]
        bvg__izu = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(eas__htl, bvg__izu)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        wlqr__vucj = typ_enum_list[1]
        nqrh__rlbd = tuple(typ_enum_list[2:2 + wlqr__vucj])
        wes__nqz = typ_enum_list[2 + wlqr__vucj:]
        bfle__tjvew = []
        for i in range(wlqr__vucj):
            wes__nqz, jclqj__hxo = _dtype_from_type_enum_list_recursor(wes__nqz
                )
            bfle__tjvew.append(jclqj__hxo)
        return wes__nqz, StructType(tuple(bfle__tjvew), nqrh__rlbd)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        tacu__fxpc = typ_enum_list[1]
        wes__nqz = typ_enum_list[2:]
        return wes__nqz, tacu__fxpc
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        tacu__fxpc = typ_enum_list[1]
        wes__nqz = typ_enum_list[2:]
        return wes__nqz, numba.types.literal(tacu__fxpc)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        wes__nqz, bzy__dhrp = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        wes__nqz, xob__ueh = _dtype_from_type_enum_list_recursor(wes__nqz)
        wes__nqz, efsu__gzvd = _dtype_from_type_enum_list_recursor(wes__nqz)
        wes__nqz, vwat__rpn = _dtype_from_type_enum_list_recursor(wes__nqz)
        wes__nqz, iggt__xegno = _dtype_from_type_enum_list_recursor(wes__nqz)
        return wes__nqz, PDCategoricalDtype(bzy__dhrp, xob__ueh, efsu__gzvd,
            vwat__rpn, iggt__xegno)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return wes__nqz, DatetimeIndexType(mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        wes__nqz, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(wes__nqz)
        wes__nqz, vwat__rpn = _dtype_from_type_enum_list_recursor(wes__nqz)
        return wes__nqz, NumericIndexType(dtype, mup__ozjk, vwat__rpn)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        wes__nqz, jmt__mvc = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(wes__nqz)
        return wes__nqz, PeriodIndexType(jmt__mvc, mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        wes__nqz, vwat__rpn = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(wes__nqz)
        return wes__nqz, CategoricalIndexType(vwat__rpn, mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return wes__nqz, RangeIndexType(mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return wes__nqz, StringIndexType(mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return wes__nqz, BinaryIndexType(mup__ozjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        wes__nqz, mup__ozjk = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return wes__nqz, TimedeltaIndexType(mup__ozjk)
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
        fhvb__kvl = get_overload_const_int(typ)
        if numba.types.maybe_literal(fhvb__kvl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, fhvb__kvl]
    elif is_overload_constant_str(typ):
        fhvb__kvl = get_overload_const_str(typ)
        if numba.types.maybe_literal(fhvb__kvl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, fhvb__kvl]
    elif is_overload_constant_bool(typ):
        fhvb__kvl = get_overload_const_bool(typ)
        if numba.types.maybe_literal(fhvb__kvl) == typ:
            return [SeriesDtypeEnum.LiteralType.value, fhvb__kvl]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        sny__qokcv = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for whx__zshin in typ.names:
            sny__qokcv.append(whx__zshin)
        for ffu__nhc in typ.data:
            sny__qokcv += _dtype_to_type_enum_list_recursor(ffu__nhc)
        return sny__qokcv
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        qva__nhmum = _dtype_to_type_enum_list_recursor(typ.categories)
        tlnr__zodwg = _dtype_to_type_enum_list_recursor(typ.elem_type)
        hppz__ctix = _dtype_to_type_enum_list_recursor(typ.ordered)
        pgl__ksml = _dtype_to_type_enum_list_recursor(typ.data)
        vqkh__sesyz = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + qva__nhmum + tlnr__zodwg + hppz__ctix + pgl__ksml + vqkh__sesyz
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                zjx__dgvhn = types.float64
                ypyg__lofx = types.Array(zjx__dgvhn, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                zjx__dgvhn = types.int64
                ypyg__lofx = types.Array(zjx__dgvhn, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                zjx__dgvhn = types.uint64
                ypyg__lofx = types.Array(zjx__dgvhn, 1, 'C')
            elif typ.dtype == types.bool_:
                zjx__dgvhn = typ.dtype
                ypyg__lofx = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(zjx__dgvhn
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(ypyg__lofx)
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
                gvh__belne = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(gvh__belne)
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
    pnq__nqey = cgutils.is_not_null(builder, parent_obj)
    jozk__ldk = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(pnq__nqey):
        xftmb__dlft = pyapi.object_getattr_string(parent_obj, 'columns')
        xxrpu__dlvwg = pyapi.call_method(xftmb__dlft, '__len__', ())
        builder.store(pyapi.long_as_longlong(xxrpu__dlvwg), jozk__ldk)
        pyapi.decref(xxrpu__dlvwg)
        pyapi.decref(xftmb__dlft)
    use_parent_obj = builder.and_(pnq__nqey, builder.icmp_unsigned('==',
        builder.load(jozk__ldk), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        cddy__ayt = df_typ.runtime_colname_typ
        context.nrt.incref(builder, cddy__ayt, dataframe_payload.columns)
        return pyapi.from_native_value(cddy__ayt, dataframe_payload.columns,
            c.env_manager)
    if all(isinstance(c, int) for c in df_typ.columns):
        ixy__pqfqu = np.array(df_typ.columns, 'int64')
    elif all(isinstance(c, str) for c in df_typ.columns):
        ixy__pqfqu = pd.array(df_typ.columns, 'string')
    else:
        ixy__pqfqu = df_typ.columns
    pczyy__hvcmb = numba.typeof(ixy__pqfqu)
    gnvd__coqyh = context.get_constant_generic(builder, pczyy__hvcmb,
        ixy__pqfqu)
    trwm__iwjc = pyapi.from_native_value(pczyy__hvcmb, gnvd__coqyh, c.
        env_manager)
    return trwm__iwjc


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (use_parent, otherwise):
        with use_parent:
            pyapi.incref(obj)
            xrzo__tpn = context.insert_const_string(c.builder.module, 'numpy')
            ihx__obd = pyapi.import_module_noblock(xrzo__tpn)
            if df_typ.has_runtime_cols:
                ebg__bpo = 0
            else:
                ebg__bpo = len(df_typ.columns)
            qjkuw__ztzj = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), ebg__bpo))
            mdmw__qhxl = pyapi.call_method(ihx__obd, 'arange', (qjkuw__ztzj,))
            pyapi.object_setattr_string(obj, 'columns', mdmw__qhxl)
            pyapi.decref(ihx__obd)
            pyapi.decref(mdmw__qhxl)
            pyapi.decref(qjkuw__ztzj)
        with otherwise:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            aebn__hcy = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            xrzo__tpn = context.insert_const_string(c.builder.module, 'pandas')
            ihx__obd = pyapi.import_module_noblock(xrzo__tpn)
            df_obj = pyapi.call_method(ihx__obd, 'DataFrame', (pyapi.
                borrow_none(), aebn__hcy))
            pyapi.decref(ihx__obd)
            pyapi.decref(aebn__hcy)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    kfd__wfrsi = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = kfd__wfrsi.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        itz__tczt = typ.table_type
        fxbg__nipka = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, itz__tczt, fxbg__nipka)
        zqjz__vov = box_table(itz__tczt, fxbg__nipka, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (then, orelse):
            with then:
                vfcii__rej = pyapi.object_getattr_string(zqjz__vov, 'arrays')
                rsorb__oiml = c.pyapi.make_none()
                if n_cols is None:
                    xxrpu__dlvwg = pyapi.call_method(vfcii__rej, '__len__', ())
                    ijul__zntw = pyapi.long_as_longlong(xxrpu__dlvwg)
                    pyapi.decref(xxrpu__dlvwg)
                else:
                    ijul__zntw = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, ijul__zntw) as loop:
                    i = loop.index
                    bkaw__faw = pyapi.list_getitem(vfcii__rej, i)
                    olck__zdvjf = c.builder.icmp_unsigned('!=', bkaw__faw,
                        rsorb__oiml)
                    with builder.if_then(olck__zdvjf):
                        udei__jyyjk = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, udei__jyyjk, bkaw__faw)
                        pyapi.decref(udei__jyyjk)
                pyapi.decref(vfcii__rej)
                pyapi.decref(rsorb__oiml)
            with orelse:
                df_obj = builder.load(res)
                aebn__hcy = pyapi.object_getattr_string(df_obj, 'index')
                nxosk__ori = c.pyapi.call_method(zqjz__vov, 'to_pandas', (
                    aebn__hcy,))
                builder.store(nxosk__ori, res)
                pyapi.decref(df_obj)
                pyapi.decref(aebn__hcy)
        pyapi.decref(zqjz__vov)
    else:
        bgicy__oppj = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        xzj__qqtru = typ.data
        for i, ovrce__oaj, khi__mdyrt in zip(range(n_cols), bgicy__oppj,
            xzj__qqtru):
            xybfd__dnpn = cgutils.alloca_once_value(builder, ovrce__oaj)
            jeng__jrkx = cgutils.alloca_once_value(builder, context.
                get_constant_null(khi__mdyrt))
            olck__zdvjf = builder.not_(is_ll_eq(builder, xybfd__dnpn,
                jeng__jrkx))
            kssr__zek = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, olck__zdvjf))
            with builder.if_then(kssr__zek):
                udei__jyyjk = pyapi.long_from_longlong(context.get_constant
                    (types.int64, i))
                context.nrt.incref(builder, khi__mdyrt, ovrce__oaj)
                arr_obj = pyapi.from_native_value(khi__mdyrt, ovrce__oaj, c
                    .env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, udei__jyyjk, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(udei__jyyjk)
    df_obj = builder.load(res)
    trwm__iwjc = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', trwm__iwjc)
    pyapi.decref(trwm__iwjc)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    rsorb__oiml = pyapi.borrow_none()
    mfbs__pbym = pyapi.unserialize(pyapi.serialize_object(slice))
    rpp__ldpik = pyapi.call_function_objargs(mfbs__pbym, [rsorb__oiml])
    knlp__ksey = pyapi.long_from_longlong(col_ind)
    smjxq__jwz = pyapi.tuple_pack([rpp__ldpik, knlp__ksey])
    zri__nzykt = pyapi.object_getattr_string(df_obj, 'iloc')
    kbf__tio = pyapi.object_getitem(zri__nzykt, smjxq__jwz)
    kcok__wfu = pyapi.object_getattr_string(kbf__tio, 'values')
    if isinstance(data_typ, types.Array):
        fayow__xulmq = context.insert_const_string(builder.module, 'numpy')
        vhnrm__bsp = pyapi.import_module_noblock(fayow__xulmq)
        arr_obj = pyapi.call_method(vhnrm__bsp, 'ascontiguousarray', (
            kcok__wfu,))
        pyapi.decref(kcok__wfu)
        pyapi.decref(vhnrm__bsp)
    else:
        arr_obj = kcok__wfu
    pyapi.decref(mfbs__pbym)
    pyapi.decref(rpp__ldpik)
    pyapi.decref(knlp__ksey)
    pyapi.decref(smjxq__jwz)
    pyapi.decref(zri__nzykt)
    pyapi.decref(kbf__tio)
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
        kfd__wfrsi = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            kfd__wfrsi.parent, args[1], data_typ)
        lpx__bonpo = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            fxbg__nipka = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            totar__jin = df_typ.table_type.type_to_blk[data_typ]
            tuugy__aid = getattr(fxbg__nipka, f'block_{totar__jin}')
            uav__dyric = ListInstance(c.context, c.builder, types.List(
                data_typ), tuugy__aid)
            mno__iabh = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[col_ind])
            uav__dyric.inititem(mno__iabh, lpx__bonpo.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, lpx__bonpo.value, col_ind)
        xdavr__vtoox = DataFramePayloadType(df_typ)
        gen__hbn = context.nrt.meminfo_data(builder, kfd__wfrsi.meminfo)
        ihgm__ywtr = context.get_value_type(xdavr__vtoox).as_pointer()
        gen__hbn = builder.bitcast(gen__hbn, ihgm__ywtr)
        builder.store(dataframe_payload._getvalue(), gen__hbn)
    return signature(types.none, df, i), codegen


@unbox(SeriesType)
def unbox_series(typ, val, c):
    kcok__wfu = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        fayow__xulmq = c.context.insert_const_string(c.builder.module, 'numpy')
        vhnrm__bsp = c.pyapi.import_module_noblock(fayow__xulmq)
        arr_obj = c.pyapi.call_method(vhnrm__bsp, 'ascontiguousarray', (
            kcok__wfu,))
        c.pyapi.decref(kcok__wfu)
        c.pyapi.decref(vhnrm__bsp)
    else:
        arr_obj = kcok__wfu
    nkvpa__wangk = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    aebn__hcy = c.pyapi.object_getattr_string(val, 'index')
    jirgb__jyqm = c.pyapi.to_native_value(typ.index, aebn__hcy).value
    gckw__ybd = c.pyapi.object_getattr_string(val, 'name')
    oqd__xgiuz = c.pyapi.to_native_value(typ.name_typ, gckw__ybd).value
    aezt__fggkf = bodo.hiframes.pd_series_ext.construct_series(c.context, c
        .builder, typ, nkvpa__wangk, jirgb__jyqm, oqd__xgiuz)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(aebn__hcy)
    c.pyapi.decref(gckw__ybd)
    return NativeValue(aezt__fggkf)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        gze__wef = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(gze__wef._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    xrzo__tpn = c.context.insert_const_string(c.builder.module, 'pandas')
    zcm__lgb = c.pyapi.import_module_noblock(xrzo__tpn)
    qizau__tsm = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, qizau__tsm.data)
    c.context.nrt.incref(c.builder, typ.index, qizau__tsm.index)
    c.context.nrt.incref(c.builder, typ.name_typ, qizau__tsm.name)
    arr_obj = c.pyapi.from_native_value(typ.data, qizau__tsm.data, c.
        env_manager)
    aebn__hcy = c.pyapi.from_native_value(typ.index, qizau__tsm.index, c.
        env_manager)
    gckw__ybd = c.pyapi.from_native_value(typ.name_typ, qizau__tsm.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(zcm__lgb, 'Series', (arr_obj, aebn__hcy,
        dtype, gckw__ybd))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(aebn__hcy)
    c.pyapi.decref(gckw__ybd)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(zcm__lgb)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    srdy__rew = []
    for tmqf__uhcak in typ_list:
        if isinstance(tmqf__uhcak, int) and not isinstance(tmqf__uhcak, bool):
            hczo__qdkt = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), tmqf__uhcak))
        else:
            bascx__uwa = numba.typeof(tmqf__uhcak)
            xjm__cucgg = context.get_constant_generic(builder, bascx__uwa,
                tmqf__uhcak)
            hczo__qdkt = pyapi.from_native_value(bascx__uwa, xjm__cucgg,
                env_manager)
        srdy__rew.append(hczo__qdkt)
    riwvg__hfnko = pyapi.list_pack(srdy__rew)
    for val in srdy__rew:
        pyapi.decref(val)
    return riwvg__hfnko


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    rdxih__sumrp = not typ.has_runtime_cols and (not typ.is_table_format or
        len(typ.columns) < TABLE_FORMAT_THRESHOLD)
    qyu__ecmes = 2 if rdxih__sumrp else 1
    leb__wdus = pyapi.dict_new(qyu__ecmes)
    immf__xyilw = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(leb__wdus, 'dist', immf__xyilw)
    pyapi.decref(immf__xyilw)
    if rdxih__sumrp:
        amqg__aajq = _dtype_to_type_enum_list(typ.index)
        if amqg__aajq != None:
            ywqx__drz = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, amqg__aajq)
        else:
            ywqx__drz = pyapi.make_none()
        wded__zhqwf = []
        for dtype in typ.data:
            typ_list = _dtype_to_type_enum_list(dtype)
            if typ_list != None:
                riwvg__hfnko = type_enum_list_to_py_list_obj(pyapi, context,
                    builder, c.env_manager, typ_list)
            else:
                riwvg__hfnko = pyapi.make_none()
            wded__zhqwf.append(riwvg__hfnko)
        gyrgz__cfdkw = pyapi.list_pack(wded__zhqwf)
        qmgxp__ndpm = pyapi.list_pack([ywqx__drz, gyrgz__cfdkw])
        for val in wded__zhqwf:
            pyapi.decref(val)
        pyapi.dict_setitem_string(leb__wdus, 'type_metadata', qmgxp__ndpm)
    pyapi.object_setattr_string(obj, '_bodo_meta', leb__wdus)
    pyapi.decref(leb__wdus)


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
    leb__wdus = pyapi.dict_new(2)
    immf__xyilw = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    amqg__aajq = _dtype_to_type_enum_list(typ.index)
    if amqg__aajq != None:
        ywqx__drz = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, amqg__aajq)
    else:
        ywqx__drz = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            zvzt__kik = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            zvzt__kik = pyapi.make_none()
    else:
        zvzt__kik = pyapi.make_none()
    kwqhb__noh = pyapi.list_pack([ywqx__drz, zvzt__kik])
    pyapi.dict_setitem_string(leb__wdus, 'type_metadata', kwqhb__noh)
    pyapi.decref(kwqhb__noh)
    pyapi.dict_setitem_string(leb__wdus, 'dist', immf__xyilw)
    pyapi.object_setattr_string(obj, '_bodo_meta', leb__wdus)
    pyapi.decref(leb__wdus)
    pyapi.decref(immf__xyilw)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as dzmcc__doocw:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    pzt__frv = numba.np.numpy_support.map_layout(val)
    iqwz__dhde = not val.flags.writeable
    return types.Array(dtype, val.ndim, pzt__frv, readonly=iqwz__dhde)


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
    lhf__tdoyw = val[i]
    if isinstance(lhf__tdoyw, str):
        return string_array_type
    elif isinstance(lhf__tdoyw, bytes):
        return binary_array_type
    elif isinstance(lhf__tdoyw, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(lhf__tdoyw, (int, np.int32, np.int64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(lhf__tdoyw))
    elif isinstance(lhf__tdoyw, (dict, Dict)) and all(isinstance(brk__fww,
        str) for brk__fww in lhf__tdoyw.keys()):
        nqrh__rlbd = tuple(lhf__tdoyw.keys())
        ejdx__msuhn = tuple(_get_struct_value_arr_type(v) for v in
            lhf__tdoyw.values())
        return StructArrayType(ejdx__msuhn, nqrh__rlbd)
    elif isinstance(lhf__tdoyw, (dict, Dict)):
        ijbko__wqn = numba.typeof(_value_to_array(list(lhf__tdoyw.keys())))
        dmjwv__hdz = numba.typeof(_value_to_array(list(lhf__tdoyw.values())))
        return MapArrayType(ijbko__wqn, dmjwv__hdz)
    elif isinstance(lhf__tdoyw, tuple):
        ejdx__msuhn = tuple(_get_struct_value_arr_type(v) for v in lhf__tdoyw)
        return TupleArrayType(ejdx__msuhn)
    if isinstance(lhf__tdoyw, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(lhf__tdoyw, list):
            lhf__tdoyw = _value_to_array(lhf__tdoyw)
        vnsf__egtw = numba.typeof(lhf__tdoyw)
        return ArrayItemArrayType(vnsf__egtw)
    if isinstance(lhf__tdoyw, datetime.date):
        return datetime_date_array_type
    if isinstance(lhf__tdoyw, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(lhf__tdoyw, decimal.Decimal):
        return DecimalArrayType(38, 18)
    raise BodoError('Unsupported object array with first value: {}'.format(
        lhf__tdoyw))


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    kte__van = val.copy()
    kte__van.append(None)
    ovrce__oaj = np.array(kte__van, np.object_)
    if len(val) and isinstance(val[0], float):
        ovrce__oaj = np.array(val, np.float64)
    return ovrce__oaj


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
    khi__mdyrt = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        khi__mdyrt = to_nullable_type(khi__mdyrt)
    return khi__mdyrt
