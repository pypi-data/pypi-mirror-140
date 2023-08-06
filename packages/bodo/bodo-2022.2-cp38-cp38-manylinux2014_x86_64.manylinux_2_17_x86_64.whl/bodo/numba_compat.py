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
    zfde__sgwpx = numba.core.bytecode.FunctionIdentity.from_function(func)
    ylra__lbufo = numba.core.interpreter.Interpreter(zfde__sgwpx)
    abps__coyyz = numba.core.bytecode.ByteCode(func_id=zfde__sgwpx)
    func_ir = ylra__lbufo.interpret(abps__coyyz)
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
        kvx__kzruq = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        kvx__kzruq.run()
    pjr__yeuf = numba.core.postproc.PostProcessor(func_ir)
    pjr__yeuf.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, jya__armr in visit_vars_extensions.items():
        if isinstance(stmt, t):
            jya__armr(stmt, callback, cbdata)
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
    hmszt__wyyjr = ['ravel', 'transpose', 'reshape']
    for piekm__zdk in blocks.values():
        for ntwqw__icnkz in piekm__zdk.body:
            if type(ntwqw__icnkz) in alias_analysis_extensions:
                jya__armr = alias_analysis_extensions[type(ntwqw__icnkz)]
                jya__armr(ntwqw__icnkz, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(ntwqw__icnkz, ir.Assign):
                exkxp__eit = ntwqw__icnkz.value
                fjzn__oqoo = ntwqw__icnkz.target.name
                if is_immutable_type(fjzn__oqoo, typemap):
                    continue
                if isinstance(exkxp__eit, ir.Var
                    ) and fjzn__oqoo != exkxp__eit.name:
                    _add_alias(fjzn__oqoo, exkxp__eit.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr) and (exkxp__eit.op ==
                    'cast' or exkxp__eit.op in ['getitem', 'static_getitem']):
                    _add_alias(fjzn__oqoo, exkxp__eit.value.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr
                    ) and exkxp__eit.op == 'inplace_binop':
                    _add_alias(fjzn__oqoo, exkxp__eit.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr
                    ) and exkxp__eit.op == 'getattr' and exkxp__eit.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(fjzn__oqoo, exkxp__eit.value.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr
                    ) and exkxp__eit.op == 'getattr' and exkxp__eit.attr not in [
                    'shape'] and exkxp__eit.value.name in arg_aliases:
                    _add_alias(fjzn__oqoo, exkxp__eit.value.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr
                    ) and exkxp__eit.op == 'getattr' and exkxp__eit.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(fjzn__oqoo, exkxp__eit.value.name, alias_map,
                        arg_aliases)
                if isinstance(exkxp__eit, ir.Expr) and exkxp__eit.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(fjzn__oqoo, typemap):
                    for osm__gyu in exkxp__eit.items:
                        _add_alias(fjzn__oqoo, osm__gyu.name, alias_map,
                            arg_aliases)
                if isinstance(exkxp__eit, ir.Expr) and exkxp__eit.op == 'call':
                    fcef__ewsz = guard(find_callname, func_ir, exkxp__eit,
                        typemap)
                    if fcef__ewsz is None:
                        continue
                    dsn__yagr, nvsu__iuh = fcef__ewsz
                    if fcef__ewsz in alias_func_extensions:
                        itwu__ziht = alias_func_extensions[fcef__ewsz]
                        itwu__ziht(fjzn__oqoo, exkxp__eit.args, alias_map,
                            arg_aliases)
                    if nvsu__iuh == 'numpy' and dsn__yagr in hmszt__wyyjr:
                        _add_alias(fjzn__oqoo, exkxp__eit.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(nvsu__iuh, ir.Var
                        ) and dsn__yagr in hmszt__wyyjr:
                        _add_alias(fjzn__oqoo, nvsu__iuh.name, alias_map,
                            arg_aliases)
    nmsue__fso = copy.deepcopy(alias_map)
    for osm__gyu in nmsue__fso:
        for zgym__xljup in nmsue__fso[osm__gyu]:
            alias_map[osm__gyu] |= alias_map[zgym__xljup]
        for zgym__xljup in nmsue__fso[osm__gyu]:
            alias_map[zgym__xljup] = alias_map[osm__gyu]
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
    yptar__drom = compute_cfg_from_blocks(func_ir.blocks)
    vjbct__twby = compute_use_defs(func_ir.blocks)
    mso__vwk = compute_live_map(yptar__drom, func_ir.blocks, vjbct__twby.
        usemap, vjbct__twby.defmap)
    rim__vnxp = True
    while rim__vnxp:
        rim__vnxp = False
        for wxfa__ydvu, block in func_ir.blocks.items():
            lives = {osm__gyu.name for osm__gyu in block.terminator.list_vars()
                }
            for jamo__tylx, vfwjd__ekru in yptar__drom.successors(wxfa__ydvu):
                lives |= mso__vwk[jamo__tylx]
            htwam__rcxo = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    fjzn__oqoo = stmt.target
                    wkab__plnv = stmt.value
                    if fjzn__oqoo.name not in lives:
                        if isinstance(wkab__plnv, ir.Expr
                            ) and wkab__plnv.op == 'make_function':
                            continue
                        if isinstance(wkab__plnv, ir.Expr
                            ) and wkab__plnv.op == 'getattr':
                            continue
                        if isinstance(wkab__plnv, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(fjzn__oqoo,
                            None), types.Function):
                            continue
                        if isinstance(wkab__plnv, ir.Expr
                            ) and wkab__plnv.op == 'build_map':
                            continue
                    if isinstance(wkab__plnv, ir.Var
                        ) and fjzn__oqoo.name == wkab__plnv.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    azpxk__pcxiw = analysis.ir_extension_usedefs[type(stmt)]
                    jrfhu__wvmi, sqhzc__zmth = azpxk__pcxiw(stmt)
                    lives -= sqhzc__zmth
                    lives |= jrfhu__wvmi
                else:
                    lives |= {osm__gyu.name for osm__gyu in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(fjzn__oqoo.name)
                htwam__rcxo.append(stmt)
            htwam__rcxo.reverse()
            if len(block.body) != len(htwam__rcxo):
                rim__vnxp = True
            block.body = htwam__rcxo


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    vmb__ofhmz = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (vmb__ofhmz,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    lpumd__aaw = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), lpumd__aaw)


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
            for sxmgg__lzt in fnty.templates:
                self._inline_overloads.update(sxmgg__lzt._inline_overloads)
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
    lpumd__aaw = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), lpumd__aaw)
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
    gkwo__fvy, xsgqk__ood = self._get_impl(args, kws)
    if gkwo__fvy is None:
        return
    zqhh__kadnm = types.Dispatcher(gkwo__fvy)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        jsq__won = gkwo__fvy._compiler
        flags = compiler.Flags()
        oyq__xfd = jsq__won.targetdescr.typing_context
        xssj__xees = jsq__won.targetdescr.target_context
        hwnw__qots = jsq__won.pipeline_class(oyq__xfd, xssj__xees, None,
            None, None, flags, None)
        pxsde__mzmu = InlineWorker(oyq__xfd, xssj__xees, jsq__won.locals,
            hwnw__qots, flags, None)
        ptfl__vkd = zqhh__kadnm.dispatcher.get_call_template
        sxmgg__lzt, zhcii__nzpw, fhtd__msgdr, kws = ptfl__vkd(xsgqk__ood, kws)
        if fhtd__msgdr in self._inline_overloads:
            return self._inline_overloads[fhtd__msgdr]['iinfo'].signature
        ir = pxsde__mzmu.run_untyped_passes(zqhh__kadnm.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, xssj__xees, ir, fhtd__msgdr, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, fhtd__msgdr, None)
        self._inline_overloads[sig.args] = {'folded_args': fhtd__msgdr}
        aheh__alkue = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = aheh__alkue
        if not self._inline.is_always_inline:
            sig = zqhh__kadnm.get_call_type(self.context, xsgqk__ood, kws)
            self._compiled_overloads[sig.args] = zqhh__kadnm.get_overload(sig)
        vjejv__nnn = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': fhtd__msgdr,
            'iinfo': vjejv__nnn}
    else:
        sig = zqhh__kadnm.get_call_type(self.context, xsgqk__ood, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = zqhh__kadnm.get_overload(sig)
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
    vct__bjzx = [True, False]
    onln__kasp = [False, True]
    tribb__sszv = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    vxuzw__cnvj = get_local_target(context)
    vkpfc__fkl = utils.order_by_target_specificity(vxuzw__cnvj, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for uwgz__bwnza in vkpfc__fkl:
        oax__uatu = uwgz__bwnza(context)
        gyc__fwrpc = vct__bjzx if oax__uatu.prefer_literal else onln__kasp
        gyc__fwrpc = [True] if getattr(oax__uatu, '_no_unliteral', False
            ) else gyc__fwrpc
        for tdl__guok in gyc__fwrpc:
            try:
                if tdl__guok:
                    sig = oax__uatu.apply(args, kws)
                else:
                    rcgrb__tvdut = tuple([_unlit_non_poison(a) for a in args])
                    xmgj__fxqto = {ummgz__bhgqf: _unlit_non_poison(osm__gyu
                        ) for ummgz__bhgqf, osm__gyu in kws.items()}
                    sig = oax__uatu.apply(rcgrb__tvdut, xmgj__fxqto)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    tribb__sszv.add_error(oax__uatu, False, e, tdl__guok)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = oax__uatu.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    xad__yzl = getattr(oax__uatu, 'cases', None)
                    if xad__yzl is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            xad__yzl)
                    else:
                        msg = 'No match.'
                    tribb__sszv.add_error(oax__uatu, True, msg, tdl__guok)
    tribb__sszv.raise_error()


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
    sxmgg__lzt = self.template(context)
    ocj__jbnlw = None
    hnwya__boe = None
    sgdqt__wbzm = None
    gyc__fwrpc = [True, False] if sxmgg__lzt.prefer_literal else [False, True]
    gyc__fwrpc = [True] if getattr(sxmgg__lzt, '_no_unliteral', False
        ) else gyc__fwrpc
    for tdl__guok in gyc__fwrpc:
        if tdl__guok:
            try:
                sgdqt__wbzm = sxmgg__lzt.apply(args, kws)
            except Exception as oprw__rdm:
                if isinstance(oprw__rdm, errors.ForceLiteralArg):
                    raise oprw__rdm
                ocj__jbnlw = oprw__rdm
                sgdqt__wbzm = None
            else:
                break
        else:
            wyt__hynnn = tuple([_unlit_non_poison(a) for a in args])
            jjkne__jrqa = {ummgz__bhgqf: _unlit_non_poison(osm__gyu) for 
                ummgz__bhgqf, osm__gyu in kws.items()}
            xalpr__amz = wyt__hynnn == args and kws == jjkne__jrqa
            if not xalpr__amz and sgdqt__wbzm is None:
                try:
                    sgdqt__wbzm = sxmgg__lzt.apply(wyt__hynnn, jjkne__jrqa)
                except Exception as oprw__rdm:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        oprw__rdm, errors.NumbaError):
                        raise oprw__rdm
                    if isinstance(oprw__rdm, errors.ForceLiteralArg):
                        if sxmgg__lzt.prefer_literal:
                            raise oprw__rdm
                    hnwya__boe = oprw__rdm
                else:
                    break
    if sgdqt__wbzm is None and (hnwya__boe is not None or ocj__jbnlw is not
        None):
        xchyp__mhr = '- Resolution failure for {} arguments:\n{}\n'
        jmtuu__zgl = _termcolor.highlight(xchyp__mhr)
        if numba.core.config.DEVELOPER_MODE:
            azqjk__xlwid = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    qkkh__jopi = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    qkkh__jopi = ['']
                yeglh__whf = '\n{}'.format(2 * azqjk__xlwid)
                ssiwj__bcncm = _termcolor.reset(yeglh__whf + yeglh__whf.
                    join(_bt_as_lines(qkkh__jopi)))
                return _termcolor.reset(ssiwj__bcncm)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            vhl__wks = str(e)
            vhl__wks = vhl__wks if vhl__wks else str(repr(e)) + add_bt(e)
            mfq__obn = errors.TypingError(textwrap.dedent(vhl__wks))
            return jmtuu__zgl.format(literalness, str(mfq__obn))
        import bodo
        if isinstance(ocj__jbnlw, bodo.utils.typing.BodoError):
            raise ocj__jbnlw
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', ocj__jbnlw) +
                nested_msg('non-literal', hnwya__boe))
        else:
            msg = 'Compilation error for '
            if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                DataFrameType):
                msg += 'DataFrame.'
            elif isinstance(self.this, bodo.hiframes.pd_series_ext.SeriesType):
                msg += 'Series.'
            msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg)
    return sgdqt__wbzm


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
    dsn__yagr = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=dsn__yagr)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            hlgm__gpyl = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), hlgm__gpyl)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    ndpwd__tkwc = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            ndpwd__tkwc.append(types.Omitted(a.value))
        else:
            ndpwd__tkwc.append(self.typeof_pyval(a))
    bdzvt__ehxzl = None
    try:
        error = None
        bdzvt__ehxzl = self.compile(tuple(ndpwd__tkwc))
    except errors.ForceLiteralArg as e:
        ilvs__jsex = [hij__wcy for hij__wcy in e.requested_args if 
            isinstance(args[hij__wcy], types.Literal) and not isinstance(
            args[hij__wcy], types.LiteralStrKeyDict)]
        if ilvs__jsex:
            frd__gsdg = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            ctx__yjzca = ', '.join('Arg #{} is {}'.format(hij__wcy, args[
                hij__wcy]) for hij__wcy in sorted(ilvs__jsex))
            raise errors.CompilerError(frd__gsdg.format(ctx__yjzca))
        xsgqk__ood = []
        try:
            for hij__wcy, osm__gyu in enumerate(args):
                if hij__wcy in e.requested_args:
                    if hij__wcy in e.file_infos:
                        xsgqk__ood.append(types.FilenameType(args[hij__wcy],
                            e.file_infos[hij__wcy]))
                    else:
                        xsgqk__ood.append(types.literal(args[hij__wcy]))
                else:
                    xsgqk__ood.append(args[hij__wcy])
            args = xsgqk__ood
        except (OSError, FileNotFoundError) as iijr__mqcj:
            error = FileNotFoundError(str(iijr__mqcj) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                bdzvt__ehxzl = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        yhbfq__dai = []
        for hij__wcy, volv__nwbd in enumerate(args):
            val = volv__nwbd.value if isinstance(volv__nwbd, numba.core.
                dispatcher.OmittedArg) else volv__nwbd
            try:
                eibya__ruq = typeof(val, Purpose.argument)
            except ValueError as jxk__axtnp:
                yhbfq__dai.append((hij__wcy, str(jxk__axtnp)))
            else:
                if eibya__ruq is None:
                    yhbfq__dai.append((hij__wcy,
                        f'cannot determine Numba type of value {val}'))
        if yhbfq__dai:
            joiyw__sogce = '\n'.join(f'- argument {hij__wcy}: {zjji__pkkx}' for
                hij__wcy, zjji__pkkx in yhbfq__dai)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{joiyw__sogce}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                hytlm__wzka = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'numba', 'Overload',
                    'lowering']
                gcou__pji = False
                for pyq__cvuhl in hytlm__wzka:
                    if pyq__cvuhl in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        gcou__pji = True
                        break
                if not gcou__pji:
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
                hlgm__gpyl = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), hlgm__gpyl)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return bdzvt__ehxzl


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
    for inlia__uvwyl in cres.library._codegen._engine._defined_symbols:
        if inlia__uvwyl.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in inlia__uvwyl and (
            'bodo_gb_udf_update_local' in inlia__uvwyl or 
            'bodo_gb_udf_combine' in inlia__uvwyl or 'bodo_gb_udf_eval' in
            inlia__uvwyl or 'bodo_gb_apply_general_udfs' in inlia__uvwyl):
            gb_agg_cfunc_addr[inlia__uvwyl
                ] = cres.library.get_pointer_to_function(inlia__uvwyl)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for inlia__uvwyl in cres.library._codegen._engine._defined_symbols:
        if inlia__uvwyl.startswith('cfunc') and ('get_join_cond_addr' not in
            inlia__uvwyl or 'bodo_join_gen_cond' in inlia__uvwyl):
            join_gen_cond_cfunc_addr[inlia__uvwyl
                ] = cres.library.get_pointer_to_function(inlia__uvwyl)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    gkwo__fvy = self._get_dispatcher_for_current_target()
    if gkwo__fvy is not self:
        return gkwo__fvy.compile(sig)
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
            qgshc__euvzt = self.overloads.get(tuple(args))
            if qgshc__euvzt is not None:
                return qgshc__euvzt.entry_point
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
            jiov__ouorp = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=jiov__ouorp):
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
    yks__gvuf = self._final_module
    kprcx__tmqop = []
    axp__wged = 0
    for fn in yks__gvuf.functions:
        axp__wged += 1
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
            kprcx__tmqop.append(fn.name)
    if axp__wged == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if kprcx__tmqop:
        yks__gvuf = yks__gvuf.clone()
        for name in kprcx__tmqop:
            yks__gvuf.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = yks__gvuf
    return yks__gvuf


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
    for lifw__wlvxu in self.constraints:
        loc = lifw__wlvxu.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                lifw__wlvxu(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                euaxk__pix = numba.core.errors.TypingError(str(e), loc=
                    lifw__wlvxu.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(euaxk__pix, e))
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
                    euaxk__pix = numba.core.errors.TypingError(msg.format(
                        con=lifw__wlvxu, err=str(e)), loc=lifw__wlvxu.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(euaxk__pix, e))
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
    for ceuwh__mlots in self._failures.values():
        for fmchg__wti in ceuwh__mlots:
            if isinstance(fmchg__wti.error, ForceLiteralArg):
                raise fmchg__wti.error
            if isinstance(fmchg__wti.error, bodo.utils.typing.BodoError):
                raise fmchg__wti.error
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
    zpofb__rcxqg = False
    htwam__rcxo = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        arg__imz = set()
        yvir__ohn = lives & alias_set
        for osm__gyu in yvir__ohn:
            arg__imz |= alias_map[osm__gyu]
        lives_n_aliases = lives | arg__imz | arg_aliases
        if type(stmt) in remove_dead_extensions:
            jya__armr = remove_dead_extensions[type(stmt)]
            stmt = jya__armr(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                zpofb__rcxqg = True
                continue
        if isinstance(stmt, ir.Assign):
            fjzn__oqoo = stmt.target
            wkab__plnv = stmt.value
            if fjzn__oqoo.name not in lives and has_no_side_effect(wkab__plnv,
                lives_n_aliases, call_table):
                zpofb__rcxqg = True
                continue
            if saved_array_analysis and fjzn__oqoo.name in lives and is_expr(
                wkab__plnv, 'getattr'
                ) and wkab__plnv.attr == 'shape' and is_array_typ(typemap[
                wkab__plnv.value.name]) and wkab__plnv.value.name not in lives:
                pwb__bec = {osm__gyu: ummgz__bhgqf for ummgz__bhgqf,
                    osm__gyu in func_ir.blocks.items()}
                if block in pwb__bec:
                    wxfa__ydvu = pwb__bec[block]
                    wfe__oup = saved_array_analysis.get_equiv_set(wxfa__ydvu)
                    rwdmp__haipy = wfe__oup.get_equiv_set(wkab__plnv.value)
                    if rwdmp__haipy is not None:
                        for osm__gyu in rwdmp__haipy:
                            if osm__gyu.endswith('#0'):
                                osm__gyu = osm__gyu[:-2]
                            if osm__gyu in typemap and is_array_typ(typemap
                                [osm__gyu]) and osm__gyu in lives:
                                wkab__plnv.value = ir.Var(wkab__plnv.value.
                                    scope, osm__gyu, wkab__plnv.value.loc)
                                zpofb__rcxqg = True
                                break
            if isinstance(wkab__plnv, ir.Var
                ) and fjzn__oqoo.name == wkab__plnv.name:
                zpofb__rcxqg = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                zpofb__rcxqg = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            azpxk__pcxiw = analysis.ir_extension_usedefs[type(stmt)]
            jrfhu__wvmi, sqhzc__zmth = azpxk__pcxiw(stmt)
            lives -= sqhzc__zmth
            lives |= jrfhu__wvmi
        else:
            lives |= {osm__gyu.name for osm__gyu in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                zxh__cagu = set()
                if isinstance(wkab__plnv, ir.Expr):
                    zxh__cagu = {osm__gyu.name for osm__gyu in wkab__plnv.
                        list_vars()}
                if fjzn__oqoo.name not in zxh__cagu:
                    lives.remove(fjzn__oqoo.name)
        htwam__rcxo.append(stmt)
    htwam__rcxo.reverse()
    block.body = htwam__rcxo
    return zpofb__rcxqg


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            rjvyx__cwpys, = args
            if isinstance(rjvyx__cwpys, types.IterableType):
                dtype = rjvyx__cwpys.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), rjvyx__cwpys)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    clc__reof = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (clc__reof, self.dtype)
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
        except LiteralTypingError as fmjq__wycgs:
            return
    try:
        return literal(value)
    except LiteralTypingError as fmjq__wycgs:
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
        twh__ohq = py_func.__qualname__
    except AttributeError as fmjq__wycgs:
        twh__ohq = py_func.__name__
    zyxto__frgdl = inspect.getfile(py_func)
    for cls in self._locator_classes:
        euh__fcyb = cls.from_function(py_func, zyxto__frgdl)
        if euh__fcyb is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (twh__ohq, zyxto__frgdl))
    self._locator = euh__fcyb
    crsst__vtat = inspect.getfile(py_func)
    nqu__edci = os.path.splitext(os.path.basename(crsst__vtat))[0]
    if zyxto__frgdl.startswith('<ipython-'):
        imfj__werk = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', nqu__edci, count=1)
        if imfj__werk == nqu__edci:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        nqu__edci = imfj__werk
    igafl__zdwf = '%s.%s' % (nqu__edci, twh__ohq)
    gria__ppnhi = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(igafl__zdwf, gria__ppnhi)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    hbs__itx = list(filter(lambda a: self._istuple(a.name), args))
    if len(hbs__itx) == 2 and fn.__name__ == 'add':
        bgrw__qzvch = self.typemap[hbs__itx[0].name]
        msru__mhgwq = self.typemap[hbs__itx[1].name]
        if bgrw__qzvch.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                hbs__itx[1]))
        if msru__mhgwq.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                hbs__itx[0]))
        try:
            vrto__ywetp = [equiv_set.get_shape(x) for x in hbs__itx]
            if None in vrto__ywetp:
                return None
            zuse__ncjmz = sum(vrto__ywetp, ())
            return ArrayAnalysis.AnalyzeResult(shape=zuse__ncjmz)
        except GuardException as fmjq__wycgs:
            return None
    qlm__cvlbx = list(filter(lambda a: self._isarray(a.name), args))
    require(len(qlm__cvlbx) > 0)
    mdr__hvk = [x.name for x in qlm__cvlbx]
    iuedl__jaz = [self.typemap[x.name].ndim for x in qlm__cvlbx]
    gdd__aafhk = max(iuedl__jaz)
    require(gdd__aafhk > 0)
    vrto__ywetp = [equiv_set.get_shape(x) for x in qlm__cvlbx]
    if any(a is None for a in vrto__ywetp):
        return ArrayAnalysis.AnalyzeResult(shape=qlm__cvlbx[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, qlm__cvlbx))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, vrto__ywetp,
        mdr__hvk)


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
    plqco__xmckf = code_obj.code
    smv__iqi = len(plqco__xmckf.co_freevars)
    rfrvk__tny = plqco__xmckf.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        wkn__dowb, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        rfrvk__tny = [osm__gyu.name for osm__gyu in wkn__dowb]
    ifuy__koe = caller_ir.func_id.func.__globals__
    try:
        ifuy__koe = getattr(code_obj, 'globals', ifuy__koe)
    except KeyError as fmjq__wycgs:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/udfs.html"
        )
    zsgul__zxxhc = []
    for x in rfrvk__tny:
        try:
            glm__bhodc = caller_ir.get_definition(x)
        except KeyError as fmjq__wycgs:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(glm__bhodc, (ir.Const, ir.Global, ir.FreeVar)):
            val = glm__bhodc.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                vmb__ofhmz = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ifuy__koe[vmb__ofhmz] = bodo.jit(distributed=False)(val)
                ifuy__koe[vmb__ofhmz].is_nested_func = True
                val = vmb__ofhmz
            if isinstance(val, CPUDispatcher):
                vmb__ofhmz = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                ifuy__koe[vmb__ofhmz] = val
                val = vmb__ofhmz
            zsgul__zxxhc.append(val)
        elif isinstance(glm__bhodc, ir.Expr
            ) and glm__bhodc.op == 'make_function':
            fvktn__tuq = convert_code_obj_to_function(glm__bhodc, caller_ir)
            vmb__ofhmz = ir_utils.mk_unique_var('nested_func').replace('.', '_'
                )
            ifuy__koe[vmb__ofhmz] = bodo.jit(distributed=False)(fvktn__tuq)
            ifuy__koe[vmb__ofhmz].is_nested_func = True
            zsgul__zxxhc.append(vmb__ofhmz)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    dacj__halk = '\n'.join([('\tc_%d = %s' % (hij__wcy, x)) for hij__wcy, x in
        enumerate(zsgul__zxxhc)])
    ofs__tsz = ','.join([('c_%d' % hij__wcy) for hij__wcy in range(smv__iqi)])
    owxt__iswz = list(plqco__xmckf.co_varnames)
    fmhiu__fnwq = 0
    igi__khu = plqco__xmckf.co_argcount
    irdel__ezz = caller_ir.get_definition(code_obj.defaults)
    if irdel__ezz is not None:
        if isinstance(irdel__ezz, tuple):
            ifss__alnkw = [caller_ir.get_definition(x).value for x in
                irdel__ezz]
            yhcc__pexbe = tuple(ifss__alnkw)
        else:
            ifss__alnkw = [caller_ir.get_definition(x).value for x in
                irdel__ezz.items]
            yhcc__pexbe = tuple(ifss__alnkw)
        fmhiu__fnwq = len(yhcc__pexbe)
    nps__klya = igi__khu - fmhiu__fnwq
    ovfu__zgp = ','.join([('%s' % owxt__iswz[hij__wcy]) for hij__wcy in
        range(nps__klya)])
    if fmhiu__fnwq:
        byvy__qbikw = [('%s = %s' % (owxt__iswz[hij__wcy + nps__klya],
            yhcc__pexbe[hij__wcy])) for hij__wcy in range(fmhiu__fnwq)]
        ovfu__zgp += ', '
        ovfu__zgp += ', '.join(byvy__qbikw)
    return _create_function_from_code_obj(plqco__xmckf, dacj__halk,
        ovfu__zgp, ofs__tsz, ifuy__koe)


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
    for yvm__htht, (yhyh__mxzfz, wyikg__zlhc) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % wyikg__zlhc)
            lwlqm__lvul = _pass_registry.get(yhyh__mxzfz).pass_inst
            if isinstance(lwlqm__lvul, CompilerPass):
                self._runPass(yvm__htht, lwlqm__lvul, state)
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
                    pipeline_name, wyikg__zlhc)
                bbcu__mfj = self._patch_error(msg, e)
                raise bbcu__mfj
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
    apd__bliq = None
    sqhzc__zmth = {}

    def lookup(var, already_seen, varonly=True):
        val = sqhzc__zmth.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    auyqc__narj = reduction_node.unversioned_name
    for hij__wcy, stmt in enumerate(nodes):
        fjzn__oqoo = stmt.target
        wkab__plnv = stmt.value
        sqhzc__zmth[fjzn__oqoo.name] = wkab__plnv
        if isinstance(wkab__plnv, ir.Var) and wkab__plnv.name in sqhzc__zmth:
            wkab__plnv = lookup(wkab__plnv, set())
        if isinstance(wkab__plnv, ir.Expr):
            xucp__htfot = set(lookup(osm__gyu, set(), True).name for
                osm__gyu in wkab__plnv.list_vars())
            if name in xucp__htfot:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(wkab__plnv)]
                wryja__kbisd = [x for x, qhon__mtor in args if qhon__mtor.
                    name != name]
                args = [(x, qhon__mtor) for x, qhon__mtor in args if x !=
                    qhon__mtor.name]
                thuuc__pelca = dict(args)
                if len(wryja__kbisd) == 1:
                    thuuc__pelca[wryja__kbisd[0]] = ir.Var(fjzn__oqoo.scope,
                        name + '#init', fjzn__oqoo.loc)
                replace_vars_inner(wkab__plnv, thuuc__pelca)
                apd__bliq = nodes[hij__wcy:]
                break
    return apd__bliq


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
        slgc__taa = expand_aliases({osm__gyu.name for osm__gyu in stmt.
            list_vars()}, alias_map, arg_aliases)
        hhx__rjddz = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        viwzb__tle = expand_aliases({osm__gyu.name for osm__gyu in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        pvr__vxi = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(hhx__rjddz & viwzb__tle | pvr__vxi & slgc__taa) == 0:
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
    yhzh__lxk = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            yhzh__lxk.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                yhzh__lxk.update(get_parfor_writes(stmt, func_ir))
    return yhzh__lxk


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    yhzh__lxk = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        yhzh__lxk.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        yhzh__lxk = {osm__gyu.name for osm__gyu in stmt.df_out_vars.values()}
        if stmt.out_key_vars is not None:
            yhzh__lxk.update({osm__gyu.name for osm__gyu in stmt.out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        yhzh__lxk = {osm__gyu.name for osm__gyu in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        yhzh__lxk = {osm__gyu.name for osm__gyu in stmt.out_data_vars.values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            yhzh__lxk.update({osm__gyu.name for osm__gyu in stmt.out_key_arrs})
            yhzh__lxk.update({osm__gyu.name for osm__gyu in stmt.
                df_out_vars.values()})
    if is_call_assign(stmt):
        fcef__ewsz = guard(find_callname, func_ir, stmt.value)
        if fcef__ewsz in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            yhzh__lxk.add(stmt.value.args[0].name)
    return yhzh__lxk


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
        jya__armr = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        uig__kfmx = jya__armr.format(self, msg)
        self.args = uig__kfmx,
    else:
        jya__armr = _termcolor.errmsg('{0}')
        uig__kfmx = jya__armr.format(self)
        self.args = uig__kfmx,
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
        for ndnfw__lttxz in options['distributed']:
            dist_spec[ndnfw__lttxz] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for ndnfw__lttxz in options['distributed_block']:
            dist_spec[ndnfw__lttxz] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    mbjp__hcqe = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, jmlln__wbyt in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(jmlln__wbyt)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    ngxnd__zyzv = {}
    for ypbd__gfn in reversed(inspect.getmro(cls)):
        ngxnd__zyzv.update(ypbd__gfn.__dict__)
    hrfm__ssb, itvku__ikjz, yomcq__dulfy, ekn__spgo = {}, {}, {}, {}
    for ummgz__bhgqf, osm__gyu in ngxnd__zyzv.items():
        if isinstance(osm__gyu, pytypes.FunctionType):
            hrfm__ssb[ummgz__bhgqf] = osm__gyu
        elif isinstance(osm__gyu, property):
            itvku__ikjz[ummgz__bhgqf] = osm__gyu
        elif isinstance(osm__gyu, staticmethod):
            yomcq__dulfy[ummgz__bhgqf] = osm__gyu
        else:
            ekn__spgo[ummgz__bhgqf] = osm__gyu
    eot__cowjy = (set(hrfm__ssb) | set(itvku__ikjz) | set(yomcq__dulfy)) & set(
        spec)
    if eot__cowjy:
        raise NameError('name shadowing: {0}'.format(', '.join(eot__cowjy)))
    mkx__celd = ekn__spgo.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(ekn__spgo)
    if ekn__spgo:
        msg = 'class members are not yet supported: {0}'
        oyg__vao = ', '.join(ekn__spgo.keys())
        raise TypeError(msg.format(oyg__vao))
    for ummgz__bhgqf, osm__gyu in itvku__ikjz.items():
        if osm__gyu.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(
                ummgz__bhgqf))
    jit_methods = {ummgz__bhgqf: bodo.jit(returns_maybe_distributed=
        mbjp__hcqe)(osm__gyu) for ummgz__bhgqf, osm__gyu in hrfm__ssb.items()}
    jit_props = {}
    for ummgz__bhgqf, osm__gyu in itvku__ikjz.items():
        lpumd__aaw = {}
        if osm__gyu.fget:
            lpumd__aaw['get'] = bodo.jit(osm__gyu.fget)
        if osm__gyu.fset:
            lpumd__aaw['set'] = bodo.jit(osm__gyu.fset)
        jit_props[ummgz__bhgqf] = lpumd__aaw
    jit_static_methods = {ummgz__bhgqf: bodo.jit(osm__gyu.__func__) for 
        ummgz__bhgqf, osm__gyu in yomcq__dulfy.items()}
    uqyd__vmiwf = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    iqutd__drh = dict(class_type=uqyd__vmiwf, __doc__=mkx__celd)
    iqutd__drh.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), iqutd__drh)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, uqyd__vmiwf)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(uqyd__vmiwf, typingctx, targetctx).register()
    as_numba_type.register(cls, uqyd__vmiwf.instance_type)
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
    hqgyx__gbx = ','.join('{0}:{1}'.format(ummgz__bhgqf, osm__gyu) for 
        ummgz__bhgqf, osm__gyu in struct.items())
    hkcdd__fqomo = ','.join('{0}:{1}'.format(ummgz__bhgqf, osm__gyu) for 
        ummgz__bhgqf, osm__gyu in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), hqgyx__gbx, hkcdd__fqomo)
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
    dqeg__dzdf = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if dqeg__dzdf is None:
        return
    bxlz__vjpu, rdh__pjv = dqeg__dzdf
    for a in itertools.chain(bxlz__vjpu, rdh__pjv.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, bxlz__vjpu, rdh__pjv)
    except ForceLiteralArg as e:
        juugh__cuf = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(juugh__cuf, self.kws)
        swf__jrk = set()
        pja__cewud = set()
        vfks__ayrt = {}
        for yvm__htht in e.requested_args:
            qhkyq__sgy = typeinfer.func_ir.get_definition(folded[yvm__htht])
            if isinstance(qhkyq__sgy, ir.Arg):
                swf__jrk.add(qhkyq__sgy.index)
                if qhkyq__sgy.index in e.file_infos:
                    vfks__ayrt[qhkyq__sgy.index] = e.file_infos[qhkyq__sgy.
                        index]
            else:
                pja__cewud.add(yvm__htht)
        if pja__cewud:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif swf__jrk:
            raise ForceLiteralArg(swf__jrk, loc=self.loc, file_infos=vfks__ayrt
                )
    if sig is None:
        hsg__oxdf = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in bxlz__vjpu]
        args += [('%s=%s' % (ummgz__bhgqf, osm__gyu)) for ummgz__bhgqf,
            osm__gyu in sorted(rdh__pjv.items())]
        oepcp__mixte = hsg__oxdf.format(fnty, ', '.join(map(str, args)))
        lrrut__ano = context.explain_function_type(fnty)
        msg = '\n'.join([oepcp__mixte, lrrut__ano])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        gphyw__ppls = context.unify_pairs(sig.recvr, fnty.this)
        if gphyw__ppls is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if gphyw__ppls is not None and gphyw__ppls.is_precise():
            gllfh__uml = fnty.copy(this=gphyw__ppls)
            typeinfer.propagate_refined_type(self.func, gllfh__uml)
    if not sig.return_type.is_precise():
        zqnr__cgjwz = typevars[self.target]
        if zqnr__cgjwz.defined:
            jeael__uujne = zqnr__cgjwz.getone()
            if context.unify_pairs(jeael__uujne, sig.return_type
                ) == jeael__uujne:
                sig = sig.replace(return_type=jeael__uujne)
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
        frd__gsdg = '*other* must be a {} but got a {} instead'
        raise TypeError(frd__gsdg.format(ForceLiteralArg, type(other)))
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
    rcsv__zzyds = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for ummgz__bhgqf, osm__gyu in kwargs.items():
        gwkdk__cqnle = None
        try:
            vpeq__kfpx = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var
                ('dummy'), loc)
            func_ir._definitions[vpeq__kfpx.name] = [osm__gyu]
            gwkdk__cqnle = get_const_value_inner(func_ir, vpeq__kfpx)
            func_ir._definitions.pop(vpeq__kfpx.name)
            if isinstance(gwkdk__cqnle, str):
                gwkdk__cqnle = sigutils._parse_signature_string(gwkdk__cqnle)
            if isinstance(gwkdk__cqnle, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {ummgz__bhgqf} is annotated as type class {gwkdk__cqnle}."""
                    )
            assert isinstance(gwkdk__cqnle, types.Type)
            if isinstance(gwkdk__cqnle, (types.List, types.Set)):
                gwkdk__cqnle = gwkdk__cqnle.copy(reflected=False)
            rcsv__zzyds[ummgz__bhgqf] = gwkdk__cqnle
        except BodoError as fmjq__wycgs:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(gwkdk__cqnle, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(osm__gyu, ir.Global):
                    msg = f'Global {osm__gyu.name!r} is not defined.'
                if isinstance(osm__gyu, ir.FreeVar):
                    msg = f'Freevar {osm__gyu.name!r} is not defined.'
            if isinstance(osm__gyu, ir.Expr) and osm__gyu.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=ummgz__bhgqf, msg=msg, loc=loc)
    for name, typ in rcsv__zzyds.items():
        self._legalize_arg_type(name, typ, loc)
    return rcsv__zzyds


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
    ejrqq__fmp = inst.arg
    assert ejrqq__fmp > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(ejrqq__fmp)]))
    tmps = [state.make_temp() for _ in range(ejrqq__fmp - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    qlbqi__nbz = ir.Global('format', format, loc=self.loc)
    self.store(value=qlbqi__nbz, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    facnv__hhhv = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=facnv__hhhv, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    ejrqq__fmp = inst.arg
    assert ejrqq__fmp > 0, 'invalid BUILD_STRING count'
    wnqu__spgl = self.get(strings[0])
    for other, ropgx__npo in zip(strings[1:], tmps):
        other = self.get(other)
        exkxp__eit = ir.Expr.binop(operator.add, lhs=wnqu__spgl, rhs=other,
            loc=self.loc)
        self.store(exkxp__eit, ropgx__npo)
        wnqu__spgl = self.get(ropgx__npo)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite.llvmpy.core import Type
    ploh__nozpn = self.context.insert_const_string(self.module, attr)
    fnty = Type.function(Type.int(), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, ploh__nozpn])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    ilyw__eleto = mk_unique_var(f'{var_name}')
    ayxf__nnevl = ilyw__eleto.replace('<', '_').replace('>', '_')
    ayxf__nnevl = ayxf__nnevl.replace('.', '_').replace('$', '_v')
    return ayxf__nnevl


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
        bwq__mdkgu = states['defmap']
        if len(bwq__mdkgu) == 0:
            qddrh__tks = assign.target
            numba.core.ssa._logger.debug('first assign: %s', qddrh__tks)
            if qddrh__tks.name not in scope.localvars:
                qddrh__tks = scope.define(assign.target.name, loc=assign.loc)
        else:
            qddrh__tks = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=qddrh__tks, value=assign.value, loc=
            assign.loc)
        bwq__mdkgu[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    iyt__esdn = []
    for ummgz__bhgqf, osm__gyu in typing.npydecl.registry.globals:
        if ummgz__bhgqf == func:
            iyt__esdn.append(osm__gyu)
    for ummgz__bhgqf, osm__gyu in typing.templates.builtin_registry.globals:
        if ummgz__bhgqf == func:
            iyt__esdn.append(osm__gyu)
    if len(iyt__esdn) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return iyt__esdn


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    hiwf__fnbxi = {}
    oglcb__sjdye = find_topo_order(blocks)
    cby__qmy = {}
    for wxfa__ydvu in oglcb__sjdye:
        block = blocks[wxfa__ydvu]
        htwam__rcxo = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                fjzn__oqoo = stmt.target.name
                wkab__plnv = stmt.value
                if (wkab__plnv.op == 'getattr' and wkab__plnv.attr in
                    arr_math and isinstance(typemap[wkab__plnv.value.name],
                    types.npytypes.Array)):
                    wkab__plnv = stmt.value
                    advc__cfgmk = wkab__plnv.value
                    hiwf__fnbxi[fjzn__oqoo] = advc__cfgmk
                    scope = advc__cfgmk.scope
                    loc = advc__cfgmk.loc
                    aggv__likyc = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[aggv__likyc.name] = types.misc.Module(numpy)
                    sywya__scqvn = ir.Global('np', numpy, loc)
                    aos__jszoj = ir.Assign(sywya__scqvn, aggv__likyc, loc)
                    wkab__plnv.value = aggv__likyc
                    htwam__rcxo.append(aos__jszoj)
                    func_ir._definitions[aggv__likyc.name] = [sywya__scqvn]
                    func = getattr(numpy, wkab__plnv.attr)
                    yaw__pohik = get_np_ufunc_typ_lst(func)
                    cby__qmy[fjzn__oqoo] = yaw__pohik
                if (wkab__plnv.op == 'call' and wkab__plnv.func.name in
                    hiwf__fnbxi):
                    advc__cfgmk = hiwf__fnbxi[wkab__plnv.func.name]
                    wjcmt__tya = calltypes.pop(wkab__plnv)
                    zdu__sdg = wjcmt__tya.args[:len(wkab__plnv.args)]
                    pitt__pra = {name: typemap[osm__gyu.name] for name,
                        osm__gyu in wkab__plnv.kws}
                    hvey__dpm = cby__qmy[wkab__plnv.func.name]
                    tmkm__dvohb = None
                    for vli__efc in hvey__dpm:
                        try:
                            tmkm__dvohb = vli__efc.get_call_type(typingctx,
                                [typemap[advc__cfgmk.name]] + list(zdu__sdg
                                ), pitt__pra)
                            typemap.pop(wkab__plnv.func.name)
                            typemap[wkab__plnv.func.name] = vli__efc
                            calltypes[wkab__plnv] = tmkm__dvohb
                            break
                        except Exception as fmjq__wycgs:
                            pass
                    if tmkm__dvohb is None:
                        raise TypeError(
                            f'No valid template found for {wkab__plnv.func.name}'
                            )
                    wkab__plnv.args = [advc__cfgmk] + wkab__plnv.args
            htwam__rcxo.append(stmt)
        block.body = htwam__rcxo


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    dtn__kbjgj = ufunc.nin
    ofk__ubyu = ufunc.nout
    nps__klya = ufunc.nargs
    assert nps__klya == dtn__kbjgj + ofk__ubyu
    if len(args) < dtn__kbjgj:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), dtn__kbjgj)
            )
    if len(args) > nps__klya:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), nps__klya))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    tywdf__xbtm = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    qpkk__tmpra = max(tywdf__xbtm)
    ylorw__opty = args[dtn__kbjgj:]
    if not all(ifss__alnkw == qpkk__tmpra for ifss__alnkw in tywdf__xbtm[
        dtn__kbjgj:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(vbpba__vey, types.ArrayCompatible) and not
        isinstance(vbpba__vey, types.Bytes) for vbpba__vey in ylorw__opty):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(vbpba__vey.mutable for vbpba__vey in ylorw__opty):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    tgwmx__gehcw = [(x.dtype if isinstance(x, types.ArrayCompatible) and 
        not isinstance(x, types.Bytes) else x) for x in args]
    iap__ldc = None
    if qpkk__tmpra > 0 and len(ylorw__opty) < ufunc.nout:
        iap__ldc = 'C'
        zhauz__evjjp = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in zhauz__evjjp and 'F' in zhauz__evjjp:
            iap__ldc = 'F'
    return tgwmx__gehcw, ylorw__opty, qpkk__tmpra, iap__ldc


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
        lut__pkws = 'Dict.key_type cannot be of type {}'
        raise TypingError(lut__pkws.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        lut__pkws = 'Dict.value_type cannot be of type {}'
        raise TypingError(lut__pkws.format(valty))
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
    for hij__wcy, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(hij__wcy))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    gxtbl__powu = self.context, tuple(args), tuple(kws.items())
    try:
        fzam__gzefd, args = self._impl_cache[gxtbl__powu]
        return fzam__gzefd, args
    except KeyError as fmjq__wycgs:
        pass
    fzam__gzefd, args = self._build_impl(gxtbl__powu, args, kws)
    return fzam__gzefd, args


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
        iroud__mfeyt = find_topo_order(parfor.loop_body)
    zauh__kbh = iroud__mfeyt[0]
    ype__pve = {}
    _update_parfor_get_setitems(parfor.loop_body[zauh__kbh].body, parfor.
        index_var, alias_map, ype__pve, lives_n_aliases)
    ahtn__mzsrw = set(ype__pve.keys())
    for lbb__tcma in iroud__mfeyt:
        if lbb__tcma == zauh__kbh:
            continue
        for stmt in parfor.loop_body[lbb__tcma].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            pajd__zepru = set(osm__gyu.name for osm__gyu in stmt.list_vars())
            zcoxu__bguz = pajd__zepru & ahtn__mzsrw
            for a in zcoxu__bguz:
                ype__pve.pop(a, None)
    for lbb__tcma in iroud__mfeyt:
        if lbb__tcma == zauh__kbh:
            continue
        block = parfor.loop_body[lbb__tcma]
        abpau__dfyqa = ype__pve.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            abpau__dfyqa, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    phjt__gdcc = max(blocks.keys())
    oxua__omx, dslx__wwx = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    mdep__ufte = ir.Jump(oxua__omx, ir.Loc('parfors_dummy', -1))
    blocks[phjt__gdcc].body.append(mdep__ufte)
    yptar__drom = compute_cfg_from_blocks(blocks)
    vjbct__twby = compute_use_defs(blocks)
    mso__vwk = compute_live_map(yptar__drom, blocks, vjbct__twby.usemap,
        vjbct__twby.defmap)
    alias_set = set(alias_map.keys())
    for wxfa__ydvu, block in blocks.items():
        htwam__rcxo = []
        lcc__pagsm = {osm__gyu.name for osm__gyu in block.terminator.
            list_vars()}
        for jamo__tylx, vfwjd__ekru in yptar__drom.successors(wxfa__ydvu):
            lcc__pagsm |= mso__vwk[jamo__tylx]
        for stmt in reversed(block.body):
            arg__imz = lcc__pagsm & alias_set
            for osm__gyu in arg__imz:
                lcc__pagsm |= alias_map[osm__gyu]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in lcc__pagsm and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                fcef__ewsz = guard(find_callname, func_ir, stmt.value)
                if fcef__ewsz == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in lcc__pagsm and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            lcc__pagsm |= {osm__gyu.name for osm__gyu in stmt.list_vars()}
            htwam__rcxo.append(stmt)
        htwam__rcxo.reverse()
        block.body = htwam__rcxo
    typemap.pop(dslx__wwx.name)
    blocks[phjt__gdcc].body.pop()

    def trim_empty_parfor_branches(parfor):
        rim__vnxp = False
        blocks = parfor.loop_body.copy()
        for wxfa__ydvu, block in blocks.items():
            if len(block.body):
                owy__ppm = block.body[-1]
                if isinstance(owy__ppm, ir.Branch):
                    if len(blocks[owy__ppm.truebr].body) == 1 and len(blocks
                        [owy__ppm.falsebr].body) == 1:
                        ujeb__zudf = blocks[owy__ppm.truebr].body[0]
                        osjpc__ykev = blocks[owy__ppm.falsebr].body[0]
                        if isinstance(ujeb__zudf, ir.Jump) and isinstance(
                            osjpc__ykev, ir.Jump
                            ) and ujeb__zudf.target == osjpc__ykev.target:
                            parfor.loop_body[wxfa__ydvu].body[-1] = ir.Jump(
                                ujeb__zudf.target, owy__ppm.loc)
                            rim__vnxp = True
                    elif len(blocks[owy__ppm.truebr].body) == 1:
                        ujeb__zudf = blocks[owy__ppm.truebr].body[0]
                        if isinstance(ujeb__zudf, ir.Jump
                            ) and ujeb__zudf.target == owy__ppm.falsebr:
                            parfor.loop_body[wxfa__ydvu].body[-1] = ir.Jump(
                                ujeb__zudf.target, owy__ppm.loc)
                            rim__vnxp = True
                    elif len(blocks[owy__ppm.falsebr].body) == 1:
                        osjpc__ykev = blocks[owy__ppm.falsebr].body[0]
                        if isinstance(osjpc__ykev, ir.Jump
                            ) and osjpc__ykev.target == owy__ppm.truebr:
                            parfor.loop_body[wxfa__ydvu].body[-1] = ir.Jump(
                                osjpc__ykev.target, owy__ppm.loc)
                            rim__vnxp = True
        return rim__vnxp
    rim__vnxp = True
    while rim__vnxp:
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
        rim__vnxp = trim_empty_parfor_branches(parfor)
    ummq__jsbwi = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        ummq__jsbwi &= len(block.body) == 0
    if ummq__jsbwi:
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
    diu__zztrc = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                diu__zztrc += 1
                parfor = stmt
                mzam__inrn = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = mzam__inrn.scope
                loc = ir.Loc('parfors_dummy', -1)
                jdw__jtsbn = ir.Var(scope, mk_unique_var('$const'), loc)
                mzam__inrn.body.append(ir.Assign(ir.Const(0, loc),
                    jdw__jtsbn, loc))
                mzam__inrn.body.append(ir.Return(jdw__jtsbn, loc))
                yptar__drom = compute_cfg_from_blocks(parfor.loop_body)
                for qypqa__yiu in yptar__drom.dead_nodes():
                    del parfor.loop_body[qypqa__yiu]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                mzam__inrn = parfor.loop_body[max(parfor.loop_body.keys())]
                mzam__inrn.body.pop()
                mzam__inrn.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return diu__zztrc


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
            qgshc__euvzt = self.overloads.get(tuple(args))
            if qgshc__euvzt is not None:
                return qgshc__euvzt.entry_point
            self._pre_compile(args, return_type, flags)
            dhtqg__qxq = self.func_ir
            jiov__ouorp = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=jiov__ouorp):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=dhtqg__qxq, args=args,
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
        juszl__xsgzk = copy.deepcopy(flags)
        juszl__xsgzk.no_rewrites = True

        def compile_local(the_ir, the_flags):
            rmtg__idv = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return rmtg__idv.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        kfte__oxyrx = compile_local(func_ir, juszl__xsgzk)
        gpn__tpvg = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    gpn__tpvg = compile_local(func_ir, flags)
                except Exception as fmjq__wycgs:
                    pass
        if gpn__tpvg is not None:
            cres = gpn__tpvg
        else:
            cres = kfte__oxyrx
        return cres
    else:
        rmtg__idv = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return rmtg__idv.compile_ir(func_ir=func_ir, lifted=lifted,
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
    ixzv__ectcd = self.get_data_type(typ.dtype)
    fojo__xqpzq = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        fojo__xqpzq):
        frm__sqwd = ary.ctypes.data
        obyxz__mgjz = self.add_dynamic_addr(builder, frm__sqwd, info=str(
            type(frm__sqwd)))
        zue__rzqrg = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        pjlxk__esmff = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            pjlxk__esmff = pjlxk__esmff.view('int64')
        yvqg__svco = Constant.array(Type.int(8), bytearray(pjlxk__esmff.data))
        obyxz__mgjz = cgutils.global_constant(builder, '.const.array.data',
            yvqg__svco)
        obyxz__mgjz.align = self.get_abi_alignment(ixzv__ectcd)
        zue__rzqrg = None
    qwe__fmt = self.get_value_type(types.intp)
    iuqq__kjfl = [self.get_constant(types.intp, cvgsn__zqrf) for
        cvgsn__zqrf in ary.shape]
    kykui__omlf = Constant.array(qwe__fmt, iuqq__kjfl)
    xaz__knq = [self.get_constant(types.intp, cvgsn__zqrf) for cvgsn__zqrf in
        ary.strides]
    cfsvw__zcmuf = Constant.array(qwe__fmt, xaz__knq)
    oibw__xuewx = self.get_constant(types.intp, ary.dtype.itemsize)
    wmjta__moczm = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        wmjta__moczm, oibw__xuewx, obyxz__mgjz.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), kykui__omlf, cfsvw__zcmuf])


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
    cwvl__xsxm = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    uvy__hsiwl = lir.Function(module, cwvl__xsxm, name='nrt_atomic_{0}'.
        format(op))
    [nvxd__rhsu] = uvy__hsiwl.args
    oste__kxqde = uvy__hsiwl.append_basic_block()
    builder = lir.IRBuilder(oste__kxqde)
    eqn__rwk = lir.Constant(_word_type, 1)
    if False:
        shj__zfk = builder.atomic_rmw(op, nvxd__rhsu, eqn__rwk, ordering=
            ordering)
        res = getattr(builder, op)(shj__zfk, eqn__rwk)
        builder.ret(res)
    else:
        shj__zfk = builder.load(nvxd__rhsu)
        dggg__spnmq = getattr(builder, op)(shj__zfk, eqn__rwk)
        ouid__cvert = builder.icmp_signed('!=', shj__zfk, lir.Constant(
            shj__zfk.type, -1))
        with cgutils.if_likely(builder, ouid__cvert):
            builder.store(dggg__spnmq, nvxd__rhsu)
        builder.ret(dggg__spnmq)
    return uvy__hsiwl


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
        ceoz__ltc = state.targetctx.codegen()
        state.library = ceoz__ltc.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    ylra__lbufo = state.func_ir
    typemap = state.typemap
    qelq__utc = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    czlgx__rfkh = state.metadata
    hwwl__xwtef = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        ncqb__yvess = (funcdesc.PythonFunctionDescriptor.
            from_specialized_function(ylra__lbufo, typemap, qelq__utc,
            calltypes, mangler=targetctx.mangler, inline=flags.forceinline,
            noalias=flags.noalias, abi_tags=[flags.get_mangle_string()]))
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            ioj__dybnb = lowering.Lower(targetctx, library, ncqb__yvess,
                ylra__lbufo, metadata=czlgx__rfkh)
            ioj__dybnb.lower()
            if not flags.no_cpython_wrapper:
                ioj__dybnb.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(qelq__utc, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        ioj__dybnb.create_cfunc_wrapper()
            gsi__dnefv = ioj__dybnb.env
            cno__xyn = ioj__dybnb.call_helper
            del ioj__dybnb
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(ncqb__yvess, cno__xyn, cfunc=None,
                env=gsi__dnefv)
        else:
            xsoh__vntw = targetctx.get_executable(library, ncqb__yvess,
                gsi__dnefv)
            targetctx.insert_user_function(xsoh__vntw, ncqb__yvess, [library])
            state['cr'] = _LowerResult(ncqb__yvess, cno__xyn, cfunc=
                xsoh__vntw, env=gsi__dnefv)
        czlgx__rfkh['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        cerqj__knbl = llvm.passmanagers.dump_refprune_stats()
        czlgx__rfkh['prune_stats'] = cerqj__knbl - hwwl__xwtef
        czlgx__rfkh['llvm_pass_timings'] = library.recorded_timings
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
        izd__ewlqn = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, izd__ewlqn),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            loop.do_break()
        hlz__chxof = c.builder.icmp_signed('!=', izd__ewlqn, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(hlz__chxof, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, izd__ewlqn)
                c.pyapi.decref(izd__ewlqn)
                loop.do_break()
        c.pyapi.decref(izd__ewlqn)
    waes__dbq, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(waes__dbq, likely=True) as (if_ok, if_not_ok):
        with if_ok:
            list.size = size
            injm__xedfs = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                injm__xedfs), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        injm__xedfs))
                    with cgutils.for_range(c.builder, size) as loop:
                        itemobj = c.pyapi.list_getitem(obj, loop.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        mnj__qne = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(mnj__qne.is_error, likely=False
                            ):
                            c.builder.store(cgutils.true_bit, errorptr)
                            loop.do_break()
                        list.setitem(loop.index, mnj__qne.value, incref=False)
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
    pbtot__emf, sdjh__aesc, iwh__vapk, qwd__ywt, axh__got = (
        compile_time_get_string_data(literal_string))
    yks__gvuf = builder.module
    gv = context.insert_const_bytes(yks__gvuf, pbtot__emf)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        sdjh__aesc), context.get_constant(types.int32, iwh__vapk), context.
        get_constant(types.uint32, qwd__ywt), context.get_constant(
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
    cgat__idx = None
    if isinstance(shape, types.Integer):
        cgat__idx = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(cvgsn__zqrf, (types.Integer, types.IntEnumMember)
            ) for cvgsn__zqrf in shape):
            cgat__idx = len(shape)
    return cgat__idx


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
            cgat__idx = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if cgat__idx == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, hij__wcy) for hij__wcy in
                    range(cgat__idx))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            mdr__hvk = self._get_names(x)
            if len(mdr__hvk) != 0:
                return mdr__hvk[0]
            return mdr__hvk
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    mdr__hvk = self._get_names(obj)
    if len(mdr__hvk) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(mdr__hvk[0])


def get_equiv_set(self, obj):
    mdr__hvk = self._get_names(obj)
    if len(mdr__hvk) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(mdr__hvk[0])


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
    kvx__zwkt = []
    for wojn__wjug in func_ir.arg_names:
        if wojn__wjug in typemap and isinstance(typemap[wojn__wjug], types.
            containers.UniTuple) and typemap[wojn__wjug].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(wojn__wjug))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for zqkn__cuyj in func_ir.blocks.values():
        for stmt in zqkn__cuyj.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    hubf__kkpxx = getattr(val, 'code', None)
                    if hubf__kkpxx is not None:
                        if getattr(val, 'closure', None) is not None:
                            vhez__qap = '<creating a function from a closure>'
                            exkxp__eit = ''
                        else:
                            vhez__qap = hubf__kkpxx.co_name
                            exkxp__eit = '(%s) ' % vhez__qap
                    else:
                        vhez__qap = '<could not ascertain use case>'
                        exkxp__eit = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (vhez__qap, exkxp__eit))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                ohu__pek = False
                if isinstance(val, pytypes.FunctionType):
                    ohu__pek = val in {numba.gdb, numba.gdb_init}
                if not ohu__pek:
                    ohu__pek = getattr(val, '_name', '') == 'gdb_internal'
                if ohu__pek:
                    kvx__zwkt.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    aat__iepp = func_ir.get_definition(var)
                    tve__fft = guard(find_callname, func_ir, aat__iepp)
                    if tve__fft and tve__fft[1] == 'numpy':
                        ty = getattr(numpy, tve__fft[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    chj__oeig = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(chj__oeig), loc=stmt.loc)
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
    if len(kvx__zwkt) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        brhjw__fbs = '\n'.join([x.strformat() for x in kvx__zwkt])
        raise errors.UnsupportedError(msg % brhjw__fbs)


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
    ummgz__bhgqf, osm__gyu = next(iter(val.items()))
    pws__lkdnr = typeof_impl(ummgz__bhgqf, c)
    wokw__wnj = typeof_impl(osm__gyu, c)
    if pws__lkdnr is None or wokw__wnj is None:
        raise ValueError(
            f'Cannot type dict element type {type(ummgz__bhgqf)}, {type(osm__gyu)}'
            )
    return types.DictType(pws__lkdnr, wokw__wnj)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    vjr__gkwz = cgutils.alloca_once_value(c.builder, val)
    ilq__bvsbz = c.pyapi.object_hasattr_string(val, '_opaque')
    szns__vttxw = c.builder.icmp_unsigned('==', ilq__bvsbz, lir.Constant(
        ilq__bvsbz.type, 0))
    xdre__yun = typ.key_type
    rkuc__sbf = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(xdre__yun, rkuc__sbf)

    def copy_dict(out_dict, in_dict):
        for ummgz__bhgqf, osm__gyu in in_dict.items():
            out_dict[ummgz__bhgqf] = osm__gyu
    with c.builder.if_then(szns__vttxw):
        ehd__odvd = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        urv__ocfy = c.pyapi.call_function_objargs(ehd__odvd, [])
        sbbmh__mxupm = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(sbbmh__mxupm, [urv__ocfy, val])
        c.builder.store(urv__ocfy, vjr__gkwz)
    val = c.builder.load(vjr__gkwz)
    dfcwh__ebv = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    duidn__gpmu = c.pyapi.object_type(val)
    kkjpx__ltygh = c.builder.icmp_unsigned('==', duidn__gpmu, dfcwh__ebv)
    with c.builder.if_else(kkjpx__ltygh) as (then, orelse):
        with then:
            vjeyz__pwnhe = c.pyapi.object_getattr_string(val, '_opaque')
            jud__bmwh = types.MemInfoPointer(types.voidptr)
            mnj__qne = c.unbox(jud__bmwh, vjeyz__pwnhe)
            mi = mnj__qne.value
            ndpwd__tkwc = jud__bmwh, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *ndpwd__tkwc)
            bgzi__ugte = context.get_constant_null(ndpwd__tkwc[1])
            args = mi, bgzi__ugte
            dwf__kuxhz, wetr__ynzjj = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, wetr__ynzjj)
            c.pyapi.decref(vjeyz__pwnhe)
            pbea__kdri = c.builder.basic_block
        with orelse:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", duidn__gpmu, dfcwh__ebv)
            azr__kuqn = c.builder.basic_block
    fznl__lxcy = c.builder.phi(wetr__ynzjj.type)
    hpr__fsqri = c.builder.phi(dwf__kuxhz.type)
    fznl__lxcy.add_incoming(wetr__ynzjj, pbea__kdri)
    fznl__lxcy.add_incoming(wetr__ynzjj.type(None), azr__kuqn)
    hpr__fsqri.add_incoming(dwf__kuxhz, pbea__kdri)
    hpr__fsqri.add_incoming(cgutils.true_bit, azr__kuqn)
    c.pyapi.decref(dfcwh__ebv)
    c.pyapi.decref(duidn__gpmu)
    with c.builder.if_then(szns__vttxw):
        c.pyapi.decref(val)
    return NativeValue(fznl__lxcy, is_error=hpr__fsqri)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def mul_list_generic(self, args, kws):
    a, szwgk__kbgo = args
    if isinstance(a, types.List) and isinstance(szwgk__kbgo, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(szwgk__kbgo, types.List):
        return signature(szwgk__kbgo, types.intp, szwgk__kbgo)


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
        htleh__qbgf, nsxir__nqu = 0, 1
    else:
        htleh__qbgf, nsxir__nqu = 1, 0
    vvhkc__zdsc = ListInstance(context, builder, sig.args[htleh__qbgf],
        args[htleh__qbgf])
    gapc__wsn = vvhkc__zdsc.size
    sec__gxvd = args[nsxir__nqu]
    injm__xedfs = lir.Constant(sec__gxvd.type, 0)
    sec__gxvd = builder.select(cgutils.is_neg_int(builder, sec__gxvd),
        injm__xedfs, sec__gxvd)
    wmjta__moczm = builder.mul(sec__gxvd, gapc__wsn)
    pktjm__vmz = ListInstance.allocate(context, builder, sig.return_type,
        wmjta__moczm)
    pktjm__vmz.size = wmjta__moczm
    with cgutils.for_range_slice(builder, injm__xedfs, wmjta__moczm,
        gapc__wsn, inc=True) as (dest_offset, _):
        with cgutils.for_range(builder, gapc__wsn) as loop:
            value = vvhkc__zdsc.getitem(loop.index)
            pktjm__vmz.setitem(builder.add(loop.index, dest_offset), value,
                incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, pktjm__vmz.value
        )
