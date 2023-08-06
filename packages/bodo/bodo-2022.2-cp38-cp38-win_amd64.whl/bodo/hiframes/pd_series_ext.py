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
            vnkmp__pon = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if other.dtype == self.dtype or not other.dtype.is_precise():
                return SeriesType(self.dtype, self.data.unify(typingctx,
                    other.data), vnkmp__pon, dist=dist)
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
    fggo__urhl = get_series_payload(context, builder, sig.args[0], args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].data))
    return impl(builder, (fggo__urhl.data,))


@infer_getattr
class HeterSeriesAttribute(OverloadedKeyAttributeTemplate):
    key = HeterogeneousSeriesType

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            evurl__jhyki = get_overload_const_tuple(S.index.data)
            if attr in evurl__jhyki:
                pupbl__djo = evurl__jhyki.index(attr)
                return S.data[pupbl__djo]


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
        cvsv__qhsk = [('data', fe_type.series_type.data), ('index', fe_type
            .series_type.index), ('name', fe_type.series_type.name_typ)]
        super(SeriesPayloadModel, self).__init__(dmm, fe_type, cvsv__qhsk)


@register_model(HeterogeneousSeriesType)
@register_model(SeriesType)
class SeriesModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = SeriesPayloadType(fe_type)
        cvsv__qhsk = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(SeriesModel, self).__init__(dmm, fe_type, cvsv__qhsk)


def define_series_dtor(context, builder, series_type, payload_type):
    fnwqd__vox = builder.module
    yzy__kpip = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    rpx__zkumt = cgutils.get_or_insert_function(fnwqd__vox, yzy__kpip, name
        ='.dtor.series.{}'.format(series_type))
    if not rpx__zkumt.is_declaration:
        return rpx__zkumt
    rpx__zkumt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(rpx__zkumt.append_basic_block())
    efdb__zxl = rpx__zkumt.args[0]
    ipe__vjvrh = context.get_value_type(payload_type).as_pointer()
    juumi__esjah = builder.bitcast(efdb__zxl, ipe__vjvrh)
    cvkp__sddlp = context.make_helper(builder, payload_type, ref=juumi__esjah)
    context.nrt.decref(builder, series_type.data, cvkp__sddlp.data)
    context.nrt.decref(builder, series_type.index, cvkp__sddlp.index)
    context.nrt.decref(builder, series_type.name_typ, cvkp__sddlp.name)
    builder.ret_void()
    return rpx__zkumt


def construct_series(context, builder, series_type, data_val, index_val,
    name_val):
    payload_type = SeriesPayloadType(series_type)
    fggo__urhl = cgutils.create_struct_proxy(payload_type)(context, builder)
    fggo__urhl.data = data_val
    fggo__urhl.index = index_val
    fggo__urhl.name = name_val
    xifa__kwf = context.get_value_type(payload_type)
    ljm__uvc = context.get_abi_sizeof(xifa__kwf)
    tugt__rjfeq = define_series_dtor(context, builder, series_type,
        payload_type)
    wwsl__racw = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ljm__uvc), tugt__rjfeq)
    mma__nfevb = context.nrt.meminfo_data(builder, wwsl__racw)
    fehqy__grh = builder.bitcast(mma__nfevb, xifa__kwf.as_pointer())
    builder.store(fggo__urhl._getvalue(), fehqy__grh)
    series = cgutils.create_struct_proxy(series_type)(context, builder)
    series.meminfo = wwsl__racw
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
        gkm__sdqmy = construct_series(context, builder, series_type,
            data_val, index_val, name_val)
        context.nrt.incref(builder, signature.args[0], data_val)
        context.nrt.incref(builder, signature.args[1], index_val)
        context.nrt.incref(builder, signature.args[2], name_val)
        return gkm__sdqmy
    if is_heterogeneous_tuple_type(data):
        yyis__zwa = HeterogeneousSeriesType(data, index, name)
    else:
        dtype = data.dtype
        data = if_series_to_array_type(data)
        yyis__zwa = SeriesType(dtype, data, index, name)
    sig = signature(yyis__zwa, data, index, name)
    return sig, codegen


def init_series_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) >= 2 and not kws
    data = args[0]
    index = args[1]
    duv__zujog = self.typemap[data.name]
    if is_heterogeneous_tuple_type(duv__zujog) or isinstance(duv__zujog,
        types.BaseTuple):
        return None
    wfk__mxo = self.typemap[index.name]
    if not isinstance(wfk__mxo, HeterogeneousIndexType
        ) and equiv_set.has_shape(data) and equiv_set.has_shape(index):
        equiv_set.insert_equiv(data, index)
    if equiv_set.has_shape(data):
        return ArrayAnalysis.AnalyzeResult(shape=data, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_init_series = (
    init_series_equiv)


def get_series_payload(context, builder, series_type, value):
    wwsl__racw = cgutils.create_struct_proxy(series_type)(context, builder,
        value).meminfo
    payload_type = SeriesPayloadType(series_type)
    cvkp__sddlp = context.nrt.meminfo_data(builder, wwsl__racw)
    ipe__vjvrh = context.get_value_type(payload_type).as_pointer()
    cvkp__sddlp = builder.bitcast(cvkp__sddlp, ipe__vjvrh)
    return context.make_helper(builder, payload_type, ref=cvkp__sddlp)


@intrinsic
def get_series_data(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        fggo__urhl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.data,
            fggo__urhl.data)
    yyis__zwa = series_typ.data
    sig = signature(yyis__zwa, series_typ)
    return sig, codegen


@intrinsic
def get_series_index(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        fggo__urhl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.index,
            fggo__urhl.index)
    yyis__zwa = series_typ.index
    sig = signature(yyis__zwa, series_typ)
    return sig, codegen


@intrinsic
def get_series_name(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        fggo__urhl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            fggo__urhl.name)
    sig = signature(series_typ.name_typ, series_typ)
    return sig, codegen


def get_series_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    yfokr__dfy = args[0]
    duv__zujog = self.typemap[yfokr__dfy.name].data
    if is_heterogeneous_tuple_type(duv__zujog) or isinstance(duv__zujog,
        types.BaseTuple):
        return None
    if equiv_set.has_shape(yfokr__dfy):
        return ArrayAnalysis.AnalyzeResult(shape=yfokr__dfy, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_data
    ) = get_series_data_equiv


def get_series_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    yfokr__dfy = args[0]
    wfk__mxo = self.typemap[yfokr__dfy.name].index
    if isinstance(wfk__mxo, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(yfokr__dfy):
        return ArrayAnalysis.AnalyzeResult(shape=yfokr__dfy, pre=[])
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
        fggo__urhl = get_series_payload(context, builder, fromty, val)
        vnkmp__pon = context.cast(builder, fggo__urhl.index, fromty.index,
            toty.index)
        context.nrt.incref(builder, fromty.data, fggo__urhl.data)
        context.nrt.incref(builder, fromty.name_typ, fggo__urhl.name)
        return construct_series(context, builder, toty, fggo__urhl.data,
            vnkmp__pon, fggo__urhl.name)
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
        amumf__nlu = 'Series.head'
        rqe__kkj = 'n',
        eqcwa__icul = {'n': 5}
        pysig, eokhz__lgtuh = bodo.utils.typing.fold_typing_args(amumf__nlu,
            args, kws, rqe__kkj, eqcwa__icul)
        vmre__xlhd = eokhz__lgtuh[0]
        if not is_overload_int(vmre__xlhd):
            raise BodoError(f"{amumf__nlu}(): 'n' must be an Integer")
        fpen__elic = ary
        return fpen__elic(*eokhz__lgtuh).replace(pysig=pysig)

    def _resolve_map_func(self, ary, func, pysig, fname, f_args=None, kws=None
        ):
        dtype = ary.dtype
        if dtype == types.NPDatetime('ns'):
            dtype = pd_timestamp_type
        if dtype == types.NPTimedelta('ns'):
            dtype = pd_timedelta_type
        pjwzv__wzu = dtype,
        if f_args is not None:
            pjwzv__wzu += tuple(f_args.types)
        if kws is None:
            kws = {}
        aarm__nmz = False
        ztmvg__fsta = True
        if fname == 'map' and isinstance(func, types.DictType):
            brs__sis = func.value_type
            aarm__nmz = True
        else:
            try:
                if types.unliteral(func) == types.unicode_type:
                    if not is_overload_constant_str(func):
                        raise BodoError(
                            f'Series.apply(): string argument (for builtins) must be a compile time constant'
                            )
                    brs__sis = bodo.utils.transform.get_udf_str_return_type(ary
                        , get_overload_const_str(func), self.context,
                        'Series.apply')
                    ztmvg__fsta = False
                elif bodo.utils.typing.is_numpy_ufunc(func):
                    brs__sis = func.get_call_type(self.context, (ary,), {}
                        ).return_type
                    ztmvg__fsta = False
                else:
                    brs__sis = get_const_func_output_type(func, pjwzv__wzu,
                        kws, self.context, numba.core.registry.cpu_target.
                        target_context)
            except Exception as ibc__trtds:
                raise BodoError(get_udf_error_msg(f'Series.{fname}()',
                    ibc__trtds))
        if ztmvg__fsta:
            if isinstance(brs__sis, (SeriesType, HeterogeneousSeriesType)
                ) and brs__sis.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(brs__sis, HeterogeneousSeriesType):
                wyj__vcs, snhya__rygqd = brs__sis.const_info
                vol__fgg = tuple(dtype_to_array_type(t) for t in brs__sis.
                    data.types)
                hwqh__wxp = bodo.DataFrameType(vol__fgg, ary.index,
                    snhya__rygqd)
            elif isinstance(brs__sis, SeriesType):
                aht__kaop, snhya__rygqd = brs__sis.const_info
                vol__fgg = tuple(dtype_to_array_type(brs__sis.dtype) for
                    wyj__vcs in range(aht__kaop))
                hwqh__wxp = bodo.DataFrameType(vol__fgg, ary.index,
                    snhya__rygqd)
            else:
                ijpv__qrynv = get_udf_out_arr_type(brs__sis, aarm__nmz)
                hwqh__wxp = SeriesType(ijpv__qrynv.dtype, ijpv__qrynv, ary.
                    index, ary.name_typ)
        else:
            hwqh__wxp = brs__sis
        return signature(hwqh__wxp, (func,)).replace(pysig=pysig)

    @bound_function('series.map', no_unliteral=True)
    def resolve_map(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['arg']
        kws.pop('arg', None)
        na_action = args[1] if len(args) > 1 else kws.pop('na_action',
            types.none)
        ycvc__nylc = dict(na_action=na_action)
        lkmvy__gpjt = dict(na_action=None)
        check_unsupported_args('Series.map', ycvc__nylc, lkmvy__gpjt,
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
        vbrji__gybek = args[1] if len(args) > 1 else kws.pop('convert_dtype',
            types.literal(True))
        f_args = args[2] if len(args) > 2 else kws.pop('args', None)
        ycvc__nylc = dict(convert_dtype=vbrji__gybek)
        jgrp__eyyr = dict(convert_dtype=True)
        check_unsupported_args('Series.apply', ycvc__nylc, jgrp__eyyr,
            package_name='pandas', module_name='Series')
        bmc__oqlnb = ', '.join("{} = ''".format(pvtv__bqn) for pvtv__bqn in
            kws.keys())
        rot__xcb = (
            f'def apply_stub(func, convert_dtype=True, args=(), {bmc__oqlnb}):\n'
            )
        rot__xcb += '    pass\n'
        zdnm__jvxzn = {}
        exec(rot__xcb, {}, zdnm__jvxzn)
        kdvkx__drp = zdnm__jvxzn['apply_stub']
        pysig = numba.core.utils.pysignature(kdvkx__drp)
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
        yxov__oezqu = ary.dtype
        if yxov__oezqu == types.NPDatetime('ns'):
            yxov__oezqu = pd_timestamp_type
        lghw__hdcdy = other.dtype
        if lghw__hdcdy == types.NPDatetime('ns'):
            lghw__hdcdy = pd_timestamp_type
        brs__sis = get_const_func_output_type(func, (yxov__oezqu,
            lghw__hdcdy), {}, self.context, numba.core.registry.cpu_target.
            target_context)
        sig = signature(SeriesType(brs__sis, index=ary.index, name_typ=
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
            evurl__jhyki = get_overload_const_tuple(S.index.data)
            if attr in evurl__jhyki:
                pupbl__djo = evurl__jhyki.index(attr)
                return S.data[pupbl__djo]


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
    nwlo__uzgn = is_overload_none(data)
    jmaxs__lsiu = is_overload_none(index)
    bpt__ause = is_overload_none(dtype)
    if nwlo__uzgn and jmaxs__lsiu and bpt__ause:
        raise BodoError(
            'pd.Series() requires at least 1 of data, index, and dtype to not be none'
            )
    if is_series_type(data) and not jmaxs__lsiu:
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
            cjk__mdh = bodo.utils.conversion.extract_index_if_none(data, index)
            uzb__wtz = bodo.utils.conversion.to_tuple(data)
            return bodo.hiframes.pd_series_ext.init_series(uzb__wtz, bodo.
                utils.conversion.convert_to_index(cjk__mdh), name)
        return impl_heter
    if nwlo__uzgn:
        if bpt__ause:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                grka__rsgam = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                cjk__mdh = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                gdihb__dwfge = len(cjk__mdh)
                uzb__wtz = np.empty(gdihb__dwfge, np.float64)
                for uoph__xvgre in numba.parfors.parfor.internal_prange(
                    gdihb__dwfge):
                    bodo.libs.array_kernels.setna(uzb__wtz, uoph__xvgre)
                return bodo.hiframes.pd_series_ext.init_series(uzb__wtz,
                    bodo.utils.conversion.convert_to_index(cjk__mdh),
                    grka__rsgam)
            return impl
        if bodo.utils.conversion._is_str_dtype(dtype):
            gkzg__dfpuy = bodo.string_array_type
        else:
            fkaw__cnur = bodo.utils.typing.parse_dtype(dtype, 'pandas.Series')
            if isinstance(fkaw__cnur, bodo.libs.int_arr_ext.IntDtype):
                gkzg__dfpuy = bodo.IntegerArrayType(fkaw__cnur.dtype)
            elif fkaw__cnur == bodo.libs.bool_arr_ext.boolean_dtype:
                gkzg__dfpuy = bodo.boolean_array
            elif isinstance(fkaw__cnur, types.Number) or fkaw__cnur in [bodo
                .datetime64ns, bodo.timedelta64ns]:
                gkzg__dfpuy = types.Array(fkaw__cnur, 1, 'C')
            else:
                raise BodoError(
                    'pd.Series with dtype: {dtype} not currently supported')
        if jmaxs__lsiu:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                grka__rsgam = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                cjk__mdh = bodo.hiframes.pd_index_ext.init_range_index(0, 0,
                    1, None)
                numba.parfors.parfor.init_prange()
                gdihb__dwfge = len(cjk__mdh)
                uzb__wtz = bodo.utils.utils.alloc_type(gdihb__dwfge,
                    gkzg__dfpuy, (-1,))
                return bodo.hiframes.pd_series_ext.init_series(uzb__wtz,
                    cjk__mdh, grka__rsgam)
            return impl
        else:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                grka__rsgam = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                cjk__mdh = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                gdihb__dwfge = len(cjk__mdh)
                uzb__wtz = bodo.utils.utils.alloc_type(gdihb__dwfge,
                    gkzg__dfpuy, (-1,))
                for uoph__xvgre in numba.parfors.parfor.internal_prange(
                    gdihb__dwfge):
                    bodo.libs.array_kernels.setna(uzb__wtz, uoph__xvgre)
                return bodo.hiframes.pd_series_ext.init_series(uzb__wtz,
                    bodo.utils.conversion.convert_to_index(cjk__mdh),
                    grka__rsgam)
            return impl

    def impl(data=None, index=None, dtype=None, name=None, copy=False,
        fastpath=False):
        grka__rsgam = bodo.utils.conversion.extract_name_if_none(data, name)
        cjk__mdh = bodo.utils.conversion.extract_index_if_none(data, index)
        kbqa__ccer = bodo.utils.conversion.coerce_to_array(data, True,
            scalar_to_arr_len=len(cjk__mdh))
        mcg__jahj = bodo.utils.conversion.fix_arr_dtype(kbqa__ccer, dtype,
            None, False)
        return bodo.hiframes.pd_series_ext.init_series(mcg__jahj, bodo.
            utils.conversion.convert_to_index(cjk__mdh), grka__rsgam)
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
    cvkp__sddlp = lir.Constant.literal_struct([data_val, index_val, name_val])
    cvkp__sddlp = cgutils.global_constant(builder, '.const.payload',
        cvkp__sddlp).bitcast(cgutils.voidptr_t)
    tuvq__aybfq = context.get_constant(types.int64, -1)
    rqfwm__sgsxy = context.get_constant_null(types.voidptr)
    wwsl__racw = lir.Constant.literal_struct([tuvq__aybfq, rqfwm__sgsxy,
        rqfwm__sgsxy, cvkp__sddlp, tuvq__aybfq])
    wwsl__racw = cgutils.global_constant(builder, '.const.meminfo', wwsl__racw
        ).bitcast(cgutils.voidptr_t)
    gkm__sdqmy = lir.Constant.literal_struct([wwsl__racw, rqfwm__sgsxy])
    return gkm__sdqmy


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
    for rrxzz__vytzo in series_unsupported_attrs:
        syq__tpjb = 'Series.' + rrxzz__vytzo
        overload_attribute(SeriesType, rrxzz__vytzo)(
            create_unsupported_overload(syq__tpjb))
    for fname in series_unsupported_methods:
        syq__tpjb = 'Series.' + fname
        overload_method(SeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(syq__tpjb))


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
    for rrxzz__vytzo in heter_series_unsupported_attrs:
        syq__tpjb = 'HeterogeneousSeries.' + rrxzz__vytzo
        overload_attribute(HeterogeneousSeriesType, rrxzz__vytzo)(
            create_unsupported_overload(syq__tpjb))
    for fname in heter_series_unsupported_methods:
        syq__tpjb = 'HeterogeneousSeries.' + fname
        overload_method(HeterogeneousSeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(syq__tpjb))


_install_heter_series_unsupported()
