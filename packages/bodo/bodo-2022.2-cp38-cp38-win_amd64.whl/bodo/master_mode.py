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
        ftq__cmmrd = state
        hts__kcy = inspect.getsourcelines(ftq__cmmrd)[0][0]
        assert hts__kcy.startswith('@bodo.jit') or hts__kcy.startswith('@jit')
        uglfx__ioifd = eval(hts__kcy[1:])
        self.dispatcher = uglfx__ioifd(ftq__cmmrd)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    hnql__wfr = MPI.COMM_WORLD
    while True:
        jroi__bhwib = hnql__wfr.bcast(None, root=MASTER_RANK)
        if jroi__bhwib[0] == 'exec':
            ftq__cmmrd = pickle.loads(jroi__bhwib[1])
            for ylbpx__pwjlp, gfe__qxjvx in list(ftq__cmmrd.__globals__.items()
                ):
                if isinstance(gfe__qxjvx, MasterModeDispatcher):
                    ftq__cmmrd.__globals__[ylbpx__pwjlp
                        ] = gfe__qxjvx.dispatcher
            if ftq__cmmrd.__module__ not in sys.modules:
                sys.modules[ftq__cmmrd.__module__] = pytypes.ModuleType(
                    ftq__cmmrd.__module__)
            hts__kcy = inspect.getsourcelines(ftq__cmmrd)[0][0]
            assert hts__kcy.startswith('@bodo.jit') or hts__kcy.startswith(
                '@jit')
            uglfx__ioifd = eval(hts__kcy[1:])
            func = uglfx__ioifd(ftq__cmmrd)
            wvgeq__byoji = jroi__bhwib[2]
            rtzn__ppp = jroi__bhwib[3]
            ylu__udh = []
            for phjf__gew in wvgeq__byoji:
                if phjf__gew == 'scatter':
                    ylu__udh.append(bodo.scatterv(None))
                elif phjf__gew == 'bcast':
                    ylu__udh.append(hnql__wfr.bcast(None, root=MASTER_RANK))
            ubuxd__ehaiz = {}
            for argname, phjf__gew in rtzn__ppp.items():
                if phjf__gew == 'scatter':
                    ubuxd__ehaiz[argname] = bodo.scatterv(None)
                elif phjf__gew == 'bcast':
                    ubuxd__ehaiz[argname] = hnql__wfr.bcast(None, root=
                        MASTER_RANK)
            qcc__hul = func(*ylu__udh, **ubuxd__ehaiz)
            if qcc__hul is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(qcc__hul)
            del (jroi__bhwib, ftq__cmmrd, func, uglfx__ioifd, wvgeq__byoji,
                rtzn__ppp, ylu__udh, ubuxd__ehaiz, qcc__hul)
            gc.collect()
        elif jroi__bhwib[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    hnql__wfr = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        wvgeq__byoji = ['scatter' for xocv__ocb in range(len(args))]
        rtzn__ppp = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        jwfqw__mqfg = func.py_func.__code__.co_varnames
        ojql__gxu = func.targetoptions

        def get_distribution(argname):
            if argname in ojql__gxu.get('distributed', []
                ) or argname in ojql__gxu.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        wvgeq__byoji = [get_distribution(argname) for argname in
            jwfqw__mqfg[:len(args)]]
        rtzn__ppp = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    tdyn__dhium = pickle.dumps(func.py_func)
    hnql__wfr.bcast(['exec', tdyn__dhium, wvgeq__byoji, rtzn__ppp])
    ylu__udh = []
    for uzlt__idd, phjf__gew in zip(args, wvgeq__byoji):
        if phjf__gew == 'scatter':
            ylu__udh.append(bodo.scatterv(uzlt__idd))
        elif phjf__gew == 'bcast':
            hnql__wfr.bcast(uzlt__idd)
            ylu__udh.append(uzlt__idd)
    ubuxd__ehaiz = {}
    for argname, uzlt__idd in kwargs.items():
        phjf__gew = rtzn__ppp[argname]
        if phjf__gew == 'scatter':
            ubuxd__ehaiz[argname] = bodo.scatterv(uzlt__idd)
        elif phjf__gew == 'bcast':
            hnql__wfr.bcast(uzlt__idd)
            ubuxd__ehaiz[argname] = uzlt__idd
    cty__oow = []
    for ylbpx__pwjlp, gfe__qxjvx in list(func.py_func.__globals__.items()):
        if isinstance(gfe__qxjvx, MasterModeDispatcher):
            cty__oow.append((func.py_func.__globals__, ylbpx__pwjlp, func.
                py_func.__globals__[ylbpx__pwjlp]))
            func.py_func.__globals__[ylbpx__pwjlp] = gfe__qxjvx.dispatcher
    qcc__hul = func(*ylu__udh, **ubuxd__ehaiz)
    for gunz__fwhnf, ylbpx__pwjlp, gfe__qxjvx in cty__oow:
        gunz__fwhnf[ylbpx__pwjlp] = gfe__qxjvx
    if qcc__hul is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        qcc__hul = bodo.gatherv(qcc__hul)
    return qcc__hul


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
