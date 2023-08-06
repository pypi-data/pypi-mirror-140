"""
Implement pd.Series typing and data model handling.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import bound_function, signature
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.io import csv_cpp
from bodo.libs.int_arr_ext import IntDtype
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, raise_bodo_error
_csv_output_is_dir = types.ExternalFunction('csv_output_is_dir', types.int8
    (types.voidptr))
ll.add_symbol('csv_output_is_dir', csv_cpp.csv_output_is_dir)


class SeriesType(types.IterableType, types.ArrayCompatible):
    ndim = 1

    def __init__(self, dtype, data=None, index=None, name_typ=None, dist=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        data = dtype_to_array_type(dtype) if data is None else data
        dtype = dtype.dtype if isinstance(dtype, IntDtype) else dtype
        self.dtype = dtype
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        super(SeriesType, self).__init__(name=
            f'series({dtype}, {data}, {index}, {name_typ}, {dist})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self, dtype=None, index=None, dist=None):
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if dtype is None:
            dtype = self.dtype
            data = self.data
        else:
            data = dtype_to_array_type(dtype)
        return SeriesType(dtype, data, index, self.name_typ, dist)

    @property
    def key(self):
        return self.dtype, self.data, self.index, self.name_typ, self.dist

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if isinstance(other, SeriesType):
            bqq__fzn = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if other.dtype == self.dtype or not other.dtype.is_precise():
                return SeriesType(self.dtype, self.data.unify(typingctx,
                    other.data), bqq__fzn, dist=dist)
        return super(SeriesType, self).unify(typingctx, other)

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, SeriesType) and self.dtype == other.dtype and
            self.data == other.data and self.index == other.index and self.
            name_typ == other.name_typ and self.dist != other.dist):
            return Conversion.safe

    def is_precise(self):
        return self.dtype.is_precise()

    @property
    def iterator_type(self):
        return self.data.iterator_type

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class HeterogeneousSeriesType(types.Type):
    ndim = 1

    def __init__(self, data=None, index=None, name_typ=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        self.dist = Distribution.REP
        super(HeterogeneousSeriesType, self).__init__(name=
            f'heter_series({data}, {index}, {name_typ})')

    def copy(self, index=None, dist=None):
        from bodo.transforms.distributed_analysis import Distribution
        assert dist == Distribution.REP, 'invalid distribution for HeterogeneousSeriesType'
        if index is None:
            index = self.index.copy()
        return HeterogeneousSeriesType(self.data, index, self.name_typ)

    @property
    def key(self):
        return self.data, self.index, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@lower_builtin('getiter', SeriesType)
def series_getiter(context, builder, sig, args):
    pvqi__rjxag = get_series_payload(context, builder, sig.args[0], args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].data))
    return impl(builder, (pvqi__rjxag.data,))


@infer_getattr
class HeterSeriesAttribute(OverloadedKeyAttributeTemplate):
    key = HeterogeneousSeriesType

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            mbkq__xbv = get_overload_const_tuple(S.index.data)
            if attr in mbkq__xbv:
                gwg__vavol = mbkq__xbv.index(attr)
                return S.data[gwg__vavol]


def is_str_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == string_type


def is_dt64_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == types.NPDatetime('ns')


def is_timedelta64_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == types.NPTimedelta('ns')


def is_datetime_date_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == datetime_date_type


class SeriesPayloadType(types.Type):

    def __init__(self, series_type):
        self.series_type = series_type
        super(SeriesPayloadType, self).__init__(name=
            f'SeriesPayloadType({series_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesPayloadType)
class SeriesPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wvci__quva = [('data', fe_type.series_type.data), ('index', fe_type
            .series_type.index), ('name', fe_type.series_type.name_typ)]
        super(SeriesPayloadModel, self).__init__(dmm, fe_type, wvci__quva)


@register_model(HeterogeneousSeriesType)
@register_model(SeriesType)
class SeriesModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = SeriesPayloadType(fe_type)
        wvci__quva = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(SeriesModel, self).__init__(dmm, fe_type, wvci__quva)


def define_series_dtor(context, builder, series_type, payload_type):
    woanx__txt = builder.module
    fcqcw__hsjev = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    wog__ufcau = cgutils.get_or_insert_function(woanx__txt, fcqcw__hsjev,
        name='.dtor.series.{}'.format(series_type))
    if not wog__ufcau.is_declaration:
        return wog__ufcau
    wog__ufcau.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(wog__ufcau.append_basic_block())
    tcfqc__ziv = wog__ufcau.args[0]
    ejczz__frwuu = context.get_value_type(payload_type).as_pointer()
    nwacq__pouy = builder.bitcast(tcfqc__ziv, ejczz__frwuu)
    fzoo__uam = context.make_helper(builder, payload_type, ref=nwacq__pouy)
    context.nrt.decref(builder, series_type.data, fzoo__uam.data)
    context.nrt.decref(builder, series_type.index, fzoo__uam.index)
    context.nrt.decref(builder, series_type.name_typ, fzoo__uam.name)
    builder.ret_void()
    return wog__ufcau


def construct_series(context, builder, series_type, data_val, index_val,
    name_val):
    payload_type = SeriesPayloadType(series_type)
    pvqi__rjxag = cgutils.create_struct_proxy(payload_type)(context, builder)
    pvqi__rjxag.data = data_val
    pvqi__rjxag.index = index_val
    pvqi__rjxag.name = name_val
    cfbdd__lfkhz = context.get_value_type(payload_type)
    tqe__fuz = context.get_abi_sizeof(cfbdd__lfkhz)
    tffoa__gcm = define_series_dtor(context, builder, series_type, payload_type
        )
    yegfv__qfzye = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tqe__fuz), tffoa__gcm)
    fnic__yii = context.nrt.meminfo_data(builder, yegfv__qfzye)
    jjwou__btyq = builder.bitcast(fnic__yii, cfbdd__lfkhz.as_pointer())
    builder.store(pvqi__rjxag._getvalue(), jjwou__btyq)
    series = cgutils.create_struct_proxy(series_type)(context, builder)
    series.meminfo = yegfv__qfzye
    series.parent = cgutils.get_null_value(series.parent.type)
    return series._getvalue()


@intrinsic
def init_series(typingctx, data, index, name=None):
    from bodo.hiframes.pd_index_ext import is_pd_index_type
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    assert is_pd_index_type(index) or isinstance(index, MultiIndexType)
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        data_val, index_val, name_val = args
        series_type = signature.return_type
        hjhv__aors = construct_series(context, builder, series_type,
            data_val, index_val, name_val)
        context.nrt.incref(builder, signature.args[0], data_val)
        context.nrt.incref(builder, signature.args[1], index_val)
        context.nrt.incref(builder, signature.args[2], name_val)
        return hjhv__aors
    if is_heterogeneous_tuple_type(data):
        wxh__sgl = HeterogeneousSeriesType(data, index, name)
    else:
        dtype = data.dtype
        data = if_series_to_array_type(data)
        wxh__sgl = SeriesType(dtype, data, index, name)
    sig = signature(wxh__sgl, data, index, name)
    return sig, codegen


def init_series_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) >= 2 and not kws
    data = args[0]
    index = args[1]
    snso__kloo = self.typemap[data.name]
    if is_heterogeneous_tuple_type(snso__kloo) or isinstance(snso__kloo,
        types.BaseTuple):
        return None
    sixf__nsy = self.typemap[index.name]
    if not isinstance(sixf__nsy, HeterogeneousIndexType
        ) and equiv_set.has_shape(data) and equiv_set.has_shape(index):
        equiv_set.insert_equiv(data, index)
    if equiv_set.has_shape(data):
        return ArrayAnalysis.AnalyzeResult(shape=data, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_init_series = (
    init_series_equiv)


def get_series_payload(context, builder, series_type, value):
    yegfv__qfzye = cgutils.create_struct_proxy(series_type)(context,
        builder, value).meminfo
    payload_type = SeriesPayloadType(series_type)
    fzoo__uam = context.nrt.meminfo_data(builder, yegfv__qfzye)
    ejczz__frwuu = context.get_value_type(payload_type).as_pointer()
    fzoo__uam = builder.bitcast(fzoo__uam, ejczz__frwuu)
    return context.make_helper(builder, payload_type, ref=fzoo__uam)


@intrinsic
def get_series_data(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        pvqi__rjxag = get_series_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, series_typ.data,
            pvqi__rjxag.data)
    wxh__sgl = series_typ.data
    sig = signature(wxh__sgl, series_typ)
    return sig, codegen


@intrinsic
def get_series_index(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        pvqi__rjxag = get_series_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, series_typ.index,
            pvqi__rjxag.index)
    wxh__sgl = series_typ.index
    sig = signature(wxh__sgl, series_typ)
    return sig, codegen


@intrinsic
def get_series_name(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        pvqi__rjxag = get_series_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            pvqi__rjxag.name)
    sig = signature(series_typ.name_typ, series_typ)
    return sig, codegen


def get_series_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ihswx__uek = args[0]
    snso__kloo = self.typemap[ihswx__uek.name].data
    if is_heterogeneous_tuple_type(snso__kloo) or isinstance(snso__kloo,
        types.BaseTuple):
        return None
    if equiv_set.has_shape(ihswx__uek):
        return ArrayAnalysis.AnalyzeResult(shape=ihswx__uek, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_data
    ) = get_series_data_equiv


def get_series_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    ihswx__uek = args[0]
    sixf__nsy = self.typemap[ihswx__uek.name].index
    if isinstance(sixf__nsy, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(ihswx__uek):
        return ArrayAnalysis.AnalyzeResult(shape=ihswx__uek, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_index
    ) = get_series_index_equiv


def alias_ext_init_series(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    if len(args) > 1:
        numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
            arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_series',
    'bodo.hiframes.pd_series_ext'] = alias_ext_init_series


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_series_data',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_series_index',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func


def is_series_type(typ):
    return isinstance(typ, SeriesType)


def if_series_to_array_type(typ):
    if isinstance(typ, SeriesType):
        return typ.data
    return typ


@lower_cast(SeriesType, SeriesType)
def cast_series(context, builder, fromty, toty, val):
    if fromty.copy(index=toty.index) == toty and isinstance(fromty.index,
        bodo.hiframes.pd_index_ext.RangeIndexType) and isinstance(toty.
        index, bodo.hiframes.pd_index_ext.NumericIndexType):
        pvqi__rjxag = get_series_payload(context, builder, fromty, val)
        bqq__fzn = context.cast(builder, pvqi__rjxag.index, fromty.index,
            toty.index)
        context.nrt.incref(builder, fromty.data, pvqi__rjxag.data)
        context.nrt.incref(builder, fromty.name_typ, pvqi__rjxag.name)
        return construct_series(context, builder, toty, pvqi__rjxag.data,
            bqq__fzn, pvqi__rjxag.name)
    if (fromty.dtype == toty.dtype and fromty.data == toty.data and fromty.
        index == toty.index and fromty.name_typ == toty.name_typ and fromty
        .dist != toty.dist):
        return val
    return val


@infer_getattr
class SeriesAttribute(OverloadedKeyAttributeTemplate):
    key = SeriesType

    @bound_function('series.head')
    def resolve_head(self, ary, args, kws):
        cqurr__jmxhw = 'Series.head'
        eur__mkuhd = 'n',
        vpuxy__hsoe = {'n': 5}
        pysig, nvs__wst = bodo.utils.typing.fold_typing_args(cqurr__jmxhw,
            args, kws, eur__mkuhd, vpuxy__hsoe)
        fgba__nhlwp = nvs__wst[0]
        if not is_overload_int(fgba__nhlwp):
            raise BodoError(f"{cqurr__jmxhw}(): 'n' must be an Integer")
        zqngb__fhroe = ary
        return zqngb__fhroe(*nvs__wst).replace(pysig=pysig)

    def _resolve_map_func(self, ary, func, pysig, fname, f_args=None, kws=None
        ):
        dtype = ary.dtype
        if dtype == types.NPDatetime('ns'):
            dtype = pd_timestamp_type
        if dtype == types.NPTimedelta('ns'):
            dtype = pd_timedelta_type
        pijy__bjeu = dtype,
        if f_args is not None:
            pijy__bjeu += tuple(f_args.types)
        if kws is None:
            kws = {}
        mmt__ckqyw = False
        ebe__bzbz = True
        if fname == 'map' and isinstance(func, types.DictType):
            jww__odv = func.value_type
            mmt__ckqyw = True
        else:
            try:
                if types.unliteral(func) == types.unicode_type:
                    if not is_overload_constant_str(func):
                        raise BodoError(
                            f'Series.apply(): string argument (for builtins) must be a compile time constant'
                            )
                    jww__odv = bodo.utils.transform.get_udf_str_return_type(ary
                        , get_overload_const_str(func), self.context,
                        'Series.apply')
                    ebe__bzbz = False
                elif bodo.utils.typing.is_numpy_ufunc(func):
                    jww__odv = func.get_call_type(self.context, (ary,), {}
                        ).return_type
                    ebe__bzbz = False
                else:
                    jww__odv = get_const_func_output_type(func, pijy__bjeu,
                        kws, self.context, numba.core.registry.cpu_target.
                        target_context)
            except Exception as lgdae__jyve:
                raise BodoError(get_udf_error_msg(f'Series.{fname}()',
                    lgdae__jyve))
        if ebe__bzbz:
            if isinstance(jww__odv, (SeriesType, HeterogeneousSeriesType)
                ) and jww__odv.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(jww__odv, HeterogeneousSeriesType):
                dczzr__hclk, wbdvw__zso = jww__odv.const_info
                uva__rhkc = tuple(dtype_to_array_type(t) for t in jww__odv.
                    data.types)
                mnnfx__fvmu = bodo.DataFrameType(uva__rhkc, ary.index,
                    wbdvw__zso)
            elif isinstance(jww__odv, SeriesType):
                ueb__loot, wbdvw__zso = jww__odv.const_info
                uva__rhkc = tuple(dtype_to_array_type(jww__odv.dtype) for
                    dczzr__hclk in range(ueb__loot))
                mnnfx__fvmu = bodo.DataFrameType(uva__rhkc, ary.index,
                    wbdvw__zso)
            else:
                zkaem__sgr = get_udf_out_arr_type(jww__odv, mmt__ckqyw)
                mnnfx__fvmu = SeriesType(zkaem__sgr.dtype, zkaem__sgr, ary.
                    index, ary.name_typ)
        else:
            mnnfx__fvmu = jww__odv
        return signature(mnnfx__fvmu, (func,)).replace(pysig=pysig)

    @bound_function('series.map', no_unliteral=True)
    def resolve_map(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['arg']
        kws.pop('arg', None)
        na_action = args[1] if len(args) > 1 else kws.pop('na_action',
            types.none)
        nnyf__iob = dict(na_action=na_action)
        regc__ztdm = dict(na_action=None)
        check_unsupported_args('Series.map', nnyf__iob, regc__ztdm,
            package_name='pandas', module_name='Series')

        def map_stub(arg, na_action=None):
            pass
        pysig = numba.core.utils.pysignature(map_stub)
        return self._resolve_map_func(ary, func, pysig, 'map')

    @bound_function('series.apply', no_unliteral=True)
    def resolve_apply(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['func']
        kws.pop('func', None)
        lhkdq__xlos = args[1] if len(args) > 1 else kws.pop('convert_dtype',
            types.literal(True))
        f_args = args[2] if len(args) > 2 else kws.pop('args', None)
        nnyf__iob = dict(convert_dtype=lhkdq__xlos)
        lsvr__lxcl = dict(convert_dtype=True)
        check_unsupported_args('Series.apply', nnyf__iob, lsvr__lxcl,
            package_name='pandas', module_name='Series')
        gxydk__rfto = ', '.join("{} = ''".format(czcr__qqlvc) for
            czcr__qqlvc in kws.keys())
        qyp__njtwn = (
            f'def apply_stub(func, convert_dtype=True, args=(), {gxydk__rfto}):\n'
            )
        qyp__njtwn += '    pass\n'
        owfx__auvx = {}
        exec(qyp__njtwn, {}, owfx__auvx)
        wpet__cmext = owfx__auvx['apply_stub']
        pysig = numba.core.utils.pysignature(wpet__cmext)
        return self._resolve_map_func(ary, func, pysig, 'apply', f_args, kws)

    def _resolve_combine_func(self, ary, args, kws):
        kwargs = dict(kws)
        other = args[0] if len(args) > 0 else types.unliteral(kwargs['other'])
        func = args[1] if len(args) > 1 else kwargs['func']
        fill_value = args[2] if len(args) > 2 else types.unliteral(kwargs.
            get('fill_value', types.none))

        def combine_stub(other, func, fill_value=None):
            pass
        pysig = numba.core.utils.pysignature(combine_stub)
        onoon__tvf = ary.dtype
        if onoon__tvf == types.NPDatetime('ns'):
            onoon__tvf = pd_timestamp_type
        dafww__xshc = other.dtype
        if dafww__xshc == types.NPDatetime('ns'):
            dafww__xshc = pd_timestamp_type
        jww__odv = get_const_func_output_type(func, (onoon__tvf,
            dafww__xshc), {}, self.context, numba.core.registry.cpu_target.
            target_context)
        sig = signature(SeriesType(jww__odv, index=ary.index, name_typ=
            types.none), (other, func, fill_value))
        return sig.replace(pysig=pysig)

    @bound_function('series.combine', no_unliteral=True)
    def resolve_combine(self, ary, args, kws):
        return self._resolve_combine_func(ary, args, kws)

    @bound_function('series.pipe', no_unliteral=True)
    def resolve_pipe(self, ary, args, kws):
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, ary,
            args, kws, 'Series')

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            mbkq__xbv = get_overload_const_tuple(S.index.data)
            if attr in mbkq__xbv:
                gwg__vavol = mbkq__xbv.index(attr)
                return S.data[gwg__vavol]


series_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesArrayOperator._op_map.keys() if op not in (operator.lshift,
    operator.rshift))
series_inplace_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesInplaceArrayOperator._op_map.keys() if op not in (operator.
    ilshift, operator.irshift, operator.itruediv))
inplace_binop_to_imm = {operator.iadd: operator.add, operator.isub:
    operator.sub, operator.imul: operator.mul, operator.ifloordiv: operator
    .floordiv, operator.imod: operator.mod, operator.ipow: operator.pow,
    operator.iand: operator.and_, operator.ior: operator.or_, operator.ixor:
    operator.xor}
series_unary_ops = operator.neg, operator.invert, operator.pos
str2str_methods = ('capitalize', 'lower', 'lstrip', 'rstrip', 'strip',
    'swapcase', 'title', 'upper')
str2bool_methods = ('isalnum', 'isalpha', 'isdigit', 'isspace', 'islower',
    'isupper', 'istitle', 'isnumeric', 'isdecimal')


@overload(pd.Series, no_unliteral=True)
def pd_series_overload(data=None, index=None, dtype=None, name=None, copy=
    False, fastpath=False):
    if not is_overload_false(fastpath):
        raise BodoError("pd.Series(): 'fastpath' argument not supported.")
    lfbu__qyy = is_overload_none(data)
    ovmk__zdr = is_overload_none(index)
    wvmct__lsewu = is_overload_none(dtype)
    if lfbu__qyy and ovmk__zdr and wvmct__lsewu:
        raise BodoError(
            'pd.Series() requires at least 1 of data, index, and dtype to not be none'
            )
    if is_series_type(data) and not ovmk__zdr:
        raise BodoError(
            'pd.Series() does not support index value when input data is a Series'
            )
    if isinstance(data, types.DictType):
        raise_bodo_error(
            'pd.Series(): When intializing series with a dictionary, it is required that the dict has constant keys'
            )
    if is_heterogeneous_tuple_type(data) and is_overload_none(dtype):

        def impl_heter(data=None, index=None, dtype=None, name=None, copy=
            False, fastpath=False):
            feu__guezi = bodo.utils.conversion.extract_index_if_none(data,
                index)
            bcwpy__knw = bodo.utils.conversion.to_tuple(data)
            return bodo.hiframes.pd_series_ext.init_series(bcwpy__knw, bodo
                .utils.conversion.convert_to_index(feu__guezi), name)
        return impl_heter
    if lfbu__qyy:
        if wvmct__lsewu:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                ofsu__bbhk = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                feu__guezi = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                vyxv__fkovu = len(feu__guezi)
                bcwpy__knw = np.empty(vyxv__fkovu, np.float64)
                for ggwcb__dygn in numba.parfors.parfor.internal_prange(
                    vyxv__fkovu):
                    bodo.libs.array_kernels.setna(bcwpy__knw, ggwcb__dygn)
                return bodo.hiframes.pd_series_ext.init_series(bcwpy__knw,
                    bodo.utils.conversion.convert_to_index(feu__guezi),
                    ofsu__bbhk)
            return impl
        if bodo.utils.conversion._is_str_dtype(dtype):
            aau__owgy = bodo.string_array_type
        else:
            lzr__olgn = bodo.utils.typing.parse_dtype(dtype, 'pandas.Series')
            if isinstance(lzr__olgn, bodo.libs.int_arr_ext.IntDtype):
                aau__owgy = bodo.IntegerArrayType(lzr__olgn.dtype)
            elif lzr__olgn == bodo.libs.bool_arr_ext.boolean_dtype:
                aau__owgy = bodo.boolean_array
            elif isinstance(lzr__olgn, types.Number) or lzr__olgn in [bodo.
                datetime64ns, bodo.timedelta64ns]:
                aau__owgy = types.Array(lzr__olgn, 1, 'C')
            else:
                raise BodoError(
                    'pd.Series with dtype: {dtype} not currently supported')
        if ovmk__zdr:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                ofsu__bbhk = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                feu__guezi = bodo.hiframes.pd_index_ext.init_range_index(0,
                    0, 1, None)
                numba.parfors.parfor.init_prange()
                vyxv__fkovu = len(feu__guezi)
                bcwpy__knw = bodo.utils.utils.alloc_type(vyxv__fkovu,
                    aau__owgy, (-1,))
                return bodo.hiframes.pd_series_ext.init_series(bcwpy__knw,
                    feu__guezi, ofsu__bbhk)
            return impl
        else:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                ofsu__bbhk = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                feu__guezi = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                vyxv__fkovu = len(feu__guezi)
                bcwpy__knw = bodo.utils.utils.alloc_type(vyxv__fkovu,
                    aau__owgy, (-1,))
                for ggwcb__dygn in numba.parfors.parfor.internal_prange(
                    vyxv__fkovu):
                    bodo.libs.array_kernels.setna(bcwpy__knw, ggwcb__dygn)
                return bodo.hiframes.pd_series_ext.init_series(bcwpy__knw,
                    bodo.utils.conversion.convert_to_index(feu__guezi),
                    ofsu__bbhk)
            return impl

    def impl(data=None, index=None, dtype=None, name=None, copy=False,
        fastpath=False):
        ofsu__bbhk = bodo.utils.conversion.extract_name_if_none(data, name)
        feu__guezi = bodo.utils.conversion.extract_index_if_none(data, index)
        eipet__cxb = bodo.utils.conversion.coerce_to_array(data, True,
            scalar_to_arr_len=len(feu__guezi))
        qsgr__bfitu = bodo.utils.conversion.fix_arr_dtype(eipet__cxb, dtype,
            None, False)
        return bodo.hiframes.pd_series_ext.init_series(qsgr__bfitu, bodo.
            utils.conversion.convert_to_index(feu__guezi), ofsu__bbhk)
    return impl


@overload_method(SeriesType, 'to_csv', no_unliteral=True)
def to_csv_overload(series, path_or_buf=None, sep=',', na_rep='',
    float_format=None, columns=None, header=True, index=True, index_label=
    None, mode='w', encoding=None, compression='infer', quoting=None,
    quotechar='"', line_terminator=None, chunksize=None, date_format=None,
    doublequote=True, escapechar=None, decimal='.', errors='strict',
    _is_parallel=False):
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "Series.to_csv(): 'path_or_buf' argument should be None or string")
    if is_overload_none(path_or_buf):

        def _impl(series, path_or_buf=None, sep=',', na_rep='',
            float_format=None, columns=None, header=True, index=True,
            index_label=None, mode='w', encoding=None, compression='infer',
            quoting=None, quotechar='"', line_terminator=None, chunksize=
            None, date_format=None, doublequote=True, escapechar=None,
            decimal='.', errors='strict', _is_parallel=False):
            with numba.objmode(D='unicode_type'):
                D = series.to_csv(None, sep, na_rep, float_format, columns,
                    header, index, index_label, mode, encoding, compression,
                    quoting, quotechar, line_terminator, chunksize,
                    date_format, doublequote, escapechar, decimal, errors)
            return D
        return _impl

    def _impl(series, path_or_buf=None, sep=',', na_rep='', float_format=
        None, columns=None, header=True, index=True, index_label=None, mode
        ='w', encoding=None, compression='infer', quoting=None, quotechar=
        '"', line_terminator=None, chunksize=None, date_format=None,
        doublequote=True, escapechar=None, decimal='.', errors='strict',
        _is_parallel=False):
        if _is_parallel:
            header &= (bodo.libs.distributed_api.get_rank() == 0
                ) | _csv_output_is_dir(unicode_to_utf8(path_or_buf))
        with numba.objmode(D='unicode_type'):
            D = series.to_csv(None, sep, na_rep, float_format, columns,
                header, index, index_label, mode, encoding, compression,
                quoting, quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors)
        bodo.io.fs_io.csv_write(path_or_buf, D, _is_parallel)
    return _impl


@lower_constant(SeriesType)
def lower_constant_series(context, builder, series_type, pyval):
    data_val = context.get_constant_generic(builder, series_type.data,
        pyval.values)
    index_val = context.get_constant_generic(builder, series_type.index,
        pyval.index)
    name_val = context.get_constant_generic(builder, series_type.name_typ,
        pyval.name)
    fzoo__uam = lir.Constant.literal_struct([data_val, index_val, name_val])
    fzoo__uam = cgutils.global_constant(builder, '.const.payload', fzoo__uam
        ).bitcast(cgutils.voidptr_t)
    qhx__kzu = context.get_constant(types.int64, -1)
    oll__vncmu = context.get_constant_null(types.voidptr)
    yegfv__qfzye = lir.Constant.literal_struct([qhx__kzu, oll__vncmu,
        oll__vncmu, fzoo__uam, qhx__kzu])
    yegfv__qfzye = cgutils.global_constant(builder, '.const.meminfo',
        yegfv__qfzye).bitcast(cgutils.voidptr_t)
    hjhv__aors = lir.Constant.literal_struct([yegfv__qfzye, oll__vncmu])
    return hjhv__aors


series_unsupported_attrs = {'axes', 'array', 'flags', 'at', 'is_unique',
    'sparse', 'attrs'}
series_unsupported_methods = ('set_flags', 'convert_dtypes', 'bool',
    'to_period', 'to_timestamp', '__array__', 'get', 'at', '__iter__',
    'items', 'iteritems', 'pop', 'item', 'xs', 'combine_first', 'agg',
    'aggregate', 'transform', 'expanding', 'ewm', 'clip', 'factorize',
    'mode', 'rank', 'align', 'drop', 'droplevel', 'reindex', 'reindex_like',
    'sample', 'set_axis', 'truncate', 'add_prefix', 'add_suffix', 'filter',
    'interpolate', 'argmin', 'argmax', 'reorder_levels', 'swaplevel',
    'unstack', 'searchsorted', 'ravel', 'squeeze', 'view', 'compare',
    'update', 'asfreq', 'asof', 'first_valid_index', 'last_valid_index',
    'resample', 'tz_convert', 'tz_localize', 'at_time', 'between_time',
    'tshift', 'slice_shift', 'plot', 'hist', 'to_pickle', 'to_excel',
    'to_xarray', 'to_hdf', 'to_sql', 'to_json', 'to_string', 'to_clipboard',
    'to_latex', 'to_markdown')


def _install_series_unsupported():
    for rexdi__zgia in series_unsupported_attrs:
        tftor__hhu = 'Series.' + rexdi__zgia
        overload_attribute(SeriesType, rexdi__zgia)(create_unsupported_overload
            (tftor__hhu))
    for fname in series_unsupported_methods:
        tftor__hhu = 'Series.' + fname
        overload_method(SeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(tftor__hhu))


_install_series_unsupported()
heter_series_unsupported_attrs = {'axes', 'array', 'dtype', 'nbytes',
    'memory_usage', 'hasnans', 'dtypes', 'flags', 'at', 'is_unique',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing',
    'dt', 'str', 'cat', 'sparse', 'attrs'}
heter_series_unsupported_methods = {'set_flags', 'astype', 'convert_dtypes',
    'infer_objects', 'copy', 'bool', 'to_numpy', 'to_period',
    'to_timestamp', 'to_list', 'tolist', '__array__', 'get', 'at', 'iat',
    'iloc', 'loc', '__iter__', 'items', 'iteritems', 'keys', 'pop', 'item',
    'xs', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'combine', 'combine_first', 'round', 'lt', 'gt', 'le', 'ge', 'ne', 'eq',
    'product', 'dot', 'apply', 'agg', 'aggregate', 'transform', 'map',
    'groupby', 'rolling', 'expanding', 'ewm', 'pipe', 'abs', 'all', 'any',
    'autocorr', 'between', 'clip', 'corr', 'count', 'cov', 'cummax',
    'cummin', 'cumprod', 'cumsum', 'describe', 'diff', 'factorize', 'kurt',
    'mad', 'max', 'mean', 'median', 'min', 'mode', 'nlargest', 'nsmallest',
    'pct_change', 'prod', 'quantile', 'rank', 'sem', 'skew', 'std', 'sum',
    'var', 'kurtosis', 'unique', 'nunique', 'value_counts', 'align', 'drop',
    'droplevel', 'drop_duplicates', 'duplicated', 'equals', 'first', 'head',
    'idxmax', 'idxmin', 'isin', 'last', 'reindex', 'reindex_like', 'rename',
    'rename_axis', 'reset_index', 'sample', 'set_axis', 'take', 'tail',
    'truncate', 'where', 'mask', 'add_prefix', 'add_suffix', 'filter',
    'backfill', 'bfill', 'dropna', 'ffill', 'fillna', 'interpolate', 'isna',
    'isnull', 'notna', 'notnull', 'pad', 'replace', 'argsort', 'argmin',
    'argmax', 'reorder_levels', 'sort_values', 'sort_index', 'swaplevel',
    'unstack', 'explode', 'searchsorted', 'ravel', 'repeat', 'squeeze',
    'view', 'append', 'compare', 'update', 'asfreq', 'asof', 'shift',
    'first_valid_index', 'last_valid_index', 'resample', 'tz_convert',
    'tz_localize', 'at_time', 'between_time', 'tshift', 'slice_shift',
    'plot', 'hist', 'to_pickle', 'to_csv', 'to_dict', 'to_excel',
    'to_frame', 'to_xarray', 'to_hdf', 'to_sql', 'to_json', 'to_string',
    'to_clipboard', 'to_latex', 'to_markdown'}


def _install_heter_series_unsupported():
    for rexdi__zgia in heter_series_unsupported_attrs:
        tftor__hhu = 'HeterogeneousSeries.' + rexdi__zgia
        overload_attribute(HeterogeneousSeriesType, rexdi__zgia)(
            create_unsupported_overload(tftor__hhu))
    for fname in heter_series_unsupported_methods:
        tftor__hhu = 'HeterogeneousSeries.' + fname
        overload_method(HeterogeneousSeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(tftor__hhu))


_install_heter_series_unsupported()
