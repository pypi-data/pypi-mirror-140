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
        qibrc__gtkol = self._get_h5_type(lhs, rhs)
        if qibrc__gtkol is not None:
            ssqf__wfiz = str(qibrc__gtkol.dtype)
            gwrbb__zapu = 'def _h5_read_impl(dset, index):\n'
            gwrbb__zapu += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(qibrc__gtkol.ndim, ssqf__wfiz))
            gjf__uhc = {}
            exec(gwrbb__zapu, {}, gjf__uhc)
            bvvvw__ohk = gjf__uhc['_h5_read_impl']
            iacrg__cmal = compile_to_numba_ir(bvvvw__ohk, {'bodo': bodo}
                ).blocks.popitem()[1]
            wkqqg__xak = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(iacrg__cmal, [rhs.value, wkqqg__xak])
            wtzwm__lybl = iacrg__cmal.body[:-3]
            wtzwm__lybl[-1].target = assign.target
            return wtzwm__lybl
        return None

    def _get_h5_type(self, lhs, rhs):
        qibrc__gtkol = self._get_h5_type_locals(lhs)
        if qibrc__gtkol is not None:
            return qibrc__gtkol
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        wkqqg__xak = rhs.index if rhs.op == 'getitem' else rhs.index_var
        uzion__jat = guard(find_const, self.func_ir, wkqqg__xak)
        require(not isinstance(uzion__jat, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            ska__yicny = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            bgfqm__kgux = get_const_value_inner(self.func_ir, ska__yicny,
                arg_types=self.arg_types)
            obj_name_list.append(bgfqm__kgux)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        syl__zdtux = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        cvaa__svzs = h5py.File(syl__zdtux, 'r')
        gmcer__mkx = cvaa__svzs
        for bgfqm__kgux in obj_name_list:
            gmcer__mkx = gmcer__mkx[bgfqm__kgux]
        require(isinstance(gmcer__mkx, h5py.Dataset))
        vuqdu__blyt = len(gmcer__mkx.shape)
        tcoxp__roxwn = numba.np.numpy_support.from_dtype(gmcer__mkx.dtype)
        cvaa__svzs.close()
        return types.Array(tcoxp__roxwn, vuqdu__blyt, 'C')

    def _get_h5_type_locals(self, varname):
        ujq__tqc = self.locals.pop(varname, None)
        if ujq__tqc is None and varname is not None:
            ujq__tqc = self.flags.h5_types.get(varname, None)
        return ujq__tqc
