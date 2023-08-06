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
        kirk__gxud = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, kirk__gxud)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[qgq__rhw].values) for
        qgq__rhw in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (jokag__vvli) for jokag__vvli in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    zmu__nhxao = c.context.insert_const_string(c.builder.module, 'pandas')
    vuhr__kfwc = c.pyapi.import_module_noblock(zmu__nhxao)
    ssi__zhg = c.pyapi.object_getattr_string(vuhr__kfwc, 'MultiIndex')
    ixe__kma = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), ixe__kma.data
        )
    ynu__ftcy = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        ixe__kma.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), ixe__kma.names)
    kjyp__luvm = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        ixe__kma.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ixe__kma.name)
    jxxnk__mkn = c.pyapi.from_native_value(typ.name_typ, ixe__kma.name, c.
        env_manager)
    ckcc__wgd = c.pyapi.borrow_none()
    zpuw__bstme = c.pyapi.call_method(ssi__zhg, 'from_arrays', (ynu__ftcy,
        ckcc__wgd, kjyp__luvm))
    c.pyapi.object_setattr_string(zpuw__bstme, 'name', jxxnk__mkn)
    c.pyapi.decref(ynu__ftcy)
    c.pyapi.decref(kjyp__luvm)
    c.pyapi.decref(jxxnk__mkn)
    c.pyapi.decref(vuhr__kfwc)
    c.pyapi.decref(ssi__zhg)
    c.context.nrt.decref(c.builder, typ, val)
    return zpuw__bstme


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    gkb__feyt = []
    wug__qnrvq = []
    for qgq__rhw in range(typ.nlevels):
        liwnp__qwsk = c.pyapi.unserialize(c.pyapi.serialize_object(qgq__rhw))
        asw__jbx = c.pyapi.call_method(val, 'get_level_values', (liwnp__qwsk,))
        ivg__zmi = c.pyapi.object_getattr_string(asw__jbx, 'values')
        c.pyapi.decref(asw__jbx)
        c.pyapi.decref(liwnp__qwsk)
        glh__jlna = c.pyapi.to_native_value(typ.array_types[qgq__rhw], ivg__zmi
            ).value
        gkb__feyt.append(glh__jlna)
        wug__qnrvq.append(ivg__zmi)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, gkb__feyt)
    else:
        data = cgutils.pack_struct(c.builder, gkb__feyt)
    kjyp__luvm = c.pyapi.object_getattr_string(val, 'names')
    eylh__uwzg = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    mce__tbbu = c.pyapi.call_function_objargs(eylh__uwzg, (kjyp__luvm,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), mce__tbbu
        ).value
    jxxnk__mkn = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, jxxnk__mkn).value
    ixe__kma = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ixe__kma.data = data
    ixe__kma.names = names
    ixe__kma.name = name
    for ivg__zmi in wug__qnrvq:
        c.pyapi.decref(ivg__zmi)
    c.pyapi.decref(kjyp__luvm)
    c.pyapi.decref(eylh__uwzg)
    c.pyapi.decref(mce__tbbu)
    c.pyapi.decref(jxxnk__mkn)
    return NativeValue(ixe__kma._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    gquk__ghzj = 'pandas.MultiIndex.from_product'
    srbkt__koe = dict(sortorder=sortorder)
    renu__axp = dict(sortorder=None)
    check_unsupported_args(gquk__ghzj, srbkt__koe, renu__axp, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{gquk__ghzj}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{gquk__ghzj}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{gquk__ghzj}: iterables and names must be of the same length.')


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
    rqc__fixuh = MultiIndexType(array_types, names_typ)
    oyzqz__rpxp = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, oyzqz__rpxp, rqc__fixuh)
    wodgf__tqw = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{oyzqz__rpxp}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    clgf__urqpl = {}
    exec(wodgf__tqw, globals(), clgf__urqpl)
    jmi__ykk = clgf__urqpl['impl']
    return jmi__ykk


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        tcf__yivcg, xzkh__rwkp, pmqts__mfsgs = args
        nmq__ixz = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        nmq__ixz.data = tcf__yivcg
        nmq__ixz.names = xzkh__rwkp
        nmq__ixz.name = pmqts__mfsgs
        context.nrt.incref(builder, signature.args[0], tcf__yivcg)
        context.nrt.incref(builder, signature.args[1], xzkh__rwkp)
        context.nrt.incref(builder, signature.args[2], pmqts__mfsgs)
        return nmq__ixz._getvalue()
    rroe__axzn = MultiIndexType(data.types, names.types, name)
    return rroe__axzn(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        kzmzu__asul = len(I.array_types)
        wodgf__tqw = 'def impl(I, ind):\n'
        wodgf__tqw += '  data = I._data\n'
        wodgf__tqw += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(f'ensure_contig_if_np(data[{qgq__rhw}][ind])' for
            qgq__rhw in range(kzmzu__asul))))
        clgf__urqpl = {}
        exec(wodgf__tqw, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, clgf__urqpl)
        jmi__ykk = clgf__urqpl['impl']
        return jmi__ykk


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    errxu__gtbjm, bef__ewdhc = sig.args
    if errxu__gtbjm != bef__ewdhc:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
