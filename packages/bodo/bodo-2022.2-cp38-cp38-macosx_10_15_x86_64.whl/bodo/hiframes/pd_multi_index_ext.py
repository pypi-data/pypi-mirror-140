"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.Type):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        saz__xtn = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, saz__xtn)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[gksbi__jlghq].values) for
        gksbi__jlghq in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (tpdxp__kcp) for tpdxp__kcp in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    chwg__xzak = c.context.insert_const_string(c.builder.module, 'pandas')
    qapew__iera = c.pyapi.import_module_noblock(chwg__xzak)
    lsbk__vsu = c.pyapi.object_getattr_string(qapew__iera, 'MultiIndex')
    chknd__ogamf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        chknd__ogamf.data)
    rzwjw__nuxve = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        chknd__ogamf.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ),
        chknd__ogamf.names)
    xydgh__yolfc = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        chknd__ogamf.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, chknd__ogamf.name)
    epix__oxl = c.pyapi.from_native_value(typ.name_typ, chknd__ogamf.name,
        c.env_manager)
    ymhpp__uyvdc = c.pyapi.borrow_none()
    tbvt__ypzh = c.pyapi.call_method(lsbk__vsu, 'from_arrays', (
        rzwjw__nuxve, ymhpp__uyvdc, xydgh__yolfc))
    c.pyapi.object_setattr_string(tbvt__ypzh, 'name', epix__oxl)
    c.pyapi.decref(rzwjw__nuxve)
    c.pyapi.decref(xydgh__yolfc)
    c.pyapi.decref(epix__oxl)
    c.pyapi.decref(qapew__iera)
    c.pyapi.decref(lsbk__vsu)
    c.context.nrt.decref(c.builder, typ, val)
    return tbvt__ypzh


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    jio__dwav = []
    dbm__wty = []
    for gksbi__jlghq in range(typ.nlevels):
        hdya__xtg = c.pyapi.unserialize(c.pyapi.serialize_object(gksbi__jlghq))
        ahi__uxnr = c.pyapi.call_method(val, 'get_level_values', (hdya__xtg,))
        ggnor__cdf = c.pyapi.object_getattr_string(ahi__uxnr, 'values')
        c.pyapi.decref(ahi__uxnr)
        c.pyapi.decref(hdya__xtg)
        zuvf__bdr = c.pyapi.to_native_value(typ.array_types[gksbi__jlghq],
            ggnor__cdf).value
        jio__dwav.append(zuvf__bdr)
        dbm__wty.append(ggnor__cdf)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, jio__dwav)
    else:
        data = cgutils.pack_struct(c.builder, jio__dwav)
    xydgh__yolfc = c.pyapi.object_getattr_string(val, 'names')
    hats__wgi = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    hbz__npbpf = c.pyapi.call_function_objargs(hats__wgi, (xydgh__yolfc,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), hbz__npbpf
        ).value
    epix__oxl = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, epix__oxl).value
    chknd__ogamf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    chknd__ogamf.data = data
    chknd__ogamf.names = names
    chknd__ogamf.name = name
    for ggnor__cdf in dbm__wty:
        c.pyapi.decref(ggnor__cdf)
    c.pyapi.decref(xydgh__yolfc)
    c.pyapi.decref(hats__wgi)
    c.pyapi.decref(hbz__npbpf)
    c.pyapi.decref(epix__oxl)
    return NativeValue(chknd__ogamf._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    shfnp__jha = 'pandas.MultiIndex.from_product'
    mmsry__itwav = dict(sortorder=sortorder)
    usd__evqd = dict(sortorder=None)
    check_unsupported_args(shfnp__jha, mmsry__itwav, usd__evqd,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{shfnp__jha}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{shfnp__jha}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{shfnp__jha}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    xblu__rbw = MultiIndexType(array_types, names_typ)
    yyhs__fxbsa = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, yyhs__fxbsa, xblu__rbw)
    wnteq__oobha = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{yyhs__fxbsa}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    wwm__opixw = {}
    exec(wnteq__oobha, globals(), wwm__opixw)
    ngpl__ghi = wwm__opixw['impl']
    return ngpl__ghi


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        harx__jon, dgrop__dkjw, xjw__eoiyg = args
        bsiru__zjg = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        bsiru__zjg.data = harx__jon
        bsiru__zjg.names = dgrop__dkjw
        bsiru__zjg.name = xjw__eoiyg
        context.nrt.incref(builder, signature.args[0], harx__jon)
        context.nrt.incref(builder, signature.args[1], dgrop__dkjw)
        context.nrt.incref(builder, signature.args[2], xjw__eoiyg)
        return bsiru__zjg._getvalue()
    ujhc__jtat = MultiIndexType(data.types, names.types, name)
    return ujhc__jtat(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        miw__tesv = len(I.array_types)
        wnteq__oobha = 'def impl(I, ind):\n'
        wnteq__oobha += '  data = I._data\n'
        wnteq__oobha += (
            '  return init_multi_index(({},), I._names, I._name)\n'.format(
            ', '.join(f'ensure_contig_if_np(data[{gksbi__jlghq}][ind])' for
            gksbi__jlghq in range(miw__tesv))))
        wwm__opixw = {}
        exec(wnteq__oobha, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, wwm__opixw)
        ngpl__ghi = wwm__opixw['impl']
        return ngpl__ghi


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    jxge__gaum, kmd__hgmpn = sig.args
    if jxge__gaum != kmd__hgmpn:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
