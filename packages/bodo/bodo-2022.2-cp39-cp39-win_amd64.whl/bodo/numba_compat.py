"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.typing import BodoError
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    xbt__uaby = numba.core.bytecode.FunctionIdentity.from_function(func)
    pxad__psd = numba.core.interpreter.Interpreter(xbt__uaby)
    lyn__zojb = numba.core.bytecode.ByteCode(func_id=xbt__uaby)
    func_ir = pxad__psd.interpret(lyn__zojb)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        tbst__qcw = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        tbst__qcw.run()
    fsxk__hlgr = numba.core.postproc.PostProcessor(func_ir)
    fsxk__hlgr.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, atcvr__dzl in visit_vars_extensions.items():
        if isinstance(stmt, t):
            atcvr__dzl(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    bpd__zne = ['ravel', 'transpose', 'reshape']
    for axefs__ljpxc in blocks.values():
        for sdrjc__qsxm in axefs__ljpxc.body:
            if type(sdrjc__qsxm) in alias_analysis_extensions:
                atcvr__dzl = alias_analysis_extensions[type(sdrjc__qsxm)]
                atcvr__dzl(sdrjc__qsxm, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(sdrjc__qsxm, ir.Assign):
                lqiyz__kwyz = sdrjc__qsxm.value
                trgoo__bzz = sdrjc__qsxm.target.name
                if is_immutable_type(trgoo__bzz, typemap):
                    continue
                if isinstance(lqiyz__kwyz, ir.Var
                    ) and trgoo__bzz != lqiyz__kwyz.name:
                    _add_alias(trgoo__bzz, lqiyz__kwyz.name, alias_map,
                        arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr) and (lqiyz__kwyz.op ==
                    'cast' or lqiyz__kwyz.op in ['getitem', 'static_getitem']):
                    _add_alias(trgoo__bzz, lqiyz__kwyz.value.name,
                        alias_map, arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr
                    ) and lqiyz__kwyz.op == 'inplace_binop':
                    _add_alias(trgoo__bzz, lqiyz__kwyz.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr
                    ) and lqiyz__kwyz.op == 'getattr' and lqiyz__kwyz.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(trgoo__bzz, lqiyz__kwyz.value.name,
                        alias_map, arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr
                    ) and lqiyz__kwyz.op == 'getattr' and lqiyz__kwyz.attr not in [
                    'shape'] and lqiyz__kwyz.value.name in arg_aliases:
                    _add_alias(trgoo__bzz, lqiyz__kwyz.value.name,
                        alias_map, arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr
                    ) and lqiyz__kwyz.op == 'getattr' and lqiyz__kwyz.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(trgoo__bzz, lqiyz__kwyz.value.name,
                        alias_map, arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr) and lqiyz__kwyz.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(trgoo__bzz, typemap):
                    for tlqvk__ldjw in lqiyz__kwyz.items:
                        _add_alias(trgoo__bzz, tlqvk__ldjw.name, alias_map,
                            arg_aliases)
                if isinstance(lqiyz__kwyz, ir.Expr
                    ) and lqiyz__kwyz.op == 'call':
                    yof__qrv = guard(find_callname, func_ir, lqiyz__kwyz,
                        typemap)
                    if yof__qrv is None:
                        continue
                    kvbsr__zfv, qxpzl__ofwx = yof__qrv
                    if yof__qrv in alias_func_extensions:
                        pikt__cbf = alias_func_extensions[yof__qrv]
                        pikt__cbf(trgoo__bzz, lqiyz__kwyz.args, alias_map,
                            arg_aliases)
                    if qxpzl__ofwx == 'numpy' and kvbsr__zfv in bpd__zne:
                        _add_alias(trgoo__bzz, lqiyz__kwyz.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(qxpzl__ofwx, ir.Var
                        ) and kvbsr__zfv in bpd__zne:
                        _add_alias(trgoo__bzz, qxpzl__ofwx.name, alias_map,
                            arg_aliases)
    dir__rbf = copy.deepcopy(alias_map)
    for tlqvk__ldjw in dir__rbf:
        for imwpw__bbus in dir__rbf[tlqvk__ldjw]:
            alias_map[tlqvk__ldjw] |= alias_map[imwpw__bbus]
        for imwpw__bbus in dir__rbf[tlqvk__ldjw]:
            alias_map[imwpw__bbus] = alias_map[tlqvk__ldjw]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    tclay__jzmoh = compute_cfg_from_blocks(func_ir.blocks)
    dfo__faaj = compute_use_defs(func_ir.blocks)
    nfqcd__rrope = compute_live_map(tclay__jzmoh, func_ir.blocks, dfo__faaj
        .usemap, dfo__faaj.defmap)
    asop__seti = True
    while asop__seti:
        asop__seti = False
        for dmzf__abas, block in func_ir.blocks.items():
            lives = {tlqvk__ldjw.name for tlqvk__ldjw in block.terminator.
                list_vars()}
            for vwpvl__qxrg, jdr__kqc in tclay__jzmoh.successors(dmzf__abas):
                lives |= nfqcd__rrope[vwpvl__qxrg]
            ljaym__sklk = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    trgoo__bzz = stmt.target
                    guqhf__ikbya = stmt.value
                    if trgoo__bzz.name not in lives:
                        if isinstance(guqhf__ikbya, ir.Expr
                            ) and guqhf__ikbya.op == 'make_function':
                            continue
                        if isinstance(guqhf__ikbya, ir.Expr
                            ) and guqhf__ikbya.op == 'getattr':
                            continue
                        if isinstance(guqhf__ikbya, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(trgoo__bzz,
                            None), types.Function):
                            continue
                        if isinstance(guqhf__ikbya, ir.Expr
                            ) and guqhf__ikbya.op == 'build_map':
                            continue
                    if isinstance(guqhf__ikbya, ir.Var
                        ) and trgoo__bzz.name == guqhf__ikbya.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    ywnz__lli = analysis.ir_extension_usedefs[type(stmt)]
                    dbuh__pfw, ugsk__whgmy = ywnz__lli(stmt)
                    lives -= ugsk__whgmy
                    lives |= dbuh__pfw
                else:
                    lives |= {tlqvk__ldjw.name for tlqvk__ldjw in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(trgoo__bzz.name)
                ljaym__sklk.append(stmt)
            ljaym__sklk.reverse()
            if len(block.body) != len(ljaym__sklk):
                asop__seti = True
            block.body = ljaym__sklk


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    fhntm__jbl = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (fhntm__jbl,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    pit__kij = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), pit__kij)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for qbiq__cbt in fnty.templates:
                self._inline_overloads.update(qbiq__cbt._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    pit__kij = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), pit__kij)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    iaq__qer, itmt__bsw = self._get_impl(args, kws)
    if iaq__qer is None:
        return
    qsh__pjx = types.Dispatcher(iaq__qer)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        wjya__sxve = iaq__qer._compiler
        flags = compiler.Flags()
        ncxtx__gir = wjya__sxve.targetdescr.typing_context
        eaizd__neb = wjya__sxve.targetdescr.target_context
        awvcy__pvib = wjya__sxve.pipeline_class(ncxtx__gir, eaizd__neb,
            None, None, None, flags, None)
        kyny__yqo = InlineWorker(ncxtx__gir, eaizd__neb, wjya__sxve.locals,
            awvcy__pvib, flags, None)
        pow__woo = qsh__pjx.dispatcher.get_call_template
        qbiq__cbt, bsrb__bzr, qqjo__qyy, kws = pow__woo(itmt__bsw, kws)
        if qqjo__qyy in self._inline_overloads:
            return self._inline_overloads[qqjo__qyy]['iinfo'].signature
        ir = kyny__yqo.run_untyped_passes(qsh__pjx.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, eaizd__neb, ir, qqjo__qyy, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, qqjo__qyy, None)
        self._inline_overloads[sig.args] = {'folded_args': qqjo__qyy}
        gnggh__qjov = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = gnggh__qjov
        if not self._inline.is_always_inline:
            sig = qsh__pjx.get_call_type(self.context, itmt__bsw, kws)
            self._compiled_overloads[sig.args] = qsh__pjx.get_overload(sig)
        ijqs__tnzuc = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': qqjo__qyy,
            'iinfo': ijqs__tnzuc}
    else:
        sig = qsh__pjx.get_call_type(self.context, itmt__bsw, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = qsh__pjx.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    ugcu__mvhpb = [True, False]
    jbmz__hbu = [False, True]
    igaa__fwwxu = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    sim__duhv = get_local_target(context)
    wsic__qwzw = utils.order_by_target_specificity(sim__duhv, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for kgs__cpcjw in wsic__qwzw:
        fuv__nhxb = kgs__cpcjw(context)
        xtjx__eygr = ugcu__mvhpb if fuv__nhxb.prefer_literal else jbmz__hbu
        xtjx__eygr = [True] if getattr(fuv__nhxb, '_no_unliteral', False
            ) else xtjx__eygr
        for zodp__xawk in xtjx__eygr:
            try:
                if zodp__xawk:
                    sig = fuv__nhxb.apply(args, kws)
                else:
                    hzhy__uzqsv = tuple([_unlit_non_poison(a) for a in args])
                    hkbt__jvc = {xcjtl__nmml: _unlit_non_poison(tlqvk__ldjw
                        ) for xcjtl__nmml, tlqvk__ldjw in kws.items()}
                    sig = fuv__nhxb.apply(hzhy__uzqsv, hkbt__jvc)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    igaa__fwwxu.add_error(fuv__nhxb, False, e, zodp__xawk)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = fuv__nhxb.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    hiwwn__qyde = getattr(fuv__nhxb, 'cases', None)
                    if hiwwn__qyde is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            hiwwn__qyde)
                    else:
                        msg = 'No match.'
                    igaa__fwwxu.add_error(fuv__nhxb, True, msg, zodp__xawk)
    igaa__fwwxu.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    qbiq__cbt = self.template(context)
    afko__rumf = None
    ocxb__kmvc = None
    wzoak__lxb = None
    xtjx__eygr = [True, False] if qbiq__cbt.prefer_literal else [False, True]
    xtjx__eygr = [True] if getattr(qbiq__cbt, '_no_unliteral', False
        ) else xtjx__eygr
    for zodp__xawk in xtjx__eygr:
        if zodp__xawk:
            try:
                wzoak__lxb = qbiq__cbt.apply(args, kws)
            except Exception as nzfpc__xgow:
                if isinstance(nzfpc__xgow, errors.ForceLiteralArg):
                    raise nzfpc__xgow
                afko__rumf = nzfpc__xgow
                wzoak__lxb = None
            else:
                break
        else:
            lmdt__aco = tuple([_unlit_non_poison(a) for a in args])
            xsezr__wip = {xcjtl__nmml: _unlit_non_poison(tlqvk__ldjw) for 
                xcjtl__nmml, tlqvk__ldjw in kws.items()}
            rxcq__xyz = lmdt__aco == args and kws == xsezr__wip
            if not rxcq__xyz and wzoak__lxb is None:
                try:
                    wzoak__lxb = qbiq__cbt.apply(lmdt__aco, xsezr__wip)
                except Exception as nzfpc__xgow:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        nzfpc__xgow, errors.NumbaError):
                        raise nzfpc__xgow
                    if isinstance(nzfpc__xgow, errors.ForceLiteralArg):
                        if qbiq__cbt.prefer_literal:
                            raise nzfpc__xgow
                    ocxb__kmvc = nzfpc__xgow
                else:
                    break
    if wzoak__lxb is None and (ocxb__kmvc is not None or afko__rumf is not None
        ):
        ondmd__bdzw = '- Resolution failure for {} arguments:\n{}\n'
        mdln__avzba = _termcolor.highlight(ondmd__bdzw)
        if numba.core.config.DEVELOPER_MODE:
            gpbd__kiohi = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    ehiup__hqu = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    ehiup__hqu = ['']
                yqett__zlxp = '\n{}'.format(2 * gpbd__kiohi)
                dzirk__bgwab = _termcolor.reset(yqett__zlxp + yqett__zlxp.
                    join(_bt_as_lines(ehiup__hqu)))
                return _termcolor.reset(dzirk__bgwab)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            eiui__lwvv = str(e)
            eiui__lwvv = eiui__lwvv if eiui__lwvv else str(repr(e)) + add_bt(e)
            muu__uxbng = errors.TypingError(textwrap.dedent(eiui__lwvv))
            return mdln__avzba.format(literalness, str(muu__uxbng))
        import bodo
        if isinstance(afko__rumf, bodo.utils.typing.BodoError):
            raise afko__rumf
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', afko__rumf) +
                nested_msg('non-literal', ocxb__kmvc))
        else:
            msg = 'Compilation error for '
            if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                DataFrameType):
                msg += 'DataFrame.'
            elif isinstance(self.this, bodo.hiframes.pd_series_ext.SeriesType):
                msg += 'Series.'
            msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg)
    return wzoak__lxb


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite.llvmpy.core import Type
    fnty = Type.function(self.pyobj, [self.cstring, self.py_ssize_t])
    kvbsr__zfv = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=kvbsr__zfv)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            ylch__umq = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), ylch__umq)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    myzd__kwns = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            myzd__kwns.append(types.Omitted(a.value))
        else:
            myzd__kwns.append(self.typeof_pyval(a))
    vces__rnwh = None
    try:
        error = None
        vces__rnwh = self.compile(tuple(myzd__kwns))
    except errors.ForceLiteralArg as e:
        zuj__ljpct = [vuhv__madoy for vuhv__madoy in e.requested_args if 
            isinstance(args[vuhv__madoy], types.Literal) and not isinstance
            (args[vuhv__madoy], types.LiteralStrKeyDict)]
        if zuj__ljpct:
            grx__pqlma = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            gnqhz__himfx = ', '.join('Arg #{} is {}'.format(vuhv__madoy,
                args[vuhv__madoy]) for vuhv__madoy in sorted(zuj__ljpct))
            raise errors.CompilerError(grx__pqlma.format(gnqhz__himfx))
        itmt__bsw = []
        try:
            for vuhv__madoy, tlqvk__ldjw in enumerate(args):
                if vuhv__madoy in e.requested_args:
                    if vuhv__madoy in e.file_infos:
                        itmt__bsw.append(types.FilenameType(args[
                            vuhv__madoy], e.file_infos[vuhv__madoy]))
                    else:
                        itmt__bsw.append(types.literal(args[vuhv__madoy]))
                else:
                    itmt__bsw.append(args[vuhv__madoy])
            args = itmt__bsw
        except (OSError, FileNotFoundError) as hxg__yar:
            error = FileNotFoundError(str(hxg__yar) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                vces__rnwh = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        rllo__fewxq = []
        for vuhv__madoy, dcwuu__qajc in enumerate(args):
            val = dcwuu__qajc.value if isinstance(dcwuu__qajc, numba.core.
                dispatcher.OmittedArg) else dcwuu__qajc
            try:
                kof__cpshn = typeof(val, Purpose.argument)
            except ValueError as rlqe__doox:
                rllo__fewxq.append((vuhv__madoy, str(rlqe__doox)))
            else:
                if kof__cpshn is None:
                    rllo__fewxq.append((vuhv__madoy,
                        f'cannot determine Numba type of value {val}'))
        if rllo__fewxq:
            eoxpu__qzc = '\n'.join(
                f'- argument {vuhv__madoy}: {juci__dnwk}' for vuhv__madoy,
                juci__dnwk in rllo__fewxq)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{eoxpu__qzc}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                ghrx__cgui = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'numba', 'Overload',
                    'lowering']
                htnbq__spjc = False
                for xhbo__flx in ghrx__cgui:
                    if xhbo__flx in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        htnbq__spjc = True
                        break
                if not htnbq__spjc:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                ylch__umq = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), ylch__umq)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return vces__rnwh


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for jtij__lpmz in cres.library._codegen._engine._defined_symbols:
        if jtij__lpmz.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in jtij__lpmz and (
            'bodo_gb_udf_update_local' in jtij__lpmz or 
            'bodo_gb_udf_combine' in jtij__lpmz or 'bodo_gb_udf_eval' in
            jtij__lpmz or 'bodo_gb_apply_general_udfs' in jtij__lpmz):
            gb_agg_cfunc_addr[jtij__lpmz
                ] = cres.library.get_pointer_to_function(jtij__lpmz)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for jtij__lpmz in cres.library._codegen._engine._defined_symbols:
        if jtij__lpmz.startswith('cfunc') and ('get_join_cond_addr' not in
            jtij__lpmz or 'bodo_join_gen_cond' in jtij__lpmz):
            join_gen_cond_cfunc_addr[jtij__lpmz
                ] = cres.library.get_pointer_to_function(jtij__lpmz)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    iaq__qer = self._get_dispatcher_for_current_target()
    if iaq__qer is not self:
        return iaq__qer.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            lsh__tkb = self.overloads.get(tuple(args))
            if lsh__tkb is not None:
                return lsh__tkb.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            jxtt__vhizb = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=jxtt__vhizb):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    ytek__mlco = self._final_module
    rfy__rpim = []
    sia__kpfg = 0
    for fn in ytek__mlco.functions:
        sia__kpfg += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            rfy__rpim.append(fn.name)
    if sia__kpfg == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if rfy__rpim:
        ytek__mlco = ytek__mlco.clone()
        for name in rfy__rpim:
            ytek__mlco.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = ytek__mlco
    return ytek__mlco


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for ygnuk__sju in self.constraints:
        loc = ygnuk__sju.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                ygnuk__sju(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                fvfp__ihmih = numba.core.errors.TypingError(str(e), loc=
                    ygnuk__sju.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(fvfp__ihmih, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    fvfp__ihmih = numba.core.errors.TypingError(msg.format(
                        con=ygnuk__sju, err=str(e)), loc=ygnuk__sju.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(fvfp__ihmih, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for rctwz__och in self._failures.values():
        for fecfm__johb in rctwz__och:
            if isinstance(fecfm__johb.error, ForceLiteralArg):
                raise fecfm__johb.error
            if isinstance(fecfm__johb.error, bodo.utils.typing.BodoError):
                raise fecfm__johb.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    tiw__cybla = False
    ljaym__sklk = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        eovz__osgwl = set()
        ivh__rkag = lives & alias_set
        for tlqvk__ldjw in ivh__rkag:
            eovz__osgwl |= alias_map[tlqvk__ldjw]
        lives_n_aliases = lives | eovz__osgwl | arg_aliases
        if type(stmt) in remove_dead_extensions:
            atcvr__dzl = remove_dead_extensions[type(stmt)]
            stmt = atcvr__dzl(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                tiw__cybla = True
                continue
        if isinstance(stmt, ir.Assign):
            trgoo__bzz = stmt.target
            guqhf__ikbya = stmt.value
            if trgoo__bzz.name not in lives and has_no_side_effect(guqhf__ikbya
                , lives_n_aliases, call_table):
                tiw__cybla = True
                continue
            if saved_array_analysis and trgoo__bzz.name in lives and is_expr(
                guqhf__ikbya, 'getattr'
                ) and guqhf__ikbya.attr == 'shape' and is_array_typ(typemap
                [guqhf__ikbya.value.name]
                ) and guqhf__ikbya.value.name not in lives:
                fsjhi__dkare = {tlqvk__ldjw: xcjtl__nmml for xcjtl__nmml,
                    tlqvk__ldjw in func_ir.blocks.items()}
                if block in fsjhi__dkare:
                    dmzf__abas = fsjhi__dkare[block]
                    vtbir__fhaqn = saved_array_analysis.get_equiv_set(
                        dmzf__abas)
                    opj__esmb = vtbir__fhaqn.get_equiv_set(guqhf__ikbya.value)
                    if opj__esmb is not None:
                        for tlqvk__ldjw in opj__esmb:
                            if tlqvk__ldjw.endswith('#0'):
                                tlqvk__ldjw = tlqvk__ldjw[:-2]
                            if tlqvk__ldjw in typemap and is_array_typ(typemap
                                [tlqvk__ldjw]) and tlqvk__ldjw in lives:
                                guqhf__ikbya.value = ir.Var(guqhf__ikbya.
                                    value.scope, tlqvk__ldjw, guqhf__ikbya.
                                    value.loc)
                                tiw__cybla = True
                                break
            if isinstance(guqhf__ikbya, ir.Var
                ) and trgoo__bzz.name == guqhf__ikbya.name:
                tiw__cybla = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                tiw__cybla = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            ywnz__lli = analysis.ir_extension_usedefs[type(stmt)]
            dbuh__pfw, ugsk__whgmy = ywnz__lli(stmt)
            lives -= ugsk__whgmy
            lives |= dbuh__pfw
        else:
            lives |= {tlqvk__ldjw.name for tlqvk__ldjw in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                mkq__yuro = set()
                if isinstance(guqhf__ikbya, ir.Expr):
                    mkq__yuro = {tlqvk__ldjw.name for tlqvk__ldjw in
                        guqhf__ikbya.list_vars()}
                if trgoo__bzz.name not in mkq__yuro:
                    lives.remove(trgoo__bzz.name)
        ljaym__sklk.append(stmt)
    ljaym__sklk.reverse()
    block.body = ljaym__sklk
    return tiw__cybla


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            bktt__uzlkg, = args
            if isinstance(bktt__uzlkg, types.IterableType):
                dtype = bktt__uzlkg.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), bktt__uzlkg)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    olv__pxj = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (olv__pxj, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as qkv__gpk:
            return
    try:
        return literal(value)
    except LiteralTypingError as qkv__gpk:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        xds__yunmw = py_func.__qualname__
    except AttributeError as qkv__gpk:
        xds__yunmw = py_func.__name__
    kiubx__zalvi = inspect.getfile(py_func)
    for cls in self._locator_classes:
        fypmp__lqgz = cls.from_function(py_func, kiubx__zalvi)
        if fypmp__lqgz is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (xds__yunmw, kiubx__zalvi))
    self._locator = fypmp__lqgz
    kxckz__duw = inspect.getfile(py_func)
    qbv__obnhw = os.path.splitext(os.path.basename(kxckz__duw))[0]
    if kiubx__zalvi.startswith('<ipython-'):
        wuk__dhvtp = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', qbv__obnhw, count=1)
        if wuk__dhvtp == qbv__obnhw:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        qbv__obnhw = wuk__dhvtp
    snf__kiqd = '%s.%s' % (qbv__obnhw, xds__yunmw)
    qbyd__vahyv = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(snf__kiqd, qbyd__vahyv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    xpnj__xnysz = list(filter(lambda a: self._istuple(a.name), args))
    if len(xpnj__xnysz) == 2 and fn.__name__ == 'add':
        bkdvt__wcni = self.typemap[xpnj__xnysz[0].name]
        aabj__rwznu = self.typemap[xpnj__xnysz[1].name]
        if bkdvt__wcni.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                xpnj__xnysz[1]))
        if aabj__rwznu.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                xpnj__xnysz[0]))
        try:
            zoyx__mlxp = [equiv_set.get_shape(x) for x in xpnj__xnysz]
            if None in zoyx__mlxp:
                return None
            goi__frccf = sum(zoyx__mlxp, ())
            return ArrayAnalysis.AnalyzeResult(shape=goi__frccf)
        except GuardException as qkv__gpk:
            return None
    gpdq__ileui = list(filter(lambda a: self._isarray(a.name), args))
    require(len(gpdq__ileui) > 0)
    upx__tfam = [x.name for x in gpdq__ileui]
    ycykv__ywzva = [self.typemap[x.name].ndim for x in gpdq__ileui]
    mwo__tvab = max(ycykv__ywzva)
    require(mwo__tvab > 0)
    zoyx__mlxp = [equiv_set.get_shape(x) for x in gpdq__ileui]
    if any(a is None for a in zoyx__mlxp):
        return ArrayAnalysis.AnalyzeResult(shape=gpdq__ileui[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, gpdq__ileui))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, zoyx__mlxp,
        upx__tfam)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    htsix__bmfu = code_obj.code
    euvqo__bpki = len(htsix__bmfu.co_freevars)
    ujy__hhs = htsix__bmfu.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        tpajh__idkg, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ujy__hhs = [tlqvk__ldjw.name for tlqvk__ldjw in tpajh__idkg]
    uxdpy__lya = caller_ir.func_id.func.__globals__
    try:
        uxdpy__lya = getattr(code_obj, 'globals', uxdpy__lya)
    except KeyError as qkv__gpk:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/udfs.html"
        )
    yntqy__yage = []
    for x in ujy__hhs:
        try:
            emzdd__pxaxl = caller_ir.get_definition(x)
        except KeyError as qkv__gpk:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(emzdd__pxaxl, (ir.Const, ir.Global, ir.FreeVar)):
            val = emzdd__pxaxl.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                fhntm__jbl = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                uxdpy__lya[fhntm__jbl] = bodo.jit(distributed=False)(val)
                uxdpy__lya[fhntm__jbl].is_nested_func = True
                val = fhntm__jbl
            if isinstance(val, CPUDispatcher):
                fhntm__jbl = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                uxdpy__lya[fhntm__jbl] = val
                val = fhntm__jbl
            yntqy__yage.append(val)
        elif isinstance(emzdd__pxaxl, ir.Expr
            ) and emzdd__pxaxl.op == 'make_function':
            niy__tdx = convert_code_obj_to_function(emzdd__pxaxl, caller_ir)
            fhntm__jbl = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            uxdpy__lya[fhntm__jbl] = bodo.jit(distributed=False)(niy__tdx)
            uxdpy__lya[fhntm__jbl].is_nested_func = True
            yntqy__yage.append(fhntm__jbl)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    cwo__pjy = '\n'.join([('\tc_%d = %s' % (vuhv__madoy, x)) for 
        vuhv__madoy, x in enumerate(yntqy__yage)])
    dnzvl__gzjl = ','.join([('c_%d' % vuhv__madoy) for vuhv__madoy in range
        (euvqo__bpki)])
    namae__lrv = list(htsix__bmfu.co_varnames)
    ktlno__dgjnl = 0
    zxto__bghc = htsix__bmfu.co_argcount
    kodee__hkl = caller_ir.get_definition(code_obj.defaults)
    if kodee__hkl is not None:
        if isinstance(kodee__hkl, tuple):
            vjohf__dle = [caller_ir.get_definition(x).value for x in kodee__hkl
                ]
            wiue__hozmb = tuple(vjohf__dle)
        else:
            vjohf__dle = [caller_ir.get_definition(x).value for x in
                kodee__hkl.items]
            wiue__hozmb = tuple(vjohf__dle)
        ktlno__dgjnl = len(wiue__hozmb)
    crvr__aqi = zxto__bghc - ktlno__dgjnl
    pfqp__kkjpj = ','.join([('%s' % namae__lrv[vuhv__madoy]) for
        vuhv__madoy in range(crvr__aqi)])
    if ktlno__dgjnl:
        zzcy__rxp = [('%s = %s' % (namae__lrv[vuhv__madoy + crvr__aqi],
            wiue__hozmb[vuhv__madoy])) for vuhv__madoy in range(ktlno__dgjnl)]
        pfqp__kkjpj += ', '
        pfqp__kkjpj += ', '.join(zzcy__rxp)
    return _create_function_from_code_obj(htsix__bmfu, cwo__pjy,
        pfqp__kkjpj, dnzvl__gzjl, uxdpy__lya)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for qnm__izju, (acla__njk, vdlm__ccxmx) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % vdlm__ccxmx)
            vyxh__xplj = _pass_registry.get(acla__njk).pass_inst
            if isinstance(vyxh__xplj, CompilerPass):
                self._runPass(qnm__izju, vyxh__xplj, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, vdlm__ccxmx)
                ljgc__bvfr = self._patch_error(msg, e)
                raise ljgc__bvfr
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    mnqj__wmo = None
    ugsk__whgmy = {}

    def lookup(var, already_seen, varonly=True):
        val = ugsk__whgmy.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    zxzt__rts = reduction_node.unversioned_name
    for vuhv__madoy, stmt in enumerate(nodes):
        trgoo__bzz = stmt.target
        guqhf__ikbya = stmt.value
        ugsk__whgmy[trgoo__bzz.name] = guqhf__ikbya
        if isinstance(guqhf__ikbya, ir.Var
            ) and guqhf__ikbya.name in ugsk__whgmy:
            guqhf__ikbya = lookup(guqhf__ikbya, set())
        if isinstance(guqhf__ikbya, ir.Expr):
            qwlg__ihd = set(lookup(tlqvk__ldjw, set(), True).name for
                tlqvk__ldjw in guqhf__ikbya.list_vars())
            if name in qwlg__ihd:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(guqhf__ikbya)]
                renxb__phpbn = [x for x, uclix__bjvs in args if uclix__bjvs
                    .name != name]
                args = [(x, uclix__bjvs) for x, uclix__bjvs in args if x !=
                    uclix__bjvs.name]
                agq__fndv = dict(args)
                if len(renxb__phpbn) == 1:
                    agq__fndv[renxb__phpbn[0]] = ir.Var(trgoo__bzz.scope, 
                        name + '#init', trgoo__bzz.loc)
                replace_vars_inner(guqhf__ikbya, agq__fndv)
                mnqj__wmo = nodes[vuhv__madoy:]
                break
    return mnqj__wmo


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        sbbb__vavqf = expand_aliases({tlqvk__ldjw.name for tlqvk__ldjw in
            stmt.list_vars()}, alias_map, arg_aliases)
        hfvx__vcn = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        xddqi__iqbed = expand_aliases({tlqvk__ldjw.name for tlqvk__ldjw in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        xanfy__pfaa = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(hfvx__vcn & xddqi__iqbed | xanfy__pfaa & sbbb__vavqf) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    bwr__zcuji = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            bwr__zcuji.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                bwr__zcuji.update(get_parfor_writes(stmt, func_ir))
    return bwr__zcuji


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    bwr__zcuji = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        bwr__zcuji.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        bwr__zcuji = {tlqvk__ldjw.name for tlqvk__ldjw in stmt.df_out_vars.
            values()}
        if stmt.out_key_vars is not None:
            bwr__zcuji.update({tlqvk__ldjw.name for tlqvk__ldjw in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        bwr__zcuji = {tlqvk__ldjw.name for tlqvk__ldjw in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        bwr__zcuji = {tlqvk__ldjw.name for tlqvk__ldjw in stmt.
            out_data_vars.values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            bwr__zcuji.update({tlqvk__ldjw.name for tlqvk__ldjw in stmt.
                out_key_arrs})
            bwr__zcuji.update({tlqvk__ldjw.name for tlqvk__ldjw in stmt.
                df_out_vars.values()})
    if is_call_assign(stmt):
        yof__qrv = guard(find_callname, func_ir, stmt.value)
        if yof__qrv in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'), (
            'setna', 'bodo.libs.array_kernels'), ('str_arr_item_to_numeric',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_int_to_str',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_NA_str',
            'bodo.libs.str_arr_ext'), ('str_arr_set_not_na',
            'bodo.libs.str_arr_ext'), ('get_str_arr_item_copy',
            'bodo.libs.str_arr_ext'), ('set_bit_to_arr',
            'bodo.libs.int_arr_ext')):
            bwr__zcuji.add(stmt.value.args[0].name)
    return bwr__zcuji


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        atcvr__dzl = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        ggwi__bgbc = atcvr__dzl.format(self, msg)
        self.args = ggwi__bgbc,
    else:
        atcvr__dzl = _termcolor.errmsg('{0}')
        ggwi__bgbc = atcvr__dzl.format(self)
        self.args = ggwi__bgbc,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for snt__pjdr in options['distributed']:
            dist_spec[snt__pjdr] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for snt__pjdr in options['distributed_block']:
            dist_spec[snt__pjdr] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    aba__dcuyl = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, jwkl__lgdk in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(jwkl__lgdk)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    fdd__vdot = {}
    for vro__ozcpt in reversed(inspect.getmro(cls)):
        fdd__vdot.update(vro__ozcpt.__dict__)
    uua__zkcpm, abyl__ndr, ikd__zbwyd, wulls__bzv = {}, {}, {}, {}
    for xcjtl__nmml, tlqvk__ldjw in fdd__vdot.items():
        if isinstance(tlqvk__ldjw, pytypes.FunctionType):
            uua__zkcpm[xcjtl__nmml] = tlqvk__ldjw
        elif isinstance(tlqvk__ldjw, property):
            abyl__ndr[xcjtl__nmml] = tlqvk__ldjw
        elif isinstance(tlqvk__ldjw, staticmethod):
            ikd__zbwyd[xcjtl__nmml] = tlqvk__ldjw
        else:
            wulls__bzv[xcjtl__nmml] = tlqvk__ldjw
    vpftk__whej = (set(uua__zkcpm) | set(abyl__ndr) | set(ikd__zbwyd)) & set(
        spec)
    if vpftk__whej:
        raise NameError('name shadowing: {0}'.format(', '.join(vpftk__whej)))
    oyz__upw = wulls__bzv.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(wulls__bzv)
    if wulls__bzv:
        msg = 'class members are not yet supported: {0}'
        fjb__mcsv = ', '.join(wulls__bzv.keys())
        raise TypeError(msg.format(fjb__mcsv))
    for xcjtl__nmml, tlqvk__ldjw in abyl__ndr.items():
        if tlqvk__ldjw.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(xcjtl__nmml)
                )
    jit_methods = {xcjtl__nmml: bodo.jit(returns_maybe_distributed=
        aba__dcuyl)(tlqvk__ldjw) for xcjtl__nmml, tlqvk__ldjw in uua__zkcpm
        .items()}
    jit_props = {}
    for xcjtl__nmml, tlqvk__ldjw in abyl__ndr.items():
        pit__kij = {}
        if tlqvk__ldjw.fget:
            pit__kij['get'] = bodo.jit(tlqvk__ldjw.fget)
        if tlqvk__ldjw.fset:
            pit__kij['set'] = bodo.jit(tlqvk__ldjw.fset)
        jit_props[xcjtl__nmml] = pit__kij
    jit_static_methods = {xcjtl__nmml: bodo.jit(tlqvk__ldjw.__func__) for 
        xcjtl__nmml, tlqvk__ldjw in ikd__zbwyd.items()}
    varxc__xli = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    jqmf__wys = dict(class_type=varxc__xli, __doc__=oyz__upw)
    jqmf__wys.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), jqmf__wys)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, varxc__xli)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(varxc__xli, typingctx, targetctx).register()
    as_numba_type.register(cls, varxc__xli.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    ibqmd__ozgzg = ','.join('{0}:{1}'.format(xcjtl__nmml, tlqvk__ldjw) for 
        xcjtl__nmml, tlqvk__ldjw in struct.items())
    wxs__bklnh = ','.join('{0}:{1}'.format(xcjtl__nmml, tlqvk__ldjw) for 
        xcjtl__nmml, tlqvk__ldjw in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), ibqmd__ozgzg, wxs__bklnh)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    bjvra__nhxy = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if bjvra__nhxy is None:
        return
    rqy__wjw, rjek__spt = bjvra__nhxy
    for a in itertools.chain(rqy__wjw, rjek__spt.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, rqy__wjw, rjek__spt)
    except ForceLiteralArg as e:
        iuvq__atu = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(iuvq__atu, self.kws)
        afmh__pzwx = set()
        zliy__hghms = set()
        hzcvw__vtd = {}
        for qnm__izju in e.requested_args:
            shz__estz = typeinfer.func_ir.get_definition(folded[qnm__izju])
            if isinstance(shz__estz, ir.Arg):
                afmh__pzwx.add(shz__estz.index)
                if shz__estz.index in e.file_infos:
                    hzcvw__vtd[shz__estz.index] = e.file_infos[shz__estz.index]
            else:
                zliy__hghms.add(qnm__izju)
        if zliy__hghms:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif afmh__pzwx:
            raise ForceLiteralArg(afmh__pzwx, loc=self.loc, file_infos=
                hzcvw__vtd)
    if sig is None:
        avo__hxo = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in rqy__wjw]
        args += [('%s=%s' % (xcjtl__nmml, tlqvk__ldjw)) for xcjtl__nmml,
            tlqvk__ldjw in sorted(rjek__spt.items())]
        lvhh__nfdnn = avo__hxo.format(fnty, ', '.join(map(str, args)))
        yjt__gmtl = context.explain_function_type(fnty)
        msg = '\n'.join([lvhh__nfdnn, yjt__gmtl])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        bax__pisbr = context.unify_pairs(sig.recvr, fnty.this)
        if bax__pisbr is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if bax__pisbr is not None and bax__pisbr.is_precise():
            rur__qeo = fnty.copy(this=bax__pisbr)
            typeinfer.propagate_refined_type(self.func, rur__qeo)
    if not sig.return_type.is_precise():
        ikxn__imz = typevars[self.target]
        if ikxn__imz.defined:
            shpzy__evt = ikxn__imz.getone()
            if context.unify_pairs(shpzy__evt, sig.return_type) == shpzy__evt:
                sig = sig.replace(return_type=shpzy__evt)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        grx__pqlma = '*other* must be a {} but got a {} instead'
        raise TypeError(grx__pqlma.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args, {**
        self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    foye__dwt = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for xcjtl__nmml, tlqvk__ldjw in kwargs.items():
        qocf__curo = None
        try:
            jnx__elb = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[jnx__elb.name] = [tlqvk__ldjw]
            qocf__curo = get_const_value_inner(func_ir, jnx__elb)
            func_ir._definitions.pop(jnx__elb.name)
            if isinstance(qocf__curo, str):
                qocf__curo = sigutils._parse_signature_string(qocf__curo)
            if isinstance(qocf__curo, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {xcjtl__nmml} is annotated as type class {qocf__curo}."""
                    )
            assert isinstance(qocf__curo, types.Type)
            if isinstance(qocf__curo, (types.List, types.Set)):
                qocf__curo = qocf__curo.copy(reflected=False)
            foye__dwt[xcjtl__nmml] = qocf__curo
        except BodoError as qkv__gpk:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(qocf__curo, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(tlqvk__ldjw, ir.Global):
                    msg = f'Global {tlqvk__ldjw.name!r} is not defined.'
                if isinstance(tlqvk__ldjw, ir.FreeVar):
                    msg = f'Freevar {tlqvk__ldjw.name!r} is not defined.'
            if isinstance(tlqvk__ldjw, ir.Expr
                ) and tlqvk__ldjw.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=xcjtl__nmml, msg=msg, loc=loc)
    for name, typ in foye__dwt.items():
        self._legalize_arg_type(name, typ, loc)
    return foye__dwt


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    nghb__sumhr = inst.arg
    assert nghb__sumhr > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(nghb__sumhr)]))
    tmps = [state.make_temp() for _ in range(nghb__sumhr - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    awtsw__days = ir.Global('format', format, loc=self.loc)
    self.store(value=awtsw__days, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    gki__vli = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=gki__vli, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    nghb__sumhr = inst.arg
    assert nghb__sumhr > 0, 'invalid BUILD_STRING count'
    vdmkk__rxezf = self.get(strings[0])
    for other, sxulq__wqlt in zip(strings[1:], tmps):
        other = self.get(other)
        lqiyz__kwyz = ir.Expr.binop(operator.add, lhs=vdmkk__rxezf, rhs=
            other, loc=self.loc)
        self.store(lqiyz__kwyz, sxulq__wqlt)
        vdmkk__rxezf = self.get(sxulq__wqlt)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite.llvmpy.core import Type
    pce__dam = self.context.insert_const_string(self.module, attr)
    fnty = Type.function(Type.int(), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, pce__dam])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    fwtwk__fxfrj = mk_unique_var(f'{var_name}')
    ydvb__aect = fwtwk__fxfrj.replace('<', '_').replace('>', '_')
    ydvb__aect = ydvb__aect.replace('.', '_').replace('$', '_v')
    return ydvb__aect


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    ty = classty.instance_type

    def typer(val):
        if isinstance(val, (types.BaseTuple, types.Sequence)):
            fnty = self.context.resolve_value_type(np.array)
            sig = fnty.get_call_type(self.context, (val, types.DType(ty)), {})
            return sig.return_type
        elif isinstance(val, (types.Number, types.Boolean, types.IntEnumMember)
            ):
            return ty
        elif val == types.unicode_type:
            return ty
        elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
            if ty.bitwidth == 64:
                return ty
            else:
                msg = f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                raise errors.TypingError(msg)
        elif isinstance(val, types.Array
            ) and val.ndim == 0 and val.dtype == ty:
            return ty
        else:
            msg = f'Casting {val} to {ty} directly is unsupported.'
            if isinstance(val, types.Array):
                msg += f" Try doing '<array>.astype(np.{ty})' instead"
            raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        pds__gscz = states['defmap']
        if len(pds__gscz) == 0:
            uub__noh = assign.target
            numba.core.ssa._logger.debug('first assign: %s', uub__noh)
            if uub__noh.name not in scope.localvars:
                uub__noh = scope.define(assign.target.name, loc=assign.loc)
        else:
            uub__noh = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=uub__noh, value=assign.value, loc=assign.loc)
        pds__gscz[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    nnjg__cjrg = []
    for xcjtl__nmml, tlqvk__ldjw in typing.npydecl.registry.globals:
        if xcjtl__nmml == func:
            nnjg__cjrg.append(tlqvk__ldjw)
    for xcjtl__nmml, tlqvk__ldjw in typing.templates.builtin_registry.globals:
        if xcjtl__nmml == func:
            nnjg__cjrg.append(tlqvk__ldjw)
    if len(nnjg__cjrg) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return nnjg__cjrg


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    hivu__irmm = {}
    xzcun__bflgs = find_topo_order(blocks)
    qliib__ycp = {}
    for dmzf__abas in xzcun__bflgs:
        block = blocks[dmzf__abas]
        ljaym__sklk = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                trgoo__bzz = stmt.target.name
                guqhf__ikbya = stmt.value
                if (guqhf__ikbya.op == 'getattr' and guqhf__ikbya.attr in
                    arr_math and isinstance(typemap[guqhf__ikbya.value.name
                    ], types.npytypes.Array)):
                    guqhf__ikbya = stmt.value
                    xgqs__xem = guqhf__ikbya.value
                    hivu__irmm[trgoo__bzz] = xgqs__xem
                    scope = xgqs__xem.scope
                    loc = xgqs__xem.loc
                    fzvck__nnkq = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[fzvck__nnkq.name] = types.misc.Module(numpy)
                    nwt__zgqf = ir.Global('np', numpy, loc)
                    melsw__apaz = ir.Assign(nwt__zgqf, fzvck__nnkq, loc)
                    guqhf__ikbya.value = fzvck__nnkq
                    ljaym__sklk.append(melsw__apaz)
                    func_ir._definitions[fzvck__nnkq.name] = [nwt__zgqf]
                    func = getattr(numpy, guqhf__ikbya.attr)
                    jjttu__ucq = get_np_ufunc_typ_lst(func)
                    qliib__ycp[trgoo__bzz] = jjttu__ucq
                if (guqhf__ikbya.op == 'call' and guqhf__ikbya.func.name in
                    hivu__irmm):
                    xgqs__xem = hivu__irmm[guqhf__ikbya.func.name]
                    oeysx__yqzz = calltypes.pop(guqhf__ikbya)
                    xzd__fcli = oeysx__yqzz.args[:len(guqhf__ikbya.args)]
                    mrb__xuwdv = {name: typemap[tlqvk__ldjw.name] for name,
                        tlqvk__ldjw in guqhf__ikbya.kws}
                    mgtn__uxntg = qliib__ycp[guqhf__ikbya.func.name]
                    vatr__vwvfx = None
                    for jvd__aktu in mgtn__uxntg:
                        try:
                            vatr__vwvfx = jvd__aktu.get_call_type(typingctx,
                                [typemap[xgqs__xem.name]] + list(xzd__fcli),
                                mrb__xuwdv)
                            typemap.pop(guqhf__ikbya.func.name)
                            typemap[guqhf__ikbya.func.name] = jvd__aktu
                            calltypes[guqhf__ikbya] = vatr__vwvfx
                            break
                        except Exception as qkv__gpk:
                            pass
                    if vatr__vwvfx is None:
                        raise TypeError(
                            f'No valid template found for {guqhf__ikbya.func.name}'
                            )
                    guqhf__ikbya.args = [xgqs__xem] + guqhf__ikbya.args
            ljaym__sklk.append(stmt)
        block.body = ljaym__sklk


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    gfp__gbenk = ufunc.nin
    vlnk__yrja = ufunc.nout
    crvr__aqi = ufunc.nargs
    assert crvr__aqi == gfp__gbenk + vlnk__yrja
    if len(args) < gfp__gbenk:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), gfp__gbenk)
            )
    if len(args) > crvr__aqi:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), crvr__aqi))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    myqyl__bfr = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    ggj__rfkkm = max(myqyl__bfr)
    cvxq__cboe = args[gfp__gbenk:]
    if not all(vjohf__dle == ggj__rfkkm for vjohf__dle in myqyl__bfr[
        gfp__gbenk:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(cgx__bfxn, types.ArrayCompatible) and not
        isinstance(cgx__bfxn, types.Bytes) for cgx__bfxn in cvxq__cboe):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(cgx__bfxn.mutable for cgx__bfxn in cvxq__cboe):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    cwqzx__gaoy = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    lhw__ymb = None
    if ggj__rfkkm > 0 and len(cvxq__cboe) < ufunc.nout:
        lhw__ymb = 'C'
        whf__vgof = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in whf__vgof and 'F' in whf__vgof:
            lhw__ymb = 'F'
    return cwqzx__gaoy, cvxq__cboe, ggj__rfkkm, lhw__ymb


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        ehxp__anbs = 'Dict.key_type cannot be of type {}'
        raise TypingError(ehxp__anbs.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        ehxp__anbs = 'Dict.value_type cannot be of type {}'
        raise TypingError(ehxp__anbs.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for vuhv__madoy, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(vuhv__madoy))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    ewq__ouym = self.context, tuple(args), tuple(kws.items())
    try:
        erm__rlxvs, args = self._impl_cache[ewq__ouym]
        return erm__rlxvs, args
    except KeyError as qkv__gpk:
        pass
    erm__rlxvs, args = self._build_impl(ewq__ouym, args, kws)
    return erm__rlxvs, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        ifhxe__hecbl = find_topo_order(parfor.loop_body)
    jyp__exspt = ifhxe__hecbl[0]
    lca__cvmb = {}
    _update_parfor_get_setitems(parfor.loop_body[jyp__exspt].body, parfor.
        index_var, alias_map, lca__cvmb, lives_n_aliases)
    jyx__mcsrs = set(lca__cvmb.keys())
    for yclq__mpkj in ifhxe__hecbl:
        if yclq__mpkj == jyp__exspt:
            continue
        for stmt in parfor.loop_body[yclq__mpkj].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            hoot__wcrgt = set(tlqvk__ldjw.name for tlqvk__ldjw in stmt.
                list_vars())
            iko__ndp = hoot__wcrgt & jyx__mcsrs
            for a in iko__ndp:
                lca__cvmb.pop(a, None)
    for yclq__mpkj in ifhxe__hecbl:
        if yclq__mpkj == jyp__exspt:
            continue
        block = parfor.loop_body[yclq__mpkj]
        yin__vcn = lca__cvmb.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            yin__vcn, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    bjba__kzzvr = max(blocks.keys())
    xltlf__evyl, jcj__suz = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    duef__jjb = ir.Jump(xltlf__evyl, ir.Loc('parfors_dummy', -1))
    blocks[bjba__kzzvr].body.append(duef__jjb)
    tclay__jzmoh = compute_cfg_from_blocks(blocks)
    dfo__faaj = compute_use_defs(blocks)
    nfqcd__rrope = compute_live_map(tclay__jzmoh, blocks, dfo__faaj.usemap,
        dfo__faaj.defmap)
    alias_set = set(alias_map.keys())
    for dmzf__abas, block in blocks.items():
        ljaym__sklk = []
        htht__gykt = {tlqvk__ldjw.name for tlqvk__ldjw in block.terminator.
            list_vars()}
        for vwpvl__qxrg, jdr__kqc in tclay__jzmoh.successors(dmzf__abas):
            htht__gykt |= nfqcd__rrope[vwpvl__qxrg]
        for stmt in reversed(block.body):
            eovz__osgwl = htht__gykt & alias_set
            for tlqvk__ldjw in eovz__osgwl:
                htht__gykt |= alias_map[tlqvk__ldjw]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in htht__gykt and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                yof__qrv = guard(find_callname, func_ir, stmt.value)
                if yof__qrv == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in htht__gykt and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            htht__gykt |= {tlqvk__ldjw.name for tlqvk__ldjw in stmt.list_vars()
                }
            ljaym__sklk.append(stmt)
        ljaym__sklk.reverse()
        block.body = ljaym__sklk
    typemap.pop(jcj__suz.name)
    blocks[bjba__kzzvr].body.pop()

    def trim_empty_parfor_branches(parfor):
        asop__seti = False
        blocks = parfor.loop_body.copy()
        for dmzf__abas, block in blocks.items():
            if len(block.body):
                ogp__puw = block.body[-1]
                if isinstance(ogp__puw, ir.Branch):
                    if len(blocks[ogp__puw.truebr].body) == 1 and len(blocks
                        [ogp__puw.falsebr].body) == 1:
                        kne__cdwys = blocks[ogp__puw.truebr].body[0]
                        syhn__pklnx = blocks[ogp__puw.falsebr].body[0]
                        if isinstance(kne__cdwys, ir.Jump) and isinstance(
                            syhn__pklnx, ir.Jump
                            ) and kne__cdwys.target == syhn__pklnx.target:
                            parfor.loop_body[dmzf__abas].body[-1] = ir.Jump(
                                kne__cdwys.target, ogp__puw.loc)
                            asop__seti = True
                    elif len(blocks[ogp__puw.truebr].body) == 1:
                        kne__cdwys = blocks[ogp__puw.truebr].body[0]
                        if isinstance(kne__cdwys, ir.Jump
                            ) and kne__cdwys.target == ogp__puw.falsebr:
                            parfor.loop_body[dmzf__abas].body[-1] = ir.Jump(
                                kne__cdwys.target, ogp__puw.loc)
                            asop__seti = True
                    elif len(blocks[ogp__puw.falsebr].body) == 1:
                        syhn__pklnx = blocks[ogp__puw.falsebr].body[0]
                        if isinstance(syhn__pklnx, ir.Jump
                            ) and syhn__pklnx.target == ogp__puw.truebr:
                            parfor.loop_body[dmzf__abas].body[-1] = ir.Jump(
                                syhn__pklnx.target, ogp__puw.loc)
                            asop__seti = True
        return asop__seti
    asop__seti = True
    while asop__seti:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        asop__seti = trim_empty_parfor_branches(parfor)
    wac__jfa = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        wac__jfa &= len(block.body) == 0
    if wac__jfa:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import simplify_CFG
    from numba.parfors.parfor import Parfor
    zkpk__hxqto = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                zkpk__hxqto += 1
                parfor = stmt
                jfr__xio = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = jfr__xio.scope
                loc = ir.Loc('parfors_dummy', -1)
                yqi__nvh = ir.Var(scope, mk_unique_var('$const'), loc)
                jfr__xio.body.append(ir.Assign(ir.Const(0, loc), yqi__nvh, loc)
                    )
                jfr__xio.body.append(ir.Return(yqi__nvh, loc))
                tclay__jzmoh = compute_cfg_from_blocks(parfor.loop_body)
                for yivt__irmee in tclay__jzmoh.dead_nodes():
                    del parfor.loop_body[yivt__irmee]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                jfr__xio = parfor.loop_body[max(parfor.loop_body.keys())]
                jfr__xio.body.pop()
                jfr__xio.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return zkpk__hxqto


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            lsh__tkb = self.overloads.get(tuple(args))
            if lsh__tkb is not None:
                return lsh__tkb.entry_point
            self._pre_compile(args, return_type, flags)
            vfeaq__aqk = self.func_ir
            jxtt__vhizb = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=jxtt__vhizb):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=vfeaq__aqk, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        swg__chr = copy.deepcopy(flags)
        swg__chr.no_rewrites = True

        def compile_local(the_ir, the_flags):
            scj__idw = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return scj__idw.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        mmb__lhy = compile_local(func_ir, swg__chr)
        cspq__mqw = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    cspq__mqw = compile_local(func_ir, flags)
                except Exception as qkv__gpk:
                    pass
        if cspq__mqw is not None:
            cres = cspq__mqw
        else:
            cres = mmb__lhy
        return cres
    else:
        scj__idw = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return scj__idw.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    from llvmlite.llvmpy.core import Constant, Type
    ovar__jdhn = self.get_data_type(typ.dtype)
    vmk__uxi = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        vmk__uxi):
        yvsvz__tkire = ary.ctypes.data
        fzm__owcy = self.add_dynamic_addr(builder, yvsvz__tkire, info=str(
            type(yvsvz__tkire)))
        gish__lanwu = self.add_dynamic_addr(builder, id(ary), info=str(type
            (ary)))
        self.global_arrays.append(ary)
    else:
        yob__iur = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            yob__iur = yob__iur.view('int64')
        uraaw__xsgfm = Constant.array(Type.int(8), bytearray(yob__iur.data))
        fzm__owcy = cgutils.global_constant(builder, '.const.array.data',
            uraaw__xsgfm)
        fzm__owcy.align = self.get_abi_alignment(ovar__jdhn)
        gish__lanwu = None
    foyki__zdp = self.get_value_type(types.intp)
    xuz__crop = [self.get_constant(types.intp, gqch__lbe) for gqch__lbe in
        ary.shape]
    gqvq__oquzu = Constant.array(foyki__zdp, xuz__crop)
    wmz__bvvr = [self.get_constant(types.intp, gqch__lbe) for gqch__lbe in
        ary.strides]
    gsf__klu = Constant.array(foyki__zdp, wmz__bvvr)
    bxgph__xxg = self.get_constant(types.intp, ary.dtype.itemsize)
    jbjqn__mewp = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        jbjqn__mewp, bxgph__xxg, fzm__owcy.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), gqvq__oquzu, gsf__klu])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    kfqs__klac = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    niewy__qehjb = lir.Function(module, kfqs__klac, name='nrt_atomic_{0}'.
        format(op))
    [avo__kesi] = niewy__qehjb.args
    adwad__wcezr = niewy__qehjb.append_basic_block()
    builder = lir.IRBuilder(adwad__wcezr)
    qvahz__wzdbj = lir.Constant(_word_type, 1)
    if False:
        bbetf__lppdj = builder.atomic_rmw(op, avo__kesi, qvahz__wzdbj,
            ordering=ordering)
        res = getattr(builder, op)(bbetf__lppdj, qvahz__wzdbj)
        builder.ret(res)
    else:
        bbetf__lppdj = builder.load(avo__kesi)
        atetf__ktbxl = getattr(builder, op)(bbetf__lppdj, qvahz__wzdbj)
        rre__eaa = builder.icmp_signed('!=', bbetf__lppdj, lir.Constant(
            bbetf__lppdj.type, -1))
        with cgutils.if_likely(builder, rre__eaa):
            builder.store(atetf__ktbxl, avo__kesi)
        builder.ret(atetf__ktbxl)
    return niewy__qehjb


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        gisz__zqoe = state.targetctx.codegen()
        state.library = gisz__zqoe.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    pxad__psd = state.func_ir
    typemap = state.typemap
    ofvr__ksbh = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    jqkeh__rfsip = state.metadata
    zwit__vpcl = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        yuvns__gqi = (funcdesc.PythonFunctionDescriptor.
            from_specialized_function(pxad__psd, typemap, ofvr__ksbh,
            calltypes, mangler=targetctx.mangler, inline=flags.forceinline,
            noalias=flags.noalias, abi_tags=[flags.get_mangle_string()]))
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            dlrd__pbz = lowering.Lower(targetctx, library, yuvns__gqi,
                pxad__psd, metadata=jqkeh__rfsip)
            dlrd__pbz.lower()
            if not flags.no_cpython_wrapper:
                dlrd__pbz.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(ofvr__ksbh, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        dlrd__pbz.create_cfunc_wrapper()
            rhj__aawk = dlrd__pbz.env
            ruc__lprer = dlrd__pbz.call_helper
            del dlrd__pbz
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(yuvns__gqi, ruc__lprer, cfunc=None,
                env=rhj__aawk)
        else:
            hrgbr__fan = targetctx.get_executable(library, yuvns__gqi,
                rhj__aawk)
            targetctx.insert_user_function(hrgbr__fan, yuvns__gqi, [library])
            state['cr'] = _LowerResult(yuvns__gqi, ruc__lprer, cfunc=
                hrgbr__fan, env=rhj__aawk)
        jqkeh__rfsip['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        esn__dwm = llvm.passmanagers.dump_refprune_stats()
        jqkeh__rfsip['prune_stats'] = esn__dwm - zwit__vpcl
        jqkeh__rfsip['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        pkm__rim = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, pkm__rim), likely
            =False):
            c.builder.store(cgutils.true_bit, errorptr)
            loop.do_break()
        tvwe__ekqg = c.builder.icmp_signed('!=', pkm__rim, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(tvwe__ekqg, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, pkm__rim)
                c.pyapi.decref(pkm__rim)
                loop.do_break()
        c.pyapi.decref(pkm__rim)
    iarz__hunr, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(iarz__hunr, likely=True) as (if_ok, if_not_ok):
        with if_ok:
            list.size = size
            wqtnu__wqlr = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                wqtnu__wqlr), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        wqtnu__wqlr))
                    with cgutils.for_range(c.builder, size) as loop:
                        itemobj = c.pyapi.list_getitem(obj, loop.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        imem__goobu = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(imem__goobu.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            loop.do_break()
                        list.setitem(loop.index, imem__goobu.value, incref=
                            False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with if_not_ok:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    cnf__hwmo, pfn__oeiv, lqumx__uqal, mtsdk__ono, vtn__brqv = (
        compile_time_get_string_data(literal_string))
    ytek__mlco = builder.module
    gv = context.insert_const_bytes(ytek__mlco, cnf__hwmo)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        pfn__oeiv), context.get_constant(types.int32, lqumx__uqal), context
        .get_constant(types.uint32, mtsdk__ono), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    akdx__stx = None
    if isinstance(shape, types.Integer):
        akdx__stx = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(gqch__lbe, (types.Integer, types.IntEnumMember)) for
            gqch__lbe in shape):
            akdx__stx = len(shape)
    return akdx__stx


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            akdx__stx = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if akdx__stx == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, vuhv__madoy) for
                    vuhv__madoy in range(akdx__stx))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            upx__tfam = self._get_names(x)
            if len(upx__tfam) != 0:
                return upx__tfam[0]
            return upx__tfam
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    upx__tfam = self._get_names(obj)
    if len(upx__tfam) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(upx__tfam[0])


def get_equiv_set(self, obj):
    upx__tfam = self._get_names(obj)
    if len(upx__tfam) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(upx__tfam[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    zsogc__eqz = []
    for qkwi__wch in func_ir.arg_names:
        if qkwi__wch in typemap and isinstance(typemap[qkwi__wch], types.
            containers.UniTuple) and typemap[qkwi__wch].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(qkwi__wch))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for oys__rzpjh in func_ir.blocks.values():
        for stmt in oys__rzpjh.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    xpltz__plt = getattr(val, 'code', None)
                    if xpltz__plt is not None:
                        if getattr(val, 'closure', None) is not None:
                            pjx__ahiny = '<creating a function from a closure>'
                            lqiyz__kwyz = ''
                        else:
                            pjx__ahiny = xpltz__plt.co_name
                            lqiyz__kwyz = '(%s) ' % pjx__ahiny
                    else:
                        pjx__ahiny = '<could not ascertain use case>'
                        lqiyz__kwyz = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (pjx__ahiny, lqiyz__kwyz))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                ubi__icld = False
                if isinstance(val, pytypes.FunctionType):
                    ubi__icld = val in {numba.gdb, numba.gdb_init}
                if not ubi__icld:
                    ubi__icld = getattr(val, '_name', '') == 'gdb_internal'
                if ubi__icld:
                    zsogc__eqz.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    udp__omhxl = func_ir.get_definition(var)
                    orxwx__jbm = guard(find_callname, func_ir, udp__omhxl)
                    if orxwx__jbm and orxwx__jbm[1] == 'numpy':
                        ty = getattr(numpy, orxwx__jbm[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    zluk__rfz = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(zluk__rfz), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(zsogc__eqz) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        wao__cpzih = '\n'.join([x.strformat() for x in zsogc__eqz])
        raise errors.UnsupportedError(msg % wao__cpzih)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    xcjtl__nmml, tlqvk__ldjw = next(iter(val.items()))
    emho__ftnk = typeof_impl(xcjtl__nmml, c)
    lcek__lwqwv = typeof_impl(tlqvk__ldjw, c)
    if emho__ftnk is None or lcek__lwqwv is None:
        raise ValueError(
            f'Cannot type dict element type {type(xcjtl__nmml)}, {type(tlqvk__ldjw)}'
            )
    return types.DictType(emho__ftnk, lcek__lwqwv)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    hxp__zsbv = cgutils.alloca_once_value(c.builder, val)
    nod__rjsxj = c.pyapi.object_hasattr_string(val, '_opaque')
    xpdqn__zkcom = c.builder.icmp_unsigned('==', nod__rjsxj, lir.Constant(
        nod__rjsxj.type, 0))
    scnx__cwp = typ.key_type
    tfo__orlh = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(scnx__cwp, tfo__orlh)

    def copy_dict(out_dict, in_dict):
        for xcjtl__nmml, tlqvk__ldjw in in_dict.items():
            out_dict[xcjtl__nmml] = tlqvk__ldjw
    with c.builder.if_then(xpdqn__zkcom):
        ftv__sffh = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        hjmco__iswtj = c.pyapi.call_function_objargs(ftv__sffh, [])
        wkrxj__hwgff = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(wkrxj__hwgff, [hjmco__iswtj, val])
        c.builder.store(hjmco__iswtj, hxp__zsbv)
    val = c.builder.load(hxp__zsbv)
    biue__xtbbk = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    esl__rdae = c.pyapi.object_type(val)
    mle__syhaz = c.builder.icmp_unsigned('==', esl__rdae, biue__xtbbk)
    with c.builder.if_else(mle__syhaz) as (then, orelse):
        with then:
            blha__cpk = c.pyapi.object_getattr_string(val, '_opaque')
            rgduu__txs = types.MemInfoPointer(types.voidptr)
            imem__goobu = c.unbox(rgduu__txs, blha__cpk)
            mi = imem__goobu.value
            myzd__kwns = rgduu__txs, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *myzd__kwns)
            xkpl__fmto = context.get_constant_null(myzd__kwns[1])
            args = mi, xkpl__fmto
            vvluy__erq, ymp__xlx = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, ymp__xlx)
            c.pyapi.decref(blha__cpk)
            gzi__jwchm = c.builder.basic_block
        with orelse:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", esl__rdae, biue__xtbbk)
            kvrq__gols = c.builder.basic_block
    dzr__qqc = c.builder.phi(ymp__xlx.type)
    ahtub__czbvp = c.builder.phi(vvluy__erq.type)
    dzr__qqc.add_incoming(ymp__xlx, gzi__jwchm)
    dzr__qqc.add_incoming(ymp__xlx.type(None), kvrq__gols)
    ahtub__czbvp.add_incoming(vvluy__erq, gzi__jwchm)
    ahtub__czbvp.add_incoming(cgutils.true_bit, kvrq__gols)
    c.pyapi.decref(biue__xtbbk)
    c.pyapi.decref(esl__rdae)
    with c.builder.if_then(xpdqn__zkcom):
        c.pyapi.decref(val)
    return NativeValue(dzr__qqc, is_error=ahtub__czbvp)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def mul_list_generic(self, args, kws):
    a, vgexb__hwzm = args
    if isinstance(a, types.List) and isinstance(vgexb__hwzm, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(vgexb__hwzm, types.List):
        return signature(vgexb__hwzm, types.intp, vgexb__hwzm)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        dffxr__wrr, uzef__tltzl = 0, 1
    else:
        dffxr__wrr, uzef__tltzl = 1, 0
    oncee__lsbz = ListInstance(context, builder, sig.args[dffxr__wrr], args
        [dffxr__wrr])
    kcufj__adh = oncee__lsbz.size
    xlg__mjitp = args[uzef__tltzl]
    wqtnu__wqlr = lir.Constant(xlg__mjitp.type, 0)
    xlg__mjitp = builder.select(cgutils.is_neg_int(builder, xlg__mjitp),
        wqtnu__wqlr, xlg__mjitp)
    jbjqn__mewp = builder.mul(xlg__mjitp, kcufj__adh)
    qpbir__bmbry = ListInstance.allocate(context, builder, sig.return_type,
        jbjqn__mewp)
    qpbir__bmbry.size = jbjqn__mewp
    with cgutils.for_range_slice(builder, wqtnu__wqlr, jbjqn__mewp,
        kcufj__adh, inc=True) as (dest_offset, _):
        with cgutils.for_range(builder, kcufj__adh) as loop:
            value = oncee__lsbz.getitem(loop.index)
            qpbir__bmbry.setitem(builder.add(loop.index, dest_offset),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, qpbir__bmbry
        .value)
