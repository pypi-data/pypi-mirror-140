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
    rtjl__tsa = MPI.COMM_WORLD
    armnb__rilwx = rtjl__tsa.Get_rank()
    hesql__trl = get_host_ranks()
    ocyv__hzco = get_nodes_first_ranks()
    if armnb__rilwx in ocyv__hzco:
        try:
            nuvk__mlwl = get_num_gpus(framework)
        except Exception as vxde__ltu:
            nuvk__mlwl = vxde__ltu
        iexcu__pmjky = create_subcomm_mpi4py(ocyv__hzco)
        bvvvi__fll = iexcu__pmjky.gather(nuvk__mlwl)
        if armnb__rilwx == 0:
            gpu_ranks = []
            fta__mpku = None
            for ryp__frbvd, slngz__ycez in enumerate(hesql__trl.values()):
                orxf__qyw = bvvvi__fll[ryp__frbvd]
                if isinstance(orxf__qyw, Exception):
                    fta__mpku = orxf__qyw
                    break
                if orxf__qyw == 0:
                    continue
                lfz__fzmg = len(slngz__ycez) // orxf__qyw
                for gtcr__dnr, rrzkb__omyki in enumerate(slngz__ycez):
                    if gtcr__dnr % lfz__fzmg == 0:
                        ojh__ygvkj = gtcr__dnr / lfz__fzmg
                        if ojh__ygvkj < orxf__qyw:
                            gpu_ranks.append(rrzkb__omyki)
            if fta__mpku:
                rtjl__tsa.bcast(fta__mpku)
                raise fta__mpku
            else:
                rtjl__tsa.bcast(gpu_ranks)
    if armnb__rilwx != 0:
        gpu_ranks = rtjl__tsa.bcast(None)
        if isinstance(gpu_ranks, Exception):
            vxde__ltu = gpu_ranks
            raise vxde__ltu
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
    dwh__eci = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        iexcu__pmjky = MPI.COMM_WORLD.Split(color=0 if dwh__eci in
            gpu_ranks else MPI.UNDEFINED, key=dwh__eci)
        if iexcu__pmjky != MPI.COMM_NULL:
            hvd.init(comm=iexcu__pmjky)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                pzq__bymj = tf.config.experimental.list_physical_devices('GPU')
                for flug__hfe in pzq__bymj:
                    tf.config.experimental.set_memory_growth(flug__hfe, True)
                tf.config.experimental.set_visible_devices(pzq__bymj[hvd.
                    local_rank()], 'GPU')
    else:
        if dwh__eci == 0:
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
        eowj__xwu = 17
        rtjl__tsa = MPI.COMM_WORLD
        jzhwi__ahhcr = MPI.Get_processor_name()
        rqk__xwjzt = get_host_ranks()[jzhwi__ahhcr]
        assert_dl_initialized()
        if bodo.get_rank() == rqk__xwjzt[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for armnb__rilwx in rqk__xwjzt[1:]:
                rtjl__tsa.isend(1, dest=armnb__rilwx, tag=eowj__xwu)
        else:
            while True:
                zttdu__aswx = MPI.Status()
                jrvwl__ueybe = rtjl__tsa.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    zttdu__aswx)
                if jrvwl__ueybe:
                    assert zttdu__aswx.source == rqk__xwjzt[0]
                    assert zttdu__aswx.tag == eowj__xwu
                    rtjl__tsa.recv(source=0, tag=eowj__xwu)
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
