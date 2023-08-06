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
    xanrl__unm = context.get_python_api(builder)
    return xanrl__unm.unserialize(xanrl__unm.serialize_object(pyval))


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
        qozax__gsas = ', '.join('e{}'.format(thcuc__wedeb) for thcuc__wedeb in
            range(len(args)))
        if qozax__gsas:
            qozax__gsas += ', '
        gof__xbs = ', '.join("{} = ''".format(wdcwb__mtnx) for wdcwb__mtnx in
            kws.keys())
        gav__uet = f'def format_stub(string, {qozax__gsas} {gof__xbs}):\n'
        gav__uet += '    pass\n'
        xvsr__saiyu = {}
        exec(gav__uet, {}, xvsr__saiyu)
        hvecw__ijbj = xvsr__saiyu['format_stub']
        rtf__hqq = numba.core.utils.pysignature(hvecw__ijbj)
        dyv__weo = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, dyv__weo).replace(pysig=rtf__hqq)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for rxjy__diiv in ('logging.Logger', 'logging.RootLogger'):
        for xwqr__vin in func_names:
            rpmf__sxf = f'@bound_function("{rxjy__diiv}.{xwqr__vin}")\n'
            rpmf__sxf += (
                f'def resolve_{xwqr__vin}(self, logger_typ, args, kws):\n')
            rpmf__sxf += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(rpmf__sxf)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for bfnx__piplq in logging_logger_unsupported_attrs:
        swx__giaz = 'logging.Logger.' + bfnx__piplq
        overload_attribute(LoggingLoggerType, bfnx__piplq)(
            create_unsupported_overload(swx__giaz))
    for jxpm__gul in logging_logger_unsupported_methods:
        swx__giaz = 'logging.Logger.' + jxpm__gul
        overload_method(LoggingLoggerType, jxpm__gul)(
            create_unsupported_overload(swx__giaz))


_install_logging_logger_unsupported_objects()
