"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        nfzff__tqtta = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(nfzff__tqtta)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        msxpv__ojaw = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, msxpv__ojaw)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        tfmvz__jxad, = args
        fkpox__krtq = signature.return_type
        pwar__dmtz = cgutils.create_struct_proxy(fkpox__krtq)(context, builder)
        pwar__dmtz.obj = tfmvz__jxad
        context.nrt.incref(builder, signature.args[0], tfmvz__jxad)
        return pwar__dmtz._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not isinstance(S, SeriesType) or not (S.data in (string_array_type,
        string_array_split_view_type) or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):

    def impl(S_str):
        S = S_str._obj
        srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(srmfg__mwbez, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n) == -1:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(srmfg__mwbez,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(srmfg__mwbez, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    zmxm__zchm = S_str.stype.data
    if (zmxm__zchm != string_array_split_view_type and zmxm__zchm !=
        string_array_type) and not isinstance(zmxm__zchm, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(zmxm__zchm, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(srmfg__mwbez, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return _str_get_array_impl
    if zmxm__zchm == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(srmfg__mwbez)
            fsg__rsou = 0
            for awxr__quk in numba.parfors.parfor.internal_prange(n):
                oioe__bdhtn, oioe__bdhtn, avjw__kacmr = get_split_view_index(
                    srmfg__mwbez, awxr__quk, i)
                fsg__rsou += avjw__kacmr
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, fsg__rsou)
            for epbg__hjryj in numba.parfors.parfor.internal_prange(n):
                cvjg__kyaq, dxgy__hcff, avjw__kacmr = get_split_view_index(
                    srmfg__mwbez, epbg__hjryj, i)
                if cvjg__kyaq == 0:
                    bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
                    rplw__drx = get_split_view_data_ptr(srmfg__mwbez, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        epbg__hjryj)
                    rplw__drx = get_split_view_data_ptr(srmfg__mwbez,
                        dxgy__hcff)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    epbg__hjryj, rplw__drx, avjw__kacmr)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return _str_get_split_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(srmfg__mwbez)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(srmfg__mwbez, epbg__hjryj
                ) or not len(srmfg__mwbez[epbg__hjryj]) > i >= -len(
                srmfg__mwbez[epbg__hjryj]):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = srmfg__mwbez[epbg__hjryj][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    zmxm__zchm = S_str.stype.data
    if (zmxm__zchm != string_array_split_view_type and zmxm__zchm !=
        ArrayItemArrayType(string_array_type) and zmxm__zchm !=
        string_array_type):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                asgyo__cetft = ugp__zphvb[epbg__hjryj]
                out_arr[epbg__hjryj] = sep.join(asgyo__cetft)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            ggu__goi = re.compile(pat, flags)
            cdh__rdhea = len(srmfg__mwbez)
            out_arr = pre_alloc_string_array(cdh__rdhea, -1)
            for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea
                ):
                if bodo.libs.array_kernels.isna(srmfg__mwbez, epbg__hjryj):
                    out_arr[epbg__hjryj] = ''
                    bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
                    continue
                out_arr[epbg__hjryj] = ggu__goi.sub(repl, srmfg__mwbez[
                    epbg__hjryj])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(srmfg__mwbez)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(srmfg__mwbez, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
                continue
            out_arr[epbg__hjryj] = srmfg__mwbez[epbg__hjryj].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


def is_regex_unsupported(pat):
    znc__ccssc = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(hilve__embrh in pat) for hilve__embrh in znc__ccssc])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    xya__jlzm = re.IGNORECASE.value
    nubyu__ugyi = 'def impl(\n'
    nubyu__ugyi += (
        '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n')
    nubyu__ugyi += '):\n'
    nubyu__ugyi += '  S = S_str._obj\n'
    nubyu__ugyi += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    nubyu__ugyi += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    nubyu__ugyi += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    nubyu__ugyi += '  l = len(arr)\n'
    nubyu__ugyi += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            nubyu__ugyi += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            nubyu__ugyi += """  get_search_regex(arr, case, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    else:
        nubyu__ugyi += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            nubyu__ugyi += '  upper_pat = pat.upper()\n'
        nubyu__ugyi += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        nubyu__ugyi += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        nubyu__ugyi += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        nubyu__ugyi += '      else: \n'
        if is_overload_true(case):
            nubyu__ugyi += '          out_arr[i] = pat in arr[i]\n'
        else:
            nubyu__ugyi += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    nubyu__ugyi += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    vbnv__cxtj = {}
    exec(nubyu__ugyi, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': xya__jlzm, 'get_search_regex':
        get_search_regex}, vbnv__cxtj)
    impl = vbnv__cxtj['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        ggu__goi = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(cdh__rdhea, np.int64)
        for i in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(ggu__goi, ugp__zphvb[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(cdh__rdhea, np.int64)
        for i in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ugp__zphvb[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(cdh__rdhea, np.int64)
        for i in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ugp__zphvb[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'center', inline='always',
    no_unliteral=True)
def overload_str_method_center(S_str, width, fillchar=' '):
    common_validate_padding('center', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                if stop is not None:
                    igr__doh = ugp__zphvb[epbg__hjryj][stop:]
                else:
                    igr__doh = ''
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj][:start
                    ] + repl + igr__doh
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):

        def impl(S_str, repeats):
            S = S_str._obj
            ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            cdh__rdhea = len(ugp__zphvb)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea,
                -1)
            for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea
                ):
                if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                    bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
                else:
                    out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return impl
    elif is_overload_constant_list(repeats):
        krl__cln = get_overload_const_list(repeats)
        zhjf__wrq = all([isinstance(luz__znnzw, int) for luz__znnzw in
            krl__cln])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        zhjf__wrq = True
    else:
        zhjf__wrq = False
    if zhjf__wrq:

        def impl(S_str, repeats):
            S = S_str._obj
            ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
            nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
            ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
            mwvgf__oxkgi = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            cdh__rdhea = len(ugp__zphvb)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea,
                -1)
            for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea
                ):
                if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                    bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
                else:
                    out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj
                        ] * mwvgf__oxkgi[epbg__hjryj]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                ruuo__gdmux, nfzff__tqtta)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


@overload_method(SeriesStrMethodType, 'ljust', inline='always',
    no_unliteral=True)
def overload_str_method_ljust(S_str, width, fillchar=' '):
    common_validate_padding('ljust', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].ljust(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'rjust', inline='always',
    no_unliteral=True)
def overload_str_method_rjust(S_str, width, fillchar=' '):
    common_validate_padding('rjust', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].rjust(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            elif side == 'left':
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)

    def impl(S_str, width):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(cdh__rdhea, -1)
        for epbg__hjryj in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, epbg__hjryj):
                out_arr[epbg__hjryj] = ''
                bodo.libs.array_kernels.setna(out_arr, epbg__hjryj)
            else:
                out_arr[epbg__hjryj] = ugp__zphvb[epbg__hjryj][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(cdh__rdhea)
        for i in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ugp__zphvb[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ugp__zphvb = bodo.hiframes.pd_series_ext.get_series_data(S)
        nfzff__tqtta = bodo.hiframes.pd_series_ext.get_series_name(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        cdh__rdhea = len(ugp__zphvb)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(cdh__rdhea)
        for i in numba.parfors.parfor.internal_prange(cdh__rdhea):
            if bodo.libs.array_kernels.isna(ugp__zphvb, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ugp__zphvb[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, ruuo__gdmux,
            nfzff__tqtta)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    pvb__cti, regex = _get_column_names_from_regex(pat, flags, 'extract')
    lfsna__quv = len(pvb__cti)
    nubyu__ugyi = 'def impl(S_str, pat, flags=0, expand=True):\n'
    nubyu__ugyi += '  regex = re.compile(pat, flags=flags)\n'
    nubyu__ugyi += '  S = S_str._obj\n'
    nubyu__ugyi += (
        '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    nubyu__ugyi += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    nubyu__ugyi += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    nubyu__ugyi += '  numba.parfors.parfor.init_prange()\n'
    nubyu__ugyi += '  n = len(str_arr)\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += (
            '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
            .format(i))
    nubyu__ugyi += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    nubyu__ugyi += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += "          out_arr_{}[j] = ''\n".format(i)
        nubyu__ugyi += (
            '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    nubyu__ugyi += '      else:\n'
    nubyu__ugyi += '          m = regex.search(str_arr[j])\n'
    nubyu__ugyi += '          if m:\n'
    nubyu__ugyi += '            g = m.groups()\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
    nubyu__ugyi += '          else:\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += "            out_arr_{}[j] = ''\n".format(i)
        nubyu__ugyi += (
            '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    if is_overload_false(expand) and regex.groups == 1:
        nfzff__tqtta = "'{}'".format(list(regex.groupindex.keys()).pop()
            ) if len(regex.groupindex.keys()) > 0 else 'name'
        nubyu__ugyi += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(nfzff__tqtta))
        vbnv__cxtj = {}
        exec(nubyu__ugyi, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, vbnv__cxtj)
        impl = vbnv__cxtj['impl']
        return impl
    pww__oiwk = ', '.join('out_arr_{}'.format(i) for i in range(lfsna__quv))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(nubyu__ugyi, pvb__cti,
        pww__oiwk, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    pvb__cti, oioe__bdhtn = _get_column_names_from_regex(pat, flags,
        'extractall')
    lfsna__quv = len(pvb__cti)
    rvb__ceqgt = isinstance(S_str.stype.index, StringIndexType)
    nubyu__ugyi = 'def impl(S_str, pat, flags=0):\n'
    nubyu__ugyi += '  regex = re.compile(pat, flags=flags)\n'
    nubyu__ugyi += '  S = S_str._obj\n'
    nubyu__ugyi += (
        '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    nubyu__ugyi += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    nubyu__ugyi += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    nubyu__ugyi += (
        '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    nubyu__ugyi += (
        '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n')
    nubyu__ugyi += '  numba.parfors.parfor.init_prange()\n'
    nubyu__ugyi += '  n = len(str_arr)\n'
    nubyu__ugyi += '  out_n_l = [0]\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += '  num_chars_{} = 0\n'.format(i)
    if rvb__ceqgt:
        nubyu__ugyi += '  index_num_chars = 0\n'
    nubyu__ugyi += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    if rvb__ceqgt:
        nubyu__ugyi += '      index_num_chars += get_utf8_size(index_arr[i])\n'
    nubyu__ugyi += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
    nubyu__ugyi += '          continue\n'
    nubyu__ugyi += '      m = regex.findall(str_arr[i])\n'
    nubyu__ugyi += '      out_n_l[0] += len(m)\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += '      l_{} = 0\n'.format(i)
    nubyu__ugyi += '      for s in m:\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += '        l_{} += get_utf8_size(s{})\n'.format(i, 
            '[{}]'.format(i) if lfsna__quv > 1 else '')
    for i in range(lfsna__quv):
        nubyu__ugyi += '      num_chars_{0} += l_{0}\n'.format(i)
    nubyu__ugyi += (
        '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
        )
    for i in range(lfsna__quv):
        nubyu__ugyi += (
            """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
            .format(i))
    if rvb__ceqgt:
        nubyu__ugyi += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
    else:
        nubyu__ugyi += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
    nubyu__ugyi += '  out_match_arr = np.empty(out_n, np.int64)\n'
    nubyu__ugyi += '  out_ind = 0\n'
    nubyu__ugyi += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    nubyu__ugyi += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    nubyu__ugyi += '          continue\n'
    nubyu__ugyi += '      m = regex.findall(str_arr[j])\n'
    nubyu__ugyi += '      for k, s in enumerate(m):\n'
    for i in range(lfsna__quv):
        nubyu__ugyi += (
            """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
            .format(i, '[{}]'.format(i) if lfsna__quv > 1 else ''))
    nubyu__ugyi += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
    nubyu__ugyi += (
        '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
        )
    nubyu__ugyi += '        out_ind += 1\n'
    nubyu__ugyi += (
        '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n')
    nubyu__ugyi += "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n"
    pww__oiwk = ', '.join('out_arr_{}'.format(i) for i in range(lfsna__quv))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(nubyu__ugyi, pvb__cti,
        pww__oiwk, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    mcs__exsjk = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    pvb__cti = [mcs__exsjk.get(1 + i, i) for i in range(regex.groups)]
    return pvb__cti, regex


def create_str2str_methods_overload(func_name):
    if func_name in ['lstrip', 'rstrip', 'strip']:
        nubyu__ugyi = 'def f(S_str, to_strip=None):\n'
    else:
        nubyu__ugyi = 'def f(S_str):\n'
    nubyu__ugyi += '    S = S_str._obj\n'
    nubyu__ugyi += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    nubyu__ugyi += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    nubyu__ugyi += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    nubyu__ugyi += '    numba.parfors.parfor.init_prange()\n'
    nubyu__ugyi += '    n = len(str_arr)\n'
    if func_name in ('capitalize', 'lower', 'swapcase', 'title', 'upper'):
        nubyu__ugyi += '    num_chars = num_total_chars(str_arr)\n'
    else:
        nubyu__ugyi += '    num_chars = -1\n'
    nubyu__ugyi += (
        '    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)\n'
        )
    nubyu__ugyi += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    nubyu__ugyi += '        if bodo.libs.array_kernels.isna(str_arr, j):\n'
    nubyu__ugyi += '            out_arr[j] = ""\n'
    nubyu__ugyi += '            bodo.libs.array_kernels.setna(out_arr, j)\n'
    nubyu__ugyi += '        else:\n'
    if func_name in ['lstrip', 'rstrip', 'strip']:
        nubyu__ugyi += ('            out_arr[j] = str_arr[j].{}(to_strip)\n'
            .format(func_name))
    else:
        nubyu__ugyi += '            out_arr[j] = str_arr[j].{}()\n'.format(
            func_name)
    nubyu__ugyi += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    vbnv__cxtj = {}
    exec(nubyu__ugyi, {'bodo': bodo, 'numba': numba, 'num_total_chars':
        bodo.libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size}, vbnv__cxtj)
    qva__sbuc = vbnv__cxtj['f']
    if func_name in ['lstrip', 'rstrip', 'strip']:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            return qva__sbuc
        return overload_strip_method
    else:

        def overload_str2str_methods(S_str):
            return qva__sbuc
        return overload_str2str_methods


def create_str2bool_methods_overload(func_name):

    def overload_str2bool_methods(S_str):
        nubyu__ugyi = 'def f(S_str):\n'
        nubyu__ugyi += '    S = S_str._obj\n'
        nubyu__ugyi += (
            '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        nubyu__ugyi += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        nubyu__ugyi += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        nubyu__ugyi += '    numba.parfors.parfor.init_prange()\n'
        nubyu__ugyi += '    l = len(str_arr)\n'
        nubyu__ugyi += (
            '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        nubyu__ugyi += (
            '    for i in numba.parfors.parfor.internal_prange(l):\n')
        nubyu__ugyi += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
        nubyu__ugyi += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        nubyu__ugyi += '        else:\n'
        nubyu__ugyi += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'
            .format(func_name))
        nubyu__ugyi += '    return bodo.hiframes.pd_series_ext.init_series(\n'
        nubyu__ugyi += '      out_arr,index, name)\n'
        vbnv__cxtj = {}
        exec(nubyu__ugyi, {'bodo': bodo, 'numba': numba, 'np': np}, vbnv__cxtj)
        qva__sbuc = vbnv__cxtj['f']
        return qva__sbuc
    return overload_str2bool_methods


def _install_str2str_methods():
    for oua__xid in bodo.hiframes.pd_series_ext.str2str_methods:
        ypbz__ujc = create_str2str_methods_overload(oua__xid)
        overload_method(SeriesStrMethodType, oua__xid, inline='always',
            no_unliteral=True)(ypbz__ujc)


def _install_str2bool_methods():
    for oua__xid in bodo.hiframes.pd_series_ext.str2bool_methods:
        ypbz__ujc = create_str2bool_methods_overload(oua__xid)
        overload_method(SeriesStrMethodType, oua__xid, inline='always',
            no_unliteral=True)(ypbz__ujc)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        nfzff__tqtta = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(nfzff__tqtta)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        msxpv__ojaw = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, msxpv__ojaw)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        tfmvz__jxad, = args
        kmjw__ekgq = signature.return_type
        ina__tbg = cgutils.create_struct_proxy(kmjw__ekgq)(context, builder)
        ina__tbg.obj = tfmvz__jxad
        context.nrt.incref(builder, signature.args[0], tfmvz__jxad)
        return ina__tbg._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        srmfg__mwbez = bodo.hiframes.pd_series_ext.get_series_data(S)
        ruuo__gdmux = bodo.hiframes.pd_series_ext.get_series_index(S)
        nfzff__tqtta = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(srmfg__mwbez),
            ruuo__gdmux, nfzff__tqtta)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for cux__oemd in unsupported_cat_attrs:
        olyi__bvo = 'Series.cat.' + cux__oemd
        overload_attribute(SeriesCatMethodType, cux__oemd)(
            create_unsupported_overload(olyi__bvo))
    for uljr__seaip in unsupported_cat_methods:
        olyi__bvo = 'Series.cat.' + uljr__seaip
        overload_method(SeriesCatMethodType, uljr__seaip)(
            create_unsupported_overload(olyi__bvo))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'cat', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for uljr__seaip in unsupported_str_methods:
        olyi__bvo = 'Series.str.' + uljr__seaip
        overload_method(SeriesStrMethodType, uljr__seaip)(
            create_unsupported_overload(olyi__bvo))


_install_strseries_unsupported()
