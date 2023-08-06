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
            .utils.is_array_typ(sbnr__swsdw, False) for sbnr__swsdw in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(sbnr__swsdw,
                str) for sbnr__swsdw in names) and len(names) == len(data)
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
        return StructType(tuple(bigoy__arfj.dtype for bigoy__arfj in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(sbnr__swsdw) for sbnr__swsdw in d.keys())
        data = tuple(dtype_to_array_type(bigoy__arfj) for bigoy__arfj in d.
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
            is_array_typ(sbnr__swsdw, False) for sbnr__swsdw in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dga__jxliw = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, dga__jxliw)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        dga__jxliw = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, dga__jxliw)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    qmr__uie = builder.module
    qgplv__ymwp = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bqh__vjcke = cgutils.get_or_insert_function(qmr__uie, qgplv__ymwp, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not bqh__vjcke.is_declaration:
        return bqh__vjcke
    bqh__vjcke.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bqh__vjcke.append_basic_block())
    mzuca__tbral = bqh__vjcke.args[0]
    avwi__udnzj = context.get_value_type(payload_type).as_pointer()
    eqjv__xuedu = builder.bitcast(mzuca__tbral, avwi__udnzj)
    azw__dikz = context.make_helper(builder, payload_type, ref=eqjv__xuedu)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), azw__dikz.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), azw__dikz
        .null_bitmap)
    builder.ret_void()
    return bqh__vjcke


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    nvy__iluiz = context.get_value_type(payload_type)
    tkncm__qyo = context.get_abi_sizeof(nvy__iluiz)
    qgsc__gixg = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    kfw__vup = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, tkncm__qyo), qgsc__gixg)
    ahwn__kay = context.nrt.meminfo_data(builder, kfw__vup)
    xga__zrpg = builder.bitcast(ahwn__kay, nvy__iluiz.as_pointer())
    azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder)
    oyu__pame = []
    tbxy__omxv = 0
    for arr_typ in struct_arr_type.data:
        nkltu__yojyv = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype
            )
        kez__oksq = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(tbxy__omxv, tbxy__omxv +
            nkltu__yojyv)])
        arr = gen_allocate_array(context, builder, arr_typ, kez__oksq, c)
        oyu__pame.append(arr)
        tbxy__omxv += nkltu__yojyv
    azw__dikz.data = cgutils.pack_array(builder, oyu__pame
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, oyu__pame)
    ptie__jhwjv = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    stom__fjqge = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [ptie__jhwjv])
    null_bitmap_ptr = stom__fjqge.data
    azw__dikz.null_bitmap = stom__fjqge._getvalue()
    builder.store(azw__dikz._getvalue(), xga__zrpg)
    return kfw__vup, azw__dikz.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    wjn__gaxd = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        malsa__pced = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            malsa__pced)
        wjn__gaxd.append(arr.data)
    qqr__mvu = cgutils.pack_array(c.builder, wjn__gaxd
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, wjn__gaxd)
    tvkye__xcto = cgutils.alloca_once_value(c.builder, qqr__mvu)
    rma__zxc = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(sbnr__swsdw.dtype)) for sbnr__swsdw in data_typ]
    iksui__gei = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, rma__zxc))
    wskf__xbo = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, sbnr__swsdw) for sbnr__swsdw in
        names])
    nkc__txv = cgutils.alloca_once_value(c.builder, wskf__xbo)
    return tvkye__xcto, iksui__gei, nkc__txv


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    dsteu__hznlg = all(isinstance(bigoy__arfj, types.Array) and bigoy__arfj
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for bigoy__arfj in typ.data)
    if dsteu__hznlg:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        jibp__aigs = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            jibp__aigs, i) for i in range(1, jibp__aigs.type.count)], lir.
            IntType(64))
    kfw__vup, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if dsteu__hznlg:
        tvkye__xcto, iksui__gei, nkc__txv = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        qgplv__ymwp = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        bqh__vjcke = cgutils.get_or_insert_function(c.builder.module,
            qgplv__ymwp, name='struct_array_from_sequence')
        c.builder.call(bqh__vjcke, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(tvkye__xcto, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(iksui__gei,
            lir.IntType(8).as_pointer()), c.builder.bitcast(nkc__txv, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    gbhc__owvmm = c.context.make_helper(c.builder, typ)
    gbhc__owvmm.meminfo = kfw__vup
    ctuy__aoxm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gbhc__owvmm._getvalue(), is_error=ctuy__aoxm)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    tiwa__qgndo = context.insert_const_string(builder.module, 'pandas')
    mxxh__vmwq = c.pyapi.import_module_noblock(tiwa__qgndo)
    pdf__lskl = c.pyapi.object_getattr_string(mxxh__vmwq, 'NA')
    with cgutils.for_range(builder, n_structs) as loop:
        rsyml__zifhk = loop.index
        vautf__abotc = seq_getitem(builder, context, val, rsyml__zifhk)
        set_bitmap_bit(builder, null_bitmap_ptr, rsyml__zifhk, 0)
        for tegei__jvd in range(len(typ.data)):
            arr_typ = typ.data[tegei__jvd]
            data_arr = builder.extract_value(data_tup, tegei__jvd)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            mslyo__dan, cayz__vvxtg = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, rsyml__zifhk])
        mok__jbol = is_na_value(builder, context, vautf__abotc, pdf__lskl)
        pzg__eaf = builder.icmp_unsigned('!=', mok__jbol, lir.Constant(
            mok__jbol.type, 1))
        with builder.if_then(pzg__eaf):
            set_bitmap_bit(builder, null_bitmap_ptr, rsyml__zifhk, 1)
            for tegei__jvd in range(len(typ.data)):
                arr_typ = typ.data[tegei__jvd]
                if is_tuple_array:
                    jkzcv__eac = c.pyapi.tuple_getitem(vautf__abotc, tegei__jvd
                        )
                else:
                    jkzcv__eac = c.pyapi.dict_getitem_string(vautf__abotc,
                        typ.names[tegei__jvd])
                mok__jbol = is_na_value(builder, context, jkzcv__eac, pdf__lskl
                    )
                pzg__eaf = builder.icmp_unsigned('!=', mok__jbol, lir.
                    Constant(mok__jbol.type, 1))
                with builder.if_then(pzg__eaf):
                    jkzcv__eac = to_arr_obj_if_list_obj(c, context, builder,
                        jkzcv__eac, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        jkzcv__eac).value
                    data_arr = builder.extract_value(data_tup, tegei__jvd)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    mslyo__dan, cayz__vvxtg = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, rsyml__zifhk, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(vautf__abotc)
    c.pyapi.decref(mxxh__vmwq)
    c.pyapi.decref(pdf__lskl)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    gbhc__owvmm = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    ahwn__kay = context.nrt.meminfo_data(builder, gbhc__owvmm.meminfo)
    xga__zrpg = builder.bitcast(ahwn__kay, context.get_value_type(
        payload_type).as_pointer())
    azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(xga__zrpg))
    return azw__dikz


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    azw__dikz = _get_struct_arr_payload(c.context, c.builder, typ, val)
    mslyo__dan, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), azw__dikz.null_bitmap).data
    dsteu__hznlg = all(isinstance(bigoy__arfj, types.Array) and bigoy__arfj
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for bigoy__arfj in typ.data)
    if dsteu__hznlg:
        tvkye__xcto, iksui__gei, nkc__txv = _get_C_API_ptrs(c, azw__dikz.
            data, typ.data, typ.names)
        qgplv__ymwp = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        gzuq__iffji = cgutils.get_or_insert_function(c.builder.module,
            qgplv__ymwp, name='np_array_from_struct_array')
        arr = c.builder.call(gzuq__iffji, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(tvkye__xcto, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            iksui__gei, lir.IntType(8).as_pointer()), c.builder.bitcast(
            nkc__txv, lir.IntType(8).as_pointer()), c.context.get_constant(
            types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, azw__dikz.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    tiwa__qgndo = context.insert_const_string(builder.module, 'numpy')
    jmu__vod = c.pyapi.import_module_noblock(tiwa__qgndo)
    ywnlt__wuhjo = c.pyapi.object_getattr_string(jmu__vod, 'object_')
    iqj__gizlj = c.pyapi.long_from_longlong(length)
    pkqk__zlusw = c.pyapi.call_method(jmu__vod, 'ndarray', (iqj__gizlj,
        ywnlt__wuhjo))
    azgcg__bllas = c.pyapi.object_getattr_string(jmu__vod, 'nan')
    with cgutils.for_range(builder, length) as loop:
        rsyml__zifhk = loop.index
        pyarray_setitem(builder, context, pkqk__zlusw, rsyml__zifhk,
            azgcg__bllas)
        gvh__ttjgn = get_bitmap_bit(builder, null_bitmap_ptr, rsyml__zifhk)
        mgan__fcgay = builder.icmp_unsigned('!=', gvh__ttjgn, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(mgan__fcgay):
            if is_tuple_array:
                vautf__abotc = c.pyapi.tuple_new(len(typ.data))
            else:
                vautf__abotc = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(azgcg__bllas)
                    c.pyapi.tuple_setitem(vautf__abotc, i, azgcg__bllas)
                else:
                    c.pyapi.dict_setitem_string(vautf__abotc, typ.names[i],
                        azgcg__bllas)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                mslyo__dan, oksea__rkblj = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, rsyml__zifhk])
                with builder.if_then(oksea__rkblj):
                    mslyo__dan, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, rsyml__zifhk])
                    ejjfx__izc = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(vautf__abotc, i, ejjfx__izc)
                    else:
                        c.pyapi.dict_setitem_string(vautf__abotc, typ.names
                            [i], ejjfx__izc)
                        c.pyapi.decref(ejjfx__izc)
            pyarray_setitem(builder, context, pkqk__zlusw, rsyml__zifhk,
                vautf__abotc)
            c.pyapi.decref(vautf__abotc)
    c.pyapi.decref(jmu__vod)
    c.pyapi.decref(ywnlt__wuhjo)
    c.pyapi.decref(iqj__gizlj)
    c.pyapi.decref(azgcg__bllas)
    return pkqk__zlusw


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    pseo__qis = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if pseo__qis == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for fpgpf__srjul in range(pseo__qis)])
    elif nested_counts_type.count < pseo__qis:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for fpgpf__srjul in range(
            pseo__qis - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(bigoy__arfj) for bigoy__arfj in
            names_typ.types)
    wqko__atfay = tuple(bigoy__arfj.instance_type for bigoy__arfj in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(wqko__atfay, names)

    def codegen(context, builder, sig, args):
        trei__oxgt, nested_counts, fpgpf__srjul, fpgpf__srjul = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        kfw__vup, fpgpf__srjul, fpgpf__srjul = construct_struct_array(context,
            builder, struct_arr_type, trei__oxgt, nested_counts)
        gbhc__owvmm = context.make_helper(builder, struct_arr_type)
        gbhc__owvmm.meminfo = kfw__vup
        return gbhc__owvmm._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(sbnr__swsdw, str
            ) for sbnr__swsdw in names) and len(names) == len(data)
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
        dga__jxliw = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, dga__jxliw)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        dga__jxliw = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, dga__jxliw)


def define_struct_dtor(context, builder, struct_type, payload_type):
    qmr__uie = builder.module
    qgplv__ymwp = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bqh__vjcke = cgutils.get_or_insert_function(qmr__uie, qgplv__ymwp, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not bqh__vjcke.is_declaration:
        return bqh__vjcke
    bqh__vjcke.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bqh__vjcke.append_basic_block())
    mzuca__tbral = bqh__vjcke.args[0]
    avwi__udnzj = context.get_value_type(payload_type).as_pointer()
    eqjv__xuedu = builder.bitcast(mzuca__tbral, avwi__udnzj)
    azw__dikz = context.make_helper(builder, payload_type, ref=eqjv__xuedu)
    for i in range(len(struct_type.data)):
        cyhxx__exai = builder.extract_value(azw__dikz.null_bitmap, i)
        mgan__fcgay = builder.icmp_unsigned('==', cyhxx__exai, lir.Constant
            (cyhxx__exai.type, 1))
        with builder.if_then(mgan__fcgay):
            val = builder.extract_value(azw__dikz.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return bqh__vjcke


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    ahwn__kay = context.nrt.meminfo_data(builder, struct.meminfo)
    xga__zrpg = builder.bitcast(ahwn__kay, context.get_value_type(
        payload_type).as_pointer())
    azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(xga__zrpg))
    return azw__dikz, xga__zrpg


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    tiwa__qgndo = context.insert_const_string(builder.module, 'pandas')
    mxxh__vmwq = c.pyapi.import_module_noblock(tiwa__qgndo)
    pdf__lskl = c.pyapi.object_getattr_string(mxxh__vmwq, 'NA')
    vxj__wul = []
    nulls = []
    for i, bigoy__arfj in enumerate(typ.data):
        ejjfx__izc = c.pyapi.dict_getitem_string(val, typ.names[i])
        tsqh__fiqz = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        hqco__jxfg = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(bigoy__arfj)))
        mok__jbol = is_na_value(builder, context, ejjfx__izc, pdf__lskl)
        mgan__fcgay = builder.icmp_unsigned('!=', mok__jbol, lir.Constant(
            mok__jbol.type, 1))
        with builder.if_then(mgan__fcgay):
            builder.store(context.get_constant(types.uint8, 1), tsqh__fiqz)
            field_val = c.pyapi.to_native_value(bigoy__arfj, ejjfx__izc).value
            builder.store(field_val, hqco__jxfg)
        vxj__wul.append(builder.load(hqco__jxfg))
        nulls.append(builder.load(tsqh__fiqz))
    c.pyapi.decref(mxxh__vmwq)
    c.pyapi.decref(pdf__lskl)
    kfw__vup = construct_struct(context, builder, typ, vxj__wul, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = kfw__vup
    ctuy__aoxm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=ctuy__aoxm)


@box(StructType)
def box_struct(typ, val, c):
    urrx__ajwb = c.pyapi.dict_new(len(typ.data))
    azw__dikz, fpgpf__srjul = _get_struct_payload(c.context, c.builder, typ,
        val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(urrx__ajwb, typ.names[i], c.pyapi.
            borrow_none())
        cyhxx__exai = c.builder.extract_value(azw__dikz.null_bitmap, i)
        mgan__fcgay = c.builder.icmp_unsigned('==', cyhxx__exai, lir.
            Constant(cyhxx__exai.type, 1))
        with c.builder.if_then(mgan__fcgay):
            rsm__rvemv = c.builder.extract_value(azw__dikz.data, i)
            c.context.nrt.incref(c.builder, val_typ, rsm__rvemv)
            jkzcv__eac = c.pyapi.from_native_value(val_typ, rsm__rvemv, c.
                env_manager)
            c.pyapi.dict_setitem_string(urrx__ajwb, typ.names[i], jkzcv__eac)
            c.pyapi.decref(jkzcv__eac)
    c.context.nrt.decref(c.builder, typ, val)
    return urrx__ajwb


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(bigoy__arfj) for bigoy__arfj in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, cfkre__huemt = args
        payload_type = StructPayloadType(struct_type.data)
        nvy__iluiz = context.get_value_type(payload_type)
        tkncm__qyo = context.get_abi_sizeof(nvy__iluiz)
        qgsc__gixg = define_struct_dtor(context, builder, struct_type,
            payload_type)
        kfw__vup = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tkncm__qyo), qgsc__gixg)
        ahwn__kay = context.nrt.meminfo_data(builder, kfw__vup)
        xga__zrpg = builder.bitcast(ahwn__kay, nvy__iluiz.as_pointer())
        azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder)
        azw__dikz.data = data
        azw__dikz.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for fpgpf__srjul in range(len(
            data_typ.types))])
        builder.store(azw__dikz._getvalue(), xga__zrpg)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = kfw__vup
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        azw__dikz, fpgpf__srjul = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            azw__dikz.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        azw__dikz, fpgpf__srjul = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            azw__dikz.null_bitmap)
    zqy__ace = types.UniTuple(types.int8, len(struct_typ.data))
    return zqy__ace(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, fpgpf__srjul, val = args
        azw__dikz, xga__zrpg = _get_struct_payload(context, builder,
            struct_typ, struct)
        ylwg__zxq = azw__dikz.data
        qvvqi__qyug = builder.insert_value(ylwg__zxq, val, field_ind)
        ndva__dar = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, ndva__dar, ylwg__zxq)
        context.nrt.incref(builder, ndva__dar, qvvqi__qyug)
        azw__dikz.data = qvvqi__qyug
        builder.store(azw__dikz._getvalue(), xga__zrpg)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    nqgn__qgi = get_overload_const_str(ind)
    if nqgn__qgi not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            nqgn__qgi, struct))
    return struct.names.index(nqgn__qgi)


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
    nvy__iluiz = context.get_value_type(payload_type)
    tkncm__qyo = context.get_abi_sizeof(nvy__iluiz)
    qgsc__gixg = define_struct_dtor(context, builder, struct_type, payload_type
        )
    kfw__vup = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, tkncm__qyo), qgsc__gixg)
    ahwn__kay = context.nrt.meminfo_data(builder, kfw__vup)
    xga__zrpg = builder.bitcast(ahwn__kay, nvy__iluiz.as_pointer())
    azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder)
    azw__dikz.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    azw__dikz.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(azw__dikz._getvalue(), xga__zrpg)
    return kfw__vup


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    qtgal__tgnpb = tuple(d.dtype for d in struct_arr_typ.data)
    outo__eunhm = StructType(qtgal__tgnpb, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        vmm__xejf, ind = args
        azw__dikz = _get_struct_arr_payload(context, builder,
            struct_arr_typ, vmm__xejf)
        vxj__wul = []
        gesy__zonkm = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            malsa__pced = builder.extract_value(azw__dikz.data, i)
            lsbrj__gjz = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                malsa__pced, ind])
            gesy__zonkm.append(lsbrj__gjz)
            thmxx__esrbh = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            mgan__fcgay = builder.icmp_unsigned('==', lsbrj__gjz, lir.
                Constant(lsbrj__gjz.type, 1))
            with builder.if_then(mgan__fcgay):
                xufw__tdyn = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    malsa__pced, ind])
                builder.store(xufw__tdyn, thmxx__esrbh)
            vxj__wul.append(builder.load(thmxx__esrbh))
        if isinstance(outo__eunhm, types.DictType):
            lvhqj__plr = [context.insert_const_string(builder.module,
                aqvv__qoijw) for aqvv__qoijw in struct_arr_typ.names]
            dyj__mastx = cgutils.pack_array(builder, vxj__wul)
            roa__vhoqk = cgutils.pack_array(builder, lvhqj__plr)

            def impl(names, vals):
                d = {}
                for i, aqvv__qoijw in enumerate(names):
                    d[aqvv__qoijw] = vals[i]
                return d
            dtva__hirx = context.compile_internal(builder, impl,
                outo__eunhm(types.Tuple(tuple(types.StringLiteral(
                aqvv__qoijw) for aqvv__qoijw in struct_arr_typ.names)),
                types.Tuple(qtgal__tgnpb)), [roa__vhoqk, dyj__mastx])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                qtgal__tgnpb), dyj__mastx)
            return dtva__hirx
        kfw__vup = construct_struct(context, builder, outo__eunhm, vxj__wul,
            gesy__zonkm)
        struct = context.make_helper(builder, outo__eunhm)
        struct.meminfo = kfw__vup
        return struct._getvalue()
    return outo__eunhm(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        azw__dikz = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            azw__dikz.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        azw__dikz = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            azw__dikz.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(bigoy__arfj) for bigoy__arfj in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, stom__fjqge, cfkre__huemt = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        nvy__iluiz = context.get_value_type(payload_type)
        tkncm__qyo = context.get_abi_sizeof(nvy__iluiz)
        qgsc__gixg = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        kfw__vup = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, tkncm__qyo), qgsc__gixg)
        ahwn__kay = context.nrt.meminfo_data(builder, kfw__vup)
        xga__zrpg = builder.bitcast(ahwn__kay, nvy__iluiz.as_pointer())
        azw__dikz = cgutils.create_struct_proxy(payload_type)(context, builder)
        azw__dikz.data = data
        azw__dikz.null_bitmap = stom__fjqge
        builder.store(azw__dikz._getvalue(), xga__zrpg)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, stom__fjqge)
        gbhc__owvmm = context.make_helper(builder, struct_arr_type)
        gbhc__owvmm.meminfo = kfw__vup
        return gbhc__owvmm._getvalue()
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
    mzjuz__mur = len(arr.data)
    zzmm__jsr = 'def impl(arr, ind):\n'
    zzmm__jsr += '  data = get_data(arr)\n'
    zzmm__jsr += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        zzmm__jsr += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        zzmm__jsr += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        zzmm__jsr += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    zzmm__jsr += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(mzjuz__mur)), ', '.join("'{}'".format(aqvv__qoijw) for
        aqvv__qoijw in arr.names)))
    spect__qghoi = {}
    exec(zzmm__jsr, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, spect__qghoi)
    impl = spect__qghoi['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        mzjuz__mur = len(arr.data)
        zzmm__jsr = 'def impl(arr, ind, val):\n'
        zzmm__jsr += '  data = get_data(arr)\n'
        zzmm__jsr += '  null_bitmap = get_null_bitmap(arr)\n'
        zzmm__jsr += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(mzjuz__mur):
            if isinstance(val, StructType):
                zzmm__jsr += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                zzmm__jsr += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                zzmm__jsr += '  else:\n'
                zzmm__jsr += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                zzmm__jsr += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        spect__qghoi = {}
        exec(zzmm__jsr, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, spect__qghoi)
        impl = spect__qghoi['impl']
        return impl
    if isinstance(ind, types.SliceType):
        mzjuz__mur = len(arr.data)
        zzmm__jsr = 'def impl(arr, ind, val):\n'
        zzmm__jsr += '  data = get_data(arr)\n'
        zzmm__jsr += '  null_bitmap = get_null_bitmap(arr)\n'
        zzmm__jsr += '  val_data = get_data(val)\n'
        zzmm__jsr += '  val_null_bitmap = get_null_bitmap(val)\n'
        zzmm__jsr += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(mzjuz__mur):
            zzmm__jsr += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        spect__qghoi = {}
        exec(zzmm__jsr, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, spect__qghoi)
        impl = spect__qghoi['impl']
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
    zzmm__jsr = 'def impl(A):\n'
    zzmm__jsr += '  total_nbytes = 0\n'
    zzmm__jsr += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        zzmm__jsr += f'  total_nbytes += data[{i}].nbytes\n'
    zzmm__jsr += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    zzmm__jsr += '  return total_nbytes\n'
    spect__qghoi = {}
    exec(zzmm__jsr, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, spect__qghoi)
    impl = spect__qghoi['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        stom__fjqge = get_null_bitmap(A)
        jmbx__latd = bodo.ir.join.copy_arr_tup(data)
        toj__alyn = stom__fjqge.copy()
        return init_struct_arr(jmbx__latd, toj__alyn, names)
    return copy_impl
