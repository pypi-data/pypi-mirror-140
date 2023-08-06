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
        cke__vrxq = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, cke__vrxq)


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
        ualfv__mmq = args[0]
        mlxcp__gjwyc = signature.return_type
        omm__wan = cgutils.create_struct_proxy(mlxcp__gjwyc)(context, builder)
        omm__wan.obj = ualfv__mmq
        context.nrt.incref(builder, signature.args[0], ualfv__mmq)
        return omm__wan._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for blaik__nbf in keys:
        selection.remove(blaik__nbf)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    mlxcp__gjwyc = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return mlxcp__gjwyc(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, qte__zpg = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(qte__zpg, (tuple, list)):
                if len(set(qte__zpg).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(qte__zpg).difference(set(grpby.df_type.
                        columns))))
                selection = qte__zpg
            else:
                if qte__zpg not in grpby.df_type.columns:
                    raise_const_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(qte__zpg))
                selection = qte__zpg,
                series_select = True
            vrmes__pxr = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(vrmes__pxr, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, qte__zpg = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(qte__zpg
            ):
            vrmes__pxr = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(qte__zpg)), {}).return_type
            return signature(vrmes__pxr, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    zcl__ruy = arr_type == ArrayItemArrayType(string_array_type)
    sft__bjzp = arr_type.dtype
    if isinstance(sft__bjzp, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {sft__bjzp} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(sft__bjzp, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {sft__bjzp} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(sft__bjzp,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(sft__bjzp, (types.Integer, types.Float, types.Boolean)):
        if zcl__ruy or sft__bjzp == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(sft__bjzp, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not sft__bjzp.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {sft__bjzp} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(sft__bjzp, types.Boolean) and func_name in {'cumsum',
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
    sft__bjzp = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(sft__bjzp, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(sft__bjzp, types.Integer):
            return IntDtype(sft__bjzp)
        return sft__bjzp
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        vzbx__hqh = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{vzbx__hqh}'."
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
    for blaik__nbf in grp.keys:
        if multi_level_names:
            yxp__wgsc = blaik__nbf, ''
        else:
            yxp__wgsc = blaik__nbf
        hikd__mlhul = grp.df_type.columns.index(blaik__nbf)
        data = grp.df_type.data[hikd__mlhul]
        out_columns.append(yxp__wgsc)
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
        sjbju__lprq = tuple(grp.df_type.columns.index(grp.keys[uolmr__enwkx
            ]) for uolmr__enwkx in range(len(grp.keys)))
        mmz__hvti = tuple(grp.df_type.data[hikd__mlhul] for hikd__mlhul in
            sjbju__lprq)
        index = MultiIndexType(mmz__hvti, tuple(types.StringLiteral(
            blaik__nbf) for blaik__nbf in grp.keys))
    else:
        hikd__mlhul = grp.df_type.columns.index(grp.keys[0])
        index = bodo.hiframes.pd_index_ext.array_type_to_index(grp.df_type.
            data[hikd__mlhul], types.StringLiteral(grp.keys[0]))
    wakz__xstp = {}
    yyq__jql = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        wakz__xstp[None, 'size'] = 'size'
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for feltc__rekg in columns:
            hikd__mlhul = grp.df_type.columns.index(feltc__rekg)
            data = grp.df_type.data[hikd__mlhul]
            dmkno__tdule = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                dmkno__tdule = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    cpk__uzox = SeriesType(data.dtype, data, None, string_type)
                    gayby__bpwsl = get_const_func_output_type(func, (
                        cpk__uzox,), {}, typing_context, target_context)
                    if gayby__bpwsl != ArrayItemArrayType(string_array_type):
                        gayby__bpwsl = dtype_to_array_type(gayby__bpwsl)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=feltc__rekg, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    vex__fnc = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    ivic__ljnq = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    fwtr__ywaij = dict(numeric_only=vex__fnc, min_count=
                        ivic__ljnq)
                    ywtg__atl = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwtr__ywaij, ywtg__atl, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    vex__fnc = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    ivic__ljnq = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    fwtr__ywaij = dict(numeric_only=vex__fnc, min_count=
                        ivic__ljnq)
                    ywtg__atl = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwtr__ywaij, ywtg__atl, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    vex__fnc = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    fwtr__ywaij = dict(numeric_only=vex__fnc)
                    ywtg__atl = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwtr__ywaij, ywtg__atl, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    mbhkf__jlwu = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    bcsrw__afoc = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    fwtr__ywaij = dict(axis=mbhkf__jlwu, skipna=bcsrw__afoc)
                    ywtg__atl = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwtr__ywaij, ywtg__atl, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    btt__aqgx = args[0] if len(args) > 0 else kws.pop('ddof', 1
                        )
                    fwtr__ywaij = dict(ddof=btt__aqgx)
                    ywtg__atl = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwtr__ywaij, ywtg__atl, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                gayby__bpwsl, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                zbnqp__ofm = gayby__bpwsl
                out_data.append(zbnqp__ofm)
                out_columns.append(feltc__rekg)
                if func_name == 'agg':
                    jpwzr__awsot = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    wakz__xstp[feltc__rekg, jpwzr__awsot] = feltc__rekg
                else:
                    wakz__xstp[feltc__rekg, func_name] = feltc__rekg
                out_column_type.append(dmkno__tdule)
            else:
                yyq__jql.append(err_msg)
    if func_name == 'sum':
        dolqf__rkauy = any([(ykr__xkdb == ColumnType.NumericalColumn.value) for
            ykr__xkdb in out_column_type])
        if dolqf__rkauy:
            out_data = [ykr__xkdb for ykr__xkdb, fiv__wqp in zip(out_data,
                out_column_type) if fiv__wqp != ColumnType.
                NonNumericalColumn.value]
            out_columns = [ykr__xkdb for ykr__xkdb, fiv__wqp in zip(
                out_columns, out_column_type) if fiv__wqp != ColumnType.
                NonNumericalColumn.value]
            wakz__xstp = {}
            for feltc__rekg in out_columns:
                if grp.as_index is False and feltc__rekg in grp.keys:
                    continue
                wakz__xstp[feltc__rekg, func_name] = feltc__rekg
    edrz__xalw = len(yyq__jql)
    if len(out_data) == 0:
        if edrz__xalw == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(edrz__xalw, ' was' if edrz__xalw == 1 else 's were',
                ','.join(yyq__jql)))
    inm__ecf = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index):
        if isinstance(out_data[0], IntegerArrayType):
            mbdnz__irrsu = IntDtype(out_data[0].dtype)
        else:
            mbdnz__irrsu = out_data[0].dtype
        daf__rqmn = types.none if func_name == 'size' else types.StringLiteral(
            grp.selection[0])
        inm__ecf = SeriesType(mbdnz__irrsu, index=index, name_typ=daf__rqmn)
    return signature(inm__ecf, *args), wakz__xstp


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    vsbzb__hna = True
    if isinstance(f_val, str):
        vsbzb__hna = False
        yhpby__fik = f_val
    elif is_overload_constant_str(f_val):
        vsbzb__hna = False
        yhpby__fik = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        vsbzb__hna = False
        yhpby__fik = bodo.utils.typing.get_builtin_function_name(f_val)
    if not vsbzb__hna:
        if yhpby__fik not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {yhpby__fik}')
        vrmes__pxr = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(vrmes__pxr, (), yhpby__fik, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            hxz__khh = types.functions.MakeFunctionLiteral(f_val)
        else:
            hxz__khh = f_val
        validate_udf('agg', hxz__khh)
        func = get_overload_const_func(hxz__khh, None)
        yra__jawx = func.code if hasattr(func, 'code') else func.__code__
        yhpby__fik = yra__jawx.co_name
        vrmes__pxr = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(vrmes__pxr, (), 'agg', typing_context,
            target_context, hxz__khh)[0].return_type
    return yhpby__fik, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    aanv__ybcm = kws and all(isinstance(wwcv__mxop, types.Tuple) and len(
        wwcv__mxop) == 2 for wwcv__mxop in kws.values())
    if is_overload_none(func) and not aanv__ybcm:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not aanv__ybcm:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    ukaiq__ice = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if aanv__ybcm or is_overload_constant_dict(func):
        if aanv__ybcm:
            pfmmt__hkfln = [get_literal_value(hvl__hjvrf) for hvl__hjvrf,
                hwyoy__vtm in kws.values()]
            vrmf__degu = [get_literal_value(zlecw__vpvc) for hwyoy__vtm,
                zlecw__vpvc in kws.values()]
        else:
            susdq__upl = get_overload_constant_dict(func)
            pfmmt__hkfln = tuple(susdq__upl.keys())
            vrmf__degu = tuple(susdq__upl.values())
        if 'head' in vrmf__degu:
            raise BodoError(
                'Groupby.agg()/aggregate(): head cannot be mixed with other groupby operations.'
                )
        if any(feltc__rekg not in grp.selection and feltc__rekg not in grp.
            keys for feltc__rekg in pfmmt__hkfln):
            raise_const_error(
                f'Selected column names {pfmmt__hkfln} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            vrmf__degu)
        if aanv__ybcm and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        wakz__xstp = {}
        out_columns = []
        out_data = []
        out_column_type = []
        hexx__jwk = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for qxb__uch, f_val in zip(pfmmt__hkfln, vrmf__degu):
            if isinstance(f_val, (tuple, list)):
                ziy__rft = 0
                for hxz__khh in f_val:
                    yhpby__fik, out_tp = get_agg_funcname_and_outtyp(grp,
                        qxb__uch, hxz__khh, typing_context, target_context)
                    ukaiq__ice = yhpby__fik in list_cumulative
                    if yhpby__fik == '<lambda>' and len(f_val) > 1:
                        yhpby__fik = '<lambda_' + str(ziy__rft) + '>'
                        ziy__rft += 1
                    out_columns.append((qxb__uch, yhpby__fik))
                    wakz__xstp[qxb__uch, yhpby__fik] = qxb__uch, yhpby__fik
                    _append_out_type(grp, out_data, out_tp)
            else:
                yhpby__fik, out_tp = get_agg_funcname_and_outtyp(grp,
                    qxb__uch, f_val, typing_context, target_context)
                ukaiq__ice = yhpby__fik in list_cumulative
                if multi_level_names:
                    out_columns.append((qxb__uch, yhpby__fik))
                    wakz__xstp[qxb__uch, yhpby__fik] = qxb__uch, yhpby__fik
                elif not aanv__ybcm:
                    out_columns.append(qxb__uch)
                    wakz__xstp[qxb__uch, yhpby__fik] = qxb__uch
                elif aanv__ybcm:
                    hexx__jwk.append(yhpby__fik)
                _append_out_type(grp, out_data, out_tp)
        if aanv__ybcm:
            for uolmr__enwkx, hrt__hkbqk in enumerate(kws.keys()):
                out_columns.append(hrt__hkbqk)
                wakz__xstp[pfmmt__hkfln[uolmr__enwkx], hexx__jwk[uolmr__enwkx]
                    ] = hrt__hkbqk
        if ukaiq__ice:
            index = grp.df_type.index
        else:
            index = out_tp.index
        inm__ecf = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(inm__ecf, *args), wakz__xstp
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
        ziy__rft = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        wakz__xstp = {}
        qopo__lnr = grp.selection[0]
        for f_val in func.types:
            yhpby__fik, out_tp = get_agg_funcname_and_outtyp(grp, qopo__lnr,
                f_val, typing_context, target_context)
            ukaiq__ice = yhpby__fik in list_cumulative
            if yhpby__fik == '<lambda>':
                yhpby__fik = '<lambda_' + str(ziy__rft) + '>'
                ziy__rft += 1
            out_columns.append(yhpby__fik)
            wakz__xstp[qopo__lnr, yhpby__fik] = yhpby__fik
            _append_out_type(grp, out_data, out_tp)
        if ukaiq__ice:
            index = grp.df_type.index
        else:
            index = out_tp.index
        inm__ecf = DataFrameType(tuple(out_data), index, tuple(out_columns))
        return signature(inm__ecf, *args), wakz__xstp
    yhpby__fik = ''
    if types.unliteral(func) == types.unicode_type:
        yhpby__fik = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        yhpby__fik = bodo.utils.typing.get_builtin_function_name(func)
    if yhpby__fik:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, yhpby__fik, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = grp.df_type.index
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        mbhkf__jlwu = args[0] if len(args) > 0 else kws.pop('axis', 0)
        vex__fnc = args[1] if len(args) > 1 else kws.pop('numeric_only', False)
        bcsrw__afoc = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        fwtr__ywaij = dict(axis=mbhkf__jlwu, numeric_only=vex__fnc)
        ywtg__atl = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', fwtr__ywaij,
            ywtg__atl, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        iolsl__fiv = args[0] if len(args) > 0 else kws.pop('periods', 1)
        gcxrl__oany = args[1] if len(args) > 1 else kws.pop('freq', None)
        mbhkf__jlwu = args[2] if len(args) > 2 else kws.pop('axis', 0)
        bcujo__oqvk = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        fwtr__ywaij = dict(freq=gcxrl__oany, axis=mbhkf__jlwu, fill_value=
            bcujo__oqvk)
        ywtg__atl = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', fwtr__ywaij,
            ywtg__atl, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        aju__dvtxx = args[0] if len(args) > 0 else kws.pop('func', None)
        ufxl__jluk = kws.pop('engine', None)
        jaavc__ipt = kws.pop('engine_kwargs', None)
        fwtr__ywaij = dict(engine=ufxl__jluk, engine_kwargs=jaavc__ipt)
        ywtg__atl = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', fwtr__ywaij, ywtg__atl,
            package_name='pandas', module_name='GroupBy')
    wakz__xstp = {}
    for feltc__rekg in grp.selection:
        out_columns.append(feltc__rekg)
        wakz__xstp[feltc__rekg, name_operation] = feltc__rekg
        hikd__mlhul = grp.df_type.columns.index(feltc__rekg)
        data = grp.df_type.data[hikd__mlhul]
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
            gayby__bpwsl, err_msg = get_groupby_output_dtype(data,
                get_literal_value(aju__dvtxx), grp.df_type.index)
            if err_msg == 'ok':
                data = gayby__bpwsl
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    inm__ecf = DataFrameType(tuple(out_data), index, tuple(out_columns))
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        inm__ecf = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(inm__ecf, *args), wakz__xstp


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
        ufiz__xwjt = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        yqfb__ssy = isinstance(ufiz__xwjt, (SeriesType,
            HeterogeneousSeriesType)
            ) and ufiz__xwjt.const_info is not None or not isinstance(
            ufiz__xwjt, (SeriesType, DataFrameType))
        if yqfb__ssy:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                cepky__ixnpd = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                sjbju__lprq = tuple(grp.df_type.columns.index(grp.keys[
                    uolmr__enwkx]) for uolmr__enwkx in range(len(grp.keys)))
                mmz__hvti = tuple(grp.df_type.data[hikd__mlhul] for
                    hikd__mlhul in sjbju__lprq)
                cepky__ixnpd = MultiIndexType(mmz__hvti, tuple(types.
                    literal(blaik__nbf) for blaik__nbf in grp.keys))
            else:
                hikd__mlhul = grp.df_type.columns.index(grp.keys[0])
                cepky__ixnpd = bodo.hiframes.pd_index_ext.array_type_to_index(
                    grp.df_type.data[hikd__mlhul], types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            umwxs__uqv = tuple(grp.df_type.data[grp.df_type.columns.index(
                feltc__rekg)] for feltc__rekg in grp.keys)
            jdp__mnejd = tuple(types.literal(wwcv__mxop) for wwcv__mxop in
                grp.keys) + get_index_name_types(ufiz__xwjt.index)
            if not grp.as_index:
                umwxs__uqv = types.Array(types.int64, 1, 'C'),
                jdp__mnejd = (types.none,) + get_index_name_types(ufiz__xwjt
                    .index)
            cepky__ixnpd = MultiIndexType(umwxs__uqv +
                get_index_data_arr_types(ufiz__xwjt.index), jdp__mnejd)
        if yqfb__ssy:
            if isinstance(ufiz__xwjt, HeterogeneousSeriesType):
                hwyoy__vtm, itfx__idl = ufiz__xwjt.const_info
                lkbg__bazx = tuple(dtype_to_array_type(froei__azczw) for
                    froei__azczw in ufiz__xwjt.data.types)
                tdr__iuj = DataFrameType(out_data + lkbg__bazx,
                    cepky__ixnpd, out_columns + itfx__idl)
            elif isinstance(ufiz__xwjt, SeriesType):
                hbjg__nxbco, itfx__idl = ufiz__xwjt.const_info
                lkbg__bazx = tuple(dtype_to_array_type(ufiz__xwjt.dtype) for
                    hwyoy__vtm in range(hbjg__nxbco))
                tdr__iuj = DataFrameType(out_data + lkbg__bazx,
                    cepky__ixnpd, out_columns + itfx__idl)
            else:
                kfv__xqhes = get_udf_out_arr_type(ufiz__xwjt)
                if not grp.as_index:
                    tdr__iuj = DataFrameType(out_data + (kfv__xqhes,),
                        cepky__ixnpd, out_columns + ('',))
                else:
                    tdr__iuj = SeriesType(kfv__xqhes.dtype, kfv__xqhes,
                        cepky__ixnpd, None)
        elif isinstance(ufiz__xwjt, SeriesType):
            tdr__iuj = SeriesType(ufiz__xwjt.dtype, ufiz__xwjt.data,
                cepky__ixnpd, ufiz__xwjt.name_typ)
        else:
            tdr__iuj = DataFrameType(ufiz__xwjt.data, cepky__ixnpd,
                ufiz__xwjt.columns)
        bbd__xyqgl = gen_apply_pysig(len(f_args), kws.keys())
        xkgu__cauz = (func, *f_args) + tuple(kws.values())
        return signature(tdr__iuj, *xkgu__cauz).replace(pysig=bbd__xyqgl)

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
    nvvp__rcxvs = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            qxb__uch = grp.selection[0]
            kfv__xqhes = nvvp__rcxvs.data[nvvp__rcxvs.columns.index(qxb__uch)]
            trm__vdl = SeriesType(kfv__xqhes.dtype, kfv__xqhes, nvvp__rcxvs
                .index, types.literal(qxb__uch))
        else:
            xttl__cvz = tuple(nvvp__rcxvs.data[nvvp__rcxvs.columns.index(
                feltc__rekg)] for feltc__rekg in grp.selection)
            trm__vdl = DataFrameType(xttl__cvz, nvvp__rcxvs.index, tuple(
                grp.selection))
    else:
        trm__vdl = nvvp__rcxvs
    ogozt__oyv = trm__vdl,
    ogozt__oyv += tuple(f_args)
    try:
        ufiz__xwjt = get_const_func_output_type(func, ogozt__oyv, kws,
            typing_context, target_context)
    except Exception as eip__zntn:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', eip__zntn),
            getattr(eip__zntn, 'loc', None))
    return ufiz__xwjt


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    ogozt__oyv = (grp,) + f_args
    try:
        ufiz__xwjt = get_const_func_output_type(func, ogozt__oyv, kws, self
            .context, numba.core.registry.cpu_target.target_context, False)
    except Exception as eip__zntn:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', eip__zntn),
            getattr(eip__zntn, 'loc', None))
    bbd__xyqgl = gen_apply_pysig(len(f_args), kws.keys())
    xkgu__cauz = (func, *f_args) + tuple(kws.values())
    return signature(ufiz__xwjt, *xkgu__cauz).replace(pysig=bbd__xyqgl)


def gen_apply_pysig(n_args, kws):
    ard__hov = ', '.join(f'arg{uolmr__enwkx}' for uolmr__enwkx in range(n_args)
        )
    ard__hov = ard__hov + ', ' if ard__hov else ''
    qhjpx__hfe = ', '.join(f"{nzj__iypm} = ''" for nzj__iypm in kws)
    ugfo__wbf = f'def apply_stub(func, {ard__hov}{qhjpx__hfe}):\n'
    ugfo__wbf += '    pass\n'
    qvaqh__nwh = {}
    exec(ugfo__wbf, {}, qvaqh__nwh)
    qjtn__rfn = qvaqh__nwh['apply_stub']
    return numba.core.utils.pysignature(qjtn__rfn)


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
        gayby__bpwsl = get_pivot_output_dtype(data, aggfunc.literal_value)
        zvoxz__ndnd = dtype_to_array_type(gayby__bpwsl)
        if is_overload_none(_pivot_values):
            raise_bodo_error(
                'Dataframe.pivot_table() requires explicit annotation to determine output columns. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/pandas.html'
                )
        yrjpl__cvdhl = _pivot_values.meta
        pbjkq__anf = len(yrjpl__cvdhl)
        hikd__mlhul = df.columns.index(index)
        rrcev__hihle = bodo.hiframes.pd_index_ext.array_type_to_index(df.
            data[hikd__mlhul], types.StringLiteral(index))
        ojjz__qmbo = DataFrameType((zvoxz__ndnd,) * pbjkq__anf,
            rrcev__hihle, tuple(yrjpl__cvdhl))
        return signature(ojjz__qmbo, *args)


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
        zvoxz__ndnd = types.Array(types.int64, 1, 'C')
        yrjpl__cvdhl = _pivot_values.meta
        pbjkq__anf = len(yrjpl__cvdhl)
        rrcev__hihle = bodo.hiframes.pd_index_ext.array_type_to_index(index
            .data, types.StringLiteral('index'))
        ojjz__qmbo = DataFrameType((zvoxz__ndnd,) * pbjkq__anf,
            rrcev__hihle, tuple(yrjpl__cvdhl))
        return signature(ojjz__qmbo, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    ugfo__wbf = 'def impl(keys, dropna, _is_parallel):\n'
    ugfo__wbf += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    ugfo__wbf += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{uolmr__enwkx}])' for uolmr__enwkx in range(
        len(keys.types))))
    ugfo__wbf += '    table = arr_info_list_to_table(info_list)\n'
    ugfo__wbf += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    ugfo__wbf += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    ugfo__wbf += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    ugfo__wbf += '    delete_table_decref_arrays(table)\n'
    ugfo__wbf += '    ev.finalize()\n'
    ugfo__wbf += '    return sort_idx, group_labels, ngroups\n'
    qvaqh__nwh = {}
    exec(ugfo__wbf, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, qvaqh__nwh)
    lchhv__amk = qvaqh__nwh['impl']
    return lchhv__amk


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    bori__dxogm = len(labels)
    syit__ydca = np.zeros(ngroups, dtype=np.int64)
    kzrz__uus = np.zeros(ngroups, dtype=np.int64)
    uti__ozqd = 0
    niuxr__fah = 0
    for uolmr__enwkx in range(bori__dxogm):
        wiwtt__cvkfu = labels[uolmr__enwkx]
        if wiwtt__cvkfu < 0:
            uti__ozqd += 1
        else:
            niuxr__fah += 1
            if uolmr__enwkx == bori__dxogm - 1 or wiwtt__cvkfu != labels[
                uolmr__enwkx + 1]:
                syit__ydca[wiwtt__cvkfu] = uti__ozqd
                kzrz__uus[wiwtt__cvkfu] = uti__ozqd + niuxr__fah
                uti__ozqd += niuxr__fah
                niuxr__fah = 0
    return syit__ydca, kzrz__uus


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    lchhv__amk, hwyoy__vtm = gen_shuffle_dataframe(df, keys, _is_parallel)
    return lchhv__amk


def gen_shuffle_dataframe(df, keys, _is_parallel):
    hbjg__nxbco = len(df.columns)
    xsoqe__evbi = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    ugfo__wbf = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        ugfo__wbf += '  return df, keys, get_null_shuffle_info()\n'
        qvaqh__nwh = {}
        exec(ugfo__wbf, {'get_null_shuffle_info': get_null_shuffle_info},
            qvaqh__nwh)
        lchhv__amk = qvaqh__nwh['impl']
        return lchhv__amk
    for uolmr__enwkx in range(hbjg__nxbco):
        ugfo__wbf += f"""  in_arr{uolmr__enwkx} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {uolmr__enwkx})
"""
    ugfo__wbf += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    ugfo__wbf += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{uolmr__enwkx}])' for uolmr__enwkx in range(
        xsoqe__evbi)), ', '.join(f'array_to_info(in_arr{uolmr__enwkx})' for
        uolmr__enwkx in range(hbjg__nxbco)), 'array_to_info(in_index_arr)')
    ugfo__wbf += '  table = arr_info_list_to_table(info_list)\n'
    ugfo__wbf += (
        f'  out_table = shuffle_table(table, {xsoqe__evbi}, _is_parallel, 1)\n'
        )
    for uolmr__enwkx in range(xsoqe__evbi):
        ugfo__wbf += f"""  out_key{uolmr__enwkx} = info_to_array(info_from_table(out_table, {uolmr__enwkx}), keys{uolmr__enwkx}_typ)
"""
    for uolmr__enwkx in range(hbjg__nxbco):
        ugfo__wbf += f"""  out_arr{uolmr__enwkx} = info_to_array(info_from_table(out_table, {uolmr__enwkx + xsoqe__evbi}), in_arr{uolmr__enwkx}_typ)
"""
    ugfo__wbf += f"""  out_arr_index = info_to_array(info_from_table(out_table, {xsoqe__evbi + hbjg__nxbco}), ind_arr_typ)
"""
    ugfo__wbf += '  shuffle_info = get_shuffle_info(out_table)\n'
    ugfo__wbf += '  delete_table(out_table)\n'
    ugfo__wbf += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{uolmr__enwkx}' for uolmr__enwkx in range
        (hbjg__nxbco))
    ugfo__wbf += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    ugfo__wbf += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, {gen_const_tup(df.columns)})
"""
    ugfo__wbf += '  return out_df, ({},), shuffle_info\n'.format(', '.join(
        f'out_key{uolmr__enwkx}' for uolmr__enwkx in range(xsoqe__evbi)))
    eedle__behoe = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, 'ind_arr_typ': types.Array(types.int64, 1, 'C') if
        isinstance(df.index, RangeIndexType) else df.index.data}
    eedle__behoe.update({f'keys{uolmr__enwkx}_typ': keys.types[uolmr__enwkx
        ] for uolmr__enwkx in range(xsoqe__evbi)})
    eedle__behoe.update({f'in_arr{uolmr__enwkx}_typ': df.data[uolmr__enwkx] for
        uolmr__enwkx in range(hbjg__nxbco)})
    qvaqh__nwh = {}
    exec(ugfo__wbf, eedle__behoe, qvaqh__nwh)
    lchhv__amk = qvaqh__nwh['impl']
    return lchhv__amk, eedle__behoe


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        rgj__zvzf = len(data.array_types)
        ugfo__wbf = 'def impl(data, shuffle_info):\n'
        ugfo__wbf += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{uolmr__enwkx}])' for uolmr__enwkx in
            range(rgj__zvzf)))
        ugfo__wbf += '  table = arr_info_list_to_table(info_list)\n'
        ugfo__wbf += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for uolmr__enwkx in range(rgj__zvzf):
            ugfo__wbf += f"""  out_arr{uolmr__enwkx} = info_to_array(info_from_table(out_table, {uolmr__enwkx}), data._data[{uolmr__enwkx}])
"""
        ugfo__wbf += '  delete_table(out_table)\n'
        ugfo__wbf += '  delete_table(table)\n'
        ugfo__wbf += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{uolmr__enwkx}' for uolmr__enwkx in
            range(rgj__zvzf))))
        qvaqh__nwh = {}
        exec(ugfo__wbf, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, qvaqh__nwh)
        lchhv__amk = qvaqh__nwh['impl']
        return lchhv__amk
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            jtoy__ejw = bodo.utils.conversion.index_to_array(data)
            zbnqp__ofm = reverse_shuffle(jtoy__ejw, shuffle_info)
            return bodo.utils.conversion.index_from_array(zbnqp__ofm)
        return impl_index

    def impl_arr(data, shuffle_info):
        klar__fltp = [array_to_info(data)]
        cqv__iuwzq = arr_info_list_to_table(klar__fltp)
        iagg__pig = reverse_shuffle_table(cqv__iuwzq, shuffle_info)
        zbnqp__ofm = info_to_array(info_from_table(iagg__pig, 0), data)
        delete_table(iagg__pig)
        delete_table(cqv__iuwzq)
        return zbnqp__ofm
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    fwtr__ywaij = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna
        )
    ywtg__atl = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', fwtr__ywaij, ywtg__atl,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    lxqw__mrdp = get_overload_const_bool(ascending)
    vned__guk = grp.selection[0]
    ugfo__wbf = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    bvbia__zcllr = (
        f"lambda S: S.value_counts(ascending={lxqw__mrdp}, _index_name='{vned__guk}')"
        )
    ugfo__wbf += f'    return grp.apply({bvbia__zcllr})\n'
    qvaqh__nwh = {}
    exec(ugfo__wbf, {'bodo': bodo}, qvaqh__nwh)
    lchhv__amk = qvaqh__nwh['impl']
    return lchhv__amk


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
    for nfepk__qvuii in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, nfepk__qvuii, no_unliteral
            =True)(create_unsupported_overload(
            f'DataFrameGroupBy.{nfepk__qvuii}'))
    for nfepk__qvuii in groupby_unsupported:
        overload_method(DataFrameGroupByType, nfepk__qvuii, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{nfepk__qvuii}'))
    for nfepk__qvuii in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, nfepk__qvuii, no_unliteral
            =True)(create_unsupported_overload(f'SeriesGroupBy.{nfepk__qvuii}')
            )
    for nfepk__qvuii in series_only_unsupported:
        overload_method(DataFrameGroupByType, nfepk__qvuii, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{nfepk__qvuii}'))
    for nfepk__qvuii in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, nfepk__qvuii, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{nfepk__qvuii}'))


_install_groupy_unsupported()
