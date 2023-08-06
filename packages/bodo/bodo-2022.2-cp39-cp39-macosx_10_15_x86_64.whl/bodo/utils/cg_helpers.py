"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    vhz__kxddc = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ggew__vtijl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    qzzd__xhy = builder.gep(null_bitmap_ptr, [vhz__kxddc], inbounds=True)
    hosyw__mctcv = builder.load(qzzd__xhy)
    oalz__hot = lir.ArrayType(lir.IntType(8), 8)
    opdan__paffq = cgutils.alloca_once_value(builder, lir.Constant(
        oalz__hot, (1, 2, 4, 8, 16, 32, 64, 128)))
    stwqj__ekdwh = builder.load(builder.gep(opdan__paffq, [lir.Constant(lir
        .IntType(64), 0), ggew__vtijl], inbounds=True))
    if val:
        builder.store(builder.or_(hosyw__mctcv, stwqj__ekdwh), qzzd__xhy)
    else:
        stwqj__ekdwh = builder.xor(stwqj__ekdwh, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(hosyw__mctcv, stwqj__ekdwh), qzzd__xhy)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    vhz__kxddc = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ggew__vtijl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    hosyw__mctcv = builder.load(builder.gep(null_bitmap_ptr, [vhz__kxddc],
        inbounds=True))
    oalz__hot = lir.ArrayType(lir.IntType(8), 8)
    opdan__paffq = cgutils.alloca_once_value(builder, lir.Constant(
        oalz__hot, (1, 2, 4, 8, 16, 32, 64, 128)))
    stwqj__ekdwh = builder.load(builder.gep(opdan__paffq, [lir.Constant(lir
        .IntType(64), 0), ggew__vtijl], inbounds=True))
    return builder.and_(hosyw__mctcv, stwqj__ekdwh)


def pyarray_getitem(builder, context, arr_obj, ind):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    pkmuu__yve = context.get_value_type(types.intp)
    aqw__ldw = lir.FunctionType(lir.IntType(8).as_pointer(), [nhc__skiqc,
        pkmuu__yve])
    hbdy__tnah = cgutils.get_or_insert_function(builder.module, aqw__ldw,
        name='array_getptr1')
    vncs__qcfkd = lir.FunctionType(nhc__skiqc, [nhc__skiqc, lir.IntType(8).
        as_pointer()])
    vrac__yfazc = cgutils.get_or_insert_function(builder.module,
        vncs__qcfkd, name='array_getitem')
    devq__hvyul = builder.call(hbdy__tnah, [arr_obj, ind])
    return builder.call(vrac__yfazc, [arr_obj, devq__hvyul])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    pkmuu__yve = context.get_value_type(types.intp)
    aqw__ldw = lir.FunctionType(lir.IntType(8).as_pointer(), [nhc__skiqc,
        pkmuu__yve])
    hbdy__tnah = cgutils.get_or_insert_function(builder.module, aqw__ldw,
        name='array_getptr1')
    nnec__fnsx = lir.FunctionType(lir.VoidType(), [nhc__skiqc, lir.IntType(
        8).as_pointer(), nhc__skiqc])
    oftp__ztwzg = cgutils.get_or_insert_function(builder.module, nnec__fnsx,
        name='array_setitem')
    devq__hvyul = builder.call(hbdy__tnah, [arr_obj, ind])
    builder.call(oftp__ztwzg, [arr_obj, devq__hvyul, val_obj])


def seq_getitem(builder, context, obj, ind):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    pkmuu__yve = context.get_value_type(types.intp)
    ica__gwmoa = lir.FunctionType(nhc__skiqc, [nhc__skiqc, pkmuu__yve])
    qeto__dzfu = cgutils.get_or_insert_function(builder.module, ica__gwmoa,
        name='seq_getitem')
    return builder.call(qeto__dzfu, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    wldeu__adq = lir.FunctionType(lir.IntType(32), [nhc__skiqc, nhc__skiqc])
    krib__eke = cgutils.get_or_insert_function(builder.module, wldeu__adq,
        name='is_na_value')
    return builder.call(krib__eke, [val, C_NA])


def list_check(builder, context, obj):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    iad__rjmvw = context.get_value_type(types.int32)
    rwy__mrcr = lir.FunctionType(iad__rjmvw, [nhc__skiqc])
    mwf__ottn = cgutils.get_or_insert_function(builder.module, rwy__mrcr,
        name='list_check')
    return builder.call(mwf__ottn, [obj])


def dict_keys(builder, context, obj):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    rwy__mrcr = lir.FunctionType(nhc__skiqc, [nhc__skiqc])
    mwf__ottn = cgutils.get_or_insert_function(builder.module, rwy__mrcr,
        name='dict_keys')
    return builder.call(mwf__ottn, [obj])


def dict_values(builder, context, obj):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    rwy__mrcr = lir.FunctionType(nhc__skiqc, [nhc__skiqc])
    mwf__ottn = cgutils.get_or_insert_function(builder.module, rwy__mrcr,
        name='dict_values')
    return builder.call(mwf__ottn, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    nhc__skiqc = context.get_argument_type(types.pyobject)
    rwy__mrcr = lir.FunctionType(lir.VoidType(), [nhc__skiqc, nhc__skiqc])
    mwf__ottn = cgutils.get_or_insert_function(builder.module, rwy__mrcr,
        name='dict_merge_from_seq2')
    builder.call(mwf__ottn, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    izzd__ogzk = cgutils.alloca_once_value(builder, val)
    fcibv__ouisw = list_check(builder, context, val)
    moo__nteke = builder.icmp_unsigned('!=', fcibv__ouisw, lir.Constant(
        fcibv__ouisw.type, 0))
    with builder.if_then(moo__nteke):
        xgoyo__aiyg = context.insert_const_string(builder.module, 'numpy')
        wgnc__qrf = c.pyapi.import_module_noblock(xgoyo__aiyg)
        bxuip__sgfh = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            bxuip__sgfh = str(typ.dtype)
        cyf__wjn = c.pyapi.object_getattr_string(wgnc__qrf, bxuip__sgfh)
        ubpu__qnjut = builder.load(izzd__ogzk)
        quh__ndo = c.pyapi.call_method(wgnc__qrf, 'asarray', (ubpu__qnjut,
            cyf__wjn))
        builder.store(quh__ndo, izzd__ogzk)
        c.pyapi.decref(wgnc__qrf)
        c.pyapi.decref(cyf__wjn)
    val = builder.load(izzd__ogzk)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        wtrbm__nlo = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        latxv__qqoji, qcnqm__jto = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [wtrbm__nlo])
        context.nrt.decref(builder, typ, wtrbm__nlo)
        return cgutils.pack_array(builder, [qcnqm__jto])
    if isinstance(typ, (StructType, types.BaseTuple)):
        xgoyo__aiyg = context.insert_const_string(builder.module, 'pandas')
        rqypz__dzajl = c.pyapi.import_module_noblock(xgoyo__aiyg)
        C_NA = c.pyapi.object_getattr_string(rqypz__dzajl, 'NA')
        mcfg__wycjl = bodo.utils.transform.get_type_alloc_counts(typ)
        vfot__rhq = context.make_tuple(builder, types.Tuple(mcfg__wycjl * [
            types.int64]), mcfg__wycjl * [context.get_constant(types.int64, 0)]
            )
        ehuk__zaj = cgutils.alloca_once_value(builder, vfot__rhq)
        ymbqp__blsu = 0
        mxhvp__dnt = typ.data if isinstance(typ, StructType) else typ.types
        for ghzel__dfyg, t in enumerate(mxhvp__dnt):
            rrgas__yzoi = bodo.utils.transform.get_type_alloc_counts(t)
            if rrgas__yzoi == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    ghzel__dfyg])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, ghzel__dfyg)
            bqj__hwp = is_na_value(builder, context, val_obj, C_NA)
            cehw__vlga = builder.icmp_unsigned('!=', bqj__hwp, lir.Constant
                (bqj__hwp.type, 1))
            with builder.if_then(cehw__vlga):
                vfot__rhq = builder.load(ehuk__zaj)
                zngye__jwra = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for ghzel__dfyg in range(rrgas__yzoi):
                    wgdpk__tqoz = builder.extract_value(vfot__rhq, 
                        ymbqp__blsu + ghzel__dfyg)
                    wfkb__rqh = builder.extract_value(zngye__jwra, ghzel__dfyg)
                    vfot__rhq = builder.insert_value(vfot__rhq, builder.add
                        (wgdpk__tqoz, wfkb__rqh), ymbqp__blsu + ghzel__dfyg)
                builder.store(vfot__rhq, ehuk__zaj)
            ymbqp__blsu += rrgas__yzoi
        c.pyapi.decref(rqypz__dzajl)
        c.pyapi.decref(C_NA)
        return builder.load(ehuk__zaj)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    xgoyo__aiyg = context.insert_const_string(builder.module, 'pandas')
    rqypz__dzajl = c.pyapi.import_module_noblock(xgoyo__aiyg)
    C_NA = c.pyapi.object_getattr_string(rqypz__dzajl, 'NA')
    mcfg__wycjl = bodo.utils.transform.get_type_alloc_counts(typ)
    vfot__rhq = context.make_tuple(builder, types.Tuple(mcfg__wycjl * [
        types.int64]), [n] + (mcfg__wycjl - 1) * [context.get_constant(
        types.int64, 0)])
    ehuk__zaj = cgutils.alloca_once_value(builder, vfot__rhq)
    with cgutils.for_range(builder, n) as loop:
        ppv__ojlux = loop.index
        xmea__ewgeb = seq_getitem(builder, context, arr_obj, ppv__ojlux)
        bqj__hwp = is_na_value(builder, context, xmea__ewgeb, C_NA)
        cehw__vlga = builder.icmp_unsigned('!=', bqj__hwp, lir.Constant(
            bqj__hwp.type, 1))
        with builder.if_then(cehw__vlga):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                vfot__rhq = builder.load(ehuk__zaj)
                zngye__jwra = get_array_elem_counts(c, builder, context,
                    xmea__ewgeb, typ.dtype)
                for ghzel__dfyg in range(mcfg__wycjl - 1):
                    wgdpk__tqoz = builder.extract_value(vfot__rhq, 
                        ghzel__dfyg + 1)
                    wfkb__rqh = builder.extract_value(zngye__jwra, ghzel__dfyg)
                    vfot__rhq = builder.insert_value(vfot__rhq, builder.add
                        (wgdpk__tqoz, wfkb__rqh), ghzel__dfyg + 1)
                builder.store(vfot__rhq, ehuk__zaj)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                ymbqp__blsu = 1
                for ghzel__dfyg, t in enumerate(typ.data):
                    rrgas__yzoi = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if rrgas__yzoi == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(xmea__ewgeb,
                            ghzel__dfyg)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(xmea__ewgeb,
                            typ.names[ghzel__dfyg])
                    bqj__hwp = is_na_value(builder, context, val_obj, C_NA)
                    cehw__vlga = builder.icmp_unsigned('!=', bqj__hwp, lir.
                        Constant(bqj__hwp.type, 1))
                    with builder.if_then(cehw__vlga):
                        vfot__rhq = builder.load(ehuk__zaj)
                        zngye__jwra = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for ghzel__dfyg in range(rrgas__yzoi):
                            wgdpk__tqoz = builder.extract_value(vfot__rhq, 
                                ymbqp__blsu + ghzel__dfyg)
                            wfkb__rqh = builder.extract_value(zngye__jwra,
                                ghzel__dfyg)
                            vfot__rhq = builder.insert_value(vfot__rhq,
                                builder.add(wgdpk__tqoz, wfkb__rqh), 
                                ymbqp__blsu + ghzel__dfyg)
                        builder.store(vfot__rhq, ehuk__zaj)
                    ymbqp__blsu += rrgas__yzoi
            else:
                assert isinstance(typ, MapArrayType), typ
                vfot__rhq = builder.load(ehuk__zaj)
                bdhxy__stu = dict_keys(builder, context, xmea__ewgeb)
                ypgxi__cbizn = dict_values(builder, context, xmea__ewgeb)
                gonzo__wwyw = get_array_elem_counts(c, builder, context,
                    bdhxy__stu, typ.key_arr_type)
                iaz__liza = bodo.utils.transform.get_type_alloc_counts(typ.
                    key_arr_type)
                for ghzel__dfyg in range(1, iaz__liza + 1):
                    wgdpk__tqoz = builder.extract_value(vfot__rhq, ghzel__dfyg)
                    wfkb__rqh = builder.extract_value(gonzo__wwyw, 
                        ghzel__dfyg - 1)
                    vfot__rhq = builder.insert_value(vfot__rhq, builder.add
                        (wgdpk__tqoz, wfkb__rqh), ghzel__dfyg)
                rpro__hhq = get_array_elem_counts(c, builder, context,
                    ypgxi__cbizn, typ.value_arr_type)
                for ghzel__dfyg in range(iaz__liza + 1, mcfg__wycjl):
                    wgdpk__tqoz = builder.extract_value(vfot__rhq, ghzel__dfyg)
                    wfkb__rqh = builder.extract_value(rpro__hhq, 
                        ghzel__dfyg - iaz__liza)
                    vfot__rhq = builder.insert_value(vfot__rhq, builder.add
                        (wgdpk__tqoz, wfkb__rqh), ghzel__dfyg)
                builder.store(vfot__rhq, ehuk__zaj)
                c.pyapi.decref(bdhxy__stu)
                c.pyapi.decref(ypgxi__cbizn)
        c.pyapi.decref(xmea__ewgeb)
    c.pyapi.decref(rqypz__dzajl)
    c.pyapi.decref(C_NA)
    return builder.load(ehuk__zaj)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    fbtuu__wwif = n_elems.type.count
    assert fbtuu__wwif >= 1
    ahye__qfnqz = builder.extract_value(n_elems, 0)
    if fbtuu__wwif != 1:
        izck__paoz = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, ghzel__dfyg) for ghzel__dfyg in range(1, fbtuu__wwif)])
        tjdel__tej = types.Tuple([types.int64] * (fbtuu__wwif - 1))
    else:
        izck__paoz = context.get_dummy_value()
        tjdel__tej = types.none
    xqyl__oapw = types.TypeRef(arr_type)
    dvr__jzq = arr_type(types.int64, xqyl__oapw, tjdel__tej)
    args = [ahye__qfnqz, context.get_dummy_value(), izck__paoz]
    cpod__jta = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        latxv__qqoji, ubpx__qojqb = c.pyapi.call_jit_code(cpod__jta,
            dvr__jzq, args)
    else:
        ubpx__qojqb = context.compile_internal(builder, cpod__jta, dvr__jzq,
            args)
    return ubpx__qojqb


def is_ll_eq(builder, val1, val2):
    blv__yxfpd = val1.type.pointee
    gny__xpj = val2.type.pointee
    assert blv__yxfpd == gny__xpj, 'invalid llvm value comparison'
    if isinstance(blv__yxfpd, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(blv__yxfpd.elements) if isinstance(blv__yxfpd, lir.
            BaseStructType) else blv__yxfpd.count
        grv__lhs = lir.Constant(lir.IntType(1), 1)
        for ghzel__dfyg in range(n_elems):
            iogfy__hjgrx = lir.IntType(32)(0)
            eaydj__fhx = lir.IntType(32)(ghzel__dfyg)
            xkof__vqvpg = builder.gep(val1, [iogfy__hjgrx, eaydj__fhx],
                inbounds=True)
            lbxa__oto = builder.gep(val2, [iogfy__hjgrx, eaydj__fhx],
                inbounds=True)
            grv__lhs = builder.and_(grv__lhs, is_ll_eq(builder, xkof__vqvpg,
                lbxa__oto))
        return grv__lhs
    gsg__upo = builder.load(val1)
    muidy__uat = builder.load(val2)
    if gsg__upo.type in (lir.FloatType(), lir.DoubleType()):
        icvae__orf = 32 if gsg__upo.type == lir.FloatType() else 64
        gsg__upo = builder.bitcast(gsg__upo, lir.IntType(icvae__orf))
        muidy__uat = builder.bitcast(muidy__uat, lir.IntType(icvae__orf))
    return builder.icmp_unsigned('==', gsg__upo, muidy__uat)
