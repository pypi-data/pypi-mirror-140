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
        ooh__bzi = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, ooh__bzi)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    rvxoo__oko = dict(win_type=win_type, axis=axis, closed=closed)
    uxart__upd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', rvxoo__oko, uxart__upd,
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
    rvxoo__oko = dict(win_type=win_type, axis=axis, closed=closed)
    uxart__upd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', rvxoo__oko, uxart__upd,
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
        pnw__wsj, cqu__jtlqe, ibhot__ymgfr, isl__osoi, thffn__rgg = args
        mhw__zyeve = signature.return_type
        kbmvn__mdi = cgutils.create_struct_proxy(mhw__zyeve)(context, builder)
        kbmvn__mdi.obj = pnw__wsj
        kbmvn__mdi.window = cqu__jtlqe
        kbmvn__mdi.min_periods = ibhot__ymgfr
        kbmvn__mdi.center = isl__osoi
        context.nrt.incref(builder, signature.args[0], pnw__wsj)
        context.nrt.incref(builder, signature.args[1], cqu__jtlqe)
        context.nrt.incref(builder, signature.args[2], ibhot__ymgfr)
        context.nrt.incref(builder, signature.args[3], isl__osoi)
        return kbmvn__mdi._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    mhw__zyeve = RollingType(obj_type, window_type, on, selection, False)
    return mhw__zyeve(obj_type, window_type, min_periods_type, center_type,
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
    jlab__kumjg = not isinstance(rolling.window_type, types.Integer)
    dezkl__wmc = 'variable' if jlab__kumjg else 'fixed'
    ujia__wcv = 'None'
    if jlab__kumjg:
        ujia__wcv = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    uzodt__upk = []
    ryr__bbzv = 'on_arr, ' if jlab__kumjg else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{dezkl__wmc}(bodo.hiframes.pd_series_ext.get_series_data(df), {ryr__bbzv}index_arr, window, minp, center, func, raw)'
            , ujia__wcv, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    ibvrq__poevn = rolling.obj_type.data
    out_cols = []
    for zcn__gkhg in rolling.selection:
        ivslf__wlq = rolling.obj_type.columns.index(zcn__gkhg)
        if zcn__gkhg == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            muxr__waen = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ivslf__wlq})'
                )
            out_cols.append(zcn__gkhg)
        else:
            if not isinstance(ibvrq__poevn[ivslf__wlq].dtype, (types.
                Boolean, types.Number)):
                continue
            muxr__waen = (
                f'bodo.hiframes.rolling.rolling_{dezkl__wmc}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ivslf__wlq}), {ryr__bbzv}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(zcn__gkhg)
        uzodt__upk.append(muxr__waen)
    return ', '.join(uzodt__upk), ujia__wcv, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    rvxoo__oko = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    uxart__upd = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', rvxoo__oko, uxart__upd,
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
    rvxoo__oko = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    uxart__upd = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', rvxoo__oko, uxart__upd,
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
        brn__jtq = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        txzoy__iwue = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{klm__xwj}'" if
                isinstance(klm__xwj, str) else f'{klm__xwj}' for klm__xwj in
                rolling.selection if klm__xwj != rolling.on))
        nwjf__vmmjf = xwsac__niw = ''
        if fname == 'apply':
            nwjf__vmmjf = 'func, raw, args, kwargs'
            xwsac__niw = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            nwjf__vmmjf = xwsac__niw = 'other, pairwise'
        if fname == 'cov':
            nwjf__vmmjf = xwsac__niw = 'other, pairwise, ddof'
        wprdx__rxwe = (
            f'lambda df, window, minp, center, {nwjf__vmmjf}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {txzoy__iwue}){selection}.{fname}({xwsac__niw})'
            )
        brn__jtq += f"""  return rolling.obj.apply({wprdx__rxwe}, rolling.window, rolling.min_periods, rolling.center, {nwjf__vmmjf})
"""
        uaktu__gsh = {}
        exec(brn__jtq, {'bodo': bodo}, uaktu__gsh)
        impl = uaktu__gsh['impl']
        return impl
    zhtea__jtebc = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if zhtea__jtebc else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if zhtea__jtebc else rolling.obj_type.columns
        other_cols = None if zhtea__jtebc else other.columns
        uzodt__upk, ujia__wcv = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        uzodt__upk, ujia__wcv, out_cols = _gen_df_rolling_out_data(rolling)
    afxq__vyw = zhtea__jtebc or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    eggfs__muqbg = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    eggfs__muqbg += '  df = rolling.obj\n'
    eggfs__muqbg += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if zhtea__jtebc else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    ozto__isur = 'None'
    if zhtea__jtebc:
        ozto__isur = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif afxq__vyw:
        zcn__gkhg = (set(out_cols) - set([rolling.on])).pop()
        ozto__isur = f"'{zcn__gkhg}'" if isinstance(zcn__gkhg, str) else str(
            zcn__gkhg)
    eggfs__muqbg += f'  name = {ozto__isur}\n'
    eggfs__muqbg += '  window = rolling.window\n'
    eggfs__muqbg += '  center = rolling.center\n'
    eggfs__muqbg += '  minp = rolling.min_periods\n'
    eggfs__muqbg += f'  on_arr = {ujia__wcv}\n'
    if fname == 'apply':
        eggfs__muqbg += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        eggfs__muqbg += f"  func = '{fname}'\n"
        eggfs__muqbg += f'  index_arr = None\n'
        eggfs__muqbg += f'  raw = False\n'
    if afxq__vyw:
        eggfs__muqbg += (
            f'  return bodo.hiframes.pd_series_ext.init_series({uzodt__upk}, index, name)'
            )
        uaktu__gsh = {}
        wql__kadzh = {'bodo': bodo}
        exec(eggfs__muqbg, wql__kadzh, uaktu__gsh)
        impl = uaktu__gsh['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(eggfs__muqbg, out_cols,
        uzodt__upk)


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
        zrq__lmbxx = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(zrq__lmbxx)


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
    jny__fsz = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(jny__fsz) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    jlab__kumjg = not isinstance(window_type, types.Integer)
    ujia__wcv = 'None'
    if jlab__kumjg:
        ujia__wcv = 'bodo.utils.conversion.index_to_array(index)'
    ryr__bbzv = 'on_arr, ' if jlab__kumjg else ''
    uzodt__upk = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {ryr__bbzv}window, minp, center)'
            , ujia__wcv)
    for zcn__gkhg in out_cols:
        if zcn__gkhg in df_cols and zcn__gkhg in other_cols:
            bgl__ogu = df_cols.index(zcn__gkhg)
            fpqih__yoqd = other_cols.index(zcn__gkhg)
            muxr__waen = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {bgl__ogu}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {fpqih__yoqd}), {ryr__bbzv}window, minp, center)'
                )
        else:
            muxr__waen = 'np.full(len(df), np.nan)'
        uzodt__upk.append(muxr__waen)
    return ', '.join(uzodt__upk), ujia__wcv


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    dklj__eytq = {'pairwise': pairwise, 'ddof': ddof}
    yfm__qspn = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        dklj__eytq, yfm__qspn, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    dklj__eytq = {'ddof': ddof, 'pairwise': pairwise}
    yfm__qspn = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        dklj__eytq, yfm__qspn, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, rramo__baklp = args
        if isinstance(rolling, RollingType):
            jny__fsz = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(rramo__baklp, (tuple, list)):
                if len(set(rramo__baklp).difference(set(jny__fsz))) > 0:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(rramo__baklp).difference(set(jny__fsz))))
                selection = list(rramo__baklp)
            else:
                if rramo__baklp not in jny__fsz:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(rramo__baklp))
                selection = [rramo__baklp]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            ymdub__cryob = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(ymdub__cryob, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        jny__fsz = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            jny__fsz = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            jny__fsz = rolling.obj_type.columns
        if attr in jny__fsz:
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
    weo__rlr = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    ibvrq__poevn = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in weo__rlr):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        npk__khf = ibvrq__poevn[weo__rlr.index(get_literal_value(on))]
        if not isinstance(npk__khf, types.Array
            ) or npk__khf.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(sfg__fuoq.dtype, (types.Boolean, types.Number)) for
        sfg__fuoq in ibvrq__poevn):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
