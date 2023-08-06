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
        fgou__gich = 'bodo' if distributed else 'bodo_seq'
        fgou__gich = (fgou__gich + '_inline' if inline_calls_pass else
            fgou__gich)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, fgou__gich
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
    for fjuz__pyo, (yhy__uys, ryxhh__ktu) in enumerate(pm.passes):
        if yhy__uys == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(fjuz__pyo, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for fjuz__pyo, (yhy__uys, ryxhh__ktu) in enumerate(pm.passes):
        if yhy__uys == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[fjuz__pyo] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for fjuz__pyo, (yhy__uys, ryxhh__ktu) in enumerate(pm.passes):
        if yhy__uys == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(fjuz__pyo)
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
    kyux__wpbde = guard(get_definition, func_ir, rhs.func)
    if isinstance(kyux__wpbde, (ir.Global, ir.FreeVar, ir.Const)):
        wntse__emp = kyux__wpbde.value
    else:
        zfrcr__vlbpm = guard(find_callname, func_ir, rhs)
        if not (zfrcr__vlbpm and isinstance(zfrcr__vlbpm[0], str) and
            isinstance(zfrcr__vlbpm[1], str)):
            return
        func_name, func_mod = zfrcr__vlbpm
        try:
            import importlib
            tlvhk__npbn = importlib.import_module(func_mod)
            wntse__emp = getattr(tlvhk__npbn, func_name)
        except:
            return
    if isinstance(wntse__emp, CPUDispatcher) and issubclass(wntse__emp.
        _compiler.pipeline_class, BodoCompiler
        ) and wntse__emp._compiler.pipeline_class != BodoCompilerUDF:
        wntse__emp._compiler.pipeline_class = BodoCompilerUDF
        wntse__emp.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for bqvbe__zcqkc in block.body:
                if is_call_assign(bqvbe__zcqkc):
                    _convert_bodo_dispatcher_to_udf(bqvbe__zcqkc.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        zrrpr__zntv = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        zrrpr__zntv.run()
        return True


def _update_definitions(func_ir, node_list):
    uyud__yukx = ir.Loc('', 0)
    gkx__mqv = ir.Block(ir.Scope(None, uyud__yukx), uyud__yukx)
    gkx__mqv.body = node_list
    build_definitions({(0): gkx__mqv}, func_ir._definitions)


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
        vnxly__rsjeq = 'overload_series_' + rhs.attr
        ikwi__jmit = getattr(bodo.hiframes.series_impl, vnxly__rsjeq)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        vnxly__rsjeq = 'overload_dataframe_' + rhs.attr
        ikwi__jmit = getattr(bodo.hiframes.dataframe_impl, vnxly__rsjeq)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    vppc__aaz = ikwi__jmit(rhs_type)
    zpkh__avuca = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc
        )
    nouc__ncq = compile_func_single_block(vppc__aaz, (rhs.value,), stmt.
        target, zpkh__avuca)
    _update_definitions(func_ir, nouc__ncq)
    new_body += nouc__ncq
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
        yqbe__wiez = tuple(typemap[msay__qadk.name] for msay__qadk in rhs.args)
        zmrru__htc = {fgou__gich: typemap[msay__qadk.name] for fgou__gich,
            msay__qadk in dict(rhs.kws).items()}
        vppc__aaz = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*yqbe__wiez, **zmrru__htc)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        yqbe__wiez = tuple(typemap[msay__qadk.name] for msay__qadk in rhs.args)
        zmrru__htc = {fgou__gich: typemap[msay__qadk.name] for fgou__gich,
            msay__qadk in dict(rhs.kws).items()}
        vppc__aaz = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*yqbe__wiez, **zmrru__htc)
    else:
        return False
    swc__fpkp = replace_func(pass_info, vppc__aaz, rhs.args, pysig=numba.
        core.utils.pysignature(vppc__aaz), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    xnlm__gpse, ryxhh__ktu = inline_closure_call(func_ir, swc__fpkp.glbls,
        block, len(new_body), swc__fpkp.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=swc__fpkp.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for azb__daerl in xnlm__gpse.values():
        azb__daerl.loc = rhs.loc
        update_locs(azb__daerl.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    gbr__gvgg = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = gbr__gvgg(func_ir, typemap)
    csgel__bwmrq = func_ir.blocks
    work_list = list((pvhv__pgfu, csgel__bwmrq[pvhv__pgfu]) for pvhv__pgfu in
        reversed(csgel__bwmrq.keys()))
    while work_list:
        elpm__mnxc, block = work_list.pop()
        new_body = []
        anhcf__lmc = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                zfrcr__vlbpm = guard(find_callname, func_ir, rhs, typemap)
                if zfrcr__vlbpm is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = zfrcr__vlbpm
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    anhcf__lmc = True
                    break
            new_body.append(stmt)
        if not anhcf__lmc:
            csgel__bwmrq[elpm__mnxc].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        rob__xkpmm = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = rob__xkpmm.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        lgrbv__ess = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        lgrbv__ess.run()
        lgrbv__ess.run()
        lgrbv__ess.run()
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        nuinx__fjm = 0
        qrrrw__ucemt = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            nuinx__fjm = int(os.environ[qrrrw__ucemt])
        except:
            pass
        if nuinx__fjm > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(nuinx__fjm,
                state.metadata)
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
        zpkh__avuca = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, zpkh__avuca)
        for block in state.func_ir.blocks.values():
            new_body = []
            for bqvbe__zcqkc in block.body:
                if type(bqvbe__zcqkc) in distributed_run_extensions:
                    uerr__sxao = distributed_run_extensions[type(bqvbe__zcqkc)]
                    jkb__sga = uerr__sxao(bqvbe__zcqkc, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += jkb__sga
                elif is_call_assign(bqvbe__zcqkc):
                    rhs = bqvbe__zcqkc.value
                    zfrcr__vlbpm = guard(find_callname, state.func_ir, rhs)
                    if zfrcr__vlbpm == ('gatherv', 'bodo') or zfrcr__vlbpm == (
                        'allgatherv', 'bodo'):
                        bqvbe__zcqkc.value = rhs.args[0]
                    new_body.append(bqvbe__zcqkc)
                else:
                    new_body.append(bqvbe__zcqkc)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        jtfh__httph = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return jtfh__httph.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    mizg__efd = set()
    while work_list:
        elpm__mnxc, block = work_list.pop()
        mizg__efd.add(elpm__mnxc)
        for i, rjyaj__ieuzh in enumerate(block.body):
            if isinstance(rjyaj__ieuzh, ir.Assign):
                cmprc__wda = rjyaj__ieuzh.value
                if isinstance(cmprc__wda, ir.Expr) and cmprc__wda.op == 'call':
                    kyux__wpbde = guard(get_definition, func_ir, cmprc__wda
                        .func)
                    if isinstance(kyux__wpbde, (ir.Global, ir.FreeVar)
                        ) and isinstance(kyux__wpbde.value, CPUDispatcher
                        ) and issubclass(kyux__wpbde.value._compiler.
                        pipeline_class, BodoCompiler):
                        yczjq__fnza = kyux__wpbde.value.py_func
                        arg_types = None
                        if typingctx:
                            knm__wem = dict(cmprc__wda.kws)
                            ajh__ggtre = tuple(typemap[msay__qadk.name] for
                                msay__qadk in cmprc__wda.args)
                            npjym__kcj = {vkrto__lntvp: typemap[msay__qadk.
                                name] for vkrto__lntvp, msay__qadk in
                                knm__wem.items()}
                            ryxhh__ktu, arg_types = (kyux__wpbde.value.
                                fold_argument_types(ajh__ggtre, npjym__kcj))
                        ryxhh__ktu, xlt__kuvz = inline_closure_call(func_ir,
                            yczjq__fnza.__globals__, block, i, yczjq__fnza,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((xlt__kuvz[vkrto__lntvp].name,
                            msay__qadk) for vkrto__lntvp, msay__qadk in
                            kyux__wpbde.value.locals.items() if 
                            vkrto__lntvp in xlt__kuvz)
                        break
    return mizg__efd


def udf_jit(signature_or_function=None, **options):
    wgais__fty = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=wgais__fty,
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
    for fjuz__pyo, (yhy__uys, ryxhh__ktu) in enumerate(pm.passes):
        if yhy__uys == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:fjuz__pyo + 1]
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
    mmm__wxd = None
    abs__rdbef = None
    _locals = {}
    ehnql__ihllu = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(ehnql__ihllu, arg_types,
        kw_types)
    ubo__zwuc = numba.core.compiler.Flags()
    llq__ogr = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    fyo__dzhqe = {'nopython': True, 'boundscheck': False, 'parallel': llq__ogr}
    numba.core.registry.cpu_target.options.parse_as_flags(ubo__zwuc, fyo__dzhqe
        )
    bwcuz__epp = TyperCompiler(typingctx, targetctx, mmm__wxd, args,
        abs__rdbef, ubo__zwuc, _locals)
    return bwcuz__epp.compile_extra(func)
