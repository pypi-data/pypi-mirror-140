"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    zyymr__tfmr = MPI.COMM_WORLD
    dade__aqcjl = zyymr__tfmr.Get_rank()
    yjktd__dzaa = get_host_ranks()
    sqc__ngc = get_nodes_first_ranks()
    if dade__aqcjl in sqc__ngc:
        try:
            qhl__jun = get_num_gpus(framework)
        except Exception as dyv__ybo:
            qhl__jun = dyv__ybo
        yyffq__juvq = create_subcomm_mpi4py(sqc__ngc)
        vtp__gwrj = yyffq__juvq.gather(qhl__jun)
        if dade__aqcjl == 0:
            gpu_ranks = []
            ndx__ukjxq = None
            for wao__mqlwp, agei__bxj in enumerate(yjktd__dzaa.values()):
                ytjhw__xtocx = vtp__gwrj[wao__mqlwp]
                if isinstance(ytjhw__xtocx, Exception):
                    ndx__ukjxq = ytjhw__xtocx
                    break
                if ytjhw__xtocx == 0:
                    continue
                erq__pbafa = len(agei__bxj) // ytjhw__xtocx
                for jsh__qtkt, tyhi__ozavw in enumerate(agei__bxj):
                    if jsh__qtkt % erq__pbafa == 0:
                        qbmif__van = jsh__qtkt / erq__pbafa
                        if qbmif__van < ytjhw__xtocx:
                            gpu_ranks.append(tyhi__ozavw)
            if ndx__ukjxq:
                zyymr__tfmr.bcast(ndx__ukjxq)
                raise ndx__ukjxq
            else:
                zyymr__tfmr.bcast(gpu_ranks)
    if dade__aqcjl != 0:
        gpu_ranks = zyymr__tfmr.bcast(None)
        if isinstance(gpu_ranks, Exception):
            dyv__ybo = gpu_ranks
            raise dyv__ybo
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    ndm__gvrvo = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        yyffq__juvq = MPI.COMM_WORLD.Split(color=0 if ndm__gvrvo in
            gpu_ranks else MPI.UNDEFINED, key=ndm__gvrvo)
        if yyffq__juvq != MPI.COMM_NULL:
            hvd.init(comm=yyffq__juvq)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                tzzy__ypwl = tf.config.experimental.list_physical_devices('GPU'
                    )
                for okt__jzk in tzzy__ypwl:
                    tf.config.experimental.set_memory_growth(okt__jzk, True)
                tf.config.experimental.set_visible_devices(tzzy__ypwl[hvd.
                    local_rank()], 'GPU')
    else:
        if ndm__gvrvo == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        edtla__xtki = 17
        zyymr__tfmr = MPI.COMM_WORLD
        wpb__rwz = MPI.Get_processor_name()
        kczp__vxktz = get_host_ranks()[wpb__rwz]
        assert_dl_initialized()
        if bodo.get_rank() == kczp__vxktz[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for dade__aqcjl in kczp__vxktz[1:]:
                zyymr__tfmr.isend(1, dest=dade__aqcjl, tag=edtla__xtki)
        else:
            while True:
                qvlvn__fuai = MPI.Status()
                zxg__txjle = zyymr__tfmr.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    qvlvn__fuai)
                if zxg__txjle:
                    assert qvlvn__fuai.source == kczp__vxktz[0]
                    assert qvlvn__fuai.tag == edtla__xtki
                    zyymr__tfmr.recv(source=0, tag=edtla__xtki)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
