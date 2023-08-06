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
        jvby__dwzk = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, jvby__dwzk)


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
        emv__wetpg = args[0]
        zygus__jmyrc = signature.return_type
        xwzbw__fkch = cgutils.create_struct_proxy(zygus__jmyrc)(context,
            builder)
        xwzbw__fkch.obj = emv__wetpg
        context.nrt.incref(builder, signature.args[0], emv__wetpg)
        return xwzbw__fkch._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for rvc__gsjna in keys:
        selection.remove(rvc__gsjna)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    zygus__jmyrc = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return zygus__jmyrc(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, rtgw__gmzb = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(rtgw__gmzb, (tuple, list)):
                if len(set(rtgw__gmzb).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(rtgw__gmzb).difference(set(grpby.
                        df_type.columns))))
                selection = rtgw__gmzb
            else:
                if rtgw__gmzb not in grpby.df_type.columns:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(rtgw__gmzb))
                selection = rtgw__gmzb,
                series_select = True
            dgwhj__brqc = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(dgwhj__brqc, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, rtgw__gmzb = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            rtgw__gmzb):
            dgwhj__brqc = StaticGetItemDataFrameGroupBy.generic(self, (
                grpby, get_literal_value(rtgw__gmzb)), {}).return_type
            return signature(dgwhj__brqc, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    vqgap__wtwlq = arr_type == ArrayItemArrayType(string_array_type)
    vrm__dql = arr_type.dtype
    if isinstance(vrm__dql, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {vrm__dql} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(vrm__dql, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {vrm__dql} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(vrm__dql,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(vrm__dql, (types.Integer, types.Float, types.Boolean)):
        if vqgap__wtwlq or vrm__dql == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(vrm__dql, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not vrm__dql.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {vrm__dql} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(vrm__dql, types.Boolean) and func_name in {'cumsum',
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
    vrm__dql = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(vrm__dql, (types
            .Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(vrm__dql, types.Integer):
            return IntDtype(vrm__dql)
        return vrm__dql
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        szcx__yyd = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{szcx__yyd}'."
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
    for rvc__gsjna in grp.keys:
        if multi_level_names:
            sqvaf__udgcg = rvc__gsjna, ''
        else:
            sqvaf__udgcg = rvc__gsjna
        ndeqh__owk = grp.df_type.columns.index(rvc__gsjna)
        data = grp.df_type.data[ndeqh__owk]
        out_columns.append(sqvaf__udgcg)
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
        jtnz__yxs = tuple(grp.df_type.columns.index(grp.keys[amduy__ihr]) for
            amduy__ihr in range(len(grp.keys)))
        lebbc__sfuh = tuple(grp.df_type.data[ndeqh__owk] for ndeqh__owk in
            jtnz__yxs)
        index = MultiIndexType(lebbc__sfuh, tuple(types.StringLiteral(
            rvc__gsjna) for rvc__gsjna in grp.keys))
    else:
        ndeqh__owk = grp.df_type.columns.index(grp.keys[0])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(grp.df_type.
            data[ndeqh__owk], types.StringLiteral(grp.keys[0]))
    jek__qwiuo = {}
    igmdx__fhno = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        jek__qwiuo[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for ehiuu__iiu in columns:
            ndeqh__owk = grp.df_type.columns.index(ehiuu__iiu)
            data = grp.df_type.data[ndeqh__owk]
            cfz__kpwg = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                cfz__kpwg = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    aws__qxfd = SeriesType(data.dtype, data, None, string_type)
                    osltr__eozs = get_const_func_output_type(func, (
                        aws__qxfd,), {}, typing_context, target_context)
                    if osltr__eozs != ArrayItemArrayType(string_array_type):
                        osltr__eozs = dtype_to_array_type(osltr__eozs)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=ehiuu__iiu, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    czmhw__znq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    ngfp__cft = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    elt__ouvtr = dict(numeric_only=czmhw__znq, min_count=
                        ngfp__cft)
                    zzxm__swsj = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        elt__ouvtr, zzxm__swsj, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    czmhw__znq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    ngfp__cft = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    elt__ouvtr = dict(numeric_only=czmhw__znq, min_count=
                        ngfp__cft)
                    zzxm__swsj = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        elt__ouvtr, zzxm__swsj, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    czmhw__znq = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    elt__ouvtr = dict(numeric_only=czmhw__znq)
                    zzxm__swsj = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        elt__ouvtr, zzxm__swsj, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    humhn__ooic = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    kngyk__guge = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    elt__ouvtr = dict(axis=humhn__ooic, skipna=kngyk__guge)
                    zzxm__swsj = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        elt__ouvtr, zzxm__swsj, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    ubh__bou = args[0] if len(args) > 0 else kws.pop('ddof', 1)
                    elt__ouvtr = dict(ddof=ubh__bou)
                    zzxm__swsj = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        elt__ouvtr, zzxm__swsj, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                osltr__eozs, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                weedk__oilif = osltr__eozs
                out_data.append(weedk__oilif)
                out_columns.append(ehiuu__iiu)
                if func_name == 'agg':
                    almy__ssfos = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    jek__qwiuo[ehiuu__iiu, almy__ssfos] = ehiuu__iiu
                else:
                    jek__qwiuo[ehiuu__iiu, func_name] = ehiuu__iiu
                out_column_type.append(cfz__kpwg)
            else:
                igmdx__fhno.append(err_msg)
    if func_name == 'sum':
        wtbw__kgom = any([(pwi__fterp == ColumnType.NumericalColumn.value) for
            pwi__fterp in out_column_type])
        if wtbw__kgom:
            out_data = [pwi__fterp for pwi__fterp, tbruq__pibwg in zip(
                out_data, out_column_type) if tbruq__pibwg != ColumnType.
                NonNumericalColumn.value]
            out_columns = [pwi__fterp for pwi__fterp, tbruq__pibwg in zip(
                out_columns, out_column_type) if tbruq__pibwg != ColumnType
                .NonNumericalColumn.value]
            jek__qwiuo = {}
            for ehiuu__iiu in out_columns:
                if grp.as_index is False and ehiuu__iiu in grp.keys:
                    continue
                jek__qwiuo[ehiuu__iiu, func_name] = ehiuu__iiu
    wbr__quc = len(igmdx__fhno)
    if len(out_data) == 0:
        if wbr__quc == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(wbr__quc, ' was' if wbr__quc == 1 else 's were',
                ','.join(igmdx__fhno)))
    zetw__gdkn = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            lgldx__lkjzg = IntDtype(out_data[0].dtype)
        else:
            lgldx__lkjzg = out_data[0].dtype
        xaso__hrijg = (types.none if func_name == 'size' else types.
            StringLiteral(grp.selection[0]))
        zetw__gdkn = SeriesType(lgldx__lkjzg, index=index, name_typ=xaso__hrijg
            )
    return signature(zetw__gdkn, *args), jek__qwiuo


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    ruj__tlrki = True
    if isinstance(f_val, str):
        ruj__tlrki = False
        sitb__kbe = f_val
    elif is_overload_constant_str(f_val):
        ruj__tlrki = False
        sitb__kbe = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        ruj__tlrki = False
        sitb__kbe = bodo.utils.typing.get_builtin_function_name(f_val)
    if not ruj__tlrki:
        if sitb__kbe not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {sitb__kbe}')
        dgwhj__brqc = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(dgwhj__brqc, (), sitb__kbe, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            yzh__eaqbp = types.functions.MakeFunctionLiteral(f_val)
        else:
            yzh__eaqbp = f_val
        validate_udf('agg', yzh__eaqbp)
        func = get_overload_const_func(yzh__eaqbp, None)
        tlpdi__hvjq = func.code if hasattr(func, 'code') else func.__code__
        sitb__kbe = tlpdi__hvjq.co_name
        dgwhj__brqc = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(dgwhj__brqc, (), 'agg', typing_context,
            target_context, yzh__eaqbp)[0].return_type
    return sitb__kbe, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    ocwe__wbd = kws and all(isinstance(qxor__hjy, types.Tuple) and len(
        qxor__hjy) == 2 for qxor__hjy in kws.values())
    if is_overload_none(func) and not ocwe__wbd:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not ocwe__wbd:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    tpxmk__ysjzv = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if ocwe__wbd or is_overload_constant_dict(func):
        if ocwe__wbd:
            qedzw__fufqk = [get_literal_value(kgjpi__zbsi) for kgjpi__zbsi,
                syyfi__teaej in kws.values()]
            wazvx__kwihu = [get_literal_value(veg__huii) for syyfi__teaej,
                veg__huii in kws.values()]
        else:
            mdt__rwsdd = get_overload_constant_dict(func)
            qedzw__fufqk = tuple(mdt__rwsdd.keys())
            wazvx__kwihu = tuple(mdt__rwsdd.values())
        if 'head' in wazvx__kwihu:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(ehiuu__iiu not in grp.selection and ehiuu__iiu not in grp.
            keys for ehiuu__iiu in qedzw__fufqk):
            raise_const_error(
                f'Selected column names {qedzw__fufqk} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            wazvx__kwihu)
        if ocwe__wbd and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        jek__qwiuo = {}
        out_columns = []
        out_data = []
        out_column_type = []
        cam__evth = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for vzd__btnpi, f_val in zip(qedzw__fufqk, wazvx__kwihu):
            if isinstance(f_val, (tuple, list)):
                qzuux__jnurp = 0
                for yzh__eaqbp in f_val:
                    sitb__kbe, out_tp = get_agg_funcname_and_outtyp(grp,
                        vzd__btnpi, yzh__eaqbp, typing_context, target_context)
                    tpxmk__ysjzv = sitb__kbe in list_cumulative
                    if sitb__kbe == '<lambda>' and len(f_val) > 1:
                        sitb__kbe = '<lambda_' + str(qzuux__jnurp) + '>'
                        qzuux__jnurp += 1
                    out_columns.append((vzd__btnpi, sitb__kbe))
                    jek__qwiuo[vzd__btnpi, sitb__kbe] = vzd__btnpi, sitb__kbe
                    _append_out_type(grp, out_data, out_tp)
            else:
                sitb__kbe, out_tp = get_agg_funcname_and_outtyp(grp,
                    vzd__btnpi, f_val, typing_context, target_context)
                tpxmk__ysjzv = sitb__kbe in list_cumulative
                if multi_level_names:
                    out_columns.append((vzd__btnpi, sitb__kbe))
                    jek__qwiuo[vzd__btnpi, sitb__kbe] = vzd__btnpi, sitb__kbe
                elif not ocwe__wbd:
                    out_columns.append(vzd__btnpi)
                    jek__qwiuo[vzd__btnpi, sitb__kbe] = vzd__btnpi
                elif ocwe__wbd:
                    cam__evth.append(sitb__kbe)
                _append_out_type(grp, out_data, out_tp)
        if ocwe__wbd:
            for amduy__ihr, ehzvv__aucv in enumerate(kws.keys()):
                out_columns.append(ehzvv__aucv)
                jek__qwiuo[qedzw__fufqk[amduy__ihr], cam__evth[amduy__ihr]
                    ] = ehzvv__aucv
        if tpxmk__ysjzv:
            index = grp.df_type.index
        else:
            index = out_tp.index
        zetw__gdkn = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(zetw__gdkn, *args), jek__qwiuo
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
        qzuux__jnurp = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        jek__qwiuo = {}
        xhy__kunx = grp.selection[0]
        for f_val in func.types:
            sitb__kbe, out_tp = get_agg_funcname_and_outtyp(grp, xhy__kunx,
                f_val, typing_context, target_context)
            tpxmk__ysjzv = sitb__kbe in list_cumulative
            if sitb__kbe == '<lambda>':
                sitb__kbe = '<lambda_' + str(qzuux__jnurp) + '>'
                qzuux__jnurp += 1
            out_columns.append(sitb__kbe)
            jek__qwiuo[xhy__kunx, sitb__kbe] = sitb__kbe
            _append_out_type(grp, out_data, out_tp)
        if tpxmk__ysjzv:
            index = grp.df_type.index
        else:
            index = out_tp.index
        zetw__gdkn = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(zetw__gdkn, *args), jek__qwiuo
    sitb__kbe = ''
    if types.unliteral(func) == types.unicode_type:
        sitb__kbe = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        sitb__kbe = bodo.utils.typing.get_builtin_function_name(func)
    if sitb__kbe:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, sitb__kbe, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        humhn__ooic = args[0] if len(args) > 0 else kws.pop('axis', 0)
        czmhw__znq = args[1] if len(args) > 1 else kws.pop('numeric_only', 
            False)
        kngyk__guge = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        elt__ouvtr = dict(axis=humhn__ooic, numeric_only=czmhw__znq)
        zzxm__swsj = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', elt__ouvtr,
            zzxm__swsj, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        btv__xbxo = args[0] if len(args) > 0 else kws.pop('periods', 1)
        xxti__adi = args[1] if len(args) > 1 else kws.pop('freq', None)
        humhn__ooic = args[2] if len(args) > 2 else kws.pop('axis', 0)
        kcpn__zeeon = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        elt__ouvtr = dict(freq=xxti__adi, axis=humhn__ooic, fill_value=
            kcpn__zeeon)
        zzxm__swsj = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', elt__ouvtr,
            zzxm__swsj, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        oqs__woii = args[0] if len(args) > 0 else kws.pop('func', None)
        ynfkr__qjs = kws.pop('engine', None)
        etx__pan = kws.pop('engine_kwargs', None)
        elt__ouvtr = dict(engine=ynfkr__qjs, engine_kwargs=etx__pan)
        zzxm__swsj = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', elt__ouvtr, zzxm__swsj,
            package_name='pandas', module_name='GroupBy')
    jek__qwiuo = {}
    for ehiuu__iiu in grp.selection:
        out_columns.append(ehiuu__iiu)
        jek__qwiuo[ehiuu__iiu, name_operation] = ehiuu__iiu
        ndeqh__owk = grp.df_type.columns.index(ehiuu__iiu)
        data = grp.df_type.data[ndeqh__owk]
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
            osltr__eozs, err_msg = get_groupby_output_dtype(data,
                get_literal_value(oqs__woii), grp.df_type.index)
            if err_msg == 'ok':
                data = osltr__eozs
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    zetw__gdkn = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        zetw__gdkn = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(zetw__gdkn, *args), jek__qwiuo


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
        irpej__rmool = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        znht__zua = isinstance(irpej__rmool, (SeriesType,
            HeterogeneousSeriesType)
            ) and irpej__rmool.const_info is not None or not isinstance(
            irpej__rmool, (SeriesType, DataFrameType))
        if znht__zua:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                rduxx__egdxu = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                jtnz__yxs = tuple(grp.df_type.columns.index(grp.keys[
                    amduy__ihr]) for amduy__ihr in range(len(grp.keys)))
                lebbc__sfuh = tuple(grp.df_type.data[ndeqh__owk] for
                    ndeqh__owk in jtnz__yxs)
                rduxx__egdxu = MultiIndexType(lebbc__sfuh, tuple(types.
                    literal(rvc__gsjna) for rvc__gsjna in grp.keys))
            else:
                ndeqh__owk = grp.df_type.columns.index(grp.keys[0])
                rduxx__egdxu = bodo.hiframes.pd_index_ext.array_type_to_index(
                    grp.df_type.data[ndeqh__owk], types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            zfgel__causi = tuple(grp.df_type.data[grp.df_type.columns.index
                (ehiuu__iiu)] for ehiuu__iiu in grp.keys)
            lugt__pkedm = tuple(types.literal(qxor__hjy) for qxor__hjy in
                grp.keys) + get_index_name_types(irpej__rmool.index)
            if not grp.as_index:
                zfgel__causi = types.Array(types.int64, 1, 'C'),
                lugt__pkedm = (types.none,) + get_index_name_types(irpej__rmool
                    .index)
            rduxx__egdxu = MultiIndexType(zfgel__causi +
                get_index_data_arr_types(irpej__rmool.index), lugt__pkedm)
        if znht__zua:
            if isinstance(irpej__rmool, HeterogeneousSeriesType):
                syyfi__teaej, cbh__med = irpej__rmool.const_info
                tqdt__ulpr = tuple(dtype_to_array_type(voiw__bhhlx) for
                    voiw__bhhlx in irpej__rmool.data.types)
                kul__ykw = DataFrameType(out_data + tqdt__ulpr,
                    rduxx__egdxu, out_columns + cbh__med)
            elif isinstance(irpej__rmool, SeriesType):
                uhjtk__ezspd, cbh__med = irpej__rmool.const_info
                tqdt__ulpr = tuple(dtype_to_array_type(irpej__rmool.dtype) for
                    syyfi__teaej in range(uhjtk__ezspd))
                kul__ykw = DataFrameType(out_data + tqdt__ulpr,
                    rduxx__egdxu, out_columns + cbh__med)
            else:
                myldy__eud = get_udf_out_arr_type(irpej__rmool)
                if not grp.as_index:
                    kul__ykw = DataFrameType(out_data + (myldy__eud,),
                        rduxx__egdxu, out_columns + ('',))
                else:
                    kul__ykw = SeriesType(myldy__eud.dtype, myldy__eud,
                        rduxx__egdxu, None)
        elif isinstance(irpej__rmool, SeriesType):
            kul__ykw = SeriesType(irpej__rmool.dtype, irpej__rmool.data,
                rduxx__egdxu, irpej__rmool.name_typ)
        else:
            kul__ykw = DataFrameType(irpej__rmool.data, rduxx__egdxu,
                irpej__rmool.columns)
        oif__qaeau = gen_apply_pysig(len(f_args), kws.keys())
        ijy__rphzu = (func, *f_args) + tuple(kws.values())
        return signature(kul__ykw, *ijy__rphzu).replace(pysig=oif__qaeau)

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
    wvt__zghei = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            vzd__btnpi = grp.selection[0]
            myldy__eud = wvt__zghei.data[wvt__zghei.columns.index(vzd__btnpi)]
            tri__ccedc = SeriesType(myldy__eud.dtype, myldy__eud,
                wvt__zghei.index, types.literal(vzd__btnpi))
        else:
            hesz__mzue = tuple(wvt__zghei.data[wvt__zghei.columns.index(
                ehiuu__iiu)] for ehiuu__iiu in grp.selection)
            tri__ccedc = DataFrameType(hesz__mzue, wvt__zghei.index, tuple(
                grp.selection))
    else:
        tri__ccedc = wvt__zghei
    rmqx__mqo = tri__ccedc,
    rmqx__mqo += tuple(f_args)
    try:
        irpej__rmool = get_const_func_output_type(func, rmqx__mqo, kws,
            typing_context, target_context)
    except Exception as wddnz__yikc:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', wddnz__yikc),
            getattr(wddnz__yikc, 'loc', None))
    return irpej__rmool


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    rmqx__mqo = (grp,) + f_args
    try:
        irpej__rmool = get_const_func_output_type(func, rmqx__mqo, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as wddnz__yikc:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()',
            wddnz__yikc), getattr(wddnz__yikc, 'loc', None))
    oif__qaeau = gen_apply_pysig(len(f_args), kws.keys())
    ijy__rphzu = (func, *f_args) + tuple(kws.values())
    return signature(irpej__rmool, *ijy__rphzu).replace(pysig=oif__qaeau)


def gen_apply_pysig(n_args, kws):
    zom__adtcz = ', '.join(f'arg{amduy__ihr}' for amduy__ihr in range(n_args))
    zom__adtcz = zom__adtcz + ', ' if zom__adtcz else ''
    zdurn__ice = ', '.join(f"{yyu__twpb} = ''" for yyu__twpb in kws)
    nmtd__dikr = f'def apply_stub(func, {zom__adtcz}{zdurn__ice}):\n'
    nmtd__dikr += '    pass\n'
    fqqyh__wexd = {}
    exec(nmtd__dikr, {}, fqqyh__wexd)
    mui__jkzqr = fqqyh__wexd['apply_stub']
    return numba.core.utils.pysignature(mui__jkzqr)


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
        osltr__eozs = get_pivot_output_dtype(data, aggfunc.literal_value)
        nav__urhnm = dtype_to_array_type(osltr__eozs)
        if is_overload_none(_pivot_values):
            raise_bodo_error(
                'Dataframe.pivot_table() requires explicit annotation to determine output columns. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/pandas.html'
                )
        lggit__tnlzw = _pivot_values.meta
        ivp__wscj = len(lggit__tnlzw)
        ndeqh__owk = df.columns.index(index)
        ugxyv__baadf = bodo.hiframes.pd_index_ext.array_type_to_index(df.
            data[ndeqh__owk], types.StringLiteral(index))
        til__bmq = DataFrameType((nav__urhnm,) * ivp__wscj, ugxyv__baadf,
            tuple(lggit__tnlzw))
        return signature(til__bmq, *args)


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
        nav__urhnm = types.Array(types.int64, 1, 'C')
        lggit__tnlzw = _pivot_values.meta
        ivp__wscj = len(lggit__tnlzw)
        ugxyv__baadf = bodo.hiframes.pd_index_ext.array_type_to_index(index
            .data, types.StringLiteral('index'))
        til__bmq = DataFrameType((nav__urhnm,) * ivp__wscj, ugxyv__baadf,
            tuple(lggit__tnlzw))
        return signature(til__bmq, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    nmtd__dikr = 'def impl(keys, dropna, _is_parallel):\n'
    nmtd__dikr += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    nmtd__dikr += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{amduy__ihr}])' for amduy__ihr in range(len(
        keys.types))))
    nmtd__dikr += '    table = arr_info_list_to_table(info_list)\n'
    nmtd__dikr += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    nmtd__dikr += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    nmtd__dikr += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    nmtd__dikr += '    delete_table_decref_arrays(table)\n'
    nmtd__dikr += '    ev.finalize()\n'
    nmtd__dikr += '    return sort_idx, group_labels, ngroups\n'
    fqqyh__wexd = {}
    exec(nmtd__dikr, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, fqqyh__wexd)
    vzjrj__nual = fqqyh__wexd['impl']
    return vzjrj__nual


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    iydts__yut = len(labels)
    ggzif__nkgv = np.zeros(ngroups, dtype=np.int64)
    prt__lby = np.zeros(ngroups, dtype=np.int64)
    jmyoc__fmqgr = 0
    rrour__doq = 0
    for amduy__ihr in range(iydts__yut):
        fvoy__sdg = labels[amduy__ihr]
        if fvoy__sdg < 0:
            jmyoc__fmqgr += 1
        else:
            rrour__doq += 1
            if amduy__ihr == iydts__yut - 1 or fvoy__sdg != labels[
                amduy__ihr + 1]:
                ggzif__nkgv[fvoy__sdg] = jmyoc__fmqgr
                prt__lby[fvoy__sdg] = jmyoc__fmqgr + rrour__doq
                jmyoc__fmqgr += rrour__doq
                rrour__doq = 0
    return ggzif__nkgv, prt__lby


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    vzjrj__nual, syyfi__teaej = gen_shuffle_dataframe(df, keys, _is_parallel)
    return vzjrj__nual


def gen_shuffle_dataframe(df, keys, _is_parallel):
    uhjtk__ezspd = len(df.columns)
    erxs__hpb = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    nmtd__dikr = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        nmtd__dikr += '  return df, keys, get_null_shuffle_info()\n'
        fqqyh__wexd = {}
        exec(nmtd__dikr, {'get_null_shuffle_info': get_null_shuffle_info},
            fqqyh__wexd)
        vzjrj__nual = fqqyh__wexd['impl']
        return vzjrj__nual
    for amduy__ihr in range(uhjtk__ezspd):
        nmtd__dikr += f"""  in_arr{amduy__ihr} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {amduy__ihr})
"""
    nmtd__dikr += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    nmtd__dikr += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{amduy__ihr}])' for amduy__ihr in range(
        erxs__hpb)), ', '.join(f'array_to_info(in_arr{amduy__ihr})' for
        amduy__ihr in range(uhjtk__ezspd)), 'array_to_info(in_index_arr)')
    nmtd__dikr += '  table = arr_info_list_to_table(info_list)\n'
    nmtd__dikr += (
        f'  out_table = shuffle_table(table, {erxs__hpb}, _is_parallel, 1)\n')
    for amduy__ihr in range(erxs__hpb):
        nmtd__dikr += f"""  out_key{amduy__ihr} = info_to_array(info_from_table(out_table, {amduy__ihr}), keys{amduy__ihr}_typ)
"""
    for amduy__ihr in range(uhjtk__ezspd):
        nmtd__dikr += f"""  out_arr{amduy__ihr} = info_to_array(info_from_table(out_table, {amduy__ihr + erxs__hpb}), in_arr{amduy__ihr}_typ)
"""
    nmtd__dikr += f"""  out_arr_index = info_to_array(info_from_table(out_table, {erxs__hpb + uhjtk__ezspd}), ind_arr_typ)
"""
    nmtd__dikr += '  shuffle_info = get_shuffle_info(out_table)\n'
    nmtd__dikr += '  delete_table(out_table)\n'
    nmtd__dikr += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{amduy__ihr}' for amduy__ihr in range(
        uhjtk__ezspd))
    nmtd__dikr += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    nmtd__dikr += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, {gen_const_tup(df.columns)})
"""
    nmtd__dikr += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{amduy__ihr}' for amduy__ihr in range(erxs__hpb)))
    nalu__pjzi = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, 'ind_arr_typ': types.Array(types.int64, 1, 'C') if
        isinstance(df.index, RangeIndexType) else df.index.data}
    nalu__pjzi.update({f'keys{amduy__ihr}_typ': keys.types[amduy__ihr] for
        amduy__ihr in range(erxs__hpb)})
    nalu__pjzi.update({f'in_arr{amduy__ihr}_typ': df.data[amduy__ihr] for
        amduy__ihr in range(uhjtk__ezspd)})
    fqqyh__wexd = {}
    exec(nmtd__dikr, nalu__pjzi, fqqyh__wexd)
    vzjrj__nual = fqqyh__wexd['impl']
    return vzjrj__nual, nalu__pjzi


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        xbzaq__rty = len(data.array_types)
        nmtd__dikr = 'def impl(data, shuffle_info):\n'
        nmtd__dikr += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{amduy__ihr}])' for amduy__ihr in
            range(xbzaq__rty)))
        nmtd__dikr += '  table = arr_info_list_to_table(info_list)\n'
        nmtd__dikr += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for amduy__ihr in range(xbzaq__rty):
            nmtd__dikr += f"""  out_arr{amduy__ihr} = info_to_array(info_from_table(out_table, {amduy__ihr}), data._data[{amduy__ihr}])
"""
        nmtd__dikr += '  delete_table(out_table)\n'
        nmtd__dikr += '  delete_table(table)\n'
        nmtd__dikr += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{amduy__ihr}' for amduy__ihr in range
            (xbzaq__rty))))
        fqqyh__wexd = {}
        exec(nmtd__dikr, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, fqqyh__wexd)
        vzjrj__nual = fqqyh__wexd['impl']
        return vzjrj__nual
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            zkr__qhdi = bodo.utils.conversion.index_to_array(data)
            weedk__oilif = reverse_shuffle(zkr__qhdi, shuffle_info)
            return bodo.utils.conversion.index_from_array(weedk__oilif)
        return impl_index

    def impl_arr(data, shuffle_info):
        icb__gsoyl = [array_to_info(data)]
        aeb__jre = arr_info_list_to_table(icb__gsoyl)
        wmhfg__lgz = reverse_shuffle_table(aeb__jre, shuffle_info)
        weedk__oilif = info_to_array(info_from_table(wmhfg__lgz, 0), data)
        delete_table(wmhfg__lgz)
        delete_table(aeb__jre)
        return weedk__oilif
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    elt__ouvtr = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    zzxm__swsj = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', elt__ouvtr, zzxm__swsj,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    icv__dhx = get_overload_const_bool(ascending)
    awqdf__skfx = grp.selection[0]
    nmtd__dikr = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    gkygi__vzsf = (
        f"lambda S: S.value_counts(ascending={icv__dhx}, _index_name='{awqdf__skfx}')"
        )
    nmtd__dikr += f'    return grp.apply({gkygi__vzsf})\n'
    fqqyh__wexd = {}
    exec(nmtd__dikr, {'bodo': bodo}, fqqyh__wexd)
    vzjrj__nual = fqqyh__wexd['impl']
    return vzjrj__nual


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
    for ulxnv__advvn in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, ulxnv__advvn, no_unliteral
            =True)(create_unsupported_overload(
            f'DataFrameGroupBy.{ulxnv__advvn}'))
    for ulxnv__advvn in groupby_unsupported:
        overload_method(DataFrameGroupByType, ulxnv__advvn, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ulxnv__advvn}'))
    for ulxnv__advvn in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, ulxnv__advvn, no_unliteral
            =True)(create_unsupported_overload(f'SeriesGroupBy.{ulxnv__advvn}')
            )
    for ulxnv__advvn in series_only_unsupported:
        overload_method(DataFrameGroupByType, ulxnv__advvn, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{ulxnv__advvn}'))
    for ulxnv__advvn in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, ulxnv__advvn, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{ulxnv__advvn}'))


_install_groupy_unsupported()
