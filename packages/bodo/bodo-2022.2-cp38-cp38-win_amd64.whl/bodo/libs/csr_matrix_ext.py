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
        ivmu__jnmkt = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, ivmu__jnmkt)


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
        tvmo__swov, dktgr__ukzvr, jgzte__wgfe, hoh__oxqym = args
        knq__wmlx = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        knq__wmlx.data = tvmo__swov
        knq__wmlx.indices = dktgr__ukzvr
        knq__wmlx.indptr = jgzte__wgfe
        knq__wmlx.shape = hoh__oxqym
        context.nrt.incref(builder, signature.args[0], tvmo__swov)
        context.nrt.incref(builder, signature.args[1], dktgr__ukzvr)
        context.nrt.incref(builder, signature.args[2], jgzte__wgfe)
        return knq__wmlx._getvalue()
    chhux__mwnxw = CSRMatrixType(data_t.dtype, indices_t.dtype)
    fqoz__eqz = chhux__mwnxw(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return fqoz__eqz, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    knq__wmlx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rylq__anil = c.pyapi.object_getattr_string(val, 'data')
    lrfp__goq = c.pyapi.object_getattr_string(val, 'indices')
    okji__iimmh = c.pyapi.object_getattr_string(val, 'indptr')
    zqf__otxk = c.pyapi.object_getattr_string(val, 'shape')
    knq__wmlx.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        rylq__anil).value
    knq__wmlx.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), lrfp__goq).value
    knq__wmlx.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), okji__iimmh).value
    knq__wmlx.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), zqf__otxk).value
    c.pyapi.decref(rylq__anil)
    c.pyapi.decref(lrfp__goq)
    c.pyapi.decref(okji__iimmh)
    c.pyapi.decref(zqf__otxk)
    qklv__kmn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(knq__wmlx._getvalue(), is_error=qklv__kmn)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    wreic__bfdt = c.context.insert_const_string(c.builder.module,
        'scipy.sparse')
    frv__fpos = c.pyapi.import_module_noblock(wreic__bfdt)
    knq__wmlx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        knq__wmlx.data)
    rylq__anil = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        knq__wmlx.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        knq__wmlx.indices)
    lrfp__goq = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), knq__wmlx.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        knq__wmlx.indptr)
    okji__iimmh = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), knq__wmlx.indptr, c.env_manager)
    zqf__otxk = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        knq__wmlx.shape, c.env_manager)
    rbvs__qbqgt = c.pyapi.tuple_pack([rylq__anil, lrfp__goq, okji__iimmh])
    tbque__zbyir = c.pyapi.call_method(frv__fpos, 'csr_matrix', (
        rbvs__qbqgt, zqf__otxk))
    c.pyapi.decref(rbvs__qbqgt)
    c.pyapi.decref(rylq__anil)
    c.pyapi.decref(lrfp__goq)
    c.pyapi.decref(okji__iimmh)
    c.pyapi.decref(zqf__otxk)
    c.pyapi.decref(frv__fpos)
    c.context.nrt.decref(c.builder, typ, val)
    return tbque__zbyir


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
    vqamt__dwhh = A.dtype
    ppdny__argwm = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            gnab__thk, dsru__sjja = A.shape
            mnjmr__bsb = numba.cpython.unicode._normalize_slice(idx[0],
                gnab__thk)
            ins__gduir = numba.cpython.unicode._normalize_slice(idx[1],
                dsru__sjja)
            if mnjmr__bsb.step != 1 or ins__gduir.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            qozu__qpzot = mnjmr__bsb.start
            gio__mtnnl = mnjmr__bsb.stop
            pnyh__undca = ins__gduir.start
            plsj__xrjjw = ins__gduir.stop
            pvstd__wafdc = A.indptr
            igudn__sxl = A.indices
            oguh__nzin = A.data
            eim__oskv = gio__mtnnl - qozu__qpzot
            eovs__fnvoe = plsj__xrjjw - pnyh__undca
            ptvx__mpjzb = 0
            fzknc__mbt = 0
            for qfemi__hoea in range(eim__oskv):
                jcy__cmafb = pvstd__wafdc[qozu__qpzot + qfemi__hoea]
                gud__uwh = pvstd__wafdc[qozu__qpzot + qfemi__hoea + 1]
                for cggha__kjpw in range(jcy__cmafb, gud__uwh):
                    if igudn__sxl[cggha__kjpw] >= pnyh__undca and igudn__sxl[
                        cggha__kjpw] < plsj__xrjjw:
                        ptvx__mpjzb += 1
            xhcd__ibj = np.empty(eim__oskv + 1, ppdny__argwm)
            fhc__kpaf = np.empty(ptvx__mpjzb, ppdny__argwm)
            scjm__gwt = np.empty(ptvx__mpjzb, vqamt__dwhh)
            xhcd__ibj[0] = 0
            for qfemi__hoea in range(eim__oskv):
                jcy__cmafb = pvstd__wafdc[qozu__qpzot + qfemi__hoea]
                gud__uwh = pvstd__wafdc[qozu__qpzot + qfemi__hoea + 1]
                for cggha__kjpw in range(jcy__cmafb, gud__uwh):
                    if igudn__sxl[cggha__kjpw] >= pnyh__undca and igudn__sxl[
                        cggha__kjpw] < plsj__xrjjw:
                        fhc__kpaf[fzknc__mbt] = igudn__sxl[cggha__kjpw
                            ] - pnyh__undca
                        scjm__gwt[fzknc__mbt] = oguh__nzin[cggha__kjpw]
                        fzknc__mbt += 1
                xhcd__ibj[qfemi__hoea + 1] = fzknc__mbt
            return init_csr_matrix(scjm__gwt, fhc__kpaf, xhcd__ibj, (
                eim__oskv, eovs__fnvoe))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
