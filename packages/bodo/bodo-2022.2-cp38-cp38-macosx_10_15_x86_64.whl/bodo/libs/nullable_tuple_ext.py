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
        fdsvc__atib = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, fdsvc__atib)


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
        yclx__vwatj = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        yclx__vwatj.data = data_tuple
        yclx__vwatj.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return yclx__vwatj._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    oml__bkf = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, oml__bkf.data)
    c.context.nrt.incref(c.builder, typ.null_typ, oml__bkf.null_values)
    uypw__rlkx = c.pyapi.from_native_value(typ.tuple_typ, oml__bkf.data, c.
        env_manager)
    waef__dot = c.pyapi.from_native_value(typ.null_typ, oml__bkf.
        null_values, c.env_manager)
    vtonb__wow = c.context.get_constant(types.int64, len(typ.tuple_typ))
    unf__jez = c.pyapi.list_new(vtonb__wow)
    with cgutils.for_range(c.builder, vtonb__wow) as loop:
        i = loop.index
        yqp__kas = c.pyapi.long_from_longlong(i)
        bdkn__izle = c.pyapi.object_getitem(waef__dot, yqp__kas)
        wgi__icee = c.pyapi.to_native_value(types.bool_, bdkn__izle).value
        with c.builder.if_else(wgi__icee) as (then, orelse):
            with then:
                c.pyapi.list_setitem(unf__jez, i, c.pyapi.make_none())
            with orelse:
                vgnqc__zzzag = c.pyapi.object_getitem(uypw__rlkx, yqp__kas)
                c.pyapi.list_setitem(unf__jez, i, vgnqc__zzzag)
        c.pyapi.decref(yqp__kas)
        c.pyapi.decref(bdkn__izle)
    zrj__khpcd = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    ofshz__qdn = c.pyapi.call_function_objargs(zrj__khpcd, (unf__jez,))
    c.pyapi.decref(uypw__rlkx)
    c.pyapi.decref(waef__dot)
    c.pyapi.decref(zrj__khpcd)
    c.pyapi.decref(unf__jez)
    c.context.nrt.decref(c.builder, typ, val)
    return ofshz__qdn


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
    yclx__vwatj = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (yclx__vwatj.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    puw__emrir = 'def impl(val1, val2):\n'
    puw__emrir += '    data_tup1 = val1._data\n'
    puw__emrir += '    null_tup1 = val1._null_values\n'
    puw__emrir += '    data_tup2 = val2._data\n'
    puw__emrir += '    null_tup2 = val2._null_values\n'
    trqf__szhi = val1._tuple_typ
    for i in range(len(trqf__szhi)):
        puw__emrir += f'    null1_{i} = null_tup1[{i}]\n'
        puw__emrir += f'    null2_{i} = null_tup2[{i}]\n'
        puw__emrir += f'    data1_{i} = data_tup1[{i}]\n'
        puw__emrir += f'    data2_{i} = data_tup2[{i}]\n'
        puw__emrir += f'    if null1_{i} != null2_{i}:\n'
        puw__emrir += '        return False\n'
        puw__emrir += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        puw__emrir += f'        return False\n'
    puw__emrir += f'    return True\n'
    nxiw__ldxm = {}
    exec(puw__emrir, {}, nxiw__ldxm)
    impl = nxiw__ldxm['impl']
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
    puw__emrir = 'def impl(nullable_tup):\n'
    puw__emrir += '    data_tup = nullable_tup._data\n'
    puw__emrir += '    null_tup = nullable_tup._null_values\n'
    puw__emrir += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    puw__emrir += '    acc = _PyHASH_XXPRIME_5\n'
    trqf__szhi = nullable_tup._tuple_typ
    for i in range(len(trqf__szhi)):
        puw__emrir += f'    null_val_{i} = null_tup[{i}]\n'
        puw__emrir += f'    null_lane_{i} = hash(null_val_{i})\n'
        puw__emrir += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        puw__emrir += '        return -1\n'
        puw__emrir += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        puw__emrir += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        puw__emrir += '    acc *= _PyHASH_XXPRIME_1\n'
        puw__emrir += f'    if not null_val_{i}:\n'
        puw__emrir += f'        lane_{i} = hash(data_tup[{i}])\n'
        puw__emrir += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        puw__emrir += f'            return -1\n'
        puw__emrir += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        puw__emrir += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        puw__emrir += '        acc *= _PyHASH_XXPRIME_1\n'
    puw__emrir += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    puw__emrir += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    puw__emrir += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    puw__emrir += '    return numba.cpython.hashing.process_return(acc)\n'
    nxiw__ldxm = {}
    exec(puw__emrir, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, nxiw__ldxm)
    impl = nxiw__ldxm['impl']
    return impl
