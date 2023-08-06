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
    ckbi__bgz = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        kpuy__frsq, = args
        xel__fei = cgutils.create_struct_proxy(string_type)(context,
            builder, value=kpuy__frsq)
        xwmpr__onns = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        auf__savgt = cgutils.create_struct_proxy(ckbi__bgz)(context, builder)
        is_ascii = builder.icmp_unsigned('==', xel__fei.is_ascii, lir.
            Constant(xel__fei.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (then, orelse):
            with then:
                context.nrt.incref(builder, string_type, kpuy__frsq)
                xwmpr__onns.data = xel__fei.data
                xwmpr__onns.meminfo = xel__fei.meminfo
                auf__savgt.f1 = xel__fei.length
            with orelse:
                aikj__isp = lir.FunctionType(lir.IntType(64), [lir.IntType(
                    8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                nfhb__jtjs = cgutils.get_or_insert_function(builder.module,
                    aikj__isp, name='unicode_to_utf8')
                ril__sggj = context.get_constant_null(types.voidptr)
                cbx__xomcx = builder.call(nfhb__jtjs, [ril__sggj, xel__fei.
                    data, xel__fei.length, xel__fei.kind])
                auf__savgt.f1 = cbx__xomcx
                jtm__gahbw = builder.add(cbx__xomcx, lir.Constant(lir.
                    IntType(64), 1))
                xwmpr__onns.meminfo = context.nrt.meminfo_alloc_aligned(builder
                    , size=jtm__gahbw, align=32)
                xwmpr__onns.data = context.nrt.meminfo_data(builder,
                    xwmpr__onns.meminfo)
                builder.call(nfhb__jtjs, [xwmpr__onns.data, xel__fei.data,
                    xel__fei.length, xel__fei.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    xwmpr__onns.data, [cbx__xomcx]))
        auf__savgt.f0 = xwmpr__onns._getvalue()
        return auf__savgt._getvalue()
    return ckbi__bgz(string_type), codegen


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
        aikj__isp = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        lrkr__dovy = cgutils.get_or_insert_function(builder.module,
            aikj__isp, name='memcmp')
        return builder.call(lrkr__dovy, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    fflhk__geo = n(10)

    def impl(n):
        if n == 0:
            return 1
        ixa__vnk = 0
        if n < 0:
            n = -n
            ixa__vnk += 1
        while n > 0:
            n = n // fflhk__geo
            ixa__vnk += 1
        return ixa__vnk
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
        [wfxbq__iven] = args
        if isinstance(wfxbq__iven, StdStringType):
            return signature(types.float64, wfxbq__iven)
        if wfxbq__iven == string_type:
            return signature(types.float64, wfxbq__iven)


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
    xel__fei = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    aikj__isp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    dtk__cme = cgutils.get_or_insert_function(builder.module, aikj__isp,
        name='init_string_const')
    return builder.call(dtk__cme, [xel__fei.data, xel__fei.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        xgxe__qkwv = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(xgxe__qkwv._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return xgxe__qkwv
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    xel__fei = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return xel__fei.data


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
        ykkhd__dak = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, ykkhd__dak)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        iqhtp__awr, = args
        dnc__jrsn = types.List(string_type)
        otm__myipb = numba.cpython.listobj.ListInstance.allocate(context,
            builder, dnc__jrsn, iqhtp__awr)
        otm__myipb.size = iqhtp__awr
        jydm__xgq = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        jydm__xgq.data = otm__myipb.value
        return jydm__xgq._getvalue()
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
            nzzmr__rkdxg = 0
            meydm__ziw = v
            if meydm__ziw < 0:
                nzzmr__rkdxg = 1
                meydm__ziw = -meydm__ziw
            if meydm__ziw < 1:
                jazg__mol = 1
            else:
                jazg__mol = 1 + int(np.floor(np.log10(meydm__ziw)))
            length = nzzmr__rkdxg + jazg__mol + 1 + 6
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
    aikj__isp = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    dtk__cme = cgutils.get_or_insert_function(builder.module, aikj__isp,
        name='str_to_float64')
    res = builder.call(dtk__cme, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    aikj__isp = lir.FunctionType(lir.FloatType(), [lir.IntType(8).as_pointer()]
        )
    dtk__cme = cgutils.get_or_insert_function(builder.module, aikj__isp,
        name='str_to_float32')
    res = builder.call(dtk__cme, (val,))
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
    xel__fei = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    aikj__isp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    dtk__cme = cgutils.get_or_insert_function(builder.module, aikj__isp,
        name='str_to_int64')
    res = builder.call(dtk__cme, (xel__fei.data, xel__fei.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    xel__fei = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    aikj__isp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    dtk__cme = cgutils.get_or_insert_function(builder.module, aikj__isp,
        name='str_to_uint64')
    res = builder.call(dtk__cme, (xel__fei.data, xel__fei.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        lzs__djdm = ', '.join('e{}'.format(kzq__bwjhn) for kzq__bwjhn in
            range(len(args)))
        if lzs__djdm:
            lzs__djdm += ', '
        ipjo__fws = ', '.join("{} = ''".format(a) for a in kws.keys())
        lfy__ybenk = f'def format_stub(string, {lzs__djdm} {ipjo__fws}):\n'
        lfy__ybenk += '    pass\n'
        tnbmu__fbc = {}
        exec(lfy__ybenk, {}, tnbmu__fbc)
        hpqre__hwm = tnbmu__fbc['format_stub']
        xkd__ccaqu = numba.core.utils.pysignature(hpqre__hwm)
        ufsim__tks = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, ufsim__tks).replace(pysig=xkd__ccaqu)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    ablyt__hpl = pat is not None and len(pat) > 1
    if ablyt__hpl:
        jzz__ixccc = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    otm__myipb = len(arr)
    ajrpb__rzfp = 0
    zgad__uzmab = 0
    for kzq__bwjhn in numba.parfors.parfor.internal_prange(otm__myipb):
        if bodo.libs.array_kernels.isna(arr, kzq__bwjhn):
            continue
        if ablyt__hpl:
            mlfbb__gnnse = jzz__ixccc.split(arr[kzq__bwjhn], maxsplit=n)
        elif pat == '':
            mlfbb__gnnse = [''] + list(arr[kzq__bwjhn]) + ['']
        else:
            mlfbb__gnnse = arr[kzq__bwjhn].split(pat, n)
        ajrpb__rzfp += len(mlfbb__gnnse)
        for s in mlfbb__gnnse:
            zgad__uzmab += bodo.libs.str_arr_ext.get_utf8_size(s)
    hyvyj__wodai = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        otm__myipb, (ajrpb__rzfp, zgad__uzmab), bodo.libs.str_arr_ext.
        string_array_type)
    rwvvo__fpbpw = bodo.libs.array_item_arr_ext.get_offsets(hyvyj__wodai)
    mzwr__lcdf = bodo.libs.array_item_arr_ext.get_null_bitmap(hyvyj__wodai)
    ihkyu__cmr = bodo.libs.array_item_arr_ext.get_data(hyvyj__wodai)
    bydr__dbwb = 0
    for pshc__uzt in numba.parfors.parfor.internal_prange(otm__myipb):
        rwvvo__fpbpw[pshc__uzt] = bydr__dbwb
        if bodo.libs.array_kernels.isna(arr, pshc__uzt):
            bodo.libs.int_arr_ext.set_bit_to_arr(mzwr__lcdf, pshc__uzt, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(mzwr__lcdf, pshc__uzt, 1)
        if ablyt__hpl:
            mlfbb__gnnse = jzz__ixccc.split(arr[pshc__uzt], maxsplit=n)
        elif pat == '':
            mlfbb__gnnse = [''] + list(arr[pshc__uzt]) + ['']
        else:
            mlfbb__gnnse = arr[pshc__uzt].split(pat, n)
        waz__goii = len(mlfbb__gnnse)
        for inlxc__srmu in range(waz__goii):
            s = mlfbb__gnnse[inlxc__srmu]
            ihkyu__cmr[bydr__dbwb] = s
            bydr__dbwb += 1
    rwvvo__fpbpw[otm__myipb] = bydr__dbwb
    return hyvyj__wodai


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                nyhym__pvok = '-0x'
                x = x * -1
            else:
                nyhym__pvok = '0x'
            x = np.uint64(x)
            if x == 0:
                ppj__clg = 1
            else:
                ppj__clg = fast_ceil_log2(x + 1)
                ppj__clg = (ppj__clg + 3) // 4
            length = len(nyhym__pvok) + ppj__clg
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, nyhym__pvok._data,
                len(nyhym__pvok), 1)
            int_to_hex(output, ppj__clg, len(nyhym__pvok), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    xkh__acq = 0 if x & x - 1 == 0 else 1
    hajft__ehc = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    mcp__htgo = 32
    for kzq__bwjhn in range(len(hajft__ehc)):
        zyo__gmml = 0 if x & hajft__ehc[kzq__bwjhn] == 0 else mcp__htgo
        xkh__acq = xkh__acq + zyo__gmml
        x = x >> zyo__gmml
        mcp__htgo = mcp__htgo >> 1
    return xkh__acq


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        ucr__quk = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        aikj__isp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        vbodx__pleu = cgutils.get_or_insert_function(builder.module,
            aikj__isp, name='int_to_hex')
        ocmi__ceog = builder.inttoptr(builder.add(builder.ptrtoint(ucr__quk
            .data, lir.IntType(64)), header_len), lir.IntType(8).as_pointer())
        builder.call(vbodx__pleu, (ocmi__ceog, out_len, int_val))
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
