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
    wxsvx__svot = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    xjnlc__hceoj = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    gfdd__ljha = builder.gep(null_bitmap_ptr, [wxsvx__svot], inbounds=True)
    mvgks__osapk = builder.load(gfdd__ljha)
    ywm__rbcqp = lir.ArrayType(lir.IntType(8), 8)
    evjdk__poa = cgutils.alloca_once_value(builder, lir.Constant(ywm__rbcqp,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    bph__pipc = builder.load(builder.gep(evjdk__poa, [lir.Constant(lir.
        IntType(64), 0), xjnlc__hceoj], inbounds=True))
    if val:
        builder.store(builder.or_(mvgks__osapk, bph__pipc), gfdd__ljha)
    else:
        bph__pipc = builder.xor(bph__pipc, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(mvgks__osapk, bph__pipc), gfdd__ljha)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    wxsvx__svot = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    xjnlc__hceoj = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    mvgks__osapk = builder.load(builder.gep(null_bitmap_ptr, [wxsvx__svot],
        inbounds=True))
    ywm__rbcqp = lir.ArrayType(lir.IntType(8), 8)
    evjdk__poa = cgutils.alloca_once_value(builder, lir.Constant(ywm__rbcqp,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    bph__pipc = builder.load(builder.gep(evjdk__poa, [lir.Constant(lir.
        IntType(64), 0), xjnlc__hceoj], inbounds=True))
    return builder.and_(mvgks__osapk, bph__pipc)


def pyarray_getitem(builder, context, arr_obj, ind):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    ryh__uejjn = context.get_value_type(types.intp)
    vdrgn__tgc = lir.FunctionType(lir.IntType(8).as_pointer(), [tvmc__qctn,
        ryh__uejjn])
    fzqo__yeixh = cgutils.get_or_insert_function(builder.module, vdrgn__tgc,
        name='array_getptr1')
    dhbp__ggdg = lir.FunctionType(tvmc__qctn, [tvmc__qctn, lir.IntType(8).
        as_pointer()])
    tnta__gnsy = cgutils.get_or_insert_function(builder.module, dhbp__ggdg,
        name='array_getitem')
    jjg__nlzc = builder.call(fzqo__yeixh, [arr_obj, ind])
    return builder.call(tnta__gnsy, [arr_obj, jjg__nlzc])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    ryh__uejjn = context.get_value_type(types.intp)
    vdrgn__tgc = lir.FunctionType(lir.IntType(8).as_pointer(), [tvmc__qctn,
        ryh__uejjn])
    fzqo__yeixh = cgutils.get_or_insert_function(builder.module, vdrgn__tgc,
        name='array_getptr1')
    tzmk__uqk = lir.FunctionType(lir.VoidType(), [tvmc__qctn, lir.IntType(8
        ).as_pointer(), tvmc__qctn])
    jumr__lxmb = cgutils.get_or_insert_function(builder.module, tzmk__uqk,
        name='array_setitem')
    jjg__nlzc = builder.call(fzqo__yeixh, [arr_obj, ind])
    builder.call(jumr__lxmb, [arr_obj, jjg__nlzc, val_obj])


def seq_getitem(builder, context, obj, ind):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    ryh__uejjn = context.get_value_type(types.intp)
    kwpln__jro = lir.FunctionType(tvmc__qctn, [tvmc__qctn, ryh__uejjn])
    luv__xmrab = cgutils.get_or_insert_function(builder.module, kwpln__jro,
        name='seq_getitem')
    return builder.call(luv__xmrab, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    npl__zip = lir.FunctionType(lir.IntType(32), [tvmc__qctn, tvmc__qctn])
    qmtkn__zjt = cgutils.get_or_insert_function(builder.module, npl__zip,
        name='is_na_value')
    return builder.call(qmtkn__zjt, [val, C_NA])


def list_check(builder, context, obj):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    iotio__ejti = context.get_value_type(types.int32)
    azgz__kaulf = lir.FunctionType(iotio__ejti, [tvmc__qctn])
    hzlv__xaet = cgutils.get_or_insert_function(builder.module, azgz__kaulf,
        name='list_check')
    return builder.call(hzlv__xaet, [obj])


def dict_keys(builder, context, obj):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    azgz__kaulf = lir.FunctionType(tvmc__qctn, [tvmc__qctn])
    hzlv__xaet = cgutils.get_or_insert_function(builder.module, azgz__kaulf,
        name='dict_keys')
    return builder.call(hzlv__xaet, [obj])


def dict_values(builder, context, obj):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    azgz__kaulf = lir.FunctionType(tvmc__qctn, [tvmc__qctn])
    hzlv__xaet = cgutils.get_or_insert_function(builder.module, azgz__kaulf,
        name='dict_values')
    return builder.call(hzlv__xaet, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    tvmc__qctn = context.get_argument_type(types.pyobject)
    azgz__kaulf = lir.FunctionType(lir.VoidType(), [tvmc__qctn, tvmc__qctn])
    hzlv__xaet = cgutils.get_or_insert_function(builder.module, azgz__kaulf,
        name='dict_merge_from_seq2')
    builder.call(hzlv__xaet, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    lqhze__lhj = cgutils.alloca_once_value(builder, val)
    azxsk__lbn = list_check(builder, context, val)
    vhv__rkwf = builder.icmp_unsigned('!=', azxsk__lbn, lir.Constant(
        azxsk__lbn.type, 0))
    with builder.if_then(vhv__rkwf):
        oxj__cxya = context.insert_const_string(builder.module, 'numpy')
        aqut__dabd = c.pyapi.import_module_noblock(oxj__cxya)
        vyhc__dsi = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            vyhc__dsi = str(typ.dtype)
        nhxg__aetcc = c.pyapi.object_getattr_string(aqut__dabd, vyhc__dsi)
        nfatf__rjma = builder.load(lqhze__lhj)
        tfjzq__umodv = c.pyapi.call_method(aqut__dabd, 'asarray', (
            nfatf__rjma, nhxg__aetcc))
        builder.store(tfjzq__umodv, lqhze__lhj)
        c.pyapi.decref(aqut__dabd)
        c.pyapi.decref(nhxg__aetcc)
    val = builder.load(lqhze__lhj)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        oohd__eaxi = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        lxta__wnug, ppvu__seoy = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [oohd__eaxi])
        context.nrt.decref(builder, typ, oohd__eaxi)
        return cgutils.pack_array(builder, [ppvu__seoy])
    if isinstance(typ, (StructType, types.BaseTuple)):
        oxj__cxya = context.insert_const_string(builder.module, 'pandas')
        vvyqo__phn = c.pyapi.import_module_noblock(oxj__cxya)
        C_NA = c.pyapi.object_getattr_string(vvyqo__phn, 'NA')
        qwms__fcr = bodo.utils.transform.get_type_alloc_counts(typ)
        obi__hxikb = context.make_tuple(builder, types.Tuple(qwms__fcr * [
            types.int64]), qwms__fcr * [context.get_constant(types.int64, 0)])
        tbm__nzsiv = cgutils.alloca_once_value(builder, obi__hxikb)
        adoy__hajlt = 0
        vnvfy__pot = typ.data if isinstance(typ, StructType) else typ.types
        for smt__qgnql, t in enumerate(vnvfy__pot):
            lnsh__rdqs = bodo.utils.transform.get_type_alloc_counts(t)
            if lnsh__rdqs == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    smt__qgnql])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, smt__qgnql)
            upu__mnutu = is_na_value(builder, context, val_obj, C_NA)
            bfg__ymg = builder.icmp_unsigned('!=', upu__mnutu, lir.Constant
                (upu__mnutu.type, 1))
            with builder.if_then(bfg__ymg):
                obi__hxikb = builder.load(tbm__nzsiv)
                vpu__wgf = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for smt__qgnql in range(lnsh__rdqs):
                    jgued__cdgwd = builder.extract_value(obi__hxikb, 
                        adoy__hajlt + smt__qgnql)
                    rkho__vwyz = builder.extract_value(vpu__wgf, smt__qgnql)
                    obi__hxikb = builder.insert_value(obi__hxikb, builder.
                        add(jgued__cdgwd, rkho__vwyz), adoy__hajlt + smt__qgnql
                        )
                builder.store(obi__hxikb, tbm__nzsiv)
            adoy__hajlt += lnsh__rdqs
        c.pyapi.decref(vvyqo__phn)
        c.pyapi.decref(C_NA)
        return builder.load(tbm__nzsiv)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    oxj__cxya = context.insert_const_string(builder.module, 'pandas')
    vvyqo__phn = c.pyapi.import_module_noblock(oxj__cxya)
    C_NA = c.pyapi.object_getattr_string(vvyqo__phn, 'NA')
    qwms__fcr = bodo.utils.transform.get_type_alloc_counts(typ)
    obi__hxikb = context.make_tuple(builder, types.Tuple(qwms__fcr * [types
        .int64]), [n] + (qwms__fcr - 1) * [context.get_constant(types.int64,
        0)])
    tbm__nzsiv = cgutils.alloca_once_value(builder, obi__hxikb)
    with cgutils.for_range(builder, n) as loop:
        mrd__dxkqm = loop.index
        cxm__bgbu = seq_getitem(builder, context, arr_obj, mrd__dxkqm)
        upu__mnutu = is_na_value(builder, context, cxm__bgbu, C_NA)
        bfg__ymg = builder.icmp_unsigned('!=', upu__mnutu, lir.Constant(
            upu__mnutu.type, 1))
        with builder.if_then(bfg__ymg):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                obi__hxikb = builder.load(tbm__nzsiv)
                vpu__wgf = get_array_elem_counts(c, builder, context,
                    cxm__bgbu, typ.dtype)
                for smt__qgnql in range(qwms__fcr - 1):
                    jgued__cdgwd = builder.extract_value(obi__hxikb, 
                        smt__qgnql + 1)
                    rkho__vwyz = builder.extract_value(vpu__wgf, smt__qgnql)
                    obi__hxikb = builder.insert_value(obi__hxikb, builder.
                        add(jgued__cdgwd, rkho__vwyz), smt__qgnql + 1)
                builder.store(obi__hxikb, tbm__nzsiv)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                adoy__hajlt = 1
                for smt__qgnql, t in enumerate(typ.data):
                    lnsh__rdqs = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if lnsh__rdqs == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(cxm__bgbu, smt__qgnql)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(cxm__bgbu,
                            typ.names[smt__qgnql])
                    upu__mnutu = is_na_value(builder, context, val_obj, C_NA)
                    bfg__ymg = builder.icmp_unsigned('!=', upu__mnutu, lir.
                        Constant(upu__mnutu.type, 1))
                    with builder.if_then(bfg__ymg):
                        obi__hxikb = builder.load(tbm__nzsiv)
                        vpu__wgf = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for smt__qgnql in range(lnsh__rdqs):
                            jgued__cdgwd = builder.extract_value(obi__hxikb,
                                adoy__hajlt + smt__qgnql)
                            rkho__vwyz = builder.extract_value(vpu__wgf,
                                smt__qgnql)
                            obi__hxikb = builder.insert_value(obi__hxikb,
                                builder.add(jgued__cdgwd, rkho__vwyz), 
                                adoy__hajlt + smt__qgnql)
                        builder.store(obi__hxikb, tbm__nzsiv)
                    adoy__hajlt += lnsh__rdqs
            else:
                assert isinstance(typ, MapArrayType), typ
                obi__hxikb = builder.load(tbm__nzsiv)
                pprb__ttf = dict_keys(builder, context, cxm__bgbu)
                wmp__ddwpf = dict_values(builder, context, cxm__bgbu)
                wuu__yhsd = get_array_elem_counts(c, builder, context,
                    pprb__ttf, typ.key_arr_type)
                eyhh__zmzk = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for smt__qgnql in range(1, eyhh__zmzk + 1):
                    jgued__cdgwd = builder.extract_value(obi__hxikb, smt__qgnql
                        )
                    rkho__vwyz = builder.extract_value(wuu__yhsd, 
                        smt__qgnql - 1)
                    obi__hxikb = builder.insert_value(obi__hxikb, builder.
                        add(jgued__cdgwd, rkho__vwyz), smt__qgnql)
                velap__flaoi = get_array_elem_counts(c, builder, context,
                    wmp__ddwpf, typ.value_arr_type)
                for smt__qgnql in range(eyhh__zmzk + 1, qwms__fcr):
                    jgued__cdgwd = builder.extract_value(obi__hxikb, smt__qgnql
                        )
                    rkho__vwyz = builder.extract_value(velap__flaoi, 
                        smt__qgnql - eyhh__zmzk)
                    obi__hxikb = builder.insert_value(obi__hxikb, builder.
                        add(jgued__cdgwd, rkho__vwyz), smt__qgnql)
                builder.store(obi__hxikb, tbm__nzsiv)
                c.pyapi.decref(pprb__ttf)
                c.pyapi.decref(wmp__ddwpf)
        c.pyapi.decref(cxm__bgbu)
    c.pyapi.decref(vvyqo__phn)
    c.pyapi.decref(C_NA)
    return builder.load(tbm__nzsiv)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    jbh__puuxm = n_elems.type.count
    assert jbh__puuxm >= 1
    jgsyt__lbm = builder.extract_value(n_elems, 0)
    if jbh__puuxm != 1:
        lzue__amw = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, smt__qgnql) for smt__qgnql in range(1, jbh__puuxm)])
        eut__ofme = types.Tuple([types.int64] * (jbh__puuxm - 1))
    else:
        lzue__amw = context.get_dummy_value()
        eut__ofme = types.none
    rpkf__vqbop = types.TypeRef(arr_type)
    ggomp__zfwkl = arr_type(types.int64, rpkf__vqbop, eut__ofme)
    args = [jgsyt__lbm, context.get_dummy_value(), lzue__amw]
    eay__amgj = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        lxta__wnug, jbus__czwto = c.pyapi.call_jit_code(eay__amgj,
            ggomp__zfwkl, args)
    else:
        jbus__czwto = context.compile_internal(builder, eay__amgj,
            ggomp__zfwkl, args)
    return jbus__czwto


def is_ll_eq(builder, val1, val2):
    eissf__dtle = val1.type.pointee
    izr__akfxg = val2.type.pointee
    assert eissf__dtle == izr__akfxg, 'invalid llvm value comparison'
    if isinstance(eissf__dtle, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(eissf__dtle.elements) if isinstance(eissf__dtle, lir.
            BaseStructType) else eissf__dtle.count
        rowhq__ojnyo = lir.Constant(lir.IntType(1), 1)
        for smt__qgnql in range(n_elems):
            ntq__dsour = lir.IntType(32)(0)
            czqc__prfbo = lir.IntType(32)(smt__qgnql)
            vala__oher = builder.gep(val1, [ntq__dsour, czqc__prfbo],
                inbounds=True)
            giky__csbar = builder.gep(val2, [ntq__dsour, czqc__prfbo],
                inbounds=True)
            rowhq__ojnyo = builder.and_(rowhq__ojnyo, is_ll_eq(builder,
                vala__oher, giky__csbar))
        return rowhq__ojnyo
    uvgv__qvup = builder.load(val1)
    yeujw__hmbnd = builder.load(val2)
    if uvgv__qvup.type in (lir.FloatType(), lir.DoubleType()):
        kxuq__sba = 32 if uvgv__qvup.type == lir.FloatType() else 64
        uvgv__qvup = builder.bitcast(uvgv__qvup, lir.IntType(kxuq__sba))
        yeujw__hmbnd = builder.bitcast(yeujw__hmbnd, lir.IntType(kxuq__sba))
    return builder.icmp_unsigned('==', uvgv__qvup, yeujw__hmbnd)
