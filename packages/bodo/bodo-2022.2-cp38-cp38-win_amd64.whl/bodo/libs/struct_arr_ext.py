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
            .utils.is_array_typ(jfod__lgit, False) for jfod__lgit in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(jfod__lgit,
                str) for jfod__lgit in names) and len(names) == len(data)
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
        return StructType(tuple(pdiiv__uhs.dtype for pdiiv__uhs in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(jfod__lgit) for jfod__lgit in d.keys())
        data = tuple(dtype_to_array_type(pdiiv__uhs) for pdiiv__uhs in d.
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
            is_array_typ(jfod__lgit, False) for jfod__lgit in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        feto__gxc = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, feto__gxc)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        feto__gxc = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, feto__gxc)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ojojp__nbsc = builder.module
    dhvf__kgoo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gcat__dysd = cgutils.get_or_insert_function(ojojp__nbsc, dhvf__kgoo,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not gcat__dysd.is_declaration:
        return gcat__dysd
    gcat__dysd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gcat__dysd.append_basic_block())
    xdy__tnka = gcat__dysd.args[0]
    xdsyo__xzr = context.get_value_type(payload_type).as_pointer()
    zevpe__aez = builder.bitcast(xdy__tnka, xdsyo__xzr)
    lmoen__xidx = context.make_helper(builder, payload_type, ref=zevpe__aez)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), lmoen__xidx.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        lmoen__xidx.null_bitmap)
    builder.ret_void()
    return gcat__dysd


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    kxi__yua = context.get_value_type(payload_type)
    etf__ycl = context.get_abi_sizeof(kxi__yua)
    zuccu__dcfyn = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    qixzq__srjf = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, etf__ycl), zuccu__dcfyn)
    lrbta__iju = context.nrt.meminfo_data(builder, qixzq__srjf)
    kcid__ojmr = builder.bitcast(lrbta__iju, kxi__yua.as_pointer())
    lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context, builder)
    wbfhp__qbms = []
    wwcy__ycpxa = 0
    for arr_typ in struct_arr_type.data:
        jzcgc__pcx = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        bab__usjaq = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(wwcy__ycpxa, 
            wwcy__ycpxa + jzcgc__pcx)])
        arr = gen_allocate_array(context, builder, arr_typ, bab__usjaq, c)
        wbfhp__qbms.append(arr)
        wwcy__ycpxa += jzcgc__pcx
    lmoen__xidx.data = cgutils.pack_array(builder, wbfhp__qbms
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, wbfhp__qbms)
    pbf__sgus = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    zpg__monc = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [pbf__sgus])
    null_bitmap_ptr = zpg__monc.data
    lmoen__xidx.null_bitmap = zpg__monc._getvalue()
    builder.store(lmoen__xidx._getvalue(), kcid__ojmr)
    return qixzq__srjf, lmoen__xidx.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    qmgw__vyd = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        ohsah__umbj = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            ohsah__umbj)
        qmgw__vyd.append(arr.data)
    fqb__dsmrc = cgutils.pack_array(c.builder, qmgw__vyd
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, qmgw__vyd)
    dzn__yxvt = cgutils.alloca_once_value(c.builder, fqb__dsmrc)
    zrxu__qhc = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(jfod__lgit.dtype)) for jfod__lgit in data_typ]
    irvx__petmh = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, zrxu__qhc))
    khygl__avocc = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, jfod__lgit) for jfod__lgit in
        names])
    emwwv__kac = cgutils.alloca_once_value(c.builder, khygl__avocc)
    return dzn__yxvt, irvx__petmh, emwwv__kac


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    gqpv__qzuqk = all(isinstance(pdiiv__uhs, types.Array) and pdiiv__uhs.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for pdiiv__uhs in typ.data)
    if gqpv__qzuqk:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        yjgjn__ber = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            yjgjn__ber, i) for i in range(1, yjgjn__ber.type.count)], lir.
            IntType(64))
    qixzq__srjf, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if gqpv__qzuqk:
        dzn__yxvt, irvx__petmh, emwwv__kac = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        dhvf__kgoo = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        gcat__dysd = cgutils.get_or_insert_function(c.builder.module,
            dhvf__kgoo, name='struct_array_from_sequence')
        c.builder.call(gcat__dysd, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(dzn__yxvt, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(irvx__petmh,
            lir.IntType(8).as_pointer()), c.builder.bitcast(emwwv__kac, lir
            .IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    stmwh__ultgk = c.context.make_helper(c.builder, typ)
    stmwh__ultgk.meminfo = qixzq__srjf
    oswhm__hqog = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(stmwh__ultgk._getvalue(), is_error=oswhm__hqog)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ybk__tviz = context.insert_const_string(builder.module, 'pandas')
    xey__cqns = c.pyapi.import_module_noblock(ybk__tviz)
    iyz__toang = c.pyapi.object_getattr_string(xey__cqns, 'NA')
    with cgutils.for_range(builder, n_structs) as loop:
        skg__ajdd = loop.index
        ashf__cquf = seq_getitem(builder, context, val, skg__ajdd)
        set_bitmap_bit(builder, null_bitmap_ptr, skg__ajdd, 0)
        for derlf__tpwcs in range(len(typ.data)):
            arr_typ = typ.data[derlf__tpwcs]
            data_arr = builder.extract_value(data_tup, derlf__tpwcs)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            wmq__hnb, ozxo__vqycx = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, skg__ajdd])
        pfk__rpa = is_na_value(builder, context, ashf__cquf, iyz__toang)
        flpzm__luuzp = builder.icmp_unsigned('!=', pfk__rpa, lir.Constant(
            pfk__rpa.type, 1))
        with builder.if_then(flpzm__luuzp):
            set_bitmap_bit(builder, null_bitmap_ptr, skg__ajdd, 1)
            for derlf__tpwcs in range(len(typ.data)):
                arr_typ = typ.data[derlf__tpwcs]
                if is_tuple_array:
                    uhc__iigq = c.pyapi.tuple_getitem(ashf__cquf, derlf__tpwcs)
                else:
                    uhc__iigq = c.pyapi.dict_getitem_string(ashf__cquf, typ
                        .names[derlf__tpwcs])
                pfk__rpa = is_na_value(builder, context, uhc__iigq, iyz__toang)
                flpzm__luuzp = builder.icmp_unsigned('!=', pfk__rpa, lir.
                    Constant(pfk__rpa.type, 1))
                with builder.if_then(flpzm__luuzp):
                    uhc__iigq = to_arr_obj_if_list_obj(c, context, builder,
                        uhc__iigq, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        uhc__iigq).value
                    data_arr = builder.extract_value(data_tup, derlf__tpwcs)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    wmq__hnb, ozxo__vqycx = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, skg__ajdd, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(ashf__cquf)
    c.pyapi.decref(xey__cqns)
    c.pyapi.decref(iyz__toang)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    stmwh__ultgk = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    lrbta__iju = context.nrt.meminfo_data(builder, stmwh__ultgk.meminfo)
    kcid__ojmr = builder.bitcast(lrbta__iju, context.get_value_type(
        payload_type).as_pointer())
    lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(kcid__ojmr))
    return lmoen__xidx


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    lmoen__xidx = _get_struct_arr_payload(c.context, c.builder, typ, val)
    wmq__hnb, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64(
        typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), lmoen__xidx.null_bitmap).data
    gqpv__qzuqk = all(isinstance(pdiiv__uhs, types.Array) and pdiiv__uhs.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for pdiiv__uhs in typ.data)
    if gqpv__qzuqk:
        dzn__yxvt, irvx__petmh, emwwv__kac = _get_C_API_ptrs(c, lmoen__xidx
            .data, typ.data, typ.names)
        dhvf__kgoo = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        ixbe__xnf = cgutils.get_or_insert_function(c.builder.module,
            dhvf__kgoo, name='np_array_from_struct_array')
        arr = c.builder.call(ixbe__xnf, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(dzn__yxvt, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            irvx__petmh, lir.IntType(8).as_pointer()), c.builder.bitcast(
            emwwv__kac, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, lmoen__xidx.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ybk__tviz = context.insert_const_string(builder.module, 'numpy')
    hnq__umuem = c.pyapi.import_module_noblock(ybk__tviz)
    osns__wazpb = c.pyapi.object_getattr_string(hnq__umuem, 'object_')
    oytnu__qgpd = c.pyapi.long_from_longlong(length)
    nja__juoxv = c.pyapi.call_method(hnq__umuem, 'ndarray', (oytnu__qgpd,
        osns__wazpb))
    ces__yanb = c.pyapi.object_getattr_string(hnq__umuem, 'nan')
    with cgutils.for_range(builder, length) as loop:
        skg__ajdd = loop.index
        pyarray_setitem(builder, context, nja__juoxv, skg__ajdd, ces__yanb)
        lkq__othw = get_bitmap_bit(builder, null_bitmap_ptr, skg__ajdd)
        mrul__yhos = builder.icmp_unsigned('!=', lkq__othw, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(mrul__yhos):
            if is_tuple_array:
                ashf__cquf = c.pyapi.tuple_new(len(typ.data))
            else:
                ashf__cquf = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(ces__yanb)
                    c.pyapi.tuple_setitem(ashf__cquf, i, ces__yanb)
                else:
                    c.pyapi.dict_setitem_string(ashf__cquf, typ.names[i],
                        ces__yanb)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                wmq__hnb, mzvh__kto = c.pyapi.call_jit_code(lambda data_arr,
                    ind: not bodo.libs.array_kernels.isna(data_arr, ind),
                    types.bool_(arr_typ, types.int64), [data_arr, skg__ajdd])
                with builder.if_then(mzvh__kto):
                    wmq__hnb, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, skg__ajdd])
                    gaj__gcg = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(ashf__cquf, i, gaj__gcg)
                    else:
                        c.pyapi.dict_setitem_string(ashf__cquf, typ.names[i
                            ], gaj__gcg)
                        c.pyapi.decref(gaj__gcg)
            pyarray_setitem(builder, context, nja__juoxv, skg__ajdd, ashf__cquf
                )
            c.pyapi.decref(ashf__cquf)
    c.pyapi.decref(hnq__umuem)
    c.pyapi.decref(osns__wazpb)
    c.pyapi.decref(oytnu__qgpd)
    c.pyapi.decref(ces__yanb)
    return nja__juoxv


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    whv__zdyl = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if whv__zdyl == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for amciw__whsyg in range(whv__zdyl)])
    elif nested_counts_type.count < whv__zdyl:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for amciw__whsyg in range(
            whv__zdyl - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(pdiiv__uhs) for pdiiv__uhs in
            names_typ.types)
    tryt__dub = tuple(pdiiv__uhs.instance_type for pdiiv__uhs in dtypes_typ
        .types)
    struct_arr_type = StructArrayType(tryt__dub, names)

    def codegen(context, builder, sig, args):
        ekmmc__nqvr, nested_counts, amciw__whsyg, amciw__whsyg = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        qixzq__srjf, amciw__whsyg, amciw__whsyg = construct_struct_array(
            context, builder, struct_arr_type, ekmmc__nqvr, nested_counts)
        stmwh__ultgk = context.make_helper(builder, struct_arr_type)
        stmwh__ultgk.meminfo = qixzq__srjf
        return stmwh__ultgk._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(jfod__lgit, str) for
            jfod__lgit in names) and len(names) == len(data)
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
        feto__gxc = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, feto__gxc)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        feto__gxc = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, feto__gxc)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ojojp__nbsc = builder.module
    dhvf__kgoo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gcat__dysd = cgutils.get_or_insert_function(ojojp__nbsc, dhvf__kgoo,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not gcat__dysd.is_declaration:
        return gcat__dysd
    gcat__dysd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gcat__dysd.append_basic_block())
    xdy__tnka = gcat__dysd.args[0]
    xdsyo__xzr = context.get_value_type(payload_type).as_pointer()
    zevpe__aez = builder.bitcast(xdy__tnka, xdsyo__xzr)
    lmoen__xidx = context.make_helper(builder, payload_type, ref=zevpe__aez)
    for i in range(len(struct_type.data)):
        dcv__hifb = builder.extract_value(lmoen__xidx.null_bitmap, i)
        mrul__yhos = builder.icmp_unsigned('==', dcv__hifb, lir.Constant(
            dcv__hifb.type, 1))
        with builder.if_then(mrul__yhos):
            val = builder.extract_value(lmoen__xidx.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return gcat__dysd


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    lrbta__iju = context.nrt.meminfo_data(builder, struct.meminfo)
    kcid__ojmr = builder.bitcast(lrbta__iju, context.get_value_type(
        payload_type).as_pointer())
    lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(kcid__ojmr))
    return lmoen__xidx, kcid__ojmr


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    ybk__tviz = context.insert_const_string(builder.module, 'pandas')
    xey__cqns = c.pyapi.import_module_noblock(ybk__tviz)
    iyz__toang = c.pyapi.object_getattr_string(xey__cqns, 'NA')
    rupi__efmsi = []
    nulls = []
    for i, pdiiv__uhs in enumerate(typ.data):
        gaj__gcg = c.pyapi.dict_getitem_string(val, typ.names[i])
        fmp__ypdc = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        rhe__scvp = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(pdiiv__uhs)))
        pfk__rpa = is_na_value(builder, context, gaj__gcg, iyz__toang)
        mrul__yhos = builder.icmp_unsigned('!=', pfk__rpa, lir.Constant(
            pfk__rpa.type, 1))
        with builder.if_then(mrul__yhos):
            builder.store(context.get_constant(types.uint8, 1), fmp__ypdc)
            field_val = c.pyapi.to_native_value(pdiiv__uhs, gaj__gcg).value
            builder.store(field_val, rhe__scvp)
        rupi__efmsi.append(builder.load(rhe__scvp))
        nulls.append(builder.load(fmp__ypdc))
    c.pyapi.decref(xey__cqns)
    c.pyapi.decref(iyz__toang)
    qixzq__srjf = construct_struct(context, builder, typ, rupi__efmsi, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = qixzq__srjf
    oswhm__hqog = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=oswhm__hqog)


@box(StructType)
def box_struct(typ, val, c):
    qiu__too = c.pyapi.dict_new(len(typ.data))
    lmoen__xidx, amciw__whsyg = _get_struct_payload(c.context, c.builder,
        typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(qiu__too, typ.names[i], c.pyapi.
            borrow_none())
        dcv__hifb = c.builder.extract_value(lmoen__xidx.null_bitmap, i)
        mrul__yhos = c.builder.icmp_unsigned('==', dcv__hifb, lir.Constant(
            dcv__hifb.type, 1))
        with c.builder.if_then(mrul__yhos):
            xgs__ipn = c.builder.extract_value(lmoen__xidx.data, i)
            c.context.nrt.incref(c.builder, val_typ, xgs__ipn)
            uhc__iigq = c.pyapi.from_native_value(val_typ, xgs__ipn, c.
                env_manager)
            c.pyapi.dict_setitem_string(qiu__too, typ.names[i], uhc__iigq)
            c.pyapi.decref(uhc__iigq)
    c.context.nrt.decref(c.builder, typ, val)
    return qiu__too


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(pdiiv__uhs) for pdiiv__uhs in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, rgjya__vvlwi = args
        payload_type = StructPayloadType(struct_type.data)
        kxi__yua = context.get_value_type(payload_type)
        etf__ycl = context.get_abi_sizeof(kxi__yua)
        zuccu__dcfyn = define_struct_dtor(context, builder, struct_type,
            payload_type)
        qixzq__srjf = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, etf__ycl), zuccu__dcfyn)
        lrbta__iju = context.nrt.meminfo_data(builder, qixzq__srjf)
        kcid__ojmr = builder.bitcast(lrbta__iju, kxi__yua.as_pointer())
        lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        lmoen__xidx.data = data
        lmoen__xidx.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for amciw__whsyg in range(len(
            data_typ.types))])
        builder.store(lmoen__xidx._getvalue(), kcid__ojmr)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = qixzq__srjf
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        lmoen__xidx, amciw__whsyg = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            lmoen__xidx.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        lmoen__xidx, amciw__whsyg = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            lmoen__xidx.null_bitmap)
    yfhr__gnlx = types.UniTuple(types.int8, len(struct_typ.data))
    return yfhr__gnlx(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, amciw__whsyg, val = args
        lmoen__xidx, kcid__ojmr = _get_struct_payload(context, builder,
            struct_typ, struct)
        yfvot__bbjhc = lmoen__xidx.data
        gua__tbwbg = builder.insert_value(yfvot__bbjhc, val, field_ind)
        fyse__egv = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, fyse__egv, yfvot__bbjhc)
        context.nrt.incref(builder, fyse__egv, gua__tbwbg)
        lmoen__xidx.data = gua__tbwbg
        builder.store(lmoen__xidx._getvalue(), kcid__ojmr)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    eppt__ngp = get_overload_const_str(ind)
    if eppt__ngp not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            eppt__ngp, struct))
    return struct.names.index(eppt__ngp)


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
    kxi__yua = context.get_value_type(payload_type)
    etf__ycl = context.get_abi_sizeof(kxi__yua)
    zuccu__dcfyn = define_struct_dtor(context, builder, struct_type,
        payload_type)
    qixzq__srjf = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, etf__ycl), zuccu__dcfyn)
    lrbta__iju = context.nrt.meminfo_data(builder, qixzq__srjf)
    kcid__ojmr = builder.bitcast(lrbta__iju, kxi__yua.as_pointer())
    lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context, builder)
    lmoen__xidx.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    lmoen__xidx.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(lmoen__xidx._getvalue(), kcid__ojmr)
    return qixzq__srjf


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    uvdla__gnaki = tuple(d.dtype for d in struct_arr_typ.data)
    rop__cws = StructType(uvdla__gnaki, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        kor__oczej, ind = args
        lmoen__xidx = _get_struct_arr_payload(context, builder,
            struct_arr_typ, kor__oczej)
        rupi__efmsi = []
        aqn__rwi = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            ohsah__umbj = builder.extract_value(lmoen__xidx.data, i)
            drw__ufbbb = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                ohsah__umbj, ind])
            aqn__rwi.append(drw__ufbbb)
            qpqwu__hrk = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            mrul__yhos = builder.icmp_unsigned('==', drw__ufbbb, lir.
                Constant(drw__ufbbb.type, 1))
            with builder.if_then(mrul__yhos):
                eed__hndz = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    ohsah__umbj, ind])
                builder.store(eed__hndz, qpqwu__hrk)
            rupi__efmsi.append(builder.load(qpqwu__hrk))
        if isinstance(rop__cws, types.DictType):
            ppbhg__ykf = [context.insert_const_string(builder.module,
                ecaw__fzfw) for ecaw__fzfw in struct_arr_typ.names]
            arqu__ros = cgutils.pack_array(builder, rupi__efmsi)
            abkr__tktz = cgutils.pack_array(builder, ppbhg__ykf)

            def impl(names, vals):
                d = {}
                for i, ecaw__fzfw in enumerate(names):
                    d[ecaw__fzfw] = vals[i]
                return d
            yxk__sas = context.compile_internal(builder, impl, rop__cws(
                types.Tuple(tuple(types.StringLiteral(ecaw__fzfw) for
                ecaw__fzfw in struct_arr_typ.names)), types.Tuple(
                uvdla__gnaki)), [abkr__tktz, arqu__ros])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                uvdla__gnaki), arqu__ros)
            return yxk__sas
        qixzq__srjf = construct_struct(context, builder, rop__cws,
            rupi__efmsi, aqn__rwi)
        struct = context.make_helper(builder, rop__cws)
        struct.meminfo = qixzq__srjf
        return struct._getvalue()
    return rop__cws(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        lmoen__xidx = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            lmoen__xidx.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        lmoen__xidx = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            lmoen__xidx.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(pdiiv__uhs) for pdiiv__uhs in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, zpg__monc, rgjya__vvlwi = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        kxi__yua = context.get_value_type(payload_type)
        etf__ycl = context.get_abi_sizeof(kxi__yua)
        zuccu__dcfyn = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        qixzq__srjf = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, etf__ycl), zuccu__dcfyn)
        lrbta__iju = context.nrt.meminfo_data(builder, qixzq__srjf)
        kcid__ojmr = builder.bitcast(lrbta__iju, kxi__yua.as_pointer())
        lmoen__xidx = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        lmoen__xidx.data = data
        lmoen__xidx.null_bitmap = zpg__monc
        builder.store(lmoen__xidx._getvalue(), kcid__ojmr)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, zpg__monc)
        stmwh__ultgk = context.make_helper(builder, struct_arr_type)
        stmwh__ultgk.meminfo = qixzq__srjf
        return stmwh__ultgk._getvalue()
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
    xff__azj = len(arr.data)
    rlxlw__zchw = 'def impl(arr, ind):\n'
    rlxlw__zchw += '  data = get_data(arr)\n'
    rlxlw__zchw += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        rlxlw__zchw += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        rlxlw__zchw += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        rlxlw__zchw += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    rlxlw__zchw += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(xff__azj)), ', '.join("'{}'".format(ecaw__fzfw) for
        ecaw__fzfw in arr.names)))
    odv__nfoki = {}
    exec(rlxlw__zchw, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, odv__nfoki)
    impl = odv__nfoki['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        xff__azj = len(arr.data)
        rlxlw__zchw = 'def impl(arr, ind, val):\n'
        rlxlw__zchw += '  data = get_data(arr)\n'
        rlxlw__zchw += '  null_bitmap = get_null_bitmap(arr)\n'
        rlxlw__zchw += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(xff__azj):
            if isinstance(val, StructType):
                rlxlw__zchw += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                rlxlw__zchw += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                rlxlw__zchw += '  else:\n'
                rlxlw__zchw += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                rlxlw__zchw += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        odv__nfoki = {}
        exec(rlxlw__zchw, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, odv__nfoki)
        impl = odv__nfoki['impl']
        return impl
    if isinstance(ind, types.SliceType):
        xff__azj = len(arr.data)
        rlxlw__zchw = 'def impl(arr, ind, val):\n'
        rlxlw__zchw += '  data = get_data(arr)\n'
        rlxlw__zchw += '  null_bitmap = get_null_bitmap(arr)\n'
        rlxlw__zchw += '  val_data = get_data(val)\n'
        rlxlw__zchw += '  val_null_bitmap = get_null_bitmap(val)\n'
        rlxlw__zchw += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(xff__azj):
            rlxlw__zchw += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        odv__nfoki = {}
        exec(rlxlw__zchw, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, odv__nfoki)
        impl = odv__nfoki['impl']
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
    rlxlw__zchw = 'def impl(A):\n'
    rlxlw__zchw += '  total_nbytes = 0\n'
    rlxlw__zchw += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        rlxlw__zchw += f'  total_nbytes += data[{i}].nbytes\n'
    rlxlw__zchw += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    rlxlw__zchw += '  return total_nbytes\n'
    odv__nfoki = {}
    exec(rlxlw__zchw, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, odv__nfoki)
    impl = odv__nfoki['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        zpg__monc = get_null_bitmap(A)
        uuvq__aijpt = bodo.ir.join.copy_arr_tup(data)
        qnlxk__jrbx = zpg__monc.copy()
        return init_struct_arr(uuvq__aijpt, qnlxk__jrbx, names)
    return copy_impl
