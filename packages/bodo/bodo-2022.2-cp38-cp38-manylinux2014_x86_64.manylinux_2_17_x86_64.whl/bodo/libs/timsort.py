import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    dwr__uuqhx = hi - lo
    if dwr__uuqhx < 2:
        return
    if dwr__uuqhx < MIN_MERGE:
        ztow__zpdft = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + ztow__zpdft, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    rrg__dzjxm = minRunLength(dwr__uuqhx)
    while True:
        fgqhg__voz = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if fgqhg__voz < rrg__dzjxm:
            sxfvs__jtes = (dwr__uuqhx if dwr__uuqhx <= rrg__dzjxm else
                rrg__dzjxm)
            binarySort(key_arrs, lo, lo + sxfvs__jtes, lo + fgqhg__voz, data)
            fgqhg__voz = sxfvs__jtes
        stackSize = pushRun(stackSize, runBase, runLen, lo, fgqhg__voz)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += fgqhg__voz
        dwr__uuqhx -= fgqhg__voz
        if dwr__uuqhx == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        ofik__dogsx = getitem_arr_tup(key_arrs, start)
        jsix__kfo = getitem_arr_tup(data, start)
        bbkpy__lqc = lo
        sfo__lczl = start
        assert bbkpy__lqc <= sfo__lczl
        while bbkpy__lqc < sfo__lczl:
            uswo__kefcu = bbkpy__lqc + sfo__lczl >> 1
            if ofik__dogsx < getitem_arr_tup(key_arrs, uswo__kefcu):
                sfo__lczl = uswo__kefcu
            else:
                bbkpy__lqc = uswo__kefcu + 1
        assert bbkpy__lqc == sfo__lczl
        n = start - bbkpy__lqc
        copyRange_tup(key_arrs, bbkpy__lqc, key_arrs, bbkpy__lqc + 1, n)
        copyRange_tup(data, bbkpy__lqc, data, bbkpy__lqc + 1, n)
        setitem_arr_tup(key_arrs, bbkpy__lqc, ofik__dogsx)
        setitem_arr_tup(data, bbkpy__lqc, jsix__kfo)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    uzl__tfkfs = lo + 1
    if uzl__tfkfs == hi:
        return 1
    if getitem_arr_tup(key_arrs, uzl__tfkfs) < getitem_arr_tup(key_arrs, lo):
        uzl__tfkfs += 1
        while uzl__tfkfs < hi and getitem_arr_tup(key_arrs, uzl__tfkfs
            ) < getitem_arr_tup(key_arrs, uzl__tfkfs - 1):
            uzl__tfkfs += 1
        reverseRange(key_arrs, lo, uzl__tfkfs, data)
    else:
        uzl__tfkfs += 1
        while uzl__tfkfs < hi and getitem_arr_tup(key_arrs, uzl__tfkfs
            ) >= getitem_arr_tup(key_arrs, uzl__tfkfs - 1):
            uzl__tfkfs += 1
    return uzl__tfkfs - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    ecocm__oyhtq = 0
    while n >= MIN_MERGE:
        ecocm__oyhtq |= n & 1
        n >>= 1
    return n + ecocm__oyhtq


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    tdz__ozza = len(key_arrs[0])
    tmpLength = (tdz__ozza >> 1 if tdz__ozza < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    pbt__vrrc = (5 if tdz__ozza < 120 else 10 if tdz__ozza < 1542 else 19 if
        tdz__ozza < 119151 else 40)
    runBase = np.empty(pbt__vrrc, np.int64)
    runLen = np.empty(pbt__vrrc, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    mpjpf__wnik = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert mpjpf__wnik >= 0
    base1 += mpjpf__wnik
    len1 -= mpjpf__wnik
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    ala__byj = 0
    spkug__hfj = 1
    if key > getitem_arr_tup(arr, base + hint):
        bfb__yvnmx = _len - hint
        while spkug__hfj < bfb__yvnmx and key > getitem_arr_tup(arr, base +
            hint + spkug__hfj):
            ala__byj = spkug__hfj
            spkug__hfj = (spkug__hfj << 1) + 1
            if spkug__hfj <= 0:
                spkug__hfj = bfb__yvnmx
        if spkug__hfj > bfb__yvnmx:
            spkug__hfj = bfb__yvnmx
        ala__byj += hint
        spkug__hfj += hint
    else:
        bfb__yvnmx = hint + 1
        while spkug__hfj < bfb__yvnmx and key <= getitem_arr_tup(arr, base +
            hint - spkug__hfj):
            ala__byj = spkug__hfj
            spkug__hfj = (spkug__hfj << 1) + 1
            if spkug__hfj <= 0:
                spkug__hfj = bfb__yvnmx
        if spkug__hfj > bfb__yvnmx:
            spkug__hfj = bfb__yvnmx
        tmp = ala__byj
        ala__byj = hint - spkug__hfj
        spkug__hfj = hint - tmp
    assert -1 <= ala__byj and ala__byj < spkug__hfj and spkug__hfj <= _len
    ala__byj += 1
    while ala__byj < spkug__hfj:
        huvf__ejh = ala__byj + (spkug__hfj - ala__byj >> 1)
        if key > getitem_arr_tup(arr, base + huvf__ejh):
            ala__byj = huvf__ejh + 1
        else:
            spkug__hfj = huvf__ejh
    assert ala__byj == spkug__hfj
    return spkug__hfj


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    spkug__hfj = 1
    ala__byj = 0
    if key < getitem_arr_tup(arr, base + hint):
        bfb__yvnmx = hint + 1
        while spkug__hfj < bfb__yvnmx and key < getitem_arr_tup(arr, base +
            hint - spkug__hfj):
            ala__byj = spkug__hfj
            spkug__hfj = (spkug__hfj << 1) + 1
            if spkug__hfj <= 0:
                spkug__hfj = bfb__yvnmx
        if spkug__hfj > bfb__yvnmx:
            spkug__hfj = bfb__yvnmx
        tmp = ala__byj
        ala__byj = hint - spkug__hfj
        spkug__hfj = hint - tmp
    else:
        bfb__yvnmx = _len - hint
        while spkug__hfj < bfb__yvnmx and key >= getitem_arr_tup(arr, base +
            hint + spkug__hfj):
            ala__byj = spkug__hfj
            spkug__hfj = (spkug__hfj << 1) + 1
            if spkug__hfj <= 0:
                spkug__hfj = bfb__yvnmx
        if spkug__hfj > bfb__yvnmx:
            spkug__hfj = bfb__yvnmx
        ala__byj += hint
        spkug__hfj += hint
    assert -1 <= ala__byj and ala__byj < spkug__hfj and spkug__hfj <= _len
    ala__byj += 1
    while ala__byj < spkug__hfj:
        huvf__ejh = ala__byj + (spkug__hfj - ala__byj >> 1)
        if key < getitem_arr_tup(arr, base + huvf__ejh):
            spkug__hfj = huvf__ejh
        else:
            ala__byj = huvf__ejh + 1
    assert ala__byj == spkug__hfj
    return spkug__hfj


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        habst__swc = 0
        wxnn__vhsau = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                wxnn__vhsau += 1
                habst__swc = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                habst__swc += 1
                wxnn__vhsau = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not habst__swc | wxnn__vhsau < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            habst__swc = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if habst__swc != 0:
                copyRange_tup(tmp, cursor1, arr, dest, habst__swc)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, habst__swc)
                dest += habst__swc
                cursor1 += habst__swc
                len1 -= habst__swc
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            wxnn__vhsau = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if wxnn__vhsau != 0:
                copyRange_tup(arr, cursor2, arr, dest, wxnn__vhsau)
                copyRange_tup(arr_data, cursor2, arr_data, dest, wxnn__vhsau)
                dest += wxnn__vhsau
                cursor2 += wxnn__vhsau
                len2 -= wxnn__vhsau
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not habst__swc >= MIN_GALLOP | wxnn__vhsau >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        habst__swc = 0
        wxnn__vhsau = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                habst__swc += 1
                wxnn__vhsau = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                wxnn__vhsau += 1
                habst__swc = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not habst__swc | wxnn__vhsau < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            habst__swc = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if habst__swc != 0:
                dest -= habst__swc
                cursor1 -= habst__swc
                len1 -= habst__swc
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, habst__swc)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    habst__swc)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            wxnn__vhsau = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if wxnn__vhsau != 0:
                dest -= wxnn__vhsau
                cursor2 -= wxnn__vhsau
                len2 -= wxnn__vhsau
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, wxnn__vhsau)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    wxnn__vhsau)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not habst__swc >= MIN_GALLOP | wxnn__vhsau >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    hzfc__nro = len(key_arrs[0])
    if tmpLength < minCapacity:
        vlenk__lsgcx = minCapacity
        vlenk__lsgcx |= vlenk__lsgcx >> 1
        vlenk__lsgcx |= vlenk__lsgcx >> 2
        vlenk__lsgcx |= vlenk__lsgcx >> 4
        vlenk__lsgcx |= vlenk__lsgcx >> 8
        vlenk__lsgcx |= vlenk__lsgcx >> 16
        vlenk__lsgcx += 1
        if vlenk__lsgcx < 0:
            vlenk__lsgcx = minCapacity
        else:
            vlenk__lsgcx = min(vlenk__lsgcx, hzfc__nro >> 1)
        tmp = alloc_arr_tup(vlenk__lsgcx, key_arrs)
        tmp_data = alloc_arr_tup(vlenk__lsgcx, data)
        tmpLength = vlenk__lsgcx
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        keoiz__tlwfp = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = keoiz__tlwfp


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    sxd__pfbw = arr_tup.count
    lhylm__bmi = 'def f(arr_tup, lo, hi):\n'
    for i in range(sxd__pfbw):
        lhylm__bmi += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        lhylm__bmi += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        lhylm__bmi += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    lhylm__bmi += '  return\n'
    rvvv__vmo = {}
    exec(lhylm__bmi, {}, rvvv__vmo)
    opjqw__qvhd = rvvv__vmo['f']
    return opjqw__qvhd


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    sxd__pfbw = src_arr_tup.count
    assert sxd__pfbw == dst_arr_tup.count
    lhylm__bmi = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(sxd__pfbw):
        lhylm__bmi += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    lhylm__bmi += '  return\n'
    rvvv__vmo = {}
    exec(lhylm__bmi, {'copyRange': copyRange}, rvvv__vmo)
    nkn__zim = rvvv__vmo['f']
    return nkn__zim


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    sxd__pfbw = src_arr_tup.count
    assert sxd__pfbw == dst_arr_tup.count
    lhylm__bmi = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(sxd__pfbw):
        lhylm__bmi += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    lhylm__bmi += '  return\n'
    rvvv__vmo = {}
    exec(lhylm__bmi, {'copyElement': copyElement}, rvvv__vmo)
    nkn__zim = rvvv__vmo['f']
    return nkn__zim


def getitem_arr_tup(arr_tup, ind):
    hcg__xjys = [arr[ind] for arr in arr_tup]
    return tuple(hcg__xjys)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    sxd__pfbw = arr_tup.count
    lhylm__bmi = 'def f(arr_tup, ind):\n'
    lhylm__bmi += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(sxd__pfbw)]), ',' if sxd__pfbw == 1 else '')
    rvvv__vmo = {}
    exec(lhylm__bmi, {}, rvvv__vmo)
    fgav__xqm = rvvv__vmo['f']
    return fgav__xqm


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, eay__fmghk in zip(arr_tup, val_tup):
        arr[ind] = eay__fmghk


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    sxd__pfbw = arr_tup.count
    lhylm__bmi = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(sxd__pfbw):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            lhylm__bmi += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            lhylm__bmi += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    lhylm__bmi += '  return\n'
    rvvv__vmo = {}
    exec(lhylm__bmi, {}, rvvv__vmo)
    fgav__xqm = rvvv__vmo['f']
    return fgav__xqm


def test():
    import time
    ppjs__wmi = time.time()
    eydx__dawgj = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((eydx__dawgj,), 0, 3, data)
    print('compile time', time.time() - ppjs__wmi)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    mciiz__vni = np.random.ranf(n)
    waor__lzvb = pd.DataFrame({'A': mciiz__vni, 'B': data[0], 'C': data[1]})
    ppjs__wmi = time.time()
    unqfx__pjhlw = waor__lzvb.sort_values('A', inplace=False)
    owf__oouq = time.time()
    sort((mciiz__vni,), 0, n, data)
    print('Bodo', time.time() - owf__oouq, 'Numpy', owf__oouq - ppjs__wmi)
    np.testing.assert_almost_equal(data[0], unqfx__pjhlw.B.values)
    np.testing.assert_almost_equal(data[1], unqfx__pjhlw.C.values)


if __name__ == '__main__':
    test()
