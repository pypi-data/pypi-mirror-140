"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import bcast_scalar
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence, string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import gen_const_tup, get_const_func_output_type, get_const_tup_vals
from bodo.utils.typing import BodoError, BodoWarning, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_tuple_like_type, raise_bodo_error, to_nullable_type
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            cym__bjj = f'{len(self.data)} columns of types {set(self.data)}'
            qhf__phkwi = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({cym__bjj}, {self.index}, {qhf__phkwi}, {self.dist}, {self.is_table_format})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            iim__bot = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(qau__wohqy.unify(typingctx, nrt__brdb) if 
                qau__wohqy != nrt__brdb else qau__wohqy for qau__wohqy,
                nrt__brdb in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if iim__bot is not None and None not in data:
                return DataFrameType(data, iim__bot, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(qau__wohqy.is_precise() for qau__wohqy in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        dxclh__oefc = self.columns.index(col_name)
        zch__mbdkv = tuple(list(self.data[:dxclh__oefc]) + [new_type] +
            list(self.data[dxclh__oefc + 1:]))
        return DataFrameType(zch__mbdkv, self.index, self.columns, self.
            dist, self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        cclp__vkobc = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            cclp__vkobc.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, cclp__vkobc)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        cclp__vkobc = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, cclp__vkobc)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        mld__lvfi = 'n',
        svev__jvm = {'n': 5}
        jwum__zga, sazxr__hmoc = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, mld__lvfi, svev__jvm)
        gofw__zkis = sazxr__hmoc[0]
        if not is_overload_int(gofw__zkis):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        xtzzc__vhivs = df.copy(is_table_format=False)
        return xtzzc__vhivs(*sazxr__hmoc).replace(pysig=jwum__zga)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        fhpsb__fybbi = (df,) + args
        mld__lvfi = 'df', 'method', 'min_periods'
        svev__jvm = {'method': 'pearson', 'min_periods': 1}
        pexpd__tnzk = 'method',
        jwum__zga, sazxr__hmoc = bodo.utils.typing.fold_typing_args(func_name,
            fhpsb__fybbi, kws, mld__lvfi, svev__jvm, pexpd__tnzk)
        sbox__gcgyd = sazxr__hmoc[2]
        if not is_overload_int(sbox__gcgyd):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        klujn__dgxke = []
        hjui__iax = []
        for gtax__kis, imzjm__evwlg in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(imzjm__evwlg.dtype):
                klujn__dgxke.append(gtax__kis)
                hjui__iax.append(types.Array(types.float64, 1, 'A'))
        if len(klujn__dgxke) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        hjui__iax = tuple(hjui__iax)
        klujn__dgxke = tuple(klujn__dgxke)
        index_typ = bodo.utils.typing.type_col_to_index(klujn__dgxke)
        xtzzc__vhivs = DataFrameType(hjui__iax, index_typ, klujn__dgxke)
        return xtzzc__vhivs(*sazxr__hmoc).replace(pysig=jwum__zga)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        rrzu__miqcg = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        bdd__gtq = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        yhvr__jbjao = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        nvtms__dig = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        wygzq__ziuma = dict(raw=bdd__gtq, result_type=yhvr__jbjao)
        jcvs__hvt = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', wygzq__ziuma, jcvs__hvt,
            package_name='pandas', module_name='DataFrame')
        vfau__ekr = True
        if types.unliteral(rrzu__miqcg) == types.unicode_type:
            if not is_overload_constant_str(rrzu__miqcg):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            vfau__ekr = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        ibca__ocv = get_overload_const_int(axis)
        if vfau__ekr and ibca__ocv != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif ibca__ocv not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        xrovc__zka = []
        for arr_typ in df.data:
            ash__kpdc = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            aoxk__fvr = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(ash__kpdc), types.int64), {}).return_type
            xrovc__zka.append(aoxk__fvr)
        grh__rmemb = types.none
        xtm__orgtb = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(gtax__kis) for gtax__kis in df.columns)), None)
        ktyov__ghji = types.BaseTuple.from_types(xrovc__zka)
        oycfz__dsncp = df.index.dtype
        if oycfz__dsncp == types.NPDatetime('ns'):
            oycfz__dsncp = bodo.pd_timestamp_type
        if oycfz__dsncp == types.NPTimedelta('ns'):
            oycfz__dsncp = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(ktyov__ghji):
            fcip__vqz = HeterogeneousSeriesType(ktyov__ghji, xtm__orgtb,
                oycfz__dsncp)
        else:
            fcip__vqz = SeriesType(ktyov__ghji.dtype, ktyov__ghji,
                xtm__orgtb, oycfz__dsncp)
        tpf__uxpm = fcip__vqz,
        if nvtms__dig is not None:
            tpf__uxpm += tuple(nvtms__dig.types)
        try:
            if not vfau__ekr:
                tseja__agq = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(rrzu__miqcg), self.context,
                    'DataFrame.apply', axis if ibca__ocv == 1 else None)
            else:
                tseja__agq = get_const_func_output_type(rrzu__miqcg,
                    tpf__uxpm, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as eycs__kds:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', eycs__kds))
        if vfau__ekr:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(tseja__agq, (SeriesType, HeterogeneousSeriesType)
                ) and tseja__agq.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(tseja__agq, HeterogeneousSeriesType):
                kue__rlpbd, mlkc__muaf = tseja__agq.const_info
                nnxv__ndqu = tuple(dtype_to_array_type(pgj__bfhr) for
                    pgj__bfhr in tseja__agq.data.types)
                xqzh__zrtz = DataFrameType(nnxv__ndqu, df.index, mlkc__muaf)
            elif isinstance(tseja__agq, SeriesType):
                cdce__pxx, mlkc__muaf = tseja__agq.const_info
                nnxv__ndqu = tuple(dtype_to_array_type(tseja__agq.dtype) for
                    kue__rlpbd in range(cdce__pxx))
                xqzh__zrtz = DataFrameType(nnxv__ndqu, df.index, mlkc__muaf)
            else:
                mtir__qfzc = get_udf_out_arr_type(tseja__agq)
                xqzh__zrtz = SeriesType(mtir__qfzc.dtype, mtir__qfzc, df.
                    index, None)
        else:
            xqzh__zrtz = tseja__agq
        ljau__rvo = ', '.join("{} = ''".format(qau__wohqy) for qau__wohqy in
            kws.keys())
        ciu__fzm = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {ljau__rvo}):
"""
        ciu__fzm += '    pass\n'
        xpv__jqx = {}
        exec(ciu__fzm, {}, xpv__jqx)
        djc__iiis = xpv__jqx['apply_stub']
        jwum__zga = numba.core.utils.pysignature(djc__iiis)
        gmzk__jort = (rrzu__miqcg, axis, bdd__gtq, yhvr__jbjao, nvtms__dig
            ) + tuple(kws.values())
        return signature(xqzh__zrtz, *gmzk__jort).replace(pysig=jwum__zga)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        mld__lvfi = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        svev__jvm = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        pexpd__tnzk = ('subplots', 'sharex', 'sharey', 'layout',
            'use_index', 'grid', 'style', 'logx', 'logy', 'loglog', 'xlim',
            'ylim', 'rot', 'colormap', 'table', 'yerr', 'xerr',
            'sort_columns', 'secondary_y', 'colorbar', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        jwum__zga, sazxr__hmoc = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, mld__lvfi, svev__jvm, pexpd__tnzk)
        ueihb__ldijw = sazxr__hmoc[2]
        if not is_overload_constant_str(ueihb__ldijw):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        inndv__ejwwn = sazxr__hmoc[0]
        if not is_overload_none(inndv__ejwwn) and not (is_overload_int(
            inndv__ejwwn) or is_overload_constant_str(inndv__ejwwn)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(inndv__ejwwn):
            pysqc__otvd = get_overload_const_str(inndv__ejwwn)
            if pysqc__otvd not in df.columns:
                raise BodoError(f'{func_name}: {pysqc__otvd} column not found.'
                    )
        elif is_overload_int(inndv__ejwwn):
            zogw__ltrm = get_overload_const_int(inndv__ejwwn)
            if zogw__ltrm > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {zogw__ltrm} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            inndv__ejwwn = df.columns[inndv__ejwwn]
        ezsp__wbo = sazxr__hmoc[1]
        if not is_overload_none(ezsp__wbo) and not (is_overload_int(
            ezsp__wbo) or is_overload_constant_str(ezsp__wbo)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ezsp__wbo):
            bvjf__vtby = get_overload_const_str(ezsp__wbo)
            if bvjf__vtby not in df.columns:
                raise BodoError(f'{func_name}: {bvjf__vtby} column not found.')
        elif is_overload_int(ezsp__wbo):
            cwp__klxqw = get_overload_const_int(ezsp__wbo)
            if cwp__klxqw > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {cwp__klxqw} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ezsp__wbo = df.columns[ezsp__wbo]
        gtelg__twxxb = sazxr__hmoc[3]
        if not is_overload_none(gtelg__twxxb) and not is_tuple_like_type(
            gtelg__twxxb):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        eghh__rriu = sazxr__hmoc[10]
        if not is_overload_none(eghh__rriu) and not is_overload_constant_str(
            eghh__rriu):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        lumam__edef = sazxr__hmoc[12]
        if not is_overload_bool(lumam__edef):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        lnnlt__jpd = sazxr__hmoc[17]
        if not is_overload_none(lnnlt__jpd) and not is_tuple_like_type(
            lnnlt__jpd):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        eflw__dskh = sazxr__hmoc[18]
        if not is_overload_none(eflw__dskh) and not is_tuple_like_type(
            eflw__dskh):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        kcl__kzqmw = sazxr__hmoc[22]
        if not is_overload_none(kcl__kzqmw) and not is_overload_int(kcl__kzqmw
            ):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        xss__dym = sazxr__hmoc[29]
        if not is_overload_none(xss__dym) and not is_overload_constant_str(
            xss__dym):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        lgxsk__ximf = sazxr__hmoc[30]
        if not is_overload_none(lgxsk__ximf) and not is_overload_constant_str(
            lgxsk__ximf):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        qpojg__fad = types.List(types.mpl_line_2d_type)
        ueihb__ldijw = get_overload_const_str(ueihb__ldijw)
        if ueihb__ldijw == 'scatter':
            if is_overload_none(inndv__ejwwn) and is_overload_none(ezsp__wbo):
                raise BodoError(
                    f'{func_name}: {ueihb__ldijw} requires an x and y column.')
            elif is_overload_none(inndv__ejwwn):
                raise BodoError(
                    f'{func_name}: {ueihb__ldijw} x column is missing.')
            elif is_overload_none(ezsp__wbo):
                raise BodoError(
                    f'{func_name}: {ueihb__ldijw} y column is missing.')
            qpojg__fad = types.mpl_path_collection_type
        elif ueihb__ldijw != 'line':
            raise BodoError(
                f'{func_name}: {ueihb__ldijw} plot is not supported.')
        return signature(qpojg__fad, *sazxr__hmoc).replace(pysig=jwum__zga)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            gkei__hbw = df.columns.index(attr)
            arr_typ = df.data[gkei__hbw]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            gegy__wccj = []
            zch__mbdkv = []
            cewo__aai = False
            for i, zhkg__cti in enumerate(df.columns):
                if zhkg__cti[0] != attr:
                    continue
                cewo__aai = True
                gegy__wccj.append(zhkg__cti[1] if len(zhkg__cti) == 2 else
                    zhkg__cti[1:])
                zch__mbdkv.append(df.data[i])
            if cewo__aai:
                return DataFrameType(tuple(zch__mbdkv), df.index, tuple(
                    gegy__wccj))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        uqz__seusy = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(uqz__seusy)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        qwsb__cona = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], qwsb__cona)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    fgm__cfxco = builder.module
    gwjrn__eheb = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ujwg__ucp = cgutils.get_or_insert_function(fgm__cfxco, gwjrn__eheb,
        name='.dtor.df.{}'.format(df_type))
    if not ujwg__ucp.is_declaration:
        return ujwg__ucp
    ujwg__ucp.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ujwg__ucp.append_basic_block())
    wsk__hpzq = ujwg__ucp.args[0]
    zguf__wcsrl = context.get_value_type(payload_type).as_pointer()
    kmq__ikrd = builder.bitcast(wsk__hpzq, zguf__wcsrl)
    payload = context.make_helper(builder, payload_type, ref=kmq__ikrd)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        juo__diwx = context.get_python_api(builder)
        jyj__cts = juo__diwx.gil_ensure()
        juo__diwx.decref(payload.parent)
        juo__diwx.gil_release(jyj__cts)
    builder.ret_void()
    return ujwg__ucp


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    wmyjs__uniw = cgutils.create_struct_proxy(payload_type)(context, builder)
    wmyjs__uniw.data = data_tup
    wmyjs__uniw.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        wmyjs__uniw.columns = colnames
    xsn__wuemg = context.get_value_type(payload_type)
    vptlr__yaiz = context.get_abi_sizeof(xsn__wuemg)
    vbu__nnnu = define_df_dtor(context, builder, df_type, payload_type)
    rgry__fvbex = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, vptlr__yaiz), vbu__nnnu)
    qjz__lefdq = context.nrt.meminfo_data(builder, rgry__fvbex)
    ujmz__epigs = builder.bitcast(qjz__lefdq, xsn__wuemg.as_pointer())
    nidu__iqd = cgutils.create_struct_proxy(df_type)(context, builder)
    nidu__iqd.meminfo = rgry__fvbex
    if parent is None:
        nidu__iqd.parent = cgutils.get_null_value(nidu__iqd.parent.type)
    else:
        nidu__iqd.parent = parent
        wmyjs__uniw.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            juo__diwx = context.get_python_api(builder)
            jyj__cts = juo__diwx.gil_ensure()
            juo__diwx.incref(parent)
            juo__diwx.gil_release(jyj__cts)
    builder.store(wmyjs__uniw._getvalue(), ujmz__epigs)
    return nidu__iqd._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        jpqiu__yhtz = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        jpqiu__yhtz = [pgj__bfhr for pgj__bfhr in data_typ.dtype.arr_types]
    qswii__mmjs = DataFrameType(tuple(jpqiu__yhtz + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        szs__hbxi = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return szs__hbxi
    sig = signature(qswii__mmjs, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ=None):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    cdce__pxx = len(data_tup_typ.types)
    if cdce__pxx == 0:
        yzx__jcp = ()
    elif isinstance(col_names_typ, types.TypeRef):
        yzx__jcp = col_names_typ.instance_type.columns
    else:
        yzx__jcp = get_const_tup_vals(col_names_typ)
    if cdce__pxx == 1 and isinstance(data_tup_typ.types[0], TableType):
        cdce__pxx = len(data_tup_typ.types[0].arr_types)
    assert len(yzx__jcp
        ) == cdce__pxx, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    rwm__kpm = data_tup_typ.types
    if cdce__pxx != 0 and isinstance(data_tup_typ.types[0], TableType):
        rwm__kpm = data_tup_typ.types[0].arr_types
        is_table_format = True
    qswii__mmjs = DataFrameType(rwm__kpm, index_typ, yzx__jcp,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            xths__zee = cgutils.create_struct_proxy(qswii__mmjs.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = xths__zee.parent
        szs__hbxi = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return szs__hbxi
    sig = signature(qswii__mmjs, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        nidu__iqd = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, nidu__iqd.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        wmyjs__uniw = get_dataframe_payload(context, builder, df_typ, args[0])
        uxs__epbp = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[uxs__epbp]
        if df_typ.is_table_format:
            xths__zee = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(wmyjs__uniw.data, 0))
            fry__zngi = df_typ.table_type.type_to_blk[arr_typ]
            wqxi__rstfv = getattr(xths__zee, f'block_{fry__zngi}')
            quqd__xpniu = ListInstance(context, builder, types.List(arr_typ
                ), wqxi__rstfv)
            cimbd__bxmkq = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[uxs__epbp])
            qwsb__cona = quqd__xpniu.getitem(cimbd__bxmkq)
        else:
            qwsb__cona = builder.extract_value(wmyjs__uniw.data, uxs__epbp)
        vem__lmmoc = cgutils.alloca_once_value(builder, qwsb__cona)
        hcj__cxvj = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, vem__lmmoc, hcj__cxvj)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    rgry__fvbex = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, rgry__fvbex)
    zguf__wcsrl = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, zguf__wcsrl)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    qswii__mmjs = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        qswii__mmjs = types.Tuple([TableType(df_typ.data)])
    sig = signature(qswii__mmjs, df_typ)

    def codegen(context, builder, signature, args):
        wmyjs__uniw = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            wmyjs__uniw.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, 'get_dataframe_index')

    def codegen(context, builder, signature, args):
        wmyjs__uniw = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index,
            wmyjs__uniw.index)
    qswii__mmjs = df_typ.index
    sig = signature(qswii__mmjs, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        xtzzc__vhivs = df.data[i]
        return xtzzc__vhivs(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        wmyjs__uniw = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(wmyjs__uniw.data, 0))
    return df_typ.table_type(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    ktyov__ghji = self.typemap[data_tup.name]
    if any(is_tuple_like_type(pgj__bfhr) for pgj__bfhr in ktyov__ghji.types):
        return None
    if equiv_set.has_shape(data_tup):
        ddw__xhor = equiv_set.get_shape(data_tup)
        if len(ddw__xhor) > 1:
            equiv_set.insert_equiv(*ddw__xhor)
        if len(ddw__xhor) > 0:
            xtm__orgtb = self.typemap[index.name]
            if not isinstance(xtm__orgtb, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(ddw__xhor[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(ddw__xhor[0], len(
                ddw__xhor)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wgmwf__foqsf = args[0]
    hqgbv__ahd = self.typemap[wgmwf__foqsf.name].data
    if any(is_tuple_like_type(pgj__bfhr) for pgj__bfhr in hqgbv__ahd):
        return None
    if equiv_set.has_shape(wgmwf__foqsf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wgmwf__foqsf)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    wgmwf__foqsf = args[0]
    xtm__orgtb = self.typemap[wgmwf__foqsf.name].index
    if isinstance(xtm__orgtb, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(wgmwf__foqsf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wgmwf__foqsf)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    wgmwf__foqsf = args[0]
    if equiv_set.has_shape(wgmwf__foqsf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wgmwf__foqsf), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    uxs__epbp = get_overload_const_int(c_ind_typ)
    if df_typ.data[uxs__epbp] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        exhdh__gluq, kue__rlpbd, qbo__kur = args
        wmyjs__uniw = get_dataframe_payload(context, builder, df_typ,
            exhdh__gluq)
        if df_typ.is_table_format:
            xths__zee = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(wmyjs__uniw.data, 0))
            fry__zngi = df_typ.table_type.type_to_blk[arr_typ]
            wqxi__rstfv = getattr(xths__zee, f'block_{fry__zngi}')
            quqd__xpniu = ListInstance(context, builder, types.List(arr_typ
                ), wqxi__rstfv)
            cimbd__bxmkq = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[uxs__epbp])
            quqd__xpniu.setitem(cimbd__bxmkq, qbo__kur, True)
        else:
            qwsb__cona = builder.extract_value(wmyjs__uniw.data, uxs__epbp)
            context.nrt.decref(builder, df_typ.data[uxs__epbp], qwsb__cona)
            wmyjs__uniw.data = builder.insert_value(wmyjs__uniw.data,
                qbo__kur, uxs__epbp)
            context.nrt.incref(builder, arr_typ, qbo__kur)
        nidu__iqd = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=exhdh__gluq)
        payload_type = DataFramePayloadType(df_typ)
        kmq__ikrd = context.nrt.meminfo_data(builder, nidu__iqd.meminfo)
        zguf__wcsrl = context.get_value_type(payload_type).as_pointer()
        kmq__ikrd = builder.bitcast(kmq__ikrd, zguf__wcsrl)
        builder.store(wmyjs__uniw._getvalue(), kmq__ikrd)
        return impl_ret_borrowed(context, builder, df_typ, exhdh__gluq)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        dsrre__ybt = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        rdcrp__ciqg = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=dsrre__ybt)
        noxdg__kitab = get_dataframe_payload(context, builder, df_typ,
            dsrre__ybt)
        nidu__iqd = construct_dataframe(context, builder, signature.
            return_type, noxdg__kitab.data, index_val, rdcrp__ciqg.parent, None
            )
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), noxdg__kitab.data)
        return nidu__iqd
    qswii__mmjs = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(qswii__mmjs, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    cdce__pxx = len(df_type.columns)
    sgdn__cvdpn = cdce__pxx
    tccu__cbcj = df_type.data
    yzx__jcp = df_type.columns
    index_typ = df_type.index
    kcyr__nkuz = col_name not in df_type.columns
    uxs__epbp = cdce__pxx
    if kcyr__nkuz:
        tccu__cbcj += arr_type,
        yzx__jcp += col_name,
        sgdn__cvdpn += 1
    else:
        uxs__epbp = df_type.columns.index(col_name)
        tccu__cbcj = tuple(arr_type if i == uxs__epbp else tccu__cbcj[i] for
            i in range(cdce__pxx))

    def codegen(context, builder, signature, args):
        exhdh__gluq, kue__rlpbd, qbo__kur = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, exhdh__gluq)
        yhwgx__jsdlg = cgutils.create_struct_proxy(df_type)(context,
            builder, value=exhdh__gluq)
        if df_type.is_table_format:
            onz__xafa = df_type.table_type
            gstft__gray = builder.extract_value(in_dataframe_payload.data, 0)
            vmf__akt = TableType(tccu__cbcj)
            oxhqj__wiy = set_table_data_codegen(context, builder, onz__xafa,
                gstft__gray, vmf__akt, arr_type, qbo__kur, uxs__epbp,
                kcyr__nkuz)
            data_tup = context.make_tuple(builder, types.Tuple([vmf__akt]),
                [oxhqj__wiy])
        else:
            rwm__kpm = [(builder.extract_value(in_dataframe_payload.data, i
                ) if i != uxs__epbp else qbo__kur) for i in range(cdce__pxx)]
            if kcyr__nkuz:
                rwm__kpm.append(qbo__kur)
            for wgmwf__foqsf, nzept__guho in zip(rwm__kpm, tccu__cbcj):
                context.nrt.incref(builder, nzept__guho, wgmwf__foqsf)
            data_tup = context.make_tuple(builder, types.Tuple(tccu__cbcj),
                rwm__kpm)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        ath__wlcos = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, yhwgx__jsdlg.parent, None)
        if not kcyr__nkuz and arr_type == df_type.data[uxs__epbp]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            kmq__ikrd = context.nrt.meminfo_data(builder, yhwgx__jsdlg.meminfo)
            zguf__wcsrl = context.get_value_type(payload_type).as_pointer()
            kmq__ikrd = builder.bitcast(kmq__ikrd, zguf__wcsrl)
            nuip__tbv = get_dataframe_payload(context, builder, df_type,
                ath__wlcos)
            builder.store(nuip__tbv._getvalue(), kmq__ikrd)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, vmf__akt, builder.extract_value
                    (data_tup, 0))
            else:
                for wgmwf__foqsf, nzept__guho in zip(rwm__kpm, tccu__cbcj):
                    context.nrt.incref(builder, nzept__guho, wgmwf__foqsf)
        has_parent = cgutils.is_not_null(builder, yhwgx__jsdlg.parent)
        with builder.if_then(has_parent):
            juo__diwx = context.get_python_api(builder)
            jyj__cts = juo__diwx.gil_ensure()
            whr__bqy = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, qbo__kur)
            gtax__kis = numba.core.pythonapi._BoxContext(context, builder,
                juo__diwx, whr__bqy)
            crxp__qrv = gtax__kis.pyapi.from_native_value(arr_type,
                qbo__kur, gtax__kis.env_manager)
            if isinstance(col_name, str):
                blwdl__zihz = context.insert_const_string(builder.module,
                    col_name)
                myeqb__tqas = juo__diwx.string_from_string(blwdl__zihz)
            else:
                assert isinstance(col_name, int)
                myeqb__tqas = juo__diwx.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            juo__diwx.object_setitem(yhwgx__jsdlg.parent, myeqb__tqas,
                crxp__qrv)
            juo__diwx.decref(crxp__qrv)
            juo__diwx.decref(myeqb__tqas)
            juo__diwx.gil_release(jyj__cts)
        return ath__wlcos
    qswii__mmjs = DataFrameType(tccu__cbcj, index_typ, yzx__jcp, df_type.
        dist, df_type.is_table_format)
    sig = signature(qswii__mmjs, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    cdce__pxx = len(pyval.columns)
    rwm__kpm = tuple(pyval.iloc[:, i].values for i in range(cdce__pxx))
    if df_type.is_table_format:
        xths__zee = context.get_constant_generic(builder, df_type.
            table_type, Table(rwm__kpm))
        data_tup = lir.Constant.literal_struct([xths__zee])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], zhkg__cti) for i,
            zhkg__cti in enumerate(rwm__kpm)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    txg__msi = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, txg__msi])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    hdel__uibyy = context.get_constant(types.int64, -1)
    mmv__hnt = context.get_constant_null(types.voidptr)
    rgry__fvbex = lir.Constant.literal_struct([hdel__uibyy, mmv__hnt,
        mmv__hnt, payload, hdel__uibyy])
    rgry__fvbex = cgutils.global_constant(builder, '.const.meminfo',
        rgry__fvbex).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([rgry__fvbex, txg__msi])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if (fromty.data != toty.data or fromty.has_runtime_cols != toty.
        has_runtime_cols):
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        iim__bot = context.cast(builder, in_dataframe_payload.index, fromty
            .index, toty.index)
    else:
        iim__bot = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, iim__bot)
    if fromty.is_table_format == toty.is_table_format:
        zch__mbdkv = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                zch__mbdkv)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), zch__mbdkv)
    elif toty.is_table_format:
        zch__mbdkv = _cast_df_data_to_table_format(context, builder, fromty,
            toty, in_dataframe_payload)
    else:
        zch__mbdkv = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, zch__mbdkv, iim__bot,
        in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    jjmoe__oppf = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        ntqy__rhn = get_index_data_arr_types(toty.index)[0]
        urbb__gfxm = bodo.utils.transform.get_type_alloc_counts(ntqy__rhn) - 1
        zxljl__zuhd = ', '.join('0' for kue__rlpbd in range(urbb__gfxm))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(zxljl__zuhd, ', ' if urbb__gfxm == 1 else ''))
        jjmoe__oppf['index_arr_type'] = ntqy__rhn
    mmih__dwk = []
    for i, arr_typ in enumerate(toty.data):
        urbb__gfxm = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        zxljl__zuhd = ', '.join('0' for kue__rlpbd in range(urbb__gfxm))
        mivz__csrqt = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, zxljl__zuhd, ', ' if urbb__gfxm == 1 else ''))
        mmih__dwk.append(mivz__csrqt)
        jjmoe__oppf[f'arr_type{i}'] = arr_typ
    mmih__dwk = ', '.join(mmih__dwk)
    ciu__fzm = 'def impl():\n'
    han__mnml = bodo.hiframes.dataframe_impl._gen_init_df(ciu__fzm, toty.
        columns, mmih__dwk, index, jjmoe__oppf)
    df = context.compile_internal(builder, han__mnml, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    qrcw__zamcd = toty.table_type
    xths__zee = cgutils.create_struct_proxy(qrcw__zamcd)(context, builder)
    xths__zee.parent = in_dataframe_payload.parent
    for pgj__bfhr, fry__zngi in qrcw__zamcd.type_to_blk.items():
        mwti__xhv = context.get_constant(types.int64, len(qrcw__zamcd.
            block_to_arr_ind[fry__zngi]))
        kue__rlpbd, pgs__awy = ListInstance.allocate_ex(context, builder,
            types.List(pgj__bfhr), mwti__xhv)
        pgs__awy.size = mwti__xhv
        setattr(xths__zee, f'block_{fry__zngi}', pgs__awy.value)
    for i, pgj__bfhr in enumerate(fromty.data):
        qwsb__cona = builder.extract_value(in_dataframe_payload.data, i)
        fry__zngi = qrcw__zamcd.type_to_blk[pgj__bfhr]
        wqxi__rstfv = getattr(xths__zee, f'block_{fry__zngi}')
        quqd__xpniu = ListInstance(context, builder, types.List(pgj__bfhr),
            wqxi__rstfv)
        cimbd__bxmkq = context.get_constant(types.int64, qrcw__zamcd.
            block_offsets[i])
        quqd__xpniu.setitem(cimbd__bxmkq, qwsb__cona, True)
    data_tup = context.make_tuple(builder, types.Tuple([qrcw__zamcd]), [
        xths__zee._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    qrcw__zamcd = fromty.table_type
    xths__zee = cgutils.create_struct_proxy(qrcw__zamcd)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    rwm__kpm = []
    for i, pgj__bfhr in enumerate(toty.data):
        fry__zngi = qrcw__zamcd.type_to_blk[pgj__bfhr]
        wqxi__rstfv = getattr(xths__zee, f'block_{fry__zngi}')
        quqd__xpniu = ListInstance(context, builder, types.List(pgj__bfhr),
            wqxi__rstfv)
        cimbd__bxmkq = context.get_constant(types.int64, qrcw__zamcd.
            block_offsets[i])
        qwsb__cona = quqd__xpniu.getitem(cimbd__bxmkq)
        context.nrt.incref(builder, pgj__bfhr, qwsb__cona)
        rwm__kpm.append(qwsb__cona)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), rwm__kpm)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    qlfi__iojj, mmih__dwk, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    dfob__uozgl = gen_const_tup(qlfi__iojj)
    ciu__fzm = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    ciu__fzm += (
        '  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, {})\n'
        .format(mmih__dwk, index_arg, dfob__uozgl))
    xpv__jqx = {}
    exec(ciu__fzm, {'bodo': bodo, 'np': np}, xpv__jqx)
    ryj__dzlgr = xpv__jqx['_init_df']
    return ryj__dzlgr


def _get_df_args(data, index, columns, dtype, copy):
    vvqsq__rqj = ''
    if not is_overload_none(dtype):
        vvqsq__rqj = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        cdce__pxx = (len(data.types) - 1) // 2
        vhv__subc = [pgj__bfhr.literal_value for pgj__bfhr in data.types[1:
            cdce__pxx + 1]]
        data_val_types = dict(zip(vhv__subc, data.types[cdce__pxx + 1:]))
        rwm__kpm = ['data[{}]'.format(i) for i in range(cdce__pxx + 1, 2 *
            cdce__pxx + 1)]
        data_dict = dict(zip(vhv__subc, rwm__kpm))
        if is_overload_none(index):
            for i, pgj__bfhr in enumerate(data.types[cdce__pxx + 1:]):
                if isinstance(pgj__bfhr, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(cdce__pxx + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        oiw__ars = '.copy()' if copy else ''
        hdtya__qdtlg = get_overload_const_list(columns)
        cdce__pxx = len(hdtya__qdtlg)
        data_val_types = {gtax__kis: data.copy(ndim=1) for gtax__kis in
            hdtya__qdtlg}
        rwm__kpm = ['data[:,{}]{}'.format(i, oiw__ars) for i in range(
            cdce__pxx)]
        data_dict = dict(zip(hdtya__qdtlg, rwm__kpm))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    mmih__dwk = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[gtax__kis], df_len, vvqsq__rqj) for gtax__kis in
        col_names))
    if len(col_names) == 0:
        mmih__dwk = '()'
    return col_names, mmih__dwk, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for gtax__kis in col_names:
        if gtax__kis in data_dict and is_iterable_type(data_val_types[
            gtax__kis]):
            df_len = 'len({})'.format(data_dict[gtax__kis])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(gtax__kis in data_dict for gtax__kis in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    gtqu__iou = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for gtax__kis in col_names:
        if gtax__kis not in data_dict:
            data_dict[gtax__kis] = gtqu__iou


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            pgj__bfhr = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(pgj__bfhr)
        return impl
    if len(df.columns) == 0:
        return lambda df: 0

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        cfb__cie = idx.literal_value
        if isinstance(cfb__cie, int):
            xtzzc__vhivs = tup.types[cfb__cie]
        elif isinstance(cfb__cie, slice):
            xtzzc__vhivs = types.BaseTuple.from_types(tup.types[cfb__cie])
        return signature(xtzzc__vhivs, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    wzbx__yohcw, idx = sig.args
    idx = idx.literal_value
    tup, kue__rlpbd = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(wzbx__yohcw)
        if not 0 <= idx < len(wzbx__yohcw):
            raise IndexError('cannot index at %d in %s' % (idx, wzbx__yohcw))
        qwz__uti = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        puwsc__lnpja = cgutils.unpack_tuple(builder, tup)[idx]
        qwz__uti = context.make_tuple(builder, sig.return_type, puwsc__lnpja)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, qwz__uti)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, xmfm__yfv, suffix_x,
            suffix_y, is_join, indicator, _bodo_na_equal, egvlp__egfny) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        bwp__uutdr = set(left_on) & set(right_on)
        xxv__fwc = set(left_df.columns) & set(right_df.columns)
        tmtoc__szcaz = xxv__fwc - bwp__uutdr
        ecb__joqly = '$_bodo_index_' in left_on
        pxk__oqwr = '$_bodo_index_' in right_on
        how = get_overload_const_str(xmfm__yfv)
        soeq__tal = how in {'left', 'outer'}
        jwyzl__ydapz = how in {'right', 'outer'}
        columns = []
        data = []
        if ecb__joqly and not pxk__oqwr and not is_join.literal_value:
            hif__grei = right_on[0]
            if hif__grei in left_df.columns:
                columns.append(hif__grei)
                data.append(right_df.data[right_df.columns.index(hif__grei)])
        if pxk__oqwr and not ecb__joqly and not is_join.literal_value:
            zey__wapog = left_on[0]
            if zey__wapog in right_df.columns:
                columns.append(zey__wapog)
                data.append(left_df.data[left_df.columns.index(zey__wapog)])
        for eveo__erqn, oxy__udm in zip(left_df.data, left_df.columns):
            columns.append(str(oxy__udm) + suffix_x.literal_value if 
                oxy__udm in tmtoc__szcaz else oxy__udm)
            if oxy__udm in bwp__uutdr:
                data.append(eveo__erqn)
            else:
                data.append(to_nullable_type(eveo__erqn) if jwyzl__ydapz else
                    eveo__erqn)
        for eveo__erqn, oxy__udm in zip(right_df.data, right_df.columns):
            if oxy__udm not in bwp__uutdr:
                columns.append(str(oxy__udm) + suffix_y.literal_value if 
                    oxy__udm in tmtoc__szcaz else oxy__udm)
                data.append(to_nullable_type(eveo__erqn) if soeq__tal else
                    eveo__erqn)
        fwho__kikw = get_overload_const_bool(indicator)
        if fwho__kikw:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        if ecb__joqly and pxk__oqwr and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif ecb__joqly and not pxk__oqwr:
            index_typ = right_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif pxk__oqwr and not ecb__joqly:
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        owy__bxujm = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(owy__bxujm, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    nidu__iqd = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return nidu__iqd._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    wygzq__ziuma = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    svev__jvm = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', wygzq__ziuma, svev__jvm,
        package_name='pandas', module_name='General')
    ciu__fzm = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        luz__pez = 0
        mmih__dwk = []
        names = []
        for i, rae__lpaxw in enumerate(objs.types):
            assert isinstance(rae__lpaxw, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(rae__lpaxw, 'pd.concat()')
            if isinstance(rae__lpaxw, SeriesType):
                names.append(str(luz__pez))
                luz__pez += 1
                mmih__dwk.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(rae__lpaxw.columns)
                for jqfyj__yohv in range(len(rae__lpaxw.data)):
                    mmih__dwk.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, jqfyj__yohv))
        return bodo.hiframes.dataframe_impl._gen_init_df(ciu__fzm, names,
            ', '.join(mmih__dwk), index)
    assert axis == 0
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(pgj__bfhr, DataFrameType) for pgj__bfhr in
            objs.types)
        pmgo__lia = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pd.concat()')
            pmgo__lia.extend(df.columns)
        pmgo__lia = list(dict.fromkeys(pmgo__lia).keys())
        jpqiu__yhtz = {}
        for luz__pez, gtax__kis in enumerate(pmgo__lia):
            for df in objs.types:
                if gtax__kis in df.columns:
                    jpqiu__yhtz['arr_typ{}'.format(luz__pez)] = df.data[df.
                        columns.index(gtax__kis)]
                    break
        assert len(jpqiu__yhtz) == len(pmgo__lia)
        chci__tfn = []
        for luz__pez, gtax__kis in enumerate(pmgo__lia):
            args = []
            for i, df in enumerate(objs.types):
                if gtax__kis in df.columns:
                    uxs__epbp = df.columns.index(gtax__kis)
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, uxs__epbp))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, luz__pez))
            ciu__fzm += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'.
                format(luz__pez, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(ciu__fzm,
            pmgo__lia, ', '.join('A{}'.format(i) for i in range(len(
            pmgo__lia))), index, jpqiu__yhtz)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(pgj__bfhr, SeriesType) for pgj__bfhr in objs.
            types)
        ciu__fzm += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'.
            format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            ciu__fzm += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ciu__fzm += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        ciu__fzm += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        xpv__jqx = {}
        exec(ciu__fzm, {'bodo': bodo, 'np': np, 'numba': numba}, xpv__jqx)
        return xpv__jqx['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pd.concat()')
        df_type = objs.dtype
        for luz__pez, gtax__kis in enumerate(df_type.columns):
            ciu__fzm += '  arrs{} = []\n'.format(luz__pez)
            ciu__fzm += '  for i in range(len(objs)):\n'
            ciu__fzm += '    df = objs[i]\n'
            ciu__fzm += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(luz__pez))
            ciu__fzm += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(luz__pez))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            ciu__fzm += '  arrs_index = []\n'
            ciu__fzm += '  for i in range(len(objs)):\n'
            ciu__fzm += '    df = objs[i]\n'
            ciu__fzm += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(ciu__fzm, df_type.
            columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        ciu__fzm += '  arrs = []\n'
        ciu__fzm += '  for i in range(len(objs)):\n'
        ciu__fzm += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        ciu__fzm += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            ciu__fzm += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ciu__fzm += '  arrs_index = []\n'
            ciu__fzm += '  for i in range(len(objs)):\n'
            ciu__fzm += '    S = objs[i]\n'
            ciu__fzm += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            ciu__fzm += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        ciu__fzm += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        xpv__jqx = {}
        exec(ciu__fzm, {'bodo': bodo, 'np': np, 'numba': numba}, xpv__jqx)
        return xpv__jqx['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        qswii__mmjs = df.copy(index=index, is_table_format=False)
        return signature(qswii__mmjs, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    ogoel__dnum = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return ogoel__dnum._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    wygzq__ziuma = dict(index=index, name=name)
    svev__jvm = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', wygzq__ziuma, svev__jvm,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        jpqiu__yhtz = (types.Array(types.int64, 1, 'C'),) + df.data
        ikat__pbal = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, jpqiu__yhtz)
        return signature(ikat__pbal, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    ogoel__dnum = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return ogoel__dnum._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    ogoel__dnum = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return ogoel__dnum._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    ogoel__dnum = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return ogoel__dnum._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True, parallel
    =False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    kgzns__mop = get_overload_const_bool(check_duplicates)
    wyai__jxi = not is_overload_none(value_names)
    adg__azd = isinstance(values_tup, types.UniTuple)
    if adg__azd:
        jsyd__ioh = [to_nullable_type(values_tup.dtype)]
    else:
        jsyd__ioh = [to_nullable_type(nzept__guho) for nzept__guho in
            values_tup]
    ciu__fzm = 'def impl(\n'
    ciu__fzm += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, parallel=False
"""
    ciu__fzm += '):\n'
    ciu__fzm += '    if parallel:\n'
    ktk__merkz = ', '.join([f'array_to_info(index_tup[{i}])' for i in range
        (len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    ciu__fzm += f'        info_list = [{ktk__merkz}]\n'
    ciu__fzm += '        cpp_table = arr_info_list_to_table(info_list)\n'
    ciu__fzm += (
        f'        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)\n'
        )
    rbauc__zdd = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    tfl__qvsmu = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    umals__zhbk = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    ciu__fzm += f'        index_tup = ({rbauc__zdd},)\n'
    ciu__fzm += f'        columns_tup = ({tfl__qvsmu},)\n'
    ciu__fzm += f'        values_tup = ({umals__zhbk},)\n'
    ciu__fzm += '        delete_table(cpp_table)\n'
    ciu__fzm += '        delete_table(out_cpp_table)\n'
    ciu__fzm += '    columns_arr = columns_tup[0]\n'
    if adg__azd:
        ciu__fzm += '    values_arrs = [arr for arr in values_tup]\n'
    ciu__fzm += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    ciu__fzm += '        index_tup\n'
    ciu__fzm += '    )\n'
    ciu__fzm += '    n_rows = len(unique_index_arr_tup[0])\n'
    ciu__fzm += '    num_values_arrays = len(values_tup)\n'
    ciu__fzm += '    n_unique_pivots = len(pivot_values)\n'
    if adg__azd:
        ciu__fzm += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        ciu__fzm += '    n_cols = n_unique_pivots\n'
    ciu__fzm += '    col_map = {}\n'
    ciu__fzm += '    for i in range(n_unique_pivots):\n'
    ciu__fzm += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    ciu__fzm += '            raise ValueError(\n'
    ciu__fzm += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    ciu__fzm += '            )\n'
    ciu__fzm += '        col_map[pivot_values[i]] = i\n'
    xgqx__ylqtq = False
    for i, zpr__yhwk in enumerate(jsyd__ioh):
        if zpr__yhwk == bodo.string_array_type:
            xgqx__ylqtq = True
            ciu__fzm += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            ciu__fzm += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if xgqx__ylqtq:
        if kgzns__mop:
            ciu__fzm += '    nbytes = (n_rows + 7) >> 3\n'
            ciu__fzm += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        ciu__fzm += '    for i in range(len(columns_arr)):\n'
        ciu__fzm += '        col_name = columns_arr[i]\n'
        ciu__fzm += '        pivot_idx = col_map[col_name]\n'
        ciu__fzm += '        row_idx = row_vector[i]\n'
        if kgzns__mop:
            ciu__fzm += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            ciu__fzm += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            ciu__fzm += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            ciu__fzm += '        else:\n'
            ciu__fzm += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if adg__azd:
            ciu__fzm += '        for j in range(num_values_arrays):\n'
            ciu__fzm += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            ciu__fzm += '            len_arr = len_arrs_0[col_idx]\n'
            ciu__fzm += '            values_arr = values_arrs[j]\n'
            ciu__fzm += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            ciu__fzm += (
                '                len_arr[row_idx] = len(values_arr[i])\n')
            ciu__fzm += (
                '                total_lens_0[col_idx] += len(values_arr[i])\n'
                )
        else:
            for i, zpr__yhwk in enumerate(jsyd__ioh):
                if zpr__yhwk == bodo.string_array_type:
                    ciu__fzm += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    ciu__fzm += f"""            len_arrs_{i}[pivot_idx][row_idx] = len(values_tup[{i}][i])
"""
                    ciu__fzm += f"""            total_lens_{i}[pivot_idx] += len(values_tup[{i}][i])
"""
    for i, zpr__yhwk in enumerate(jsyd__ioh):
        if zpr__yhwk == bodo.string_array_type:
            ciu__fzm += f'    data_arrs_{i} = [\n'
            ciu__fzm += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            ciu__fzm += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            ciu__fzm += '        )\n'
            ciu__fzm += '        for i in range(n_cols)\n'
            ciu__fzm += '    ]\n'
        else:
            ciu__fzm += f'    data_arrs_{i} = [\n'
            ciu__fzm += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            ciu__fzm += '        for _ in range(n_cols)\n'
            ciu__fzm += '    ]\n'
    if not xgqx__ylqtq and kgzns__mop:
        ciu__fzm += '    nbytes = (n_rows + 7) >> 3\n'
        ciu__fzm += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    ciu__fzm += '    for i in range(len(columns_arr)):\n'
    ciu__fzm += '        col_name = columns_arr[i]\n'
    ciu__fzm += '        pivot_idx = col_map[col_name]\n'
    ciu__fzm += '        row_idx = row_vector[i]\n'
    if not xgqx__ylqtq and kgzns__mop:
        ciu__fzm += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        ciu__fzm += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        ciu__fzm += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        ciu__fzm += '        else:\n'
        ciu__fzm += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if adg__azd:
        ciu__fzm += '        for j in range(num_values_arrays):\n'
        ciu__fzm += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        ciu__fzm += '            col_arr = data_arrs_0[col_idx]\n'
        ciu__fzm += '            values_arr = values_arrs[j]\n'
        ciu__fzm += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        ciu__fzm += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        ciu__fzm += '            else:\n'
        ciu__fzm += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, zpr__yhwk in enumerate(jsyd__ioh):
            ciu__fzm += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            ciu__fzm += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            ciu__fzm += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            ciu__fzm += f'        else:\n'
            ciu__fzm += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_tup) == 1:
        ciu__fzm += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names[0])
"""
    else:
        ciu__fzm += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names, None)
"""
    if wyai__jxi:
        ciu__fzm += '    num_rows = len(value_names) * len(pivot_values)\n'
        if value_names == bodo.string_array_type:
            ciu__fzm += '    total_chars = 0\n'
            ciu__fzm += '    for i in range(len(value_names)):\n'
            ciu__fzm += '        total_chars += len(value_names[i])\n'
            ciu__fzm += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
        else:
            ciu__fzm += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names, (-1,))
"""
        if pivot_values == bodo.string_array_type:
            ciu__fzm += '    total_chars = 0\n'
            ciu__fzm += '    for i in range(len(pivot_values)):\n'
            ciu__fzm += '        total_chars += len(pivot_values[i])\n'
            ciu__fzm += """    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(value_names))
"""
        else:
            ciu__fzm += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
        ciu__fzm += '    for i in range(len(value_names)):\n'
        ciu__fzm += '        for j in range(len(pivot_values)):\n'
        ciu__fzm += (
            '            new_value_names[(i * len(pivot_values)) + j] = value_names[i]\n'
            )
        ciu__fzm += (
            '            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]\n'
            )
        ciu__fzm += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name), None)
"""
    else:
        ciu__fzm += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name)
"""
    quum__nuujb = ', '.join(f'data_arrs_{i}' for i in range(len(jsyd__ioh)))
    ciu__fzm += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({quum__nuujb},), n_rows)
"""
    ciu__fzm += (
        '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
        )
    ciu__fzm += '        (table,), index, column_index\n'
    ciu__fzm += '    )\n'
    xpv__jqx = {}
    tryw__fxsyd = {f'data_arr_typ_{i}': zpr__yhwk for i, zpr__yhwk in
        enumerate(jsyd__ioh)}
    gaw__elwi = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, **tryw__fxsyd}
    exec(ciu__fzm, gaw__elwi, xpv__jqx)
    impl = xpv__jqx['impl']
    return impl


def gen_pandas_parquet_metadata(df, write_non_range_index_to_metadata,
    write_rangeindex_to_metadata, partition_cols=None):
    saq__tjusk = {}
    saq__tjusk['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, ysy__mkgfc in zip(df.columns, df.data):
        if col_name in partition_cols:
            continue
        if isinstance(ysy__mkgfc, types.Array) or ysy__mkgfc == boolean_array:
            knsqh__vula = ldzru__bzdva = ysy__mkgfc.dtype.name
            if ldzru__bzdva.startswith('datetime'):
                knsqh__vula = 'datetime'
        elif ysy__mkgfc == string_array_type:
            knsqh__vula = 'unicode'
            ldzru__bzdva = 'object'
        elif ysy__mkgfc == binary_array_type:
            knsqh__vula = 'bytes'
            ldzru__bzdva = 'object'
        elif isinstance(ysy__mkgfc, DecimalArrayType):
            knsqh__vula = ldzru__bzdva = 'object'
        elif isinstance(ysy__mkgfc, IntegerArrayType):
            savke__rnmfs = ysy__mkgfc.dtype.name
            if savke__rnmfs.startswith('int'):
                knsqh__vula = 'Int' + savke__rnmfs[3:]
            elif savke__rnmfs.startswith('uint'):
                knsqh__vula = 'UInt' + savke__rnmfs[4:]
            else:
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, ysy__mkgfc))
            ldzru__bzdva = ysy__mkgfc.dtype.name
        elif ysy__mkgfc == datetime_date_array_type:
            knsqh__vula = 'datetime'
            ldzru__bzdva = 'object'
        elif isinstance(ysy__mkgfc, (StructArrayType, ArrayItemArrayType)):
            knsqh__vula = 'object'
            ldzru__bzdva = 'object'
        else:
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, ysy__mkgfc))
        mtd__rnvla = {'name': col_name, 'field_name': col_name,
            'pandas_type': knsqh__vula, 'numpy_type': ldzru__bzdva,
            'metadata': None}
        saq__tjusk['columns'].append(mtd__rnvla)
    if write_non_range_index_to_metadata:
        if isinstance(df.index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in df.index.name:
            nzdp__imtwd = '__index_level_0__'
            qqcq__mxoq = None
        else:
            nzdp__imtwd = '%s'
            qqcq__mxoq = '%s'
        saq__tjusk['index_columns'] = [nzdp__imtwd]
        saq__tjusk['columns'].append({'name': qqcq__mxoq, 'field_name':
            nzdp__imtwd, 'pandas_type': df.index.pandas_type_name,
            'numpy_type': df.index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        saq__tjusk['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        saq__tjusk['index_columns'] = []
    saq__tjusk['pandas_version'] = pd.__version__
    return saq__tjusk


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, fname, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_parquet()')
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        ptj__qxq = []
        for inklp__kda in partition_cols:
            try:
                idx = df.columns.index(inklp__kda)
            except ValueError as ralpf__ixv:
                raise BodoError(
                    f'Partition column {inklp__kda} is not in dataframe')
            ptj__qxq.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    ngntg__cmlmq = isinstance(df.index, bodo.hiframes.pd_index_ext.
        RangeIndexType)
    kshoh__izrkl = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not ngntg__cmlmq)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not ngntg__cmlmq or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and ngntg__cmlmq and not is_overload_true(_is_parallel)
    wyj__fowy = json.dumps(gen_pandas_parquet_metadata(df,
        write_non_range_index_to_metadata, write_rangeindex_to_metadata,
        partition_cols=partition_cols))
    if not is_overload_true(_is_parallel) and ngntg__cmlmq:
        wyj__fowy = wyj__fowy.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            wyj__fowy = wyj__fowy.replace('"%s"', '%s')
    mmih__dwk = ', '.join(
        'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(len(df.columns)))
    ciu__fzm = """def df_to_parquet(df, fname, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, _is_parallel=False):
"""
    if df.is_table_format:
        ciu__fzm += (
            '    table = py_table_to_cpp_table(get_dataframe_table(df), py_table_typ)\n'
            )
    else:
        ciu__fzm += '    info_list = [{}]\n'.format(mmih__dwk)
        ciu__fzm += '    table = arr_info_list_to_table(info_list)\n'
    ciu__fzm += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and kshoh__izrkl:
        ciu__fzm += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        mda__bge = True
    else:
        ciu__fzm += '    index_col = array_to_info(np.empty(0))\n'
        mda__bge = False
    ciu__fzm += '    metadata = """' + wyj__fowy + '"""\n'
    ciu__fzm += '    if compression is None:\n'
    ciu__fzm += "        compression = 'none'\n"
    ciu__fzm += '    if df.index.name is not None:\n'
    ciu__fzm += '        name_ptr = df.index.name\n'
    ciu__fzm += '    else:\n'
    ciu__fzm += "        name_ptr = 'null'\n"
    ciu__fzm += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel=_is_parallel)
"""
    uxbbm__tvq = None
    if partition_cols:
        uxbbm__tvq = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        tpo__ukzx = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in ptj__qxq)
        if tpo__ukzx:
            ciu__fzm += '    cat_info_list = [{}]\n'.format(tpo__ukzx)
            ciu__fzm += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            ciu__fzm += '    cat_table = table\n'
        ciu__fzm += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        ciu__fzm += (
            f'    part_cols_idxs = np.array({ptj__qxq}, dtype=np.int32)\n')
        ciu__fzm += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(fname),\n'
            )
        ciu__fzm += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        ciu__fzm += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        ciu__fzm += (
            '                            unicode_to_utf8(compression),\n')
        ciu__fzm += '                            _is_parallel,\n'
        ciu__fzm += (
            '                            unicode_to_utf8(bucket_region))\n')
        ciu__fzm += '    delete_table_decref_arrays(table)\n'
        ciu__fzm += '    delete_info_decref_array(index_col)\n'
        ciu__fzm += '    delete_info_decref_array(col_names_no_partitions)\n'
        ciu__fzm += '    delete_info_decref_array(col_names)\n'
        if tpo__ukzx:
            ciu__fzm += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        ciu__fzm += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        ciu__fzm += (
            '                            table, col_names, index_col,\n')
        ciu__fzm += '                            ' + str(mda__bge) + ',\n'
        ciu__fzm += '                            unicode_to_utf8(metadata),\n'
        ciu__fzm += (
            '                            unicode_to_utf8(compression),\n')
        ciu__fzm += (
            '                            _is_parallel, 1, df.index.start,\n')
        ciu__fzm += (
            '                            df.index.stop, df.index.step,\n')
        ciu__fzm += '                            unicode_to_utf8(name_ptr),\n'
        ciu__fzm += (
            '                            unicode_to_utf8(bucket_region))\n')
        ciu__fzm += '    delete_table_decref_arrays(table)\n'
        ciu__fzm += '    delete_info_decref_array(index_col)\n'
        ciu__fzm += '    delete_info_decref_array(col_names)\n'
    else:
        ciu__fzm += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        ciu__fzm += (
            '                            table, col_names, index_col,\n')
        ciu__fzm += '                            ' + str(mda__bge) + ',\n'
        ciu__fzm += '                            unicode_to_utf8(metadata),\n'
        ciu__fzm += (
            '                            unicode_to_utf8(compression),\n')
        ciu__fzm += '                            _is_parallel, 0, 0, 0, 0,\n'
        ciu__fzm += '                            unicode_to_utf8(name_ptr),\n'
        ciu__fzm += (
            '                            unicode_to_utf8(bucket_region))\n')
        ciu__fzm += '    delete_table_decref_arrays(table)\n'
        ciu__fzm += '    delete_info_decref_array(index_col)\n'
        ciu__fzm += '    delete_info_decref_array(col_names)\n'
    xpv__jqx = {}
    exec(ciu__fzm, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': pd.array(df.columns),
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': uxbbm__tvq}, xpv__jqx)
    xgtn__sos = xpv__jqx['df_to_parquet']
    return xgtn__sos


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    wxtn__alq = 'all_ok'
    jak__mse = urlparse(con).scheme
    if _is_parallel and bodo.get_rank() == 0:
        wdswa__vdse = 100
        if chunksize is None:
            rupx__dbq = wdswa__vdse
        else:
            rupx__dbq = min(chunksize, wdswa__vdse)
        if _is_table_create:
            df = df.iloc[:rupx__dbq, :]
        else:
            df = df.iloc[rupx__dbq:, :]
            if len(df) == 0:
                return wxtn__alq
    if jak__mse == 'snowflake':
        try:
            from snowflake.connector.pandas_tools import pd_writer
            from bodo import snowflake_sqlalchemy_compat
            if method is not None and _is_table_create and bodo.get_rank(
                ) == 0:
                import warnings
                from bodo.utils.typing import BodoWarning
                warnings.warn(BodoWarning(
                    'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                    ))
            method = pd_writer
            df.columns = [(gtax__kis.upper() if gtax__kis.islower() else
                gtax__kis) for gtax__kis in df.columns]
        except ImportError as ralpf__ixv:
            wxtn__alq = (
                "Snowflake Python connector not found. It can be installed by calling 'conda install -c conda-forge snowflake-connector-python' or 'pip install snowflake-connector-python'."
                )
            return wxtn__alq
    try:
        df.to_sql(name, con, schema, if_exists, index, index_label,
            chunksize, dtype, method)
    except Exception as eycs__kds:
        wxtn__alq = eycs__kds.args[0]
    return wxtn__alq


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    wygzq__ziuma = dict(chunksize=chunksize)
    svev__jvm = dict(chunksize=None)
    check_unsupported_args('to_sql', wygzq__ziuma, svev__jvm, package_name=
        'pandas', module_name='IO')
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues for writing to table {name}.'
                ))

    def _impl(df, name, con, schema=None, if_exists='fail', index=True,
        index_label=None, chunksize=None, dtype=None, method=None,
        _is_parallel=False):
        npv__mew = bodo.libs.distributed_api.get_rank()
        wxtn__alq = 'unset'
        if npv__mew != 0:
            wxtn__alq = bcast_scalar(wxtn__alq)
        elif npv__mew == 0:
            wxtn__alq = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                True, _is_parallel)
            wxtn__alq = bcast_scalar(wxtn__alq)
        if_exists = 'append'
        if _is_parallel and wxtn__alq == 'all_ok':
            wxtn__alq = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                False, _is_parallel)
        if wxtn__alq != 'all_ok':
            print('err_msg=', wxtn__alq)
            raise ValueError('error in to_sql() operation')
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        pdr__ueks = get_overload_const_str(path_or_buf)
        if pdr__ueks.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if isinstance(columns, types.List):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must not be list type. Please convert to tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='columns', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=False, compression='infer', index=True,
    indent=None, storage_options=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='columns', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=False, compression='infer', index=
            True, indent=None, storage_options=None):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='columns', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=False, compression='infer', index=True,
        indent=None, storage_options=None):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        tte__yyn = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(tte__yyn))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(tte__yyn))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    sme__ctjj = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    khz__gxgs = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', sme__ctjj, khz__gxgs,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    ciu__fzm = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        ryw__ujy = data.data.dtype.categories
        ciu__fzm += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        ryw__ujy = data.dtype.categories
        ciu__fzm += '  data_values = data\n'
    cdce__pxx = len(ryw__ujy)
    ciu__fzm += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    ciu__fzm += '  numba.parfors.parfor.init_prange()\n'
    ciu__fzm += '  n = len(data_values)\n'
    for i in range(cdce__pxx):
        ciu__fzm += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    ciu__fzm += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ciu__fzm += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for jqfyj__yohv in range(cdce__pxx):
        ciu__fzm += '          data_arr_{}[i] = 0\n'.format(jqfyj__yohv)
    ciu__fzm += '      else:\n'
    for onrdt__zteu in range(cdce__pxx):
        ciu__fzm += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            onrdt__zteu)
    mmih__dwk = ', '.join(f'data_arr_{i}' for i in range(cdce__pxx))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(ryw__ujy[0], np.datetime64):
        ryw__ujy = tuple(pd.Timestamp(gtax__kis) for gtax__kis in ryw__ujy)
    elif isinstance(ryw__ujy[0], np.timedelta64):
        ryw__ujy = tuple(pd.Timedelta(gtax__kis) for gtax__kis in ryw__ujy)
    return bodo.hiframes.dataframe_impl._gen_init_df(ciu__fzm, ryw__ujy,
        mmih__dwk, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_table, pd.read_sql_query, pd.read_gbq, pd.read_stata, pd.
    ExcelWriter, pd.json_normalize, pd.melt, pd.merge_ordered, pd.factorize,
    pd.unique, pd.wide_to_long, pd.bdate_range, pd.period_range, pd.
    infer_freq, pd.interval_range, pd.eval, pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'rank',
    'round', 'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix',
    'align', 'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'melt',
    'squeeze', 'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq',
    'asof', 'slice_shift', 'tshift', 'first_valid_index',
    'last_valid_index', 'resample', 'to_period', 'to_timestamp',
    'tz_convert', 'tz_localize', 'boxplot', 'hist', 'from_dict',
    'from_records', 'to_pickle', 'to_hdf', 'to_dict', 'to_excel', 'to_html',
    'to_feather', 'to_latex', 'to_stata', 'to_gbq', 'to_records',
    'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for psr__wlz in pd_unsupported:
        fname = mod_name + '.' + psr__wlz.__name__
        overload(psr__wlz, no_unliteral=True)(create_unsupported_overload(
            fname))


def _install_dataframe_unsupported():
    for iusw__rggj in dataframe_unsupported_attrs:
        vsyq__fgher = 'DataFrame.' + iusw__rggj
        overload_attribute(DataFrameType, iusw__rggj)(
            create_unsupported_overload(vsyq__fgher))
    for fname in dataframe_unsupported:
        vsyq__fgher = 'DataFrame.' + fname + '()'
        overload_method(DataFrameType, fname)(create_unsupported_overload(
            vsyq__fgher))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
