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
        mmc__uogih = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(mmc__uogih)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tpgut__yvdnz = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, tpgut__yvdnz)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        rysbo__bgtg, = args
        xppd__mjqg = signature.return_type
        rwwv__qspw = cgutils.create_struct_proxy(xppd__mjqg)(context, builder)
        rwwv__qspw.obj = rysbo__bgtg
        context.nrt.incref(builder, signature.args[0], rysbo__bgtg)
        return rwwv__qspw._getvalue()
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
        cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(cvrjc__bgbky, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
            cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(cvrjc__bgbky,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(cvrjc__bgbky, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    oysuq__ldddv = S_str.stype.data
    if (oysuq__ldddv != string_array_split_view_type and oysuq__ldddv !=
        string_array_type) and not isinstance(oysuq__ldddv, ArrayItemArrayType
        ):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(oysuq__ldddv, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(cvrjc__bgbky, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
        return _str_get_array_impl
    if oysuq__ldddv == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(cvrjc__bgbky)
            atukz__yxx = 0
            for auxn__uvjj in numba.parfors.parfor.internal_prange(n):
                ivvd__enj, ivvd__enj, vacn__mmoko = get_split_view_index(
                    cvrjc__bgbky, auxn__uvjj, i)
                atukz__yxx += vacn__mmoko
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, atukz__yxx)
            for ubqx__tdsd in numba.parfors.parfor.internal_prange(n):
                hmjr__emwa, qlf__qhqcx, vacn__mmoko = get_split_view_index(
                    cvrjc__bgbky, ubqx__tdsd, i)
                if hmjr__emwa == 0:
                    bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
                    ahik__khgnl = get_split_view_data_ptr(cvrjc__bgbky, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        ubqx__tdsd)
                    ahik__khgnl = get_split_view_data_ptr(cvrjc__bgbky,
                        qlf__qhqcx)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    ubqx__tdsd, ahik__khgnl, vacn__mmoko)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
        return _str_get_split_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(cvrjc__bgbky)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(cvrjc__bgbky, ubqx__tdsd
                ) or not len(cvrjc__bgbky[ubqx__tdsd]) > i >= -len(cvrjc__bgbky
                [ubqx__tdsd]):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = cvrjc__bgbky[ubqx__tdsd][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    oysuq__ldddv = S_str.stype.data
    if (oysuq__ldddv != string_array_split_view_type and oysuq__ldddv !=
        ArrayItemArrayType(string_array_type) and oysuq__ldddv !=
        string_array_type):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                sds__dmvk = ryr__gne[ubqx__tdsd]
                out_arr[ubqx__tdsd] = sep.join(sds__dmvk)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
            cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            pprn__qscf = re.compile(pat, flags)
            enxif__nuybe = len(cvrjc__bgbky)
            out_arr = pre_alloc_string_array(enxif__nuybe, -1)
            for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe
                ):
                if bodo.libs.array_kernels.isna(cvrjc__bgbky, ubqx__tdsd):
                    out_arr[ubqx__tdsd] = ''
                    bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
                    continue
                out_arr[ubqx__tdsd] = pprn__qscf.sub(repl, cvrjc__bgbky[
                    ubqx__tdsd])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(cvrjc__bgbky)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(enxif__nuybe, -1)
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(cvrjc__bgbky, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
                continue
            out_arr[ubqx__tdsd] = cvrjc__bgbky[ubqx__tdsd].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


def is_regex_unsupported(pat):
    rigjq__lyd = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(khrsv__estz in pat) for khrsv__estz in rigjq__lyd])
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
    umm__qywp = re.IGNORECASE.value
    vjmz__vhd = 'def impl(\n'
    vjmz__vhd += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    vjmz__vhd += '):\n'
    vjmz__vhd += '  S = S_str._obj\n'
    vjmz__vhd += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    vjmz__vhd += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    vjmz__vhd += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    vjmz__vhd += '  l = len(arr)\n'
    vjmz__vhd += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            vjmz__vhd += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            vjmz__vhd += """  get_search_regex(arr, case, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    else:
        vjmz__vhd += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            vjmz__vhd += '  upper_pat = pat.upper()\n'
        vjmz__vhd += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        vjmz__vhd += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        vjmz__vhd += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        vjmz__vhd += '      else: \n'
        if is_overload_true(case):
            vjmz__vhd += '          out_arr[i] = pat in arr[i]\n'
        else:
            vjmz__vhd += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    vjmz__vhd += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ube__dyo = {}
    exec(vjmz__vhd, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': umm__qywp, 'get_search_regex':
        get_search_regex}, ube__dyo)
    impl = ube__dyo['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        pprn__qscf = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(enxif__nuybe, np.int64)
        for i in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(pprn__qscf, ryr__gne[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(enxif__nuybe, np.int64)
        for i in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ryr__gne[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(enxif__nuybe, np.int64)
        for i in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ryr__gne[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'center', inline='always',
    no_unliteral=True)
def overload_str_method_center(S_str, width, fillchar=' '):
    common_validate_padding('center', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                if stop is not None:
                    ityd__ieez = ryr__gne[ubqx__tdsd][stop:]
                else:
                    ityd__ieez = ''
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd][:start
                    ] + repl + ityd__ieez
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):

        def impl(S_str, repeats):
            S = S_str._obj
            ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            enxif__nuybe = len(ryr__gne)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe
                , -1)
            for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe
                ):
                if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                    bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
                else:
                    out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
        return impl
    elif is_overload_constant_list(repeats):
        ecb__nex = get_overload_const_list(repeats)
        hhy__dtdei = all([isinstance(pguq__xsu, int) for pguq__xsu in ecb__nex]
            )
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        hhy__dtdei = True
    else:
        hhy__dtdei = False
    if hhy__dtdei:

        def impl(S_str, repeats):
            S = S_str._obj
            ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
            mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
            bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
            frx__gxap = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            enxif__nuybe = len(ryr__gne)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe
                , -1)
            for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe
                ):
                if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                    bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
                else:
                    out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd] * frx__gxap[
                        ubqx__tdsd]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].ljust(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'rjust', inline='always',
    no_unliteral=True)
def overload_str_method_rjust(S_str, width, fillchar=' '):
    common_validate_padding('rjust', width, fillchar)

    def impl(S_str, width, fillchar=' '):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].rjust(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            elif side == 'left':
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)

    def impl(S_str, width):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(enxif__nuybe, -1
            )
        for ubqx__tdsd in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, ubqx__tdsd):
                out_arr[ubqx__tdsd] = ''
                bodo.libs.array_kernels.setna(out_arr, ubqx__tdsd)
            else:
                out_arr[ubqx__tdsd] = ryr__gne[ubqx__tdsd][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(enxif__nuybe)
        for i in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ryr__gne[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ryr__gne = bodo.hiframes.pd_series_ext.get_series_data(S)
        mmc__uogih = bodo.hiframes.pd_series_ext.get_series_name(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        enxif__nuybe = len(ryr__gne)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(enxif__nuybe)
        for i in numba.parfors.parfor.internal_prange(enxif__nuybe):
            if bodo.libs.array_kernels.isna(ryr__gne, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ryr__gne[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr,
            bhgmp__ucgjv, mmc__uogih)
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
    tqnw__mxwue, regex = _get_column_names_from_regex(pat, flags, 'extract')
    dug__unpla = len(tqnw__mxwue)
    vjmz__vhd = 'def impl(S_str, pat, flags=0, expand=True):\n'
    vjmz__vhd += '  regex = re.compile(pat, flags=flags)\n'
    vjmz__vhd += '  S = S_str._obj\n'
    vjmz__vhd += '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    vjmz__vhd += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    vjmz__vhd += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    vjmz__vhd += '  numba.parfors.parfor.init_prange()\n'
    vjmz__vhd += '  n = len(str_arr)\n'
    for i in range(dug__unpla):
        vjmz__vhd += (
            '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
            .format(i))
    vjmz__vhd += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    vjmz__vhd += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    for i in range(dug__unpla):
        vjmz__vhd += "          out_arr_{}[j] = ''\n".format(i)
        vjmz__vhd += (
            '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    vjmz__vhd += '      else:\n'
    vjmz__vhd += '          m = regex.search(str_arr[j])\n'
    vjmz__vhd += '          if m:\n'
    vjmz__vhd += '            g = m.groups()\n'
    for i in range(dug__unpla):
        vjmz__vhd += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
    vjmz__vhd += '          else:\n'
    for i in range(dug__unpla):
        vjmz__vhd += "            out_arr_{}[j] = ''\n".format(i)
        vjmz__vhd += (
            '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
            format(i))
    if is_overload_false(expand) and regex.groups == 1:
        mmc__uogih = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        vjmz__vhd += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(mmc__uogih))
        ube__dyo = {}
        exec(vjmz__vhd, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, ube__dyo)
        impl = ube__dyo['impl']
        return impl
    aszi__azh = ', '.join('out_arr_{}'.format(i) for i in range(dug__unpla))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(vjmz__vhd, tqnw__mxwue,
        aszi__azh, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    tqnw__mxwue, ivvd__enj = _get_column_names_from_regex(pat, flags,
        'extractall')
    dug__unpla = len(tqnw__mxwue)
    nanwd__fkpd = isinstance(S_str.stype.index, StringIndexType)
    vjmz__vhd = 'def impl(S_str, pat, flags=0):\n'
    vjmz__vhd += '  regex = re.compile(pat, flags=flags)\n'
    vjmz__vhd += '  S = S_str._obj\n'
    vjmz__vhd += '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    vjmz__vhd += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    vjmz__vhd += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    vjmz__vhd += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    vjmz__vhd += (
        '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n')
    vjmz__vhd += '  numba.parfors.parfor.init_prange()\n'
    vjmz__vhd += '  n = len(str_arr)\n'
    vjmz__vhd += '  out_n_l = [0]\n'
    for i in range(dug__unpla):
        vjmz__vhd += '  num_chars_{} = 0\n'.format(i)
    if nanwd__fkpd:
        vjmz__vhd += '  index_num_chars = 0\n'
    vjmz__vhd += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    if nanwd__fkpd:
        vjmz__vhd += '      index_num_chars += get_utf8_size(index_arr[i])\n'
    vjmz__vhd += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
    vjmz__vhd += '          continue\n'
    vjmz__vhd += '      m = regex.findall(str_arr[i])\n'
    vjmz__vhd += '      out_n_l[0] += len(m)\n'
    for i in range(dug__unpla):
        vjmz__vhd += '      l_{} = 0\n'.format(i)
    vjmz__vhd += '      for s in m:\n'
    for i in range(dug__unpla):
        vjmz__vhd += '        l_{} += get_utf8_size(s{})\n'.format(i, 
            '[{}]'.format(i) if dug__unpla > 1 else '')
    for i in range(dug__unpla):
        vjmz__vhd += '      num_chars_{0} += l_{0}\n'.format(i)
    vjmz__vhd += (
        '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
        )
    for i in range(dug__unpla):
        vjmz__vhd += (
            """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
            .format(i))
    if nanwd__fkpd:
        vjmz__vhd += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
    else:
        vjmz__vhd += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
    vjmz__vhd += '  out_match_arr = np.empty(out_n, np.int64)\n'
    vjmz__vhd += '  out_ind = 0\n'
    vjmz__vhd += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    vjmz__vhd += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
    vjmz__vhd += '          continue\n'
    vjmz__vhd += '      m = regex.findall(str_arr[j])\n'
    vjmz__vhd += '      for k, s in enumerate(m):\n'
    for i in range(dug__unpla):
        vjmz__vhd += (
            '        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})\n'
            .format(i, '[{}]'.format(i) if dug__unpla > 1 else ''))
    vjmz__vhd += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
    vjmz__vhd += (
        '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
        )
    vjmz__vhd += '        out_ind += 1\n'
    vjmz__vhd += (
        '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n')
    vjmz__vhd += "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n"
    aszi__azh = ', '.join('out_arr_{}'.format(i) for i in range(dug__unpla))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(vjmz__vhd, tqnw__mxwue,
        aszi__azh, 'out_index', extra_globals={'get_utf8_size':
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
    mxpv__mlg = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    tqnw__mxwue = [mxpv__mlg.get(1 + i, i) for i in range(regex.groups)]
    return tqnw__mxwue, regex


def create_str2str_methods_overload(func_name):
    if func_name in ['lstrip', 'rstrip', 'strip']:
        vjmz__vhd = 'def f(S_str, to_strip=None):\n'
    else:
        vjmz__vhd = 'def f(S_str):\n'
    vjmz__vhd += '    S = S_str._obj\n'
    vjmz__vhd += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    vjmz__vhd += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    vjmz__vhd += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    vjmz__vhd += '    numba.parfors.parfor.init_prange()\n'
    vjmz__vhd += '    n = len(str_arr)\n'
    if func_name in ('capitalize', 'lower', 'swapcase', 'title', 'upper'):
        vjmz__vhd += '    num_chars = num_total_chars(str_arr)\n'
    else:
        vjmz__vhd += '    num_chars = -1\n'
    vjmz__vhd += (
        '    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)\n'
        )
    vjmz__vhd += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    vjmz__vhd += '        if bodo.libs.array_kernels.isna(str_arr, j):\n'
    vjmz__vhd += '            out_arr[j] = ""\n'
    vjmz__vhd += '            bodo.libs.array_kernels.setna(out_arr, j)\n'
    vjmz__vhd += '        else:\n'
    if func_name in ['lstrip', 'rstrip', 'strip']:
        vjmz__vhd += ('            out_arr[j] = str_arr[j].{}(to_strip)\n'.
            format(func_name))
    else:
        vjmz__vhd += '            out_arr[j] = str_arr[j].{}()\n'.format(
            func_name)
    vjmz__vhd += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ube__dyo = {}
    exec(vjmz__vhd, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size}, ube__dyo)
    rpch__gpmt = ube__dyo['f']
    if func_name in ['lstrip', 'rstrip', 'strip']:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            return rpch__gpmt
        return overload_strip_method
    else:

        def overload_str2str_methods(S_str):
            return rpch__gpmt
        return overload_str2str_methods


def create_str2bool_methods_overload(func_name):

    def overload_str2bool_methods(S_str):
        vjmz__vhd = 'def f(S_str):\n'
        vjmz__vhd += '    S = S_str._obj\n'
        vjmz__vhd += (
            '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        vjmz__vhd += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        vjmz__vhd += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        vjmz__vhd += '    numba.parfors.parfor.init_prange()\n'
        vjmz__vhd += '    l = len(str_arr)\n'
        vjmz__vhd += (
            '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        vjmz__vhd += '    for i in numba.parfors.parfor.internal_prange(l):\n'
        vjmz__vhd += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
        vjmz__vhd += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        vjmz__vhd += '        else:\n'
        vjmz__vhd += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'
            .format(func_name))
        vjmz__vhd += '    return bodo.hiframes.pd_series_ext.init_series(\n'
        vjmz__vhd += '      out_arr,index, name)\n'
        ube__dyo = {}
        exec(vjmz__vhd, {'bodo': bodo, 'numba': numba, 'np': np}, ube__dyo)
        rpch__gpmt = ube__dyo['f']
        return rpch__gpmt
    return overload_str2bool_methods


def _install_str2str_methods():
    for wbww__bld in bodo.hiframes.pd_series_ext.str2str_methods:
        dipyt__kjvf = create_str2str_methods_overload(wbww__bld)
        overload_method(SeriesStrMethodType, wbww__bld, inline='always',
            no_unliteral=True)(dipyt__kjvf)


def _install_str2bool_methods():
    for wbww__bld in bodo.hiframes.pd_series_ext.str2bool_methods:
        dipyt__kjvf = create_str2bool_methods_overload(wbww__bld)
        overload_method(SeriesStrMethodType, wbww__bld, inline='always',
            no_unliteral=True)(dipyt__kjvf)


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
        mmc__uogih = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(mmc__uogih)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tpgut__yvdnz = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, tpgut__yvdnz)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        rysbo__bgtg, = args
        syfp__fayq = signature.return_type
        aiqu__xpe = cgutils.create_struct_proxy(syfp__fayq)(context, builder)
        aiqu__xpe.obj = rysbo__bgtg
        context.nrt.incref(builder, signature.args[0], rysbo__bgtg)
        return aiqu__xpe._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        cvrjc__bgbky = bodo.hiframes.pd_series_ext.get_series_data(S)
        bhgmp__ucgjv = bodo.hiframes.pd_series_ext.get_series_index(S)
        mmc__uogih = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(cvrjc__bgbky),
            bhgmp__ucgjv, mmc__uogih)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for nnao__xydmv in unsupported_cat_attrs:
        tsi__yojqe = 'Series.cat.' + nnao__xydmv
        overload_attribute(SeriesCatMethodType, nnao__xydmv)(
            create_unsupported_overload(tsi__yojqe))
    for etm__bjdl in unsupported_cat_methods:
        tsi__yojqe = 'Series.cat.' + etm__bjdl
        overload_method(SeriesCatMethodType, etm__bjdl)(
            create_unsupported_overload(tsi__yojqe))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'cat', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for etm__bjdl in unsupported_str_methods:
        tsi__yojqe = 'Series.str.' + etm__bjdl
        overload_method(SeriesStrMethodType, etm__bjdl)(
            create_unsupported_overload(tsi__yojqe))


_install_strseries_unsupported()
