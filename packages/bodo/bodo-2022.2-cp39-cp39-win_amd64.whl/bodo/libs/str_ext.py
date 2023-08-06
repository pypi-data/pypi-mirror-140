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
    vnv__jyhui = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        yrskq__zkat, = args
        lagy__slm = cgutils.create_struct_proxy(string_type)(context,
            builder, value=yrskq__zkat)
        vzy__gemd = cgutils.create_struct_proxy(utf8_str_type)(context, builder
            )
        doifl__cfnwo = cgutils.create_struct_proxy(vnv__jyhui)(context, builder
            )
        is_ascii = builder.icmp_unsigned('==', lagy__slm.is_ascii, lir.
            Constant(lagy__slm.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (then, orelse):
            with then:
                context.nrt.incref(builder, string_type, yrskq__zkat)
                vzy__gemd.data = lagy__slm.data
                vzy__gemd.meminfo = lagy__slm.meminfo
                doifl__cfnwo.f1 = lagy__slm.length
            with orelse:
                axkux__gfxsc = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                zgim__axlma = cgutils.get_or_insert_function(builder.module,
                    axkux__gfxsc, name='unicode_to_utf8')
                frfb__ycuse = context.get_constant_null(types.voidptr)
                asftz__sxb = builder.call(zgim__axlma, [frfb__ycuse,
                    lagy__slm.data, lagy__slm.length, lagy__slm.kind])
                doifl__cfnwo.f1 = asftz__sxb
                buu__vvveu = builder.add(asftz__sxb, lir.Constant(lir.
                    IntType(64), 1))
                vzy__gemd.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=buu__vvveu, align=32)
                vzy__gemd.data = context.nrt.meminfo_data(builder,
                    vzy__gemd.meminfo)
                builder.call(zgim__axlma, [vzy__gemd.data, lagy__slm.data,
                    lagy__slm.length, lagy__slm.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    vzy__gemd.data, [asftz__sxb]))
        doifl__cfnwo.f0 = vzy__gemd._getvalue()
        return doifl__cfnwo._getvalue()
    return vnv__jyhui(string_type), codegen


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
        axkux__gfxsc = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        zalmc__yssj = cgutils.get_or_insert_function(builder.module,
            axkux__gfxsc, name='memcmp')
        return builder.call(zalmc__yssj, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    bren__gez = n(10)

    def impl(n):
        if n == 0:
            return 1
        pfepo__duoq = 0
        if n < 0:
            n = -n
            pfepo__duoq += 1
        while n > 0:
            n = n // bren__gez
            pfepo__duoq += 1
        return pfepo__duoq
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
        [vvpsf__pqtr] = args
        if isinstance(vvpsf__pqtr, StdStringType):
            return signature(types.float64, vvpsf__pqtr)
        if vvpsf__pqtr == string_type:
            return signature(types.float64, vvpsf__pqtr)


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
    lagy__slm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    axkux__gfxsc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    mzl__ugfa = cgutils.get_or_insert_function(builder.module, axkux__gfxsc,
        name='init_string_const')
    return builder.call(mzl__ugfa, [lagy__slm.data, lagy__slm.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        uvhn__nqhtm = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(uvhn__nqhtm._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return uvhn__nqhtm
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    lagy__slm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return lagy__slm.data


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
        yhgy__zfr = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, yhgy__zfr)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        idkmu__upt, = args
        lryqi__ohbj = types.List(string_type)
        lpnmv__fbug = numba.cpython.listobj.ListInstance.allocate(context,
            builder, lryqi__ohbj, idkmu__upt)
        lpnmv__fbug.size = idkmu__upt
        jgsz__jky = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        jgsz__jky.data = lpnmv__fbug.value
        return jgsz__jky._getvalue()
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
            fmn__azaov = 0
            schcy__bjfp = v
            if schcy__bjfp < 0:
                fmn__azaov = 1
                schcy__bjfp = -schcy__bjfp
            if schcy__bjfp < 1:
                jatvk__kds = 1
            else:
                jatvk__kds = 1 + int(np.floor(np.log10(schcy__bjfp)))
            length = fmn__azaov + jatvk__kds + 1 + 6
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
    axkux__gfxsc = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    mzl__ugfa = cgutils.get_or_insert_function(builder.module, axkux__gfxsc,
        name='str_to_float64')
    res = builder.call(mzl__ugfa, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    axkux__gfxsc = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    mzl__ugfa = cgutils.get_or_insert_function(builder.module, axkux__gfxsc,
        name='str_to_float32')
    res = builder.call(mzl__ugfa, (val,))
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
    lagy__slm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    axkux__gfxsc = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    mzl__ugfa = cgutils.get_or_insert_function(builder.module, axkux__gfxsc,
        name='str_to_int64')
    res = builder.call(mzl__ugfa, (lagy__slm.data, lagy__slm.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    lagy__slm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    axkux__gfxsc = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    mzl__ugfa = cgutils.get_or_insert_function(builder.module, axkux__gfxsc,
        name='str_to_uint64')
    res = builder.call(mzl__ugfa, (lagy__slm.data, lagy__slm.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        nzfqg__kpoow = ', '.join('e{}'.format(liynh__nyin) for liynh__nyin in
            range(len(args)))
        if nzfqg__kpoow:
            nzfqg__kpoow += ', '
        ihdh__rsxxk = ', '.join("{} = ''".format(a) for a in kws.keys())
        qiouk__dguk = (
            f'def format_stub(string, {nzfqg__kpoow} {ihdh__rsxxk}):\n')
        qiouk__dguk += '    pass\n'
        fdlzp__scc = {}
        exec(qiouk__dguk, {}, fdlzp__scc)
        rkxs__jmk = fdlzp__scc['format_stub']
        htzwu__jniy = numba.core.utils.pysignature(rkxs__jmk)
        qgv__oat = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, qgv__oat).replace(pysig=htzwu__jniy)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    bkx__aswje = pat is not None and len(pat) > 1
    if bkx__aswje:
        xkxpb__yea = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    lpnmv__fbug = len(arr)
    gdgi__mac = 0
    jaqwh__qjvcr = 0
    for liynh__nyin in numba.parfors.parfor.internal_prange(lpnmv__fbug):
        if bodo.libs.array_kernels.isna(arr, liynh__nyin):
            continue
        if bkx__aswje:
            wvms__zah = xkxpb__yea.split(arr[liynh__nyin], maxsplit=n)
        elif pat == '':
            wvms__zah = [''] + list(arr[liynh__nyin]) + ['']
        else:
            wvms__zah = arr[liynh__nyin].split(pat, n)
        gdgi__mac += len(wvms__zah)
        for s in wvms__zah:
            jaqwh__qjvcr += bodo.libs.str_arr_ext.get_utf8_size(s)
    xefj__fpcb = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        lpnmv__fbug, (gdgi__mac, jaqwh__qjvcr), bodo.libs.str_arr_ext.
        string_array_type)
    zzjz__xwgia = bodo.libs.array_item_arr_ext.get_offsets(xefj__fpcb)
    xfo__vyswz = bodo.libs.array_item_arr_ext.get_null_bitmap(xefj__fpcb)
    yuqc__fbabr = bodo.libs.array_item_arr_ext.get_data(xefj__fpcb)
    kvk__sxouj = 0
    for ubuaa__amt in numba.parfors.parfor.internal_prange(lpnmv__fbug):
        zzjz__xwgia[ubuaa__amt] = kvk__sxouj
        if bodo.libs.array_kernels.isna(arr, ubuaa__amt):
            bodo.libs.int_arr_ext.set_bit_to_arr(xfo__vyswz, ubuaa__amt, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(xfo__vyswz, ubuaa__amt, 1)
        if bkx__aswje:
            wvms__zah = xkxpb__yea.split(arr[ubuaa__amt], maxsplit=n)
        elif pat == '':
            wvms__zah = [''] + list(arr[ubuaa__amt]) + ['']
        else:
            wvms__zah = arr[ubuaa__amt].split(pat, n)
        saz__mtfn = len(wvms__zah)
        for gztqb__uwmvd in range(saz__mtfn):
            s = wvms__zah[gztqb__uwmvd]
            yuqc__fbabr[kvk__sxouj] = s
            kvk__sxouj += 1
    zzjz__xwgia[lpnmv__fbug] = kvk__sxouj
    return xefj__fpcb


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                ifbyp__rzzem = '-0x'
                x = x * -1
            else:
                ifbyp__rzzem = '0x'
            x = np.uint64(x)
            if x == 0:
                cvd__zcp = 1
            else:
                cvd__zcp = fast_ceil_log2(x + 1)
                cvd__zcp = (cvd__zcp + 3) // 4
            length = len(ifbyp__rzzem) + cvd__zcp
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, ifbyp__rzzem._data,
                len(ifbyp__rzzem), 1)
            int_to_hex(output, cvd__zcp, len(ifbyp__rzzem), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    jym__uvt = 0 if x & x - 1 == 0 else 1
    vhqd__wkhi = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    imf__esz = 32
    for liynh__nyin in range(len(vhqd__wkhi)):
        zutf__myi = 0 if x & vhqd__wkhi[liynh__nyin] == 0 else imf__esz
        jym__uvt = jym__uvt + zutf__myi
        x = x >> zutf__myi
        imf__esz = imf__esz >> 1
    return jym__uvt


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        oxn__dji = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        axkux__gfxsc = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        gxzf__zniu = cgutils.get_or_insert_function(builder.module,
            axkux__gfxsc, name='int_to_hex')
        roztf__qrzb = builder.inttoptr(builder.add(builder.ptrtoint(
            oxn__dji.data, lir.IntType(64)), header_len), lir.IntType(8).
            as_pointer())
        builder.call(gxzf__zniu, (roztf__qrzb, out_len, int_val))
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
