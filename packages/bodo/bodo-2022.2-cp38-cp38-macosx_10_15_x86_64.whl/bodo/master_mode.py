import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        omto__bykhu = state
        nuf__rdqff = inspect.getsourcelines(omto__bykhu)[0][0]
        assert nuf__rdqff.startswith('@bodo.jit') or nuf__rdqff.startswith(
            '@jit')
        lysyr__xnm = eval(nuf__rdqff[1:])
        self.dispatcher = lysyr__xnm(omto__bykhu)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    zqv__nhde = MPI.COMM_WORLD
    while True:
        jdohj__xara = zqv__nhde.bcast(None, root=MASTER_RANK)
        if jdohj__xara[0] == 'exec':
            omto__bykhu = pickle.loads(jdohj__xara[1])
            for chvb__nzc, voik__rxvo in list(omto__bykhu.__globals__.items()):
                if isinstance(voik__rxvo, MasterModeDispatcher):
                    omto__bykhu.__globals__[chvb__nzc] = voik__rxvo.dispatcher
            if omto__bykhu.__module__ not in sys.modules:
                sys.modules[omto__bykhu.__module__] = pytypes.ModuleType(
                    omto__bykhu.__module__)
            nuf__rdqff = inspect.getsourcelines(omto__bykhu)[0][0]
            assert nuf__rdqff.startswith('@bodo.jit') or nuf__rdqff.startswith(
                '@jit')
            lysyr__xnm = eval(nuf__rdqff[1:])
            func = lysyr__xnm(omto__bykhu)
            bsgu__mroo = jdohj__xara[2]
            wsyq__ujeig = jdohj__xara[3]
            izml__umb = []
            for lws__yer in bsgu__mroo:
                if lws__yer == 'scatter':
                    izml__umb.append(bodo.scatterv(None))
                elif lws__yer == 'bcast':
                    izml__umb.append(zqv__nhde.bcast(None, root=MASTER_RANK))
            ueeu__tuq = {}
            for argname, lws__yer in wsyq__ujeig.items():
                if lws__yer == 'scatter':
                    ueeu__tuq[argname] = bodo.scatterv(None)
                elif lws__yer == 'bcast':
                    ueeu__tuq[argname] = zqv__nhde.bcast(None, root=MASTER_RANK
                        )
            lcne__lqmlb = func(*izml__umb, **ueeu__tuq)
            if lcne__lqmlb is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(lcne__lqmlb)
            del (jdohj__xara, omto__bykhu, func, lysyr__xnm, bsgu__mroo,
                wsyq__ujeig, izml__umb, ueeu__tuq, lcne__lqmlb)
            gc.collect()
        elif jdohj__xara[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    zqv__nhde = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        bsgu__mroo = ['scatter' for hsdfn__hxhiq in range(len(args))]
        wsyq__ujeig = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        gtzl__xlx = func.py_func.__code__.co_varnames
        pogv__uma = func.targetoptions

        def get_distribution(argname):
            if argname in pogv__uma.get('distributed', []
                ) or argname in pogv__uma.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        bsgu__mroo = [get_distribution(argname) for argname in gtzl__xlx[:
            len(args)]]
        wsyq__ujeig = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    xmpgu__zeym = pickle.dumps(func.py_func)
    zqv__nhde.bcast(['exec', xmpgu__zeym, bsgu__mroo, wsyq__ujeig])
    izml__umb = []
    for ddb__eegz, lws__yer in zip(args, bsgu__mroo):
        if lws__yer == 'scatter':
            izml__umb.append(bodo.scatterv(ddb__eegz))
        elif lws__yer == 'bcast':
            zqv__nhde.bcast(ddb__eegz)
            izml__umb.append(ddb__eegz)
    ueeu__tuq = {}
    for argname, ddb__eegz in kwargs.items():
        lws__yer = wsyq__ujeig[argname]
        if lws__yer == 'scatter':
            ueeu__tuq[argname] = bodo.scatterv(ddb__eegz)
        elif lws__yer == 'bcast':
            zqv__nhde.bcast(ddb__eegz)
            ueeu__tuq[argname] = ddb__eegz
    khxa__mwy = []
    for chvb__nzc, voik__rxvo in list(func.py_func.__globals__.items()):
        if isinstance(voik__rxvo, MasterModeDispatcher):
            khxa__mwy.append((func.py_func.__globals__, chvb__nzc, func.
                py_func.__globals__[chvb__nzc]))
            func.py_func.__globals__[chvb__nzc] = voik__rxvo.dispatcher
    lcne__lqmlb = func(*izml__umb, **ueeu__tuq)
    for gwn__raq, chvb__nzc, voik__rxvo in khxa__mwy:
        gwn__raq[chvb__nzc] = voik__rxvo
    if lcne__lqmlb is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        lcne__lqmlb = bodo.gatherv(lcne__lqmlb)
    return lcne__lqmlb


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
