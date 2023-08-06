"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            ojwf__lgu = idx
            yzzb__ekuyv = df.data
            kow__pahsh = df.columns
            lfaa__rcz = self.replace_range_with_numeric_idx_if_needed(df,
                ojwf__lgu)
            azzy__gzvl = DataFrameType(yzzb__ekuyv, lfaa__rcz, kow__pahsh)
            return azzy__gzvl(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            bdoa__dtoh = idx.types[0]
            lzkb__ciuo = idx.types[1]
            if isinstance(bdoa__dtoh, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(lzkb__ciuo):
                    ujxg__arnjz = get_overload_const_str(lzkb__ciuo)
                    if ujxg__arnjz not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, ujxg__arnjz))
                    sjv__nblto = df.columns.index(ujxg__arnjz)
                    return df.data[sjv__nblto].dtype(*args)
                if isinstance(lzkb__ciuo, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(bdoa__dtoh
                ) and bdoa__dtoh.dtype == types.bool_ or isinstance(bdoa__dtoh,
                types.SliceType):
                lfaa__rcz = self.replace_range_with_numeric_idx_if_needed(df,
                    bdoa__dtoh)
                if is_overload_constant_str(lzkb__ciuo):
                    kgb__ndk = get_overload_const_str(lzkb__ciuo)
                    if kgb__ndk not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {kgb__ndk}'
                            )
                    sjv__nblto = df.columns.index(kgb__ndk)
                    pkrsy__cxwcr = df.data[sjv__nblto]
                    wllf__sqsbm = pkrsy__cxwcr.dtype
                    emwho__lglh = types.literal(df.columns[sjv__nblto])
                    azzy__gzvl = bodo.SeriesType(wllf__sqsbm, pkrsy__cxwcr,
                        lfaa__rcz, emwho__lglh)
                    return azzy__gzvl(*args)
                if isinstance(lzkb__ciuo, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                elif is_overload_constant_list(lzkb__ciuo):
                    opk__yak = get_overload_const_list(lzkb__ciuo)
                    ypelw__lzh = types.unliteral(lzkb__ciuo)
                    if ypelw__lzh.dtype == types.bool_:
                        if len(df.columns) != len(opk__yak):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {opk__yak} has {len(opk__yak)} values'
                                )
                        bjcns__trv = []
                        ywxwo__naiim = []
                        for nirv__whja in range(len(opk__yak)):
                            if opk__yak[nirv__whja]:
                                bjcns__trv.append(df.columns[nirv__whja])
                                ywxwo__naiim.append(df.data[nirv__whja])
                        kvzg__jfg = tuple()
                        azzy__gzvl = DataFrameType(tuple(ywxwo__naiim),
                            lfaa__rcz, tuple(bjcns__trv))
                        return azzy__gzvl(*args)
                    elif ypelw__lzh.dtype == bodo.string_type:
                        kvzg__jfg, ywxwo__naiim = self.get_kept_cols_and_data(
                            df, opk__yak)
                        azzy__gzvl = DataFrameType(ywxwo__naiim, lfaa__rcz,
                            kvzg__jfg)
                        return azzy__gzvl(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                bjcns__trv = []
                ywxwo__naiim = []
                for nirv__whja, zsvy__lvwrz in enumerate(df.columns):
                    if zsvy__lvwrz[0] != ind_val:
                        continue
                    bjcns__trv.append(zsvy__lvwrz[1] if len(zsvy__lvwrz) ==
                        2 else zsvy__lvwrz[1:])
                    ywxwo__naiim.append(df.data[nirv__whja])
                pkrsy__cxwcr = tuple(ywxwo__naiim)
                ajnll__hfj = df.index
                hqqj__rslvd = tuple(bjcns__trv)
                azzy__gzvl = DataFrameType(pkrsy__cxwcr, ajnll__hfj,
                    hqqj__rslvd)
                return azzy__gzvl(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                sjv__nblto = df.columns.index(ind_val)
                pkrsy__cxwcr = df.data[sjv__nblto]
                wllf__sqsbm = pkrsy__cxwcr.dtype
                ajnll__hfj = df.index
                emwho__lglh = types.literal(df.columns[sjv__nblto])
                azzy__gzvl = bodo.SeriesType(wllf__sqsbm, pkrsy__cxwcr,
                    ajnll__hfj, emwho__lglh)
                return azzy__gzvl(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            pkrsy__cxwcr = df.data
            ajnll__hfj = self.replace_range_with_numeric_idx_if_needed(df, ind)
            hqqj__rslvd = df.columns
            azzy__gzvl = DataFrameType(pkrsy__cxwcr, ajnll__hfj,
                hqqj__rslvd, is_table_format=df.is_table_format)
            return azzy__gzvl(*args)
        elif is_overload_constant_list(ind):
            pwfrh__bhb = get_overload_const_list(ind)
            hqqj__rslvd, pkrsy__cxwcr = self.get_kept_cols_and_data(df,
                pwfrh__bhb)
            ajnll__hfj = df.index
            azzy__gzvl = DataFrameType(pkrsy__cxwcr, ajnll__hfj, hqqj__rslvd)
            return azzy__gzvl(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
            )

    def get_kept_cols_and_data(self, df, cols_to_keep_list):
        for vuh__nhopg in cols_to_keep_list:
            if vuh__nhopg not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(vuh__nhopg, df.columns))
        hqqj__rslvd = tuple(cols_to_keep_list)
        pkrsy__cxwcr = tuple(df.data[df.columns.index(wuh__bpyt)] for
            wuh__bpyt in hqqj__rslvd)
        return hqqj__rslvd, pkrsy__cxwcr

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        lfaa__rcz = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64,
            df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return lfaa__rcz


DataFrameGetItemTemplate._no_unliteral = True


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            bjcns__trv = []
            ywxwo__naiim = []
            for nirv__whja, zsvy__lvwrz in enumerate(df.columns):
                if zsvy__lvwrz[0] != ind_val:
                    continue
                bjcns__trv.append(zsvy__lvwrz[1] if len(zsvy__lvwrz) == 2 else
                    zsvy__lvwrz[1:])
                ywxwo__naiim.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(nirv__whja))
            jtdsr__yll = 'def impl(df, ind):\n'
            ifsod__tohf = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll,
                bjcns__trv, ', '.join(ywxwo__naiim), ifsod__tohf)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        pwfrh__bhb = get_overload_const_list(ind)
        for vuh__nhopg in pwfrh__bhb:
            if vuh__nhopg not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(vuh__nhopg, df.columns))
        ywxwo__naiim = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}).copy()'
            .format(df.columns.index(vuh__nhopg)) for vuh__nhopg in pwfrh__bhb)
        jtdsr__yll = 'def impl(df, ind):\n'
        ifsod__tohf = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll,
            pwfrh__bhb, ywxwo__naiim, ifsod__tohf)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        jtdsr__yll = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            jtdsr__yll += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        ifsod__tohf = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            ywxwo__naiim = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            ywxwo__naiim = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(vuh__nhopg)})[ind]'
                 for vuh__nhopg in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll, df.
            columns, ywxwo__naiim, ifsod__tohf, out_df_type=df)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wuh__bpyt = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(wuh__bpyt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        twsj__cypt = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, twsj__cypt)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zyzbd__iunoz, = args
        rfl__fxzwy = signature.return_type
        cvk__jwtsd = cgutils.create_struct_proxy(rfl__fxzwy)(context, builder)
        cvk__jwtsd.obj = zyzbd__iunoz
        context.nrt.incref(builder, signature.args[0], zyzbd__iunoz)
        return cvk__jwtsd._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                )
        atws__ntfw = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            yarl__vkeue = get_overload_const_int(idx.types[1])
            if yarl__vkeue < 0 or yarl__vkeue >= atws__ntfw:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            fvoj__cqb = [yarl__vkeue]
        else:
            is_out_series = False
            fvoj__cqb = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= atws__ntfw for
                ind in fvoj__cqb):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[fvoj__cqb])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                yarl__vkeue = fvoj__cqb[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, yarl__vkeue
                        )[idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    jtdsr__yll = 'def impl(I, idx):\n'
    jtdsr__yll += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        jtdsr__yll += f'  idx_t = {idx}\n'
    else:
        jtdsr__yll += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    ifsod__tohf = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    ywxwo__naiim = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(vuh__nhopg)})[idx_t]'
         for vuh__nhopg in col_names)
    if is_out_series:
        kjk__bqf = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        jtdsr__yll += f"""  return bodo.hiframes.pd_series_ext.init_series({ywxwo__naiim}, {ifsod__tohf}, {kjk__bqf})
"""
        mnsod__uapik = {}
        exec(jtdsr__yll, {'bodo': bodo}, mnsod__uapik)
        return mnsod__uapik['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll, col_names,
        ywxwo__naiim, ifsod__tohf)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    jtdsr__yll = 'def impl(I, idx):\n'
    jtdsr__yll += '  df = I._obj\n'
    qqpl__pvq = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(vuh__nhopg)})[{idx}]'
         for vuh__nhopg in col_names)
    jtdsr__yll += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    jtdsr__yll += f"""  return bodo.hiframes.pd_series_ext.init_series(({qqpl__pvq},), row_idx, None)
"""
    mnsod__uapik = {}
    exec(jtdsr__yll, {'bodo': bodo}, mnsod__uapik)
    impl = mnsod__uapik['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wuh__bpyt = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(wuh__bpyt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        twsj__cypt = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, twsj__cypt)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zyzbd__iunoz, = args
        mhwq__gmal = signature.return_type
        xxmz__axrk = cgutils.create_struct_proxy(mhwq__gmal)(context, builder)
        xxmz__axrk.obj = zyzbd__iunoz
        context.nrt.incref(builder, signature.args[0], zyzbd__iunoz)
        return xxmz__axrk._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        jtdsr__yll = 'def impl(I, idx):\n'
        jtdsr__yll += '  df = I._obj\n'
        jtdsr__yll += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        ifsod__tohf = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        ywxwo__naiim = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx_t]'
            .format(df.columns.index(vuh__nhopg)) for vuh__nhopg in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll, df.
            columns, ywxwo__naiim, ifsod__tohf)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        anxee__knxi = idx.types[1]
        if is_overload_constant_str(anxee__knxi):
            ghrr__rjzrq = get_overload_const_str(anxee__knxi)
            yarl__vkeue = df.columns.index(ghrr__rjzrq)

            def impl_col_name(I, idx):
                df = I._obj
                ifsod__tohf = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                dxs__jztsl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, yarl__vkeue)
                return bodo.hiframes.pd_series_ext.init_series(dxs__jztsl,
                    ifsod__tohf, ghrr__rjzrq).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(anxee__knxi):
            col_idx_list = get_overload_const_list(anxee__knxi)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(vuh__nhopg in df.columns for
                vuh__nhopg in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        col_idx_list = list(pd.Series(df.columns, dtype=object)[col_idx_list])
    ywxwo__naiim = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx[0]]'
        .format(df.columns.index(vuh__nhopg)) for vuh__nhopg in col_idx_list)
    ifsod__tohf = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    jtdsr__yll = 'def impl(I, idx):\n'
    jtdsr__yll += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(jtdsr__yll,
        col_idx_list, ywxwo__naiim, ifsod__tohf)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wuh__bpyt = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(wuh__bpyt)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        twsj__cypt = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, twsj__cypt)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zyzbd__iunoz, = args
        ees__oeynp = signature.return_type
        sga__iov = cgutils.create_struct_proxy(ees__oeynp)(context, builder)
        sga__iov.obj = zyzbd__iunoz
        context.nrt.incref(builder, signature.args[0], zyzbd__iunoz)
        return sga__iov._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                )
        yarl__vkeue = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            dxs__jztsl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                yarl__vkeue)
            return dxs__jztsl[idx[0]]
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        yarl__vkeue = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[yarl__vkeue]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            dxs__jztsl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                yarl__vkeue)
            dxs__jztsl[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    sga__iov = cgutils.create_struct_proxy(fromty)(context, builder, val)
    gko__jkzlf = context.cast(builder, sga__iov.obj, fromty.df_type, toty.
        df_type)
    heqg__vvg = cgutils.create_struct_proxy(toty)(context, builder)
    heqg__vvg.obj = gko__jkzlf
    return heqg__vvg._getvalue()
