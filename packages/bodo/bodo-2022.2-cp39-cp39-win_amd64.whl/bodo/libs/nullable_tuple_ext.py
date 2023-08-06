"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ivf__xxid = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, ivf__xxid)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        ulnsq__gvxbv = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ulnsq__gvxbv.data = data_tuple
        ulnsq__gvxbv.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return ulnsq__gvxbv._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    uaama__fendi = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, uaama__fendi.data)
    c.context.nrt.incref(c.builder, typ.null_typ, uaama__fendi.null_values)
    gfjyj__sfzo = c.pyapi.from_native_value(typ.tuple_typ, uaama__fendi.
        data, c.env_manager)
    oxduz__kdmh = c.pyapi.from_native_value(typ.null_typ, uaama__fendi.
        null_values, c.env_manager)
    bmkp__usr = c.context.get_constant(types.int64, len(typ.tuple_typ))
    age__zdkof = c.pyapi.list_new(bmkp__usr)
    with cgutils.for_range(c.builder, bmkp__usr) as loop:
        i = loop.index
        fiykq__poj = c.pyapi.long_from_longlong(i)
        eylon__vsq = c.pyapi.object_getitem(oxduz__kdmh, fiykq__poj)
        innp__njdw = c.pyapi.to_native_value(types.bool_, eylon__vsq).value
        with c.builder.if_else(innp__njdw) as (then, orelse):
            with then:
                c.pyapi.list_setitem(age__zdkof, i, c.pyapi.make_none())
            with orelse:
                tafy__kopqn = c.pyapi.object_getitem(gfjyj__sfzo, fiykq__poj)
                c.pyapi.list_setitem(age__zdkof, i, tafy__kopqn)
        c.pyapi.decref(fiykq__poj)
        c.pyapi.decref(eylon__vsq)
    pxg__nknhr = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    ezmig__vajoo = c.pyapi.call_function_objargs(pxg__nknhr, (age__zdkof,))
    c.pyapi.decref(gfjyj__sfzo)
    c.pyapi.decref(oxduz__kdmh)
    c.pyapi.decref(pxg__nknhr)
    c.pyapi.decref(age__zdkof)
    c.context.nrt.decref(c.builder, typ, val)
    return ezmig__vajoo


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    ulnsq__gvxbv = cgutils.create_struct_proxy(sig.args[0])(context,
        builder, value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (ulnsq__gvxbv.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    bsxc__mrb = 'def impl(val1, val2):\n'
    bsxc__mrb += '    data_tup1 = val1._data\n'
    bsxc__mrb += '    null_tup1 = val1._null_values\n'
    bsxc__mrb += '    data_tup2 = val2._data\n'
    bsxc__mrb += '    null_tup2 = val2._null_values\n'
    ytfz__blje = val1._tuple_typ
    for i in range(len(ytfz__blje)):
        bsxc__mrb += f'    null1_{i} = null_tup1[{i}]\n'
        bsxc__mrb += f'    null2_{i} = null_tup2[{i}]\n'
        bsxc__mrb += f'    data1_{i} = data_tup1[{i}]\n'
        bsxc__mrb += f'    data2_{i} = data_tup2[{i}]\n'
        bsxc__mrb += f'    if null1_{i} != null2_{i}:\n'
        bsxc__mrb += '        return False\n'
        bsxc__mrb += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        bsxc__mrb += f'        return False\n'
    bsxc__mrb += f'    return True\n'
    kqk__ijn = {}
    exec(bsxc__mrb, {}, kqk__ijn)
    impl = kqk__ijn['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    bsxc__mrb = 'def impl(nullable_tup):\n'
    bsxc__mrb += '    data_tup = nullable_tup._data\n'
    bsxc__mrb += '    null_tup = nullable_tup._null_values\n'
    bsxc__mrb += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    bsxc__mrb += '    acc = _PyHASH_XXPRIME_5\n'
    ytfz__blje = nullable_tup._tuple_typ
    for i in range(len(ytfz__blje)):
        bsxc__mrb += f'    null_val_{i} = null_tup[{i}]\n'
        bsxc__mrb += f'    null_lane_{i} = hash(null_val_{i})\n'
        bsxc__mrb += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        bsxc__mrb += '        return -1\n'
        bsxc__mrb += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        bsxc__mrb += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        bsxc__mrb += '    acc *= _PyHASH_XXPRIME_1\n'
        bsxc__mrb += f'    if not null_val_{i}:\n'
        bsxc__mrb += f'        lane_{i} = hash(data_tup[{i}])\n'
        bsxc__mrb += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        bsxc__mrb += f'            return -1\n'
        bsxc__mrb += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        bsxc__mrb += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        bsxc__mrb += '        acc *= _PyHASH_XXPRIME_1\n'
    bsxc__mrb += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    bsxc__mrb += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    bsxc__mrb += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    bsxc__mrb += '    return numba.cpython.hashing.process_return(acc)\n'
    kqk__ijn = {}
    exec(bsxc__mrb, {'numba': numba, '_PyHASH_XXPRIME_1': _PyHASH_XXPRIME_1,
        '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2, '_PyHASH_XXPRIME_5':
        _PyHASH_XXPRIME_5}, kqk__ijn)
    impl = kqk__ijn['impl']
    return impl
