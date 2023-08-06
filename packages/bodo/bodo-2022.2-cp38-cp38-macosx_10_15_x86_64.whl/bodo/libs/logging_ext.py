"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    fkdu__lmyhu = context.get_python_api(builder)
    return fkdu__lmyhu.unserialize(fkdu__lmyhu.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        rncko__gjcem = ', '.join('e{}'.format(nyv__yxs) for nyv__yxs in
            range(len(args)))
        if rncko__gjcem:
            rncko__gjcem += ', '
        fxcj__raezs = ', '.join("{} = ''".format(rjsvz__elm) for rjsvz__elm in
            kws.keys())
        hqoep__spj = (
            f'def format_stub(string, {rncko__gjcem} {fxcj__raezs}):\n')
        hqoep__spj += '    pass\n'
        egmpx__qngf = {}
        exec(hqoep__spj, {}, egmpx__qngf)
        bwt__tprei = egmpx__qngf['format_stub']
        wdf__nur = numba.core.utils.pysignature(bwt__tprei)
        qkvfi__aww = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, qkvfi__aww).replace(pysig=wdf__nur)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for epzjo__cmd in ('logging.Logger', 'logging.RootLogger'):
        for rnfz__owmxw in func_names:
            pxso__gtim = f'@bound_function("{epzjo__cmd}.{rnfz__owmxw}")\n'
            pxso__gtim += (
                f'def resolve_{rnfz__owmxw}(self, logger_typ, args, kws):\n')
            pxso__gtim += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(pxso__gtim)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for dppth__yrgf in logging_logger_unsupported_attrs:
        kbx__fowc = 'logging.Logger.' + dppth__yrgf
        overload_attribute(LoggingLoggerType, dppth__yrgf)(
            create_unsupported_overload(kbx__fowc))
    for zja__fhi in logging_logger_unsupported_methods:
        kbx__fowc = 'logging.Logger.' + zja__fhi
        overload_method(LoggingLoggerType, zja__fhi)(
            create_unsupported_overload(kbx__fowc))


_install_logging_logger_unsupported_objects()
