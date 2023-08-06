import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ=None):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    mjy__qfnx = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        ejymo__fngdi, = args
        kovqn__cme = cgutils.create_struct_proxy(string_type)(context,
            builder, value=ejymo__fngdi)
        cdfdh__kon = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        muqn__aqbia = cgutils.create_struct_proxy(mjy__qfnx)(context, builder)
        is_ascii = builder.icmp_unsigned('==', kovqn__cme.is_ascii, lir.
            Constant(kovqn__cme.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (then, orelse):
            with then:
                context.nrt.incref(builder, string_type, ejymo__fngdi)
                cdfdh__kon.data = kovqn__cme.data
                cdfdh__kon.meminfo = kovqn__cme.meminfo
                muqn__aqbia.f1 = kovqn__cme.length
            with orelse:
                kyiqw__egogl = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                swt__mrcqm = cgutils.get_or_insert_function(builder.module,
                    kyiqw__egogl, name='unicode_to_utf8')
                sbtli__iab = context.get_constant_null(types.voidptr)
                yjsoi__qpp = builder.call(swt__mrcqm, [sbtli__iab,
                    kovqn__cme.data, kovqn__cme.length, kovqn__cme.kind])
                muqn__aqbia.f1 = yjsoi__qpp
                cie__zud = builder.add(yjsoi__qpp, lir.Constant(lir.IntType
                    (64), 1))
                cdfdh__kon.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=cie__zud, align=32)
                cdfdh__kon.data = context.nrt.meminfo_data(builder,
                    cdfdh__kon.meminfo)
                builder.call(swt__mrcqm, [cdfdh__kon.data, kovqn__cme.data,
                    kovqn__cme.length, kovqn__cme.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    cdfdh__kon.data, [yjsoi__qpp]))
        muqn__aqbia.f0 = cdfdh__kon._getvalue()
        return muqn__aqbia._getvalue()
    return mjy__qfnx(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        kyiqw__egogl = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        qgsx__spj = cgutils.get_or_insert_function(builder.module,
            kyiqw__egogl, name='memcmp')
        return builder.call(qgsx__spj, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    hmmx__tli = n(10)

    def impl(n):
        if n == 0:
            return 1
        pod__daxyp = 0
        if n < 0:
            n = -n
            pod__daxyp += 1
        while n > 0:
            n = n // hmmx__tli
            pod__daxyp += 1
        return pod__daxyp
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [vuny__prl] = args
        if isinstance(vuny__prl, StdStringType):
            return signature(types.float64, vuny__prl)
        if vuny__prl == string_type:
            return signature(types.float64, vuny__prl)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    kovqn__cme = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    kyiqw__egogl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    quty__htltm = cgutils.get_or_insert_function(builder.module,
        kyiqw__egogl, name='init_string_const')
    return builder.call(quty__htltm, [kovqn__cme.data, kovqn__cme.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        mzukh__ndolx = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(mzukh__ndolx._data, bodo.libs.str_ext
            .get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return mzukh__ndolx
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    kovqn__cme = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return kovqn__cme.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vjapf__tvlzm = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, vjapf__tvlzm)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        cimf__osdql, = args
        xnnnl__cdqs = types.List(string_type)
        spm__nrq = numba.cpython.listobj.ListInstance.allocate(context,
            builder, xnnnl__cdqs, cimf__osdql)
        spm__nrq.size = cimf__osdql
        lzb__pgrkw = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        lzb__pgrkw.data = spm__nrq.value
        return lzb__pgrkw._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            kuwu__qbv = 0
            erh__zzox = v
            if erh__zzox < 0:
                kuwu__qbv = 1
                erh__zzox = -erh__zzox
            if erh__zzox < 1:
                tijv__itwxe = 1
            else:
                tijv__itwxe = 1 + int(np.floor(np.log10(erh__zzox)))
            length = kuwu__qbv + tijv__itwxe + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    kyiqw__egogl = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    quty__htltm = cgutils.get_or_insert_function(builder.module,
        kyiqw__egogl, name='str_to_float64')
    res = builder.call(quty__htltm, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    kyiqw__egogl = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    quty__htltm = cgutils.get_or_insert_function(builder.module,
        kyiqw__egogl, name='str_to_float32')
    res = builder.call(quty__htltm, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    kovqn__cme = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    kyiqw__egogl = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    quty__htltm = cgutils.get_or_insert_function(builder.module,
        kyiqw__egogl, name='str_to_int64')
    res = builder.call(quty__htltm, (kovqn__cme.data, kovqn__cme.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    kovqn__cme = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    kyiqw__egogl = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    quty__htltm = cgutils.get_or_insert_function(builder.module,
        kyiqw__egogl, name='str_to_uint64')
    res = builder.call(quty__htltm, (kovqn__cme.data, kovqn__cme.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        dev__adyfk = ', '.join('e{}'.format(lam__dsoji) for lam__dsoji in
            range(len(args)))
        if dev__adyfk:
            dev__adyfk += ', '
        qxxy__qklha = ', '.join("{} = ''".format(a) for a in kws.keys())
        bsyj__ltai = f'def format_stub(string, {dev__adyfk} {qxxy__qklha}):\n'
        bsyj__ltai += '    pass\n'
        nlx__wtic = {}
        exec(bsyj__ltai, {}, nlx__wtic)
        fnf__ihgnl = nlx__wtic['format_stub']
        cieej__tshgk = numba.core.utils.pysignature(fnf__ihgnl)
        gkrhk__ijsh = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, gkrhk__ijsh).replace(pysig=cieej__tshgk)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    bwt__fsx = pat is not None and len(pat) > 1
    if bwt__fsx:
        ovx__dgaos = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    spm__nrq = len(arr)
    xjle__rjz = 0
    qirxf__xzyaz = 0
    for lam__dsoji in numba.parfors.parfor.internal_prange(spm__nrq):
        if bodo.libs.array_kernels.isna(arr, lam__dsoji):
            continue
        if bwt__fsx:
            bjnhf__sjeri = ovx__dgaos.split(arr[lam__dsoji], maxsplit=n)
        elif pat == '':
            bjnhf__sjeri = [''] + list(arr[lam__dsoji]) + ['']
        else:
            bjnhf__sjeri = arr[lam__dsoji].split(pat, n)
        xjle__rjz += len(bjnhf__sjeri)
        for s in bjnhf__sjeri:
            qirxf__xzyaz += bodo.libs.str_arr_ext.get_utf8_size(s)
    ocb__nuanr = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        spm__nrq, (xjle__rjz, qirxf__xzyaz), bodo.libs.str_arr_ext.
        string_array_type)
    fed__shvdj = bodo.libs.array_item_arr_ext.get_offsets(ocb__nuanr)
    tth__lligi = bodo.libs.array_item_arr_ext.get_null_bitmap(ocb__nuanr)
    khd__hzmkz = bodo.libs.array_item_arr_ext.get_data(ocb__nuanr)
    ctsji__klypk = 0
    for anxll__evfi in numba.parfors.parfor.internal_prange(spm__nrq):
        fed__shvdj[anxll__evfi] = ctsji__klypk
        if bodo.libs.array_kernels.isna(arr, anxll__evfi):
            bodo.libs.int_arr_ext.set_bit_to_arr(tth__lligi, anxll__evfi, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(tth__lligi, anxll__evfi, 1)
        if bwt__fsx:
            bjnhf__sjeri = ovx__dgaos.split(arr[anxll__evfi], maxsplit=n)
        elif pat == '':
            bjnhf__sjeri = [''] + list(arr[anxll__evfi]) + ['']
        else:
            bjnhf__sjeri = arr[anxll__evfi].split(pat, n)
        uyrch__cocib = len(bjnhf__sjeri)
        for pvq__vztc in range(uyrch__cocib):
            s = bjnhf__sjeri[pvq__vztc]
            khd__hzmkz[ctsji__klypk] = s
            ctsji__klypk += 1
    fed__shvdj[spm__nrq] = ctsji__klypk
    return ocb__nuanr


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                dfqp__smtfe = '-0x'
                x = x * -1
            else:
                dfqp__smtfe = '0x'
            x = np.uint64(x)
            if x == 0:
                ydm__dzfk = 1
            else:
                ydm__dzfk = fast_ceil_log2(x + 1)
                ydm__dzfk = (ydm__dzfk + 3) // 4
            length = len(dfqp__smtfe) + ydm__dzfk
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, dfqp__smtfe._data,
                len(dfqp__smtfe), 1)
            int_to_hex(output, ydm__dzfk, len(dfqp__smtfe), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    mjfy__lhqza = 0 if x & x - 1 == 0 else 1
    wpn__yyvt = [np.uint64(18446744069414584320), np.uint64(4294901760), np
        .uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    jlkw__epqx = 32
    for lam__dsoji in range(len(wpn__yyvt)):
        burw__umbed = 0 if x & wpn__yyvt[lam__dsoji] == 0 else jlkw__epqx
        mjfy__lhqza = mjfy__lhqza + burw__umbed
        x = x >> burw__umbed
        jlkw__epqx = jlkw__epqx >> 1
    return mjfy__lhqza


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        lnpz__ctns = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        kyiqw__egogl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        nxlyu__twcxv = cgutils.get_or_insert_function(builder.module,
            kyiqw__egogl, name='int_to_hex')
        yfakm__lyopl = builder.inttoptr(builder.add(builder.ptrtoint(
            lnpz__ctns.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(nxlyu__twcxv, (yfakm__lyopl, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
