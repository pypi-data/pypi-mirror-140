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
        agm__cvij = self._get_h5_type(lhs, rhs)
        if agm__cvij is not None:
            ims__zhtdo = str(agm__cvij.dtype)
            fodg__njewp = 'def _h5_read_impl(dset, index):\n'
            fodg__njewp += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(agm__cvij.ndim, ims__zhtdo))
            qsyh__lsbt = {}
            exec(fodg__njewp, {}, qsyh__lsbt)
            zcjz__gzj = qsyh__lsbt['_h5_read_impl']
            nykab__xey = compile_to_numba_ir(zcjz__gzj, {'bodo': bodo}
                ).blocks.popitem()[1]
            nzgg__iacv = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(nykab__xey, [rhs.value, nzgg__iacv])
            zwyos__one = nykab__xey.body[:-3]
            zwyos__one[-1].target = assign.target
            return zwyos__one
        return None

    def _get_h5_type(self, lhs, rhs):
        agm__cvij = self._get_h5_type_locals(lhs)
        if agm__cvij is not None:
            return agm__cvij
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        nzgg__iacv = rhs.index if rhs.op == 'getitem' else rhs.index_var
        uvx__vlkn = guard(find_const, self.func_ir, nzgg__iacv)
        require(not isinstance(uvx__vlkn, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            hyv__ustqa = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            auu__fdrzt = get_const_value_inner(self.func_ir, hyv__ustqa,
                arg_types=self.arg_types)
            obj_name_list.append(auu__fdrzt)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        wqlj__kjbsj = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        gbinu__xpb = h5py.File(wqlj__kjbsj, 'r')
        yhmm__yxks = gbinu__xpb
        for auu__fdrzt in obj_name_list:
            yhmm__yxks = yhmm__yxks[auu__fdrzt]
        require(isinstance(yhmm__yxks, h5py.Dataset))
        vedyr__yzsp = len(yhmm__yxks.shape)
        eglq__smkli = numba.np.numpy_support.from_dtype(yhmm__yxks.dtype)
        gbinu__xpb.close()
        return types.Array(eglq__smkli, vedyr__yzsp, 'C')

    def _get_h5_type_locals(self, varname):
        hrtya__grbm = self.locals.pop(varname, None)
        if hrtya__grbm is None and varname is not None:
            hrtya__grbm = self.flags.h5_types.get(varname, None)
        return hrtya__grbm
