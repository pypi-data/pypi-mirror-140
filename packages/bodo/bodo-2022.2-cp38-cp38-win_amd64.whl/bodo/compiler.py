"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        two__wgzmp = 'bodo' if distributed else 'bodo_seq'
        two__wgzmp = (two__wgzmp + '_inline' if inline_calls_pass else
            two__wgzmp)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, two__wgzmp
            )
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for axu__htrh, (ubhz__uadmv, zenfa__xvyhe) in enumerate(pm.passes):
        if ubhz__uadmv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(axu__htrh, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for axu__htrh, (ubhz__uadmv, zenfa__xvyhe) in enumerate(pm.passes):
        if ubhz__uadmv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[axu__htrh] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for axu__htrh, (ubhz__uadmv, zenfa__xvyhe) in enumerate(pm.passes):
        if ubhz__uadmv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(axu__htrh)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    wth__xpf = guard(get_definition, func_ir, rhs.func)
    if isinstance(wth__xpf, (ir.Global, ir.FreeVar, ir.Const)):
        mlv__mka = wth__xpf.value
    else:
        bwph__mrel = guard(find_callname, func_ir, rhs)
        if not (bwph__mrel and isinstance(bwph__mrel[0], str) and
            isinstance(bwph__mrel[1], str)):
            return
        func_name, func_mod = bwph__mrel
        try:
            import importlib
            oamd__mpdlc = importlib.import_module(func_mod)
            mlv__mka = getattr(oamd__mpdlc, func_name)
        except:
            return
    if isinstance(mlv__mka, CPUDispatcher) and issubclass(mlv__mka.
        _compiler.pipeline_class, BodoCompiler
        ) and mlv__mka._compiler.pipeline_class != BodoCompilerUDF:
        mlv__mka._compiler.pipeline_class = BodoCompilerUDF
        mlv__mka.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for gbcfw__rdqyt in block.body:
                if is_call_assign(gbcfw__rdqyt):
                    _convert_bodo_dispatcher_to_udf(gbcfw__rdqyt.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        siut__cvz = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        siut__cvz.run()
        return True


def _update_definitions(func_ir, node_list):
    xqk__trof = ir.Loc('', 0)
    pypuc__wlljh = ir.Block(ir.Scope(None, xqk__trof), xqk__trof)
    pypuc__wlljh.body = node_list
    build_definitions({(0): pypuc__wlljh}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        bfbt__jct = 'overload_series_' + rhs.attr
        hgt__tlj = getattr(bodo.hiframes.series_impl, bfbt__jct)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        bfbt__jct = 'overload_dataframe_' + rhs.attr
        hgt__tlj = getattr(bodo.hiframes.dataframe_impl, bfbt__jct)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    uuffp__qqdi = hgt__tlj(rhs_type)
    yqho__utj = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    lafr__tlb = compile_func_single_block(uuffp__qqdi, (rhs.value,), stmt.
        target, yqho__utj)
    _update_definitions(func_ir, lafr__tlb)
    new_body += lafr__tlb
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        dneun__dilu = tuple(typemap[eonqe__lgw.name] for eonqe__lgw in rhs.args
            )
        oapba__mdize = {two__wgzmp: typemap[eonqe__lgw.name] for two__wgzmp,
            eonqe__lgw in dict(rhs.kws).items()}
        uuffp__qqdi = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*dneun__dilu, **oapba__mdize)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        dneun__dilu = tuple(typemap[eonqe__lgw.name] for eonqe__lgw in rhs.args
            )
        oapba__mdize = {two__wgzmp: typemap[eonqe__lgw.name] for two__wgzmp,
            eonqe__lgw in dict(rhs.kws).items()}
        uuffp__qqdi = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*dneun__dilu, **oapba__mdize)
    else:
        return False
    evrf__pqr = replace_func(pass_info, uuffp__qqdi, rhs.args, pysig=numba.
        core.utils.pysignature(uuffp__qqdi), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    jeie__vggou, zenfa__xvyhe = inline_closure_call(func_ir, evrf__pqr.
        glbls, block, len(new_body), evrf__pqr.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=evrf__pqr.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for trym__mmnr in jeie__vggou.values():
        trym__mmnr.loc = rhs.loc
        update_locs(trym__mmnr.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    teyr__wxykc = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = teyr__wxykc(func_ir, typemap)
    ovnb__faos = func_ir.blocks
    work_list = list((seazh__yhb, ovnb__faos[seazh__yhb]) for seazh__yhb in
        reversed(ovnb__faos.keys()))
    while work_list:
        likp__aft, block = work_list.pop()
        new_body = []
        znu__hihyb = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                bwph__mrel = guard(find_callname, func_ir, rhs, typemap)
                if bwph__mrel is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = bwph__mrel
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    znu__hihyb = True
                    break
            new_body.append(stmt)
        if not znu__hihyb:
            ovnb__faos[likp__aft].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        pflt__pul = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = pflt__pul.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        nhryd__vanj = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        nhryd__vanj.run()
        nhryd__vanj.run()
        nhryd__vanj.run()
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        xgz__wwza = 0
        cibxh__khly = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            xgz__wwza = int(os.environ[cibxh__khly])
        except:
            pass
        if xgz__wwza > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(xgz__wwza, state
                .metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        yqho__utj = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, yqho__utj)
        for block in state.func_ir.blocks.values():
            new_body = []
            for gbcfw__rdqyt in block.body:
                if type(gbcfw__rdqyt) in distributed_run_extensions:
                    iee__gdm = distributed_run_extensions[type(gbcfw__rdqyt)]
                    voogs__fac = iee__gdm(gbcfw__rdqyt, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += voogs__fac
                elif is_call_assign(gbcfw__rdqyt):
                    rhs = gbcfw__rdqyt.value
                    bwph__mrel = guard(find_callname, state.func_ir, rhs)
                    if bwph__mrel == ('gatherv', 'bodo') or bwph__mrel == (
                        'allgatherv', 'bodo'):
                        gbcfw__rdqyt.value = rhs.args[0]
                    new_body.append(gbcfw__rdqyt)
                else:
                    new_body.append(gbcfw__rdqyt)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        rkf__zrq = TableColumnDelPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes)
        return rkf__zrq.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    dfbph__yhiv = set()
    while work_list:
        likp__aft, block = work_list.pop()
        dfbph__yhiv.add(likp__aft)
        for i, ynk__bavw in enumerate(block.body):
            if isinstance(ynk__bavw, ir.Assign):
                fbrp__cvxy = ynk__bavw.value
                if isinstance(fbrp__cvxy, ir.Expr) and fbrp__cvxy.op == 'call':
                    wth__xpf = guard(get_definition, func_ir, fbrp__cvxy.func)
                    if isinstance(wth__xpf, (ir.Global, ir.FreeVar)
                        ) and isinstance(wth__xpf.value, CPUDispatcher
                        ) and issubclass(wth__xpf.value._compiler.
                        pipeline_class, BodoCompiler):
                        ahyes__hcesf = wth__xpf.value.py_func
                        arg_types = None
                        if typingctx:
                            qwyxz__tggdb = dict(fbrp__cvxy.kws)
                            qke__iit = tuple(typemap[eonqe__lgw.name] for
                                eonqe__lgw in fbrp__cvxy.args)
                            hqwq__lpdxv = {qnbdi__trtso: typemap[eonqe__lgw
                                .name] for qnbdi__trtso, eonqe__lgw in
                                qwyxz__tggdb.items()}
                            zenfa__xvyhe, arg_types = (wth__xpf.value.
                                fold_argument_types(qke__iit, hqwq__lpdxv))
                        zenfa__xvyhe, leup__wpw = inline_closure_call(func_ir,
                            ahyes__hcesf.__globals__, block, i,
                            ahyes__hcesf, typingctx=typingctx, targetctx=
                            targetctx, arg_typs=arg_types, typemap=typemap,
                            calltypes=calltypes, work_list=work_list)
                        _locals.update((leup__wpw[qnbdi__trtso].name,
                            eonqe__lgw) for qnbdi__trtso, eonqe__lgw in
                            wth__xpf.value.locals.items() if qnbdi__trtso in
                            leup__wpw)
                        break
    return dfbph__yhiv


def udf_jit(signature_or_function=None, **options):
    byiv__npj = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=byiv__npj,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for axu__htrh, (ubhz__uadmv, zenfa__xvyhe) in enumerate(pm.passes):
        if ubhz__uadmv == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:axu__htrh + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    qtoa__oueqx = None
    hktz__moen = None
    _locals = {}
    esh__osb = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(esh__osb, arg_types,
        kw_types)
    pcjk__zsp = numba.core.compiler.Flags()
    lde__kfanb = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    msqp__pscot = {'nopython': True, 'boundscheck': False, 'parallel':
        lde__kfanb}
    numba.core.registry.cpu_target.options.parse_as_flags(pcjk__zsp,
        msqp__pscot)
    cmr__uimm = TyperCompiler(typingctx, targetctx, qtoa__oueqx, args,
        hktz__moen, pcjk__zsp, _locals)
    return cmr__uimm.compile_extra(func)
