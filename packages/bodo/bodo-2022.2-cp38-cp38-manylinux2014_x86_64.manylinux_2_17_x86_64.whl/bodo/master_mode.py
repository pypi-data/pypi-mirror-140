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
        txdtn__tpk = state
        yaqcn__aupld = inspect.getsourcelines(txdtn__tpk)[0][0]
        assert yaqcn__aupld.startswith('@bodo.jit') or yaqcn__aupld.startswith(
            '@jit')
        svu__dmm = eval(yaqcn__aupld[1:])
        self.dispatcher = svu__dmm(txdtn__tpk)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    lqh__wosca = MPI.COMM_WORLD
    while True:
        ocyr__lotl = lqh__wosca.bcast(None, root=MASTER_RANK)
        if ocyr__lotl[0] == 'exec':
            txdtn__tpk = pickle.loads(ocyr__lotl[1])
            for skm__blgd, nkv__yqsqh in list(txdtn__tpk.__globals__.items()):
                if isinstance(nkv__yqsqh, MasterModeDispatcher):
                    txdtn__tpk.__globals__[skm__blgd] = nkv__yqsqh.dispatcher
            if txdtn__tpk.__module__ not in sys.modules:
                sys.modules[txdtn__tpk.__module__] = pytypes.ModuleType(
                    txdtn__tpk.__module__)
            yaqcn__aupld = inspect.getsourcelines(txdtn__tpk)[0][0]
            assert yaqcn__aupld.startswith('@bodo.jit'
                ) or yaqcn__aupld.startswith('@jit')
            svu__dmm = eval(yaqcn__aupld[1:])
            func = svu__dmm(txdtn__tpk)
            hnu__ckgrb = ocyr__lotl[2]
            zukwn__cwf = ocyr__lotl[3]
            yvbrl__gyx = []
            for twe__fdd in hnu__ckgrb:
                if twe__fdd == 'scatter':
                    yvbrl__gyx.append(bodo.scatterv(None))
                elif twe__fdd == 'bcast':
                    yvbrl__gyx.append(lqh__wosca.bcast(None, root=MASTER_RANK))
            tam__rzjde = {}
            for argname, twe__fdd in zukwn__cwf.items():
                if twe__fdd == 'scatter':
                    tam__rzjde[argname] = bodo.scatterv(None)
                elif twe__fdd == 'bcast':
                    tam__rzjde[argname] = lqh__wosca.bcast(None, root=
                        MASTER_RANK)
            jjlrf__sbsxs = func(*yvbrl__gyx, **tam__rzjde)
            if jjlrf__sbsxs is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(jjlrf__sbsxs)
            del (ocyr__lotl, txdtn__tpk, func, svu__dmm, hnu__ckgrb,
                zukwn__cwf, yvbrl__gyx, tam__rzjde, jjlrf__sbsxs)
            gc.collect()
        elif ocyr__lotl[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    lqh__wosca = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        hnu__ckgrb = ['scatter' for exqi__gaki in range(len(args))]
        zukwn__cwf = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        vnvy__sfgoz = func.py_func.__code__.co_varnames
        kjpn__bgw = func.targetoptions

        def get_distribution(argname):
            if argname in kjpn__bgw.get('distributed', []
                ) or argname in kjpn__bgw.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        hnu__ckgrb = [get_distribution(argname) for argname in vnvy__sfgoz[
            :len(args)]]
        zukwn__cwf = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    dslg__yhvbo = pickle.dumps(func.py_func)
    lqh__wosca.bcast(['exec', dslg__yhvbo, hnu__ckgrb, zukwn__cwf])
    yvbrl__gyx = []
    for qin__bxqv, twe__fdd in zip(args, hnu__ckgrb):
        if twe__fdd == 'scatter':
            yvbrl__gyx.append(bodo.scatterv(qin__bxqv))
        elif twe__fdd == 'bcast':
            lqh__wosca.bcast(qin__bxqv)
            yvbrl__gyx.append(qin__bxqv)
    tam__rzjde = {}
    for argname, qin__bxqv in kwargs.items():
        twe__fdd = zukwn__cwf[argname]
        if twe__fdd == 'scatter':
            tam__rzjde[argname] = bodo.scatterv(qin__bxqv)
        elif twe__fdd == 'bcast':
            lqh__wosca.bcast(qin__bxqv)
            tam__rzjde[argname] = qin__bxqv
    git__azd = []
    for skm__blgd, nkv__yqsqh in list(func.py_func.__globals__.items()):
        if isinstance(nkv__yqsqh, MasterModeDispatcher):
            git__azd.append((func.py_func.__globals__, skm__blgd, func.
                py_func.__globals__[skm__blgd]))
            func.py_func.__globals__[skm__blgd] = nkv__yqsqh.dispatcher
    jjlrf__sbsxs = func(*yvbrl__gyx, **tam__rzjde)
    for jtz__nqeg, skm__blgd, nkv__yqsqh in git__azd:
        jtz__nqeg[skm__blgd] = nkv__yqsqh
    if jjlrf__sbsxs is not None and func.overloads[func.signatures[0]
        ].metadata['is_return_distributed']:
        jjlrf__sbsxs = bodo.gatherv(jjlrf__sbsxs)
    return jjlrf__sbsxs


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
