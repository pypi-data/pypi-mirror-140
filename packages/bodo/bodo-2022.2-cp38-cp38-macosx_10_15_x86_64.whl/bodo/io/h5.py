"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        npg__owap = self._get_h5_type(lhs, rhs)
        if npg__owap is not None:
            bwxnt__onzk = str(npg__owap.dtype)
            vet__thqhm = 'def _h5_read_impl(dset, index):\n'
            vet__thqhm += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(npg__owap.ndim, bwxnt__onzk))
            rrllm__ufzf = {}
            exec(vet__thqhm, {}, rrllm__ufzf)
            lkg__ulqr = rrllm__ufzf['_h5_read_impl']
            fmr__spubr = compile_to_numba_ir(lkg__ulqr, {'bodo': bodo}
                ).blocks.popitem()[1]
            upet__dcsr = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(fmr__spubr, [rhs.value, upet__dcsr])
            grhbn__oguie = fmr__spubr.body[:-3]
            grhbn__oguie[-1].target = assign.target
            return grhbn__oguie
        return None

    def _get_h5_type(self, lhs, rhs):
        npg__owap = self._get_h5_type_locals(lhs)
        if npg__owap is not None:
            return npg__owap
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        upet__dcsr = rhs.index if rhs.op == 'getitem' else rhs.index_var
        idplk__ynd = guard(find_const, self.func_ir, upet__dcsr)
        require(not isinstance(idplk__ynd, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            ycsc__narlv = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            kpjm__hzka = get_const_value_inner(self.func_ir, ycsc__narlv,
                arg_types=self.arg_types)
            obj_name_list.append(kpjm__hzka)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        zxn__gfmb = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        pqqka__ztaz = h5py.File(zxn__gfmb, 'r')
        mwm__fnn = pqqka__ztaz
        for kpjm__hzka in obj_name_list:
            mwm__fnn = mwm__fnn[kpjm__hzka]
        require(isinstance(mwm__fnn, h5py.Dataset))
        vnn__jjj = len(mwm__fnn.shape)
        ppmzb__rulkh = numba.np.numpy_support.from_dtype(mwm__fnn.dtype)
        pqqka__ztaz.close()
        return types.Array(ppmzb__rulkh, vnn__jjj, 'C')

    def _get_h5_type_locals(self, varname):
        vyy__gkpo = self.locals.pop(varname, None)
        if vyy__gkpo is None and varname is not None:
            vyy__gkpo = self.flags.h5_types.get(varname, None)
        return vyy__gkpo
