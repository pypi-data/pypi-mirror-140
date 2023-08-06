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
            idlc__yko = f'{len(self.data)} columns of types {set(self.data)}'
            keyl__top = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({idlc__yko}, {self.index}, {keyl__top}, {self.dist}, {self.is_table_format})'
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
            mvcw__iqj = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(rugm__hxcqb.unify(typingctx, hhyer__hihw) if 
                rugm__hxcqb != hhyer__hihw else rugm__hxcqb for rugm__hxcqb,
                hhyer__hihw in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if mvcw__iqj is not None and None not in data:
                return DataFrameType(data, mvcw__iqj, self.columns, dist,
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
        return all(rugm__hxcqb.is_precise() for rugm__hxcqb in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        sij__zfkhx = self.columns.index(col_name)
        zwrjv__gehvx = tuple(list(self.data[:sij__zfkhx]) + [new_type] +
            list(self.data[sij__zfkhx + 1:]))
        return DataFrameType(zwrjv__gehvx, self.index, self.columns, self.
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
        hacc__cmsjn = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            hacc__cmsjn.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, hacc__cmsjn)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        hacc__cmsjn = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, hacc__cmsjn)


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
        gie__eew = 'n',
        jzi__mmc = {'n': 5}
        jhvmo__cfekb, kzg__lobf = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, gie__eew, jzi__mmc)
        oihh__rgyn = kzg__lobf[0]
        if not is_overload_int(oihh__rgyn):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        rsv__bpvrd = df.copy(is_table_format=False)
        return rsv__bpvrd(*kzg__lobf).replace(pysig=jhvmo__cfekb)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ure__qas = (df,) + args
        gie__eew = 'df', 'method', 'min_periods'
        jzi__mmc = {'method': 'pearson', 'min_periods': 1}
        zoq__dhps = 'method',
        jhvmo__cfekb, kzg__lobf = bodo.utils.typing.fold_typing_args(func_name,
            ure__qas, kws, gie__eew, jzi__mmc, zoq__dhps)
        exkw__mitg = kzg__lobf[2]
        if not is_overload_int(exkw__mitg):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        crm__elzu = []
        whitc__obqwk = []
        for pij__blk, dowkx__suf in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(dowkx__suf.dtype):
                crm__elzu.append(pij__blk)
                whitc__obqwk.append(types.Array(types.float64, 1, 'A'))
        if len(crm__elzu) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        whitc__obqwk = tuple(whitc__obqwk)
        crm__elzu = tuple(crm__elzu)
        index_typ = bodo.utils.typing.type_col_to_index(crm__elzu)
        rsv__bpvrd = DataFrameType(whitc__obqwk, index_typ, crm__elzu)
        return rsv__bpvrd(*kzg__lobf).replace(pysig=jhvmo__cfekb)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        mwn__scn = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        iec__neh = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        phu__qicb = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        qjwdr__nrg = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        ahp__mclx = dict(raw=iec__neh, result_type=phu__qicb)
        gphr__uaaim = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', ahp__mclx, gphr__uaaim,
            package_name='pandas', module_name='DataFrame')
        snvm__fshg = True
        if types.unliteral(mwn__scn) == types.unicode_type:
            if not is_overload_constant_str(mwn__scn):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            snvm__fshg = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        vnr__htaw = get_overload_const_int(axis)
        if snvm__fshg and vnr__htaw != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif vnr__htaw not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        guo__dmvp = []
        for arr_typ in df.data:
            ruk__pvm = SeriesType(arr_typ.dtype, arr_typ, df.index, string_type
                )
            fvgti__pug = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(ruk__pvm), types.int64), {}
                ).return_type
            guo__dmvp.append(fvgti__pug)
        cfr__ddkxl = types.none
        lwosp__scq = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(pij__blk) for pij__blk in df.columns)), None)
        itom__had = types.BaseTuple.from_types(guo__dmvp)
        ayz__ran = df.index.dtype
        if ayz__ran == types.NPDatetime('ns'):
            ayz__ran = bodo.pd_timestamp_type
        if ayz__ran == types.NPTimedelta('ns'):
            ayz__ran = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(itom__had):
            kasc__nvovk = HeterogeneousSeriesType(itom__had, lwosp__scq,
                ayz__ran)
        else:
            kasc__nvovk = SeriesType(itom__had.dtype, itom__had, lwosp__scq,
                ayz__ran)
        oflz__wvq = kasc__nvovk,
        if qjwdr__nrg is not None:
            oflz__wvq += tuple(qjwdr__nrg.types)
        try:
            if not snvm__fshg:
                ibif__wkj = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(mwn__scn), self.context,
                    'DataFrame.apply', axis if vnr__htaw == 1 else None)
            else:
                ibif__wkj = get_const_func_output_type(mwn__scn, oflz__wvq,
                    kws, self.context, numba.core.registry.cpu_target.
                    target_context)
        except Exception as wpbxc__eyipr:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                wpbxc__eyipr))
        if snvm__fshg:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(ibif__wkj, (SeriesType, HeterogeneousSeriesType)
                ) and ibif__wkj.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(ibif__wkj, HeterogeneousSeriesType):
                mfa__yodkj, kjjv__ofqp = ibif__wkj.const_info
                tgm__sctd = tuple(dtype_to_array_type(vmv__aje) for
                    vmv__aje in ibif__wkj.data.types)
                czd__mah = DataFrameType(tgm__sctd, df.index, kjjv__ofqp)
            elif isinstance(ibif__wkj, SeriesType):
                afpn__zcja, kjjv__ofqp = ibif__wkj.const_info
                tgm__sctd = tuple(dtype_to_array_type(ibif__wkj.dtype) for
                    mfa__yodkj in range(afpn__zcja))
                czd__mah = DataFrameType(tgm__sctd, df.index, kjjv__ofqp)
            else:
                zco__vixke = get_udf_out_arr_type(ibif__wkj)
                czd__mah = SeriesType(zco__vixke.dtype, zco__vixke, df.
                    index, None)
        else:
            czd__mah = ibif__wkj
        fyzw__qhx = ', '.join("{} = ''".format(rugm__hxcqb) for rugm__hxcqb in
            kws.keys())
        ecgci__chebg = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {fyzw__qhx}):
"""
        ecgci__chebg += '    pass\n'
        sagl__ptf = {}
        exec(ecgci__chebg, {}, sagl__ptf)
        iwmh__nljml = sagl__ptf['apply_stub']
        jhvmo__cfekb = numba.core.utils.pysignature(iwmh__nljml)
        defjq__wuijp = (mwn__scn, axis, iec__neh, phu__qicb, qjwdr__nrg
            ) + tuple(kws.values())
        return signature(czd__mah, *defjq__wuijp).replace(pysig=jhvmo__cfekb)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        gie__eew = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots', 'sharex',
            'sharey', 'layout', 'use_index', 'title', 'grid', 'legend',
            'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim',
            'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr', 'xerr',
            'secondary_y', 'sort_columns', 'xlabel', 'ylabel', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        jzi__mmc = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        zoq__dhps = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        jhvmo__cfekb, kzg__lobf = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, gie__eew, jzi__mmc, zoq__dhps)
        frste__pjg = kzg__lobf[2]
        if not is_overload_constant_str(frste__pjg):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        jilur__cord = kzg__lobf[0]
        if not is_overload_none(jilur__cord) and not (is_overload_int(
            jilur__cord) or is_overload_constant_str(jilur__cord)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(jilur__cord):
            rgdxi__mhezh = get_overload_const_str(jilur__cord)
            if rgdxi__mhezh not in df.columns:
                raise BodoError(
                    f'{func_name}: {rgdxi__mhezh} column not found.')
        elif is_overload_int(jilur__cord):
            znq__tfvo = get_overload_const_int(jilur__cord)
            if znq__tfvo > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {znq__tfvo} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            jilur__cord = df.columns[jilur__cord]
        rubj__xfvt = kzg__lobf[1]
        if not is_overload_none(rubj__xfvt) and not (is_overload_int(
            rubj__xfvt) or is_overload_constant_str(rubj__xfvt)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(rubj__xfvt):
            atkc__igx = get_overload_const_str(rubj__xfvt)
            if atkc__igx not in df.columns:
                raise BodoError(f'{func_name}: {atkc__igx} column not found.')
        elif is_overload_int(rubj__xfvt):
            mqms__qaipx = get_overload_const_int(rubj__xfvt)
            if mqms__qaipx > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {mqms__qaipx} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            rubj__xfvt = df.columns[rubj__xfvt]
        qravc__xyjt = kzg__lobf[3]
        if not is_overload_none(qravc__xyjt) and not is_tuple_like_type(
            qravc__xyjt):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        ciamg__jlyb = kzg__lobf[10]
        if not is_overload_none(ciamg__jlyb) and not is_overload_constant_str(
            ciamg__jlyb):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        flo__igw = kzg__lobf[12]
        if not is_overload_bool(flo__igw):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        wbk__tgql = kzg__lobf[17]
        if not is_overload_none(wbk__tgql) and not is_tuple_like_type(wbk__tgql
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        ezrh__khiqz = kzg__lobf[18]
        if not is_overload_none(ezrh__khiqz) and not is_tuple_like_type(
            ezrh__khiqz):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        kuf__iigl = kzg__lobf[22]
        if not is_overload_none(kuf__iigl) and not is_overload_int(kuf__iigl):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        cgxey__otyj = kzg__lobf[29]
        if not is_overload_none(cgxey__otyj) and not is_overload_constant_str(
            cgxey__otyj):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        drt__twoqk = kzg__lobf[30]
        if not is_overload_none(drt__twoqk) and not is_overload_constant_str(
            drt__twoqk):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        kzuep__nsy = types.List(types.mpl_line_2d_type)
        frste__pjg = get_overload_const_str(frste__pjg)
        if frste__pjg == 'scatter':
            if is_overload_none(jilur__cord) and is_overload_none(rubj__xfvt):
                raise BodoError(
                    f'{func_name}: {frste__pjg} requires an x and y column.')
            elif is_overload_none(jilur__cord):
                raise BodoError(
                    f'{func_name}: {frste__pjg} x column is missing.')
            elif is_overload_none(rubj__xfvt):
                raise BodoError(
                    f'{func_name}: {frste__pjg} y column is missing.')
            kzuep__nsy = types.mpl_path_collection_type
        elif frste__pjg != 'line':
            raise BodoError(f'{func_name}: {frste__pjg} plot is not supported.'
                )
        return signature(kzuep__nsy, *kzg__lobf).replace(pysig=jhvmo__cfekb)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            iykmi__ixv = df.columns.index(attr)
            arr_typ = df.data[iykmi__ixv]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            ngf__ybdbk = []
            zwrjv__gehvx = []
            rnvbq__obyk = False
            for i, kud__kdx in enumerate(df.columns):
                if kud__kdx[0] != attr:
                    continue
                rnvbq__obyk = True
                ngf__ybdbk.append(kud__kdx[1] if len(kud__kdx) == 2 else
                    kud__kdx[1:])
                zwrjv__gehvx.append(df.data[i])
            if rnvbq__obyk:
                return DataFrameType(tuple(zwrjv__gehvx), df.index, tuple(
                    ngf__ybdbk))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        ekol__vhhc = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(ekol__vhhc)
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
        sgoa__qoye = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], sgoa__qoye)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    ygvjj__xqsad = builder.module
    cbpv__qes = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    unrn__ngvtn = cgutils.get_or_insert_function(ygvjj__xqsad, cbpv__qes,
        name='.dtor.df.{}'.format(df_type))
    if not unrn__ngvtn.is_declaration:
        return unrn__ngvtn
    unrn__ngvtn.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(unrn__ngvtn.append_basic_block())
    vok__erm = unrn__ngvtn.args[0]
    kvoiy__omrl = context.get_value_type(payload_type).as_pointer()
    sexbr__rzpc = builder.bitcast(vok__erm, kvoiy__omrl)
    payload = context.make_helper(builder, payload_type, ref=sexbr__rzpc)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        ilni__wqfg = context.get_python_api(builder)
        qmj__yvt = ilni__wqfg.gil_ensure()
        ilni__wqfg.decref(payload.parent)
        ilni__wqfg.gil_release(qmj__yvt)
    builder.ret_void()
    return unrn__ngvtn


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    xajh__xmv = cgutils.create_struct_proxy(payload_type)(context, builder)
    xajh__xmv.data = data_tup
    xajh__xmv.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        xajh__xmv.columns = colnames
    qtihb__srb = context.get_value_type(payload_type)
    tbq__werjn = context.get_abi_sizeof(qtihb__srb)
    eeoxe__fwffm = define_df_dtor(context, builder, df_type, payload_type)
    quwi__put = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tbq__werjn), eeoxe__fwffm)
    isoip__ptuc = context.nrt.meminfo_data(builder, quwi__put)
    sjd__clci = builder.bitcast(isoip__ptuc, qtihb__srb.as_pointer())
    awcn__zor = cgutils.create_struct_proxy(df_type)(context, builder)
    awcn__zor.meminfo = quwi__put
    if parent is None:
        awcn__zor.parent = cgutils.get_null_value(awcn__zor.parent.type)
    else:
        awcn__zor.parent = parent
        xajh__xmv.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            ilni__wqfg = context.get_python_api(builder)
            qmj__yvt = ilni__wqfg.gil_ensure()
            ilni__wqfg.incref(parent)
            ilni__wqfg.gil_release(qmj__yvt)
    builder.store(xajh__xmv._getvalue(), sjd__clci)
    return awcn__zor._getvalue()


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
        advhg__egsz = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        advhg__egsz = [vmv__aje for vmv__aje in data_typ.dtype.arr_types]
    ykr__weav = DataFrameType(tuple(advhg__egsz + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        lwp__cjra = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return lwp__cjra
    sig = signature(ykr__weav, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ=None):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    afpn__zcja = len(data_tup_typ.types)
    if afpn__zcja == 0:
        agud__uhnv = ()
    elif isinstance(col_names_typ, types.TypeRef):
        agud__uhnv = col_names_typ.instance_type.columns
    else:
        agud__uhnv = get_const_tup_vals(col_names_typ)
    if afpn__zcja == 1 and isinstance(data_tup_typ.types[0], TableType):
        afpn__zcja = len(data_tup_typ.types[0].arr_types)
    assert len(agud__uhnv
        ) == afpn__zcja, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    eisw__ueye = data_tup_typ.types
    if afpn__zcja != 0 and isinstance(data_tup_typ.types[0], TableType):
        eisw__ueye = data_tup_typ.types[0].arr_types
        is_table_format = True
    ykr__weav = DataFrameType(eisw__ueye, index_typ, agud__uhnv,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            rod__ludfx = cgutils.create_struct_proxy(ykr__weav.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = rod__ludfx.parent
        lwp__cjra = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return lwp__cjra
    sig = signature(ykr__weav, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        awcn__zor = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, awcn__zor.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        xajh__xmv = get_dataframe_payload(context, builder, df_typ, args[0])
        mwefy__ykh = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[mwefy__ykh]
        if df_typ.is_table_format:
            rod__ludfx = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(xajh__xmv.data, 0))
            ymrj__yus = df_typ.table_type.type_to_blk[arr_typ]
            goe__imk = getattr(rod__ludfx, f'block_{ymrj__yus}')
            lwcq__usfl = ListInstance(context, builder, types.List(arr_typ),
                goe__imk)
            zvl__ngwd = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[mwefy__ykh])
            sgoa__qoye = lwcq__usfl.getitem(zvl__ngwd)
        else:
            sgoa__qoye = builder.extract_value(xajh__xmv.data, mwefy__ykh)
        agb__aga = cgutils.alloca_once_value(builder, sgoa__qoye)
        epjh__qavw = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, agb__aga, epjh__qavw)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    quwi__put = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, quwi__put)
    kvoiy__omrl = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, kvoiy__omrl)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    ykr__weav = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        ykr__weav = types.Tuple([TableType(df_typ.data)])
    sig = signature(ykr__weav, df_typ)

    def codegen(context, builder, signature, args):
        xajh__xmv = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            xajh__xmv.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, 'get_dataframe_index')

    def codegen(context, builder, signature, args):
        xajh__xmv = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, xajh__xmv.
            index)
    ykr__weav = df_typ.index
    sig = signature(ykr__weav, df_typ)
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
        rsv__bpvrd = df.data[i]
        return rsv__bpvrd(*args)


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
        xajh__xmv = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(xajh__xmv.data, 0))
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
    itom__had = self.typemap[data_tup.name]
    if any(is_tuple_like_type(vmv__aje) for vmv__aje in itom__had.types):
        return None
    if equiv_set.has_shape(data_tup):
        amxql__rslxi = equiv_set.get_shape(data_tup)
        if len(amxql__rslxi) > 1:
            equiv_set.insert_equiv(*amxql__rslxi)
        if len(amxql__rslxi) > 0:
            lwosp__scq = self.typemap[index.name]
            if not isinstance(lwosp__scq, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(amxql__rslxi[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(amxql__rslxi[0], len(
                amxql__rslxi)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    fdy__aptxa = args[0]
    xii__sfrno = self.typemap[fdy__aptxa.name].data
    if any(is_tuple_like_type(vmv__aje) for vmv__aje in xii__sfrno):
        return None
    if equiv_set.has_shape(fdy__aptxa):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            fdy__aptxa)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    fdy__aptxa = args[0]
    lwosp__scq = self.typemap[fdy__aptxa.name].index
    if isinstance(lwosp__scq, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(fdy__aptxa):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            fdy__aptxa)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    fdy__aptxa = args[0]
    if equiv_set.has_shape(fdy__aptxa):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            fdy__aptxa), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    mwefy__ykh = get_overload_const_int(c_ind_typ)
    if df_typ.data[mwefy__ykh] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        vyi__rbv, mfa__yodkj, sltq__kcxf = args
        xajh__xmv = get_dataframe_payload(context, builder, df_typ, vyi__rbv)
        if df_typ.is_table_format:
            rod__ludfx = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(xajh__xmv.data, 0))
            ymrj__yus = df_typ.table_type.type_to_blk[arr_typ]
            goe__imk = getattr(rod__ludfx, f'block_{ymrj__yus}')
            lwcq__usfl = ListInstance(context, builder, types.List(arr_typ),
                goe__imk)
            zvl__ngwd = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[mwefy__ykh])
            lwcq__usfl.setitem(zvl__ngwd, sltq__kcxf, True)
        else:
            sgoa__qoye = builder.extract_value(xajh__xmv.data, mwefy__ykh)
            context.nrt.decref(builder, df_typ.data[mwefy__ykh], sgoa__qoye)
            xajh__xmv.data = builder.insert_value(xajh__xmv.data,
                sltq__kcxf, mwefy__ykh)
            context.nrt.incref(builder, arr_typ, sltq__kcxf)
        awcn__zor = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=vyi__rbv)
        payload_type = DataFramePayloadType(df_typ)
        sexbr__rzpc = context.nrt.meminfo_data(builder, awcn__zor.meminfo)
        kvoiy__omrl = context.get_value_type(payload_type).as_pointer()
        sexbr__rzpc = builder.bitcast(sexbr__rzpc, kvoiy__omrl)
        builder.store(xajh__xmv._getvalue(), sexbr__rzpc)
        return impl_ret_borrowed(context, builder, df_typ, vyi__rbv)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        hbaff__kbehp = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        ult__bqfh = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=hbaff__kbehp)
        mvj__ejp = get_dataframe_payload(context, builder, df_typ, hbaff__kbehp
            )
        awcn__zor = construct_dataframe(context, builder, signature.
            return_type, mvj__ejp.data, index_val, ult__bqfh.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), mvj__ejp.data)
        return awcn__zor
    ykr__weav = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(ykr__weav, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    afpn__zcja = len(df_type.columns)
    lzsqw__dcr = afpn__zcja
    zbebx__uujwp = df_type.data
    agud__uhnv = df_type.columns
    index_typ = df_type.index
    lbvbe__ostp = col_name not in df_type.columns
    mwefy__ykh = afpn__zcja
    if lbvbe__ostp:
        zbebx__uujwp += arr_type,
        agud__uhnv += col_name,
        lzsqw__dcr += 1
    else:
        mwefy__ykh = df_type.columns.index(col_name)
        zbebx__uujwp = tuple(arr_type if i == mwefy__ykh else zbebx__uujwp[
            i] for i in range(afpn__zcja))

    def codegen(context, builder, signature, args):
        vyi__rbv, mfa__yodkj, sltq__kcxf = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, vyi__rbv)
        hzj__hgor = cgutils.create_struct_proxy(df_type)(context, builder,
            value=vyi__rbv)
        if df_type.is_table_format:
            ipmg__pjiof = df_type.table_type
            rtk__bymo = builder.extract_value(in_dataframe_payload.data, 0)
            zgmhe__sqy = TableType(zbebx__uujwp)
            oycv__obv = set_table_data_codegen(context, builder,
                ipmg__pjiof, rtk__bymo, zgmhe__sqy, arr_type, sltq__kcxf,
                mwefy__ykh, lbvbe__ostp)
            data_tup = context.make_tuple(builder, types.Tuple([zgmhe__sqy]
                ), [oycv__obv])
        else:
            eisw__ueye = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != mwefy__ykh else sltq__kcxf) for i in range(
                afpn__zcja)]
            if lbvbe__ostp:
                eisw__ueye.append(sltq__kcxf)
            for fdy__aptxa, ehzhv__byt in zip(eisw__ueye, zbebx__uujwp):
                context.nrt.incref(builder, ehzhv__byt, fdy__aptxa)
            data_tup = context.make_tuple(builder, types.Tuple(zbebx__uujwp
                ), eisw__ueye)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        miz__uaoh = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, hzj__hgor.parent, None)
        if not lbvbe__ostp and arr_type == df_type.data[mwefy__ykh]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            sexbr__rzpc = context.nrt.meminfo_data(builder, hzj__hgor.meminfo)
            kvoiy__omrl = context.get_value_type(payload_type).as_pointer()
            sexbr__rzpc = builder.bitcast(sexbr__rzpc, kvoiy__omrl)
            mlvq__iqi = get_dataframe_payload(context, builder, df_type,
                miz__uaoh)
            builder.store(mlvq__iqi._getvalue(), sexbr__rzpc)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, zgmhe__sqy, builder.
                    extract_value(data_tup, 0))
            else:
                for fdy__aptxa, ehzhv__byt in zip(eisw__ueye, zbebx__uujwp):
                    context.nrt.incref(builder, ehzhv__byt, fdy__aptxa)
        has_parent = cgutils.is_not_null(builder, hzj__hgor.parent)
        with builder.if_then(has_parent):
            ilni__wqfg = context.get_python_api(builder)
            qmj__yvt = ilni__wqfg.gil_ensure()
            clv__esxzj = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, sltq__kcxf)
            pij__blk = numba.core.pythonapi._BoxContext(context, builder,
                ilni__wqfg, clv__esxzj)
            khidt__tsta = pij__blk.pyapi.from_native_value(arr_type,
                sltq__kcxf, pij__blk.env_manager)
            if isinstance(col_name, str):
                udhk__rcxdr = context.insert_const_string(builder.module,
                    col_name)
                ohthf__bwop = ilni__wqfg.string_from_string(udhk__rcxdr)
            else:
                assert isinstance(col_name, int)
                ohthf__bwop = ilni__wqfg.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            ilni__wqfg.object_setitem(hzj__hgor.parent, ohthf__bwop,
                khidt__tsta)
            ilni__wqfg.decref(khidt__tsta)
            ilni__wqfg.decref(ohthf__bwop)
            ilni__wqfg.gil_release(qmj__yvt)
        return miz__uaoh
    ykr__weav = DataFrameType(zbebx__uujwp, index_typ, agud__uhnv, df_type.
        dist, df_type.is_table_format)
    sig = signature(ykr__weav, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    afpn__zcja = len(pyval.columns)
    eisw__ueye = tuple(pyval.iloc[:, i].values for i in range(afpn__zcja))
    if df_type.is_table_format:
        rod__ludfx = context.get_constant_generic(builder, df_type.
            table_type, Table(eisw__ueye))
        data_tup = lir.Constant.literal_struct([rod__ludfx])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], kud__kdx) for i,
            kud__kdx in enumerate(eisw__ueye)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    zqkew__lpv = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, zqkew__lpv])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    cpidq__yudz = context.get_constant(types.int64, -1)
    atln__eswr = context.get_constant_null(types.voidptr)
    quwi__put = lir.Constant.literal_struct([cpidq__yudz, atln__eswr,
        atln__eswr, payload, cpidq__yudz])
    quwi__put = cgutils.global_constant(builder, '.const.meminfo', quwi__put
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([quwi__put, zqkew__lpv])


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
        mvcw__iqj = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        mvcw__iqj = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, mvcw__iqj)
    if fromty.is_table_format == toty.is_table_format:
        zwrjv__gehvx = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                zwrjv__gehvx)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), zwrjv__gehvx)
    elif toty.is_table_format:
        zwrjv__gehvx = _cast_df_data_to_table_format(context, builder,
            fromty, toty, in_dataframe_payload)
    else:
        zwrjv__gehvx = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, zwrjv__gehvx,
        mvcw__iqj, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    oxevq__lkbst = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        eid__ijrn = get_index_data_arr_types(toty.index)[0]
        mvk__riv = bodo.utils.transform.get_type_alloc_counts(eid__ijrn) - 1
        qaov__nzteq = ', '.join('0' for mfa__yodkj in range(mvk__riv))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(qaov__nzteq, ', ' if mvk__riv == 1 else ''))
        oxevq__lkbst['index_arr_type'] = eid__ijrn
    ocivt__bztod = []
    for i, arr_typ in enumerate(toty.data):
        mvk__riv = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        qaov__nzteq = ', '.join('0' for mfa__yodkj in range(mvk__riv))
        nqd__unc = 'bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.format(
            i, qaov__nzteq, ', ' if mvk__riv == 1 else '')
        ocivt__bztod.append(nqd__unc)
        oxevq__lkbst[f'arr_type{i}'] = arr_typ
    ocivt__bztod = ', '.join(ocivt__bztod)
    ecgci__chebg = 'def impl():\n'
    outtg__aqnr = bodo.hiframes.dataframe_impl._gen_init_df(ecgci__chebg,
        toty.columns, ocivt__bztod, index, oxevq__lkbst)
    df = context.compile_internal(builder, outtg__aqnr, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    xrhn__avu = toty.table_type
    rod__ludfx = cgutils.create_struct_proxy(xrhn__avu)(context, builder)
    rod__ludfx.parent = in_dataframe_payload.parent
    for vmv__aje, ymrj__yus in xrhn__avu.type_to_blk.items():
        css__stjgc = context.get_constant(types.int64, len(xrhn__avu.
            block_to_arr_ind[ymrj__yus]))
        mfa__yodkj, jqdb__sha = ListInstance.allocate_ex(context, builder,
            types.List(vmv__aje), css__stjgc)
        jqdb__sha.size = css__stjgc
        setattr(rod__ludfx, f'block_{ymrj__yus}', jqdb__sha.value)
    for i, vmv__aje in enumerate(fromty.data):
        sgoa__qoye = builder.extract_value(in_dataframe_payload.data, i)
        ymrj__yus = xrhn__avu.type_to_blk[vmv__aje]
        goe__imk = getattr(rod__ludfx, f'block_{ymrj__yus}')
        lwcq__usfl = ListInstance(context, builder, types.List(vmv__aje),
            goe__imk)
        zvl__ngwd = context.get_constant(types.int64, xrhn__avu.
            block_offsets[i])
        lwcq__usfl.setitem(zvl__ngwd, sgoa__qoye, True)
    data_tup = context.make_tuple(builder, types.Tuple([xrhn__avu]), [
        rod__ludfx._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    xrhn__avu = fromty.table_type
    rod__ludfx = cgutils.create_struct_proxy(xrhn__avu)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    eisw__ueye = []
    for i, vmv__aje in enumerate(toty.data):
        ymrj__yus = xrhn__avu.type_to_blk[vmv__aje]
        goe__imk = getattr(rod__ludfx, f'block_{ymrj__yus}')
        lwcq__usfl = ListInstance(context, builder, types.List(vmv__aje),
            goe__imk)
        zvl__ngwd = context.get_constant(types.int64, xrhn__avu.
            block_offsets[i])
        sgoa__qoye = lwcq__usfl.getitem(zvl__ngwd)
        context.nrt.incref(builder, vmv__aje, sgoa__qoye)
        eisw__ueye.append(sgoa__qoye)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), eisw__ueye)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    vesdq__wfej, ocivt__bztod, index_arg = _get_df_args(data, index,
        columns, dtype, copy)
    eqccr__czmnu = gen_const_tup(vesdq__wfej)
    ecgci__chebg = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    ecgci__chebg += (
        '  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, {})\n'
        .format(ocivt__bztod, index_arg, eqccr__czmnu))
    sagl__ptf = {}
    exec(ecgci__chebg, {'bodo': bodo, 'np': np}, sagl__ptf)
    rwc__nya = sagl__ptf['_init_df']
    return rwc__nya


def _get_df_args(data, index, columns, dtype, copy):
    comh__bhpjj = ''
    if not is_overload_none(dtype):
        comh__bhpjj = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        afpn__zcja = (len(data.types) - 1) // 2
        ivt__vdwvq = [vmv__aje.literal_value for vmv__aje in data.types[1:
            afpn__zcja + 1]]
        data_val_types = dict(zip(ivt__vdwvq, data.types[afpn__zcja + 1:]))
        eisw__ueye = ['data[{}]'.format(i) for i in range(afpn__zcja + 1, 2 *
            afpn__zcja + 1)]
        data_dict = dict(zip(ivt__vdwvq, eisw__ueye))
        if is_overload_none(index):
            for i, vmv__aje in enumerate(data.types[afpn__zcja + 1:]):
                if isinstance(vmv__aje, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(afpn__zcja + 1 + i))
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
        myiq__zwl = '.copy()' if copy else ''
        mnq__ier = get_overload_const_list(columns)
        afpn__zcja = len(mnq__ier)
        data_val_types = {pij__blk: data.copy(ndim=1) for pij__blk in mnq__ier}
        eisw__ueye = ['data[:,{}]{}'.format(i, myiq__zwl) for i in range(
            afpn__zcja)]
        data_dict = dict(zip(mnq__ier, eisw__ueye))
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
    ocivt__bztod = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[pij__blk], df_len, comh__bhpjj) for pij__blk in
        col_names))
    if len(col_names) == 0:
        ocivt__bztod = '()'
    return col_names, ocivt__bztod, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for pij__blk in col_names:
        if pij__blk in data_dict and is_iterable_type(data_val_types[pij__blk]
            ):
            df_len = 'len({})'.format(data_dict[pij__blk])
            break
    if df_len == '0' and not index_is_none:
        df_len = f'len({index_arg})'
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(pij__blk in data_dict for pij__blk in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    mnoc__hzfw = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for pij__blk in col_names:
        if pij__blk not in data_dict:
            data_dict[pij__blk] = mnoc__hzfw


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
            vmv__aje = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(vmv__aje)
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
        lbbf__kvo = idx.literal_value
        if isinstance(lbbf__kvo, int):
            rsv__bpvrd = tup.types[lbbf__kvo]
        elif isinstance(lbbf__kvo, slice):
            rsv__bpvrd = types.BaseTuple.from_types(tup.types[lbbf__kvo])
        return signature(rsv__bpvrd, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    sdqg__amh, idx = sig.args
    idx = idx.literal_value
    tup, mfa__yodkj = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(sdqg__amh)
        if not 0 <= idx < len(sdqg__amh):
            raise IndexError('cannot index at %d in %s' % (idx, sdqg__amh))
        vnw__nhoo = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        hrnlg__mozwd = cgutils.unpack_tuple(builder, tup)[idx]
        vnw__nhoo = context.make_tuple(builder, sig.return_type, hrnlg__mozwd)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, vnw__nhoo)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, xhzll__vcnk, suffix_x,
            suffix_y, is_join, indicator, _bodo_na_equal, dfxo__ijo) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        iggj__frcx = set(left_on) & set(right_on)
        bmp__vvbt = set(left_df.columns) & set(right_df.columns)
        dyzl__ogo = bmp__vvbt - iggj__frcx
        zlko__qpzl = '$_bodo_index_' in left_on
        wba__qbyvk = '$_bodo_index_' in right_on
        how = get_overload_const_str(xhzll__vcnk)
        nmqs__odj = how in {'left', 'outer'}
        plgk__lhcm = how in {'right', 'outer'}
        columns = []
        data = []
        if zlko__qpzl and not wba__qbyvk and not is_join.literal_value:
            tvv__jmjqy = right_on[0]
            if tvv__jmjqy in left_df.columns:
                columns.append(tvv__jmjqy)
                data.append(right_df.data[right_df.columns.index(tvv__jmjqy)])
        if wba__qbyvk and not zlko__qpzl and not is_join.literal_value:
            rys__jenu = left_on[0]
            if rys__jenu in right_df.columns:
                columns.append(rys__jenu)
                data.append(left_df.data[left_df.columns.index(rys__jenu)])
        for wbqq__qgcqs, rxvfk__cbi in zip(left_df.data, left_df.columns):
            columns.append(str(rxvfk__cbi) + suffix_x.literal_value if 
                rxvfk__cbi in dyzl__ogo else rxvfk__cbi)
            if rxvfk__cbi in iggj__frcx:
                data.append(wbqq__qgcqs)
            else:
                data.append(to_nullable_type(wbqq__qgcqs) if plgk__lhcm else
                    wbqq__qgcqs)
        for wbqq__qgcqs, rxvfk__cbi in zip(right_df.data, right_df.columns):
            if rxvfk__cbi not in iggj__frcx:
                columns.append(str(rxvfk__cbi) + suffix_y.literal_value if 
                    rxvfk__cbi in dyzl__ogo else rxvfk__cbi)
                data.append(to_nullable_type(wbqq__qgcqs) if nmqs__odj else
                    wbqq__qgcqs)
        dkuc__icrje = get_overload_const_bool(indicator)
        if dkuc__icrje:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        if zlko__qpzl and wba__qbyvk and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif zlko__qpzl and not wba__qbyvk:
            index_typ = right_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        elif wba__qbyvk and not zlko__qpzl:
            index_typ = left_df.index
            if isinstance(index_typ, bodo.hiframes.pd_index_ext.RangeIndexType
                ):
                index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types
                    .int64)
        hvgyc__oxdwj = DataFrameType(tuple(data), index_typ, tuple(columns))
        return signature(hvgyc__oxdwj, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    awcn__zor = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return awcn__zor._getvalue()


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
    ahp__mclx = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    jzi__mmc = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', ahp__mclx, jzi__mmc,
        package_name='pandas', module_name='General')
    ecgci__chebg = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        wwzo__fobaj = 0
        ocivt__bztod = []
        names = []
        for i, gtap__qtyd in enumerate(objs.types):
            assert isinstance(gtap__qtyd, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(gtap__qtyd, 'pd.concat()')
            if isinstance(gtap__qtyd, SeriesType):
                names.append(str(wwzo__fobaj))
                wwzo__fobaj += 1
                ocivt__bztod.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(gtap__qtyd.columns)
                for yyz__bqoc in range(len(gtap__qtyd.data)):
                    ocivt__bztod.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, yyz__bqoc))
        return bodo.hiframes.dataframe_impl._gen_init_df(ecgci__chebg,
            names, ', '.join(ocivt__bztod), index)
    assert axis == 0
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(vmv__aje, DataFrameType) for vmv__aje in objs
            .types)
        sjwkl__jntxv = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pd.concat()')
            sjwkl__jntxv.extend(df.columns)
        sjwkl__jntxv = list(dict.fromkeys(sjwkl__jntxv).keys())
        advhg__egsz = {}
        for wwzo__fobaj, pij__blk in enumerate(sjwkl__jntxv):
            for df in objs.types:
                if pij__blk in df.columns:
                    advhg__egsz['arr_typ{}'.format(wwzo__fobaj)] = df.data[df
                        .columns.index(pij__blk)]
                    break
        assert len(advhg__egsz) == len(sjwkl__jntxv)
        qbhs__lml = []
        for wwzo__fobaj, pij__blk in enumerate(sjwkl__jntxv):
            args = []
            for i, df in enumerate(objs.types):
                if pij__blk in df.columns:
                    mwefy__ykh = df.columns.index(pij__blk)
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, mwefy__ykh))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, wwzo__fobaj))
            ecgci__chebg += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(wwzo__fobaj, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(ecgci__chebg,
            sjwkl__jntxv, ', '.join('A{}'.format(i) for i in range(len(
            sjwkl__jntxv))), index, advhg__egsz)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(vmv__aje, SeriesType) for vmv__aje in objs.types)
        ecgci__chebg += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            ecgci__chebg += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ecgci__chebg += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        ecgci__chebg += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        sagl__ptf = {}
        exec(ecgci__chebg, {'bodo': bodo, 'np': np, 'numba': numba}, sagl__ptf)
        return sagl__ptf['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pd.concat()')
        df_type = objs.dtype
        for wwzo__fobaj, pij__blk in enumerate(df_type.columns):
            ecgci__chebg += '  arrs{} = []\n'.format(wwzo__fobaj)
            ecgci__chebg += '  for i in range(len(objs)):\n'
            ecgci__chebg += '    df = objs[i]\n'
            ecgci__chebg += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(wwzo__fobaj))
            ecgci__chebg += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(wwzo__fobaj))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            ecgci__chebg += '  arrs_index = []\n'
            ecgci__chebg += '  for i in range(len(objs)):\n'
            ecgci__chebg += '    df = objs[i]\n'
            ecgci__chebg += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(ecgci__chebg,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        ecgci__chebg += '  arrs = []\n'
        ecgci__chebg += '  for i in range(len(objs)):\n'
        ecgci__chebg += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        ecgci__chebg += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            ecgci__chebg += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ecgci__chebg += '  arrs_index = []\n'
            ecgci__chebg += '  for i in range(len(objs)):\n'
            ecgci__chebg += '    S = objs[i]\n'
            ecgci__chebg += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            ecgci__chebg += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        ecgci__chebg += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        sagl__ptf = {}
        exec(ecgci__chebg, {'bodo': bodo, 'np': np, 'numba': numba}, sagl__ptf)
        return sagl__ptf['impl']
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
        ykr__weav = df.copy(index=index, is_table_format=False)
        return signature(ykr__weav, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    ghql__pkzz = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ghql__pkzz._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    ahp__mclx = dict(index=index, name=name)
    jzi__mmc = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', ahp__mclx, jzi__mmc,
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
        advhg__egsz = (types.Array(types.int64, 1, 'C'),) + df.data
        aaq__tqyd = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(columns
            , advhg__egsz)
        return signature(aaq__tqyd, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    ghql__pkzz = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ghql__pkzz._getvalue()


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
    ghql__pkzz = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ghql__pkzz._getvalue()


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
    ghql__pkzz = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ghql__pkzz._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True, parallel
    =False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    kejpb__zww = get_overload_const_bool(check_duplicates)
    nrc__luhq = not is_overload_none(value_names)
    wxxvo__bvlas = isinstance(values_tup, types.UniTuple)
    if wxxvo__bvlas:
        obh__xaa = [to_nullable_type(values_tup.dtype)]
    else:
        obh__xaa = [to_nullable_type(ehzhv__byt) for ehzhv__byt in values_tup]
    ecgci__chebg = 'def impl(\n'
    ecgci__chebg += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, parallel=False
"""
    ecgci__chebg += '):\n'
    ecgci__chebg += '    if parallel:\n'
    txt__fmu = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    ecgci__chebg += f'        info_list = [{txt__fmu}]\n'
    ecgci__chebg += '        cpp_table = arr_info_list_to_table(info_list)\n'
    ecgci__chebg += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    crn__vhxxz = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    cmak__fyio = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    eupb__pnws = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    ecgci__chebg += f'        index_tup = ({crn__vhxxz},)\n'
    ecgci__chebg += f'        columns_tup = ({cmak__fyio},)\n'
    ecgci__chebg += f'        values_tup = ({eupb__pnws},)\n'
    ecgci__chebg += '        delete_table(cpp_table)\n'
    ecgci__chebg += '        delete_table(out_cpp_table)\n'
    ecgci__chebg += '    columns_arr = columns_tup[0]\n'
    if wxxvo__bvlas:
        ecgci__chebg += '    values_arrs = [arr for arr in values_tup]\n'
    ecgci__chebg += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    ecgci__chebg += '        index_tup\n'
    ecgci__chebg += '    )\n'
    ecgci__chebg += '    n_rows = len(unique_index_arr_tup[0])\n'
    ecgci__chebg += '    num_values_arrays = len(values_tup)\n'
    ecgci__chebg += '    n_unique_pivots = len(pivot_values)\n'
    if wxxvo__bvlas:
        ecgci__chebg += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        ecgci__chebg += '    n_cols = n_unique_pivots\n'
    ecgci__chebg += '    col_map = {}\n'
    ecgci__chebg += '    for i in range(n_unique_pivots):\n'
    ecgci__chebg += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    ecgci__chebg += '            raise ValueError(\n'
    ecgci__chebg += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    ecgci__chebg += '            )\n'
    ecgci__chebg += '        col_map[pivot_values[i]] = i\n'
    flvbf__nuci = False
    for i, jcesx__mdqp in enumerate(obh__xaa):
        if jcesx__mdqp == bodo.string_array_type:
            flvbf__nuci = True
            ecgci__chebg += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            ecgci__chebg += (
                f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n')
    if flvbf__nuci:
        if kejpb__zww:
            ecgci__chebg += '    nbytes = (n_rows + 7) >> 3\n'
            ecgci__chebg += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        ecgci__chebg += '    for i in range(len(columns_arr)):\n'
        ecgci__chebg += '        col_name = columns_arr[i]\n'
        ecgci__chebg += '        pivot_idx = col_map[col_name]\n'
        ecgci__chebg += '        row_idx = row_vector[i]\n'
        if kejpb__zww:
            ecgci__chebg += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            ecgci__chebg += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            ecgci__chebg += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            ecgci__chebg += '        else:\n'
            ecgci__chebg += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if wxxvo__bvlas:
            ecgci__chebg += '        for j in range(num_values_arrays):\n'
            ecgci__chebg += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            ecgci__chebg += '            len_arr = len_arrs_0[col_idx]\n'
            ecgci__chebg += '            values_arr = values_arrs[j]\n'
            ecgci__chebg += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            ecgci__chebg += (
                '                len_arr[row_idx] = len(values_arr[i])\n')
            ecgci__chebg += (
                '                total_lens_0[col_idx] += len(values_arr[i])\n'
                )
        else:
            for i, jcesx__mdqp in enumerate(obh__xaa):
                if jcesx__mdqp == bodo.string_array_type:
                    ecgci__chebg += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    ecgci__chebg += f"""            len_arrs_{i}[pivot_idx][row_idx] = len(values_tup[{i}][i])
"""
                    ecgci__chebg += f"""            total_lens_{i}[pivot_idx] += len(values_tup[{i}][i])
"""
    for i, jcesx__mdqp in enumerate(obh__xaa):
        if jcesx__mdqp == bodo.string_array_type:
            ecgci__chebg += f'    data_arrs_{i} = [\n'
            ecgci__chebg += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            ecgci__chebg += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            ecgci__chebg += '        )\n'
            ecgci__chebg += '        for i in range(n_cols)\n'
            ecgci__chebg += '    ]\n'
        else:
            ecgci__chebg += f'    data_arrs_{i} = [\n'
            ecgci__chebg += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            ecgci__chebg += '        for _ in range(n_cols)\n'
            ecgci__chebg += '    ]\n'
    if not flvbf__nuci and kejpb__zww:
        ecgci__chebg += '    nbytes = (n_rows + 7) >> 3\n'
        ecgci__chebg += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    ecgci__chebg += '    for i in range(len(columns_arr)):\n'
    ecgci__chebg += '        col_name = columns_arr[i]\n'
    ecgci__chebg += '        pivot_idx = col_map[col_name]\n'
    ecgci__chebg += '        row_idx = row_vector[i]\n'
    if not flvbf__nuci and kejpb__zww:
        ecgci__chebg += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        ecgci__chebg += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        ecgci__chebg += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        ecgci__chebg += '        else:\n'
        ecgci__chebg += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if wxxvo__bvlas:
        ecgci__chebg += '        for j in range(num_values_arrays):\n'
        ecgci__chebg += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        ecgci__chebg += '            col_arr = data_arrs_0[col_idx]\n'
        ecgci__chebg += '            values_arr = values_arrs[j]\n'
        ecgci__chebg += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        ecgci__chebg += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        ecgci__chebg += '            else:\n'
        ecgci__chebg += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, jcesx__mdqp in enumerate(obh__xaa):
            ecgci__chebg += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            ecgci__chebg += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            ecgci__chebg += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            ecgci__chebg += f'        else:\n'
            ecgci__chebg += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_tup) == 1:
        ecgci__chebg += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names[0])
"""
    else:
        ecgci__chebg += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names, None)
"""
    if nrc__luhq:
        ecgci__chebg += '    num_rows = len(value_names) * len(pivot_values)\n'
        if value_names == bodo.string_array_type:
            ecgci__chebg += '    total_chars = 0\n'
            ecgci__chebg += '    for i in range(len(value_names)):\n'
            ecgci__chebg += '        total_chars += len(value_names[i])\n'
            ecgci__chebg += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
        else:
            ecgci__chebg += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names, (-1,))
"""
        if pivot_values == bodo.string_array_type:
            ecgci__chebg += '    total_chars = 0\n'
            ecgci__chebg += '    for i in range(len(pivot_values)):\n'
            ecgci__chebg += '        total_chars += len(pivot_values[i])\n'
            ecgci__chebg += """    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(value_names))
"""
        else:
            ecgci__chebg += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
        ecgci__chebg += '    for i in range(len(value_names)):\n'
        ecgci__chebg += '        for j in range(len(pivot_values)):\n'
        ecgci__chebg += """            new_value_names[(i * len(pivot_values)) + j] = value_names[i]
"""
        ecgci__chebg += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
        ecgci__chebg += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name), None)
"""
    else:
        ecgci__chebg += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name)
"""
    xec__syqiq = ', '.join(f'data_arrs_{i}' for i in range(len(obh__xaa)))
    ecgci__chebg += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({xec__syqiq},), n_rows)
"""
    ecgci__chebg += (
        '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
        )
    ecgci__chebg += '        (table,), index, column_index\n'
    ecgci__chebg += '    )\n'
    sagl__ptf = {}
    fgjs__sph = {f'data_arr_typ_{i}': jcesx__mdqp for i, jcesx__mdqp in
        enumerate(obh__xaa)}
    hrqw__uawz = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, **fgjs__sph}
    exec(ecgci__chebg, hrqw__uawz, sagl__ptf)
    impl = sagl__ptf['impl']
    return impl


def gen_pandas_parquet_metadata(df, write_non_range_index_to_metadata,
    write_rangeindex_to_metadata, partition_cols=None):
    nlp__xfdh = {}
    nlp__xfdh['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, ebh__hse in zip(df.columns, df.data):
        if col_name in partition_cols:
            continue
        if isinstance(ebh__hse, types.Array) or ebh__hse == boolean_array:
            lhxki__jgdvu = dld__mrd = ebh__hse.dtype.name
            if dld__mrd.startswith('datetime'):
                lhxki__jgdvu = 'datetime'
        elif ebh__hse == string_array_type:
            lhxki__jgdvu = 'unicode'
            dld__mrd = 'object'
        elif ebh__hse == binary_array_type:
            lhxki__jgdvu = 'bytes'
            dld__mrd = 'object'
        elif isinstance(ebh__hse, DecimalArrayType):
            lhxki__jgdvu = dld__mrd = 'object'
        elif isinstance(ebh__hse, IntegerArrayType):
            rnyvx__tbvzh = ebh__hse.dtype.name
            if rnyvx__tbvzh.startswith('int'):
                lhxki__jgdvu = 'Int' + rnyvx__tbvzh[3:]
            elif rnyvx__tbvzh.startswith('uint'):
                lhxki__jgdvu = 'UInt' + rnyvx__tbvzh[4:]
            else:
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, ebh__hse))
            dld__mrd = ebh__hse.dtype.name
        elif ebh__hse == datetime_date_array_type:
            lhxki__jgdvu = 'datetime'
            dld__mrd = 'object'
        elif isinstance(ebh__hse, (StructArrayType, ArrayItemArrayType)):
            lhxki__jgdvu = 'object'
            dld__mrd = 'object'
        else:
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, ebh__hse))
        xush__vuq = {'name': col_name, 'field_name': col_name,
            'pandas_type': lhxki__jgdvu, 'numpy_type': dld__mrd, 'metadata':
            None}
        nlp__xfdh['columns'].append(xush__vuq)
    if write_non_range_index_to_metadata:
        if isinstance(df.index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in df.index.name:
            jnlwa__zcv = '__index_level_0__'
            kbrdg__vab = None
        else:
            jnlwa__zcv = '%s'
            kbrdg__vab = '%s'
        nlp__xfdh['index_columns'] = [jnlwa__zcv]
        nlp__xfdh['columns'].append({'name': kbrdg__vab, 'field_name':
            jnlwa__zcv, 'pandas_type': df.index.pandas_type_name,
            'numpy_type': df.index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        nlp__xfdh['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        nlp__xfdh['index_columns'] = []
    nlp__xfdh['pandas_version'] = pd.__version__
    return nlp__xfdh


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
        aztxb__rwvcq = []
        for jacoh__tstj in partition_cols:
            try:
                idx = df.columns.index(jacoh__tstj)
            except ValueError as ndjah__aymsz:
                raise BodoError(
                    f'Partition column {jacoh__tstj} is not in dataframe')
            aztxb__rwvcq.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    zfr__pkvsd = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    pho__kgcn = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not zfr__pkvsd)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not zfr__pkvsd or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and zfr__pkvsd and not is_overload_true(_is_parallel)
    thad__yxc = json.dumps(gen_pandas_parquet_metadata(df,
        write_non_range_index_to_metadata, write_rangeindex_to_metadata,
        partition_cols=partition_cols))
    if not is_overload_true(_is_parallel) and zfr__pkvsd:
        thad__yxc = thad__yxc.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            thad__yxc = thad__yxc.replace('"%s"', '%s')
    ocivt__bztod = ', '.join(
        'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(len(df.columns)))
    ecgci__chebg = """def df_to_parquet(df, fname, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, _is_parallel=False):
"""
    if df.is_table_format:
        ecgci__chebg += """    table = py_table_to_cpp_table(get_dataframe_table(df), py_table_typ)
"""
    else:
        ecgci__chebg += '    info_list = [{}]\n'.format(ocivt__bztod)
        ecgci__chebg += '    table = arr_info_list_to_table(info_list)\n'
    ecgci__chebg += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and pho__kgcn:
        ecgci__chebg += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        grs__xqci = True
    else:
        ecgci__chebg += '    index_col = array_to_info(np.empty(0))\n'
        grs__xqci = False
    ecgci__chebg += '    metadata = """' + thad__yxc + '"""\n'
    ecgci__chebg += '    if compression is None:\n'
    ecgci__chebg += "        compression = 'none'\n"
    ecgci__chebg += '    if df.index.name is not None:\n'
    ecgci__chebg += '        name_ptr = df.index.name\n'
    ecgci__chebg += '    else:\n'
    ecgci__chebg += "        name_ptr = 'null'\n"
    ecgci__chebg += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel=_is_parallel)
"""
    gge__jglw = None
    if partition_cols:
        gge__jglw = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        ngwav__gpyru = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in aztxb__rwvcq)
        if ngwav__gpyru:
            ecgci__chebg += '    cat_info_list = [{}]\n'.format(ngwav__gpyru)
            ecgci__chebg += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            ecgci__chebg += '    cat_table = table\n'
        ecgci__chebg += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        ecgci__chebg += (
            f'    part_cols_idxs = np.array({aztxb__rwvcq}, dtype=np.int32)\n')
        ecgci__chebg += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(fname),\n'
            )
        ecgci__chebg += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        ecgci__chebg += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        ecgci__chebg += (
            '                            unicode_to_utf8(compression),\n')
        ecgci__chebg += '                            _is_parallel,\n'
        ecgci__chebg += (
            '                            unicode_to_utf8(bucket_region))\n')
        ecgci__chebg += '    delete_table_decref_arrays(table)\n'
        ecgci__chebg += '    delete_info_decref_array(index_col)\n'
        ecgci__chebg += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        ecgci__chebg += '    delete_info_decref_array(col_names)\n'
        if ngwav__gpyru:
            ecgci__chebg += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        ecgci__chebg += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        ecgci__chebg += (
            '                            table, col_names, index_col,\n')
        ecgci__chebg += '                            ' + str(grs__xqci) + ',\n'
        ecgci__chebg += (
            '                            unicode_to_utf8(metadata),\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(compression),\n')
        ecgci__chebg += (
            '                            _is_parallel, 1, df.index.start,\n')
        ecgci__chebg += (
            '                            df.index.stop, df.index.step,\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(name_ptr),\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(bucket_region))\n')
        ecgci__chebg += '    delete_table_decref_arrays(table)\n'
        ecgci__chebg += '    delete_info_decref_array(index_col)\n'
        ecgci__chebg += '    delete_info_decref_array(col_names)\n'
    else:
        ecgci__chebg += '    parquet_write_table_cpp(unicode_to_utf8(fname),\n'
        ecgci__chebg += (
            '                            table, col_names, index_col,\n')
        ecgci__chebg += '                            ' + str(grs__xqci) + ',\n'
        ecgci__chebg += (
            '                            unicode_to_utf8(metadata),\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(compression),\n')
        ecgci__chebg += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(name_ptr),\n')
        ecgci__chebg += (
            '                            unicode_to_utf8(bucket_region))\n')
        ecgci__chebg += '    delete_table_decref_arrays(table)\n'
        ecgci__chebg += '    delete_info_decref_array(index_col)\n'
        ecgci__chebg += '    delete_info_decref_array(col_names)\n'
    sagl__ptf = {}
    exec(ecgci__chebg, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
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
        'col_names_no_parts_arr': gge__jglw}, sagl__ptf)
    pdydc__kakof = sagl__ptf['df_to_parquet']
    return pdydc__kakof


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    mwbo__fcy = 'all_ok'
    rfqbi__gehmm = urlparse(con).scheme
    if _is_parallel and bodo.get_rank() == 0:
        dommk__imri = 100
        if chunksize is None:
            kuav__vrmkr = dommk__imri
        else:
            kuav__vrmkr = min(chunksize, dommk__imri)
        if _is_table_create:
            df = df.iloc[:kuav__vrmkr, :]
        else:
            df = df.iloc[kuav__vrmkr:, :]
            if len(df) == 0:
                return mwbo__fcy
    if rfqbi__gehmm == 'snowflake':
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
            df.columns = [(pij__blk.upper() if pij__blk.islower() else
                pij__blk) for pij__blk in df.columns]
        except ImportError as ndjah__aymsz:
            mwbo__fcy = (
                "Snowflake Python connector not found. It can be installed by calling 'conda install -c conda-forge snowflake-connector-python' or 'pip install snowflake-connector-python'."
                )
            return mwbo__fcy
    try:
        df.to_sql(name, con, schema, if_exists, index, index_label,
            chunksize, dtype, method)
    except Exception as wpbxc__eyipr:
        mwbo__fcy = wpbxc__eyipr.args[0]
    return mwbo__fcy


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
    ahp__mclx = dict(chunksize=chunksize)
    jzi__mmc = dict(chunksize=None)
    check_unsupported_args('to_sql', ahp__mclx, jzi__mmc, package_name=
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
        pximn__agq = bodo.libs.distributed_api.get_rank()
        mwbo__fcy = 'unset'
        if pximn__agq != 0:
            mwbo__fcy = bcast_scalar(mwbo__fcy)
        elif pximn__agq == 0:
            mwbo__fcy = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                True, _is_parallel)
            mwbo__fcy = bcast_scalar(mwbo__fcy)
        if_exists = 'append'
        if _is_parallel and mwbo__fcy == 'all_ok':
            mwbo__fcy = to_sql_exception_guard_encaps(df, name, con, schema,
                if_exists, index, index_label, chunksize, dtype, method, 
                False, _is_parallel)
        if mwbo__fcy != 'all_ok':
            print('err_msg=', mwbo__fcy)
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
        tdhrs__xin = get_overload_const_str(path_or_buf)
        if tdhrs__xin.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        eyza__wkya = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(eyza__wkya))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(eyza__wkya))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    nvlib__qtta = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    rsh__izat = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', nvlib__qtta, rsh__izat,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    ecgci__chebg = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        nunt__urzal = data.data.dtype.categories
        ecgci__chebg += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        nunt__urzal = data.dtype.categories
        ecgci__chebg += '  data_values = data\n'
    afpn__zcja = len(nunt__urzal)
    ecgci__chebg += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    ecgci__chebg += '  numba.parfors.parfor.init_prange()\n'
    ecgci__chebg += '  n = len(data_values)\n'
    for i in range(afpn__zcja):
        ecgci__chebg += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    ecgci__chebg += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ecgci__chebg += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for yyz__bqoc in range(afpn__zcja):
        ecgci__chebg += '          data_arr_{}[i] = 0\n'.format(yyz__bqoc)
    ecgci__chebg += '      else:\n'
    for qzati__kvpr in range(afpn__zcja):
        ecgci__chebg += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            qzati__kvpr)
    ocivt__bztod = ', '.join(f'data_arr_{i}' for i in range(afpn__zcja))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(nunt__urzal[0], np.datetime64):
        nunt__urzal = tuple(pd.Timestamp(pij__blk) for pij__blk in nunt__urzal)
    elif isinstance(nunt__urzal[0], np.timedelta64):
        nunt__urzal = tuple(pd.Timedelta(pij__blk) for pij__blk in nunt__urzal)
    return bodo.hiframes.dataframe_impl._gen_init_df(ecgci__chebg,
        nunt__urzal, ocivt__bztod, index)


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
    for xgek__brtdp in pd_unsupported:
        fname = mod_name + '.' + xgek__brtdp.__name__
        overload(xgek__brtdp, no_unliteral=True)(create_unsupported_overload
            (fname))


def _install_dataframe_unsupported():
    for uex__rdy in dataframe_unsupported_attrs:
        doani__fww = 'DataFrame.' + uex__rdy
        overload_attribute(DataFrameType, uex__rdy)(create_unsupported_overload
            (doani__fww))
    for fname in dataframe_unsupported:
        doani__fww = 'DataFrame.' + fname + '()'
        overload_method(DataFrameType, fname)(create_unsupported_overload(
            doani__fww))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
