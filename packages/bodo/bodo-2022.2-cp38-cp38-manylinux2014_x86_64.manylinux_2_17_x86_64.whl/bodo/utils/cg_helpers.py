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
    wlu__cawz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    tub__ansjb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    iyqw__bszz = builder.gep(null_bitmap_ptr, [wlu__cawz], inbounds=True)
    eeb__mohsy = builder.load(iyqw__bszz)
    daic__tgn = lir.ArrayType(lir.IntType(8), 8)
    qehca__pyidi = cgutils.alloca_once_value(builder, lir.Constant(
        daic__tgn, (1, 2, 4, 8, 16, 32, 64, 128)))
    dtxt__supat = builder.load(builder.gep(qehca__pyidi, [lir.Constant(lir.
        IntType(64), 0), tub__ansjb], inbounds=True))
    if val:
        builder.store(builder.or_(eeb__mohsy, dtxt__supat), iyqw__bszz)
    else:
        dtxt__supat = builder.xor(dtxt__supat, lir.Constant(lir.IntType(8), -1)
            )
        builder.store(builder.and_(eeb__mohsy, dtxt__supat), iyqw__bszz)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    wlu__cawz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    tub__ansjb = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    eeb__mohsy = builder.load(builder.gep(null_bitmap_ptr, [wlu__cawz],
        inbounds=True))
    daic__tgn = lir.ArrayType(lir.IntType(8), 8)
    qehca__pyidi = cgutils.alloca_once_value(builder, lir.Constant(
        daic__tgn, (1, 2, 4, 8, 16, 32, 64, 128)))
    dtxt__supat = builder.load(builder.gep(qehca__pyidi, [lir.Constant(lir.
        IntType(64), 0), tub__ansjb], inbounds=True))
    return builder.and_(eeb__mohsy, dtxt__supat)


def pyarray_getitem(builder, context, arr_obj, ind):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    acf__yddwt = context.get_value_type(types.intp)
    ppcas__exm = lir.FunctionType(lir.IntType(8).as_pointer(), [
        jxlcv__xpqil, acf__yddwt])
    zobza__hjx = cgutils.get_or_insert_function(builder.module, ppcas__exm,
        name='array_getptr1')
    vgo__tqvq = lir.FunctionType(jxlcv__xpqil, [jxlcv__xpqil, lir.IntType(8
        ).as_pointer()])
    patfu__zilw = cgutils.get_or_insert_function(builder.module, vgo__tqvq,
        name='array_getitem')
    bhk__ynyn = builder.call(zobza__hjx, [arr_obj, ind])
    return builder.call(patfu__zilw, [arr_obj, bhk__ynyn])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    acf__yddwt = context.get_value_type(types.intp)
    ppcas__exm = lir.FunctionType(lir.IntType(8).as_pointer(), [
        jxlcv__xpqil, acf__yddwt])
    zobza__hjx = cgutils.get_or_insert_function(builder.module, ppcas__exm,
        name='array_getptr1')
    xzv__fhq = lir.FunctionType(lir.VoidType(), [jxlcv__xpqil, lir.IntType(
        8).as_pointer(), jxlcv__xpqil])
    gsj__fiqg = cgutils.get_or_insert_function(builder.module, xzv__fhq,
        name='array_setitem')
    bhk__ynyn = builder.call(zobza__hjx, [arr_obj, ind])
    builder.call(gsj__fiqg, [arr_obj, bhk__ynyn, val_obj])


def seq_getitem(builder, context, obj, ind):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    acf__yddwt = context.get_value_type(types.intp)
    nmab__yymut = lir.FunctionType(jxlcv__xpqil, [jxlcv__xpqil, acf__yddwt])
    utnbb__kmail = cgutils.get_or_insert_function(builder.module,
        nmab__yymut, name='seq_getitem')
    return builder.call(utnbb__kmail, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    lvz__sxe = lir.FunctionType(lir.IntType(32), [jxlcv__xpqil, jxlcv__xpqil])
    ckzj__kwn = cgutils.get_or_insert_function(builder.module, lvz__sxe,
        name='is_na_value')
    return builder.call(ckzj__kwn, [val, C_NA])


def list_check(builder, context, obj):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    zhibv__ayv = context.get_value_type(types.int32)
    hvo__obpyi = lir.FunctionType(zhibv__ayv, [jxlcv__xpqil])
    sooc__lqrm = cgutils.get_or_insert_function(builder.module, hvo__obpyi,
        name='list_check')
    return builder.call(sooc__lqrm, [obj])


def dict_keys(builder, context, obj):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    hvo__obpyi = lir.FunctionType(jxlcv__xpqil, [jxlcv__xpqil])
    sooc__lqrm = cgutils.get_or_insert_function(builder.module, hvo__obpyi,
        name='dict_keys')
    return builder.call(sooc__lqrm, [obj])


def dict_values(builder, context, obj):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    hvo__obpyi = lir.FunctionType(jxlcv__xpqil, [jxlcv__xpqil])
    sooc__lqrm = cgutils.get_or_insert_function(builder.module, hvo__obpyi,
        name='dict_values')
    return builder.call(sooc__lqrm, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    jxlcv__xpqil = context.get_argument_type(types.pyobject)
    hvo__obpyi = lir.FunctionType(lir.VoidType(), [jxlcv__xpqil, jxlcv__xpqil])
    sooc__lqrm = cgutils.get_or_insert_function(builder.module, hvo__obpyi,
        name='dict_merge_from_seq2')
    builder.call(sooc__lqrm, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    waoi__wzf = cgutils.alloca_once_value(builder, val)
    rug__ordrv = list_check(builder, context, val)
    brh__vsbn = builder.icmp_unsigned('!=', rug__ordrv, lir.Constant(
        rug__ordrv.type, 0))
    with builder.if_then(brh__vsbn):
        bwp__jmiar = context.insert_const_string(builder.module, 'numpy')
        gxz__nywbm = c.pyapi.import_module_noblock(bwp__jmiar)
        lth__usd = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            lth__usd = str(typ.dtype)
        xxqxj__thli = c.pyapi.object_getattr_string(gxz__nywbm, lth__usd)
        fpqmc__kcm = builder.load(waoi__wzf)
        rhgb__cqj = c.pyapi.call_method(gxz__nywbm, 'asarray', (fpqmc__kcm,
            xxqxj__thli))
        builder.store(rhgb__cqj, waoi__wzf)
        c.pyapi.decref(gxz__nywbm)
        c.pyapi.decref(xxqxj__thli)
    val = builder.load(waoi__wzf)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        qolwb__kcy = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        nvvyv__czh, xndd__ruwz = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [qolwb__kcy])
        context.nrt.decref(builder, typ, qolwb__kcy)
        return cgutils.pack_array(builder, [xndd__ruwz])
    if isinstance(typ, (StructType, types.BaseTuple)):
        bwp__jmiar = context.insert_const_string(builder.module, 'pandas')
        mnfiw__xnh = c.pyapi.import_module_noblock(bwp__jmiar)
        C_NA = c.pyapi.object_getattr_string(mnfiw__xnh, 'NA')
        wsvsy__xcac = bodo.utils.transform.get_type_alloc_counts(typ)
        ixx__lphr = context.make_tuple(builder, types.Tuple(wsvsy__xcac * [
            types.int64]), wsvsy__xcac * [context.get_constant(types.int64, 0)]
            )
        yxbtm__kicqy = cgutils.alloca_once_value(builder, ixx__lphr)
        msdk__xusgh = 0
        eiknx__mzh = typ.data if isinstance(typ, StructType) else typ.types
        for hhmk__wdge, t in enumerate(eiknx__mzh):
            gixp__gdshc = bodo.utils.transform.get_type_alloc_counts(t)
            if gixp__gdshc == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    hhmk__wdge])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, hhmk__wdge)
            wcip__wxyey = is_na_value(builder, context, val_obj, C_NA)
            xcn__gnqk = builder.icmp_unsigned('!=', wcip__wxyey, lir.
                Constant(wcip__wxyey.type, 1))
            with builder.if_then(xcn__gnqk):
                ixx__lphr = builder.load(yxbtm__kicqy)
                igsjw__hsyeb = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for hhmk__wdge in range(gixp__gdshc):
                    qaoge__nlk = builder.extract_value(ixx__lphr, 
                        msdk__xusgh + hhmk__wdge)
                    lfn__qawac = builder.extract_value(igsjw__hsyeb, hhmk__wdge
                        )
                    ixx__lphr = builder.insert_value(ixx__lphr, builder.add
                        (qaoge__nlk, lfn__qawac), msdk__xusgh + hhmk__wdge)
                builder.store(ixx__lphr, yxbtm__kicqy)
            msdk__xusgh += gixp__gdshc
        c.pyapi.decref(mnfiw__xnh)
        c.pyapi.decref(C_NA)
        return builder.load(yxbtm__kicqy)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    bwp__jmiar = context.insert_const_string(builder.module, 'pandas')
    mnfiw__xnh = c.pyapi.import_module_noblock(bwp__jmiar)
    C_NA = c.pyapi.object_getattr_string(mnfiw__xnh, 'NA')
    wsvsy__xcac = bodo.utils.transform.get_type_alloc_counts(typ)
    ixx__lphr = context.make_tuple(builder, types.Tuple(wsvsy__xcac * [
        types.int64]), [n] + (wsvsy__xcac - 1) * [context.get_constant(
        types.int64, 0)])
    yxbtm__kicqy = cgutils.alloca_once_value(builder, ixx__lphr)
    with cgutils.for_range(builder, n) as loop:
        bso__grly = loop.index
        pfigp__rbbm = seq_getitem(builder, context, arr_obj, bso__grly)
        wcip__wxyey = is_na_value(builder, context, pfigp__rbbm, C_NA)
        xcn__gnqk = builder.icmp_unsigned('!=', wcip__wxyey, lir.Constant(
            wcip__wxyey.type, 1))
        with builder.if_then(xcn__gnqk):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                ixx__lphr = builder.load(yxbtm__kicqy)
                igsjw__hsyeb = get_array_elem_counts(c, builder, context,
                    pfigp__rbbm, typ.dtype)
                for hhmk__wdge in range(wsvsy__xcac - 1):
                    qaoge__nlk = builder.extract_value(ixx__lphr, 
                        hhmk__wdge + 1)
                    lfn__qawac = builder.extract_value(igsjw__hsyeb, hhmk__wdge
                        )
                    ixx__lphr = builder.insert_value(ixx__lphr, builder.add
                        (qaoge__nlk, lfn__qawac), hhmk__wdge + 1)
                builder.store(ixx__lphr, yxbtm__kicqy)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                msdk__xusgh = 1
                for hhmk__wdge, t in enumerate(typ.data):
                    gixp__gdshc = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if gixp__gdshc == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(pfigp__rbbm, hhmk__wdge
                            )
                    else:
                        val_obj = c.pyapi.dict_getitem_string(pfigp__rbbm,
                            typ.names[hhmk__wdge])
                    wcip__wxyey = is_na_value(builder, context, val_obj, C_NA)
                    xcn__gnqk = builder.icmp_unsigned('!=', wcip__wxyey,
                        lir.Constant(wcip__wxyey.type, 1))
                    with builder.if_then(xcn__gnqk):
                        ixx__lphr = builder.load(yxbtm__kicqy)
                        igsjw__hsyeb = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for hhmk__wdge in range(gixp__gdshc):
                            qaoge__nlk = builder.extract_value(ixx__lphr, 
                                msdk__xusgh + hhmk__wdge)
                            lfn__qawac = builder.extract_value(igsjw__hsyeb,
                                hhmk__wdge)
                            ixx__lphr = builder.insert_value(ixx__lphr,
                                builder.add(qaoge__nlk, lfn__qawac), 
                                msdk__xusgh + hhmk__wdge)
                        builder.store(ixx__lphr, yxbtm__kicqy)
                    msdk__xusgh += gixp__gdshc
            else:
                assert isinstance(typ, MapArrayType), typ
                ixx__lphr = builder.load(yxbtm__kicqy)
                tfiua__dopc = dict_keys(builder, context, pfigp__rbbm)
                nbojd__xuix = dict_values(builder, context, pfigp__rbbm)
                tjsq__itq = get_array_elem_counts(c, builder, context,
                    tfiua__dopc, typ.key_arr_type)
                zsj__tpbwm = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for hhmk__wdge in range(1, zsj__tpbwm + 1):
                    qaoge__nlk = builder.extract_value(ixx__lphr, hhmk__wdge)
                    lfn__qawac = builder.extract_value(tjsq__itq, 
                        hhmk__wdge - 1)
                    ixx__lphr = builder.insert_value(ixx__lphr, builder.add
                        (qaoge__nlk, lfn__qawac), hhmk__wdge)
                hhyxu__mbflr = get_array_elem_counts(c, builder, context,
                    nbojd__xuix, typ.value_arr_type)
                for hhmk__wdge in range(zsj__tpbwm + 1, wsvsy__xcac):
                    qaoge__nlk = builder.extract_value(ixx__lphr, hhmk__wdge)
                    lfn__qawac = builder.extract_value(hhyxu__mbflr, 
                        hhmk__wdge - zsj__tpbwm)
                    ixx__lphr = builder.insert_value(ixx__lphr, builder.add
                        (qaoge__nlk, lfn__qawac), hhmk__wdge)
                builder.store(ixx__lphr, yxbtm__kicqy)
                c.pyapi.decref(tfiua__dopc)
                c.pyapi.decref(nbojd__xuix)
        c.pyapi.decref(pfigp__rbbm)
    c.pyapi.decref(mnfiw__xnh)
    c.pyapi.decref(C_NA)
    return builder.load(yxbtm__kicqy)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    izo__anf = n_elems.type.count
    assert izo__anf >= 1
    hjfgk__ncwk = builder.extract_value(n_elems, 0)
    if izo__anf != 1:
        qsvh__cul = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, hhmk__wdge) for hhmk__wdge in range(1, izo__anf)])
        bogdq__ozqq = types.Tuple([types.int64] * (izo__anf - 1))
    else:
        qsvh__cul = context.get_dummy_value()
        bogdq__ozqq = types.none
    uxiib__qrjca = types.TypeRef(arr_type)
    gkx__pzh = arr_type(types.int64, uxiib__qrjca, bogdq__ozqq)
    args = [hjfgk__ncwk, context.get_dummy_value(), qsvh__cul]
    dkb__ndoh = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        nvvyv__czh, vzy__fwtas = c.pyapi.call_jit_code(dkb__ndoh, gkx__pzh,
            args)
    else:
        vzy__fwtas = context.compile_internal(builder, dkb__ndoh, gkx__pzh,
            args)
    return vzy__fwtas


def is_ll_eq(builder, val1, val2):
    ozk__qsls = val1.type.pointee
    bvs__kyccl = val2.type.pointee
    assert ozk__qsls == bvs__kyccl, 'invalid llvm value comparison'
    if isinstance(ozk__qsls, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(ozk__qsls.elements) if isinstance(ozk__qsls, lir.
            BaseStructType) else ozk__qsls.count
        gshzq__hucts = lir.Constant(lir.IntType(1), 1)
        for hhmk__wdge in range(n_elems):
            fdjad__nbq = lir.IntType(32)(0)
            wbfdn__jrpbj = lir.IntType(32)(hhmk__wdge)
            ssr__vnq = builder.gep(val1, [fdjad__nbq, wbfdn__jrpbj],
                inbounds=True)
            lgmw__egxx = builder.gep(val2, [fdjad__nbq, wbfdn__jrpbj],
                inbounds=True)
            gshzq__hucts = builder.and_(gshzq__hucts, is_ll_eq(builder,
                ssr__vnq, lgmw__egxx))
        return gshzq__hucts
    bscl__njvp = builder.load(val1)
    duxy__cnrd = builder.load(val2)
    if bscl__njvp.type in (lir.FloatType(), lir.DoubleType()):
        nwdwl__nvao = 32 if bscl__njvp.type == lir.FloatType() else 64
        bscl__njvp = builder.bitcast(bscl__njvp, lir.IntType(nwdwl__nvao))
        duxy__cnrd = builder.bitcast(duxy__cnrd, lir.IntType(nwdwl__nvao))
    return builder.icmp_unsigned('==', bscl__njvp, duxy__cnrd)
