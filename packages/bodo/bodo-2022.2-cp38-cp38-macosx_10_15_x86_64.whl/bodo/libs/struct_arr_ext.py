"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(okn__klh, False) for okn__klh in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(okn__klh,
                str) for okn__klh in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(dypsa__ojh.dtype for dypsa__ojh in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(okn__klh) for okn__klh in d.keys())
        data = tuple(dtype_to_array_type(dypsa__ojh) for dypsa__ojh in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(okn__klh, False) for okn__klh in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        abuu__ccfsj = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, abuu__ccfsj)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        abuu__ccfsj = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, abuu__ccfsj)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    rhp__eaelb = builder.module
    otixh__qczmk = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gntl__tfe = cgutils.get_or_insert_function(rhp__eaelb, otixh__qczmk,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not gntl__tfe.is_declaration:
        return gntl__tfe
    gntl__tfe.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gntl__tfe.append_basic_block())
    yuhux__mlls = gntl__tfe.args[0]
    udb__dybg = context.get_value_type(payload_type).as_pointer()
    lkzg__bzl = builder.bitcast(yuhux__mlls, udb__dybg)
    hedgg__kfy = context.make_helper(builder, payload_type, ref=lkzg__bzl)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), hedgg__kfy.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        hedgg__kfy.null_bitmap)
    builder.ret_void()
    return gntl__tfe


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    fzsmm__rjxpu = context.get_value_type(payload_type)
    znuma__hvt = context.get_abi_sizeof(fzsmm__rjxpu)
    apqk__kjqjt = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    rhzfx__ewsz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, znuma__hvt), apqk__kjqjt)
    gzcm__qum = context.nrt.meminfo_data(builder, rhzfx__ewsz)
    ylafb__laav = builder.bitcast(gzcm__qum, fzsmm__rjxpu.as_pointer())
    hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder)
    ryqcd__xlg = []
    ljtzq__xjrih = 0
    for arr_typ in struct_arr_type.data:
        syby__ffd = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        mbir__iyoi = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(ljtzq__xjrih, 
            ljtzq__xjrih + syby__ffd)])
        arr = gen_allocate_array(context, builder, arr_typ, mbir__iyoi, c)
        ryqcd__xlg.append(arr)
        ljtzq__xjrih += syby__ffd
    hedgg__kfy.data = cgutils.pack_array(builder, ryqcd__xlg
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, ryqcd__xlg)
    ged__cocr = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    yxv__jpn = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [ged__cocr])
    null_bitmap_ptr = yxv__jpn.data
    hedgg__kfy.null_bitmap = yxv__jpn._getvalue()
    builder.store(hedgg__kfy._getvalue(), ylafb__laav)
    return rhzfx__ewsz, hedgg__kfy.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    ihz__mrgv = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        sbvcn__bwdvq = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            sbvcn__bwdvq)
        ihz__mrgv.append(arr.data)
    baj__rkj = cgutils.pack_array(c.builder, ihz__mrgv
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, ihz__mrgv)
    mjhw__tcjtg = cgutils.alloca_once_value(c.builder, baj__rkj)
    dzv__oblv = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(okn__klh.dtype)) for okn__klh in data_typ]
    wajd__vnjaf = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, dzv__oblv))
    yzrw__ydrg = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, okn__klh) for okn__klh in names])
    jipp__pgz = cgutils.alloca_once_value(c.builder, yzrw__ydrg)
    return mjhw__tcjtg, wajd__vnjaf, jipp__pgz


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    pck__nwpce = all(isinstance(dypsa__ojh, types.Array) and dypsa__ojh.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for dypsa__ojh in typ.data)
    if pck__nwpce:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        mxc__tgs = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            mxc__tgs, i) for i in range(1, mxc__tgs.type.count)], lir.
            IntType(64))
    rhzfx__ewsz, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if pck__nwpce:
        mjhw__tcjtg, wajd__vnjaf, jipp__pgz = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        otixh__qczmk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        gntl__tfe = cgutils.get_or_insert_function(c.builder.module,
            otixh__qczmk, name='struct_array_from_sequence')
        c.builder.call(gntl__tfe, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(mjhw__tcjtg, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(wajd__vnjaf,
            lir.IntType(8).as_pointer()), c.builder.bitcast(jipp__pgz, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    weyxe__vfukm = c.context.make_helper(c.builder, typ)
    weyxe__vfukm.meminfo = rhzfx__ewsz
    dbyng__ehqaq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(weyxe__vfukm._getvalue(), is_error=dbyng__ehqaq)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    lmlf__ekir = context.insert_const_string(builder.module, 'pandas')
    ait__jhlge = c.pyapi.import_module_noblock(lmlf__ekir)
    wmaej__tqx = c.pyapi.object_getattr_string(ait__jhlge, 'NA')
    with cgutils.for_range(builder, n_structs) as loop:
        mmerh__mav = loop.index
        wqi__tserz = seq_getitem(builder, context, val, mmerh__mav)
        set_bitmap_bit(builder, null_bitmap_ptr, mmerh__mav, 0)
        for toir__mkul in range(len(typ.data)):
            arr_typ = typ.data[toir__mkul]
            data_arr = builder.extract_value(data_tup, toir__mkul)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            epb__ljzk, ibdyb__otr = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, mmerh__mav])
        hqep__tojmp = is_na_value(builder, context, wqi__tserz, wmaej__tqx)
        zlf__hqf = builder.icmp_unsigned('!=', hqep__tojmp, lir.Constant(
            hqep__tojmp.type, 1))
        with builder.if_then(zlf__hqf):
            set_bitmap_bit(builder, null_bitmap_ptr, mmerh__mav, 1)
            for toir__mkul in range(len(typ.data)):
                arr_typ = typ.data[toir__mkul]
                if is_tuple_array:
                    rpt__ukiqw = c.pyapi.tuple_getitem(wqi__tserz, toir__mkul)
                else:
                    rpt__ukiqw = c.pyapi.dict_getitem_string(wqi__tserz,
                        typ.names[toir__mkul])
                hqep__tojmp = is_na_value(builder, context, rpt__ukiqw,
                    wmaej__tqx)
                zlf__hqf = builder.icmp_unsigned('!=', hqep__tojmp, lir.
                    Constant(hqep__tojmp.type, 1))
                with builder.if_then(zlf__hqf):
                    rpt__ukiqw = to_arr_obj_if_list_obj(c, context, builder,
                        rpt__ukiqw, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        rpt__ukiqw).value
                    data_arr = builder.extract_value(data_tup, toir__mkul)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    epb__ljzk, ibdyb__otr = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, mmerh__mav, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(wqi__tserz)
    c.pyapi.decref(ait__jhlge)
    c.pyapi.decref(wmaej__tqx)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    weyxe__vfukm = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    gzcm__qum = context.nrt.meminfo_data(builder, weyxe__vfukm.meminfo)
    ylafb__laav = builder.bitcast(gzcm__qum, context.get_value_type(
        payload_type).as_pointer())
    hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ylafb__laav))
    return hedgg__kfy


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    hedgg__kfy = _get_struct_arr_payload(c.context, c.builder, typ, val)
    epb__ljzk, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), hedgg__kfy.null_bitmap).data
    pck__nwpce = all(isinstance(dypsa__ojh, types.Array) and dypsa__ojh.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for dypsa__ojh in typ.data)
    if pck__nwpce:
        mjhw__tcjtg, wajd__vnjaf, jipp__pgz = _get_C_API_ptrs(c, hedgg__kfy
            .data, typ.data, typ.names)
        otixh__qczmk = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        tmkv__nmhvv = cgutils.get_or_insert_function(c.builder.module,
            otixh__qczmk, name='np_array_from_struct_array')
        arr = c.builder.call(tmkv__nmhvv, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(mjhw__tcjtg, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            wajd__vnjaf, lir.IntType(8).as_pointer()), c.builder.bitcast(
            jipp__pgz, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, hedgg__kfy.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    lmlf__ekir = context.insert_const_string(builder.module, 'numpy')
    iknn__sgp = c.pyapi.import_module_noblock(lmlf__ekir)
    nkv__wup = c.pyapi.object_getattr_string(iknn__sgp, 'object_')
    euy__vchu = c.pyapi.long_from_longlong(length)
    habkb__qudqh = c.pyapi.call_method(iknn__sgp, 'ndarray', (euy__vchu,
        nkv__wup))
    zioa__tfxkm = c.pyapi.object_getattr_string(iknn__sgp, 'nan')
    with cgutils.for_range(builder, length) as loop:
        mmerh__mav = loop.index
        pyarray_setitem(builder, context, habkb__qudqh, mmerh__mav, zioa__tfxkm
            )
        arf__wzax = get_bitmap_bit(builder, null_bitmap_ptr, mmerh__mav)
        qtht__ikm = builder.icmp_unsigned('!=', arf__wzax, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(qtht__ikm):
            if is_tuple_array:
                wqi__tserz = c.pyapi.tuple_new(len(typ.data))
            else:
                wqi__tserz = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(zioa__tfxkm)
                    c.pyapi.tuple_setitem(wqi__tserz, i, zioa__tfxkm)
                else:
                    c.pyapi.dict_setitem_string(wqi__tserz, typ.names[i],
                        zioa__tfxkm)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                epb__ljzk, bnpv__irnf = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, mmerh__mav])
                with builder.if_then(bnpv__irnf):
                    epb__ljzk, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, mmerh__mav])
                    rigg__itb = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(wqi__tserz, i, rigg__itb)
                    else:
                        c.pyapi.dict_setitem_string(wqi__tserz, typ.names[i
                            ], rigg__itb)
                        c.pyapi.decref(rigg__itb)
            pyarray_setitem(builder, context, habkb__qudqh, mmerh__mav,
                wqi__tserz)
            c.pyapi.decref(wqi__tserz)
    c.pyapi.decref(iknn__sgp)
    c.pyapi.decref(nkv__wup)
    c.pyapi.decref(euy__vchu)
    c.pyapi.decref(zioa__tfxkm)
    return habkb__qudqh


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    vdhk__qhetq = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if vdhk__qhetq == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for qqo__oconh in range(vdhk__qhetq)])
    elif nested_counts_type.count < vdhk__qhetq:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for qqo__oconh in range(
            vdhk__qhetq - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(dypsa__ojh) for dypsa__ojh in
            names_typ.types)
    gsxzs__asvr = tuple(dypsa__ojh.instance_type for dypsa__ojh in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(gsxzs__asvr, names)

    def codegen(context, builder, sig, args):
        ccu__mbj, nested_counts, qqo__oconh, qqo__oconh = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        rhzfx__ewsz, qqo__oconh, qqo__oconh = construct_struct_array(context,
            builder, struct_arr_type, ccu__mbj, nested_counts)
        weyxe__vfukm = context.make_helper(builder, struct_arr_type)
        weyxe__vfukm.meminfo = rhzfx__ewsz
        return weyxe__vfukm._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(okn__klh, str) for
            okn__klh in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        abuu__ccfsj = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, abuu__ccfsj)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        abuu__ccfsj = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, abuu__ccfsj)


def define_struct_dtor(context, builder, struct_type, payload_type):
    rhp__eaelb = builder.module
    otixh__qczmk = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gntl__tfe = cgutils.get_or_insert_function(rhp__eaelb, otixh__qczmk,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not gntl__tfe.is_declaration:
        return gntl__tfe
    gntl__tfe.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gntl__tfe.append_basic_block())
    yuhux__mlls = gntl__tfe.args[0]
    udb__dybg = context.get_value_type(payload_type).as_pointer()
    lkzg__bzl = builder.bitcast(yuhux__mlls, udb__dybg)
    hedgg__kfy = context.make_helper(builder, payload_type, ref=lkzg__bzl)
    for i in range(len(struct_type.data)):
        fqg__tizp = builder.extract_value(hedgg__kfy.null_bitmap, i)
        qtht__ikm = builder.icmp_unsigned('==', fqg__tizp, lir.Constant(
            fqg__tizp.type, 1))
        with builder.if_then(qtht__ikm):
            val = builder.extract_value(hedgg__kfy.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return gntl__tfe


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    gzcm__qum = context.nrt.meminfo_data(builder, struct.meminfo)
    ylafb__laav = builder.bitcast(gzcm__qum, context.get_value_type(
        payload_type).as_pointer())
    hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(ylafb__laav))
    return hedgg__kfy, ylafb__laav


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    lmlf__ekir = context.insert_const_string(builder.module, 'pandas')
    ait__jhlge = c.pyapi.import_module_noblock(lmlf__ekir)
    wmaej__tqx = c.pyapi.object_getattr_string(ait__jhlge, 'NA')
    mdha__dbb = []
    nulls = []
    for i, dypsa__ojh in enumerate(typ.data):
        rigg__itb = c.pyapi.dict_getitem_string(val, typ.names[i])
        rghq__sprs = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        ypusp__hyxq = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(dypsa__ojh)))
        hqep__tojmp = is_na_value(builder, context, rigg__itb, wmaej__tqx)
        qtht__ikm = builder.icmp_unsigned('!=', hqep__tojmp, lir.Constant(
            hqep__tojmp.type, 1))
        with builder.if_then(qtht__ikm):
            builder.store(context.get_constant(types.uint8, 1), rghq__sprs)
            field_val = c.pyapi.to_native_value(dypsa__ojh, rigg__itb).value
            builder.store(field_val, ypusp__hyxq)
        mdha__dbb.append(builder.load(ypusp__hyxq))
        nulls.append(builder.load(rghq__sprs))
    c.pyapi.decref(ait__jhlge)
    c.pyapi.decref(wmaej__tqx)
    rhzfx__ewsz = construct_struct(context, builder, typ, mdha__dbb, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = rhzfx__ewsz
    dbyng__ehqaq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=dbyng__ehqaq)


@box(StructType)
def box_struct(typ, val, c):
    fexs__alfvx = c.pyapi.dict_new(len(typ.data))
    hedgg__kfy, qqo__oconh = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(fexs__alfvx, typ.names[i], c.pyapi.
            borrow_none())
        fqg__tizp = c.builder.extract_value(hedgg__kfy.null_bitmap, i)
        qtht__ikm = c.builder.icmp_unsigned('==', fqg__tizp, lir.Constant(
            fqg__tizp.type, 1))
        with c.builder.if_then(qtht__ikm):
            iwyki__zomz = c.builder.extract_value(hedgg__kfy.data, i)
            c.context.nrt.incref(c.builder, val_typ, iwyki__zomz)
            rpt__ukiqw = c.pyapi.from_native_value(val_typ, iwyki__zomz, c.
                env_manager)
            c.pyapi.dict_setitem_string(fexs__alfvx, typ.names[i], rpt__ukiqw)
            c.pyapi.decref(rpt__ukiqw)
    c.context.nrt.decref(c.builder, typ, val)
    return fexs__alfvx


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(dypsa__ojh) for dypsa__ojh in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, rckjt__lbgej = args
        payload_type = StructPayloadType(struct_type.data)
        fzsmm__rjxpu = context.get_value_type(payload_type)
        znuma__hvt = context.get_abi_sizeof(fzsmm__rjxpu)
        apqk__kjqjt = define_struct_dtor(context, builder, struct_type,
            payload_type)
        rhzfx__ewsz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, znuma__hvt), apqk__kjqjt)
        gzcm__qum = context.nrt.meminfo_data(builder, rhzfx__ewsz)
        ylafb__laav = builder.bitcast(gzcm__qum, fzsmm__rjxpu.as_pointer())
        hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        hedgg__kfy.data = data
        hedgg__kfy.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for qqo__oconh in range(len(
            data_typ.types))])
        builder.store(hedgg__kfy._getvalue(), ylafb__laav)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = rhzfx__ewsz
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hedgg__kfy, qqo__oconh = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hedgg__kfy.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        hedgg__kfy, qqo__oconh = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hedgg__kfy.null_bitmap)
    pxcts__uitgu = types.UniTuple(types.int8, len(struct_typ.data))
    return pxcts__uitgu(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, qqo__oconh, val = args
        hedgg__kfy, ylafb__laav = _get_struct_payload(context, builder,
            struct_typ, struct)
        hnh__hudx = hedgg__kfy.data
        jsq__ylha = builder.insert_value(hnh__hudx, val, field_ind)
        jkkmc__nmk = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, jkkmc__nmk, hnh__hudx)
        context.nrt.incref(builder, jkkmc__nmk, jsq__ylha)
        hedgg__kfy.data = jsq__ylha
        builder.store(hedgg__kfy._getvalue(), ylafb__laav)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    xlvr__gmxzq = get_overload_const_str(ind)
    if xlvr__gmxzq not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            xlvr__gmxzq, struct))
    return struct.names.index(xlvr__gmxzq)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    fzsmm__rjxpu = context.get_value_type(payload_type)
    znuma__hvt = context.get_abi_sizeof(fzsmm__rjxpu)
    apqk__kjqjt = define_struct_dtor(context, builder, struct_type,
        payload_type)
    rhzfx__ewsz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, znuma__hvt), apqk__kjqjt)
    gzcm__qum = context.nrt.meminfo_data(builder, rhzfx__ewsz)
    ylafb__laav = builder.bitcast(gzcm__qum, fzsmm__rjxpu.as_pointer())
    hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder)
    hedgg__kfy.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    hedgg__kfy.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(hedgg__kfy._getvalue(), ylafb__laav)
    return rhzfx__ewsz


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    qpfbx__ycok = tuple(d.dtype for d in struct_arr_typ.data)
    bfyaa__rxsys = StructType(qpfbx__ycok, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        qsluk__spnl, ind = args
        hedgg__kfy = _get_struct_arr_payload(context, builder,
            struct_arr_typ, qsluk__spnl)
        mdha__dbb = []
        frtu__yzb = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            sbvcn__bwdvq = builder.extract_value(hedgg__kfy.data, i)
            vkh__wkp = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                sbvcn__bwdvq, ind])
            frtu__yzb.append(vkh__wkp)
            ymoo__gaf = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            qtht__ikm = builder.icmp_unsigned('==', vkh__wkp, lir.Constant(
                vkh__wkp.type, 1))
            with builder.if_then(qtht__ikm):
                kifq__lxp = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    sbvcn__bwdvq, ind])
                builder.store(kifq__lxp, ymoo__gaf)
            mdha__dbb.append(builder.load(ymoo__gaf))
        if isinstance(bfyaa__rxsys, types.DictType):
            rkh__ehx = [context.insert_const_string(builder.module,
                kdkci__fzi) for kdkci__fzi in struct_arr_typ.names]
            fvk__zawnn = cgutils.pack_array(builder, mdha__dbb)
            fhhp__gfa = cgutils.pack_array(builder, rkh__ehx)

            def impl(names, vals):
                d = {}
                for i, kdkci__fzi in enumerate(names):
                    d[kdkci__fzi] = vals[i]
                return d
            sze__imeig = context.compile_internal(builder, impl,
                bfyaa__rxsys(types.Tuple(tuple(types.StringLiteral(
                kdkci__fzi) for kdkci__fzi in struct_arr_typ.names)), types
                .Tuple(qpfbx__ycok)), [fhhp__gfa, fvk__zawnn])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                qpfbx__ycok), fvk__zawnn)
            return sze__imeig
        rhzfx__ewsz = construct_struct(context, builder, bfyaa__rxsys,
            mdha__dbb, frtu__yzb)
        struct = context.make_helper(builder, bfyaa__rxsys)
        struct.meminfo = rhzfx__ewsz
        return struct._getvalue()
    return bfyaa__rxsys(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hedgg__kfy = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hedgg__kfy.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        hedgg__kfy = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            hedgg__kfy.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(dypsa__ojh) for dypsa__ojh in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, yxv__jpn, rckjt__lbgej = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        fzsmm__rjxpu = context.get_value_type(payload_type)
        znuma__hvt = context.get_abi_sizeof(fzsmm__rjxpu)
        apqk__kjqjt = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        rhzfx__ewsz = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, znuma__hvt), apqk__kjqjt)
        gzcm__qum = context.nrt.meminfo_data(builder, rhzfx__ewsz)
        ylafb__laav = builder.bitcast(gzcm__qum, fzsmm__rjxpu.as_pointer())
        hedgg__kfy = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        hedgg__kfy.data = data
        hedgg__kfy.null_bitmap = yxv__jpn
        builder.store(hedgg__kfy._getvalue(), ylafb__laav)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, yxv__jpn)
        weyxe__vfukm = context.make_helper(builder, struct_arr_type)
        weyxe__vfukm.meminfo = rhzfx__ewsz
        return weyxe__vfukm._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    fzi__wlx = len(arr.data)
    dzx__nupvi = 'def impl(arr, ind):\n'
    dzx__nupvi += '  data = get_data(arr)\n'
    dzx__nupvi += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        dzx__nupvi += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        dzx__nupvi += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        dzx__nupvi += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    dzx__nupvi += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(fzi__wlx)), ', '.join("'{}'".format(kdkci__fzi) for
        kdkci__fzi in arr.names)))
    smuo__zuy = {}
    exec(dzx__nupvi, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, smuo__zuy)
    impl = smuo__zuy['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        fzi__wlx = len(arr.data)
        dzx__nupvi = 'def impl(arr, ind, val):\n'
        dzx__nupvi += '  data = get_data(arr)\n'
        dzx__nupvi += '  null_bitmap = get_null_bitmap(arr)\n'
        dzx__nupvi += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(fzi__wlx):
            if isinstance(val, StructType):
                dzx__nupvi += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                dzx__nupvi += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                dzx__nupvi += '  else:\n'
                dzx__nupvi += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                dzx__nupvi += "  data[{}][ind] = val['{}']\n".format(i, arr
                    .names[i])
        smuo__zuy = {}
        exec(dzx__nupvi, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, smuo__zuy)
        impl = smuo__zuy['impl']
        return impl
    if isinstance(ind, types.SliceType):
        fzi__wlx = len(arr.data)
        dzx__nupvi = 'def impl(arr, ind, val):\n'
        dzx__nupvi += '  data = get_data(arr)\n'
        dzx__nupvi += '  null_bitmap = get_null_bitmap(arr)\n'
        dzx__nupvi += '  val_data = get_data(val)\n'
        dzx__nupvi += '  val_null_bitmap = get_null_bitmap(val)\n'
        dzx__nupvi += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(fzi__wlx):
            dzx__nupvi += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        smuo__zuy = {}
        exec(dzx__nupvi, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, smuo__zuy)
        impl = smuo__zuy['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    dzx__nupvi = 'def impl(A):\n'
    dzx__nupvi += '  total_nbytes = 0\n'
    dzx__nupvi += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        dzx__nupvi += f'  total_nbytes += data[{i}].nbytes\n'
    dzx__nupvi += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    dzx__nupvi += '  return total_nbytes\n'
    smuo__zuy = {}
    exec(dzx__nupvi, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, smuo__zuy)
    impl = smuo__zuy['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        yxv__jpn = get_null_bitmap(A)
        tiy__jdz = bodo.ir.join.copy_arr_tup(data)
        umz__weycy = yxv__jpn.copy()
        return init_struct_arr(tiy__jdz, umz__weycy, names)
    return copy_impl
