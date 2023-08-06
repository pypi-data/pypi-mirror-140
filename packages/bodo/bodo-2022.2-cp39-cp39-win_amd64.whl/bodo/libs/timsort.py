import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    usf__prn = hi - lo
    if usf__prn < 2:
        return
    if usf__prn < MIN_MERGE:
        qvelc__ygtcb = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + qvelc__ygtcb, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    nkt__znep = minRunLength(usf__prn)
    while True:
        vpp__usrpa = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if vpp__usrpa < nkt__znep:
            wady__twe = usf__prn if usf__prn <= nkt__znep else nkt__znep
            binarySort(key_arrs, lo, lo + wady__twe, lo + vpp__usrpa, data)
            vpp__usrpa = wady__twe
        stackSize = pushRun(stackSize, runBase, runLen, lo, vpp__usrpa)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += vpp__usrpa
        usf__prn -= vpp__usrpa
        if usf__prn == 0:
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
        zwf__beql = getitem_arr_tup(key_arrs, start)
        rxhyg__vln = getitem_arr_tup(data, start)
        orrd__hvk = lo
        cjy__lsoh = start
        assert orrd__hvk <= cjy__lsoh
        while orrd__hvk < cjy__lsoh:
            dyxul__lgil = orrd__hvk + cjy__lsoh >> 1
            if zwf__beql < getitem_arr_tup(key_arrs, dyxul__lgil):
                cjy__lsoh = dyxul__lgil
            else:
                orrd__hvk = dyxul__lgil + 1
        assert orrd__hvk == cjy__lsoh
        n = start - orrd__hvk
        copyRange_tup(key_arrs, orrd__hvk, key_arrs, orrd__hvk + 1, n)
        copyRange_tup(data, orrd__hvk, data, orrd__hvk + 1, n)
        setitem_arr_tup(key_arrs, orrd__hvk, zwf__beql)
        setitem_arr_tup(data, orrd__hvk, rxhyg__vln)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    uoqrl__bccn = lo + 1
    if uoqrl__bccn == hi:
        return 1
    if getitem_arr_tup(key_arrs, uoqrl__bccn) < getitem_arr_tup(key_arrs, lo):
        uoqrl__bccn += 1
        while uoqrl__bccn < hi and getitem_arr_tup(key_arrs, uoqrl__bccn
            ) < getitem_arr_tup(key_arrs, uoqrl__bccn - 1):
            uoqrl__bccn += 1
        reverseRange(key_arrs, lo, uoqrl__bccn, data)
    else:
        uoqrl__bccn += 1
        while uoqrl__bccn < hi and getitem_arr_tup(key_arrs, uoqrl__bccn
            ) >= getitem_arr_tup(key_arrs, uoqrl__bccn - 1):
            uoqrl__bccn += 1
    return uoqrl__bccn - lo


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
    szf__jwynb = 0
    while n >= MIN_MERGE:
        szf__jwynb |= n & 1
        n >>= 1
    return n + szf__jwynb


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    mihvf__sgq = len(key_arrs[0])
    tmpLength = (mihvf__sgq >> 1 if mihvf__sgq < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    tydp__jqra = (5 if mihvf__sgq < 120 else 10 if mihvf__sgq < 1542 else 
        19 if mihvf__sgq < 119151 else 40)
    runBase = np.empty(tydp__jqra, np.int64)
    runLen = np.empty(tydp__jqra, np.int64)
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
    ohf__tlp = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert ohf__tlp >= 0
    base1 += ohf__tlp
    len1 -= ohf__tlp
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
    hrimn__yvadf = 0
    lvk__klk = 1
    if key > getitem_arr_tup(arr, base + hint):
        mgmg__stxj = _len - hint
        while lvk__klk < mgmg__stxj and key > getitem_arr_tup(arr, base +
            hint + lvk__klk):
            hrimn__yvadf = lvk__klk
            lvk__klk = (lvk__klk << 1) + 1
            if lvk__klk <= 0:
                lvk__klk = mgmg__stxj
        if lvk__klk > mgmg__stxj:
            lvk__klk = mgmg__stxj
        hrimn__yvadf += hint
        lvk__klk += hint
    else:
        mgmg__stxj = hint + 1
        while lvk__klk < mgmg__stxj and key <= getitem_arr_tup(arr, base +
            hint - lvk__klk):
            hrimn__yvadf = lvk__klk
            lvk__klk = (lvk__klk << 1) + 1
            if lvk__klk <= 0:
                lvk__klk = mgmg__stxj
        if lvk__klk > mgmg__stxj:
            lvk__klk = mgmg__stxj
        tmp = hrimn__yvadf
        hrimn__yvadf = hint - lvk__klk
        lvk__klk = hint - tmp
    assert -1 <= hrimn__yvadf and hrimn__yvadf < lvk__klk and lvk__klk <= _len
    hrimn__yvadf += 1
    while hrimn__yvadf < lvk__klk:
        nvsn__xts = hrimn__yvadf + (lvk__klk - hrimn__yvadf >> 1)
        if key > getitem_arr_tup(arr, base + nvsn__xts):
            hrimn__yvadf = nvsn__xts + 1
        else:
            lvk__klk = nvsn__xts
    assert hrimn__yvadf == lvk__klk
    return lvk__klk


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    lvk__klk = 1
    hrimn__yvadf = 0
    if key < getitem_arr_tup(arr, base + hint):
        mgmg__stxj = hint + 1
        while lvk__klk < mgmg__stxj and key < getitem_arr_tup(arr, base +
            hint - lvk__klk):
            hrimn__yvadf = lvk__klk
            lvk__klk = (lvk__klk << 1) + 1
            if lvk__klk <= 0:
                lvk__klk = mgmg__stxj
        if lvk__klk > mgmg__stxj:
            lvk__klk = mgmg__stxj
        tmp = hrimn__yvadf
        hrimn__yvadf = hint - lvk__klk
        lvk__klk = hint - tmp
    else:
        mgmg__stxj = _len - hint
        while lvk__klk < mgmg__stxj and key >= getitem_arr_tup(arr, base +
            hint + lvk__klk):
            hrimn__yvadf = lvk__klk
            lvk__klk = (lvk__klk << 1) + 1
            if lvk__klk <= 0:
                lvk__klk = mgmg__stxj
        if lvk__klk > mgmg__stxj:
            lvk__klk = mgmg__stxj
        hrimn__yvadf += hint
        lvk__klk += hint
    assert -1 <= hrimn__yvadf and hrimn__yvadf < lvk__klk and lvk__klk <= _len
    hrimn__yvadf += 1
    while hrimn__yvadf < lvk__klk:
        nvsn__xts = hrimn__yvadf + (lvk__klk - hrimn__yvadf >> 1)
        if key < getitem_arr_tup(arr, base + nvsn__xts):
            lvk__klk = nvsn__xts
        else:
            hrimn__yvadf = nvsn__xts + 1
    assert hrimn__yvadf == lvk__klk
    return lvk__klk


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
        cdqbe__ypl = 0
        swat__iie = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                swat__iie += 1
                cdqbe__ypl = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                cdqbe__ypl += 1
                swat__iie = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not cdqbe__ypl | swat__iie < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            cdqbe__ypl = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if cdqbe__ypl != 0:
                copyRange_tup(tmp, cursor1, arr, dest, cdqbe__ypl)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, cdqbe__ypl)
                dest += cdqbe__ypl
                cursor1 += cdqbe__ypl
                len1 -= cdqbe__ypl
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            swat__iie = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if swat__iie != 0:
                copyRange_tup(arr, cursor2, arr, dest, swat__iie)
                copyRange_tup(arr_data, cursor2, arr_data, dest, swat__iie)
                dest += swat__iie
                cursor2 += swat__iie
                len2 -= swat__iie
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
            if not cdqbe__ypl >= MIN_GALLOP | swat__iie >= MIN_GALLOP:
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
        cdqbe__ypl = 0
        swat__iie = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                cdqbe__ypl += 1
                swat__iie = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                swat__iie += 1
                cdqbe__ypl = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not cdqbe__ypl | swat__iie < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            cdqbe__ypl = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if cdqbe__ypl != 0:
                dest -= cdqbe__ypl
                cursor1 -= cdqbe__ypl
                len1 -= cdqbe__ypl
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, cdqbe__ypl)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    cdqbe__ypl)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            swat__iie = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if swat__iie != 0:
                dest -= swat__iie
                cursor2 -= swat__iie
                len2 -= swat__iie
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, swat__iie)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    swat__iie)
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
            if not cdqbe__ypl >= MIN_GALLOP | swat__iie >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    yoc__lfq = len(key_arrs[0])
    if tmpLength < minCapacity:
        vmn__aived = minCapacity
        vmn__aived |= vmn__aived >> 1
        vmn__aived |= vmn__aived >> 2
        vmn__aived |= vmn__aived >> 4
        vmn__aived |= vmn__aived >> 8
        vmn__aived |= vmn__aived >> 16
        vmn__aived += 1
        if vmn__aived < 0:
            vmn__aived = minCapacity
        else:
            vmn__aived = min(vmn__aived, yoc__lfq >> 1)
        tmp = alloc_arr_tup(vmn__aived, key_arrs)
        tmp_data = alloc_arr_tup(vmn__aived, data)
        tmpLength = vmn__aived
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        rnwib__rjwr = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = rnwib__rjwr


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    bhc__ztjlt = arr_tup.count
    qykhm__kxdy = 'def f(arr_tup, lo, hi):\n'
    for i in range(bhc__ztjlt):
        qykhm__kxdy += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        qykhm__kxdy += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        qykhm__kxdy += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    qykhm__kxdy += '  return\n'
    jyzrq__zlaie = {}
    exec(qykhm__kxdy, {}, jyzrq__zlaie)
    azb__zldck = jyzrq__zlaie['f']
    return azb__zldck


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    bhc__ztjlt = src_arr_tup.count
    assert bhc__ztjlt == dst_arr_tup.count
    qykhm__kxdy = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(bhc__ztjlt):
        qykhm__kxdy += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    qykhm__kxdy += '  return\n'
    jyzrq__zlaie = {}
    exec(qykhm__kxdy, {'copyRange': copyRange}, jyzrq__zlaie)
    kgr__szahq = jyzrq__zlaie['f']
    return kgr__szahq


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    bhc__ztjlt = src_arr_tup.count
    assert bhc__ztjlt == dst_arr_tup.count
    qykhm__kxdy = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(bhc__ztjlt):
        qykhm__kxdy += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    qykhm__kxdy += '  return\n'
    jyzrq__zlaie = {}
    exec(qykhm__kxdy, {'copyElement': copyElement}, jyzrq__zlaie)
    kgr__szahq = jyzrq__zlaie['f']
    return kgr__szahq


def getitem_arr_tup(arr_tup, ind):
    zcg__tgi = [arr[ind] for arr in arr_tup]
    return tuple(zcg__tgi)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    bhc__ztjlt = arr_tup.count
    qykhm__kxdy = 'def f(arr_tup, ind):\n'
    qykhm__kxdy += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(bhc__ztjlt)]), ',' if bhc__ztjlt == 1 else '')
    jyzrq__zlaie = {}
    exec(qykhm__kxdy, {}, jyzrq__zlaie)
    guff__shej = jyzrq__zlaie['f']
    return guff__shej


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, fsvqh__pao in zip(arr_tup, val_tup):
        arr[ind] = fsvqh__pao


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    bhc__ztjlt = arr_tup.count
    qykhm__kxdy = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(bhc__ztjlt):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            qykhm__kxdy += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            qykhm__kxdy += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    qykhm__kxdy += '  return\n'
    jyzrq__zlaie = {}
    exec(qykhm__kxdy, {}, jyzrq__zlaie)
    guff__shej = jyzrq__zlaie['f']
    return guff__shej


def test():
    import time
    xhq__gzev = time.time()
    koww__gzyw = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((koww__gzyw,), 0, 3, data)
    print('compile time', time.time() - xhq__gzev)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    hafg__ilxxt = np.random.ranf(n)
    svq__edyl = pd.DataFrame({'A': hafg__ilxxt, 'B': data[0], 'C': data[1]})
    xhq__gzev = time.time()
    uey__rry = svq__edyl.sort_values('A', inplace=False)
    bqm__zwee = time.time()
    sort((hafg__ilxxt,), 0, n, data)
    print('Bodo', time.time() - bqm__zwee, 'Numpy', bqm__zwee - xhq__gzev)
    np.testing.assert_almost_equal(data[0], uey__rry.B.values)
    np.testing.assert_almost_equal(data[1], uey__rry.C.values)


if __name__ == '__main__':
    test()
