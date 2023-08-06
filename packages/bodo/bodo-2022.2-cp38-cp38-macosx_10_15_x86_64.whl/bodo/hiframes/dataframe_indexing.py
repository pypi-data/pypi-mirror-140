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
            wkgdg__gwk = idx
            jby__pdzpd = df.data
            xutn__lymn = df.columns
            idvc__ggqoe = self.replace_range_with_numeric_idx_if_needed(df,
                wkgdg__gwk)
            dqo__fsvu = DataFrameType(jby__pdzpd, idvc__ggqoe, xutn__lymn)
            return dqo__fsvu(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            zwd__feuc = idx.types[0]
            ogdwg__tsvl = idx.types[1]
            if isinstance(zwd__feuc, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(ogdwg__tsvl):
                    tmprb__kjv = get_overload_const_str(ogdwg__tsvl)
                    if tmprb__kjv not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, tmprb__kjv))
                    krvez__kte = df.columns.index(tmprb__kjv)
                    return df.data[krvez__kte].dtype(*args)
                if isinstance(ogdwg__tsvl, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(zwd__feuc
                ) and zwd__feuc.dtype == types.bool_ or isinstance(zwd__feuc,
                types.SliceType):
                idvc__ggqoe = self.replace_range_with_numeric_idx_if_needed(df,
                    zwd__feuc)
                if is_overload_constant_str(ogdwg__tsvl):
                    ycf__veuhy = get_overload_const_str(ogdwg__tsvl)
                    if ycf__veuhy not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {ycf__veuhy}'
                            )
                    krvez__kte = df.columns.index(ycf__veuhy)
                    vgvkz__prg = df.data[krvez__kte]
                    jedcj__omltd = vgvkz__prg.dtype
                    uyvtq__hwzfe = types.literal(df.columns[krvez__kte])
                    dqo__fsvu = bodo.SeriesType(jedcj__omltd, vgvkz__prg,
                        idvc__ggqoe, uyvtq__hwzfe)
                    return dqo__fsvu(*args)
                if isinstance(ogdwg__tsvl, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html.'
                        )
                elif is_overload_constant_list(ogdwg__tsvl):
                    tou__qkrvo = get_overload_const_list(ogdwg__tsvl)
                    exev__jbi = types.unliteral(ogdwg__tsvl)
                    if exev__jbi.dtype == types.bool_:
                        if len(df.columns) != len(tou__qkrvo):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {tou__qkrvo} has {len(tou__qkrvo)} values'
                                )
                        fof__avbsf = []
                        xatj__iwtg = []
                        for vvoyr__css in range(len(tou__qkrvo)):
                            if tou__qkrvo[vvoyr__css]:
                                fof__avbsf.append(df.columns[vvoyr__css])
                                xatj__iwtg.append(df.data[vvoyr__css])
                        crz__evha = tuple()
                        dqo__fsvu = DataFrameType(tuple(xatj__iwtg),
                            idvc__ggqoe, tuple(fof__avbsf))
                        return dqo__fsvu(*args)
                    elif exev__jbi.dtype == bodo.string_type:
                        crz__evha, xatj__iwtg = self.get_kept_cols_and_data(df,
                            tou__qkrvo)
                        dqo__fsvu = DataFrameType(xatj__iwtg, idvc__ggqoe,
                            crz__evha)
                        return dqo__fsvu(*args)
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
                fof__avbsf = []
                xatj__iwtg = []
                for vvoyr__css, yqee__rskk in enumerate(df.columns):
                    if yqee__rskk[0] != ind_val:
                        continue
                    fof__avbsf.append(yqee__rskk[1] if len(yqee__rskk) == 2
                         else yqee__rskk[1:])
                    xatj__iwtg.append(df.data[vvoyr__css])
                vgvkz__prg = tuple(xatj__iwtg)
                vqrvm__dbo = df.index
                zhh__pabuz = tuple(fof__avbsf)
                dqo__fsvu = DataFrameType(vgvkz__prg, vqrvm__dbo, zhh__pabuz)
                return dqo__fsvu(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                krvez__kte = df.columns.index(ind_val)
                vgvkz__prg = df.data[krvez__kte]
                jedcj__omltd = vgvkz__prg.dtype
                vqrvm__dbo = df.index
                uyvtq__hwzfe = types.literal(df.columns[krvez__kte])
                dqo__fsvu = bodo.SeriesType(jedcj__omltd, vgvkz__prg,
                    vqrvm__dbo, uyvtq__hwzfe)
                return dqo__fsvu(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            vgvkz__prg = df.data
            vqrvm__dbo = self.replace_range_with_numeric_idx_if_needed(df, ind)
            zhh__pabuz = df.columns
            dqo__fsvu = DataFrameType(vgvkz__prg, vqrvm__dbo, zhh__pabuz,
                is_table_format=df.is_table_format)
            return dqo__fsvu(*args)
        elif is_overload_constant_list(ind):
            ayc__fkt = get_overload_const_list(ind)
            zhh__pabuz, vgvkz__prg = self.get_kept_cols_and_data(df, ayc__fkt)
            vqrvm__dbo = df.index
            dqo__fsvu = DataFrameType(vgvkz__prg, vqrvm__dbo, zhh__pabuz)
            return dqo__fsvu(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/source/programming_with_bodo/require_constants.html'
            )

    def get_kept_cols_and_data(self, df, cols_to_keep_list):
        for bxn__xqf in cols_to_keep_list:
            if bxn__xqf not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(bxn__xqf, df.columns))
        zhh__pabuz = tuple(cols_to_keep_list)
        vgvkz__prg = tuple(df.data[df.columns.index(nimu__tewku)] for
            nimu__tewku in zhh__pabuz)
        return zhh__pabuz, vgvkz__prg

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        idvc__ggqoe = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return idvc__ggqoe


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
            fof__avbsf = []
            xatj__iwtg = []
            for vvoyr__css, yqee__rskk in enumerate(df.columns):
                if yqee__rskk[0] != ind_val:
                    continue
                fof__avbsf.append(yqee__rskk[1] if len(yqee__rskk) == 2 else
                    yqee__rskk[1:])
                xatj__iwtg.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(vvoyr__css))
            rjp__qsrbf = 'def impl(df, ind):\n'
            zzfkq__oirq = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf,
                fof__avbsf, ', '.join(xatj__iwtg), zzfkq__oirq)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        ayc__fkt = get_overload_const_list(ind)
        for bxn__xqf in ayc__fkt:
            if bxn__xqf not in df.columns:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(bxn__xqf, df.columns))
        xatj__iwtg = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}).copy()'
            .format(df.columns.index(bxn__xqf)) for bxn__xqf in ayc__fkt)
        rjp__qsrbf = 'def impl(df, ind):\n'
        zzfkq__oirq = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf,
            ayc__fkt, xatj__iwtg, zzfkq__oirq)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        rjp__qsrbf = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            rjp__qsrbf += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        zzfkq__oirq = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            xatj__iwtg = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            xatj__iwtg = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(bxn__xqf)})[ind]'
                 for bxn__xqf in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf, df.
            columns, xatj__iwtg, zzfkq__oirq, out_df_type=df)
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
        nimu__tewku = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(nimu__tewku)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ctwmn__gysv = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, ctwmn__gysv)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        nmqv__jkxe, = args
        gncg__xrxy = signature.return_type
        qpwx__dlknm = cgutils.create_struct_proxy(gncg__xrxy)(context, builder)
        qpwx__dlknm.obj = nmqv__jkxe
        context.nrt.incref(builder, signature.args[0], nmqv__jkxe)
        return qpwx__dlknm._getvalue()
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
        rfnh__iofuu = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            wodct__ljz = get_overload_const_int(idx.types[1])
            if wodct__ljz < 0 or wodct__ljz >= rfnh__iofuu:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            lwkdn__jvl = [wodct__ljz]
        else:
            is_out_series = False
            lwkdn__jvl = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >=
                rfnh__iofuu for ind in lwkdn__jvl):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[lwkdn__jvl])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                wodct__ljz = lwkdn__jvl[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, wodct__ljz)
                        [idx[0]])
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
    rjp__qsrbf = 'def impl(I, idx):\n'
    rjp__qsrbf += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        rjp__qsrbf += f'  idx_t = {idx}\n'
    else:
        rjp__qsrbf += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    zzfkq__oirq = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    xatj__iwtg = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(bxn__xqf)})[idx_t]'
         for bxn__xqf in col_names)
    if is_out_series:
        axnq__rbvqf = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        rjp__qsrbf += f"""  return bodo.hiframes.pd_series_ext.init_series({xatj__iwtg}, {zzfkq__oirq}, {axnq__rbvqf})
"""
        ilcmk__cgl = {}
        exec(rjp__qsrbf, {'bodo': bodo}, ilcmk__cgl)
        return ilcmk__cgl['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf, col_names,
        xatj__iwtg, zzfkq__oirq)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    rjp__qsrbf = 'def impl(I, idx):\n'
    rjp__qsrbf += '  df = I._obj\n'
    cchbw__wnlrw = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(bxn__xqf)})[{idx}]'
         for bxn__xqf in col_names)
    rjp__qsrbf += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    rjp__qsrbf += f"""  return bodo.hiframes.pd_series_ext.init_series(({cchbw__wnlrw},), row_idx, None)
"""
    ilcmk__cgl = {}
    exec(rjp__qsrbf, {'bodo': bodo}, ilcmk__cgl)
    impl = ilcmk__cgl['impl']
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
        nimu__tewku = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(nimu__tewku)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ctwmn__gysv = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, ctwmn__gysv)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        nmqv__jkxe, = args
        iuz__jxrs = signature.return_type
        covk__ryej = cgutils.create_struct_proxy(iuz__jxrs)(context, builder)
        covk__ryej.obj = nmqv__jkxe
        context.nrt.incref(builder, signature.args[0], nmqv__jkxe)
        return covk__ryej._getvalue()
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
        rjp__qsrbf = 'def impl(I, idx):\n'
        rjp__qsrbf += '  df = I._obj\n'
        rjp__qsrbf += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        zzfkq__oirq = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        xatj__iwtg = ', '.join(
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx_t]'
            .format(df.columns.index(bxn__xqf)) for bxn__xqf in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf, df.
            columns, xatj__iwtg, zzfkq__oirq)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        glv__iheei = idx.types[1]
        if is_overload_constant_str(glv__iheei):
            ybx__wcpf = get_overload_const_str(glv__iheei)
            wodct__ljz = df.columns.index(ybx__wcpf)

            def impl_col_name(I, idx):
                df = I._obj
                zzfkq__oirq = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                kcl__inzpg = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, wodct__ljz)
                return bodo.hiframes.pd_series_ext.init_series(kcl__inzpg,
                    zzfkq__oirq, ybx__wcpf).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(glv__iheei):
            col_idx_list = get_overload_const_list(glv__iheei)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(bxn__xqf in df.columns for
                bxn__xqf in col_idx_list):
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
    xatj__iwtg = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[idx[0]]'
        .format(df.columns.index(bxn__xqf)) for bxn__xqf in col_idx_list)
    zzfkq__oirq = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    rjp__qsrbf = 'def impl(I, idx):\n'
    rjp__qsrbf += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(rjp__qsrbf,
        col_idx_list, xatj__iwtg, zzfkq__oirq)


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
        nimu__tewku = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(nimu__tewku)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ctwmn__gysv = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, ctwmn__gysv)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        nmqv__jkxe, = args
        uoxd__frgd = signature.return_type
        pset__aqqo = cgutils.create_struct_proxy(uoxd__frgd)(context, builder)
        pset__aqqo.obj = nmqv__jkxe
        context.nrt.incref(builder, signature.args[0], nmqv__jkxe)
        return pset__aqqo._getvalue()
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
        wodct__ljz = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            kcl__inzpg = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                wodct__ljz)
            return kcl__inzpg[idx[0]]
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
        wodct__ljz = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[wodct__ljz]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            kcl__inzpg = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                wodct__ljz)
            kcl__inzpg[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    pset__aqqo = cgutils.create_struct_proxy(fromty)(context, builder, val)
    voev__ivdss = context.cast(builder, pset__aqqo.obj, fromty.df_type,
        toty.df_type)
    swm__qaaya = cgutils.create_struct_proxy(toty)(context, builder)
    swm__qaaya.obj = voev__ivdss
    return swm__qaaya._getvalue()
