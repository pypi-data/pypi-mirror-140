"""implementations of rolling window functions (sequential and parallel)
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, register_jitable
import bodo
from bodo.libs.distributed_api import Reduce_Type
from bodo.utils.typing import BodoError, get_overload_const_func, get_overload_const_str, is_const_func_type, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true
from bodo.utils.utils import unliteral_all
supported_rolling_funcs = ('sum', 'mean', 'var', 'std', 'count', 'median',
    'min', 'max', 'cov', 'corr', 'apply')
unsupported_rolling_methods = ['skew', 'kurt', 'aggregate', 'quantile', 'sem']


def rolling_fixed(arr, win):
    return arr


def rolling_variable(arr, on_arr, win):
    return arr


def rolling_cov(arr, arr2, win):
    return arr


def rolling_corr(arr, arr2, win):
    return arr


@infer_global(rolling_cov)
@infer_global(rolling_corr)
class RollingCovType(AbstractTemplate):

    def generic(self, args, kws):
        arr = args[0]
        vha__bedy = arr.copy(dtype=types.float64)
        return signature(vha__bedy, *unliteral_all(args))


@lower_builtin(rolling_corr, types.VarArg(types.Any))
@lower_builtin(rolling_cov, types.VarArg(types.Any))
def lower_rolling_corr_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@overload(rolling_fixed, no_unliteral=True)
def overload_rolling_fixed(arr, index_arr, win, minp, center, fname, raw=
    True, parallel=False):
    assert is_overload_constant_bool(raw
        ), 'raw argument should be constant bool'
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    izea__yes = get_overload_const_str(fname)
    if izea__yes not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (fixed window) function {}'.format
            (izea__yes))
    if izea__yes in ('median', 'min', 'max'):
        ihepp__otku = 'def kernel_func(A):\n'
        ihepp__otku += '  if np.isnan(A).sum() != 0: return np.nan\n'
        ihepp__otku += '  return np.{}(A)\n'.format(izea__yes)
        jzjc__icp = {}
        exec(ihepp__otku, {'np': np}, jzjc__icp)
        kernel_func = register_jitable(jzjc__icp['kernel_func'])
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        izea__yes]
    return (lambda arr, index_arr, win, minp, center, fname, raw=True,
        parallel=False: roll_fixed_linear_generic(arr, win, minp, center,
        parallel, init_kernel, add_kernel, remove_kernel, calc_kernel))


@overload(rolling_variable, no_unliteral=True)
def overload_rolling_variable(arr, on_arr, index_arr, win, minp, center,
    fname, raw=True, parallel=False):
    assert is_overload_constant_bool(raw)
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    izea__yes = get_overload_const_str(fname)
    if izea__yes not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (variable window) function {}'.
            format(izea__yes))
    if izea__yes in ('median', 'min', 'max'):
        ihepp__otku = 'def kernel_func(A):\n'
        ihepp__otku += '  arr  = dropna(A)\n'
        ihepp__otku += '  if len(arr) == 0: return np.nan\n'
        ihepp__otku += '  return np.{}(arr)\n'.format(izea__yes)
        jzjc__icp = {}
        exec(ihepp__otku, {'np': np, 'dropna': _dropna}, jzjc__icp)
        kernel_func = register_jitable(jzjc__icp['kernel_func'])
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        izea__yes]
    return (lambda arr, on_arr, index_arr, win, minp, center, fname, raw=
        True, parallel=False: roll_var_linear_generic(arr, on_arr, win,
        minp, center, parallel, init_kernel, add_kernel, remove_kernel,
        calc_kernel))


def _get_apply_func(f_type):
    func = get_overload_const_func(f_type, None)
    return bodo.compiler.udf_jit(func)


comm_border_tag = 22


@register_jitable
def roll_fixed_linear_generic(in_arr, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data(in_arr, win, minp, center, rank,
                n_pes, init_data, add_obs, remove_obs, calc_out)
        ggckw__htwf = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            ywi__vcsau) = ggckw__htwf
    output, data = roll_fixed_linear_generic_seq(in_arr, win, minp, center,
        init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(ywi__vcsau, True)
            for dnue__qzav in range(0, halo_size):
                data = add_obs(r_recv_buff[dnue__qzav], *data)
                rtc__acw = in_arr[N + dnue__qzav - win]
                data = remove_obs(rtc__acw, *data)
                output[N + dnue__qzav - offset] = calc_out(minp, *data)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            data = init_data()
            for dnue__qzav in range(0, halo_size):
                data = add_obs(l_recv_buff[dnue__qzav], *data)
            for dnue__qzav in range(0, win - 1):
                data = add_obs(in_arr[dnue__qzav], *data)
                if dnue__qzav > offset:
                    rtc__acw = l_recv_buff[dnue__qzav - offset - 1]
                    data = remove_obs(rtc__acw, *data)
                if dnue__qzav >= offset:
                    output[dnue__qzav - offset] = calc_out(minp, *data)
    return output


@register_jitable
def roll_fixed_linear_generic_seq(in_arr, win, minp, center, init_data,
    add_obs, remove_obs, calc_out):
    data = init_data()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    output = np.empty(N, dtype=np.float64)
    xhly__xdba = max(minp, 1) - 1
    xhly__xdba = min(xhly__xdba, N)
    for dnue__qzav in range(0, xhly__xdba):
        data = add_obs(in_arr[dnue__qzav], *data)
        if dnue__qzav >= offset:
            output[dnue__qzav - offset] = calc_out(minp, *data)
    for dnue__qzav in range(xhly__xdba, N):
        val = in_arr[dnue__qzav]
        data = add_obs(val, *data)
        if dnue__qzav > win - 1:
            rtc__acw = in_arr[dnue__qzav - win]
            data = remove_obs(rtc__acw, *data)
        output[dnue__qzav - offset] = calc_out(minp, *data)
    wqyt__mcae = data
    for dnue__qzav in range(N, N + offset):
        if dnue__qzav > win - 1:
            rtc__acw = in_arr[dnue__qzav - win]
            data = remove_obs(rtc__acw, *data)
        output[dnue__qzav - offset] = calc_out(minp, *data)
    return output, wqyt__mcae


def roll_fixed_apply(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    pass


@overload(roll_fixed_apply, no_unliteral=True)
def overload_roll_fixed_apply(in_arr, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_fixed_apply_impl


def roll_fixed_apply_impl(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    index_arr = fix_index_arr(index_arr)
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_apply(in_arr, index_arr, win, minp,
                center, rank, n_pes, kernel_func, raw)
        ggckw__htwf = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            ywi__vcsau) = ggckw__htwf
        if raw == False:
            gct__sfbxz = _border_icomm(index_arr, rank, n_pes, halo_size, 
                True, center)
            (l_recv_buff_idx, r_recv_buff_idx, ewjeb__ante, oynoi__gxmqi,
                goqaz__svot, idquv__rsd) = gct__sfbxz
    output = roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
        kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if raw == False:
            _border_send_wait(oynoi__gxmqi, ewjeb__ante, rank, n_pes, True,
                center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(ywi__vcsau, True)
            if raw == False:
                bodo.libs.distributed_api.wait(idquv__rsd, True)
            recv_right_compute(output, in_arr, index_arr, N, win, minp,
                offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            if raw == False:
                bodo.libs.distributed_api.wait(goqaz__svot, True)
            recv_left_compute(output, in_arr, index_arr, win, minp, offset,
                l_recv_buff, l_recv_buff_idx, kernel_func, raw)
    return output


def recv_right_compute(output, in_arr, index_arr, N, win, minp, offset,
    r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_right_compute, no_unliteral=True)
def overload_recv_right_compute(output, in_arr, index_arr, N, win, minp,
    offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, N, win, minp, offset,
            r_recv_buff, r_recv_buff_idx, kernel_func, raw):
            wqyt__mcae = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
            rntj__nulin = 0
            for dnue__qzav in range(max(N - offset, 0), N):
                data = wqyt__mcae[rntj__nulin:rntj__nulin + win]
                if win - np.isnan(data).sum() < minp:
                    output[dnue__qzav] = np.nan
                else:
                    output[dnue__qzav] = kernel_func(data)
                rntj__nulin += 1
        return impl

    def impl_series(output, in_arr, index_arr, N, win, minp, offset,
        r_recv_buff, r_recv_buff_idx, kernel_func, raw):
        wqyt__mcae = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
        fijqu__mdoti = np.concatenate((index_arr[N - win + 1:],
            r_recv_buff_idx))
        rntj__nulin = 0
        for dnue__qzav in range(max(N - offset, 0), N):
            data = wqyt__mcae[rntj__nulin:rntj__nulin + win]
            if win - np.isnan(data).sum() < minp:
                output[dnue__qzav] = np.nan
            else:
                output[dnue__qzav] = kernel_func(pd.Series(data,
                    fijqu__mdoti[rntj__nulin:rntj__nulin + win]))
            rntj__nulin += 1
    return impl_series


def recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_left_compute, no_unliteral=True)
def overload_recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, win, minp, offset, l_recv_buff,
            l_recv_buff_idx, kernel_func, raw):
            wqyt__mcae = np.concatenate((l_recv_buff, in_arr[:win - 1]))
            for dnue__qzav in range(0, win - offset - 1):
                data = wqyt__mcae[dnue__qzav:dnue__qzav + win]
                if win - np.isnan(data).sum() < minp:
                    output[dnue__qzav] = np.nan
                else:
                    output[dnue__qzav] = kernel_func(data)
        return impl

    def impl_series(output, in_arr, index_arr, win, minp, offset,
        l_recv_buff, l_recv_buff_idx, kernel_func, raw):
        wqyt__mcae = np.concatenate((l_recv_buff, in_arr[:win - 1]))
        fijqu__mdoti = np.concatenate((l_recv_buff_idx, index_arr[:win - 1]))
        for dnue__qzav in range(0, win - offset - 1):
            data = wqyt__mcae[dnue__qzav:dnue__qzav + win]
            if win - np.isnan(data).sum() < minp:
                output[dnue__qzav] = np.nan
            else:
                output[dnue__qzav] = kernel_func(pd.Series(data,
                    fijqu__mdoti[dnue__qzav:dnue__qzav + win]))
    return impl_series


def roll_fixed_apply_seq(in_arr, index_arr, win, minp, center, kernel_func,
    raw=True):
    pass


@overload(roll_fixed_apply_seq, no_unliteral=True)
def overload_roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
    kernel_func, raw=True):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"

    def roll_fixed_apply_seq_impl(in_arr, index_arr, win, minp, center,
        kernel_func, raw=True):
        N = len(in_arr)
        output = np.empty(N, dtype=np.float64)
        offset = (win - 1) // 2 if center else 0
        for dnue__qzav in range(0, N):
            start = max(dnue__qzav - win + 1 + offset, 0)
            end = min(dnue__qzav + 1 + offset, N)
            data = in_arr[start:end]
            if end - start - np.isnan(data).sum() < minp:
                output[dnue__qzav] = np.nan
            else:
                output[dnue__qzav] = apply_func(kernel_func, data,
                    index_arr, start, end, raw)
        return output
    return roll_fixed_apply_seq_impl


def apply_func(kernel_func, data, index_arr, start, end, raw):
    return kernel_func(data)


@overload(apply_func, no_unliteral=True)
def overload_apply_func(kernel_func, data, index_arr, start, end, raw):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"
    if is_overload_true(raw):
        return (lambda kernel_func, data, index_arr, start, end, raw:
            kernel_func(data))
    return lambda kernel_func, data, index_arr, start, end, raw: kernel_func(pd
        .Series(data, index_arr[start:end]))


def fix_index_arr(A):
    return A


@overload(fix_index_arr)
def overload_fix_index_arr(A):
    if is_overload_none(A):
        return lambda A: np.zeros(3)
    return lambda A: A


def get_offset_nanos(w):
    out = status = 0
    try:
        out = pd.tseries.frequencies.to_offset(w).nanos
    except:
        status = 1
    return out, status


def offset_to_nanos(w):
    return w


@overload(offset_to_nanos)
def overload_offset_to_nanos(w):
    if isinstance(w, types.Integer):
        return lambda w: w

    def impl(w):
        with numba.objmode(out='int64', status='int64'):
            out, status = get_offset_nanos(w)
        if status != 0:
            raise ValueError('Invalid offset value')
        return out
    return impl


@register_jitable
def roll_var_linear_generic(in_arr, on_arr_dt, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable(in_arr, on_arr, win, minp,
                rank, n_pes, init_data, add_obs, remove_obs, calc_out)
        ggckw__htwf = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, fbypf__iaa, l_recv_req,
            pzso__kzpq) = ggckw__htwf
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start,
        end, init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(fbypf__iaa, fbypf__iaa, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(pzso__kzpq, True)
            num_zero_starts = 0
            for dnue__qzav in range(0, N):
                if start[dnue__qzav] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            data = init_data()
            for yqt__rbj in range(recv_starts[0], len(l_recv_t_buff)):
                data = add_obs(l_recv_buff[yqt__rbj], *data)
            if right_closed:
                data = add_obs(in_arr[0], *data)
            output[0] = calc_out(minp, *data)
            for dnue__qzav in range(1, num_zero_starts):
                s = recv_starts[dnue__qzav]
                qyxak__kvfam = end[dnue__qzav]
                for yqt__rbj in range(recv_starts[dnue__qzav - 1], s):
                    data = remove_obs(l_recv_buff[yqt__rbj], *data)
                for yqt__rbj in range(end[dnue__qzav - 1], qyxak__kvfam):
                    data = add_obs(in_arr[yqt__rbj], *data)
                output[dnue__qzav] = calc_out(minp, *data)
    return output


@register_jitable(cache=True)
def _get_var_recv_starts(on_arr, l_recv_t_buff, num_zero_starts, win):
    recv_starts = np.zeros(num_zero_starts, np.int64)
    halo_size = len(l_recv_t_buff)
    hvl__nkh = cast_dt64_arr_to_int(on_arr)
    left_closed = False
    iqj__btiid = hvl__nkh[0] - win
    if left_closed:
        iqj__btiid -= 1
    recv_starts[0] = halo_size
    for yqt__rbj in range(0, halo_size):
        if l_recv_t_buff[yqt__rbj] > iqj__btiid:
            recv_starts[0] = yqt__rbj
            break
    for dnue__qzav in range(1, num_zero_starts):
        iqj__btiid = hvl__nkh[dnue__qzav] - win
        if left_closed:
            iqj__btiid -= 1
        recv_starts[dnue__qzav] = halo_size
        for yqt__rbj in range(recv_starts[dnue__qzav - 1], halo_size):
            if l_recv_t_buff[yqt__rbj] > iqj__btiid:
                recv_starts[dnue__qzav] = yqt__rbj
                break
    return recv_starts


@register_jitable
def roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start, end,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    output = np.empty(N, np.float64)
    data = init_data()
    for yqt__rbj in range(start[0], end[0]):
        data = add_obs(in_arr[yqt__rbj], *data)
    output[0] = calc_out(minp, *data)
    for dnue__qzav in range(1, N):
        s = start[dnue__qzav]
        qyxak__kvfam = end[dnue__qzav]
        for yqt__rbj in range(start[dnue__qzav - 1], s):
            data = remove_obs(in_arr[yqt__rbj], *data)
        for yqt__rbj in range(end[dnue__qzav - 1], qyxak__kvfam):
            data = add_obs(in_arr[yqt__rbj], *data)
        output[dnue__qzav] = calc_out(minp, *data)
    return output


def roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    pass


@overload(roll_variable_apply, no_unliteral=True)
def overload_roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_variable_apply_impl


def roll_variable_apply_impl(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    index_arr = fix_index_arr(index_arr)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable_apply(in_arr, on_arr,
                index_arr, win, minp, rank, n_pes, kernel_func, raw)
        ggckw__htwf = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, fbypf__iaa, l_recv_req,
            pzso__kzpq) = ggckw__htwf
        if raw == False:
            gct__sfbxz = _border_icomm_var(index_arr, on_arr, rank, n_pes, win)
            (l_recv_buff_idx, pxak__rfkc, oynoi__gxmqi, fet__fzpdn,
                goqaz__svot, rvd__pmhzo) = gct__sfbxz
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
        start, end, kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(fbypf__iaa, fbypf__iaa, rank, n_pes, True, False)
        if raw == False:
            _border_send_wait(oynoi__gxmqi, oynoi__gxmqi, rank, n_pes, True,
                False)
            _border_send_wait(fet__fzpdn, fet__fzpdn, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(pzso__kzpq, True)
            if raw == False:
                bodo.libs.distributed_api.wait(goqaz__svot, True)
                bodo.libs.distributed_api.wait(rvd__pmhzo, True)
            num_zero_starts = 0
            for dnue__qzav in range(0, N):
                if start[dnue__qzav] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            recv_left_var_compute(output, in_arr, index_arr,
                num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx,
                minp, kernel_func, raw)
    return output


def recv_left_var_compute(output, in_arr, index_arr, num_zero_starts,
    recv_starts, l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
    pass


@overload(recv_left_var_compute)
def overload_recv_left_var_compute(output, in_arr, index_arr,
    num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx, minp,
    kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, num_zero_starts, recv_starts,
            l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
            for dnue__qzav in range(0, num_zero_starts):
                als__eoke = recv_starts[dnue__qzav]
                mpa__edr = np.concatenate((l_recv_buff[als__eoke:], in_arr[
                    :dnue__qzav + 1]))
                if len(mpa__edr) - np.isnan(mpa__edr).sum() >= minp:
                    output[dnue__qzav] = kernel_func(mpa__edr)
                else:
                    output[dnue__qzav] = np.nan
        return impl

    def impl_series(output, in_arr, index_arr, num_zero_starts, recv_starts,
        l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
        for dnue__qzav in range(0, num_zero_starts):
            als__eoke = recv_starts[dnue__qzav]
            mpa__edr = np.concatenate((l_recv_buff[als__eoke:], in_arr[:
                dnue__qzav + 1]))
            oirh__ylre = np.concatenate((l_recv_buff_idx[als__eoke:],
                index_arr[:dnue__qzav + 1]))
            if len(mpa__edr) - np.isnan(mpa__edr).sum() >= minp:
                output[dnue__qzav] = kernel_func(pd.Series(mpa__edr,
                    oirh__ylre))
            else:
                output[dnue__qzav] = np.nan
    return impl_series


def roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp, start,
    end, kernel_func, raw):
    pass


@overload(roll_variable_apply_seq)
def overload_roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):
        return roll_variable_apply_seq_impl
    return roll_variable_apply_seq_impl_series


def roll_variable_apply_seq_impl(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for dnue__qzav in range(0, N):
        s = start[dnue__qzav]
        qyxak__kvfam = end[dnue__qzav]
        data = in_arr[s:qyxak__kvfam]
        if qyxak__kvfam - s - np.isnan(data).sum() >= minp:
            output[dnue__qzav] = kernel_func(data)
        else:
            output[dnue__qzav] = np.nan
    return output


def roll_variable_apply_seq_impl_series(in_arr, on_arr, index_arr, win,
    minp, start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for dnue__qzav in range(0, N):
        s = start[dnue__qzav]
        qyxak__kvfam = end[dnue__qzav]
        data = in_arr[s:qyxak__kvfam]
        if qyxak__kvfam - s - np.isnan(data).sum() >= minp:
            output[dnue__qzav] = kernel_func(pd.Series(data, index_arr[s:
                qyxak__kvfam]))
        else:
            output[dnue__qzav] = np.nan
    return output


@register_jitable(cache=True)
def _build_indexer(on_arr, N, win, left_closed, right_closed):
    hvl__nkh = cast_dt64_arr_to_int(on_arr)
    start = np.empty(N, np.int64)
    end = np.empty(N, np.int64)
    start[0] = 0
    if right_closed:
        end[0] = 1
    else:
        end[0] = 0
    for dnue__qzav in range(1, N):
        atb__fagjm = hvl__nkh[dnue__qzav]
        iqj__btiid = hvl__nkh[dnue__qzav] - win
        if left_closed:
            iqj__btiid -= 1
        start[dnue__qzav] = dnue__qzav
        for yqt__rbj in range(start[dnue__qzav - 1], dnue__qzav):
            if hvl__nkh[yqt__rbj] > iqj__btiid:
                start[dnue__qzav] = yqt__rbj
                break
        if hvl__nkh[end[dnue__qzav - 1]] <= atb__fagjm:
            end[dnue__qzav] = dnue__qzav + 1
        else:
            end[dnue__qzav] = end[dnue__qzav - 1]
        if not right_closed:
            end[dnue__qzav] -= 1
    return start, end


@register_jitable
def init_data_sum():
    return 0, 0.0


@register_jitable
def add_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
    return nobs, sum_x


@register_jitable
def remove_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
    return nobs, sum_x


@register_jitable
def calc_sum(minp, nobs, sum_x):
    return sum_x if nobs >= minp else np.nan


@register_jitable
def init_data_mean():
    return 0, 0.0, 0


@register_jitable
def add_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
        if val < 0:
            neg_ct += 1
    return nobs, sum_x, neg_ct


@register_jitable
def remove_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
        if val < 0:
            neg_ct -= 1
    return nobs, sum_x, neg_ct


@register_jitable
def calc_mean(minp, nobs, sum_x, neg_ct):
    if nobs >= minp:
        jxs__xjzad = sum_x / nobs
        if neg_ct == 0 and jxs__xjzad < 0.0:
            jxs__xjzad = 0
        elif neg_ct == nobs and jxs__xjzad > 0.0:
            jxs__xjzad = 0
    else:
        jxs__xjzad = np.nan
    return jxs__xjzad


@register_jitable
def init_data_var():
    return 0, 0.0, 0.0


@register_jitable
def add_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs += 1
        dte__hysi = val - mean_x
        mean_x += dte__hysi / nobs
        ssqdm_x += (nobs - 1) * dte__hysi ** 2 / nobs
    return nobs, mean_x, ssqdm_x


@register_jitable
def remove_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs -= 1
        if nobs != 0:
            dte__hysi = val - mean_x
            mean_x -= dte__hysi / nobs
            ssqdm_x -= (nobs + 1) * dte__hysi ** 2 / nobs
        else:
            mean_x = 0.0
            ssqdm_x = 0.0
    return nobs, mean_x, ssqdm_x


@register_jitable
def calc_var(minp, nobs, mean_x, ssqdm_x):
    egap__ukg = 1.0
    jxs__xjzad = np.nan
    if nobs >= minp and nobs > egap__ukg:
        if nobs == 1:
            jxs__xjzad = 0.0
        else:
            jxs__xjzad = ssqdm_x / (nobs - egap__ukg)
            if jxs__xjzad < 0.0:
                jxs__xjzad = 0.0
    return jxs__xjzad


@register_jitable
def calc_std(minp, nobs, mean_x, ssqdm_x):
    wetco__vfmp = calc_var(minp, nobs, mean_x, ssqdm_x)
    return np.sqrt(wetco__vfmp)


@register_jitable
def init_data_count():
    return 0.0,


@register_jitable
def add_count(val, count_x):
    if not np.isnan(val):
        count_x += 1.0
    return count_x,


@register_jitable
def remove_count(val, count_x):
    if not np.isnan(val):
        count_x -= 1.0
    return count_x,


@register_jitable
def calc_count(minp, count_x):
    return count_x


@register_jitable
def calc_count_var(minp, count_x):
    return count_x if count_x >= minp else np.nan


linear_kernels = {'sum': (init_data_sum, add_sum, remove_sum, calc_sum),
    'mean': (init_data_mean, add_mean, remove_mean, calc_mean), 'var': (
    init_data_var, add_var, remove_var, calc_var), 'std': (init_data_var,
    add_var, remove_var, calc_std), 'count': (init_data_count, add_count,
    remove_count, calc_count)}


def shift():
    return


@overload(shift, jit_options={'cache': True})
def shift_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return shift_impl


def shift_impl(in_arr, shift, parallel):
    N = len(in_arr)
    output = alloc_shift(N, in_arr, (-1,))
    send_right = shift > 0
    send_left = shift <= 0
    is_parallel_str = False
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_shift(in_arr, shift, rank, n_pes)
        ggckw__htwf = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            ywi__vcsau) = ggckw__htwf
        if send_right and is_str_binary_array(in_arr):
            is_parallel_str = True
            shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
                l_recv_req, l_recv_buff, output)
    shift_seq(in_arr, shift, output, is_parallel_str)
    if parallel:
        if send_right:
            if not is_str_binary_array(in_arr):
                shift_left_recv(r_send_req, l_send_req, rank, n_pes,
                    halo_size, l_recv_req, l_recv_buff, output)
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(ywi__vcsau, True)
                for dnue__qzav in range(0, halo_size):
                    if bodo.libs.array_kernels.isna(r_recv_buff, dnue__qzav):
                        bodo.libs.array_kernels.setna(output, N - halo_size +
                            dnue__qzav)
                        continue
                    output[N - halo_size + dnue__qzav] = r_recv_buff[dnue__qzav
                        ]
    return output


@register_jitable(cache=True)
def shift_seq(in_arr, shift, output, is_parallel_str=False):
    N = len(in_arr)
    ygl__rfcyp = 1 if shift > 0 else -1
    shift = ygl__rfcyp * min(abs(shift), N)
    if shift > 0 and (not is_parallel_str or bodo.get_rank() == 0):
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    start = max(shift, 0)
    end = min(N, N + shift)
    for dnue__qzav in range(start, end):
        if bodo.libs.array_kernels.isna(in_arr, dnue__qzav - shift):
            bodo.libs.array_kernels.setna(output, dnue__qzav)
            continue
        output[dnue__qzav] = in_arr[dnue__qzav - shift]
    if shift < 0:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    return output


@register_jitable
def shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
    l_recv_req, l_recv_buff, output):
    _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
    if rank != 0:
        bodo.libs.distributed_api.wait(l_recv_req, True)
        for dnue__qzav in range(0, halo_size):
            if bodo.libs.array_kernels.isna(l_recv_buff, dnue__qzav):
                bodo.libs.array_kernels.setna(output, dnue__qzav)
                continue
            output[dnue__qzav] = l_recv_buff[dnue__qzav]


def is_str_binary_array(arr):
    return False


@overload(is_str_binary_array)
def overload_is_str_binary_array(arr):
    if arr in [bodo.string_array_type, bodo.binary_array_type]:
        return lambda arr: True
    return lambda arr: False


def is_supported_shift_array_type(arr_type):
    return isinstance(arr_type, types.Array) and (isinstance(arr_type.dtype,
        types.Number) or arr_type.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]) or isinstance(arr_type, (bodo.IntegerArrayType,
        bodo.DecimalArrayType)) or arr_type in (bodo.boolean_array, bodo.
        datetime_date_array_type, bodo.string_array_type, bodo.
        binary_array_type)


def pct_change():
    return


@overload(pct_change, jit_options={'cache': True})
def pct_change_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return pct_change_impl


def pct_change_impl(in_arr, shift, parallel):
    N = len(in_arr)
    send_right = shift > 0
    send_left = shift <= 0
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_pct_change(in_arr, shift, rank, n_pes)
        ggckw__htwf = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            ywi__vcsau) = ggckw__htwf
    output = pct_change_seq(in_arr, shift)
    if parallel:
        if send_right:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
            if rank != 0:
                bodo.libs.distributed_api.wait(l_recv_req, True)
                for dnue__qzav in range(0, halo_size):
                    slhe__cqw = l_recv_buff[dnue__qzav]
                    output[dnue__qzav] = (in_arr[dnue__qzav] - slhe__cqw
                        ) / slhe__cqw
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(ywi__vcsau, True)
                for dnue__qzav in range(0, halo_size):
                    slhe__cqw = r_recv_buff[dnue__qzav]
                    output[N - halo_size + dnue__qzav] = (in_arr[N -
                        halo_size + dnue__qzav] - slhe__cqw) / slhe__cqw
    return output


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_first_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[0]
    assert isinstance(arr.dtype, types.Float)
    thyri__myt = np.nan
    if arr.dtype == types.float32:
        thyri__myt = np.float32('nan')

    def impl(arr):
        for dnue__qzav in range(len(arr)):
            if not bodo.libs.array_kernels.isna(arr, dnue__qzav):
                return arr[dnue__qzav]
        return thyri__myt
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_last_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[-1]
    assert isinstance(arr.dtype, types.Float)
    thyri__myt = np.nan
    if arr.dtype == types.float32:
        thyri__myt = np.float32('nan')

    def impl(arr):
        zfala__ewmu = len(arr)
        for dnue__qzav in range(len(arr)):
            rntj__nulin = zfala__ewmu - dnue__qzav - 1
            if not bodo.libs.array_kernels.isna(arr, rntj__nulin):
                return arr[rntj__nulin]
        return thyri__myt
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_one_from_arr_dtype(arr):
    one = arr.dtype(1)
    return lambda arr: one


@register_jitable(cache=True)
def pct_change_seq(in_arr, shift):
    N = len(in_arr)
    output = alloc_pct_change(N, in_arr)
    ygl__rfcyp = 1 if shift > 0 else -1
    shift = ygl__rfcyp * min(abs(shift), N)
    if shift > 0:
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    else:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    if shift > 0:
        gpcnu__lfqw = get_first_non_na(in_arr[:shift])
        tcegi__dnrfo = get_last_non_na(in_arr[:shift])
    else:
        gpcnu__lfqw = get_last_non_na(in_arr[:-shift])
        tcegi__dnrfo = get_first_non_na(in_arr[:-shift])
    one = get_one_from_arr_dtype(output)
    start = max(shift, 0)
    end = min(N, N + shift)
    for dnue__qzav in range(start, end):
        slhe__cqw = in_arr[dnue__qzav - shift]
        if np.isnan(slhe__cqw):
            slhe__cqw = gpcnu__lfqw
        else:
            gpcnu__lfqw = slhe__cqw
        val = in_arr[dnue__qzav]
        if np.isnan(val):
            val = tcegi__dnrfo
        else:
            tcegi__dnrfo = val
        output[dnue__qzav] = val / slhe__cqw - one
    return output


@register_jitable(cache=True)
def _border_icomm(in_arr, rank, n_pes, halo_size, send_right=True,
    send_left=False):
    gxszi__fdlm = np.int32(comm_border_tag)
    l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    r_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    if send_right and rank != n_pes - 1:
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            halo_size, np.int32(rank + 1), gxszi__fdlm, True)
    if send_right and rank != 0:
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, halo_size,
            np.int32(rank - 1), gxszi__fdlm, True)
    if send_left and rank != 0:
        l_send_req = bodo.libs.distributed_api.isend(in_arr[:halo_size],
            halo_size, np.int32(rank - 1), gxszi__fdlm, True)
    if send_left and rank != n_pes - 1:
        ywi__vcsau = bodo.libs.distributed_api.irecv(r_recv_buff, halo_size,
            np.int32(rank + 1), gxszi__fdlm, True)
    return (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
        ywi__vcsau)


@register_jitable(cache=True)
def _border_icomm_var(in_arr, on_arr, rank, n_pes, win_size):
    gxszi__fdlm = np.int32(comm_border_tag)
    N = len(on_arr)
    halo_size = N
    end = on_arr[-1]
    for yqt__rbj in range(-2, -N, -1):
        dxu__tmg = on_arr[yqt__rbj]
        if end - dxu__tmg >= win_size:
            halo_size = -yqt__rbj
            break
    if rank != n_pes - 1:
        bodo.libs.distributed_api.send(halo_size, np.int32(rank + 1),
            gxszi__fdlm)
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), gxszi__fdlm, True)
        fbypf__iaa = bodo.libs.distributed_api.isend(on_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), gxszi__fdlm, True)
    if rank != 0:
        halo_size = bodo.libs.distributed_api.recv(np.int64, np.int32(rank -
            1), gxszi__fdlm)
        l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr)
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, np.int32(
            halo_size), np.int32(rank - 1), gxszi__fdlm, True)
        l_recv_t_buff = np.empty(halo_size, np.int64)
        pzso__kzpq = bodo.libs.distributed_api.irecv(l_recv_t_buff, np.
            int32(halo_size), np.int32(rank - 1), gxszi__fdlm, True)
    return (l_recv_buff, l_recv_t_buff, r_send_req, fbypf__iaa, l_recv_req,
        pzso__kzpq)


@register_jitable
def _border_send_wait(r_send_req, l_send_req, rank, n_pes, right, left):
    if right and rank != n_pes - 1:
        bodo.libs.distributed_api.wait(r_send_req, True)
    if left and rank != 0:
        bodo.libs.distributed_api.wait(l_send_req, True)


@register_jitable
def _is_small_for_parallel(N, halo_size):
    eqf__zqyf = bodo.libs.distributed_api.dist_reduce(int(N <= 2 *
        halo_size + 1), np.int32(Reduce_Type.Sum.value))
    return eqf__zqyf != 0


@register_jitable
def _handle_small_data(in_arr, win, minp, center, rank, n_pes, init_data,
    add_obs, remove_obs, calc_out):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        ghhcw__opl, gtz__orii = roll_fixed_linear_generic_seq(vkn__pko, win,
            minp, center, init_data, add_obs, remove_obs, calc_out)
    else:
        ghhcw__opl = np.empty(ztsp__qku, np.float64)
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


@register_jitable
def _handle_small_data_apply(in_arr, index_arr, win, minp, center, rank,
    n_pes, kernel_func, raw=True):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    jwsy__djayw = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        ghhcw__opl = roll_fixed_apply_seq(vkn__pko, jwsy__djayw, win, minp,
            center, kernel_func, raw)
    else:
        ghhcw__opl = np.empty(ztsp__qku, np.float64)
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


def bcast_n_chars_if_str_binary_arr(arr):
    pass


@overload(bcast_n_chars_if_str_binary_arr)
def overload_bcast_n_chars_if_str_binary_arr(arr):
    if arr in [bodo.binary_array_type, bodo.string_array_type]:

        def impl(arr):
            return bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.
                libs.str_arr_ext.num_total_chars(arr)))
        return impl
    return lambda arr: -1


@register_jitable
def _handle_small_data_shift(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        ghhcw__opl = alloc_shift(len(vkn__pko), vkn__pko, (-1,))
        shift_seq(vkn__pko, shift, ghhcw__opl)
        lysmj__nigv = bcast_n_chars_if_str_binary_arr(ghhcw__opl)
    else:
        lysmj__nigv = bcast_n_chars_if_str_binary_arr(in_arr)
        ghhcw__opl = alloc_shift(ztsp__qku, in_arr, (lysmj__nigv,))
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


@register_jitable
def _handle_small_data_pct_change(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        ghhcw__opl = pct_change_seq(vkn__pko, shift)
    else:
        ghhcw__opl = alloc_pct_change(ztsp__qku, in_arr)
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


def cast_dt64_arr_to_int(arr):
    return arr


@infer_global(cast_dt64_arr_to_int)
class DtArrToIntType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        assert args[0] == types.Array(types.NPDatetime('ns'), 1, 'C') or args[0
            ] == types.Array(types.int64, 1, 'C')
        return signature(types.Array(types.int64, 1, 'C'), *args)


@lower_builtin(cast_dt64_arr_to_int, types.Array(types.NPDatetime('ns'), 1,
    'C'))
@lower_builtin(cast_dt64_arr_to_int, types.Array(types.int64, 1, 'C'))
def lower_cast_dt64_arr_to_int(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@register_jitable
def _is_small_for_parallel_variable(on_arr, win_size):
    if len(on_arr) < 2:
        ltho__vfhfb = 1
    else:
        start = on_arr[0]
        end = on_arr[-1]
        ncze__hbbeo = end - start
        ltho__vfhfb = int(ncze__hbbeo <= win_size)
    eqf__zqyf = bodo.libs.distributed_api.dist_reduce(ltho__vfhfb, np.int32
        (Reduce_Type.Sum.value))
    return eqf__zqyf != 0


@register_jitable
def _handle_small_data_variable(in_arr, on_arr, win, minp, rank, n_pes,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    nkmh__uiis = bodo.libs.distributed_api.gatherv(on_arr)
    if rank == 0:
        start, end = _build_indexer(nkmh__uiis, ztsp__qku, win, False, True)
        ghhcw__opl = roll_var_linear_generic_seq(vkn__pko, nkmh__uiis, win,
            minp, start, end, init_data, add_obs, remove_obs, calc_out)
    else:
        ghhcw__opl = np.empty(ztsp__qku, np.float64)
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


@register_jitable
def _handle_small_data_variable_apply(in_arr, on_arr, index_arr, win, minp,
    rank, n_pes, kernel_func, raw):
    N = len(in_arr)
    ztsp__qku = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vkn__pko = bodo.libs.distributed_api.gatherv(in_arr)
    nkmh__uiis = bodo.libs.distributed_api.gatherv(on_arr)
    jwsy__djayw = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        start, end = _build_indexer(nkmh__uiis, ztsp__qku, win, False, True)
        ghhcw__opl = roll_variable_apply_seq(vkn__pko, nkmh__uiis,
            jwsy__djayw, win, minp, start, end, kernel_func, raw)
    else:
        ghhcw__opl = np.empty(ztsp__qku, np.float64)
    bodo.libs.distributed_api.bcast(ghhcw__opl)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return ghhcw__opl[start:end]


@register_jitable(cache=True)
def _dropna(arr):
    kewls__qcrr = len(arr)
    qmu__oreu = kewls__qcrr - np.isnan(arr).sum()
    A = np.empty(qmu__oreu, arr.dtype)
    yjxe__llngj = 0
    for dnue__qzav in range(kewls__qcrr):
        val = arr[dnue__qzav]
        if not np.isnan(val):
            A[yjxe__llngj] = val
            yjxe__llngj += 1
    return A


def alloc_shift(n, A, s=None):
    return np.empty(n, A.dtype)


@overload(alloc_shift, no_unliteral=True)
def alloc_shift_overload(n, A, s=None):
    if not isinstance(A, types.Array):
        return lambda n, A, s=None: bodo.utils.utils.alloc_type(n, A, s)
    if isinstance(A.dtype, types.Integer):
        return lambda n, A, s=None: np.empty(n, np.float64)
    return lambda n, A, s=None: np.empty(n, A.dtype)


def alloc_pct_change(n, A):
    return np.empty(n, A.dtype)


@overload(alloc_pct_change, no_unliteral=True)
def alloc_pct_change_overload(n, A):
    if isinstance(A.dtype, types.Integer):
        return lambda n, A: np.empty(n, np.float64)
    return lambda n, A: np.empty(n, A.dtype)


def prep_values(A):
    return A.astype('float64')


@overload(prep_values, no_unliteral=True)
def prep_values_overload(A):
    if A == types.Array(types.float64, 1, 'C'):
        return lambda A: A
    return lambda A: A.astype(np.float64)


@register_jitable
def _validate_roll_fixed_args(win, minp):
    if win < 0:
        raise ValueError('window must be non-negative')
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if minp > win:
        raise ValueError('min_periods must be <= window')


@register_jitable
def _validate_roll_var_args(minp, center):
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if center:
        raise NotImplementedError(
            'rolling: center is not implemented for datetimelike and offset based windows'
            )
