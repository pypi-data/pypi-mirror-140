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
        skb__bzya = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, skb__bzya)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[oet__hxux].values) for
        oet__hxux in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (bubxr__xvpib) for bubxr__xvpib in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    jqzn__ois = c.context.insert_const_string(c.builder.module, 'pandas')
    toeo__lkg = c.pyapi.import_module_noblock(jqzn__ois)
    rcv__lokts = c.pyapi.object_getattr_string(toeo__lkg, 'MultiIndex')
    dfqn__kxal = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        dfqn__kxal.data)
    ukv__wkm = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        dfqn__kxal.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), dfqn__kxal.
        names)
    gflp__gmi = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        dfqn__kxal.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, dfqn__kxal.name)
    xfaqo__kygq = c.pyapi.from_native_value(typ.name_typ, dfqn__kxal.name,
        c.env_manager)
    idbu__wzuzi = c.pyapi.borrow_none()
    lxpqh__vkk = c.pyapi.call_method(rcv__lokts, 'from_arrays', (ukv__wkm,
        idbu__wzuzi, gflp__gmi))
    c.pyapi.object_setattr_string(lxpqh__vkk, 'name', xfaqo__kygq)
    c.pyapi.decref(ukv__wkm)
    c.pyapi.decref(gflp__gmi)
    c.pyapi.decref(xfaqo__kygq)
    c.pyapi.decref(toeo__lkg)
    c.pyapi.decref(rcv__lokts)
    c.context.nrt.decref(c.builder, typ, val)
    return lxpqh__vkk


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    whf__zqia = []
    nxzc__pzbg = []
    for oet__hxux in range(typ.nlevels):
        erzxv__thkle = c.pyapi.unserialize(c.pyapi.serialize_object(oet__hxux))
        dfpf__wnw = c.pyapi.call_method(val, 'get_level_values', (
            erzxv__thkle,))
        wxd__dwv = c.pyapi.object_getattr_string(dfpf__wnw, 'values')
        c.pyapi.decref(dfpf__wnw)
        c.pyapi.decref(erzxv__thkle)
        wpnb__cxc = c.pyapi.to_native_value(typ.array_types[oet__hxux],
            wxd__dwv).value
        whf__zqia.append(wpnb__cxc)
        nxzc__pzbg.append(wxd__dwv)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, whf__zqia)
    else:
        data = cgutils.pack_struct(c.builder, whf__zqia)
    gflp__gmi = c.pyapi.object_getattr_string(val, 'names')
    gjsov__jjvx = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    zwyxh__mchdi = c.pyapi.call_function_objargs(gjsov__jjvx, (gflp__gmi,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), zwyxh__mchdi
        ).value
    xfaqo__kygq = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, xfaqo__kygq).value
    dfqn__kxal = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    dfqn__kxal.data = data
    dfqn__kxal.names = names
    dfqn__kxal.name = name
    for wxd__dwv in nxzc__pzbg:
        c.pyapi.decref(wxd__dwv)
    c.pyapi.decref(gflp__gmi)
    c.pyapi.decref(gjsov__jjvx)
    c.pyapi.decref(zwyxh__mchdi)
    c.pyapi.decref(xfaqo__kygq)
    return NativeValue(dfqn__kxal._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    zjg__ilvb = 'pandas.MultiIndex.from_product'
    zkwf__bvls = dict(sortorder=sortorder)
    ssm__iysd = dict(sortorder=None)
    check_unsupported_args(zjg__ilvb, zkwf__bvls, ssm__iysd, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{zjg__ilvb}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{zjg__ilvb}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{zjg__ilvb}: iterables and names must be of the same length.')


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
    amo__aod = MultiIndexType(array_types, names_typ)
    etmr__drf = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, etmr__drf, amo__aod)
    bqda__ibzse = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{etmr__drf}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    jme__pthf = {}
    exec(bqda__ibzse, globals(), jme__pthf)
    sua__jfk = jme__pthf['impl']
    return sua__jfk


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        ldns__ljna, hkbte__zplwc, uye__nlb = args
        jcni__fly = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jcni__fly.data = ldns__ljna
        jcni__fly.names = hkbte__zplwc
        jcni__fly.name = uye__nlb
        context.nrt.incref(builder, signature.args[0], ldns__ljna)
        context.nrt.incref(builder, signature.args[1], hkbte__zplwc)
        context.nrt.incref(builder, signature.args[2], uye__nlb)
        return jcni__fly._getvalue()
    uvlfi__ocz = MultiIndexType(data.types, names.types, name)
    return uvlfi__ocz(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        lklve__ivyg = len(I.array_types)
        bqda__ibzse = 'def impl(I, ind):\n'
        bqda__ibzse += '  data = I._data\n'
        bqda__ibzse += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{oet__hxux}][ind])' for oet__hxux in
            range(lklve__ivyg))))
        jme__pthf = {}
        exec(bqda__ibzse, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, jme__pthf)
        sua__jfk = jme__pthf['impl']
        return sua__jfk


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    aiun__xbggb, mbtf__foxo = sig.args
    if aiun__xbggb != mbtf__foxo:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
