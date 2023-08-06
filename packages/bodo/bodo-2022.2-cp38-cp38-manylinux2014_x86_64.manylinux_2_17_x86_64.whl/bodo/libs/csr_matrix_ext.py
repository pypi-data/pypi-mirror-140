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
        huw__rogm = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, huw__rogm)


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
        jlm__aubd, qkgkx__omq, nhb__jun, bdr__ozsmw = args
        swbu__wmcud = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        swbu__wmcud.data = jlm__aubd
        swbu__wmcud.indices = qkgkx__omq
        swbu__wmcud.indptr = nhb__jun
        swbu__wmcud.shape = bdr__ozsmw
        context.nrt.incref(builder, signature.args[0], jlm__aubd)
        context.nrt.incref(builder, signature.args[1], qkgkx__omq)
        context.nrt.incref(builder, signature.args[2], nhb__jun)
        return swbu__wmcud._getvalue()
    xzh__gqs = CSRMatrixType(data_t.dtype, indices_t.dtype)
    vggj__ungt = xzh__gqs(data_t, indices_t, indptr_t, types.UniTuple(types
        .int64, 2))
    return vggj__ungt, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    swbu__wmcud = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cjxxj__fgxpy = c.pyapi.object_getattr_string(val, 'data')
    lqo__uddde = c.pyapi.object_getattr_string(val, 'indices')
    chdit__ijtjp = c.pyapi.object_getattr_string(val, 'indptr')
    vzaz__asny = c.pyapi.object_getattr_string(val, 'shape')
    swbu__wmcud.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), cjxxj__fgxpy).value
    swbu__wmcud.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), lqo__uddde).value
    swbu__wmcud.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), chdit__ijtjp).value
    swbu__wmcud.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), vzaz__asny).value
    c.pyapi.decref(cjxxj__fgxpy)
    c.pyapi.decref(lqo__uddde)
    c.pyapi.decref(chdit__ijtjp)
    c.pyapi.decref(vzaz__asny)
    kwoh__afn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(swbu__wmcud._getvalue(), is_error=kwoh__afn)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    rdf__phld = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    ofqs__exvq = c.pyapi.import_module_noblock(rdf__phld)
    swbu__wmcud = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        swbu__wmcud.data)
    cjxxj__fgxpy = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        swbu__wmcud.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        swbu__wmcud.indices)
    lqo__uddde = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), swbu__wmcud.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        swbu__wmcud.indptr)
    chdit__ijtjp = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), swbu__wmcud.indptr, c.env_manager)
    vzaz__asny = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        swbu__wmcud.shape, c.env_manager)
    tvk__luwmw = c.pyapi.tuple_pack([cjxxj__fgxpy, lqo__uddde, chdit__ijtjp])
    tjgq__llwn = c.pyapi.call_method(ofqs__exvq, 'csr_matrix', (tvk__luwmw,
        vzaz__asny))
    c.pyapi.decref(tvk__luwmw)
    c.pyapi.decref(cjxxj__fgxpy)
    c.pyapi.decref(lqo__uddde)
    c.pyapi.decref(chdit__ijtjp)
    c.pyapi.decref(vzaz__asny)
    c.pyapi.decref(ofqs__exvq)
    c.context.nrt.decref(c.builder, typ, val)
    return tjgq__llwn


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
    rqbyq__nmnv = A.dtype
    xrxp__kngu = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            vcp__ndzr, sgxa__fat = A.shape
            frz__nlzj = numba.cpython.unicode._normalize_slice(idx[0],
                vcp__ndzr)
            ehng__ritka = numba.cpython.unicode._normalize_slice(idx[1],
                sgxa__fat)
            if frz__nlzj.step != 1 or ehng__ritka.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            ilky__ibih = frz__nlzj.start
            guwj__oeir = frz__nlzj.stop
            bdci__czwmw = ehng__ritka.start
            ydv__eoqkw = ehng__ritka.stop
            kfek__ynobk = A.indptr
            hyje__mjutg = A.indices
            fuh__iyaw = A.data
            eesd__zzcml = guwj__oeir - ilky__ibih
            jkde__set = ydv__eoqkw - bdci__czwmw
            ucgfk__oynz = 0
            rev__uac = 0
            for hse__cpc in range(eesd__zzcml):
                laizv__ogzt = kfek__ynobk[ilky__ibih + hse__cpc]
                hmfa__bqst = kfek__ynobk[ilky__ibih + hse__cpc + 1]
                for mwzxh__xxpuf in range(laizv__ogzt, hmfa__bqst):
                    if hyje__mjutg[mwzxh__xxpuf
                        ] >= bdci__czwmw and hyje__mjutg[mwzxh__xxpuf
                        ] < ydv__eoqkw:
                        ucgfk__oynz += 1
            xlc__woeu = np.empty(eesd__zzcml + 1, xrxp__kngu)
            inaxd__aonap = np.empty(ucgfk__oynz, xrxp__kngu)
            pdd__nbwp = np.empty(ucgfk__oynz, rqbyq__nmnv)
            xlc__woeu[0] = 0
            for hse__cpc in range(eesd__zzcml):
                laizv__ogzt = kfek__ynobk[ilky__ibih + hse__cpc]
                hmfa__bqst = kfek__ynobk[ilky__ibih + hse__cpc + 1]
                for mwzxh__xxpuf in range(laizv__ogzt, hmfa__bqst):
                    if hyje__mjutg[mwzxh__xxpuf
                        ] >= bdci__czwmw and hyje__mjutg[mwzxh__xxpuf
                        ] < ydv__eoqkw:
                        inaxd__aonap[rev__uac] = hyje__mjutg[mwzxh__xxpuf
                            ] - bdci__czwmw
                        pdd__nbwp[rev__uac] = fuh__iyaw[mwzxh__xxpuf]
                        rev__uac += 1
                xlc__woeu[hse__cpc + 1] = rev__uac
            return init_csr_matrix(pdd__nbwp, inaxd__aonap, xlc__woeu, (
                eesd__zzcml, jkde__set))
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
