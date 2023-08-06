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
            cascb__qbtb = f'{len(self.data)} columns of types {set(self.data)}'
            vuy__xchvv = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({cascb__qbtb}, {self.index}, {vuy__xchvv}, {self.dist}, {self.is_table_format})'
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
            zodg__woqk = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(cnj__owkm.unify(typingctx, baqlz__fclz) if 
                cnj__owkm != baqlz__fclz else cnj__owkm for cnj__owkm,
                baqlz__fclz in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if zodg__woqk is not None and None not in data:
                return DataFrameType(data, zodg__woqk, self.columns, dist,
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
        return all(cnj__owkm.is_precise() for cnj__owkm in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        yos__saqz = self.columns.index(col_name)
        aomc__rjeqt = tuple(list(self.data[:yos__saqz]) + [new_type] + list
            (self.data[yos__saqz + 1:]))
        return DataFrameType(aomc__rjeqt, self.index, self.columns, self.
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
        kspe__kfp = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            kspe__kfp.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, kspe__kfp)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        kspe__kfp = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, kspe__kfp)


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
        ugkjy__tkbie = 'n',
        uevc__lrr = {'n': 5}
        nyzkz__esv, hbk__dtbb = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ugkjy__tkbie, uevc__lrr)
        lfa__tntvh = hbk__dtbb[0]
        if not is_overload_int(lfa__tntvh):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        cvxs__mmtst = df.copy(is_table_format=False)
        return cvxs__mmtst(*hbk__dtbb).replace(pysig=nyzkz__esv)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        necs__dzyy = (df,) + args
        ugkjy__tkbie = 'df', 'method', 'min_periods'
        uevc__lrr = {'method': 'pearson', 'min_periods': 1}
        kutm__tenft = 'method',
        nyzkz__esv, hbk__dtbb = bodo.utils.typing.fold_typing_args(func_name,
            necs__dzyy, kws, ugkjy__tkbie, uevc__lrr, kutm__tenft)
        qzhqs__tnqfh = hbk__dtbb[2]
        if not is_overload_int(qzhqs__tnqfh):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        dlrw__rymxc = []
        ggtuq__rrhn = []
        for odl__ysyw, kmv__mobvl in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(kmv__mobvl.dtype):
                dlrw__rymxc.append(odl__ysyw)
                ggtuq__rrhn.append(types.Array(types.float64, 1, 'A'))
        if len(dlrw__rymxc) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        ggtuq__rrhn = tuple(ggtuq__rrhn)
        dlrw__rymxc = tuple(dlrw__rymxc)
        index_typ = bodo.utils.typing.type_col_to_index(dlrw__rymxc)
        cvxs__mmtst = DataFrameType(ggtuq__rrhn, index_typ, dlrw__rymxc)
        return cvxs__mmtst(*hbk__dtbb).replace(pysig=nyzkz__esv)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        cnu__smst = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        ngm__lutce = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        pwy__wgd = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        qsuuv__iwe = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        kim__vxejo = dict(raw=ngm__lutce, result_type=pwy__wgd)
        nlmfw__lmfwf = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', kim__vxejo, nlmfw__lmfwf,
            package_name='pandas', module_name='DataFrame')
        vyn__dmla = True
        if types.unliteral(cnu__smst) == types.unicode_type:
            if not is_overload_constant_str(cnu__smst):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            vyn__dmla = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        ymek__faop = get_overload_const_int(axis)
        if vyn__dmla and ymek__faop != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif ymek__faop not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        exc__nti = []
        for arr_typ in df.data:
            fsrt__vfy = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            osfk__ikt = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(fsrt__vfy), types.int64), {}).return_type
            exc__nti.append(osfk__ikt)
        qmsto__igsih = types.none
        popb__idmnw = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(odl__ysyw) for odl__ysyw in df.columns)), None)
        odhp__vbd = types.BaseTuple.from_types(exc__nti)
        ycuh__sqf = df.index.dtype
        if ycuh__sqf == types.NPDatetime('ns'):
            ycuh__sqf = bodo.pd_timestamp_type
        if ycuh__sqf == types.NPTimedelta('ns'):
            ycuh__sqf = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(odhp__vbd):
            fohz__mjcg = HeterogeneousSeriesType(odhp__vbd, popb__idmnw,
                ycuh__sqf)
        else:
            fohz__mjcg = SeriesType(odhp__vbd.dtype, odhp__vbd, popb__idmnw,
                ycuh__sqf)
        uykhs__kjc = fohz__mjcg,
        if qsuuv__iwe is not None:
            uykhs__kjc += tuple(qsuuv__iwe.types)
        try:
            if not vyn__dmla:
                kbq__hbxmk = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(cnu__smst), self.context,
                    'DataFrame.apply', axis if ymek__faop == 1 else None)
            else:
                kbq__hbxmk = get_const_func_output_type(cnu__smst,
                    uykhs__kjc, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as uuif__lsrlz:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                uuif__lsrlz))
        if vyn__dmla:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(kbq__hbxmk, (SeriesType, HeterogeneousSeriesType)
                ) and kbq__hbxmk.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(kbq__hbxmk, HeterogeneousSeriesType):
                sir__jpvkx, vwqcb__fiffe = kbq__hbxmk.const_info
                ggb__cru = tuple(dtype_to_array_type(xyu__ujndm) for
                    xyu__ujndm in kbq__hbxmk.data.types)
                qtr__kbvpw = DataFrameType(ggb__cru, df.index, vwqcb__fiffe)
            elif isinstance(kbq__hbxmk, SeriesType):
                mygyh__upxwk, vwqcb__fiffe = kbq__hbxmk.const_info
                ggb__cru = tuple(dtype_to_array_type(kbq__hbxmk.dtype) for
                    sir__jpvkx in range(mygyh__upxwk))
                qtr__kbvpw = DataFrameType(ggb__cru, df.index, vwqcb__fiffe)
            else:
                bry__vaq = get_udf_out_arr_type(kbq__hbxmk)
                qtr__kbvpw = SeriesType(bry__vaq.dtype, bry__vaq, df.index,
                    None)
        else:
            qtr__kbvpw = kbq__hbxmk
        qbzf__srip = ', '.join("{} = ''".format(cnj__owkm) for cnj__owkm in
            kws.keys())
        vijy__pwpaw = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {qbzf__srip}):
"""
        vijy__pwpaw += '    pass\n'
        iqjh__yplmn = {}
        exec(vijy__pwpaw, {}, iqjh__yplmn)
        tpvmj__mgmhq = iqjh__yplmn['apply_stub']
        nyzkz__esv = numba.core.utils.pysignature(tpvmj__mgmhq)
        nxe__zozq = (cnu__smst, axis, ngm__lutce, pwy__wgd, qsuuv__iwe
            ) + tuple(kws.values())
        return signature(qtr__kbvpw, *nxe__zozq).replace(pysig=nyzkz__esv)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ugkjy__tkbie = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        uevc__lrr = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        kutm__tenft = ('subplots', 'sharex', 'sharey', 'layout',
            'use_index', 'grid', 'style', 'logx', 'logy', 'loglog', 'xlim',
            'ylim', 'rot', 'colormap', 'table', 'yerr', 'xerr',
            'sort_columns', 'secondary_y', 'colorbar', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        nyzkz__esv, hbk__dtbb = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ugkjy__tkbie, uevc__lrr, kutm__tenft)
        lycq__haxf = hbk__dtbb[2]
        if not is_overload_constant_str(lycq__haxf):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        etuwq__mzfra = hbk__dtbb[0]
        if not is_overload_none(etuwq__mzfra) and not (is_overload_int(
            etuwq__mzfra) or is_overload_constant_str(etuwq__mzfra)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(etuwq__mzfra):
            skb__adyb = get_overload_const_str(etuwq__mzfra)
            if skb__adyb not in df.columns:
                raise BodoError(f'{func_name}: {skb__adyb} column not found.')
        elif is_overload_int(etuwq__mzfra):
            beit__viuvn = get_overload_const_int(etuwq__mzfra)
            if beit__viuvn > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {beit__viuvn} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            etuwq__mzfra = df.columns[etuwq__mzfra]
        uyta__csife = hbk__dtbb[1]
        if not is_overload_none(uyta__csife) and not (is_overload_int(
            uyta__csife) or is_overload_constant_str(uyta__csife)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(uyta__csife):
            csmww__jkri = get_overload_const_str(uyta__csife)
            if csmww__jkri not in df.columns:
                raise BodoError(f'{func_name}: {csmww__jkri} column not found.'
                    )
        elif is_overload_int(uyta__csife):
            abddh__rtzo = get_overload_const_int(uyta__csife)
            if abddh__rtzo > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {abddh__rtzo} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            uyta__csife = df.columns[uyta__csife]
        ajoqn__mhqwk = hbk__dtbb[3]
        if not is_overload_none(ajoqn__mhqwk) and not is_tuple_like_type(
            ajoqn__mhqwk):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        wem__kptn = hbk__dtbb[10]
        if not is_overload_none(wem__kptn) and not is_overload_constant_str(
            wem__kptn):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        uwmn__aco = hbk__dtbb[12]
        if not is_overload_bool(uwmn__aco):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        rel__irwvw = hbk__dtbb[17]
        if not is_overload_none(rel__irwvw) and not is_tuple_like_type(
            rel__irwvw):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        oaoga__bukyn = hbk__dtbb[18]
        if not is_overload_none(oaoga__bukyn) and not is_tuple_like_type(
            oaoga__bukyn):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        gjn__mckb = hbk__dtbb[22]
        if not is_overload_none(gjn__mckb) and not is_overload_int(gjn__mckb):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        fun__wlcsc = hbk__dtbb[29]
        if not is_overload_none(fun__wlcsc) and not is_overload_constant_str(
            fun__wlcsc):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        djt__oksuk = hbk__dtbb[30]
        if not is_overload_none(djt__oksuk) and not is_overload_constant_str(
            djt__oksuk):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        opojc__rtp = types.List(types.mpl_line_2d_type)
        lycq__haxf = get_overload_const_str(lycq__haxf)
        if lycq__haxf == 'scatter':
            if is_overload_none(etuwq__mzfra) and is_overload_none(uyta__csife
                ):
                raise BodoError(
                    f'{func_name}: {lycq__haxf} requires an x and y column.')
            elif is_overload_none(etuwq__mzfra):
                raise BodoError(
                    f'{func_name}: {lycq__haxf} x column is missing.')
            elif is_overload_none(uyta__csife):
                raise BodoError(
                    f'{func_name}: {lycq__haxf} y column is missing.')
            opojc__rtp = types.mpl_path_collection_type
        elif lycq__haxf != 'line':
            raise BodoError(f'{func_name}: {lycq__haxf} plot is not supported.'
                )
        return signature(opojc__rtp, *hbk__dtbb).replace(pysig=nyzkz__esv)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            ueegp__zwsa = df.columns.index(attr)
            arr_typ = df.data[ueegp__zwsa]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            aktq__lydcv = []
            aomc__rjeqt = []
            nexxr__ltbvm = False
            for i, sdsh__pwsg in enumerate(df.columns):
                if sdsh__pwsg[0] != attr:
                    continue
                nexxr__ltbvm = True
                aktq__lydcv.append(sdsh__pwsg[1] if len(sdsh__pwsg) == 2 else
                    sdsh__pwsg[1:])
                aomc__rjeqt.append(df.data[i])
            if nexxr__ltbvm:
                return DataFrameType(tuple(aomc__rjeqt), df.index, tuple(
                    aktq__lydcv))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        jogx__duyb = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(jogx__duyb)
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
        hhqri__pmrz = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], hhqri__pmrz)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    sfvhk__tgb = builder.module
    nksts__aggp = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    tgfdh__quupv = cgutils.get_or_insert_function(sfvhk__tgb, nksts__aggp,
        name='.dtor.df.{}'.format(df_type))
    if not tgfdh__quupv.is_declaration:
        return tgfdh__quupv
    tgfdh__quupv.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(tgfdh__quupv.append_basic_block())
    djgv__qpjq = tgfdh__quupv.args[0]
    gmpr__byxr = context.get_value_type(payload_type).as_pointer()
    lyb__qee = builder.bitcast(djgv__qpjq, gmpr__byxr)
    payload = context.make_helper(builder, payload_type, ref=lyb__qee)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        dxay__hsoel = context.get_python_api(builder)
        jzw__dmdt = dxay__hsoel.gil_ensure()
        dxay__hsoel.decref(payload.parent)
        dxay__hsoel.gil_release(jzw__dmdt)
    builder.ret_void()
    return tgfdh__quupv


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    vbo__dpq = cgutils.create_struct_proxy(payload_type)(context, builder)
    vbo__dpq.data = data_tup
    vbo__dpq.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        vbo__dpq.columns = colnames
    gyyaa__edfzq = context.get_value_type(payload_type)
    uap__ien = context.get_abi_sizeof(gyyaa__edfzq)
    anwws__bltc = define_df_dtor(context, builder, df_type, payload_type)
    yua__cit = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, uap__ien), anwws__bltc)
    wlwon__hcxqt = context.nrt.meminfo_data(builder, yua__cit)
    bxhbp__yxddw = builder.bitcast(wlwon__hcxqt, gyyaa__edfzq.as_pointer())
    qmrm__wki = cgutils.create_struct_proxy(df_type)(context, builder)
    qmrm__wki.meminfo = yua__cit
    if parent is None:
        qmrm__wki.parent = cgutils.get_null_value(qmrm__wki.parent.type)
    else:
        qmrm__wki.parent = parent
        vbo__dpq.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            dxay__hsoel = context.get_python_api(builder)
            jzw__dmdt = dxay__hsoel.gil_ensure()
            dxay__hsoel.incref(parent)
            dxay__hsoel.gil_release(jzw__dmdt)
    builder.store(vbo__dpq._getvalue(), bxhbp__yxddw)
    return qmrm__wki._getvalue()


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
        mdfyv__xtqz = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        mdfyv__xtqz = [xyu__ujndm for xyu__ujndm in data_typ.dtype.arr_types]
    eowpz__osayg = DataFrameType(tuple(mdfyv__xtqz + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        ijgxj__pysz = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return ijgxj__pysz
    sig = signature(eowpz__osayg, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ=None):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    mygyh__upxwk = len(data_tup_typ.types)
    if mygyh__upxwk == 0:
        ikwnb__hfqt = ()
    elif isinstance(col_names_typ, types.TypeRef):
        ikwnb__hfqt = col_names_typ.instance_type.columns
    else:
        ikwnb__hfqt = get_const_tup_vals(col_names_typ)
    if mygyh__upxwk == 1 and isinstance(data_tup_typ.types[0], TableType):
        mygyh__upxwk = len(data_tup_typ.types[0].arr_types)
    assert len(ikwnb__hfqt
        ) == mygyh__upxwk, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    url__jnlg = data_tup_typ.types
    if mygyh__upxwk != 0 and isinstance(data_tup_typ.types[0], TableType):
        url__jnlg = data_tup_typ.types[0].arr_types
        is_table_format = True
    eowpz__osayg = DataFrameType(url__jnlg, index_typ, ikwnb__hfqt,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            qqq__sqi = cgutils.create_struct_proxy(eowpz__osayg.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = qqq__sqi.parent
        ijgxj__pysz = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return ijgxj__pysz
    sig = signature(eowpz__osayg, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        qmrm__wki = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, qmrm__wki.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        vbo__dpq = get_dataframe_payload(context, builder, df_typ, args[0])
        eqx__axn = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[eqx__axn]
        if df_typ.is_table_format:
            qqq__sqi = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(vbo__dpq.data, 0))
            zdbs__ckc = df_typ.table_type.type_to_blk[arr_typ]
            hpp__ccgwx = getattr(qqq__sqi, f'block_{zdbs__ckc}')
            mmgp__edag = ListInstance(context, builder, types.List(arr_typ),
                hpp__ccgwx)
            etiqk__nmn = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[eqx__axn])
            hhqri__pmrz = mmgp__edag.getitem(etiqk__nmn)
        else:
            hhqri__pmrz = builder.extract_value(vbo__dpq.data, eqx__axn)
        jlkb__fzsg = cgutils.alloca_once_value(builder, hhqri__pmrz)
        wfexz__rouo = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, jlkb__fzsg, wfexz__rouo)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    yua__cit = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, yua__cit)
    gmpr__byxr = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, gmpr__byxr)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    eowpz__osayg = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        eowpz__osayg = types.Tuple([TableType(df_typ.data)])
    sig = signature(eowpz__osayg, df_typ)

    def codegen(context, builder, signature, args):
        vbo__dpq = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            vbo__dpq.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, 'get_dataframe_index')

    def codegen(context, builder, signature, args):
        vbo__dpq = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, vbo__dpq.index
            )
    eowpz__osayg = df_typ.index
    sig = signature(eowpz__osayg, df_typ)
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
        cvxs__mmtst = df.data[i]
        return cvxs__mmtst(*args)


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
        vbo__dpq = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(vbo__dpq.data, 0))
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
    odhp__vbd = self.typemap[data_tup.name]
    if any(is_tuple_like_type(xyu__ujndm) for xyu__ujndm in odhp__vbd.types):
        return None
    if equiv_set.has_shape(data_tup):
        yrsv__tqfu = equiv_set.get_shape(data_tup)
        if len(yrsv__tqfu) > 1:
            equiv_set.insert_equiv(*yrsv__tqfu)
        if len(yrsv__tqfu) > 0:
            popb__idmnw = self.typemap[index.name]
            if not isinstance(popb__idmnw, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(yrsv__tqfu[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(yrsv__tqfu[0], len(
                yrsv__tqfu)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    pmv__wlsdg = args[0]
    dqla__qbyg = self.typemap[pmv__wlsdg.name].data
    if any(is_tuple_like_type(xyu__ujndm) for xyu__ujndm in dqla__qbyg):
        return None
    if equiv_set.has_shape(pmv__wlsdg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            pmv__wlsdg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    pmv__wlsdg = args[0]
    popb__idmnw = self.typemap[pmv__wlsdg.name].index
    if isinstance(popb__idmnw, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(pmv__wlsdg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            pmv__wlsdg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    pmv__wlsdg = args[0]
    if equiv_set.has_shape(pmv__wlsdg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            pmv__wlsdg), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    eqx__axn = get_overload_const_int(c_ind_typ)
    if df_typ.data[eqx__axn] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        egv__atnbs, sir__jpvkx, lbu__zwheb = args
        vbo__dpq = get_dataframe_payload(context, builder, df_typ, egv__atnbs)
        if df_typ.is_table_format:
            qqq__sqi = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(vbo__dpq.data, 0))
            zdbs__ckc = df_typ.table_type.type_to_blk[arr_typ]
            hpp__ccgwx = getattr(qqq__sqi, f'block_{zdbs__ckc}')
            mmgp__edag = ListInstance(context, builder, types.List(arr_typ),
                hpp__ccgwx)
            etiqk__nmn = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[eqx__axn])
            mmgp__edag.setitem(etiqk__nmn, lbu__zwheb, True)
        else:
            hhqri__pmrz = builder.extract_value(vbo__dpq.data, eqx__axn)
            context.nrt.decref(builder, df_typ.data[eqx__axn], hhqri__pmrz)
            vbo__dpq.data = builder.insert_value(vbo__dpq.data, lbu__zwheb,
                eqx__axn)
            context.nrt.incref(builder, arr_typ, lbu__zwheb)
        qmrm__wki = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=egv__atnbs)
        payload_type = DataFramePayloadType(df_typ)
        lyb__qee = context.nrt.meminfo_data(builder, qmrm__wki.meminfo)
        gmpr__byxr = context.get_value_type(payload_type).as_pointer()
        lyb__qee = builder.bitcast(lyb__qee, gmpr__byxr)
        builder.store(vbo__dpq._getvalue(), lyb__qee)
        return impl_ret_borrowed(context, builder, df_typ, egv__atnbs)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        caow__ldbjv = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        clrve__wsfn = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=caow__ldbjv)
        iwnoz__rjczr = get_dataframe_payload(context, builder, df_typ,
            caow__ldbjv)
        qmrm__wki = construct_dataframe(context, builder, signature.
            return_type, iwnoz__rjczr.data, index_val, clrve__wsfn.parent, None
            )
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), iwnoz__rjczr.data)
        return qmrm__wki
    eowpz__osayg = DataFrameType(df_t.data, index_t, df_t.columns, df_t.
        dist, df_t.is_table_format)
    sig = signature(eowpz__osayg, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    mygyh__upxwk = len(df_type.columns)
    fox__omv = mygyh__upxwk
    hqmr__sot = df_type.data
    ikwnb__hfqt = df_type.columns
    index_typ = df_type.index
    jgqfd__yflyg = col_name not in df_type.columns
    eqx__axn = mygyh__upxwk
    if jgqfd__yflyg:
        hqmr__sot += arr_type,
        ikwnb__hfqt += col_name,
        fox__omv += 1
    else:
        eqx__axn = df_type.columns.index(col_name)
        hqmr__sot = tuple(arr_type if i == eqx__axn else hqmr__sot[i] for i in
            range(mygyh__upxwk))

    def codegen(context, builder, signature, args):
        egv__atnbs, sir__jpvkx, lbu__zwheb = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, egv__atnbs)
        geuwi__pgzew = cgutils.create_struct_proxy(df_type)(context,
            builder, value=egv__atnbs)
        if df_type.is_table_format:
            wydig__gjek = df_type.table_type
            sdkb__yoqha = builder.extract_value(in_dataframe_payload.data, 0)
            vlmf__dep = TableType(hqmr__sot)
            ievcz__brvgt = set_table_data_codegen(context, builder,
                wydig__gjek, sdkb__yoqha, vlmf__dep, arr_type, lbu__zwheb,
                eqx__axn, jgqfd__yflyg)
            data_tup = context.make_tuple(builder, types.Tuple([vlmf__dep]),
                [ievcz__brvgt])
        else:
            url__jnlg = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != eqx__axn else lbu__zwheb) for i in range(
                mygyh__upxwk)]
            if jgqfd__yflyg:
                url__jnlg.append(lbu__zwheb)
            for pmv__wlsdg, hdrao__zpbzg in zip(url__jnlg, hqmr__sot):
                context.nrt.incref(builder, hdrao__zpbzg, pmv__wlsdg)
            data_tup = context.make_tuple(builder, types.Tuple(hqmr__sot),
                url__jnlg)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        krly__drlo = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, geuwi__pgzew.parent, None)
        if not jgqfd__yflyg and arr_type == df_type.data[eqx__axn]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            lyb__qee = context.nrt.meminfo_data(builder, geuwi__pgzew.meminfo)
            gmpr__byxr = context.get_value_type(payload_type).as_pointer()
            lyb__qee = builder.bitcast(lyb__qee, gmpr__byxr)
            vdjv__whfe = get_dataframe_payload(context, builder, df_type,
                krly__drlo)
            builder.store(vdjv__whfe._getvalue(), lyb__qee)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, vlmf__dep, builder.
                    extract_value(data_tup, 0))
            else:
                for pmv__wlsdg, hdrao__zpbzg in zip(url__jnlg, hqmr__sot):
                    context.nrt.incref(builder, hdrao__zpbzg, pmv__wlsdg)
        has_parent = cgutils.is_not_null(builder, geuwi__pgzew.parent)
        with builder.if_then(has_parent):
            dxay__hsoel = context.get_python_api(builder)
            jzw__dmdt = dxay__hsoel.gil_ensure()
            vfnk__hipju = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, lbu__zwheb)
            odl__ysyw = numba.core.pythonapi._BoxContext(context, builder,
                dxay__hsoel, vfnk__hipju)
            pvvop__vjd = odl__ysyw.pyapi.from_native_value(arr_type,
                lbu__zwheb, odl__ysyw.env_manager)
            if isinstance(col_name, str):
                ctj__qkha = context.insert_const_string(builder.module,
                    col_name)
                ptd__kgzbl = dxay__hsoel.string_from_string(ctj__qkha)
            else:
                assert isinstance(col_name, int)
                ptd__kgzbl = dxay__hsoel.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            dxay__hsoel.object_setitem(geuwi__pgzew.parent, ptd__kgzbl,
                pvvop__vjd)
            dxay__hsoel.decref(pvvop__vjd)
            dxay__hsoel.decref(ptd__kgzbl)
            dxay__hsoel.gil_release(jzw__dmdt)
        return krly__drlo
    eowpz__osayg = DataFrameType(hqmr__sot, index_typ, ikwnb__hfqt, df_type
        .dist, df_type.is_table_format)
    sig = signature(eowpz__osayg, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    mygyh__upxwk = len(pyval.columns)
    url__jnlg = tuple(pyval.iloc[:, i].values for i in range(mygyh__upxwk))
    if df_type.is_table_format:
        qqq__sqi = context.get_constant_generic(builder, df_type.table_type,
            Table(url__jnlg))
        data_tup = lir.Constant.literal_struct([qqq__sqi])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], sdsh__pwsg) for 
            i, sdsh__pwsg in enumerate(url__jnlg)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    qkpuc__bqmsf = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, qkpuc__bqmsf])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    wwegu__mkcp = context.get_constant(types.int64, -1)
    wvy__mqmnd = context.get_constant_null(types.voidptr)
    yua__cit = lir.Constant.literal_struct([wwegu__mkcp, wvy__mqmnd,
        wvy__mqmnd, payload, wwegu__mkcp])
    yua__cit = cgutils.global_constant(builder, '.const.meminfo', yua__cit
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([yua__cit, qkpuc__bqmsf])


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
        zodg__woqk = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        zodg__woqk = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, zodg__woqk)
    if fromty.is_table_format == toty.is_table_format:
        aomc__rjeqt = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                aomc__rjeqt)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), aomc__rjeqt)
    elif toty.is_table_format:
        aomc__rjeqt = _cast_df_data_to_table_format(context, builder,
            fromty, toty, in_dataframe_payload)
    else:
        aomc__rjeqt = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, aomc__rjeqt,
        zodg__woqk, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    paby__wwqm = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        alfok__xikrf = get_index_data_arr_types(toty.index)[0]
        bwtah__byctz = bodo.utils.transform.get_type_alloc_counts(alfok__xikrf
            ) - 1
        ann__wjkno = ', '.join('0' for sir__jpvkx in range(bwtah__byctz))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(ann__wjkno, ', ' if bwtah__byctz == 1 else ''))
        paby__wwqm['index_arr_type'] = alfok__xikrf
    ennd__vqn = []
    for i, arr_typ in enumerate(toty.data):
        bwtah__byctz = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        ann__wjkno = ', '.join('0' for sir__jpvkx in range(bwtah__byctz))
        gti__cebx = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, ann__wjkno, ', ' if bwtah__byctz == 1 else ''))
        ennd__vqn.append(gti__cebx)
        paby__wwqm[f'arr_type{i}'] = arr_typ
    ennd__vqn = ', '.join(ennd__vqn)
    vijy__pwpaw = 'def impl():\n'
    nay__cmnxv = bodo.hiframes.dataframe_impl._gen_init_df(vijy__pwpaw,
        toty.columns, ennd__vqn, index, paby__wwqm)
    df = context.compile_internal(builder, nay__cmnxv, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    zoi__lfc = toty.table_type
    qqq__sqi = cgutils.create_struct_proxy(zoi__lfc)(context, builder)
    qqq__sqi.parent = in_dataframe_payload.parent
    for xyu__ujndm, zdbs__ckc in zoi__lfc.type_to_blk.items():
        hbpa__idr = context.get_constant(types.int64, len(zoi__lfc.
            block_to_arr_ind[zdbs__ckc]))
        sir__jpvkx, hlc__smy = ListInstance.allocate_ex(context, builder,
            types.List(xyu__ujndm), hbpa__idr)
        hlc__smy.size = hbpa__idr
        setattr(qqq__sqi, f'block_{zdbs__ckc}', hlc__smy.value)
    for i, xyu__ujndm in enumerate(fromty.data):
        hhqri__pmrz = builder.extract_value(in_dataframe_payload.data, i)
        zdbs__ckc = zoi__lfc.type_to_blk[xyu__ujndm]
        hpp__ccgwx = getattr(qqq__sqi, f'block_{zdbs__ckc}')
        mmgp__edag = ListInstance(context, builder, types.List(xyu__ujndm),
            hpp__ccgwx)
        etiqk__nmn = context.get_constant(types.int64, zoi__lfc.
            block_offsets[i])
        mmgp__edag.setitem(etiqk__nmn, hhqri__pmrz, True)
    data_tup = context.make_tuple(builder, types.Tuple([zoi__lfc]), [
        qqq__sqi._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    zoi__lfc = fromty.table_type
    qqq__sqi = cgutils.create_struct_proxy(zoi__lfc)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    url__jnlg = []
    for i, xyu__ujndm in enumerate(toty.data):
        zdbs__ckc = zoi__lfc.type_to_blk[xyu__ujndm]
        hpp__ccgwx = getattr(qqq__sqi, f'block_{zdbs__ckc}')
        mmgp__edag = ListInstance(context, builder, types.List(xyu__ujndm),
            hpp__ccgwx)
        etiqk__nmn = context.get_constant(types.int64, zoi__lfc.
            block_offsets[i])
        hhqri__pmrz = mmgp__edag.getitem(etiqk__nmn)
        context.nrt.incref(builder, xyu__ujndm, hhqri__pmrz)
        url__jnlg.append(hhqri__pmrz)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), url__jnlg)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    xrton__uup, ennd__vqn, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    aaoz__bcmso = gen_const_tup(xrton__uup)
    vijy__pwpaw = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    vijy__pwpaw += (
        '  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, {})\n'
        .format(ennd__vqn, index_arg, aaoz__bcmso))
    iqjh__yplmn = {}
    exec(vijy__pwpaw, {'bodo': bodo, 'np': np}, iqjh__yplmn)
    xao__hvn = iqjh__yplmn['_init_df']
    return xao__hvn


def _get_df_args(data, index, columns, dtype, copy):
    edd__ykpcw = ''
    if not is_overload_none(dtype):
        edd__ykpcw = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        mygyh__upxwk = (len(data.types) - 1) // 2
        czk__wqwlr = [xyu__ujndm.literal_value for xyu__ujndm in data.types
            [1:mygyh__upxwk + 1]]
        data_val_types = dict(zip(czk__wqwlr, data.types[mygyh__upxwk + 1:]))
        url__jnlg = ['data[{}]'.format(i) for i in range(mygyh__upxwk + 1, 
            2 * mygyh__upxwk + 1)]
        data_dict = dict(zip(czk__wqwlr, url__jnlg))
        if is_overload_none(index):
            for i, xyu__ujndm in enumerate(data.types[mygyh__upxwk + 1:]):
                if isinstance(xyu__ujndm, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(mygyh__upxwk + 1 + i))
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
        cfvlv__nrxu = '.copy()' if copy else ''
        srlc__qvj = get_overload_const_list(columns)
        mygyh__upxwk = len(srlc__qvj)
        data_val_types = {odl__ysyw: data.copy(ndim=1) for odl__ysyw in
            srlc__qvj}
        url__jnlg = ['data[:,{}]{}'.format(i, cfvlv__nrxu) for i in range(
            mygyh__upxwk)]
        data_dict = dict(zip(srlc__qvj, url__jnlg))
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
    ennd__vqn = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[odl__ysyw], df_len, edd__ykpcw) for odl__ysyw in
        col_names))
    if len(col_names) == 0:
        ennd__vqn = '()'
    return col_names, ennd__vqn, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for odl__ysyw in col_names:
        if odl__ysyw in data_dict and is_iterable_type(data_val_types[
            odl__ysyw]):
            df_len = 'len({})'.format(data_dict[odl__ysyw])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(odl__ysyw in data_dict for odl__ysyw in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    ssfbl__mtth = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for odl__ysyw in col_names:
        if odl__ysyw not in data_dict:
            data_dict[odl__ysyw] = ssfbl__mtth


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
            xyu__ujndm = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(xyu__ujndm)
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
        zkq__ebhe = idx.literal_value
        if isinstance(zkq__ebhe, int):
            cvxs__mmtst = tup.types[zkq__ebhe]
        elif isinstance(zkq__ebhe, slice):
            cvxs__mmtst = types.BaseTuple.from_types(tup.types[zkq__ebhe])
        return signature(cvxs__mmtst, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    eovc__xfl, idx = sig.args
    idx = idx.literal_value
    tup, sir__jpvkx = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(eovc__xfl)
        if not 0 <= idx < len(eovc__xfl):
            raise IndexError('cannot index at %d in %s' % (idx, eovc__xfl))
        igzo__dwbzq = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        whmt__gej = cgutils.unpack_tuple(builder, tup)[idx]
        igzo__dwbzq = context.make_tuple(builder, sig.return_type, whmt__gej)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, igzo__dwbzq)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, qoxvo__tpy, suffix_x,
            suffix_y, is_join, indicator, _bodo_na_equal, qujb__uxo) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        mpbj__qurz = set(left_on) & set(right_on)
        dplh__lvzrj = set(left_df.columns) & set(right_df.columns)
        xibb__jorx = dplh__lvzrj - mpbj__qurz
        xdkf__qfrey = '$_bodo_index_' in left_on
        eak__kwro = '$_bodo_index_' in right_on
        how = get_overload_const_str(qoxvo__tpy)
        cjxz__alw = how in {'left', 'outer'}
        qbknl__gklbl = how in {'right', 'outer'}
        columns = []
        data = []
        if xdkf__qfrey and not eak__kwro and not is_join.literal_value:
            sea__vumh = right_on[0]
            if sea__vumh in left_df.columns:
                columns.append(sea__vumh)
                data.append(right_df.data[right_df.columns.index(sea__vumh)])
        if eak__kwro and not xdkf__qfrey and not is_join.literal_value:
            yekkc__xqipx = left_on[0]
            if yekkc__xqipx in right_df.columns:
                columns.append(yekkc__xqipx)
                data.append(left_df.data[left_df.columns.index(yekkc__xqipx)])
        for xbe__mkw, clexr__semq in zip(left_df.data, left_df.columns):
            columns.append(str(clexr__semq) + suffix_x.literal_value if 
                clexr__semq in xibb__jorx else clexr__semq)
            if clexr__semq in mpbj__qurz:
                data.append(xbe__mkw)
            else:
                data.append(to_nullable_type(xbe__mkw) if qbknl__gklbl else
                    xbe__mkw)
        for xbe__mkw, clexr__semq in zip(right_df.data, right_df.columns):
            if clexr__semq not in mpbj__qurz:
                columns.append(str(clexr__semq) + suffix_y.literal_value if
                    clexr__semq in xibb__jorx else clexr__semq)
                data.append(to_nullable_type(xbe__mkw) if cjxz__alw else
                    xbe__mkw)
        pdut__feopa = get_overload_const_bool(indicator)
        if pdut__feopa:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        if xdkf__qfrey and eak__kwro and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif xdkf__qfrey and not eak__kwro:
            index_typ = right_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif eak__kwro and not xdkf__qfrey:
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        byfpx__sie = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(byfpx__sie, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    qmrm__wki = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return qmrm__wki._getvalue()


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
    kim__vxejo = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    uevc__lrr = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', kim__vxejo, uevc__lrr,
        package_name='pandas', module_name='General')
    vijy__pwpaw = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        uqg__rfe = 0
        ennd__vqn = []
        names = []
        for i, jpw__njr in enumerate(objs.types):
            assert isinstance(jpw__njr, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(jpw__njr, 'pd.concat()')
            if isinstance(jpw__njr, SeriesType):
                names.append(str(uqg__rfe))
                uqg__rfe += 1
                ennd__vqn.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(jpw__njr.columns)
                for ywqd__rix in range(len(jpw__njr.data)):
                    ennd__vqn.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, ywqd__rix))
        return bodo.hiframes.dataframe_impl._gen_init_df(vijy__pwpaw, names,
            ', '.join(ennd__vqn), index)
    assert axis == 0
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(xyu__ujndm, DataFrameType) for xyu__ujndm in
            objs.types)
        sds__hch = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pd.concat()')
            sds__hch.extend(df.columns)
        sds__hch = list(dict.fromkeys(sds__hch).keys())
        mdfyv__xtqz = {}
        for uqg__rfe, odl__ysyw in enumerate(sds__hch):
            for df in objs.types:
                if odl__ysyw in df.columns:
                    mdfyv__xtqz['arr_typ{}'.format(uqg__rfe)] = df.data[df.
                        columns.index(odl__ysyw)]
                    break
        assert len(mdfyv__xtqz) == len(sds__hch)
        bphmy__wfwy = []
        for uqg__rfe, odl__ysyw in enumerate(sds__hch):
            args = []
            for i, df in enumerate(objs.types):
                if odl__ysyw in df.columns:
                    eqx__axn = df.columns.index(odl__ysyw)
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, eqx__axn))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, uqg__rfe))
            vijy__pwpaw += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(uqg__rfe, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(vijy__pwpaw,
            sds__hch, ', '.join('A{}'.format(i) for i in range(len(sds__hch
            ))), index, mdfyv__xtqz)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(xyu__ujndm, SeriesType) for xyu__ujndm in
            objs.types)
        vijy__pwpaw += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            vijy__pwpaw += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            vijy__pwpaw += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        vijy__pwpaw += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        iqjh__yplmn = {}
        exec(vijy__pwpaw, {'bodo': bodo, 'np': np, 'numba': numba}, iqjh__yplmn
            )
        return iqjh__yplmn['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pd.concat()')
        df_type = objs.dtype
        for uqg__rfe, odl__ysyw in enumerate(df_type.columns):
            vijy__pwpaw += '  arrs{} = []\n'.format(uqg__rfe)
            vijy__pwpaw += '  for i in range(len(objs)):\n'
            vijy__pwpaw += '    df = objs[i]\n'
            vijy__pwpaw += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(uqg__rfe))
            vijy__pwpaw += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(uqg__rfe))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            vijy__pwpaw += '  arrs_index = []\n'
            vijy__pwpaw += '  for i in range(len(objs)):\n'
            vijy__pwpaw += '    df = objs[i]\n'
            vijy__pwpaw += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(vijy__pwpaw,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        vijy__pwpaw += '  arrs = []\n'
        vijy__pwpaw += '  for i in range(len(objs)):\n'
        vijy__pwpaw += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        vijy__pwpaw += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            vijy__pwpaw += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            vijy__pwpaw += '  arrs_index = []\n'
            vijy__pwpaw += '  for i in range(len(objs)):\n'
            vijy__pwpaw += '    S = objs[i]\n'
            vijy__pwpaw += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            vijy__pwpaw += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        vijy__pwpaw += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        iqjh__yplmn = {}
        exec(vijy__pwpaw, {'bodo': bodo, 'np': np, 'numba': numba}, iqjh__yplmn
            )
        return iqjh__yplmn['impl']
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
        eowpz__osayg = df.copy(index=index, is_table_format=False)
        return signature(eowpz__osayg, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    vriw__zlsu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return vriw__zlsu._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    kim__vxejo = dict(index=index, name=name)
    uevc__lrr = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', kim__vxejo, uevc__lrr,
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
        mdfyv__xtqz = (types.Array(types.int64, 1, 'C'),) + df.data
        dzqw__nyqhb = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, mdfyv__xtqz)
        return signature(dzqw__nyqhb, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    vriw__zlsu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return vriw__zlsu._getvalue()


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
    vriw__zlsu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return vriw__zlsu._getvalue()


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
    vriw__zlsu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return vriw__zlsu._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True, parallel
    =False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    mqun__vlezz = get_overload_const_bool(check_duplicates)
    xfahb__cluvz = not is_overload_none(value_names)
    mbyfk__jla = isinstance(values_tup, types.UniTuple)
    if mbyfk__jla:
        srndf__evx = [to_nullable_type(values_tup.dtype)]
    else:
        srndf__evx = [to_nullable_type(hdrao__zpbzg) for hdrao__zpbzg in
            values_tup]
    vijy__pwpaw = 'def impl(\n'
    vijy__pwpaw += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, parallel=False
"""
    vijy__pwpaw += '):\n'
    vijy__pwpaw += '    if parallel:\n'
    xdk__ell = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    vijy__pwpaw += f'        info_list = [{xdk__ell}]\n'
    vijy__pwpaw += '        cpp_table = arr_info_list_to_table(info_list)\n'
    vijy__pwpaw += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    mwpcy__ppoeh = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    twugq__rezt = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    askq__tqcy = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    vijy__pwpaw += f'        index_tup = ({mwpcy__ppoeh},)\n'
    vijy__pwpaw += f'        columns_tup = ({twugq__rezt},)\n'
    vijy__pwpaw += f'        values_tup = ({askq__tqcy},)\n'
    vijy__pwpaw += '        delete_table(cpp_table)\n'
    vijy__pwpaw += '        delete_table(out_cpp_table)\n'
    vijy__pwpaw += '    columns_arr = columns_tup[0]\n'
    if mbyfk__jla:
        vijy__pwpaw += '    values_arrs = [arr for arr in values_tup]\n'
    vijy__pwpaw += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    vijy__pwpaw += '        index_tup\n'
    vijy__pwpaw += '    )\n'
    vijy__pwpaw += '    n_rows = len(unique_index_arr_tup[0])\n'
    vijy__pwpaw += '    num_values_arrays = len(values_tup)\n'
    vijy__pwpaw += '    n_unique_pivots = len(pivot_values)\n'
    if mbyfk__jla:
        vijy__pwpaw += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        vijy__pwpaw += '    n_cols = n_unique_pivots\n'
    vijy__pwpaw += '    col_map = {}\n'
    vijy__pwpaw += '    for i in range(n_unique_pivots):\n'
    vijy__pwpaw += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    vijy__pwpaw += '            raise ValueError(\n'
    vijy__pwpaw += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    vijy__pwpaw += '            )\n'
    vijy__pwpaw += '        col_map[pivot_values[i]] = i\n'
    pwt__ohu = False
    for i, clq__sgu in enumerate(srndf__evx):
        if clq__sgu == bodo.string_array_type:
            pwt__ohu = True
            vijy__pwpaw += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            vijy__pwpaw += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if pwt__ohu:
        if mqun__vlezz:
            vijy__pwpaw += '    nbytes = (n_rows + 7) >> 3\n'
            vijy__pwpaw += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        vijy__pwpaw += '    for i in range(len(columns_arr)):\n'
        vijy__pwpaw += '        col_name = columns_arr[i]\n'
        vijy__pwpaw += '        pivot_idx = col_map[col_name]\n'
        vijy__pwpaw += '        row_idx = row_vector[i]\n'
        if mqun__vlezz:
            vijy__pwpaw += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            vijy__pwpaw += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            vijy__pwpaw += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            vijy__pwpaw += '        else:\n'
            vijy__pwpaw += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if mbyfk__jla:
            vijy__pwpaw += '        for j in range(num_values_arrays):\n'
            vijy__pwpaw += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            vijy__pwpaw += '            len_arr = len_arrs_0[col_idx]\n'
            vijy__pwpaw += '            values_arr = values_arrs[j]\n'
            vijy__pwpaw += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            vijy__pwpaw += (
                '                len_arr[row_idx] = len(values_arr[i])\n')
            vijy__pwpaw += (
                '                total_lens_0[col_idx] += len(values_arr[i])\n'
                )
        else:
            for i, clq__sgu in enumerate(srndf__evx):
                if clq__sgu == bodo.string_array_type:
                    vijy__pwpaw += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    vijy__pwpaw += f"""            len_arrs_{i}[pivot_idx][row_idx] = len(values_tup[{i}][i])
"""
                    vijy__pwpaw += f"""            total_lens_{i}[pivot_idx] += len(values_tup[{i}][i])
"""
    for i, clq__sgu in enumerate(srndf__evx):
        if clq__sgu == bodo.string_array_type:
            vijy__pwpaw += f'    data_arrs_{i} = [\n'
            vijy__pwpaw += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            vijy__pwpaw += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            vijy__pwpaw += '        )\n'
            vijy__pwpaw += '        for i in range(n_cols)\n'
            vijy__pwpaw += '    ]\n'
        else:
            vijy__pwpaw += f'    data_arrs_{i} = [\n'
            vijy__pwpaw += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            vijy__pwpaw += '        for _ in range(n_cols)\n'
            vijy__pwpaw += '    ]\n'
    if not pwt__ohu and mqun__vlezz:
        vijy__pwpaw += '    nbytes = (n_rows + 7) >> 3\n'
        vijy__pwpaw += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    vijy__pwpaw += '    for i in range(len(columns_arr)):\n'
    vijy__pwpaw += '        col_name = columns_arr[i]\n'
    vijy__pwpaw += '        pivot_idx = col_map[col_name]\n'
    vijy__pwpaw += '        row_idx = row_vector[i]\n'
    if not pwt__ohu and mqun__vlezz:
        vijy__pwpaw += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        vijy__pwpaw += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        vijy__pwpaw += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        vijy__pwpaw += '        else:\n'
        vijy__pwpaw += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if mbyfk__jla:
        vijy__pwpaw += '        for j in range(num_values_arrays):\n'
        vijy__pwpaw += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        vijy__pwpaw += '            col_arr = data_arrs_0[col_idx]\n'
        vijy__pwpaw += '            values_arr = values_arrs[j]\n'
        vijy__pwpaw += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        vijy__pwpaw += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        vijy__pwpaw += '            else:\n'
        vijy__pwpaw += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, clq__sgu in enumerate(srndf__evx):
            vijy__pwpaw += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            vijy__pwpaw += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            vijy__pwpaw += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            vijy__pwpaw += f'        else:\n'
            vijy__pwpaw += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_tup) == 1:
        vijy__pwpaw += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names[0])
"""
    else:
        vijy__pwpaw += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names, None)
"""
    if xfahb__cluvz:
        vijy__pwpaw += '    num_rows = len(value_names) * len(pivot_values)\n'
        if value_names == bodo.string_array_type:
            vijy__pwpaw += '    total_chars = 0\n'
            vijy__pwpaw += '    for i in range(len(value_names)):\n'
            vijy__pwpaw += '        total_chars += len(value_names[i])\n'
            vijy__pwpaw += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
        else:
            vijy__pwpaw += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names, (-1,))
"""
        if pivot_values == bodo.string_array_type:
            vijy__pwpaw += '    total_chars = 0\n'
            vijy__pwpaw += '    for i in range(len(pivot_values)):\n'
            vijy__pwpaw += '        total_chars += len(pivot_values[i])\n'
            vijy__pwpaw += """    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(value_names))
"""
        else:
            vijy__pwpaw += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
        vijy__pwpaw += '    for i in range(len(value_names)):\n'
        vijy__pwpaw += '        for j in range(len(pivot_values)):\n'
        vijy__pwpaw += """            new_value_names[(i * len(pivot_values)) + j] = value_names[i]
"""
        vijy__pwpaw += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
        vijy__pwpaw += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name), None)
"""
    else:
        vijy__pwpaw += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name)
"""
    gjc__jaomq = ', '.join(f'data_arrs_{i}' for i in range(len(srndf__evx)))
    vijy__pwpaw += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({gjc__jaomq},), n_rows)
"""
    vijy__pwpaw += (
        '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
        )
    vijy__pwpaw += '        (table,), index, column_index\n'
    vijy__pwpaw += '    )\n'
    iqjh__yplmn = {}
    gzlb__eirq = {f'data_arr_typ_{i}': clq__sgu for i, clq__sgu in
        enumerate(srndf__evx)}
    reeid__aens = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, **gzlb__eirq}
    exec(vijy__pwpaw, reeid__aens, iqjh__yplmn)
    impl = iqjh__yplmn['impl']
    return impl


def gen_pandas_parquet_metadata(df, write_non_range_index_to_metadata,
    write_rangeindex_to_metadata, partition_cols=None):
    abx__uct = {}
    abx__uct['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, axdvu__kliq in zip(df.columns, df.data):
        if col_name in partition_cols:
            continue
        if isinstance(axdvu__kliq, types.Array
            ) or axdvu__kliq == boolean_array:
            vfzt__syuwt = sbmn__aokr = axdvu__kliq.dtype.name
            if sbmn__aokr.startswith('datetime'):
                vfzt__syuwt = 'datetime'
        elif axdvu__kliq == string_array_type:
            vfzt__syuwt = 'unicode'
            sbmn__aokr = 'object'
        elif axdvu__kliq == binary_array_type:
            vfzt__syuwt = 'bytes'
            sbmn__aokr = 'object'
        elif isinstance(axdvu__kliq, DecimalArrayType):
            vfzt__syuwt = sbmn__aokr = 'object'
        elif isinstance(axdvu__kliq, IntegerArrayType):
            bwks__dmv = axdvu__kliq.dtype.name
            if bwks__dmv.startswith('int'):
                vfzt__syuwt = 'Int' + bwks__dmv[3:]
            elif bwks__dmv.startswith('uint'):
                vfzt__syuwt = 'UInt' + bwks__dmv[4:]
            else:
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, axdvu__kliq))
            sbmn__aokr = axdvu__kliq.dtype.name
        elif axdvu__kliq == datetime_date_array_type:
            vfzt__syuwt = 'datetime'
            sbmn__aokr = 'object'
        elif isinstance(axdvu__kliq, (StructArrayType, ArrayItemArrayType)):
            vfzt__syuwt = 'object'
            sbmn__aokr = 'object'
        else:
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, axdvu__kliq))
        tfkjo__jjhu = {'name': col_name, 'field_name': col_name,
            'pandas_type': vfzt__syuwt, 'numpy_type': sbmn__aokr,
            'metadata': None}
        abx__uct['columns'].append(tfkjo__jjhu)
    if write_non_range_index_to_metadata:
        if isinstance(df.index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in df.index.name:
            wnvf__sal = '__index_level_0__'
            nec__oay = None
        else:
            wnvf__sal = '%s'
            nec__oay = '%s'
        abx__uct['index_columns'] = [wnvf__sal]
        abx__uct['columns'].append({'name': nec__oay, 'field_name':
            wnvf__sal, 'pandas_type': df.index.pandas_type_name,
            'numpy_type': df.index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        abx__uct['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        abx__uct['index_columns'] = []
    abx__uct['pandas_version'] = pd.__version__
    return abx__uct


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
        kcp__cwbjg = []
        for ajfnr__mivj in partition_cols:
            try:
                idx = df.columns.index(ajfnr__mivj)
            except ValueError as xvxb__sbso:
                raise BodoError(
                    f'Partition column {ajfnr__mivj} is not in dataframe')
            kcp__cwbjg.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    maxe__bwgu = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    kucgy__sxxle = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not maxe__bwgu)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not maxe__bwgu or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and maxe__bwgu and not is_overload_true(_is_parallel)
    tqzjx__dwo = json.dumps(gen_pandas_parquet_metadata(df,
        write_non_range_index_to_metadata, write_rangeindex_to_metadata,
        partition_cols=partition_cols))
    if not is_overload_true(_is_parallel) and maxe__bwgu:
        tqzjx__dwo = tqzjx__dwo.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            tqzjx__dwo = tqzjx__dwo.replace('"%s"', '%s')
    ennd__vqn = ', '.join(
        'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(len(df.columns)))
    vijy__pwpaw = """def df_to_parquet(df, fname, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, _is_parallel=False):
"""
    if df.is_table_format:
        vijy__pwpaw += (
            '    table = py_table_to_cpp_table(get_dataframe_table(df), py_table_typ)\n'
            )
    else:
        vijy__pwpaw += '    info_list = [{}]\n'.format(ennd__vqn)
        vijy__pwpaw += '    table = arr_info_list_to_table(info_list)\n'
    vijy__pwpaw += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and kucgy__sxxle:
        vijy__pwpaw += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        yrte__gke = True
    else:
        vijy__pwpaw += '    index_col = array_to_info(np.empty(0))\n'
        yrte__gke = False
    vijy__pwpaw += '    metadata = """' + tqzjx__dwo + '"""\n'
    vijy__pwpaw += '    if compression is None:\n'
    vijy__pwpaw += "        compression = 'none'\n"
    vijy__pwpaw += '    if df.index.name is not None:\n'
    vijy__pwpaw += '        name_ptr = df.index.name\n'
    vijy__pwpaw += '    else:\n'
    vijy__pwpaw += "        name_ptr = 'null'\n"
    vijy__pwpaw += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel=_is_parallel)
"""
    aug__ucjy = None
    if partition_cols:
        aug__ucjy = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        kbalw__qvobt = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in kcp__cwbjg)
        if kbalw__qvobt:
            vijy__pwpaw += '    cat_info_list = [{}]\n'.format(kbalw__qvobt)
            vijy__pwpaw += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            vijy__pwpaw += '    cat_table = table\n'
        vijy__pwpaw += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        vijy__pwpaw += (
            f'    part_cols_idxs = np.array({kcp__cwbjg}, dtype=np.int32)\n')
        vijy__pwpaw += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(fname),\n'
            )
        vijy__pwpaw += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        vijy__pwpaw += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        vijy__pwpaw += (
            '                            unicode_to_utf8(compression),\n')
        vijy__pwpaw += '                            _is_parallel,\n'
        vijy__pwpaw += (
            '                            unicode_to_utf8(bucket_region))\n')
        vijy__pwpaw += '    delete_table_decref_arrays(table)\n'
        vijy__pwpaw += '    delete_info_decref_array(index_col)\n'
        vijy__pwpaw += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        vijy__pwpaw += '    delete_info_decref_array(col_names)\n'
        if kbalw__qvobt:
            vijy__pwpaw += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        vijy__pwpaw += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        vijy__pwpaw += (
            '                            table, col_names, index_col,\n')
        vijy__pwpaw += '                            ' + str(yrte__gke) + ',\n'
        vijy__pwpaw += (
            '                            unicode_to_utf8(metadata),\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(compression),\n')
        vijy__pwpaw += (
            '                            _is_parallel, 1, df.index.start,\n')
        vijy__pwpaw += (
            '                            df.index.stop, df.index.step,\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(name_ptr),\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(bucket_region))\n')
        vijy__pwpaw += '    delete_table_decref_arrays(table)\n'
        vijy__pwpaw += '    delete_info_decref_array(index_col)\n'
        vijy__pwpaw += '    delete_info_decref_array(col_names)\n'
    else:
        vijy__pwpaw += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        vijy__pwpaw += (
            '                            table, col_names, index_col,\n')
        vijy__pwpaw += '                            ' + str(yrte__gke) + ',\n'
        vijy__pwpaw += (
            '                            unicode_to_utf8(metadata),\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(compression),\n')
        vijy__pwpaw += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(name_ptr),\n')
        vijy__pwpaw += (
            '                            unicode_to_utf8(bucket_region))\n')
        vijy__pwpaw += '    delete_table_decref_arrays(table)\n'
        vijy__pwpaw += '    delete_info_decref_array(index_col)\n'
        vijy__pwpaw += '    delete_info_decref_array(col_names)\n'
    iqjh__yplmn = {}
    exec(vijy__pwpaw, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
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
        'col_names_no_parts_arr': aug__ucjy}, iqjh__yplmn)
    jiyl__zegc = iqjh__yplmn['df_to_parquet']
    return jiyl__zegc


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    zrqlb__ddycb = 'all_ok'
    lwgnb__cvu = urlparse(con).scheme
    if _is_parallel and bodo.get_rank() == 0:
        rml__omf = 100
        if chunksize is None:
            cqaa__mqbxa = rml__omf
        else:
            cqaa__mqbxa = min(chunksize, rml__omf)
        if _is_table_create:
            df = df.iloc[:cqaa__mqbxa, :]
        else:
            df = df.iloc[cqaa__mqbxa:, :]
            if len(df) == 0:
                return zrqlb__ddycb
    if lwgnb__cvu == 'snowflake':
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
            df.columns = [(odl__ysyw.upper() if odl__ysyw.islower() else
                odl__ysyw) for odl__ysyw in df.columns]
        except ImportError as xvxb__sbso:
            zrqlb__ddycb = (
                "Snowflake Python connector not found. It can be installed by calling 'conda install -c conda-forge snowflake-connector-python' or 'pip install snowflake-connector-python'."
                )
            return zrqlb__ddycb
    try:
        df.to_sql(name, con, schema, if_exists, index, index_label,
            chunksize, dtype, method)
    except Exception as uuif__lsrlz:
        zrqlb__ddycb = uuif__lsrlz.args[0]
    return zrqlb__ddycb


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
    kim__vxejo = dict(chunksize=chunksize)
    uevc__lrr = dict(chunksize=None)
    check_unsupported_args('to_sql', kim__vxejo, uevc__lrr, package_name=
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
        dcunh__yyp = bodo.libs.distributed_api.get_rank()
        zrqlb__ddycb = 'unset'
        if dcunh__yyp != 0:
            zrqlb__ddycb = bcast_scalar(zrqlb__ddycb)
        elif dcunh__yyp == 0:
            zrqlb__ddycb = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, True, _is_parallel)
            zrqlb__ddycb = bcast_scalar(zrqlb__ddycb)
        if_exists = 'append'
        if _is_parallel and zrqlb__ddycb == 'all_ok':
            zrqlb__ddycb = to_sql_exception_guard_encaps(df, name, con,
                schema, if_exists, index, index_label, chunksize, dtype,
                method, False, _is_parallel)
        if zrqlb__ddycb != 'all_ok':
            print('err_msg=', zrqlb__ddycb)
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
        xxysy__zuzug = get_overload_const_str(path_or_buf)
        if xxysy__zuzug.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        shna__cfg = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(shna__cfg))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(shna__cfg))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    tomdy__fpx = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    myf__dcp = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', tomdy__fpx, myf__dcp,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    vijy__pwpaw = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        xcib__tzyj = data.data.dtype.categories
        vijy__pwpaw += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        xcib__tzyj = data.dtype.categories
        vijy__pwpaw += '  data_values = data\n'
    mygyh__upxwk = len(xcib__tzyj)
    vijy__pwpaw += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    vijy__pwpaw += '  numba.parfors.parfor.init_prange()\n'
    vijy__pwpaw += '  n = len(data_values)\n'
    for i in range(mygyh__upxwk):
        vijy__pwpaw += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    vijy__pwpaw += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    vijy__pwpaw += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for ywqd__rix in range(mygyh__upxwk):
        vijy__pwpaw += '          data_arr_{}[i] = 0\n'.format(ywqd__rix)
    vijy__pwpaw += '      else:\n'
    for jkoyz__fphp in range(mygyh__upxwk):
        vijy__pwpaw += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            jkoyz__fphp)
    ennd__vqn = ', '.join(f'data_arr_{i}' for i in range(mygyh__upxwk))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(xcib__tzyj[0], np.datetime64):
        xcib__tzyj = tuple(pd.Timestamp(odl__ysyw) for odl__ysyw in xcib__tzyj)
    elif isinstance(xcib__tzyj[0], np.timedelta64):
        xcib__tzyj = tuple(pd.Timedelta(odl__ysyw) for odl__ysyw in xcib__tzyj)
    return bodo.hiframes.dataframe_impl._gen_init_df(vijy__pwpaw,
        xcib__tzyj, ennd__vqn, index)


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
    for soh__laf in pd_unsupported:
        fname = mod_name + '.' + soh__laf.__name__
        overload(soh__laf, no_unliteral=True)(create_unsupported_overload(
            fname))


def _install_dataframe_unsupported():
    for ghe__cepui in dataframe_unsupported_attrs:
        rspdo__xavw = 'DataFrame.' + ghe__cepui
        overload_attribute(DataFrameType, ghe__cepui)(
            create_unsupported_overload(rspdo__xavw))
    for fname in dataframe_unsupported:
        rspdo__xavw = 'DataFrame.' + fname + '()'
        overload_method(DataFrameType, fname)(create_unsupported_overload(
            rspdo__xavw))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
