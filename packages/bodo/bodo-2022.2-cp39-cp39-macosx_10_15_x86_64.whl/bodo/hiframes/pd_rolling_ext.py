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
        syh__cvsa = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, syh__cvsa)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    dqwz__etsn = dict(win_type=win_type, axis=axis, closed=closed)
    qis__cycxu = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', dqwz__etsn, qis__cycxu,
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
    dqwz__etsn = dict(win_type=win_type, axis=axis, closed=closed)
    qis__cycxu = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', dqwz__etsn, qis__cycxu,
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
        ywft__tnez, jgqd__tlht, gjgxv__refy, bdwy__ova, sysa__iogp = args
        tziw__nrty = signature.return_type
        kuq__jge = cgutils.create_struct_proxy(tziw__nrty)(context, builder)
        kuq__jge.obj = ywft__tnez
        kuq__jge.window = jgqd__tlht
        kuq__jge.min_periods = gjgxv__refy
        kuq__jge.center = bdwy__ova
        context.nrt.incref(builder, signature.args[0], ywft__tnez)
        context.nrt.incref(builder, signature.args[1], jgqd__tlht)
        context.nrt.incref(builder, signature.args[2], gjgxv__refy)
        context.nrt.incref(builder, signature.args[3], bdwy__ova)
        return kuq__jge._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    tziw__nrty = RollingType(obj_type, window_type, on, selection, False)
    return tziw__nrty(obj_type, window_type, min_periods_type, center_type,
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
    vaz__aqp = not isinstance(rolling.window_type, types.Integer)
    nfjom__cgsrh = 'variable' if vaz__aqp else 'fixed'
    dqy__slra = 'None'
    if vaz__aqp:
        dqy__slra = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    jvek__nwy = []
    czzd__wnxbi = 'on_arr, ' if vaz__aqp else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{nfjom__cgsrh}(bodo.hiframes.pd_series_ext.get_series_data(df), {czzd__wnxbi}index_arr, window, minp, center, func, raw)'
            , dqy__slra, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    tku__bpwxp = rolling.obj_type.data
    out_cols = []
    for zzap__wotni in rolling.selection:
        yywz__snac = rolling.obj_type.columns.index(zzap__wotni)
        if zzap__wotni == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            khd__gpp = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {yywz__snac})'
                )
            out_cols.append(zzap__wotni)
        else:
            if not isinstance(tku__bpwxp[yywz__snac].dtype, (types.Boolean,
                types.Number)):
                continue
            khd__gpp = (
                f'bodo.hiframes.rolling.rolling_{nfjom__cgsrh}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {yywz__snac}), {czzd__wnxbi}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(zzap__wotni)
        jvek__nwy.append(khd__gpp)
    return ', '.join(jvek__nwy), dqy__slra, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    dqwz__etsn = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    qis__cycxu = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', dqwz__etsn, qis__cycxu,
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
    dqwz__etsn = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    qis__cycxu = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', dqwz__etsn, qis__cycxu,
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
        bnjr__kbh = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        hcl__rko = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{qujl__cjxi}'" if
                isinstance(qujl__cjxi, str) else f'{qujl__cjxi}' for
                qujl__cjxi in rolling.selection if qujl__cjxi != rolling.on))
        tccc__ftf = eyrjw__fex = ''
        if fname == 'apply':
            tccc__ftf = 'func, raw, args, kwargs'
            eyrjw__fex = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            tccc__ftf = eyrjw__fex = 'other, pairwise'
        if fname == 'cov':
            tccc__ftf = eyrjw__fex = 'other, pairwise, ddof'
        odick__tseh = (
            f'lambda df, window, minp, center, {tccc__ftf}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {hcl__rko}){selection}.{fname}({eyrjw__fex})'
            )
        bnjr__kbh += f"""  return rolling.obj.apply({odick__tseh}, rolling.window, rolling.min_periods, rolling.center, {tccc__ftf})
"""
        vaz__jjhv = {}
        exec(bnjr__kbh, {'bodo': bodo}, vaz__jjhv)
        impl = vaz__jjhv['impl']
        return impl
    yns__jcag = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if yns__jcag else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if yns__jcag else rolling.obj_type.columns
        other_cols = None if yns__jcag else other.columns
        jvek__nwy, dqy__slra = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        jvek__nwy, dqy__slra, out_cols = _gen_df_rolling_out_data(rolling)
    uhpbn__bck = yns__jcag or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    lrzwd__qjwsr = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    lrzwd__qjwsr += '  df = rolling.obj\n'
    lrzwd__qjwsr += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if yns__jcag else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    qtrki__ggau = 'None'
    if yns__jcag:
        qtrki__ggau = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif uhpbn__bck:
        zzap__wotni = (set(out_cols) - set([rolling.on])).pop()
        qtrki__ggau = f"'{zzap__wotni}'" if isinstance(zzap__wotni, str
            ) else str(zzap__wotni)
    lrzwd__qjwsr += f'  name = {qtrki__ggau}\n'
    lrzwd__qjwsr += '  window = rolling.window\n'
    lrzwd__qjwsr += '  center = rolling.center\n'
    lrzwd__qjwsr += '  minp = rolling.min_periods\n'
    lrzwd__qjwsr += f'  on_arr = {dqy__slra}\n'
    if fname == 'apply':
        lrzwd__qjwsr += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        lrzwd__qjwsr += f"  func = '{fname}'\n"
        lrzwd__qjwsr += f'  index_arr = None\n'
        lrzwd__qjwsr += f'  raw = False\n'
    if uhpbn__bck:
        lrzwd__qjwsr += (
            f'  return bodo.hiframes.pd_series_ext.init_series({jvek__nwy}, index, name)'
            )
        vaz__jjhv = {}
        ykkq__urk = {'bodo': bodo}
        exec(lrzwd__qjwsr, ykkq__urk, vaz__jjhv)
        impl = vaz__jjhv['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(lrzwd__qjwsr, out_cols,
        jvek__nwy)


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
        sifi__rvxne = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(sifi__rvxne)


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
    vidps__yjay = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(vidps__yjay) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    vaz__aqp = not isinstance(window_type, types.Integer)
    dqy__slra = 'None'
    if vaz__aqp:
        dqy__slra = 'bodo.utils.conversion.index_to_array(index)'
    czzd__wnxbi = 'on_arr, ' if vaz__aqp else ''
    jvek__nwy = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {czzd__wnxbi}window, minp, center)'
            , dqy__slra)
    for zzap__wotni in out_cols:
        if zzap__wotni in df_cols and zzap__wotni in other_cols:
            lnom__rfeq = df_cols.index(zzap__wotni)
            djqmb__huv = other_cols.index(zzap__wotni)
            khd__gpp = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {lnom__rfeq}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {djqmb__huv}), {czzd__wnxbi}window, minp, center)'
                )
        else:
            khd__gpp = 'np.full(len(df), np.nan)'
        jvek__nwy.append(khd__gpp)
    return ', '.join(jvek__nwy), dqy__slra


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    ffo__jqgkl = {'pairwise': pairwise, 'ddof': ddof}
    pksbw__qys = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        ffo__jqgkl, pksbw__qys, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    ffo__jqgkl = {'ddof': ddof, 'pairwise': pairwise}
    pksbw__qys = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        ffo__jqgkl, pksbw__qys, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, lzkm__dtjhx = args
        if isinstance(rolling, RollingType):
            vidps__yjay = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(lzkm__dtjhx, (tuple, list)):
                if len(set(lzkm__dtjhx).difference(set(vidps__yjay))) > 0:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(lzkm__dtjhx).difference(set(vidps__yjay))))
                selection = list(lzkm__dtjhx)
            else:
                if lzkm__dtjhx not in vidps__yjay:
                    raise_const_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(lzkm__dtjhx))
                selection = [lzkm__dtjhx]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            ggwnd__evvzw = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(ggwnd__evvzw, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        vidps__yjay = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            vidps__yjay = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            vidps__yjay = rolling.obj_type.columns
        if attr in vidps__yjay:
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
    coiqo__gem = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    tku__bpwxp = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in coiqo__gem):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        umuc__bsye = tku__bpwxp[coiqo__gem.index(get_literal_value(on))]
        if not isinstance(umuc__bsye, types.Array
            ) or umuc__bsye.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(vaos__hmurc.dtype, (types.Boolean, types.Number)) for
        vaos__hmurc in tku__bpwxp):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
