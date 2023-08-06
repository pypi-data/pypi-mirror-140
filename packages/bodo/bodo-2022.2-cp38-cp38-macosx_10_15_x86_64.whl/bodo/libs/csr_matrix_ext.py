"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ttc__muvoj = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ttc__muvoj)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        uzpb__vzksb, zbcc__hcq, dlt__vxsqn, aedlh__grzx = args
        akmhb__wslit = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        akmhb__wslit.data = uzpb__vzksb
        akmhb__wslit.indices = zbcc__hcq
        akmhb__wslit.indptr = dlt__vxsqn
        akmhb__wslit.shape = aedlh__grzx
        context.nrt.incref(builder, signature.args[0], uzpb__vzksb)
        context.nrt.incref(builder, signature.args[1], zbcc__hcq)
        context.nrt.incref(builder, signature.args[2], dlt__vxsqn)
        return akmhb__wslit._getvalue()
    vcf__xlfmv = CSRMatrixType(data_t.dtype, indices_t.dtype)
    eym__lvc = vcf__xlfmv(data_t, indices_t, indptr_t, types.UniTuple(types
        .int64, 2))
    return eym__lvc, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    akmhb__wslit = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tpeo__yagi = c.pyapi.object_getattr_string(val, 'data')
    cvlkt__zwqsm = c.pyapi.object_getattr_string(val, 'indices')
    qmxm__mtz = c.pyapi.object_getattr_string(val, 'indptr')
    ikg__ezrfk = c.pyapi.object_getattr_string(val, 'shape')
    akmhb__wslit.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), tpeo__yagi).value
    akmhb__wslit.indices = c.pyapi.to_native_value(types.Array(typ.
        idx_dtype, 1, 'C'), cvlkt__zwqsm).value
    akmhb__wslit.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), qmxm__mtz).value
    akmhb__wslit.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), ikg__ezrfk).value
    c.pyapi.decref(tpeo__yagi)
    c.pyapi.decref(cvlkt__zwqsm)
    c.pyapi.decref(qmxm__mtz)
    c.pyapi.decref(ikg__ezrfk)
    fqtj__omyis = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(akmhb__wslit._getvalue(), is_error=fqtj__omyis)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    khz__pell = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    apa__pgfw = c.pyapi.import_module_noblock(khz__pell)
    akmhb__wslit = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        akmhb__wslit.data)
    tpeo__yagi = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        akmhb__wslit.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        akmhb__wslit.indices)
    cvlkt__zwqsm = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), akmhb__wslit.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        akmhb__wslit.indptr)
    qmxm__mtz = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), akmhb__wslit.indptr, c.env_manager)
    ikg__ezrfk = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        akmhb__wslit.shape, c.env_manager)
    kzwvu__jzjy = c.pyapi.tuple_pack([tpeo__yagi, cvlkt__zwqsm, qmxm__mtz])
    kaviw__wmcz = c.pyapi.call_method(apa__pgfw, 'csr_matrix', (kzwvu__jzjy,
        ikg__ezrfk))
    c.pyapi.decref(kzwvu__jzjy)
    c.pyapi.decref(tpeo__yagi)
    c.pyapi.decref(cvlkt__zwqsm)
    c.pyapi.decref(qmxm__mtz)
    c.pyapi.decref(ikg__ezrfk)
    c.pyapi.decref(apa__pgfw)
    c.context.nrt.decref(c.builder, typ, val)
    return kaviw__wmcz


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    vhy__gst = A.dtype
    tbce__wvqfl = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            jauj__nwfm, klevu__ohgqs = A.shape
            vxj__yenz = numba.cpython.unicode._normalize_slice(idx[0],
                jauj__nwfm)
            zxbwy__dawti = numba.cpython.unicode._normalize_slice(idx[1],
                klevu__ohgqs)
            if vxj__yenz.step != 1 or zxbwy__dawti.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            knpfq__iyf = vxj__yenz.start
            bigo__zhiyx = vxj__yenz.stop
            pqgbp__qov = zxbwy__dawti.start
            xryv__bmo = zxbwy__dawti.stop
            lmvpi__day = A.indptr
            naucl__pnf = A.indices
            mgflt__pvadh = A.data
            mgrpo__nce = bigo__zhiyx - knpfq__iyf
            wzsws__kkr = xryv__bmo - pqgbp__qov
            ipjh__yolt = 0
            tttq__yzwf = 0
            for xnj__djrv in range(mgrpo__nce):
                uosxq__nfm = lmvpi__day[knpfq__iyf + xnj__djrv]
                hee__gnxeu = lmvpi__day[knpfq__iyf + xnj__djrv + 1]
                for gxzpx__iukp in range(uosxq__nfm, hee__gnxeu):
                    if naucl__pnf[gxzpx__iukp] >= pqgbp__qov and naucl__pnf[
                        gxzpx__iukp] < xryv__bmo:
                        ipjh__yolt += 1
            hxtmv__qka = np.empty(mgrpo__nce + 1, tbce__wvqfl)
            smci__kiwus = np.empty(ipjh__yolt, tbce__wvqfl)
            odasm__gwk = np.empty(ipjh__yolt, vhy__gst)
            hxtmv__qka[0] = 0
            for xnj__djrv in range(mgrpo__nce):
                uosxq__nfm = lmvpi__day[knpfq__iyf + xnj__djrv]
                hee__gnxeu = lmvpi__day[knpfq__iyf + xnj__djrv + 1]
                for gxzpx__iukp in range(uosxq__nfm, hee__gnxeu):
                    if naucl__pnf[gxzpx__iukp] >= pqgbp__qov and naucl__pnf[
                        gxzpx__iukp] < xryv__bmo:
                        smci__kiwus[tttq__yzwf] = naucl__pnf[gxzpx__iukp
                            ] - pqgbp__qov
                        odasm__gwk[tttq__yzwf] = mgflt__pvadh[gxzpx__iukp]
                        tttq__yzwf += 1
                hxtmv__qka[xnj__djrv + 1] = tttq__yzwf
            return init_csr_matrix(odasm__gwk, smci__kiwus, hxtmv__qka, (
                mgrpo__nce, wzsws__kkr))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
