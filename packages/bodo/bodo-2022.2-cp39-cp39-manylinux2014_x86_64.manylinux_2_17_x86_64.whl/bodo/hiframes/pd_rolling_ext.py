"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error, raise_const_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pedl__yedfq = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, pedl__yedfq)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    srda__aauug = dict(win_type=win_type, axis=axis, closed=closed)
    jfxiu__vfnkj = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', srda__aauug, jfxiu__vfnkj,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    srda__aauug = dict(win_type=win_type, axis=axis, closed=closed)
    jfxiu__vfnkj = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', srda__aauug, jfxiu__vfnkj,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        sjjc__ymcm, occ__yjg, tmpel__ptzz, zcacc__yssoe, wqy__hfbm = args
        sckg__hvnva = signature.return_type
        iysga__ovkhw = cgutils.create_struct_proxy(sckg__hvnva)(context,
            builder)
        iysga__ovkhw.obj = sjjc__ymcm
        iysga__ovkhw.window = occ__yjg
        iysga__ovkhw.min_periods = tmpel__ptzz
        iysga__ovkhw.center = zcacc__yssoe
        context.nrt.incref(builder, signature.args[0], sjjc__ymcm)
        context.nrt.incref(builder, signature.args[1], occ__yjg)
        context.nrt.incref(builder, signature.args[2], tmpel__ptzz)
        context.nrt.incref(builder, signature.args[3], zcacc__yssoe)
        return iysga__ovkhw._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    sckg__hvnva = RollingType(obj_type, window_type, on, selection, False)
    return sckg__hvnva(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    kyksd__sng = not isinstance(rolling.window_type, types.Integer)
    xyxal__wgdz = 'variable' if kyksd__sng else 'fixed'
    cde__qzmav = 'None'
    if kyksd__sng:
        cde__qzmav = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    keck__sgii = []
    hyzxd__pozr = 'on_arr, ' if kyksd__sng else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{xyxal__wgdz}(bodo.hiframes.pd_series_ext.get_series_data(df), {hyzxd__pozr}index_arr, window, minp, center, func, raw)'
            , cde__qzmav, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    ffmw__ujaoz = rolling.obj_type.data
    out_cols = []
    for uvz__nxkmt in rolling.selection:
        gqoz__wht = rolling.obj_type.columns.index(uvz__nxkmt)
        if uvz__nxkmt == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            ogw__gkjvo = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {gqoz__wht})'
                )
            out_cols.append(uvz__nxkmt)
        else:
            if not isinstance(ffmw__ujaoz[gqoz__wht].dtype, (types.Boolean,
                types.Number)):
                continue
            ogw__gkjvo = (
                f'bodo.hiframes.rolling.rolling_{xyxal__wgdz}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {gqoz__wht}), {hyzxd__pozr}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(uvz__nxkmt)
        keck__sgii.append(ogw__gkjvo)
    return ', '.join(keck__sgii), cde__qzmav, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    srda__aauug = dict(engine=engine, engine_kwargs=engine_kwargs, args=
        args, kwargs=kwargs)
    jfxiu__vfnkj = dict(engine=None, engine_kwargs=None, args=None, kwargs=None
        )
    check_unsupported_args('Rolling.apply', srda__aauug, jfxiu__vfnkj,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    srda__aauug = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    jfxiu__vfnkj = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', srda__aauug, jfxiu__vfnkj,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        tusyd__kbf = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        eef__cpoi = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{bnzm__bphjh}'" if
                isinstance(bnzm__bphjh, str) else f'{bnzm__bphjh}' for
                bnzm__bphjh in rolling.selection if bnzm__bphjh != rolling.on))
        rfrdi__hpr = mrisu__kmrzv = ''
        if fname == 'apply':
            rfrdi__hpr = 'func, raw, args, kwargs'
            mrisu__kmrzv = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            rfrdi__hpr = mrisu__kmrzv = 'other, pairwise'
        if fname == 'cov':
            rfrdi__hpr = mrisu__kmrzv = 'other, pairwise, ddof'
        jlv__uyz = (
            f'lambda df, window, minp, center, {rfrdi__hpr}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {eef__cpoi}){selection}.{fname}({mrisu__kmrzv})'
            )
        tusyd__kbf += f"""  return rolling.obj.apply({jlv__uyz}, rolling.window, rolling.min_periods, rolling.center, {rfrdi__hpr})
"""
        ojxxr__ndgn = {}
        exec(tusyd__kbf, {'bodo': bodo}, ojxxr__ndgn)
        impl = ojxxr__ndgn['impl']
        return impl
    qyahe__yocn = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if qyahe__yocn else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if qyahe__yocn else rolling.obj_type.columns
        other_cols = None if qyahe__yocn else other.columns
        keck__sgii, cde__qzmav = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        keck__sgii, cde__qzmav, out_cols = _gen_df_rolling_out_data(rolling)
    mlj__nqoay = qyahe__yocn or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    ypnt__xyv = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    ypnt__xyv += '  df = rolling.obj\n'
    ypnt__xyv += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if qyahe__yocn else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    hmyou__cdmup = 'None'
    if qyahe__yocn:
        hmyou__cdmup = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif mlj__nqoay:
        uvz__nxkmt = (set(out_cols) - set([rolling.on])).pop()
        hmyou__cdmup = f"'{uvz__nxkmt}'" if isinstance(uvz__nxkmt, str
            ) else str(uvz__nxkmt)
    ypnt__xyv += f'  name = {hmyou__cdmup}\n'
    ypnt__xyv += '  window = rolling.window\n'
    ypnt__xyv += '  center = rolling.center\n'
    ypnt__xyv += '  minp = rolling.min_periods\n'
    ypnt__xyv += f'  on_arr = {cde__qzmav}\n'
    if fname == 'apply':
        ypnt__xyv += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        ypnt__xyv += f"  func = '{fname}'\n"
        ypnt__xyv += f'  index_arr = None\n'
        ypnt__xyv += f'  raw = False\n'
    if mlj__nqoay:
        ypnt__xyv += (
            f'  return bodo.hiframes.pd_series_ext.init_series({keck__sgii}, index, name)'
            )
        ojxxr__ndgn = {}
        quz__hiead = {'bodo': bodo}
        exec(ypnt__xyv, quz__hiead, ojxxr__ndgn)
        impl = ojxxr__ndgn['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(ypnt__xyv, out_cols,
        keck__sgii)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        iwbqe__zrip = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(iwbqe__zrip)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    cbq__npv = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(cbq__npv) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    kyksd__sng = not isinstance(window_type, types.Integer)
    cde__qzmav = 'None'
    if kyksd__sng:
        cde__qzmav = 'bodo.utils.conversion.index_to_array(index)'
    hyzxd__pozr = 'on_arr, ' if kyksd__sng else ''
    keck__sgii = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {hyzxd__pozr}window, minp, center)'
            , cde__qzmav)
    for uvz__nxkmt in out_cols:
        if uvz__nxkmt in df_cols and uvz__nxkmt in other_cols:
            gpf__jwy = df_cols.index(uvz__nxkmt)
            siycf__zhqc = other_cols.index(uvz__nxkmt)
            ogw__gkjvo = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {gpf__jwy}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {siycf__zhqc}), {hyzxd__pozr}window, minp, center)'
                )
        else:
            ogw__gkjvo = 'np.full(len(df), np.nan)'
        keck__sgii.append(ogw__gkjvo)
    return ', '.join(keck__sgii), cde__qzmav


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    bxeuc__nanv = {'pairwise': pairwise, 'ddof': ddof}
    mrp__uatxp = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        bxeuc__nanv, mrp__uatxp, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    bxeuc__nanv = {'ddof': ddof, 'pairwise': pairwise}
    mrp__uatxp = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        bxeuc__nanv, mrp__uatxp, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, hbu__hlslo = args
        if isinstance(rolling, RollingType):
            cbq__npv = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(hbu__hlslo, (tuple, list)):
                if len(set(hbu__hlslo).difference(set(cbq__npv))) > 0:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(hbu__hlslo).difference(set(cbq__npv))))
                selection = list(hbu__hlslo)
            else:
                if hbu__hlslo not in cbq__npv:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(hbu__hlslo))
                selection = [hbu__hlslo]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            ylb__zpifo = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(ylb__zpifo, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        cbq__npv = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            cbq__npv = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            cbq__npv = rolling.obj_type.columns
        if attr in cbq__npv:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    pcyib__zfhdu = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    ffmw__ujaoz = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in pcyib__zfhdu):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        fjxpd__xth = ffmw__ujaoz[pcyib__zfhdu.index(get_literal_value(on))]
        if not isinstance(fjxpd__xth, types.Array
            ) or fjxpd__xth.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(rgp__kiart.dtype, (types.Boolean, types.Number)) for
        rgp__kiart in ffmw__ujaoz):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
