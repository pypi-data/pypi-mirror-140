import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    qhb__bbv = hi - lo
    if qhb__bbv < 2:
        return
    if qhb__bbv < MIN_MERGE:
        fqgzg__xquj = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + fqgzg__xquj, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    tcu__wmvjh = minRunLength(qhb__bbv)
    while True:
        zcgvk__qki = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if zcgvk__qki < tcu__wmvjh:
            hid__phgqm = qhb__bbv if qhb__bbv <= tcu__wmvjh else tcu__wmvjh
            binarySort(key_arrs, lo, lo + hid__phgqm, lo + zcgvk__qki, data)
            zcgvk__qki = hid__phgqm
        stackSize = pushRun(stackSize, runBase, runLen, lo, zcgvk__qki)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += zcgvk__qki
        qhb__bbv -= zcgvk__qki
        if qhb__bbv == 0:
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
        glauj__grt = getitem_arr_tup(key_arrs, start)
        dsc__jfd = getitem_arr_tup(data, start)
        fzzxg__ovyr = lo
        mirj__dmx = start
        assert fzzxg__ovyr <= mirj__dmx
        while fzzxg__ovyr < mirj__dmx:
            nqss__ynxed = fzzxg__ovyr + mirj__dmx >> 1
            if glauj__grt < getitem_arr_tup(key_arrs, nqss__ynxed):
                mirj__dmx = nqss__ynxed
            else:
                fzzxg__ovyr = nqss__ynxed + 1
        assert fzzxg__ovyr == mirj__dmx
        n = start - fzzxg__ovyr
        copyRange_tup(key_arrs, fzzxg__ovyr, key_arrs, fzzxg__ovyr + 1, n)
        copyRange_tup(data, fzzxg__ovyr, data, fzzxg__ovyr + 1, n)
        setitem_arr_tup(key_arrs, fzzxg__ovyr, glauj__grt)
        setitem_arr_tup(data, fzzxg__ovyr, dsc__jfd)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    mdkbt__ews = lo + 1
    if mdkbt__ews == hi:
        return 1
    if getitem_arr_tup(key_arrs, mdkbt__ews) < getitem_arr_tup(key_arrs, lo):
        mdkbt__ews += 1
        while mdkbt__ews < hi and getitem_arr_tup(key_arrs, mdkbt__ews
            ) < getitem_arr_tup(key_arrs, mdkbt__ews - 1):
            mdkbt__ews += 1
        reverseRange(key_arrs, lo, mdkbt__ews, data)
    else:
        mdkbt__ews += 1
        while mdkbt__ews < hi and getitem_arr_tup(key_arrs, mdkbt__ews
            ) >= getitem_arr_tup(key_arrs, mdkbt__ews - 1):
            mdkbt__ews += 1
    return mdkbt__ews - lo


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
    xvcp__onzqb = 0
    while n >= MIN_MERGE:
        xvcp__onzqb |= n & 1
        n >>= 1
    return n + xvcp__onzqb


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    qsoik__apt = len(key_arrs[0])
    tmpLength = (qsoik__apt >> 1 if qsoik__apt < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    ibv__tjv = (5 if qsoik__apt < 120 else 10 if qsoik__apt < 1542 else 19 if
        qsoik__apt < 119151 else 40)
    runBase = np.empty(ibv__tjv, np.int64)
    runLen = np.empty(ibv__tjv, np.int64)
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
    qixj__bgsm = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert qixj__bgsm >= 0
    base1 += qixj__bgsm
    len1 -= qixj__bgsm
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
    lwd__dadsi = 0
    uxdm__yei = 1
    if key > getitem_arr_tup(arr, base + hint):
        cxnz__raf = _len - hint
        while uxdm__yei < cxnz__raf and key > getitem_arr_tup(arr, base +
            hint + uxdm__yei):
            lwd__dadsi = uxdm__yei
            uxdm__yei = (uxdm__yei << 1) + 1
            if uxdm__yei <= 0:
                uxdm__yei = cxnz__raf
        if uxdm__yei > cxnz__raf:
            uxdm__yei = cxnz__raf
        lwd__dadsi += hint
        uxdm__yei += hint
    else:
        cxnz__raf = hint + 1
        while uxdm__yei < cxnz__raf and key <= getitem_arr_tup(arr, base +
            hint - uxdm__yei):
            lwd__dadsi = uxdm__yei
            uxdm__yei = (uxdm__yei << 1) + 1
            if uxdm__yei <= 0:
                uxdm__yei = cxnz__raf
        if uxdm__yei > cxnz__raf:
            uxdm__yei = cxnz__raf
        tmp = lwd__dadsi
        lwd__dadsi = hint - uxdm__yei
        uxdm__yei = hint - tmp
    assert -1 <= lwd__dadsi and lwd__dadsi < uxdm__yei and uxdm__yei <= _len
    lwd__dadsi += 1
    while lwd__dadsi < uxdm__yei:
        fti__oxkiz = lwd__dadsi + (uxdm__yei - lwd__dadsi >> 1)
        if key > getitem_arr_tup(arr, base + fti__oxkiz):
            lwd__dadsi = fti__oxkiz + 1
        else:
            uxdm__yei = fti__oxkiz
    assert lwd__dadsi == uxdm__yei
    return uxdm__yei


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    uxdm__yei = 1
    lwd__dadsi = 0
    if key < getitem_arr_tup(arr, base + hint):
        cxnz__raf = hint + 1
        while uxdm__yei < cxnz__raf and key < getitem_arr_tup(arr, base +
            hint - uxdm__yei):
            lwd__dadsi = uxdm__yei
            uxdm__yei = (uxdm__yei << 1) + 1
            if uxdm__yei <= 0:
                uxdm__yei = cxnz__raf
        if uxdm__yei > cxnz__raf:
            uxdm__yei = cxnz__raf
        tmp = lwd__dadsi
        lwd__dadsi = hint - uxdm__yei
        uxdm__yei = hint - tmp
    else:
        cxnz__raf = _len - hint
        while uxdm__yei < cxnz__raf and key >= getitem_arr_tup(arr, base +
            hint + uxdm__yei):
            lwd__dadsi = uxdm__yei
            uxdm__yei = (uxdm__yei << 1) + 1
            if uxdm__yei <= 0:
                uxdm__yei = cxnz__raf
        if uxdm__yei > cxnz__raf:
            uxdm__yei = cxnz__raf
        lwd__dadsi += hint
        uxdm__yei += hint
    assert -1 <= lwd__dadsi and lwd__dadsi < uxdm__yei and uxdm__yei <= _len
    lwd__dadsi += 1
    while lwd__dadsi < uxdm__yei:
        fti__oxkiz = lwd__dadsi + (uxdm__yei - lwd__dadsi >> 1)
        if key < getitem_arr_tup(arr, base + fti__oxkiz):
            uxdm__yei = fti__oxkiz
        else:
            lwd__dadsi = fti__oxkiz + 1
    assert lwd__dadsi == uxdm__yei
    return uxdm__yei


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
        gvbnh__apv = 0
        pia__mdye = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                pia__mdye += 1
                gvbnh__apv = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                gvbnh__apv += 1
                pia__mdye = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not gvbnh__apv | pia__mdye < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            gvbnh__apv = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if gvbnh__apv != 0:
                copyRange_tup(tmp, cursor1, arr, dest, gvbnh__apv)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, gvbnh__apv)
                dest += gvbnh__apv
                cursor1 += gvbnh__apv
                len1 -= gvbnh__apv
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            pia__mdye = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if pia__mdye != 0:
                copyRange_tup(arr, cursor2, arr, dest, pia__mdye)
                copyRange_tup(arr_data, cursor2, arr_data, dest, pia__mdye)
                dest += pia__mdye
                cursor2 += pia__mdye
                len2 -= pia__mdye
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
            if not gvbnh__apv >= MIN_GALLOP | pia__mdye >= MIN_GALLOP:
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
        gvbnh__apv = 0
        pia__mdye = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                gvbnh__apv += 1
                pia__mdye = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                pia__mdye += 1
                gvbnh__apv = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not gvbnh__apv | pia__mdye < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            gvbnh__apv = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if gvbnh__apv != 0:
                dest -= gvbnh__apv
                cursor1 -= gvbnh__apv
                len1 -= gvbnh__apv
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, gvbnh__apv)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    gvbnh__apv)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            pia__mdye = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if pia__mdye != 0:
                dest -= pia__mdye
                cursor2 -= pia__mdye
                len2 -= pia__mdye
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, pia__mdye)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    pia__mdye)
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
            if not gvbnh__apv >= MIN_GALLOP | pia__mdye >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    oxmsx__rboi = len(key_arrs[0])
    if tmpLength < minCapacity:
        mfb__kblm = minCapacity
        mfb__kblm |= mfb__kblm >> 1
        mfb__kblm |= mfb__kblm >> 2
        mfb__kblm |= mfb__kblm >> 4
        mfb__kblm |= mfb__kblm >> 8
        mfb__kblm |= mfb__kblm >> 16
        mfb__kblm += 1
        if mfb__kblm < 0:
            mfb__kblm = minCapacity
        else:
            mfb__kblm = min(mfb__kblm, oxmsx__rboi >> 1)
        tmp = alloc_arr_tup(mfb__kblm, key_arrs)
        tmp_data = alloc_arr_tup(mfb__kblm, data)
        tmpLength = mfb__kblm
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        yhaf__ysgxg = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = yhaf__ysgxg


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    lmqci__ahxp = arr_tup.count
    wnsv__ohsoy = 'def f(arr_tup, lo, hi):\n'
    for i in range(lmqci__ahxp):
        wnsv__ohsoy += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        wnsv__ohsoy += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        wnsv__ohsoy += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    wnsv__ohsoy += '  return\n'
    zrr__jhr = {}
    exec(wnsv__ohsoy, {}, zrr__jhr)
    bki__fvpb = zrr__jhr['f']
    return bki__fvpb


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    lmqci__ahxp = src_arr_tup.count
    assert lmqci__ahxp == dst_arr_tup.count
    wnsv__ohsoy = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(lmqci__ahxp):
        wnsv__ohsoy += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    wnsv__ohsoy += '  return\n'
    zrr__jhr = {}
    exec(wnsv__ohsoy, {'copyRange': copyRange}, zrr__jhr)
    hnjl__khxoh = zrr__jhr['f']
    return hnjl__khxoh


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    lmqci__ahxp = src_arr_tup.count
    assert lmqci__ahxp == dst_arr_tup.count
    wnsv__ohsoy = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(lmqci__ahxp):
        wnsv__ohsoy += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    wnsv__ohsoy += '  return\n'
    zrr__jhr = {}
    exec(wnsv__ohsoy, {'copyElement': copyElement}, zrr__jhr)
    hnjl__khxoh = zrr__jhr['f']
    return hnjl__khxoh


def getitem_arr_tup(arr_tup, ind):
    ccpbi__cbgt = [arr[ind] for arr in arr_tup]
    return tuple(ccpbi__cbgt)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    lmqci__ahxp = arr_tup.count
    wnsv__ohsoy = 'def f(arr_tup, ind):\n'
    wnsv__ohsoy += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(lmqci__ahxp)]), ',' if lmqci__ahxp == 1 else
        '')
    zrr__jhr = {}
    exec(wnsv__ohsoy, {}, zrr__jhr)
    guz__eqp = zrr__jhr['f']
    return guz__eqp


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, rlk__bsdm in zip(arr_tup, val_tup):
        arr[ind] = rlk__bsdm


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    lmqci__ahxp = arr_tup.count
    wnsv__ohsoy = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(lmqci__ahxp):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            wnsv__ohsoy += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            wnsv__ohsoy += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    wnsv__ohsoy += '  return\n'
    zrr__jhr = {}
    exec(wnsv__ohsoy, {}, zrr__jhr)
    guz__eqp = zrr__jhr['f']
    return guz__eqp


def test():
    import time
    oiup__rvx = time.time()
    xdhn__sxmt = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((xdhn__sxmt,), 0, 3, data)
    print('compile time', time.time() - oiup__rvx)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    sdp__wnx = np.random.ranf(n)
    qkol__xqduf = pd.DataFrame({'A': sdp__wnx, 'B': data[0], 'C': data[1]})
    oiup__rvx = time.time()
    qrfj__jxud = qkol__xqduf.sort_values('A', inplace=False)
    ccjg__qrvhd = time.time()
    sort((sdp__wnx,), 0, n, data)
    print('Bodo', time.time() - ccjg__qrvhd, 'Numpy', ccjg__qrvhd - oiup__rvx)
    np.testing.assert_almost_equal(data[0], qrfj__jxud.B.values)
    np.testing.assert_almost_equal(data[1], qrfj__jxud.C.values)


if __name__ == '__main__':
    test()
