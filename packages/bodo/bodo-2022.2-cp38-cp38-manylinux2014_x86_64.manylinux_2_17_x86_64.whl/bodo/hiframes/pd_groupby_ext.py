"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import gen_const_tup, get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, raise_const_error
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False):
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eisxb__qyk = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, eisxb__qyk)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_const_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type=None,
    dropna_type=None):

    def codegen(context, builder, signature, args):
        ury__dmt = args[0]
        qowx__bhc = signature.return_type
        wcxz__nhkhr = cgutils.create_struct_proxy(qowx__bhc)(context, builder)
        wcxz__nhkhr.obj = ury__dmt
        context.nrt.incref(builder, signature.args[0], ury__dmt)
        return wcxz__nhkhr._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for hsh__akp in keys:
        selection.remove(hsh__akp)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    qowx__bhc = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return qowx__bhc(obj_type, by_type, as_index_type, dropna_type), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, xuu__rpbb = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(xuu__rpbb, (tuple, list)):
                if len(set(xuu__rpbb).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(xuu__rpbb).difference(set(grpby.df_type
                        .columns))))
                selection = xuu__rpbb
            else:
                if xuu__rpbb not in grpby.df_type.columns:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(xuu__rpbb))
                selection = xuu__rpbb,
                series_select = True
            mcnur__kagnq = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(mcnur__kagnq, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, xuu__rpbb = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            xuu__rpbb):
            mcnur__kagnq = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(xuu__rpbb)), {}).return_type
            return signature(mcnur__kagnq, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    xyu__maix = arr_type == ArrayItemArrayType(string_array_type)
    ngu__xcc = arr_type.dtype
    if isinstance(ngu__xcc, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {ngu__xcc} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(ngu__xcc, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {ngu__xcc} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(ngu__xcc,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(ngu__xcc, (types.Integer, types.Float, types.Boolean)):
        if xyu__maix or ngu__xcc == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(ngu__xcc, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not ngu__xcc.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {ngu__xcc} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(ngu__xcc, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    ngu__xcc = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(ngu__xcc, (types
            .Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(ngu__xcc, types.Integer):
            return IntDtype(ngu__xcc)
        return ngu__xcc
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        nfgma__ytbok = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{nfgma__ytbok}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for hsh__akp in grp.keys:
        if multi_level_names:
            gsytw__qau = hsh__akp, ''
        else:
            gsytw__qau = hsh__akp
        mwjl__nngiv = grp.df_type.columns.index(hsh__akp)
        data = grp.df_type.data[mwjl__nngiv]
        out_columns.append(gsytw__qau)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name == 'head':
        grp.dropna = False
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name == 'head':
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        ett__olv = tuple(grp.df_type.columns.index(grp.keys[whxmr__fhxle]) for
            whxmr__fhxle in range(len(grp.keys)))
        ppat__nbja = tuple(grp.df_type.data[mwjl__nngiv] for mwjl__nngiv in
            ett__olv)
        index = MultiIndexType(ppat__nbja, tuple(types.StringLiteral(
            hsh__akp) for hsh__akp in grp.keys))
    else:
        mwjl__nngiv = grp.df_type.columns.index(grp.keys[0])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(grp.df_type.
            data[mwjl__nngiv], types.StringLiteral(grp.keys[0]))
    dkkm__gbfk = {}
    mbcz__pruyo = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        dkkm__gbfk[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for qlp__wnryo in columns:
            mwjl__nngiv = grp.df_type.columns.index(qlp__wnryo)
            data = grp.df_type.data[mwjl__nngiv]
            mxu__wyvwj = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                mxu__wyvwj = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    kmlj__xxb = SeriesType(data.dtype, data, None, string_type)
                    zzhot__qxtnb = get_const_func_output_type(func, (
                        kmlj__xxb,), {}, typing_context, target_context)
                    if zzhot__qxtnb != ArrayItemArrayType(string_array_type):
                        zzhot__qxtnb = dtype_to_array_type(zzhot__qxtnb)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=qlp__wnryo, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    aizkg__gsu = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    kaers__zcj = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    bjry__wym = dict(numeric_only=aizkg__gsu, min_count=
                        kaers__zcj)
                    beo__gyma = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        bjry__wym, beo__gyma, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    aizkg__gsu = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    kaers__zcj = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    bjry__wym = dict(numeric_only=aizkg__gsu, min_count=
                        kaers__zcj)
                    beo__gyma = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        bjry__wym, beo__gyma, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    aizkg__gsu = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    bjry__wym = dict(numeric_only=aizkg__gsu)
                    beo__gyma = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        bjry__wym, beo__gyma, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    obvu__ypx = args[0] if len(args) > 0 else kws.pop('axis', 0
                        )
                    ypsni__kmhxo = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    bjry__wym = dict(axis=obvu__ypx, skipna=ypsni__kmhxo)
                    beo__gyma = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        bjry__wym, beo__gyma, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    dpm__xpsxf = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    bjry__wym = dict(ddof=dpm__xpsxf)
                    beo__gyma = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        bjry__wym, beo__gyma, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                zzhot__qxtnb, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                tav__cdi = zzhot__qxtnb
                out_data.append(tav__cdi)
                out_columns.append(qlp__wnryo)
                if func_name == 'agg':
                    rjibd__nnyt = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    dkkm__gbfk[qlp__wnryo, rjibd__nnyt] = qlp__wnryo
                else:
                    dkkm__gbfk[qlp__wnryo, func_name] = qlp__wnryo
                out_column_type.append(mxu__wyvwj)
            else:
                mbcz__pruyo.append(err_msg)
    if func_name == 'sum':
        jhvgm__ala = any([(ipul__yzlm == ColumnType.NumericalColumn.value) for
            ipul__yzlm in out_column_type])
        if jhvgm__ala:
            out_data = [ipul__yzlm for ipul__yzlm, bsjya__faqg in zip(
                out_data, out_column_type) if bsjya__faqg != ColumnType.
                NonNumericalColumn.value]
            out_columns = [ipul__yzlm for ipul__yzlm, bsjya__faqg in zip(
                out_columns, out_column_type) if bsjya__faqg != ColumnType.
                NonNumericalColumn.value]
            dkkm__gbfk = {}
            for qlp__wnryo in out_columns:
                if grp.as_index is False and qlp__wnryo in grp.keys:
                    continue
                dkkm__gbfk[qlp__wnryo, func_name] = qlp__wnryo
    yfad__jggp = len(mbcz__pruyo)
    if len(out_data) == 0:
        if yfad__jggp == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(yfad__jggp, ' was' if yfad__jggp == 1 else 's were',
                ','.join(mbcz__pruyo)))
    slztn__pqvg = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            zpipi__xls = IntDtype(out_data[0].dtype)
        else:
            zpipi__xls = out_data[0].dtype
        usoxl__eviny = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        slztn__pqvg = SeriesType(zpipi__xls, index=index, name_typ=usoxl__eviny
            )
    return signature(slztn__pqvg, *args), dkkm__gbfk


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    men__mwz = True
    if isinstance(f_val, str):
        men__mwz = False
        orf__ugq = f_val
    elif is_overload_constant_str(f_val):
        men__mwz = False
        orf__ugq = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        men__mwz = False
        orf__ugq = bodo.utils.typing.get_builtin_function_name(f_val)
    if not men__mwz:
        if orf__ugq not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {orf__ugq}')
        mcnur__kagnq = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(mcnur__kagnq, (), orf__ugq, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            cfs__bdo = types.functions.MakeFunctionLiteral(f_val)
        else:
            cfs__bdo = f_val
        validate_udf('agg', cfs__bdo)
        func = get_overload_const_func(cfs__bdo, None)
        zwsrp__bkj = func.code if hasattr(func, 'code') else func.__code__
        orf__ugq = zwsrp__bkj.co_name
        mcnur__kagnq = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(mcnur__kagnq, (), 'agg', typing_context,
            target_context, cfs__bdo)[0].return_type
    return orf__ugq, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    goox__lzb = kws and all(isinstance(uogt__nqznp, types.Tuple) and len(
        uogt__nqznp) == 2 for uogt__nqznp in kws.values())
    if is_overload_none(func) and not goox__lzb:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not goox__lzb:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    pvxhj__woht = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if goox__lzb or is_overload_constant_dict(func):
        if goox__lzb:
            aqhnf__zpa = [get_literal_value(sdi__nyypx) for sdi__nyypx,
                xdqxc__eshjj in kws.values()]
            xrc__vzrj = [get_literal_value(uwuor__gkva) for xdqxc__eshjj,
                uwuor__gkva in kws.values()]
        else:
            nxxxu__fbov = get_overload_constant_dict(func)
            aqhnf__zpa = tuple(nxxxu__fbov.keys())
            xrc__vzrj = tuple(nxxxu__fbov.values())
        if 'head' in xrc__vzrj:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(qlp__wnryo not in grp.selection and qlp__wnryo not in grp.
            keys for qlp__wnryo in aqhnf__zpa):
            raise_const_error(
                f'Selected column names {aqhnf__zpa} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            xrc__vzrj)
        if goox__lzb and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        dkkm__gbfk = {}
        out_columns = []
        out_data = []
        out_column_type = []
        xwzp__hkful = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for jofyd__bwau, f_val in zip(aqhnf__zpa, xrc__vzrj):
            if isinstance(f_val, (tuple, list)):
                xven__rmhj = 0
                for cfs__bdo in f_val:
                    orf__ugq, out_tp = get_agg_funcname_and_outtyp(grp,
                        jofyd__bwau, cfs__bdo, typing_context, target_context)
                    pvxhj__woht = orf__ugq in list_cumulative
                    if orf__ugq == '<lambda>' and len(f_val) > 1:
                        orf__ugq = '<lambda_' + str(xven__rmhj) + '>'
                        xven__rmhj += 1
                    out_columns.append((jofyd__bwau, orf__ugq))
                    dkkm__gbfk[jofyd__bwau, orf__ugq] = jofyd__bwau, orf__ugq
                    _append_out_type(grp, out_data, out_tp)
            else:
                orf__ugq, out_tp = get_agg_funcname_and_outtyp(grp,
                    jofyd__bwau, f_val, typing_context, target_context)
                pvxhj__woht = orf__ugq in list_cumulative
                if multi_level_names:
                    out_columns.append((jofyd__bwau, orf__ugq))
                    dkkm__gbfk[jofyd__bwau, orf__ugq] = jofyd__bwau, orf__ugq
                elif not goox__lzb:
                    out_columns.append(jofyd__bwau)
                    dkkm__gbfk[jofyd__bwau, orf__ugq] = jofyd__bwau
                elif goox__lzb:
                    xwzp__hkful.append(orf__ugq)
                _append_out_type(grp, out_data, out_tp)
        if goox__lzb:
            for whxmr__fhxle, qfewn__wbv in enumerate(kws.keys()):
                out_columns.append(qfewn__wbv)
                dkkm__gbfk[aqhnf__zpa[whxmr__fhxle], xwzp__hkful[whxmr__fhxle]
                    ] = qfewn__wbv
        if pvxhj__woht:
            index = grp.df_type.index
        else:
            index = out_tp.index
        slztn__pqvg = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(slztn__pqvg, *args), dkkm__gbfk
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one functions supplied'
                )
        assert len(func) > 0
        out_data = []
        out_columns = []
        out_column_type = []
        xven__rmhj = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        dkkm__gbfk = {}
        rsnfj__rsckp = grp.selection[0]
        for f_val in func.types:
            orf__ugq, out_tp = get_agg_funcname_and_outtyp(grp,
                rsnfj__rsckp, f_val, typing_context, target_context)
            pvxhj__woht = orf__ugq in list_cumulative
            if orf__ugq == '<lambda>':
                orf__ugq = '<lambda_' + str(xven__rmhj) + '>'
                xven__rmhj += 1
            out_columns.append(orf__ugq)
            dkkm__gbfk[rsnfj__rsckp, orf__ugq] = orf__ugq
            _append_out_type(grp, out_data, out_tp)
        if pvxhj__woht:
            index = grp.df_type.index
        else:
            index = out_tp.index
        slztn__pqvg = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(slztn__pqvg, *args), dkkm__gbfk
    orf__ugq = ''
    if types.unliteral(func) == types.unicode_type:
        orf__ugq = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        orf__ugq = bodo.utils.typing.get_builtin_function_name(func)
    if orf__ugq:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, orf__ugq, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        obvu__ypx = args[0] if len(args) > 0 else kws.pop('axis', 0)
        aizkg__gsu = args[1] if len(args) > 1 else kws.pop('numeric_only', 
            False)
        ypsni__kmhxo = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        bjry__wym = dict(axis=obvu__ypx, numeric_only=aizkg__gsu)
        beo__gyma = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', bjry__wym,
            beo__gyma, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        vjyok__ojs = args[0] if len(args) > 0 else kws.pop('periods', 1)
        vbg__kiw = args[1] if len(args) > 1 else kws.pop('freq', None)
        obvu__ypx = args[2] if len(args) > 2 else kws.pop('axis', 0)
        texnh__tnd = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        bjry__wym = dict(freq=vbg__kiw, axis=obvu__ypx, fill_value=texnh__tnd)
        beo__gyma = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', bjry__wym,
            beo__gyma, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        fsflj__nza = args[0] if len(args) > 0 else kws.pop('func', None)
        bkl__jycxn = kws.pop('engine', None)
        mhxc__ezzws = kws.pop('engine_kwargs', None)
        bjry__wym = dict(engine=bkl__jycxn, engine_kwargs=mhxc__ezzws)
        beo__gyma = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', bjry__wym, beo__gyma,
            package_name='pandas', module_name='GroupBy')
    dkkm__gbfk = {}
    for qlp__wnryo in grp.selection:
        out_columns.append(qlp__wnryo)
        dkkm__gbfk[qlp__wnryo, name_operation] = qlp__wnryo
        mwjl__nngiv = grp.df_type.columns.index(qlp__wnryo)
        data = grp.df_type.data[mwjl__nngiv]
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            zzhot__qxtnb, err_msg = get_groupby_output_dtype(data,
                get_literal_value(fsflj__nza), grp.df_type.index)
            if err_msg == 'ok':
                data = zzhot__qxtnb
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    slztn__pqvg = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        slztn__pqvg = SeriesType(out_data[0].dtype, data=out_data[0], index
            =index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(slztn__pqvg, *args), dkkm__gbfk


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        oxfw__jhjvd = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        xrfm__pjfe = isinstance(oxfw__jhjvd, (SeriesType,
            HeterogeneousSeriesType)
            ) and oxfw__jhjvd.const_info is not None or not isinstance(
            oxfw__jhjvd, (SeriesType, DataFrameType))
        if xrfm__pjfe:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                taw__skqk = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                ett__olv = tuple(grp.df_type.columns.index(grp.keys[
                    whxmr__fhxle]) for whxmr__fhxle in range(len(grp.keys)))
                ppat__nbja = tuple(grp.df_type.data[mwjl__nngiv] for
                    mwjl__nngiv in ett__olv)
                taw__skqk = MultiIndexType(ppat__nbja, tuple(types.literal(
                    hsh__akp) for hsh__akp in grp.keys))
            else:
                mwjl__nngiv = grp.df_type.columns.index(grp.keys[0])
                taw__skqk = bodo.hiframes.pd_index_ext.array_type_to_index(grp
                    .df_type.data[mwjl__nngiv], types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            bqlp__sgosi = tuple(grp.df_type.data[grp.df_type.columns.index(
                qlp__wnryo)] for qlp__wnryo in grp.keys)
            uloil__huv = tuple(types.literal(uogt__nqznp) for uogt__nqznp in
                grp.keys) + get_index_name_types(oxfw__jhjvd.index)
            if not grp.as_index:
                bqlp__sgosi = types.Array(types.int64, 1, 'C'),
                uloil__huv = (types.none,) + get_index_name_types(oxfw__jhjvd
                    .index)
            taw__skqk = MultiIndexType(bqlp__sgosi +
                get_index_data_arr_types(oxfw__jhjvd.index), uloil__huv)
        if xrfm__pjfe:
            if isinstance(oxfw__jhjvd, HeterogeneousSeriesType):
                xdqxc__eshjj, eqryp__plrmi = oxfw__jhjvd.const_info
                qid__xxaiy = tuple(dtype_to_array_type(tmmgc__ewk) for
                    tmmgc__ewk in oxfw__jhjvd.data.types)
                tcsb__nrr = DataFrameType(out_data + qid__xxaiy, taw__skqk,
                    out_columns + eqryp__plrmi)
            elif isinstance(oxfw__jhjvd, SeriesType):
                odjlz__klmp, eqryp__plrmi = oxfw__jhjvd.const_info
                qid__xxaiy = tuple(dtype_to_array_type(oxfw__jhjvd.dtype) for
                    xdqxc__eshjj in range(odjlz__klmp))
                tcsb__nrr = DataFrameType(out_data + qid__xxaiy, taw__skqk,
                    out_columns + eqryp__plrmi)
            else:
                cchyq__zvz = get_udf_out_arr_type(oxfw__jhjvd)
                if not grp.as_index:
                    tcsb__nrr = DataFrameType(out_data + (cchyq__zvz,),
                        taw__skqk, out_columns + ('',))
                else:
                    tcsb__nrr = SeriesType(cchyq__zvz.dtype, cchyq__zvz,
                        taw__skqk, None)
        elif isinstance(oxfw__jhjvd, SeriesType):
            tcsb__nrr = SeriesType(oxfw__jhjvd.dtype, oxfw__jhjvd.data,
                taw__skqk, oxfw__jhjvd.name_typ)
        else:
            tcsb__nrr = DataFrameType(oxfw__jhjvd.data, taw__skqk,
                oxfw__jhjvd.columns)
        cjrip__qus = gen_apply_pysig(len(f_args), kws.keys())
        vkp__jgjk = (func, *f_args) + tuple(kws.values())
        return signature(tcsb__nrr, *vkp__jgjk).replace(pysig=cjrip__qus)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_const_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    ymvie__jtow = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            jofyd__bwau = grp.selection[0]
            cchyq__zvz = ymvie__jtow.data[ymvie__jtow.columns.index(
                jofyd__bwau)]
            rqdf__hqjmy = SeriesType(cchyq__zvz.dtype, cchyq__zvz,
                ymvie__jtow.index, types.literal(jofyd__bwau))
        else:
            bwdek__iys = tuple(ymvie__jtow.data[ymvie__jtow.columns.index(
                qlp__wnryo)] for qlp__wnryo in grp.selection)
            rqdf__hqjmy = DataFrameType(bwdek__iys, ymvie__jtow.index,
                tuple(grp.selection))
    else:
        rqdf__hqjmy = ymvie__jtow
    uuz__mccka = rqdf__hqjmy,
    uuz__mccka += tuple(f_args)
    try:
        oxfw__jhjvd = get_const_func_output_type(func, uuz__mccka, kws,
            typing_context, target_context)
    except Exception as tfx__daek:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', tfx__daek),
            getattr(tfx__daek, 'loc', None))
    return oxfw__jhjvd


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    uuz__mccka = (grp,) + f_args
    try:
        oxfw__jhjvd = get_const_func_output_type(func, uuz__mccka, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as tfx__daek:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', tfx__daek),
            getattr(tfx__daek, 'loc', None))
    cjrip__qus = gen_apply_pysig(len(f_args), kws.keys())
    vkp__jgjk = (func, *f_args) + tuple(kws.values())
    return signature(oxfw__jhjvd, *vkp__jgjk).replace(pysig=cjrip__qus)


def gen_apply_pysig(n_args, kws):
    jiw__pqk = ', '.join(f'arg{whxmr__fhxle}' for whxmr__fhxle in range(n_args)
        )
    jiw__pqk = jiw__pqk + ', ' if jiw__pqk else ''
    gocgp__zbc = ', '.join(f"{desk__gcjh} = ''" for desk__gcjh in kws)
    cki__kxaa = f'def apply_stub(func, {jiw__pqk}{gocgp__zbc}):\n'
    cki__kxaa += '    pass\n'
    rie__kutp = {}
    exec(cki__kxaa, {}, rie__kutp)
    oetze__oephg = rie__kutp['apply_stub']
    return numba.core.utils.pysignature(oetze__oephg)


def pivot_table_dummy(df, values, index, columns, aggfunc, _pivot_values):
    return 0


@infer_global(pivot_table_dummy)
class PivotTableTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, values, index, columns, aggfunc, _pivot_values = args
        if not (is_overload_constant_str(values) and
            is_overload_constant_str(index) and is_overload_constant_str(
            columns)):
            raise BodoError(
                "pivot_table() only support string constants for 'values', 'index' and 'columns' arguments"
                )
        values = values.literal_value
        index = index.literal_value
        columns = columns.literal_value
        data = df.data[df.columns.index(values)]
        zzhot__qxtnb = get_pivot_output_dtype(data, aggfunc.literal_value)
        yhudk__xqrb = dtype_to_array_type(zzhot__qxtnb)
        if is_overload_none(_pivot_values):
            raise_bodo_error(
                'Dataframe.pivot_table() requires explicit annotation to determine output columns. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/pandas.html'
                )
        qqbha__kkuo = _pivot_values.meta
        ycm__pxqx = len(qqbha__kkuo)
        mwjl__nngiv = df.columns.index(index)
        vhqp__lsomc = bodo.hiframes.pd_index_ext.array_type_to_index(df.
            data[mwjl__nngiv], types.StringLiteral(index))
        vki__tcsye = DataFrameType((yhudk__xqrb,) * ycm__pxqx, vhqp__lsomc,
            tuple(qqbha__kkuo))
        return signature(vki__tcsye, *args)


PivotTableTyper._no_unliteral = True


@lower_builtin(pivot_table_dummy, types.VarArg(types.Any))
def lower_pivot_table_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        yhudk__xqrb = types.Array(types.int64, 1, 'C')
        qqbha__kkuo = _pivot_values.meta
        ycm__pxqx = len(qqbha__kkuo)
        vhqp__lsomc = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        vki__tcsye = DataFrameType((yhudk__xqrb,) * ycm__pxqx, vhqp__lsomc,
            tuple(qqbha__kkuo))
        return signature(vki__tcsye, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    cki__kxaa = 'def impl(keys, dropna, _is_parallel):\n'
    cki__kxaa += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    cki__kxaa += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{whxmr__fhxle}])' for whxmr__fhxle in range(
        len(keys.types))))
    cki__kxaa += '    table = arr_info_list_to_table(info_list)\n'
    cki__kxaa += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    cki__kxaa += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    cki__kxaa += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    cki__kxaa += '    delete_table_decref_arrays(table)\n'
    cki__kxaa += '    ev.finalize()\n'
    cki__kxaa += '    return sort_idx, group_labels, ngroups\n'
    rie__kutp = {}
    exec(cki__kxaa, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, rie__kutp)
    rnm__oos = rie__kutp['impl']
    return rnm__oos


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    lytmo__ndwe = len(labels)
    tmxto__rqcwf = np.zeros(ngroups, dtype=np.int64)
    vck__iodj = np.zeros(ngroups, dtype=np.int64)
    ohv__wto = 0
    jllvk__iuux = 0
    for whxmr__fhxle in range(lytmo__ndwe):
        upb__kbwmf = labels[whxmr__fhxle]
        if upb__kbwmf < 0:
            ohv__wto += 1
        else:
            jllvk__iuux += 1
            if whxmr__fhxle == lytmo__ndwe - 1 or upb__kbwmf != labels[
                whxmr__fhxle + 1]:
                tmxto__rqcwf[upb__kbwmf] = ohv__wto
                vck__iodj[upb__kbwmf] = ohv__wto + jllvk__iuux
                ohv__wto += jllvk__iuux
                jllvk__iuux = 0
    return tmxto__rqcwf, vck__iodj


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    rnm__oos, xdqxc__eshjj = gen_shuffle_dataframe(df, keys, _is_parallel)
    return rnm__oos


def gen_shuffle_dataframe(df, keys, _is_parallel):
    odjlz__klmp = len(df.columns)
    mdrs__xvrb = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    cki__kxaa = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        cki__kxaa += '  return df, keys, get_null_shuffle_info()\n'
        rie__kutp = {}
        exec(cki__kxaa, {'get_null_shuffle_info': get_null_shuffle_info},
            rie__kutp)
        rnm__oos = rie__kutp['impl']
        return rnm__oos
    for whxmr__fhxle in range(odjlz__klmp):
        cki__kxaa += f"""  in_arr{whxmr__fhxle} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {whxmr__fhxle})
"""
    cki__kxaa += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    cki__kxaa += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{whxmr__fhxle}])' for whxmr__fhxle in range(
        mdrs__xvrb)), ', '.join(f'array_to_info(in_arr{whxmr__fhxle})' for
        whxmr__fhxle in range(odjlz__klmp)), 'array_to_info(in_index_arr)')
    cki__kxaa += '  table = arr_info_list_to_table(info_list)\n'
    cki__kxaa += (
        f'  out_table = shuffle_table(table, {mdrs__xvrb}, _is_parallel, 1)\n')
    for whxmr__fhxle in range(mdrs__xvrb):
        cki__kxaa += f"""  out_key{whxmr__fhxle} = info_to_array(info_from_table(out_table, {whxmr__fhxle}), keys{whxmr__fhxle}_typ)
"""
    for whxmr__fhxle in range(odjlz__klmp):
        cki__kxaa += f"""  out_arr{whxmr__fhxle} = info_to_array(info_from_table(out_table, {whxmr__fhxle + mdrs__xvrb}), in_arr{whxmr__fhxle}_typ)
"""
    cki__kxaa += f"""  out_arr_index = info_to_array(info_from_table(out_table, {mdrs__xvrb + odjlz__klmp}), ind_arr_typ)
"""
    cki__kxaa += '  shuffle_info = get_shuffle_info(out_table)\n'
    cki__kxaa += '  delete_table(out_table)\n'
    cki__kxaa += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{whxmr__fhxle}' for whxmr__fhxle in range
        (odjlz__klmp))
    cki__kxaa += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    cki__kxaa += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, {gen_const_tup(df.columns)})
"""
    cki__kxaa += '  return out_df, ({},), shuffle_info\n'.format(', '.join(
        f'out_key{whxmr__fhxle}' for whxmr__fhxle in range(mdrs__xvrb)))
    uehx__phig = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, 'ind_arr_typ': types.Array(types.int64, 1, 'C') if
        isinstance(df.index, RangeIndexType) else df.index.data}
    uehx__phig.update({f'keys{whxmr__fhxle}_typ': keys.types[whxmr__fhxle] for
        whxmr__fhxle in range(mdrs__xvrb)})
    uehx__phig.update({f'in_arr{whxmr__fhxle}_typ': df.data[whxmr__fhxle] for
        whxmr__fhxle in range(odjlz__klmp)})
    rie__kutp = {}
    exec(cki__kxaa, uehx__phig, rie__kutp)
    rnm__oos = rie__kutp['impl']
    return rnm__oos, uehx__phig


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        tnjz__kugtz = len(data.array_types)
        cki__kxaa = 'def impl(data, shuffle_info):\n'
        cki__kxaa += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{whxmr__fhxle}])' for whxmr__fhxle in
            range(tnjz__kugtz)))
        cki__kxaa += '  table = arr_info_list_to_table(info_list)\n'
        cki__kxaa += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for whxmr__fhxle in range(tnjz__kugtz):
            cki__kxaa += f"""  out_arr{whxmr__fhxle} = info_to_array(info_from_table(out_table, {whxmr__fhxle}), data._data[{whxmr__fhxle}])
"""
        cki__kxaa += '  delete_table(out_table)\n'
        cki__kxaa += '  delete_table(table)\n'
        cki__kxaa += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{whxmr__fhxle}' for whxmr__fhxle in
            range(tnjz__kugtz))))
        rie__kutp = {}
        exec(cki__kxaa, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, rie__kutp)
        rnm__oos = rie__kutp['impl']
        return rnm__oos
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            qyxx__mwl = bodo.utils.conversion.index_to_array(data)
            tav__cdi = reverse_shuffle(qyxx__mwl, shuffle_info)
            return bodo.utils.conversion.index_from_array(tav__cdi)
        return impl_index

    def impl_arr(data, shuffle_info):
        fhgnx__rjkg = [array_to_info(data)]
        jojvl__vlatd = arr_info_list_to_table(fhgnx__rjkg)
        rhprr__zzxve = reverse_shuffle_table(jojvl__vlatd, shuffle_info)
        tav__cdi = info_to_array(info_from_table(rhprr__zzxve, 0), data)
        delete_table(rhprr__zzxve)
        delete_table(jojvl__vlatd)
        return tav__cdi
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    bjry__wym = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    beo__gyma = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', bjry__wym, beo__gyma,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    ufyqj__lcql = get_overload_const_bool(ascending)
    aaz__qkbw = grp.selection[0]
    cki__kxaa = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    okr__pje = (
        f"lambda S: S.value_counts(ascending={ufyqj__lcql}, _index_name='{aaz__qkbw}')"
        )
    cki__kxaa += f'    return grp.apply({okr__pje})\n'
    rie__kutp = {}
    exec(cki__kxaa, {'bodo': bodo}, rie__kutp)
    rnm__oos = rie__kutp['impl']
    return rnm__oos


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill',
    'ngroup', 'nth', 'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail',
    'corr', 'cov', 'describe', 'diff', 'fillna', 'filter', 'hist', 'mad',
    'plot', 'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupy_unsupported():
    for yeisy__wnc in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, yeisy__wnc, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{yeisy__wnc}'))
    for yeisy__wnc in groupby_unsupported:
        overload_method(DataFrameGroupByType, yeisy__wnc, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{yeisy__wnc}'))
    for yeisy__wnc in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, yeisy__wnc, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{yeisy__wnc}'))
    for yeisy__wnc in series_only_unsupported:
        overload_method(DataFrameGroupByType, yeisy__wnc, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{yeisy__wnc}'))
    for yeisy__wnc in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, yeisy__wnc, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{yeisy__wnc}'))


_install_groupy_unsupported()
