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
    oxl__mhuxr = numba.core.bytecode.FunctionIdentity.from_function(func)
    wuck__rpfdf = numba.core.interpreter.Interpreter(oxl__mhuxr)
    ojkv__osf = numba.core.bytecode.ByteCode(func_id=oxl__mhuxr)
    func_ir = wuck__rpfdf.interpret(ojkv__osf)
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
        rncl__kzyz = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        rncl__kzyz.run()
    vgoj__wqd = numba.core.postproc.PostProcessor(func_ir)
    vgoj__wqd.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, yios__zmi in visit_vars_extensions.items():
        if isinstance(stmt, t):
            yios__zmi(stmt, callback, cbdata)
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
    mrxyx__fuff = ['ravel', 'transpose', 'reshape']
    for vytd__lvub in blocks.values():
        for twhkj__itfa in vytd__lvub.body:
            if type(twhkj__itfa) in alias_analysis_extensions:
                yios__zmi = alias_analysis_extensions[type(twhkj__itfa)]
                yios__zmi(twhkj__itfa, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(twhkj__itfa, ir.Assign):
                kawlc__urack = twhkj__itfa.value
                kpurp__qtumx = twhkj__itfa.target.name
                if is_immutable_type(kpurp__qtumx, typemap):
                    continue
                if isinstance(kawlc__urack, ir.Var
                    ) and kpurp__qtumx != kawlc__urack.name:
                    _add_alias(kpurp__qtumx, kawlc__urack.name, alias_map,
                        arg_aliases)
                if isinstance(kawlc__urack, ir.Expr) and (kawlc__urack.op ==
                    'cast' or kawlc__urack.op in ['getitem', 'static_getitem']
                    ):
                    _add_alias(kpurp__qtumx, kawlc__urack.value.name,
                        alias_map, arg_aliases)
                if isinstance(kawlc__urack, ir.Expr
                    ) and kawlc__urack.op == 'inplace_binop':
                    _add_alias(kpurp__qtumx, kawlc__urack.lhs.name,
                        alias_map, arg_aliases)
                if isinstance(kawlc__urack, ir.Expr
                    ) and kawlc__urack.op == 'getattr' and kawlc__urack.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(kpurp__qtumx, kawlc__urack.value.name,
                        alias_map, arg_aliases)
                if (isinstance(kawlc__urack, ir.Expr) and kawlc__urack.op ==
                    'getattr' and kawlc__urack.attr not in ['shape'] and 
                    kawlc__urack.value.name in arg_aliases):
                    _add_alias(kpurp__qtumx, kawlc__urack.value.name,
                        alias_map, arg_aliases)
                if isinstance(kawlc__urack, ir.Expr
                    ) and kawlc__urack.op == 'getattr' and kawlc__urack.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(kpurp__qtumx, kawlc__urack.value.name,
                        alias_map, arg_aliases)
                if isinstance(kawlc__urack, ir.Expr) and kawlc__urack.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(kpurp__qtumx, typemap):
                    for giean__dcqzi in kawlc__urack.items:
                        _add_alias(kpurp__qtumx, giean__dcqzi.name,
                            alias_map, arg_aliases)
                if isinstance(kawlc__urack, ir.Expr
                    ) and kawlc__urack.op == 'call':
                    ajke__xdl = guard(find_callname, func_ir, kawlc__urack,
                        typemap)
                    if ajke__xdl is None:
                        continue
                    gprx__jid, jkg__hrapl = ajke__xdl
                    if ajke__xdl in alias_func_extensions:
                        wldg__gkyp = alias_func_extensions[ajke__xdl]
                        wldg__gkyp(kpurp__qtumx, kawlc__urack.args,
                            alias_map, arg_aliases)
                    if jkg__hrapl == 'numpy' and gprx__jid in mrxyx__fuff:
                        _add_alias(kpurp__qtumx, kawlc__urack.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(jkg__hrapl, ir.Var
                        ) and gprx__jid in mrxyx__fuff:
                        _add_alias(kpurp__qtumx, jkg__hrapl.name, alias_map,
                            arg_aliases)
    qhh__lhx = copy.deepcopy(alias_map)
    for giean__dcqzi in qhh__lhx:
        for mkr__oeo in qhh__lhx[giean__dcqzi]:
            alias_map[giean__dcqzi] |= alias_map[mkr__oeo]
        for mkr__oeo in qhh__lhx[giean__dcqzi]:
            alias_map[mkr__oeo] = alias_map[giean__dcqzi]
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
    iqys__jyo = compute_cfg_from_blocks(func_ir.blocks)
    oog__qaqb = compute_use_defs(func_ir.blocks)
    jrer__uzmrs = compute_live_map(iqys__jyo, func_ir.blocks, oog__qaqb.
        usemap, oog__qaqb.defmap)
    xgseo__dpk = True
    while xgseo__dpk:
        xgseo__dpk = False
        for olw__ifmrm, block in func_ir.blocks.items():
            lives = {giean__dcqzi.name for giean__dcqzi in block.terminator
                .list_vars()}
            for paq__uyzfk, yclv__dgsbd in iqys__jyo.successors(olw__ifmrm):
                lives |= jrer__uzmrs[paq__uyzfk]
            ehzpi__tvx = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    kpurp__qtumx = stmt.target
                    xmvkr__zslbq = stmt.value
                    if kpurp__qtumx.name not in lives:
                        if isinstance(xmvkr__zslbq, ir.Expr
                            ) and xmvkr__zslbq.op == 'make_function':
                            continue
                        if isinstance(xmvkr__zslbq, ir.Expr
                            ) and xmvkr__zslbq.op == 'getattr':
                            continue
                        if isinstance(xmvkr__zslbq, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(kpurp__qtumx,
                            None), types.Function):
                            continue
                        if isinstance(xmvkr__zslbq, ir.Expr
                            ) and xmvkr__zslbq.op == 'build_map':
                            continue
                    if isinstance(xmvkr__zslbq, ir.Var
                        ) and kpurp__qtumx.name == xmvkr__zslbq.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    smiyg__tbkar = analysis.ir_extension_usedefs[type(stmt)]
                    aaq__nucu, snid__kljj = smiyg__tbkar(stmt)
                    lives -= snid__kljj
                    lives |= aaq__nucu
                else:
                    lives |= {giean__dcqzi.name for giean__dcqzi in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(kpurp__qtumx.name)
                ehzpi__tvx.append(stmt)
            ehzpi__tvx.reverse()
            if len(block.body) != len(ehzpi__tvx):
                xgseo__dpk = True
            block.body = ehzpi__tvx


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    nhww__ozqyo = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (nhww__ozqyo,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    tfun__ewbe = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), tfun__ewbe)


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
            for aqpm__kqh in fnty.templates:
                self._inline_overloads.update(aqpm__kqh._inline_overloads)
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
    tfun__ewbe = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), tfun__ewbe)
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
    gguw__bwp, cjuoj__wsmg = self._get_impl(args, kws)
    if gguw__bwp is None:
        return
    cxe__fte = types.Dispatcher(gguw__bwp)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        azibs__dygdr = gguw__bwp._compiler
        flags = compiler.Flags()
        icmh__jghr = azibs__dygdr.targetdescr.typing_context
        uftxk__ochc = azibs__dygdr.targetdescr.target_context
        eeuij__rzl = azibs__dygdr.pipeline_class(icmh__jghr, uftxk__ochc,
            None, None, None, flags, None)
        mcidn__wyu = InlineWorker(icmh__jghr, uftxk__ochc, azibs__dygdr.
            locals, eeuij__rzl, flags, None)
        qje__ricyg = cxe__fte.dispatcher.get_call_template
        aqpm__kqh, hbfxv__pdo, uqf__yrjew, kws = qje__ricyg(cjuoj__wsmg, kws)
        if uqf__yrjew in self._inline_overloads:
            return self._inline_overloads[uqf__yrjew]['iinfo'].signature
        ir = mcidn__wyu.run_untyped_passes(cxe__fte.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, uftxk__ochc, ir, uqf__yrjew, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, uqf__yrjew, None)
        self._inline_overloads[sig.args] = {'folded_args': uqf__yrjew}
        vrz__ekiq = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = vrz__ekiq
        if not self._inline.is_always_inline:
            sig = cxe__fte.get_call_type(self.context, cjuoj__wsmg, kws)
            self._compiled_overloads[sig.args] = cxe__fte.get_overload(sig)
        nlts__jkgs = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': uqf__yrjew,
            'iinfo': nlts__jkgs}
    else:
        sig = cxe__fte.get_call_type(self.context, cjuoj__wsmg, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = cxe__fte.get_overload(sig)
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
    hab__pqp = [True, False]
    odah__rfbv = [False, True]
    nzgd__jveiy = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    swjb__ukbsl = get_local_target(context)
    oeqk__zwedf = utils.order_by_target_specificity(swjb__ukbsl, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for ymi__gewz in oeqk__zwedf:
        vobu__ekid = ymi__gewz(context)
        wbr__nrkhu = hab__pqp if vobu__ekid.prefer_literal else odah__rfbv
        wbr__nrkhu = [True] if getattr(vobu__ekid, '_no_unliteral', False
            ) else wbr__nrkhu
        for vthop__kigwk in wbr__nrkhu:
            try:
                if vthop__kigwk:
                    sig = vobu__ekid.apply(args, kws)
                else:
                    nfe__npa = tuple([_unlit_non_poison(a) for a in args])
                    dxgul__sws = {ujwvn__hch: _unlit_non_poison(
                        giean__dcqzi) for ujwvn__hch, giean__dcqzi in kws.
                        items()}
                    sig = vobu__ekid.apply(nfe__npa, dxgul__sws)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    nzgd__jveiy.add_error(vobu__ekid, False, e, vthop__kigwk)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = vobu__ekid.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    wii__bqt = getattr(vobu__ekid, 'cases', None)
                    if wii__bqt is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            wii__bqt)
                    else:
                        msg = 'No match.'
                    nzgd__jveiy.add_error(vobu__ekid, True, msg, vthop__kigwk)
    nzgd__jveiy.raise_error()


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
    aqpm__kqh = self.template(context)
    fwgct__pvy = None
    lgbtx__xknbe = None
    soahj__klbl = None
    wbr__nrkhu = [True, False] if aqpm__kqh.prefer_literal else [False, True]
    wbr__nrkhu = [True] if getattr(aqpm__kqh, '_no_unliteral', False
        ) else wbr__nrkhu
    for vthop__kigwk in wbr__nrkhu:
        if vthop__kigwk:
            try:
                soahj__klbl = aqpm__kqh.apply(args, kws)
            except Exception as iaj__gdwj:
                if isinstance(iaj__gdwj, errors.ForceLiteralArg):
                    raise iaj__gdwj
                fwgct__pvy = iaj__gdwj
                soahj__klbl = None
            else:
                break
        else:
            skkix__lah = tuple([_unlit_non_poison(a) for a in args])
            erry__nmb = {ujwvn__hch: _unlit_non_poison(giean__dcqzi) for 
                ujwvn__hch, giean__dcqzi in kws.items()}
            hjhqe__hcjv = skkix__lah == args and kws == erry__nmb
            if not hjhqe__hcjv and soahj__klbl is None:
                try:
                    soahj__klbl = aqpm__kqh.apply(skkix__lah, erry__nmb)
                except Exception as iaj__gdwj:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        iaj__gdwj, errors.NumbaError):
                        raise iaj__gdwj
                    if isinstance(iaj__gdwj, errors.ForceLiteralArg):
                        if aqpm__kqh.prefer_literal:
                            raise iaj__gdwj
                    lgbtx__xknbe = iaj__gdwj
                else:
                    break
    if soahj__klbl is None and (lgbtx__xknbe is not None or fwgct__pvy is not
        None):
        owso__ilnn = '- Resolution failure for {} arguments:\n{}\n'
        grgq__sfmw = _termcolor.highlight(owso__ilnn)
        if numba.core.config.DEVELOPER_MODE:
            bjvg__wljo = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    sraad__jlmlf = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    sraad__jlmlf = ['']
                brl__nvn = '\n{}'.format(2 * bjvg__wljo)
                nhmh__yupku = _termcolor.reset(brl__nvn + brl__nvn.join(
                    _bt_as_lines(sraad__jlmlf)))
                return _termcolor.reset(nhmh__yupku)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            gzmqe__mqtfz = str(e)
            gzmqe__mqtfz = gzmqe__mqtfz if gzmqe__mqtfz else str(repr(e)
                ) + add_bt(e)
            sgajq__lwl = errors.TypingError(textwrap.dedent(gzmqe__mqtfz))
            return grgq__sfmw.format(literalness, str(sgajq__lwl))
        import bodo
        if isinstance(fwgct__pvy, bodo.utils.typing.BodoError):
            raise fwgct__pvy
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', fwgct__pvy) +
                nested_msg('non-literal', lgbtx__xknbe))
        else:
            msg = 'Compilation error for '
            if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                DataFrameType):
                msg += 'DataFrame.'
            elif isinstance(self.this, bodo.hiframes.pd_series_ext.SeriesType):
                msg += 'Series.'
            msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg)
    return soahj__klbl


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
    gprx__jid = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=gprx__jid)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            ttewf__fyfc = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), ttewf__fyfc)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    zhibq__had = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            zhibq__had.append(types.Omitted(a.value))
        else:
            zhibq__had.append(self.typeof_pyval(a))
    dah__fsb = None
    try:
        error = None
        dah__fsb = self.compile(tuple(zhibq__had))
    except errors.ForceLiteralArg as e:
        dmasu__ickw = [phn__xli for phn__xli in e.requested_args if 
            isinstance(args[phn__xli], types.Literal) and not isinstance(
            args[phn__xli], types.LiteralStrKeyDict)]
        if dmasu__ickw:
            wlx__hwf = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            obv__yypnj = ', '.join('Arg #{} is {}'.format(phn__xli, args[
                phn__xli]) for phn__xli in sorted(dmasu__ickw))
            raise errors.CompilerError(wlx__hwf.format(obv__yypnj))
        cjuoj__wsmg = []
        try:
            for phn__xli, giean__dcqzi in enumerate(args):
                if phn__xli in e.requested_args:
                    if phn__xli in e.file_infos:
                        cjuoj__wsmg.append(types.FilenameType(args[phn__xli
                            ], e.file_infos[phn__xli]))
                    else:
                        cjuoj__wsmg.append(types.literal(args[phn__xli]))
                else:
                    cjuoj__wsmg.append(args[phn__xli])
            args = cjuoj__wsmg
        except (OSError, FileNotFoundError) as kmrv__lwh:
            error = FileNotFoundError(str(kmrv__lwh) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                dah__fsb = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        eer__sphec = []
        for phn__xli, kudt__kcmb in enumerate(args):
            val = kudt__kcmb.value if isinstance(kudt__kcmb, numba.core.
                dispatcher.OmittedArg) else kudt__kcmb
            try:
                gdujc__afcir = typeof(val, Purpose.argument)
            except ValueError as iwn__nky:
                eer__sphec.append((phn__xli, str(iwn__nky)))
            else:
                if gdujc__afcir is None:
                    eer__sphec.append((phn__xli,
                        f'cannot determine Numba type of value {val}'))
        if eer__sphec:
            xbkrg__mdhqh = '\n'.join(
                f'- argument {phn__xli}: {mrmi__oehfz}' for phn__xli,
                mrmi__oehfz in eer__sphec)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{xbkrg__mdhqh}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                mvyr__wzns = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'numba', 'Overload',
                    'lowering']
                zxcyb__ovj = False
                for qdjb__ommz in mvyr__wzns:
                    if qdjb__ommz in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        zxcyb__ovj = True
                        break
                if not zxcyb__ovj:
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
                ttewf__fyfc = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), ttewf__fyfc)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return dah__fsb


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
    for fcx__npwbg in cres.library._codegen._engine._defined_symbols:
        if fcx__npwbg.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in fcx__npwbg and (
            'bodo_gb_udf_update_local' in fcx__npwbg or 
            'bodo_gb_udf_combine' in fcx__npwbg or 'bodo_gb_udf_eval' in
            fcx__npwbg or 'bodo_gb_apply_general_udfs' in fcx__npwbg):
            gb_agg_cfunc_addr[fcx__npwbg
                ] = cres.library.get_pointer_to_function(fcx__npwbg)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for fcx__npwbg in cres.library._codegen._engine._defined_symbols:
        if fcx__npwbg.startswith('cfunc') and ('get_join_cond_addr' not in
            fcx__npwbg or 'bodo_join_gen_cond' in fcx__npwbg):
            join_gen_cond_cfunc_addr[fcx__npwbg
                ] = cres.library.get_pointer_to_function(fcx__npwbg)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    gguw__bwp = self._get_dispatcher_for_current_target()
    if gguw__bwp is not self:
        return gguw__bwp.compile(sig)
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
            tec__svyyv = self.overloads.get(tuple(args))
            if tec__svyyv is not None:
                return tec__svyyv.entry_point
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
            smi__dbecg = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=smi__dbecg):
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
    nsnuv__fzlb = self._final_module
    wfk__qoct = []
    dsr__gbn = 0
    for fn in nsnuv__fzlb.functions:
        dsr__gbn += 1
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
            wfk__qoct.append(fn.name)
    if dsr__gbn == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if wfk__qoct:
        nsnuv__fzlb = nsnuv__fzlb.clone()
        for name in wfk__qoct:
            nsnuv__fzlb.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = nsnuv__fzlb
    return nsnuv__fzlb


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
    for sukl__jvmt in self.constraints:
        loc = sukl__jvmt.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                sukl__jvmt(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                wdefs__eqw = numba.core.errors.TypingError(str(e), loc=
                    sukl__jvmt.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(wdefs__eqw, e))
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
                    wdefs__eqw = numba.core.errors.TypingError(msg.format(
                        con=sukl__jvmt, err=str(e)), loc=sukl__jvmt.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(wdefs__eqw, e))
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
    for wtj__gimg in self._failures.values():
        for oowfm__bjid in wtj__gimg:
            if isinstance(oowfm__bjid.error, ForceLiteralArg):
                raise oowfm__bjid.error
            if isinstance(oowfm__bjid.error, bodo.utils.typing.BodoError):
                raise oowfm__bjid.error
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
    smiuo__jroj = False
    ehzpi__tvx = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        bkatm__ouqax = set()
        kura__trhfk = lives & alias_set
        for giean__dcqzi in kura__trhfk:
            bkatm__ouqax |= alias_map[giean__dcqzi]
        lives_n_aliases = lives | bkatm__ouqax | arg_aliases
        if type(stmt) in remove_dead_extensions:
            yios__zmi = remove_dead_extensions[type(stmt)]
            stmt = yios__zmi(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                smiuo__jroj = True
                continue
        if isinstance(stmt, ir.Assign):
            kpurp__qtumx = stmt.target
            xmvkr__zslbq = stmt.value
            if kpurp__qtumx.name not in lives and has_no_side_effect(
                xmvkr__zslbq, lives_n_aliases, call_table):
                smiuo__jroj = True
                continue
            if saved_array_analysis and kpurp__qtumx.name in lives and is_expr(
                xmvkr__zslbq, 'getattr'
                ) and xmvkr__zslbq.attr == 'shape' and is_array_typ(typemap
                [xmvkr__zslbq.value.name]
                ) and xmvkr__zslbq.value.name not in lives:
                pcgm__gixub = {giean__dcqzi: ujwvn__hch for ujwvn__hch,
                    giean__dcqzi in func_ir.blocks.items()}
                if block in pcgm__gixub:
                    olw__ifmrm = pcgm__gixub[block]
                    xokm__wpv = saved_array_analysis.get_equiv_set(olw__ifmrm)
                    ggun__jpx = xokm__wpv.get_equiv_set(xmvkr__zslbq.value)
                    if ggun__jpx is not None:
                        for giean__dcqzi in ggun__jpx:
                            if giean__dcqzi.endswith('#0'):
                                giean__dcqzi = giean__dcqzi[:-2]
                            if giean__dcqzi in typemap and is_array_typ(typemap
                                [giean__dcqzi]) and giean__dcqzi in lives:
                                xmvkr__zslbq.value = ir.Var(xmvkr__zslbq.
                                    value.scope, giean__dcqzi, xmvkr__zslbq
                                    .value.loc)
                                smiuo__jroj = True
                                break
            if isinstance(xmvkr__zslbq, ir.Var
                ) and kpurp__qtumx.name == xmvkr__zslbq.name:
                smiuo__jroj = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                smiuo__jroj = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            smiyg__tbkar = analysis.ir_extension_usedefs[type(stmt)]
            aaq__nucu, snid__kljj = smiyg__tbkar(stmt)
            lives -= snid__kljj
            lives |= aaq__nucu
        else:
            lives |= {giean__dcqzi.name for giean__dcqzi in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                ybvpt__zqgb = set()
                if isinstance(xmvkr__zslbq, ir.Expr):
                    ybvpt__zqgb = {giean__dcqzi.name for giean__dcqzi in
                        xmvkr__zslbq.list_vars()}
                if kpurp__qtumx.name not in ybvpt__zqgb:
                    lives.remove(kpurp__qtumx.name)
        ehzpi__tvx.append(stmt)
    ehzpi__tvx.reverse()
    block.body = ehzpi__tvx
    return smiuo__jroj


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            qvi__xeab, = args
            if isinstance(qvi__xeab, types.IterableType):
                dtype = qvi__xeab.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), qvi__xeab)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    yhib__ugs = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (yhib__ugs, self.dtype)
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
        except LiteralTypingError as ocow__gubem:
            return
    try:
        return literal(value)
    except LiteralTypingError as ocow__gubem:
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
        eiy__hqmta = py_func.__qualname__
    except AttributeError as ocow__gubem:
        eiy__hqmta = py_func.__name__
    zwc__iyzx = inspect.getfile(py_func)
    for cls in self._locator_classes:
        tprlx__liqc = cls.from_function(py_func, zwc__iyzx)
        if tprlx__liqc is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (eiy__hqmta, zwc__iyzx))
    self._locator = tprlx__liqc
    gzpet__jwkj = inspect.getfile(py_func)
    wmxz__lhfcx = os.path.splitext(os.path.basename(gzpet__jwkj))[0]
    if zwc__iyzx.startswith('<ipython-'):
        fulzp__cdeoj = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', wmxz__lhfcx, count=1)
        if fulzp__cdeoj == wmxz__lhfcx:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        wmxz__lhfcx = fulzp__cdeoj
    qcz__mtip = '%s.%s' % (wmxz__lhfcx, eiy__hqmta)
    tujp__gox = getattr(sys, 'abiflags', '')
    self._filename_base = self.get_filename_base(qcz__mtip, tujp__gox)


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    dyuo__yudtz = list(filter(lambda a: self._istuple(a.name), args))
    if len(dyuo__yudtz) == 2 and fn.__name__ == 'add':
        rkksi__avuu = self.typemap[dyuo__yudtz[0].name]
        kvus__lrs = self.typemap[dyuo__yudtz[1].name]
        if rkksi__avuu.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                dyuo__yudtz[1]))
        if kvus__lrs.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                dyuo__yudtz[0]))
        try:
            xinqx__wyky = [equiv_set.get_shape(x) for x in dyuo__yudtz]
            if None in xinqx__wyky:
                return None
            sitln__whg = sum(xinqx__wyky, ())
            return ArrayAnalysis.AnalyzeResult(shape=sitln__whg)
        except GuardException as ocow__gubem:
            return None
    zgptq__hfry = list(filter(lambda a: self._isarray(a.name), args))
    require(len(zgptq__hfry) > 0)
    gpgbs__ydxzb = [x.name for x in zgptq__hfry]
    bdp__owo = [self.typemap[x.name].ndim for x in zgptq__hfry]
    umi__dju = max(bdp__owo)
    require(umi__dju > 0)
    xinqx__wyky = [equiv_set.get_shape(x) for x in zgptq__hfry]
    if any(a is None for a in xinqx__wyky):
        return ArrayAnalysis.AnalyzeResult(shape=zgptq__hfry[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, zgptq__hfry))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, xinqx__wyky,
        gpgbs__ydxzb)


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
    nbr__khaj = code_obj.code
    ozpj__ezdfv = len(nbr__khaj.co_freevars)
    ngiy__ferib = nbr__khaj.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        wis__iqw, op = ir_utils.find_build_sequence(caller_ir, code_obj.closure
            )
        assert op == 'build_tuple'
        ngiy__ferib = [giean__dcqzi.name for giean__dcqzi in wis__iqw]
    cile__szs = caller_ir.func_id.func.__globals__
    try:
        cile__szs = getattr(code_obj, 'globals', cile__szs)
    except KeyError as ocow__gubem:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/source/programming_with_bodo/bodo_api_reference/udfs.html"
        )
    aeoj__wtltz = []
    for x in ngiy__ferib:
        try:
            rzyh__wxxrj = caller_ir.get_definition(x)
        except KeyError as ocow__gubem:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(rzyh__wxxrj, (ir.Const, ir.Global, ir.FreeVar)):
            val = rzyh__wxxrj.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                nhww__ozqyo = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                cile__szs[nhww__ozqyo] = bodo.jit(distributed=False)(val)
                cile__szs[nhww__ozqyo].is_nested_func = True
                val = nhww__ozqyo
            if isinstance(val, CPUDispatcher):
                nhww__ozqyo = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                cile__szs[nhww__ozqyo] = val
                val = nhww__ozqyo
            aeoj__wtltz.append(val)
        elif isinstance(rzyh__wxxrj, ir.Expr
            ) and rzyh__wxxrj.op == 'make_function':
            ybak__stqom = convert_code_obj_to_function(rzyh__wxxrj, caller_ir)
            nhww__ozqyo = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            cile__szs[nhww__ozqyo] = bodo.jit(distributed=False)(ybak__stqom)
            cile__szs[nhww__ozqyo].is_nested_func = True
            aeoj__wtltz.append(nhww__ozqyo)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    mfqx__gyvu = '\n'.join([('\tc_%d = %s' % (phn__xli, x)) for phn__xli, x in
        enumerate(aeoj__wtltz)])
    gzk__sdm = ','.join([('c_%d' % phn__xli) for phn__xli in range(
        ozpj__ezdfv)])
    qzvw__oqytj = list(nbr__khaj.co_varnames)
    dqil__arq = 0
    gif__lhi = nbr__khaj.co_argcount
    rbc__foss = caller_ir.get_definition(code_obj.defaults)
    if rbc__foss is not None:
        if isinstance(rbc__foss, tuple):
            jqyrk__zkfrj = [caller_ir.get_definition(x).value for x in
                rbc__foss]
            hfwj__dcutf = tuple(jqyrk__zkfrj)
        else:
            jqyrk__zkfrj = [caller_ir.get_definition(x).value for x in
                rbc__foss.items]
            hfwj__dcutf = tuple(jqyrk__zkfrj)
        dqil__arq = len(hfwj__dcutf)
    xmpm__yacw = gif__lhi - dqil__arq
    tggkh__qokx = ','.join([('%s' % qzvw__oqytj[phn__xli]) for phn__xli in
        range(xmpm__yacw)])
    if dqil__arq:
        roa__bqcd = [('%s = %s' % (qzvw__oqytj[phn__xli + xmpm__yacw],
            hfwj__dcutf[phn__xli])) for phn__xli in range(dqil__arq)]
        tggkh__qokx += ', '
        tggkh__qokx += ', '.join(roa__bqcd)
    return _create_function_from_code_obj(nbr__khaj, mfqx__gyvu,
        tggkh__qokx, gzk__sdm, cile__szs)


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
    for rwx__sxb, (xsnhz__kkgwm, lqd__yvh) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % lqd__yvh)
            crwzj__jpluo = _pass_registry.get(xsnhz__kkgwm).pass_inst
            if isinstance(crwzj__jpluo, CompilerPass):
                self._runPass(rwx__sxb, crwzj__jpluo, state)
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
                    pipeline_name, lqd__yvh)
                qknbv__bkr = self._patch_error(msg, e)
                raise qknbv__bkr
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
    zvt__ebjj = None
    snid__kljj = {}

    def lookup(var, already_seen, varonly=True):
        val = snid__kljj.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    emytn__aam = reduction_node.unversioned_name
    for phn__xli, stmt in enumerate(nodes):
        kpurp__qtumx = stmt.target
        xmvkr__zslbq = stmt.value
        snid__kljj[kpurp__qtumx.name] = xmvkr__zslbq
        if isinstance(xmvkr__zslbq, ir.Var
            ) and xmvkr__zslbq.name in snid__kljj:
            xmvkr__zslbq = lookup(xmvkr__zslbq, set())
        if isinstance(xmvkr__zslbq, ir.Expr):
            isl__ldd = set(lookup(giean__dcqzi, set(), True).name for
                giean__dcqzi in xmvkr__zslbq.list_vars())
            if name in isl__ldd:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(xmvkr__zslbq)]
                sol__mifmw = [x for x, auly__hrwy in args if auly__hrwy.
                    name != name]
                args = [(x, auly__hrwy) for x, auly__hrwy in args if x !=
                    auly__hrwy.name]
                rnir__zbkgw = dict(args)
                if len(sol__mifmw) == 1:
                    rnir__zbkgw[sol__mifmw[0]] = ir.Var(kpurp__qtumx.scope,
                        name + '#init', kpurp__qtumx.loc)
                replace_vars_inner(xmvkr__zslbq, rnir__zbkgw)
                zvt__ebjj = nodes[phn__xli:]
                break
    return zvt__ebjj


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
        ctgb__dkio = expand_aliases({giean__dcqzi.name for giean__dcqzi in
            stmt.list_vars()}, alias_map, arg_aliases)
        kcm__fty = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        mvcjx__ovodx = expand_aliases({giean__dcqzi.name for giean__dcqzi in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        mjt__lnwv = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(kcm__fty & mvcjx__ovodx | mjt__lnwv & ctgb__dkio) == 0:
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
    lavxb__sqmq = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            lavxb__sqmq.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                lavxb__sqmq.update(get_parfor_writes(stmt, func_ir))
    return lavxb__sqmq


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    lavxb__sqmq = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        lavxb__sqmq.add(stmt.target.name)
    if isinstance(stmt, bodo.ir.aggregate.Aggregate):
        lavxb__sqmq = {giean__dcqzi.name for giean__dcqzi in stmt.
            df_out_vars.values()}
        if stmt.out_key_vars is not None:
            lavxb__sqmq.update({giean__dcqzi.name for giean__dcqzi in stmt.
                out_key_vars})
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        lavxb__sqmq = {giean__dcqzi.name for giean__dcqzi in stmt.out_vars}
    if isinstance(stmt, bodo.ir.join.Join):
        lavxb__sqmq = {giean__dcqzi.name for giean__dcqzi in stmt.
            out_data_vars.values()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            lavxb__sqmq.update({giean__dcqzi.name for giean__dcqzi in stmt.
                out_key_arrs})
            lavxb__sqmq.update({giean__dcqzi.name for giean__dcqzi in stmt.
                df_out_vars.values()})
    if is_call_assign(stmt):
        ajke__xdl = guard(find_callname, func_ir, stmt.value)
        if ajke__xdl in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            lavxb__sqmq.add(stmt.value.args[0].name)
    return lavxb__sqmq


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
        yios__zmi = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        gsxr__pqnw = yios__zmi.format(self, msg)
        self.args = gsxr__pqnw,
    else:
        yios__zmi = _termcolor.errmsg('{0}')
        gsxr__pqnw = yios__zmi.format(self)
        self.args = gsxr__pqnw,
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
        for rkf__jjle in options['distributed']:
            dist_spec[rkf__jjle] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for rkf__jjle in options['distributed_block']:
            dist_spec[rkf__jjle] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    wjs__tcmf = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, txdz__jqf in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(txdz__jqf)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    kakjw__tdy = {}
    for jxbo__fini in reversed(inspect.getmro(cls)):
        kakjw__tdy.update(jxbo__fini.__dict__)
    odbv__kek, zri__xnz, szo__lcrxo, qet__vzjtj = {}, {}, {}, {}
    for ujwvn__hch, giean__dcqzi in kakjw__tdy.items():
        if isinstance(giean__dcqzi, pytypes.FunctionType):
            odbv__kek[ujwvn__hch] = giean__dcqzi
        elif isinstance(giean__dcqzi, property):
            zri__xnz[ujwvn__hch] = giean__dcqzi
        elif isinstance(giean__dcqzi, staticmethod):
            szo__lcrxo[ujwvn__hch] = giean__dcqzi
        else:
            qet__vzjtj[ujwvn__hch] = giean__dcqzi
    uze__bocx = (set(odbv__kek) | set(zri__xnz) | set(szo__lcrxo)) & set(spec)
    if uze__bocx:
        raise NameError('name shadowing: {0}'.format(', '.join(uze__bocx)))
    stwhs__zepve = qet__vzjtj.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(qet__vzjtj)
    if qet__vzjtj:
        msg = 'class members are not yet supported: {0}'
        fyno__sxmk = ', '.join(qet__vzjtj.keys())
        raise TypeError(msg.format(fyno__sxmk))
    for ujwvn__hch, giean__dcqzi in zri__xnz.items():
        if giean__dcqzi.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(ujwvn__hch))
    jit_methods = {ujwvn__hch: bodo.jit(returns_maybe_distributed=wjs__tcmf
        )(giean__dcqzi) for ujwvn__hch, giean__dcqzi in odbv__kek.items()}
    jit_props = {}
    for ujwvn__hch, giean__dcqzi in zri__xnz.items():
        tfun__ewbe = {}
        if giean__dcqzi.fget:
            tfun__ewbe['get'] = bodo.jit(giean__dcqzi.fget)
        if giean__dcqzi.fset:
            tfun__ewbe['set'] = bodo.jit(giean__dcqzi.fset)
        jit_props[ujwvn__hch] = tfun__ewbe
    jit_static_methods = {ujwvn__hch: bodo.jit(giean__dcqzi.__func__) for 
        ujwvn__hch, giean__dcqzi in szo__lcrxo.items()}
    lhrsd__zvt = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    vbvir__cbcf = dict(class_type=lhrsd__zvt, __doc__=stwhs__zepve)
    vbvir__cbcf.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), vbvir__cbcf)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, lhrsd__zvt)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(lhrsd__zvt, typingctx, targetctx).register()
    as_numba_type.register(cls, lhrsd__zvt.instance_type)
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
    cag__bzcmx = ','.join('{0}:{1}'.format(ujwvn__hch, giean__dcqzi) for 
        ujwvn__hch, giean__dcqzi in struct.items())
    jhtv__dpm = ','.join('{0}:{1}'.format(ujwvn__hch, giean__dcqzi) for 
        ujwvn__hch, giean__dcqzi in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), cag__bzcmx, jhtv__dpm)
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
    rrq__hda = numba.core.typeinfer.fold_arg_vars(typevars, self.args, self
        .vararg, self.kws)
    if rrq__hda is None:
        return
    saag__fxzf, mjf__adpo = rrq__hda
    for a in itertools.chain(saag__fxzf, mjf__adpo.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, saag__fxzf, mjf__adpo)
    except ForceLiteralArg as e:
        ijrgw__dktwy = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(ijrgw__dktwy, self.kws)
        eozzm__nic = set()
        swu__rst = set()
        kiuab__zkieq = {}
        for rwx__sxb in e.requested_args:
            rbsd__uhe = typeinfer.func_ir.get_definition(folded[rwx__sxb])
            if isinstance(rbsd__uhe, ir.Arg):
                eozzm__nic.add(rbsd__uhe.index)
                if rbsd__uhe.index in e.file_infos:
                    kiuab__zkieq[rbsd__uhe.index] = e.file_infos[rbsd__uhe.
                        index]
            else:
                swu__rst.add(rwx__sxb)
        if swu__rst:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif eozzm__nic:
            raise ForceLiteralArg(eozzm__nic, loc=self.loc, file_infos=
                kiuab__zkieq)
    if sig is None:
        chow__surj = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in saag__fxzf]
        args += [('%s=%s' % (ujwvn__hch, giean__dcqzi)) for ujwvn__hch,
            giean__dcqzi in sorted(mjf__adpo.items())]
        orgm__pzrtn = chow__surj.format(fnty, ', '.join(map(str, args)))
        tqbe__zgky = context.explain_function_type(fnty)
        msg = '\n'.join([orgm__pzrtn, tqbe__zgky])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        alzu__kyie = context.unify_pairs(sig.recvr, fnty.this)
        if alzu__kyie is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if alzu__kyie is not None and alzu__kyie.is_precise():
            yttl__qqizs = fnty.copy(this=alzu__kyie)
            typeinfer.propagate_refined_type(self.func, yttl__qqizs)
    if not sig.return_type.is_precise():
        qac__seiv = typevars[self.target]
        if qac__seiv.defined:
            zzly__pgw = qac__seiv.getone()
            if context.unify_pairs(zzly__pgw, sig.return_type) == zzly__pgw:
                sig = sig.replace(return_type=zzly__pgw)
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
        wlx__hwf = '*other* must be a {} but got a {} instead'
        raise TypeError(wlx__hwf.format(ForceLiteralArg, type(other)))
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
    vlled__qqpcj = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for ujwvn__hch, giean__dcqzi in kwargs.items():
        sznsj__pcvx = None
        try:
            lvr__icpk = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[lvr__icpk.name] = [giean__dcqzi]
            sznsj__pcvx = get_const_value_inner(func_ir, lvr__icpk)
            func_ir._definitions.pop(lvr__icpk.name)
            if isinstance(sznsj__pcvx, str):
                sznsj__pcvx = sigutils._parse_signature_string(sznsj__pcvx)
            if isinstance(sznsj__pcvx, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {ujwvn__hch} is annotated as type class {sznsj__pcvx}."""
                    )
            assert isinstance(sznsj__pcvx, types.Type)
            if isinstance(sznsj__pcvx, (types.List, types.Set)):
                sznsj__pcvx = sznsj__pcvx.copy(reflected=False)
            vlled__qqpcj[ujwvn__hch] = sznsj__pcvx
        except BodoError as ocow__gubem:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(sznsj__pcvx, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(giean__dcqzi, ir.Global):
                    msg = f'Global {giean__dcqzi.name!r} is not defined.'
                if isinstance(giean__dcqzi, ir.FreeVar):
                    msg = f'Freevar {giean__dcqzi.name!r} is not defined.'
            if isinstance(giean__dcqzi, ir.Expr
                ) and giean__dcqzi.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=ujwvn__hch, msg=msg, loc=loc)
    for name, typ in vlled__qqpcj.items():
        self._legalize_arg_type(name, typ, loc)
    return vlled__qqpcj


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
    dkq__dryy = inst.arg
    assert dkq__dryy > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(dkq__dryy)]))
    tmps = [state.make_temp() for _ in range(dkq__dryy - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    jpp__kiepo = ir.Global('format', format, loc=self.loc)
    self.store(value=jpp__kiepo, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    rrwb__wnlug = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=rrwb__wnlug, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    dkq__dryy = inst.arg
    assert dkq__dryy > 0, 'invalid BUILD_STRING count'
    kgk__tnc = self.get(strings[0])
    for other, iklh__alwx in zip(strings[1:], tmps):
        other = self.get(other)
        kawlc__urack = ir.Expr.binop(operator.add, lhs=kgk__tnc, rhs=other,
            loc=self.loc)
        self.store(kawlc__urack, iklh__alwx)
        kgk__tnc = self.get(iklh__alwx)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite.llvmpy.core import Type
    wlij__vac = self.context.insert_const_string(self.module, attr)
    fnty = Type.function(Type.int(), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, wlij__vac])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    dmwx__hodea = mk_unique_var(f'{var_name}')
    nzn__weexz = dmwx__hodea.replace('<', '_').replace('>', '_')
    nzn__weexz = nzn__weexz.replace('.', '_').replace('$', '_v')
    return nzn__weexz


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
        luje__fsvan = states['defmap']
        if len(luje__fsvan) == 0:
            yyn__gxunl = assign.target
            numba.core.ssa._logger.debug('first assign: %s', yyn__gxunl)
            if yyn__gxunl.name not in scope.localvars:
                yyn__gxunl = scope.define(assign.target.name, loc=assign.loc)
        else:
            yyn__gxunl = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=yyn__gxunl, value=assign.value, loc=
            assign.loc)
        luje__fsvan[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    cxs__nty = []
    for ujwvn__hch, giean__dcqzi in typing.npydecl.registry.globals:
        if ujwvn__hch == func:
            cxs__nty.append(giean__dcqzi)
    for ujwvn__hch, giean__dcqzi in typing.templates.builtin_registry.globals:
        if ujwvn__hch == func:
            cxs__nty.append(giean__dcqzi)
    if len(cxs__nty) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return cxs__nty


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    ydw__lpmw = {}
    ibp__jhh = find_topo_order(blocks)
    qvwan__zusx = {}
    for olw__ifmrm in ibp__jhh:
        block = blocks[olw__ifmrm]
        ehzpi__tvx = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                kpurp__qtumx = stmt.target.name
                xmvkr__zslbq = stmt.value
                if (xmvkr__zslbq.op == 'getattr' and xmvkr__zslbq.attr in
                    arr_math and isinstance(typemap[xmvkr__zslbq.value.name
                    ], types.npytypes.Array)):
                    xmvkr__zslbq = stmt.value
                    drx__ncnba = xmvkr__zslbq.value
                    ydw__lpmw[kpurp__qtumx] = drx__ncnba
                    scope = drx__ncnba.scope
                    loc = drx__ncnba.loc
                    bjhel__oywj = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[bjhel__oywj.name] = types.misc.Module(numpy)
                    zagj__jpbf = ir.Global('np', numpy, loc)
                    hkp__xxh = ir.Assign(zagj__jpbf, bjhel__oywj, loc)
                    xmvkr__zslbq.value = bjhel__oywj
                    ehzpi__tvx.append(hkp__xxh)
                    func_ir._definitions[bjhel__oywj.name] = [zagj__jpbf]
                    func = getattr(numpy, xmvkr__zslbq.attr)
                    zjw__lvsq = get_np_ufunc_typ_lst(func)
                    qvwan__zusx[kpurp__qtumx] = zjw__lvsq
                if (xmvkr__zslbq.op == 'call' and xmvkr__zslbq.func.name in
                    ydw__lpmw):
                    drx__ncnba = ydw__lpmw[xmvkr__zslbq.func.name]
                    ozdk__hsydg = calltypes.pop(xmvkr__zslbq)
                    zaqc__icw = ozdk__hsydg.args[:len(xmvkr__zslbq.args)]
                    zef__vvgq = {name: typemap[giean__dcqzi.name] for name,
                        giean__dcqzi in xmvkr__zslbq.kws}
                    ikg__jzi = qvwan__zusx[xmvkr__zslbq.func.name]
                    hxqm__bdmo = None
                    for vvxz__kxoj in ikg__jzi:
                        try:
                            hxqm__bdmo = vvxz__kxoj.get_call_type(typingctx,
                                [typemap[drx__ncnba.name]] + list(zaqc__icw
                                ), zef__vvgq)
                            typemap.pop(xmvkr__zslbq.func.name)
                            typemap[xmvkr__zslbq.func.name] = vvxz__kxoj
                            calltypes[xmvkr__zslbq] = hxqm__bdmo
                            break
                        except Exception as ocow__gubem:
                            pass
                    if hxqm__bdmo is None:
                        raise TypeError(
                            f'No valid template found for {xmvkr__zslbq.func.name}'
                            )
                    xmvkr__zslbq.args = [drx__ncnba] + xmvkr__zslbq.args
            ehzpi__tvx.append(stmt)
        block.body = ehzpi__tvx


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    xjfkm__hhxv = ufunc.nin
    dldvd__dgvpp = ufunc.nout
    xmpm__yacw = ufunc.nargs
    assert xmpm__yacw == xjfkm__hhxv + dldvd__dgvpp
    if len(args) < xjfkm__hhxv:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            xjfkm__hhxv))
    if len(args) > xmpm__yacw:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), xmpm__yacw)
            )
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    sod__jspa = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    knjrd__ujdv = max(sod__jspa)
    xizdz__gqkku = args[xjfkm__hhxv:]
    if not all(jqyrk__zkfrj == knjrd__ujdv for jqyrk__zkfrj in sod__jspa[
        xjfkm__hhxv:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(aha__jlj, types.ArrayCompatible) and not
        isinstance(aha__jlj, types.Bytes) for aha__jlj in xizdz__gqkku):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(aha__jlj.mutable for aha__jlj in xizdz__gqkku):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    xpya__ljwkg = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    opvi__cbltf = None
    if knjrd__ujdv > 0 and len(xizdz__gqkku) < ufunc.nout:
        opvi__cbltf = 'C'
        qnld__hhpj = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in qnld__hhpj and 'F' in qnld__hhpj:
            opvi__cbltf = 'F'
    return xpya__ljwkg, xizdz__gqkku, knjrd__ujdv, opvi__cbltf


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
        ryfx__egzf = 'Dict.key_type cannot be of type {}'
        raise TypingError(ryfx__egzf.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        ryfx__egzf = 'Dict.value_type cannot be of type {}'
        raise TypingError(ryfx__egzf.format(valty))
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
    for phn__xli, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(phn__xli))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    zdphc__koio = self.context, tuple(args), tuple(kws.items())
    try:
        mjsn__jgu, args = self._impl_cache[zdphc__koio]
        return mjsn__jgu, args
    except KeyError as ocow__gubem:
        pass
    mjsn__jgu, args = self._build_impl(zdphc__koio, args, kws)
    return mjsn__jgu, args


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
        pruxb__rjygv = find_topo_order(parfor.loop_body)
    yvntp__sdu = pruxb__rjygv[0]
    jmti__rwegz = {}
    _update_parfor_get_setitems(parfor.loop_body[yvntp__sdu].body, parfor.
        index_var, alias_map, jmti__rwegz, lives_n_aliases)
    ilrdd__oesai = set(jmti__rwegz.keys())
    for zfu__ivuy in pruxb__rjygv:
        if zfu__ivuy == yvntp__sdu:
            continue
        for stmt in parfor.loop_body[zfu__ivuy].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            mujla__pdqkd = set(giean__dcqzi.name for giean__dcqzi in stmt.
                list_vars())
            kjie__cgjn = mujla__pdqkd & ilrdd__oesai
            for a in kjie__cgjn:
                jmti__rwegz.pop(a, None)
    for zfu__ivuy in pruxb__rjygv:
        if zfu__ivuy == yvntp__sdu:
            continue
        block = parfor.loop_body[zfu__ivuy]
        xdph__kgyj = jmti__rwegz.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            xdph__kgyj, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    ebnrn__jsnd = max(blocks.keys())
    ixczn__dbgo, mek__jixuj = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    egmk__sicl = ir.Jump(ixczn__dbgo, ir.Loc('parfors_dummy', -1))
    blocks[ebnrn__jsnd].body.append(egmk__sicl)
    iqys__jyo = compute_cfg_from_blocks(blocks)
    oog__qaqb = compute_use_defs(blocks)
    jrer__uzmrs = compute_live_map(iqys__jyo, blocks, oog__qaqb.usemap,
        oog__qaqb.defmap)
    alias_set = set(alias_map.keys())
    for olw__ifmrm, block in blocks.items():
        ehzpi__tvx = []
        caaau__nbhky = {giean__dcqzi.name for giean__dcqzi in block.
            terminator.list_vars()}
        for paq__uyzfk, yclv__dgsbd in iqys__jyo.successors(olw__ifmrm):
            caaau__nbhky |= jrer__uzmrs[paq__uyzfk]
        for stmt in reversed(block.body):
            bkatm__ouqax = caaau__nbhky & alias_set
            for giean__dcqzi in bkatm__ouqax:
                caaau__nbhky |= alias_map[giean__dcqzi]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in caaau__nbhky and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                ajke__xdl = guard(find_callname, func_ir, stmt.value)
                if ajke__xdl == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in caaau__nbhky and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            caaau__nbhky |= {giean__dcqzi.name for giean__dcqzi in stmt.
                list_vars()}
            ehzpi__tvx.append(stmt)
        ehzpi__tvx.reverse()
        block.body = ehzpi__tvx
    typemap.pop(mek__jixuj.name)
    blocks[ebnrn__jsnd].body.pop()

    def trim_empty_parfor_branches(parfor):
        xgseo__dpk = False
        blocks = parfor.loop_body.copy()
        for olw__ifmrm, block in blocks.items():
            if len(block.body):
                olp__skc = block.body[-1]
                if isinstance(olp__skc, ir.Branch):
                    if len(blocks[olp__skc.truebr].body) == 1 and len(blocks
                        [olp__skc.falsebr].body) == 1:
                        lefra__ldb = blocks[olp__skc.truebr].body[0]
                        xwl__twd = blocks[olp__skc.falsebr].body[0]
                        if isinstance(lefra__ldb, ir.Jump) and isinstance(
                            xwl__twd, ir.Jump
                            ) and lefra__ldb.target == xwl__twd.target:
                            parfor.loop_body[olw__ifmrm].body[-1] = ir.Jump(
                                lefra__ldb.target, olp__skc.loc)
                            xgseo__dpk = True
                    elif len(blocks[olp__skc.truebr].body) == 1:
                        lefra__ldb = blocks[olp__skc.truebr].body[0]
                        if isinstance(lefra__ldb, ir.Jump
                            ) and lefra__ldb.target == olp__skc.falsebr:
                            parfor.loop_body[olw__ifmrm].body[-1] = ir.Jump(
                                lefra__ldb.target, olp__skc.loc)
                            xgseo__dpk = True
                    elif len(blocks[olp__skc.falsebr].body) == 1:
                        xwl__twd = blocks[olp__skc.falsebr].body[0]
                        if isinstance(xwl__twd, ir.Jump
                            ) and xwl__twd.target == olp__skc.truebr:
                            parfor.loop_body[olw__ifmrm].body[-1] = ir.Jump(
                                xwl__twd.target, olp__skc.loc)
                            xgseo__dpk = True
        return xgseo__dpk
    xgseo__dpk = True
    while xgseo__dpk:
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
        xgseo__dpk = trim_empty_parfor_branches(parfor)
    rirb__pgsy = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        rirb__pgsy &= len(block.body) == 0
    if rirb__pgsy:
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
    ejmyl__fzfw = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                ejmyl__fzfw += 1
                parfor = stmt
                vjhn__ngtv = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = vjhn__ngtv.scope
                loc = ir.Loc('parfors_dummy', -1)
                cnkv__apk = ir.Var(scope, mk_unique_var('$const'), loc)
                vjhn__ngtv.body.append(ir.Assign(ir.Const(0, loc),
                    cnkv__apk, loc))
                vjhn__ngtv.body.append(ir.Return(cnkv__apk, loc))
                iqys__jyo = compute_cfg_from_blocks(parfor.loop_body)
                for tas__lmvw in iqys__jyo.dead_nodes():
                    del parfor.loop_body[tas__lmvw]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                vjhn__ngtv = parfor.loop_body[max(parfor.loop_body.keys())]
                vjhn__ngtv.body.pop()
                vjhn__ngtv.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return ejmyl__fzfw


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
            tec__svyyv = self.overloads.get(tuple(args))
            if tec__svyyv is not None:
                return tec__svyyv.entry_point
            self._pre_compile(args, return_type, flags)
            bcg__xzlmp = self.func_ir
            smi__dbecg = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=smi__dbecg):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=bcg__xzlmp, args=args,
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
        sfg__edf = copy.deepcopy(flags)
        sfg__edf.no_rewrites = True

        def compile_local(the_ir, the_flags):
            nqk__btnby = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return nqk__btnby.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        xhrga__ltra = compile_local(func_ir, sfg__edf)
        wplf__tyo = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    wplf__tyo = compile_local(func_ir, flags)
                except Exception as ocow__gubem:
                    pass
        if wplf__tyo is not None:
            cres = wplf__tyo
        else:
            cres = xhrga__ltra
        return cres
    else:
        nqk__btnby = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return nqk__btnby.compile_ir(func_ir=func_ir, lifted=lifted,
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
    yhg__dizy = self.get_data_type(typ.dtype)
    liaps__nzirl = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        liaps__nzirl):
        glyqm__skl = ary.ctypes.data
        pfddq__cvdzo = self.add_dynamic_addr(builder, glyqm__skl, info=str(
            type(glyqm__skl)))
        kxgkl__ldl = self.add_dynamic_addr(builder, id(ary), info=str(type(
            ary)))
        self.global_arrays.append(ary)
    else:
        ofi__uafga = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            ofi__uafga = ofi__uafga.view('int64')
        ydey__wxiun = Constant.array(Type.int(8), bytearray(ofi__uafga.data))
        pfddq__cvdzo = cgutils.global_constant(builder, '.const.array.data',
            ydey__wxiun)
        pfddq__cvdzo.align = self.get_abi_alignment(yhg__dizy)
        kxgkl__ldl = None
    zei__scra = self.get_value_type(types.intp)
    smwmd__juwd = [self.get_constant(types.intp, xtgx__vzu) for xtgx__vzu in
        ary.shape]
    yialg__seg = Constant.array(zei__scra, smwmd__juwd)
    qhsnf__qzlx = [self.get_constant(types.intp, xtgx__vzu) for xtgx__vzu in
        ary.strides]
    tblb__nie = Constant.array(zei__scra, qhsnf__qzlx)
    stllq__hutot = self.get_constant(types.intp, ary.dtype.itemsize)
    jxog__iodp = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        jxog__iodp, stllq__hutot, pfddq__cvdzo.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), yialg__seg, tblb__nie])


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
    icn__uvw = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    jzgk__ehmwo = lir.Function(module, icn__uvw, name='nrt_atomic_{0}'.
        format(op))
    [ndrm__apnuk] = jzgk__ehmwo.args
    gdszi__lcwp = jzgk__ehmwo.append_basic_block()
    builder = lir.IRBuilder(gdszi__lcwp)
    anak__wfvo = lir.Constant(_word_type, 1)
    if False:
        itus__aibs = builder.atomic_rmw(op, ndrm__apnuk, anak__wfvo,
            ordering=ordering)
        res = getattr(builder, op)(itus__aibs, anak__wfvo)
        builder.ret(res)
    else:
        itus__aibs = builder.load(ndrm__apnuk)
        vsyrx__tmlj = getattr(builder, op)(itus__aibs, anak__wfvo)
        dwd__qnx = builder.icmp_signed('!=', itus__aibs, lir.Constant(
            itus__aibs.type, -1))
        with cgutils.if_likely(builder, dwd__qnx):
            builder.store(vsyrx__tmlj, ndrm__apnuk)
        builder.ret(vsyrx__tmlj)
    return jzgk__ehmwo


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
        xwhe__surg = state.targetctx.codegen()
        state.library = xwhe__surg.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    wuck__rpfdf = state.func_ir
    typemap = state.typemap
    ipd__pfjlb = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    ffm__qkkls = state.metadata
    vez__idex = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        nvnho__wri = (funcdesc.PythonFunctionDescriptor.
            from_specialized_function(wuck__rpfdf, typemap, ipd__pfjlb,
            calltypes, mangler=targetctx.mangler, inline=flags.forceinline,
            noalias=flags.noalias, abi_tags=[flags.get_mangle_string()]))
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            mkml__hqxy = lowering.Lower(targetctx, library, nvnho__wri,
                wuck__rpfdf, metadata=ffm__qkkls)
            mkml__hqxy.lower()
            if not flags.no_cpython_wrapper:
                mkml__hqxy.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(ipd__pfjlb, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        mkml__hqxy.create_cfunc_wrapper()
            oxcbc__frz = mkml__hqxy.env
            zwnt__dme = mkml__hqxy.call_helper
            del mkml__hqxy
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(nvnho__wri, zwnt__dme, cfunc=None,
                env=oxcbc__frz)
        else:
            dqyyi__ybfsq = targetctx.get_executable(library, nvnho__wri,
                oxcbc__frz)
            targetctx.insert_user_function(dqyyi__ybfsq, nvnho__wri, [library])
            state['cr'] = _LowerResult(nvnho__wri, zwnt__dme, cfunc=
                dqyyi__ybfsq, env=oxcbc__frz)
        ffm__qkkls['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        whs__wmsxu = llvm.passmanagers.dump_refprune_stats()
        ffm__qkkls['prune_stats'] = whs__wmsxu - vez__idex
        ffm__qkkls['llvm_pass_timings'] = library.recorded_timings
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
        ndxev__rplb = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, ndxev__rplb),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            loop.do_break()
        lycwn__hgkyh = c.builder.icmp_signed('!=', ndxev__rplb, expected_typobj
            )
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(lycwn__hgkyh, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, ndxev__rplb)
                c.pyapi.decref(ndxev__rplb)
                loop.do_break()
        c.pyapi.decref(ndxev__rplb)
    rygk__iyf, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(rygk__iyf, likely=True) as (if_ok, if_not_ok):
        with if_ok:
            list.size = size
            qqwj__clg = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                qqwj__clg), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        qqwj__clg))
                    with cgutils.for_range(c.builder, size) as loop:
                        itemobj = c.pyapi.list_getitem(obj, loop.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        gklqu__vxl = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(gklqu__vxl.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            loop.do_break()
                        list.setitem(loop.index, gklqu__vxl.value, incref=False
                            )
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
    bmosc__cmbi, uau__czl, xph__rko, alaj__dfu, iapl__gis = (
        compile_time_get_string_data(literal_string))
    nsnuv__fzlb = builder.module
    gv = context.insert_const_bytes(nsnuv__fzlb, bmosc__cmbi)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        uau__czl), context.get_constant(types.int32, xph__rko), context.
        get_constant(types.uint32, alaj__dfu), context.get_constant(
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
    bupr__srqzx = None
    if isinstance(shape, types.Integer):
        bupr__srqzx = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(xtgx__vzu, (types.Integer, types.IntEnumMember)) for
            xtgx__vzu in shape):
            bupr__srqzx = len(shape)
    return bupr__srqzx


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
            bupr__srqzx = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if bupr__srqzx == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, phn__xli) for phn__xli in
                    range(bupr__srqzx))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            gpgbs__ydxzb = self._get_names(x)
            if len(gpgbs__ydxzb) != 0:
                return gpgbs__ydxzb[0]
            return gpgbs__ydxzb
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    gpgbs__ydxzb = self._get_names(obj)
    if len(gpgbs__ydxzb) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(gpgbs__ydxzb[0])


def get_equiv_set(self, obj):
    gpgbs__ydxzb = self._get_names(obj)
    if len(gpgbs__ydxzb) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(gpgbs__ydxzb[0])


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
    oxpss__kep = []
    for nwwrm__gtyc in func_ir.arg_names:
        if nwwrm__gtyc in typemap and isinstance(typemap[nwwrm__gtyc],
            types.containers.UniTuple) and typemap[nwwrm__gtyc].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(nwwrm__gtyc))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for mhnmc__cgue in func_ir.blocks.values():
        for stmt in mhnmc__cgue.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    gha__coxx = getattr(val, 'code', None)
                    if gha__coxx is not None:
                        if getattr(val, 'closure', None) is not None:
                            pgd__umyw = '<creating a function from a closure>'
                            kawlc__urack = ''
                        else:
                            pgd__umyw = gha__coxx.co_name
                            kawlc__urack = '(%s) ' % pgd__umyw
                    else:
                        pgd__umyw = '<could not ascertain use case>'
                        kawlc__urack = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (pgd__umyw, kawlc__urack))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                twj__yanh = False
                if isinstance(val, pytypes.FunctionType):
                    twj__yanh = val in {numba.gdb, numba.gdb_init}
                if not twj__yanh:
                    twj__yanh = getattr(val, '_name', '') == 'gdb_internal'
                if twj__yanh:
                    oxpss__kep.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    cjyxk__unj = func_ir.get_definition(var)
                    xhx__cneec = guard(find_callname, func_ir, cjyxk__unj)
                    if xhx__cneec and xhx__cneec[1] == 'numpy':
                        ty = getattr(numpy, xhx__cneec[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    iybze__jejhi = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(iybze__jejhi), loc=stmt.loc)
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
    if len(oxpss__kep) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        eos__opkic = '\n'.join([x.strformat() for x in oxpss__kep])
        raise errors.UnsupportedError(msg % eos__opkic)


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
    ujwvn__hch, giean__dcqzi = next(iter(val.items()))
    csp__aka = typeof_impl(ujwvn__hch, c)
    fey__duz = typeof_impl(giean__dcqzi, c)
    if csp__aka is None or fey__duz is None:
        raise ValueError(
            f'Cannot type dict element type {type(ujwvn__hch)}, {type(giean__dcqzi)}'
            )
    return types.DictType(csp__aka, fey__duz)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    cke__hruak = cgutils.alloca_once_value(c.builder, val)
    ogwm__mxsn = c.pyapi.object_hasattr_string(val, '_opaque')
    vfz__mtg = c.builder.icmp_unsigned('==', ogwm__mxsn, lir.Constant(
        ogwm__mxsn.type, 0))
    xbiba__buh = typ.key_type
    dnhsm__hbp = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(xbiba__buh, dnhsm__hbp)

    def copy_dict(out_dict, in_dict):
        for ujwvn__hch, giean__dcqzi in in_dict.items():
            out_dict[ujwvn__hch] = giean__dcqzi
    with c.builder.if_then(vfz__mtg):
        tvvw__arj = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        umze__rzy = c.pyapi.call_function_objargs(tvvw__arj, [])
        lssvc__kgg = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(lssvc__kgg, [umze__rzy, val])
        c.builder.store(umze__rzy, cke__hruak)
    val = c.builder.load(cke__hruak)
    dpm__tgz = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    jzx__bprum = c.pyapi.object_type(val)
    puz__hxlc = c.builder.icmp_unsigned('==', jzx__bprum, dpm__tgz)
    with c.builder.if_else(puz__hxlc) as (then, orelse):
        with then:
            fbp__rak = c.pyapi.object_getattr_string(val, '_opaque')
            kjddz__qyf = types.MemInfoPointer(types.voidptr)
            gklqu__vxl = c.unbox(kjddz__qyf, fbp__rak)
            mi = gklqu__vxl.value
            zhibq__had = kjddz__qyf, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *zhibq__had)
            piyeh__judh = context.get_constant_null(zhibq__had[1])
            args = mi, piyeh__judh
            bsn__fqit, ihc__cifiy = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, ihc__cifiy)
            c.pyapi.decref(fbp__rak)
            duta__wsuaz = c.builder.basic_block
        with orelse:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", jzx__bprum, dpm__tgz)
            bxjsu__fdd = c.builder.basic_block
    bdowg__roitu = c.builder.phi(ihc__cifiy.type)
    nga__pdpg = c.builder.phi(bsn__fqit.type)
    bdowg__roitu.add_incoming(ihc__cifiy, duta__wsuaz)
    bdowg__roitu.add_incoming(ihc__cifiy.type(None), bxjsu__fdd)
    nga__pdpg.add_incoming(bsn__fqit, duta__wsuaz)
    nga__pdpg.add_incoming(cgutils.true_bit, bxjsu__fdd)
    c.pyapi.decref(dpm__tgz)
    c.pyapi.decref(jzx__bprum)
    with c.builder.if_then(vfz__mtg):
        c.pyapi.decref(val)
    return NativeValue(bdowg__roitu, is_error=nga__pdpg)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def mul_list_generic(self, args, kws):
    a, delx__ldav = args
    if isinstance(a, types.List) and isinstance(delx__ldav, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(delx__ldav, types.List):
        return signature(delx__ldav, types.intp, delx__ldav)


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
        wyh__yuwtc, pepf__xto = 0, 1
    else:
        wyh__yuwtc, pepf__xto = 1, 0
    mdqku__eyzsm = ListInstance(context, builder, sig.args[wyh__yuwtc],
        args[wyh__yuwtc])
    kvh__ggz = mdqku__eyzsm.size
    uxv__ibqe = args[pepf__xto]
    qqwj__clg = lir.Constant(uxv__ibqe.type, 0)
    uxv__ibqe = builder.select(cgutils.is_neg_int(builder, uxv__ibqe),
        qqwj__clg, uxv__ibqe)
    jxog__iodp = builder.mul(uxv__ibqe, kvh__ggz)
    haklt__sjf = ListInstance.allocate(context, builder, sig.return_type,
        jxog__iodp)
    haklt__sjf.size = jxog__iodp
    with cgutils.for_range_slice(builder, qqwj__clg, jxog__iodp, kvh__ggz,
        inc=True) as (dest_offset, _):
        with cgutils.for_range(builder, kvh__ggz) as loop:
            value = mdqku__eyzsm.getitem(loop.index)
            haklt__sjf.setitem(builder.add(loop.index, dest_offset), value,
                incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, haklt__sjf.value
        )
