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
    ztrx__mau = MPI.COMM_WORLD
    ylo__liidb = ztrx__mau.Get_rank()
    wqkf__ymno = get_host_ranks()
    oafo__jphpf = get_nodes_first_ranks()
    if ylo__liidb in oafo__jphpf:
        try:
            alq__uzl = get_num_gpus(framework)
        except Exception as umhdg__iemld:
            alq__uzl = umhdg__iemld
        dioda__lafsc = create_subcomm_mpi4py(oafo__jphpf)
        iplee__yacqe = dioda__lafsc.gather(alq__uzl)
        if ylo__liidb == 0:
            gpu_ranks = []
            pcs__xkoow = None
            for mjde__pmy, dgn__unpzp in enumerate(wqkf__ymno.values()):
                euck__bbmc = iplee__yacqe[mjde__pmy]
                if isinstance(euck__bbmc, Exception):
                    pcs__xkoow = euck__bbmc
                    break
                if euck__bbmc == 0:
                    continue
                bfg__ddlqw = len(dgn__unpzp) // euck__bbmc
                for dmm__goump, iqiw__czwv in enumerate(dgn__unpzp):
                    if dmm__goump % bfg__ddlqw == 0:
                        ijt__jvxvo = dmm__goump / bfg__ddlqw
                        if ijt__jvxvo < euck__bbmc:
                            gpu_ranks.append(iqiw__czwv)
            if pcs__xkoow:
                ztrx__mau.bcast(pcs__xkoow)
                raise pcs__xkoow
            else:
                ztrx__mau.bcast(gpu_ranks)
    if ylo__liidb != 0:
        gpu_ranks = ztrx__mau.bcast(None)
        if isinstance(gpu_ranks, Exception):
            umhdg__iemld = gpu_ranks
            raise umhdg__iemld
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
    fffqj__ziu = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        dioda__lafsc = MPI.COMM_WORLD.Split(color=0 if fffqj__ziu in
            gpu_ranks else MPI.UNDEFINED, key=fffqj__ziu)
        if dioda__lafsc != MPI.COMM_NULL:
            hvd.init(comm=dioda__lafsc)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                fnjd__sve = tf.config.experimental.list_physical_devices('GPU')
                for zlgf__gip in fnjd__sve:
                    tf.config.experimental.set_memory_growth(zlgf__gip, True)
                tf.config.experimental.set_visible_devices(fnjd__sve[hvd.
                    local_rank()], 'GPU')
    else:
        if fffqj__ziu == 0:
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
        dgg__nrfe = 17
        ztrx__mau = MPI.COMM_WORLD
        zuh__otjj = MPI.Get_processor_name()
        ddg__hpm = get_host_ranks()[zuh__otjj]
        assert_dl_initialized()
        if bodo.get_rank() == ddg__hpm[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for ylo__liidb in ddg__hpm[1:]:
                ztrx__mau.isend(1, dest=ylo__liidb, tag=dgg__nrfe)
        else:
            while True:
                ayd__ubdk = MPI.Status()
                bmwl__kjimj = ztrx__mau.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    ayd__ubdk)
                if bmwl__kjimj:
                    assert ayd__ubdk.source == ddg__hpm[0]
                    assert ayd__ubdk.tag == dgg__nrfe
                    ztrx__mau.recv(source=0, tag=dgg__nrfe)
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
