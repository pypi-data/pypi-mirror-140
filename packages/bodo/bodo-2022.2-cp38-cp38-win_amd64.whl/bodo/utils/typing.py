"""
Helper functions to enable typing.
"""
import itertools
import operator
import types as pytypes
import warnings
from inspect import getfullargspec
import numba
import numba.cpython.unicode
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.errors import NumbaError
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, signature
from numba.extending import NativeValue, box, infer, intrinsic, lower_builtin, lower_cast, models, overload, overload_attribute, overload_method, register_jitable, register_model, unbox
import bodo
CONST_DICT_SENTINEL = '$_bodo_const_dict_$'
list_cumulative = {'cumsum', 'cumprod', 'cummin', 'cummax'}


def is_timedelta_type(in_type):
    return in_type in [bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type, bodo.hiframes.datetime_date_ext.
        datetime_timedelta_type]


def is_dtype_nullable(in_dtype):
    return isinstance(in_dtype, (types.Float, types.NPDatetime, types.
        NPTimedelta))


def is_nullable(typ):
    return bodo.utils.utils.is_array_typ(typ, False) and (not isinstance(
        typ, types.Array) or is_dtype_nullable(typ.dtype))


class BodoError(NumbaError):

    def __init__(self, msg, loc=None, locs_in_msg=None):
        if locs_in_msg is None:
            self.locs_in_msg = []
        else:
            self.locs_in_msg = locs_in_msg
        hrd__spyaa = numba.core.errors.termcolor().errmsg
        super(BodoError, self).__init__(hrd__spyaa(msg), loc)


class BodoException(numba.core.errors.TypingError):
    pass


class BodoNotConstError(Exception):
    pass


class BodoConstUpdatedError(Exception):
    pass


def raise_const_error(msg):
    if bodo.transforms.typing_pass.in_partial_typing:
        bodo.transforms.typing_pass.typing_transform_required = True
        raise BodoNotConstError(msg)
    else:
        raise BodoError(msg)


def raise_bodo_error(msg, loc=None):
    if bodo.transforms.typing_pass.in_partial_typing:
        bodo.transforms.typing_pass.typing_transform_required = True
        raise BodoException(msg)
    else:
        dnehv__hhoq = [] if loc is None else [loc]
        raise BodoError(msg, locs_in_msg=dnehv__hhoq)


class BodoWarning(Warning):
    pass


def get_udf_error_msg(context_str, error):
    msg = ''
    if hasattr(error, 'msg'):
        msg = str(error.msg)
    if hasattr(error, 'args') and error.args:
        msg = str(error.args[0])
    loc = ''
    if hasattr(error, 'loc') and error.loc is not None:
        loc = error.loc.strformat()
    return f'{context_str}: user-defined function not supported: {msg}\n{loc}'


class FileInfo:

    def __init__(self):
        self._concat_str = None
        self._concat_left = None

    def get_schema(self, fname):
        kzq__viipn = self.get_full_filename(fname)
        return self._get_schema(kzq__viipn)

    def set_concat(self, concat_str, is_left):
        self._concat_str = concat_str
        self._concat_left = is_left

    def _get_schema(self, fname):
        raise NotImplementedError

    def get_full_filename(self, fname):
        if self._concat_str is None:
            return fname
        if self._concat_left:
            return self._concat_str + fname
        return fname + self._concat_str


class FilenameType(types.Literal):

    def __init__(self, fname, finfo):
        self.fname = fname
        self.schema = finfo.get_schema(fname)
        super(FilenameType, self).__init__(self.fname)

    def __hash__(self):
        return 37

    def __eq__(self, other):
        if isinstance(other, types.FilenameType):
            assert self.schema is not None
            assert other.schema is not None
            return bodo.typeof(self.fname) == bodo.typeof(other.fname
                ) and self.schema == other.schema
        else:
            return False


types.FilenameType = FilenameType


@register_model(types.FilenameType)
class FilenameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gtvz__jhl = dmm.lookup(bodo.typeof(fe_type.fname))
        xjcee__elxe = [(fbdpm__mclq, eqg__umjw) for fbdpm__mclq, eqg__umjw in
            zip(gtvz__jhl._fields, gtvz__jhl._members)]
        super().__init__(dmm, fe_type, xjcee__elxe)


@unbox(FilenameType)
def unbox_file_name_type(typ, obj, c):
    return c.unbox(bodo.typeof(typ.fname), obj)


@lower_cast(types.FilenameType, types.unicode_type)
@lower_cast(types.FilenameType, types.List)
def cast_filename_to_unicode(context, builder, fromty, toty, val):
    return val


@box(FilenameType)
def box_filename_type(typ, val, c):
    return c.box(bodo.typeof(typ.fname), val)


class NotConstant:
    pass


NOT_CONSTANT = NotConstant()


def is_overload_none(val):
    return val is None or val == types.none or getattr(val, 'value', False
        ) is None


def is_overload_constant_bool(val):
    return isinstance(val, bool) or isinstance(val, types.BooleanLiteral
        ) or isinstance(val, types.Omitted) and isinstance(val.value, bool)


def is_overload_bool(val):
    return isinstance(val, types.Boolean) or is_overload_constant_bool(val)


def is_overload_constant_str(val):
    return isinstance(val, str) or isinstance(val, types.StringLiteral
        ) and isinstance(val.literal_value, str) or isinstance(val, types.
        Omitted) and isinstance(val.value, str)


def is_overload_constant_bytes(val):
    return isinstance(val, bytes) or isinstance(val, types.Omitted
        ) and isinstance(val.value, bytes)


def is_overload_constant_list(val):
    return isinstance(val, (list, tuple)) or isinstance(val, types.Omitted
        ) and isinstance(val.value, tuple) or is_initial_value_list_type(val
        ) or isinstance(val, types.LiteralList) or isinstance(val, bodo.
        utils.typing.ListLiteral) or isinstance(val, types.BaseTuple) and all(
        is_literal_type(t) for t in val.types) and (not val.types or val.
        types[0] != types.StringLiteral(CONST_DICT_SENTINEL))


def is_overload_constant_tuple(val):
    return isinstance(val, tuple) or isinstance(val, types.Omitted
        ) and isinstance(val.value, tuple) or isinstance(val, types.BaseTuple
        ) and all(get_overload_const(t) is not NOT_CONSTANT for t in val.types)


def is_initial_value_type(t):
    if not isinstance(t, types.InitialValue) or t.initial_value is None:
        return False
    smqq__fam = t.initial_value
    if isinstance(smqq__fam, dict):
        smqq__fam = smqq__fam.values()
    return not any(isinstance(jxmf__sicm, (types.Poison, numba.core.
        interpreter._UNKNOWN_VALUE)) for jxmf__sicm in smqq__fam)


def is_initial_value_list_type(t):
    return isinstance(t, types.List) and is_initial_value_type(t)


def is_initial_value_dict_type(t):
    return isinstance(t, types.DictType) and is_initial_value_type(t)


def is_overload_constant_dict(val):
    return isinstance(val, types.LiteralStrKeyDict) and all(is_literal_type
        (jxmf__sicm) for jxmf__sicm in val.types
        ) or is_initial_value_dict_type(val) or isinstance(val, DictLiteral
        ) or isinstance(val, types.BaseTuple) and val.types and val.types[0
        ] == types.StringLiteral(CONST_DICT_SENTINEL) or isinstance(val, dict)


def is_overload_constant_number(val):
    return is_overload_constant_int(val) or is_overload_constant_float(val)


def is_overload_constant_nan(val):
    return is_overload_constant_float(val) and np.isnan(
        get_overload_const_float(val))


def is_overload_constant_float(val):
    return isinstance(val, float) or isinstance(val, types.Omitted
        ) and isinstance(val.value, float)


def is_overload_int(val):
    return is_overload_constant_int(val) or isinstance(val, types.Integer)


def is_overload_constant_int(val):
    return isinstance(val, int) or isinstance(val, types.IntegerLiteral
        ) and isinstance(val.literal_value, int) or isinstance(val, types.
        Omitted) and isinstance(val.value, int)


def is_overload_bool_list(val):
    return is_overload_constant_list(val) and all(is_overload_constant_bool
        (jxmf__sicm) for jxmf__sicm in get_overload_const_list(val))


def is_overload_true(val):
    return val == True or val == types.BooleanLiteral(True) or getattr(val,
        'value', False) is True


def is_overload_false(val):
    return val == False or val == types.BooleanLiteral(False) or getattr(val,
        'value', True) is False


def is_overload_zero(val):
    return val == 0 or val == types.IntegerLiteral(0) or getattr(val,
        'value', -1) == 0


def is_overload_str(val, const):
    return val == const or val == types.StringLiteral(const) or getattr(val,
        'value', -1) == const


def get_overload_const(val):
    from bodo.hiframes.datetime_timedelta_ext import _no_input
    if isinstance(val, types.TypeRef):
        val = val.instance_type
    if val == types.none:
        return None
    if val is _no_input:
        return _no_input
    if val is None or isinstance(val, (bool, int, float, str, tuple, types.
        Dispatcher)):
        return val
    if isinstance(val, types.Omitted):
        return val.value
    if isinstance(val, types.LiteralList):
        rjs__uamsn = []
        for jxmf__sicm in val.literal_value:
            thvx__tmczh = get_overload_const(jxmf__sicm)
            if thvx__tmczh == NOT_CONSTANT:
                return NOT_CONSTANT
            else:
                rjs__uamsn.append(thvx__tmczh)
        return rjs__uamsn
    if isinstance(val, types.Literal):
        return val.literal_value
    if isinstance(val, types.Dispatcher):
        return val
    if isinstance(val, types.BaseTuple):
        rjs__uamsn = []
        for jxmf__sicm in val.types:
            thvx__tmczh = get_overload_const(jxmf__sicm)
            if thvx__tmczh == NOT_CONSTANT:
                return NOT_CONSTANT
            else:
                rjs__uamsn.append(thvx__tmczh)
        return tuple(rjs__uamsn)
    if is_initial_value_list_type(val):
        return val.initial_value
    if is_literal_type(val):
        return get_literal_value(val)
    return NOT_CONSTANT


def element_type(val):
    if isinstance(val, (types.List, types.ArrayCompatible)):
        if isinstance(val.dtype, bodo.hiframes.pd_categorical_ext.
            PDCategoricalDtype):
            return val.dtype.elem_type
        if val == bodo.bytes_type:
            return bodo.bytes_type
        return val.dtype
    return types.unliteral(val)


def can_replace(to_replace, value):
    return is_common_scalar_dtype([to_replace, value]) and not (isinstance(
        to_replace, types.Integer) and isinstance(value, types.Float)
        ) and not (isinstance(to_replace, types.Boolean) and isinstance(
        value, (types.Integer, types.Float)))


_const_type_repr = {str: 'string', bool: 'boolean', int: 'integer'}


def ensure_constant_arg(fname, arg_name, val, const_type):
    thvx__tmczh = get_overload_const(val)
    zex__ewa = _const_type_repr.get(const_type, str(const_type))
    if not isinstance(thvx__tmczh, const_type):
        raise BodoError(
            f"{fname}(): argument '{arg_name}' should be a constant {zex__ewa} not {val}"
            )


def ensure_constant_values(fname, arg_name, val, const_values):
    thvx__tmczh = get_overload_const(val)
    if thvx__tmczh not in const_values:
        raise BodoError(
            f"{fname}(): argument '{arg_name}' should be a constant value in {const_values} not '{thvx__tmczh}'"
            )


def check_unsupported_args(fname, args_dict, arg_defaults_dict,
    package_name='pandas', fn_str=None, module_name=''):
    from bodo.hiframes.datetime_timedelta_ext import _no_input
    assert len(args_dict) == len(arg_defaults_dict)
    if fn_str == None:
        fn_str = f'{fname}()'
    rddf__ohem = ''
    xujo__dmyzl = False
    for fbdpm__mclq in args_dict:
        gpr__zsoc = get_overload_const(args_dict[fbdpm__mclq])
        cyc__jzai = arg_defaults_dict[fbdpm__mclq]
        if (gpr__zsoc is NOT_CONSTANT or gpr__zsoc is not None and 
            cyc__jzai is None or gpr__zsoc is None and cyc__jzai is not
            None or gpr__zsoc != cyc__jzai or gpr__zsoc is not _no_input and
            cyc__jzai is _no_input or gpr__zsoc is _no_input and cyc__jzai
             is not _no_input):
            rddf__ohem = (
                f'{fn_str}: {fbdpm__mclq} parameter only supports default value {cyc__jzai}'
                )
            xujo__dmyzl = True
            break
    if xujo__dmyzl and package_name == 'pandas':
        if module_name == 'IO':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/io.html).
"""
        elif module_name == 'General':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/general.html).
"""
        elif module_name == 'DataFrame':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/dataframe.html).
"""
        elif module_name == 'Window':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/window.html).
"""
        elif module_name == 'GroupBy':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/groupby.html).
"""
        elif module_name == 'Series':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/series.html).
"""
        elif module_name == 'HeterogeneousSeries':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/series.html#heterogeneous-series).
"""
        elif module_name == 'Index':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/indexapi.html).
"""
        elif module_name == 'Timestamp':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/timestamp.html).
"""
        elif module_name == 'Timedelta':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/timedelta.html).
"""
        elif module_name == 'DateOffsets':
            rddf__ohem += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/pandas/dateoffsets.html).
"""
    elif xujo__dmyzl and package_name == 'ml':
        rddf__ohem += """
Please check supported ML operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/ml.html).
"""
    elif xujo__dmyzl and package_name == 'numpy':
        rddf__ohem += """
Please check supported Numpy operations here (https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/numpy.html).
"""
    if xujo__dmyzl:
        raise BodoError(rddf__ohem)


def get_overload_const_tuple(val):
    if isinstance(val, tuple):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, tuple)
        return val.value
    if isinstance(val, types.BaseTuple):
        return tuple(get_overload_const(t) for t in val.types)


def get_overload_constant_dict(val):
    if isinstance(val, types.LiteralStrKeyDict):
        return {get_literal_value(yyuh__nzpxw): get_literal_value(
            jxmf__sicm) for yyuh__nzpxw, jxmf__sicm in val.literal_value.
            items()}
    if isinstance(val, DictLiteral):
        return val.literal_value
    if isinstance(val, dict):
        return val
    assert is_initial_value_dict_type(val) or isinstance(val, types.BaseTuple
        ) and val.types and val.types[0] == types.StringLiteral(
        CONST_DICT_SENTINEL), 'invalid const dict'
    if isinstance(val, types.DictType):
        assert val.initial_value is not None, 'invalid dict initial value'
        return val.initial_value
    wqwj__hlxo = [get_overload_const(jxmf__sicm) for jxmf__sicm in val.
        types[1:]]
    return {wqwj__hlxo[2 * dhykn__bhkad]: wqwj__hlxo[2 * dhykn__bhkad + 1] for
        dhykn__bhkad in range(len(wqwj__hlxo) // 2)}


def get_overload_const_str_len(val):
    if isinstance(val, str):
        return len(val)
    if isinstance(val, types.StringLiteral) and isinstance(val.
        literal_value, str):
        return len(val.literal_value)
    if isinstance(val, types.Omitted) and isinstance(val.value, str):
        return len(val.value)


def get_overload_const_list(val):
    if isinstance(val, (list, tuple)):
        return val
    if isinstance(val, types.Omitted) and isinstance(val.value, tuple):
        return val.value
    if is_initial_value_list_type(val):
        return val.initial_value
    if isinstance(val, types.LiteralList):
        return [get_literal_value(jxmf__sicm) for jxmf__sicm in val.
            literal_value]
    if isinstance(val, bodo.utils.typing.ListLiteral):
        return val.literal_value
    if isinstance(val, types.Omitted):
        return [val.value]
    if isinstance(val, types.Literal):
        return [val.literal_value]
    if isinstance(val, types.BaseTuple) and all(is_literal_type(t) for t in
        val.types):
        return tuple(get_literal_value(t) for t in val.types)


def get_overload_const_str(val):
    if isinstance(val, str):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, str)
        return val.value
    if isinstance(val, types.StringLiteral):
        assert isinstance(val.literal_value, str)
        return val.literal_value
    raise BodoError('{} not constant string'.format(val))


def get_overload_const_bytes(val):
    if isinstance(val, bytes):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, bytes)
        return val.value
    raise BodoError('{} not constant binary'.format(val))


def get_overload_const_int(val):
    if isinstance(val, int):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, int)
        return val.value
    if isinstance(val, types.IntegerLiteral):
        assert isinstance(val.literal_value, int)
        return val.literal_value
    raise BodoError('{} not constant integer'.format(val))


def get_overload_const_float(val):
    if isinstance(val, float):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, float)
        return val.value
    raise BodoError('{} not constant float'.format(val))


def get_overload_const_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, bool)
        return val.value
    if isinstance(val, types.BooleanLiteral):
        assert isinstance(val.literal_value, bool)
        return val.literal_value
    raise BodoError('{} not constant boolean'.format(val))


def is_const_func_type(t):
    return isinstance(t, (types.MakeFunctionLiteral, bodo.utils.typing.
        FunctionLiteral, types.Dispatcher))


def get_overload_const_func(val, func_ir):
    if isinstance(val, (types.MakeFunctionLiteral, bodo.utils.typing.
        FunctionLiteral)):
        func = val.literal_value
        if isinstance(func, ir.Expr) and func.op == 'make_function':
            assert func_ir is not None, 'Function expression is make_function but there is no existing IR'
            func = numba.core.ir_utils.convert_code_obj_to_function(func,
                func_ir)
        return func
    if isinstance(val, types.Dispatcher):
        return val.dispatcher.py_func
    if isinstance(val, CPUDispatcher):
        return val.py_func
    raise BodoError("'{}' not a constant function type".format(val))


def is_heterogeneous_tuple_type(t):
    if is_overload_constant_list(t):
        if isinstance(t, types.LiteralList):
            t = types.BaseTuple.from_types(t.types)
        else:
            t = bodo.typeof(tuple(get_overload_const_list(t)))
    if isinstance(t, bodo.NullableTupleType):
        t = t.tuple_typ
    return isinstance(t, types.BaseTuple) and not isinstance(t, types.UniTuple)


def parse_dtype(dtype, func_name=None):
    if isinstance(dtype, types.TypeRef):
        return dtype.instance_type
    if isinstance(dtype, types.Function):
        if dtype.key[0] == float:
            dtype = types.StringLiteral('float')
        elif dtype.key[0] == int:
            dtype = types.StringLiteral('int')
        elif dtype.key[0] == bool:
            dtype = types.StringLiteral('bool')
        elif dtype.key[0] == str:
            dtype = bodo.string_type
    if isinstance(dtype, types.DTypeSpec):
        return dtype.dtype
    if isinstance(dtype, types.Number) or dtype == bodo.string_type:
        return dtype
    try:
        gbonj__jmmyy = get_overload_const_str(dtype)
        if gbonj__jmmyy.startswith('Int') or gbonj__jmmyy.startswith('UInt'):
            return bodo.libs.int_arr_ext.typeof_pd_int_dtype(pd.api.types.
                pandas_dtype(gbonj__jmmyy), None)
        if gbonj__jmmyy == 'boolean':
            return bodo.libs.bool_arr_ext.boolean_dtype
        return numba.np.numpy_support.from_dtype(np.dtype(gbonj__jmmyy))
    except:
        pass
    if func_name is not None:
        raise BodoError(f'{func_name}(): invalid dtype {dtype}')
    else:
        raise BodoError(f'invalid dtype {dtype}')


def is_list_like_index_type(t):
    from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.libs.bool_arr_ext import boolean_array
    return isinstance(t, types.List) or isinstance(t, types.Array
        ) and t.ndim == 1 or isinstance(t, (NumericIndexType, RangeIndexType)
        ) or isinstance(t, SeriesType) or t == boolean_array


def is_tuple_like_type(t):
    return isinstance(t, types.BaseTuple) or is_heterogeneous_tuple_type(t
        ) or isinstance(t, bodo.hiframes.pd_index_ext.HeterogeneousIndexType)


def get_index_names(t, func_name, default_name):
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    gjn__eqwe = '{}: index name should be a constant string'.format(func_name)
    if isinstance(t, MultiIndexType):
        yaglw__lysdm = []
        for dhykn__bhkad, ngxn__gvn in enumerate(t.names_typ):
            if ngxn__gvn == types.none:
                yaglw__lysdm.append('level_{}'.format(dhykn__bhkad))
                continue
            if not is_overload_constant_str(ngxn__gvn):
                raise BodoError(gjn__eqwe)
            yaglw__lysdm.append(get_overload_const_str(ngxn__gvn))
        return tuple(yaglw__lysdm)
    if t.name_typ == types.none:
        return default_name,
    if not is_overload_constant_str(t.name_typ):
        raise BodoError(gjn__eqwe)
    return get_overload_const_str(t.name_typ),


def get_index_data_arr_types(t):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, IntervalIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    if isinstance(t, MultiIndexType):
        return tuple(t.array_types)
    if isinstance(t, (RangeIndexType, PeriodIndexType)):
        return types.Array(types.int64, 1, 'C'),
    if isinstance(t, (NumericIndexType, StringIndexType, BinaryIndexType,
        DatetimeIndexType, TimedeltaIndexType, CategoricalIndexType,
        IntervalIndexType)):
        return t.data,
    raise BodoError(f'Invalid index type {t}')


def get_index_type_from_dtype(t):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, StringIndexType, TimedeltaIndexType
    if t in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type, bodo.
        datetime64ns]:
        return DatetimeIndexType(types.none)
    if t in [bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type, bodo.
        timedelta64ns]:
        return TimedeltaIndexType(types.none)
    if t == bodo.string_type:
        return StringIndexType(types.none)
    if t == bodo.bytes_type:
        return BinaryIndexType(types.none)
    if isinstance(t, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(t, types.none)
    if isinstance(t, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        return CategoricalIndexType(bodo.CategoricalArrayType(t))
    raise BodoError(f'Cannot convert dtype {t} to index type')


def get_val_type_maybe_str_literal(value):
    t = numba.typeof(value)
    if isinstance(value, str):
        t = types.StringLiteral(value)
    return t


def get_index_name_types(t):
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    if isinstance(t, MultiIndexType):
        return t.names_typ
    return t.name_typ,


if types.SliceLiteral in numba.core.pythonapi._boxers.functions:
    warnings.warn('SliceLiteral boxing has been implemented in Numba')
else:

    @box(types.SliceLiteral)
    def box_slice_literal(typ, val, c):
        nntt__avck = typ.literal_value
        nabs__lmjgc = []
        for rxx__wwjnf in ('start', 'stop', 'step'):
            dzt__msjyc = getattr(typ.literal_value, rxx__wwjnf)
            fiicz__mylg = c.pyapi.make_none(
                ) if dzt__msjyc is None else c.pyapi.from_native_value(types
                .literal(dzt__msjyc), dzt__msjyc, c.env_manager)
            nabs__lmjgc.append(fiicz__mylg)
        fqchy__evw = c.pyapi.unserialize(c.pyapi.serialize_object(slice))
        widi__pbtz = c.pyapi.call_function_objargs(fqchy__evw, nabs__lmjgc)
        for fbdpm__mclq in nabs__lmjgc:
            c.pyapi.decref(fbdpm__mclq)
        c.pyapi.decref(fqchy__evw)
        return widi__pbtz


class ListLiteral(types.Literal):
    pass


types.Literal.ctor_map[list] = ListLiteral
register_model(ListLiteral)(models.OpaqueModel)


@unbox(ListLiteral)
def unbox_list_literal(typ, obj, c):
    return NativeValue(c.context.get_dummy_value())


@box(ListLiteral)
def box_list_literal(typ, val, c):
    zosgh__chuqf = typ.literal_value
    jueha__ymage = [c.pyapi.from_native_value(types.literal(jxmf__sicm),
        jxmf__sicm, c.env_manager) for jxmf__sicm in zosgh__chuqf]
    bju__udh = c.pyapi.list_pack(jueha__ymage)
    for fbdpm__mclq in jueha__ymage:
        c.pyapi.decref(fbdpm__mclq)
    return bju__udh


@lower_cast(ListLiteral, types.List)
def list_literal_to_list(context, builder, fromty, toty, val):
    list_vals = tuple(fromty.literal_value)
    sms__jjpn = types.List(toty.dtype)
    return context.compile_internal(builder, lambda : list(list_vals),
        sms__jjpn(), [])


class DictLiteral(types.Literal):
    pass


types.Literal.ctor_map[dict] = DictLiteral
register_model(DictLiteral)(models.OpaqueModel)


@unbox(DictLiteral)
def unbox_dict_literal(typ, obj, c):
    return NativeValue(c.context.get_dummy_value())


class FunctionLiteral(types.Literal, types.Opaque):
    pass


types.Literal.ctor_map[pytypes.FunctionType] = FunctionLiteral
register_model(FunctionLiteral)(models.OpaqueModel)


@unbox(FunctionLiteral)
def unbox_func_literal(typ, obj, c):
    return NativeValue(obj)


types.MakeFunctionLiteral._literal_type_cache = types.MakeFunctionLiteral(
    lambda : 0)


class MetaType(types.Type):

    def __init__(self, meta):
        self.meta = meta
        super(MetaType, self).__init__('MetaType({})'.format(meta))

    def can_convert_from(self, typingctx, other):
        return True

    @property
    def key(self):
        return tuple(self.meta)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


register_model(MetaType)(models.OpaqueModel)


def is_literal_type(t):
    if isinstance(t, types.TypeRef):
        t = t.instance_type
    return isinstance(t, (types.Literal, types.Omitted)) and not isinstance(t,
        types.LiteralStrKeyDict) or t == types.none or isinstance(t, types.
        Dispatcher) or isinstance(t, types.BaseTuple) and all(
        is_literal_type(jxmf__sicm) for jxmf__sicm in t.types
        ) or is_initial_value_type(t) or isinstance(t, (types.DTypeSpec,
        types.Function)) or isinstance(t, bodo.libs.int_arr_ext.IntDtype
        ) or t in (bodo.libs.bool_arr_ext.boolean_dtype, bodo.libs.
        str_arr_ext.string_dtype) or isinstance(t, types.Function
        ) or is_overload_constant_index(t) or is_overload_constant_series(t
        ) or is_overload_constant_dict(t)


def is_overload_constant_index(t):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    return isinstance(t, HeterogeneousIndexType) and is_literal_type(t.data
        ) and is_literal_type(t.name_typ)


def get_overload_constant_index(t):
    assert is_overload_constant_index(t)
    return pd.Index(get_literal_value(t.data), name=get_literal_value(t.
        name_typ))


def is_overload_constant_series(t):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    return isinstance(t, (SeriesType, HeterogeneousSeriesType)
        ) and is_literal_type(t.data) and is_literal_type(t.index
        ) and is_literal_type(t.name_typ)


def get_overload_constant_series(t):
    assert is_overload_constant_series(t)
    return pd.Series(get_literal_value(t.data), get_literal_value(t.index),
        name=get_literal_value(t.name_typ))


def get_literal_value(t):
    if isinstance(t, types.TypeRef):
        t = t.instance_type
    assert is_literal_type(t)
    if t == types.none:
        return None
    if isinstance(t, types.Literal):
        if isinstance(t, types.LiteralStrKeyDict):
            return {get_literal_value(yyuh__nzpxw): get_literal_value(
                jxmf__sicm) for yyuh__nzpxw, jxmf__sicm in t.literal_value.
                items()}
        if isinstance(t, types.LiteralList):
            return [get_literal_value(jxmf__sicm) for jxmf__sicm in t.
                literal_value]
        return t.literal_value
    if isinstance(t, types.Omitted):
        return t.value
    if isinstance(t, types.BaseTuple):
        return tuple(get_literal_value(jxmf__sicm) for jxmf__sicm in t.types)
    if isinstance(t, types.Dispatcher):
        return t
    if is_initial_value_type(t):
        return t.initial_value
    if isinstance(t, (types.DTypeSpec, types.Function)):
        return t
    if isinstance(t, bodo.libs.int_arr_ext.IntDtype):
        return getattr(pd, str(t)[:-2])()
    if t == bodo.libs.bool_arr_ext.boolean_dtype:
        return pd.BooleanDtype()
    if t == bodo.libs.str_arr_ext.string_dtype:
        return pd.StringDtype()
    if is_overload_constant_index(t):
        return get_overload_constant_index(t)
    if is_overload_constant_series(t):
        return get_overload_constant_series(t)
    if is_overload_constant_dict(t):
        return get_overload_constant_dict(t)


def can_literalize_type(t, pyobject_to_literal=False):
    return t in (bodo.string_type, types.bool_) or isinstance(t, (types.
        Integer, types.List, types.SliceType, types.DictType)
        ) or pyobject_to_literal and t == types.pyobject


def dtype_to_array_type(dtype):
    dtype = types.unliteral(dtype)
    if isinstance(dtype, types.List):
        dtype = dtype_to_array_type(dtype.dtype)
    wljpu__ptdp = False
    if isinstance(dtype, types.Optional):
        dtype = dtype.type
        wljpu__ptdp = True
    if dtype == bodo.string_type:
        return bodo.string_array_type
    if dtype == bodo.bytes_type:
        return bodo.binary_array_type
    if bodo.utils.utils.is_array_typ(dtype, False):
        return bodo.ArrayItemArrayType(dtype)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        return bodo.CategoricalArrayType(dtype)
    if isinstance(dtype, bodo.libs.int_arr_ext.IntDtype):
        return bodo.IntegerArrayType(dtype.dtype)
    if dtype == types.bool_:
        return bodo.boolean_array
    if dtype == bodo.datetime_date_type:
        return bodo.hiframes.datetime_date_ext.datetime_date_array_type
    if isinstance(dtype, bodo.Decimal128Type):
        return bodo.DecimalArrayType(dtype.precision, dtype.scale)
    if isinstance(dtype, bodo.libs.struct_arr_ext.StructType):
        return bodo.StructArrayType(tuple(dtype_to_array_type(t) for t in
            dtype.data), dtype.names)
    if isinstance(dtype, types.BaseTuple):
        return bodo.TupleArrayType(tuple(dtype_to_array_type(t) for t in
            dtype.types))
    if isinstance(dtype, types.DictType):
        return bodo.MapArrayType(dtype_to_array_type(dtype.key_type),
            dtype_to_array_type(dtype.value_type))
    if dtype in (bodo.pd_timestamp_type, bodo.hiframes.
        datetime_datetime_ext.datetime_datetime_type):
        return types.Array(bodo.datetime64ns, 1, 'C')
    if dtype in (bodo.pd_timedelta_type, bodo.hiframes.
        datetime_timedelta_ext.datetime_timedelta_type):
        return types.Array(bodo.timedelta64ns, 1, 'C')
    if isinstance(dtype, (types.Number, types.Boolean, types.NPDatetime,
        types.NPTimedelta)):
        orwss__zjum = types.Array(dtype, 1, 'C')
        if wljpu__ptdp:
            return to_nullable_type(orwss__zjum)
        return orwss__zjum
    raise BodoError(f'dtype {dtype} cannot be stored in arrays')


def get_udf_out_arr_type(f_return_type, return_nullable=False):
    if isinstance(f_return_type, types.Optional):
        f_return_type = f_return_type.type
        return_nullable = True
    if f_return_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        f_return_type = types.NPDatetime('ns')
    if f_return_type == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        f_return_type = types.NPTimedelta('ns')
    carfg__zdq = dtype_to_array_type(f_return_type)
    carfg__zdq = to_nullable_type(carfg__zdq
        ) if return_nullable else carfg__zdq
    return carfg__zdq


def equality_always_false(t1, t2):
    string_types = types.UnicodeType, types.StringLiteral, types.UnicodeCharSeq
    return isinstance(t1, string_types) and not isinstance(t2, string_types
        ) or isinstance(t2, string_types) and not isinstance(t1, string_types)


def types_equality_exists(t1, t2):
    lfq__qubr = numba.core.registry.cpu_target.typing_context
    try:
        lfq__qubr.resolve_function_type(operator.eq, (t1, t2), {})
        return True
    except:
        return False


def is_hashable_type(t):
    whitelist_types = (types.UnicodeType, types.StringLiteral, types.
        UnicodeCharSeq, types.Number)
    pwlz__het = (types.bool_, bodo.datetime64ns, bodo.timedelta64ns, bodo.
        pd_timestamp_type, bodo.pd_timedelta_type)
    if isinstance(t, whitelist_types) or t in pwlz__het:
        return True
    lfq__qubr = numba.core.registry.cpu_target.typing_context
    try:
        lfq__qubr.resolve_function_type(hash, (t,), {})
        return True
    except:
        return False


def to_nullable_type(t):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(t, DataFrameType):
        jty__wpj = tuple(to_nullable_type(t) for t in t.data)
        return DataFrameType(jty__wpj, t.index, t.columns, t.dist, t.
            is_table_format)
    if isinstance(t, SeriesType):
        return SeriesType(t.dtype, to_nullable_type(t.data), t.index, t.
            name_typ)
    if isinstance(t, types.Array):
        if t.dtype == types.bool_:
            return bodo.libs.bool_arr_ext.boolean_array
        if isinstance(t.dtype, types.Integer):
            return bodo.libs.int_arr_ext.IntegerArrayType(t.dtype)
    return t


def is_nullable_type(t):
    return t == to_nullable_type(t)


def is_iterable_type(t):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    return bodo.utils.utils.is_array_typ(t, False) or isinstance(t, (
        SeriesType, DataFrameType, types.List, types.BaseTuple, types.
        LiteralList)) or bodo.hiframes.pd_index_ext.is_pd_index_type(t)


def is_scalar_type(t):
    return isinstance(t, (types.Boolean, types.Number, types.StringLiteral)
        ) or t in (bodo.datetime64ns, bodo.timedelta64ns, bodo.string_type,
        bodo.bytes_type, bodo.datetime_date_type, bodo.
        datetime_datetime_type, bodo.datetime_timedelta_type, bodo.
        pd_timestamp_type, bodo.pd_timedelta_type, bodo.month_end_type,
        bodo.week_type, bodo.date_offset_type, types.none)


def is_common_scalar_dtype(scalar_types):
    schx__cintw, oukr__juihp = get_common_scalar_dtype(scalar_types)
    return oukr__juihp


def get_common_scalar_dtype(scalar_types):
    scalar_types = [types.unliteral(fbdpm__mclq) for fbdpm__mclq in
        scalar_types]
    if len(scalar_types) == 0:
        raise_bodo_error(
            'Internal error, length of argument passed to get_common_scalar_dtype scalar_types is 0'
            )
    try:
        yhl__asoq = np.find_common_type([numba.np.numpy_support.as_dtype(t) for
            t in scalar_types], [])
        if yhl__asoq != object:
            return numba.np.numpy_support.from_dtype(yhl__asoq), True
    except numba.core.errors.NumbaNotImplementedError as vqxtv__nll:
        pass
    if scalar_types[0] in (bodo.datetime64ns, bodo.pd_timestamp_type):
        for typ in scalar_types[1:]:
            if typ not in (bodo.datetime64ns, bodo.pd_timestamp_type):
                return None, False
        return bodo.datetime64ns, True
    if scalar_types[0] in (bodo.timedelta64ns, bodo.pd_timedelta_type):
        for typ in scalar_types[1:]:
            if scalar_types[0] not in (bodo.timedelta64ns, bodo.
                pd_timedelta_type):
                return None, False
        return bodo.timedelta64ns, True
    bnijh__capld = itertools.groupby(scalar_types)
    if next(bnijh__capld, True) and not next(bnijh__capld, False):
        return scalar_types[0], True
    return None, False


def find_common_np_dtype(arr_types):
    return numba.np.numpy_support.from_dtype(np.find_common_type([numba.np.
        numpy_support.as_dtype(t.dtype) for t in arr_types], []))


def is_immutable_array(typ):
    return isinstance(typ, (bodo.ArrayItemArrayType, bodo.MapArrayType))


def get_nullable_and_non_nullable_types(array_of_types):
    qkiz__msps = []
    for typ in array_of_types:
        if typ == bodo.libs.bool_arr_ext.boolean_array:
            qkiz__msps.append(types.Array(types.bool_, 1, 'C'))
        elif isinstance(typ, bodo.libs.int_arr_ext.IntegerArrayType):
            qkiz__msps.append(types.Array(typ.dtype, 1, 'C'))
        elif isinstance(typ, types.Array):
            if typ.dtype == types.bool_:
                qkiz__msps.append(bodo.libs.bool_arr_ext.boolean_array)
            if isinstance(typ.dtype, types.Integer):
                qkiz__msps.append(bodo.libs.int_arr_ext.IntegerArrayType(
                    typ.dtype))
        qkiz__msps.append(typ)
    return qkiz__msps


def is_np_arr_typ(t, dtype, ndim=1):
    return isinstance(t, types.Array) and t.dtype == dtype and t.ndim == ndim


def _gen_objmode_overload(func, output_type, attr_name=None, is_function=
    True, single_rank=False):
    if is_function:
        lxwdm__vgmu = getfullargspec(func)
        assert lxwdm__vgmu.varargs is None, 'varargs not supported'
        assert lxwdm__vgmu.varkw is None, 'varkw not supported'
        defaults = [] if lxwdm__vgmu.defaults is None else lxwdm__vgmu.defaults
        trngj__sir = len(lxwdm__vgmu.args) - len(defaults)
        args = lxwdm__vgmu.args[1:] if attr_name else lxwdm__vgmu.args[:]
        dlqdl__vnf = []
        for dhykn__bhkad, elmwv__nwj in enumerate(lxwdm__vgmu.args):
            if dhykn__bhkad < trngj__sir:
                dlqdl__vnf.append(elmwv__nwj)
            elif str(defaults[dhykn__bhkad - trngj__sir]
                ) != '<deprecated parameter>':
                dlqdl__vnf.append(elmwv__nwj + '=' + str(defaults[
                    dhykn__bhkad - trngj__sir]))
            else:
                args.remove(elmwv__nwj)
        if lxwdm__vgmu.kwonlyargs is not None:
            for elmwv__nwj in lxwdm__vgmu.kwonlyargs:
                args.append(f'{elmwv__nwj}={elmwv__nwj}')
                dlqdl__vnf.append(
                    f'{elmwv__nwj}={str(lxwdm__vgmu.kwonlydefaults[elmwv__nwj])}'
                    )
        sig = ', '.join(dlqdl__vnf)
        args = ', '.join(args)
    else:
        sig = 'self'
    type_name = str(output_type)
    if not hasattr(types, type_name):
        type_name = f'objmode_type{ir_utils.next_label()}'
        setattr(types, type_name, output_type)
    if not attr_name:
        func_name = func.__module__.replace('.', '_'
            ) + '_' + func.__name__ + '_func'
    iepip__skir = f'self.{attr_name}' if attr_name else f'{func_name}'
    jdtpc__fupu = f'def overload_impl({sig}):\n'
    jdtpc__fupu += f'    def impl({sig}):\n'
    if single_rank:
        jdtpc__fupu += f'        if bodo.get_rank() == 0:\n'
        wsg__rbj = '    '
    else:
        wsg__rbj = ''
    jdtpc__fupu += (
        f"        {wsg__rbj}with numba.objmode(res='{type_name}'):\n")
    if is_function:
        jdtpc__fupu += f'            {wsg__rbj}res = {iepip__skir}({args})\n'
    else:
        jdtpc__fupu += f'            {wsg__rbj}res = {iepip__skir}\n'
    jdtpc__fupu += f'        return res\n'
    jdtpc__fupu += f'    return impl\n'
    czj__xbgyn = {}
    nrkl__jis = globals()
    if not attr_name:
        nrkl__jis[func_name] = func
    exec(jdtpc__fupu, nrkl__jis, czj__xbgyn)
    mqkd__yyx = czj__xbgyn['overload_impl']
    return mqkd__yyx


def gen_objmode_func_overload(func, output_type=None, single_rank=False):
    try:
        mqkd__yyx = _gen_objmode_overload(func, output_type, is_function=
            True, single_rank=single_rank)
        overload(func, no_unliteral=True)(mqkd__yyx)
    except Exception as vqxtv__nll:
        pass


def gen_objmode_method_overload(obj_type, method_name, method, output_type=
    None, single_rank=False):
    try:
        mqkd__yyx = _gen_objmode_overload(method, output_type, method_name,
            True, single_rank)
        overload_method(obj_type, method_name, no_unliteral=True)(mqkd__yyx)
    except Exception as vqxtv__nll:
        pass


def gen_objmode_attr_overload(obj_type, attr_name, attr, output_type=None,
    single_rank=False):
    try:
        mqkd__yyx = _gen_objmode_overload(attr, output_type, attr_name, 
            False, single_rank)
        overload_attribute(obj_type, attr_name, no_unliteral=True)(mqkd__yyx)
    except Exception as vqxtv__nll:
        pass


@infer
class NumTypeStaticGetItem(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        val, wze__vlgbd = args
        if isinstance(wze__vlgbd, slice) and (isinstance(val, types.
            NumberClass) or isinstance(val, types.TypeRef) and isinstance(
            val.instance_type, (types.NPDatetime, types.NPTimedelta))):
            return signature(types.TypeRef(val.instance_type[wze__vlgbd]),
                *args)


@lower_builtin('static_getitem', types.NumberClass, types.SliceLiteral)
def num_class_type_static_getitem(context, builder, sig, args):
    return context.get_dummy_value()


@overload(itertools.chain, no_unliteral=True)
def chain_overload():
    return lambda : [0]


@register_jitable
def from_iterable_impl(A):
    return bodo.utils.conversion.flatten_array(bodo.utils.conversion.
        coerce_to_array(A))


@intrinsic
def unliteral_val(typingctx, val=None):

    def codegen(context, builder, signature, args):
        return args[0]
    return types.unliteral(val)(val), codegen


def create_unsupported_overload(fname):

    def overload_f(*a, **kws):
        raise BodoError('{} not supported yet'.format(fname))
    return overload_f


def is_numpy_ufunc(func):
    return isinstance(func, types.Function) and isinstance(func.typing_key,
        np.ufunc)


def is_builtin_function(func):
    return isinstance(func, types.Function) and isinstance(func.typing_key,
        pytypes.BuiltinFunctionType)


def get_builtin_function_name(func):
    return func.typing_key.__name__


def construct_pysig(arg_names, defaults):
    jdtpc__fupu = f'def stub('
    for elmwv__nwj in arg_names:
        jdtpc__fupu += elmwv__nwj
        if elmwv__nwj in defaults:
            if isinstance(defaults[elmwv__nwj], str):
                jdtpc__fupu += f"='{defaults[elmwv__nwj]}'"
            else:
                jdtpc__fupu += f'={defaults[elmwv__nwj]}'
        jdtpc__fupu += ', '
    jdtpc__fupu += '):\n'
    jdtpc__fupu += '    pass\n'
    czj__xbgyn = {}
    exec(jdtpc__fupu, {}, czj__xbgyn)
    xjlrg__ovr = czj__xbgyn['stub']
    return numba.core.utils.pysignature(xjlrg__ovr)


def fold_typing_args(func_name, args, kws, arg_names, defaults,
    unsupported_arg_names=()):
    kws = dict(kws)
    thr__rcq = len(arg_names)
    xuzg__hlr = len(args) + len(kws)
    if xuzg__hlr > thr__rcq:
        eao__rjoti = 'argument' if thr__rcq == 1 else 'arguments'
        arwg__xdexy = 'was' if xuzg__hlr == 1 else 'were'
        raise BodoError(
            f'{func_name}(): Too many arguments specified. Function takes {thr__rcq} {eao__rjoti}, but {xuzg__hlr} {arwg__xdexy} provided.'
            )
    hwt__yepfr = bodo.utils.typing.construct_pysig(arg_names, defaults)
    try:
        tavph__qeo = bodo.utils.transform.fold_argument_types(hwt__yepfr,
            args, kws)
    except Exception as qmwm__tqb:
        raise_bodo_error(f'{func_name}(): {qmwm__tqb}')
    if unsupported_arg_names:
        jri__cbgw = {}
        ntrql__hgfq = {}
        for dhykn__bhkad, arg_name in enumerate(arg_names):
            if arg_name in unsupported_arg_names:
                assert arg_name in defaults, f"{func_name}(): '{arg_name}' is unsupported but no default is provided"
                jri__cbgw[arg_name] = tavph__qeo[dhykn__bhkad]
                ntrql__hgfq[arg_name] = defaults[arg_name]
        check_unsupported_args(func_name, jri__cbgw, ntrql__hgfq)
    return hwt__yepfr, tavph__qeo


def _is_pandas_numeric_dtype(dtype):
    return isinstance(dtype, types.Number) or dtype == types.bool_


def type_col_to_index(col_names):
    if all(isinstance(fbdpm__mclq, str) for fbdpm__mclq in col_names):
        return bodo.StringIndexType(None)
    elif all(isinstance(fbdpm__mclq, bytes) for fbdpm__mclq in col_names):
        return bodo.BinaryIndexType(None)
    elif all(isinstance(fbdpm__mclq, (int, float)) for fbdpm__mclq in col_names
        ):
        if any(isinstance(fbdpm__mclq, float) for fbdpm__mclq in col_names):
            return bodo.NumericIndexType(types.float64)
        else:
            return bodo.NumericIndexType(types.int64)
    else:
        return bodo.hiframes.pd_index_ext.HeterogeneousIndexType(col_names)


def index_typ_from_dtype_name(elem_dtype, name):
    ulk__meyw = type(get_index_type_from_dtype(elem_dtype))
    if name is None:
        etup__pun = None
    else:
        etup__pun = types.StringLiteral(name)
    if ulk__meyw == bodo.hiframes.pd_index_ext.NumericIndexType:
        yhf__ugl = ulk__meyw(elem_dtype, etup__pun)
    elif ulk__meyw == bodo.hiframes.pd_index_ext.CategoricalIndexType:
        yhf__ugl = ulk__meyw(bodo.CategoricalArrayType(elem_dtype), etup__pun)
    else:
        yhf__ugl = ulk__meyw(etup__pun)
    return yhf__ugl


def is_safe_arrow_cast(lhs_scalar_typ, rhs_scalar_typ):
    if lhs_scalar_typ == types.unicode_type:
        return rhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type)
    elif lhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type):
        return rhs_scalar_typ == types.unicode_type
    return False


def register_type(type_name, type_value):
    if not isinstance(type_name, str):
        raise BodoError(
            f'register_type(): type name should be a string, not {type(type_name)}'
            )
    if not isinstance(type_value, types.Type):
        raise BodoError(
            f'register_type(): type value should be a valid data type, not {type(type_value)}'
            )
    if hasattr(types, type_name):
        raise BodoError(
            f"register_type(): type name '{type_name}' already exists")
    setattr(types, type_name, type_value)


@box(types.TypeRef)
def box_typeref(typ, val, c):
    return c.pyapi.unserialize(c.pyapi.serialize_object(typ.instance_type))


def check_objmode_output_type(ret_tup, ret_type):
    return tuple(_check_objmode_type(jxmf__sicm, t) for jxmf__sicm, t in
        zip(ret_tup, ret_type.types))


def _is_equiv_array_type(A, B):
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.struct_arr_ext import StructArrayType
    return isinstance(A, StructArrayType) and isinstance(B, MapArrayType
        ) and set(A.data) == {B.value_arr_type
        } and B.key_arr_type.dtype == bodo.string_type or isinstance(A,
        types.Array) and isinstance(B, types.Array
        ) and A.ndim == B.ndim and A.dtype == B.dtype and B.layout in ('A',
        A.layout) and (A.mutable or not B.mutable) and (A.aligned or not B.
        aligned)


def _fix_objmode_df_type(val, val_typ, typ):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if val_typ.dist != typ.dist:
        val_typ = val_typ.copy(dist=typ.dist)
    if isinstance(typ.index, RangeIndexType) and not isinstance(val_typ.
        index, RangeIndexType):
        warnings.warn(BodoWarning(
            f'Dropping Index of objmode output dataframe since RangeIndexType specified in type annotation ({val_typ.index} to {typ.index})'
            ))
        val.reset_index(drop=True, inplace=True)
        val_typ = val_typ.copy(index=typ.index)
    if (val_typ.index.name_typ != types.none and typ.index.name_typ ==
        types.none):
        warnings.warn(BodoWarning(
            f'Dropping name field in Index of objmode output dataframe since none specified in type annotation ({val_typ.index} to {typ.index})'
            ))
        val_typ = val_typ.copy(index=typ.index)
        val.index.name = None
    for dhykn__bhkad, (A, B) in enumerate(zip(val_typ.data, typ.data)):
        if _is_equiv_array_type(A, B):
            val_typ = val_typ.replace_col_type(val_typ.columns[dhykn__bhkad], B
                )
    if val_typ.is_table_format and not typ.is_table_format:
        val_typ = val_typ.copy(is_table_format=False)
    if val_typ != typ:
        wpcdh__vso = pd.Index(val_typ.columns)
        ozkhd__bcqr = pd.Index(typ.columns)
        xgzvl__acuyo = wpcdh__vso.argsort()
        prbg__enhvp = ozkhd__bcqr.argsort()
        fgdx__vwh = val_typ.copy(data=tuple(np.array(val_typ.data)[
            xgzvl__acuyo]), columns=tuple(wpcdh__vso[xgzvl__acuyo]))
        kwh__hkk = typ.copy(data=tuple(np.array(typ.data)[prbg__enhvp]),
            columns=tuple(ozkhd__bcqr[prbg__enhvp]))
        if fgdx__vwh == kwh__hkk:
            val_typ = typ
            val = val.reindex(columns=typ.columns)
    return val, val_typ


def _check_objmode_type(val, typ):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    val_typ = bodo.typeof(val)
    if isinstance(typ, DataFrameType) and isinstance(val_typ, DataFrameType):
        val, val_typ = _fix_objmode_df_type(val, val_typ, typ)
    if _is_equiv_array_type(val_typ, typ):
        val_typ = typ
    if isinstance(val_typ, (types.List, types.Set)):
        val_typ = val_typ.copy(reflected=False)
    if isinstance(val_typ, (types.Integer, types.Float)) and isinstance(typ,
        (types.Integer, types.Float)):
        return val
    if val_typ != typ:
        raise BodoError(
            f"""Invalid objmode data type specified.
User specified:	{typ}
Value type:	{val_typ}"""
            )
    return val


gen_objmode_func_overload(warnings.warn, 'none')
