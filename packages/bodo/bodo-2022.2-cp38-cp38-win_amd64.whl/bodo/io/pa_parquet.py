import asyncio
import os
import threading
from collections import defaultdict
from concurrent import futures
import pyarrow.parquet as pq
from bodo.io.fs_io import get_s3_bucket_region_njit


def get_parquet_filesnames_from_deltalake(delta_lake_path):
    try:
        from deltalake import DeltaTable
    except Exception as dxy__jcmj:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    xvqyc__vnswm = None
    znlcp__hmyim = delta_lake_path.rstrip('/')
    guhv__pryxe = 'AWS_DEFAULT_REGION' in os.environ
    ckt__sle = os.environ.get('AWS_DEFAULT_REGION', '')
    nxziy__ohw = False
    if delta_lake_path.startswith('s3://'):
        hwsc__xaw = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if hwsc__xaw != '':
            os.environ['AWS_DEFAULT_REGION'] = hwsc__xaw
            nxziy__ohw = True
    psssb__xird = DeltaTable(delta_lake_path)
    xvqyc__vnswm = psssb__xird.files()
    xvqyc__vnswm = [(znlcp__hmyim + '/' + lpn__sxk) for lpn__sxk in sorted(
        xvqyc__vnswm)]
    if nxziy__ohw:
        if guhv__pryxe:
            os.environ['AWS_DEFAULT_REGION'] = ckt__sle
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return xvqyc__vnswm


def get_dataset_schema(dataset):
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    zph__syhqe = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for unkf__ozy in dataset.partitions.partition_names:
            if zph__syhqe.get_field_index(unkf__ozy) != -1:
                ozsh__zzrpu = zph__syhqe.get_field_index(unkf__ozy)
                zph__syhqe = zph__syhqe.remove(ozsh__zzrpu)
    return zph__syhqe


class VisitLevelThread(threading.Thread):

    def __init__(self, manifest):
        threading.Thread.__init__(self)
        self.manifest = manifest
        self.exc = None

    def run(self):
        try:
            manifest = self.manifest
            manifest.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(manifest.loop)
            manifest.loop.run_until_complete(manifest._visit_level(0,
                manifest.dirpath, []))
        except Exception as dxy__jcmj:
            self.exc = dxy__jcmj
        finally:
            if hasattr(manifest, 'loop') and not manifest.loop.is_closed():
                manifest.loop.close()

    def join(self):
        super(VisitLevelThread, self).join()
        if self.exc:
            raise self.exc


class ParquetManifest:

    def __init__(self, dirpath, open_file_func=None, filesystem=None,
        pathsep='/', partition_scheme='hive', metadata_nthreads=1):
        filesystem, dirpath = pq._get_filesystem_and_path(filesystem, dirpath)
        self.filesystem = filesystem
        self.open_file_func = open_file_func
        self.pathsep = pathsep
        self.dirpath = pq._stringify_path(dirpath)
        self.partition_scheme = partition_scheme
        self.partitions = pq.ParquetPartitions()
        self.pieces = []
        self._metadata_nthreads = metadata_nthreads
        self._thread_pool = futures.ThreadPoolExecutor(max_workers=
            metadata_nthreads)
        self.common_metadata_path = None
        self.metadata_path = None
        self.delta_lake_filter = set()
        self.partition_vals = defaultdict(set)
        ssqo__qufrk = VisitLevelThread(self)
        ssqo__qufrk.start()
        ssqo__qufrk.join()
        for ggrkj__cxz in self.partition_vals.keys():
            self.partition_vals[ggrkj__cxz] = sorted(self.partition_vals[
                ggrkj__cxz])
        for hlib__bra in self.partitions.levels:
            hlib__bra.keys = sorted(hlib__bra.keys)
        for efg__nwgo in self.pieces:
            if efg__nwgo.partition_keys is not None:
                efg__nwgo.partition_keys = [(ubn__gamgg, self.
                    partition_vals[ubn__gamgg].index(nlpz__egzt)) for 
                    ubn__gamgg, nlpz__egzt in efg__nwgo.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, tnpju__vgs, base_path, bwm__njsxe):
        fs = self.filesystem
        wuks__gpi, cixdr__xlk, oxlt__gfuno = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if tnpju__vgs == 0 and '_delta_log' in cixdr__xlk:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        qad__ikwsy = []
        for znlcp__hmyim in oxlt__gfuno:
            if znlcp__hmyim == '':
                continue
            qwt__rcaa = self.pathsep.join((base_path, znlcp__hmyim))
            if znlcp__hmyim.endswith('_common_metadata'):
                self.common_metadata_path = qwt__rcaa
            elif znlcp__hmyim.endswith('_metadata'):
                self.metadata_path = qwt__rcaa
            elif self._should_silently_exclude(znlcp__hmyim):
                continue
            elif self.delta_lake_filter and qwt__rcaa not in self.delta_lake_filter:
                continue
            else:
                qad__ikwsy.append(qwt__rcaa)
        wmi__kue = [self.pathsep.join((base_path, hap__fhtb)) for hap__fhtb in
            cixdr__xlk if not pq._is_private_directory(hap__fhtb)]
        qad__ikwsy.sort()
        wmi__kue.sort()
        if len(qad__ikwsy) > 0 and len(wmi__kue) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(wmi__kue) > 0:
            await self._visit_directories(tnpju__vgs, wmi__kue, bwm__njsxe)
        else:
            self._push_pieces(qad__ikwsy, bwm__njsxe)

    async def _visit_directories(self, tnpju__vgs, cixdr__xlk, bwm__njsxe):
        iieq__ula = []
        for znlcp__hmyim in cixdr__xlk:
            tuz__ijpk, afhm__eqlw = pq._path_split(znlcp__hmyim, self.pathsep)
            ubn__gamgg, jeca__iuzwo = pq._parse_hive_partition(afhm__eqlw)
            cfwt__nwh = self.partitions.get_index(tnpju__vgs, ubn__gamgg,
                jeca__iuzwo)
            self.partition_vals[ubn__gamgg].add(jeca__iuzwo)
            cifxh__fkjzh = bwm__njsxe + [(ubn__gamgg, jeca__iuzwo)]
            iieq__ula.append(self._visit_level(tnpju__vgs + 1, znlcp__hmyim,
                cifxh__fkjzh))
        await asyncio.wait(iieq__ula)


ParquetManifest._should_silently_exclude = (pq.ParquetManifest.
    _should_silently_exclude)
ParquetManifest._parse_partition = pq.ParquetManifest._parse_partition
ParquetManifest._push_pieces = pq.ParquetManifest._push_pieces
pq.ParquetManifest = ParquetManifest


def pieces(self):
    return self._pieces


pq.ParquetDataset.pieces = property(pieces)


def partitions(self):
    return self._partitions


pq.ParquetDataset.partitions = property(partitions)
