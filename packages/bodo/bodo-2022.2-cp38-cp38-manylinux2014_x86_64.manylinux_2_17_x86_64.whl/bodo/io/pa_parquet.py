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
    except Exception as qmuey__sxmt:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    ogt__ynn = None
    vjn__ahf = delta_lake_path.rstrip('/')
    pxwk__ymhv = 'AWS_DEFAULT_REGION' in os.environ
    baweb__ila = os.environ.get('AWS_DEFAULT_REGION', '')
    vnip__uqw = False
    if delta_lake_path.startswith('s3://'):
        umn__dibj = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if umn__dibj != '':
            os.environ['AWS_DEFAULT_REGION'] = umn__dibj
            vnip__uqw = True
    nqf__ouh = DeltaTable(delta_lake_path)
    ogt__ynn = nqf__ouh.files()
    ogt__ynn = [(vjn__ahf + '/' + lmuq__qimgw) for lmuq__qimgw in sorted(
        ogt__ynn)]
    if vnip__uqw:
        if pxwk__ymhv:
            os.environ['AWS_DEFAULT_REGION'] = baweb__ila
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return ogt__ynn


def get_dataset_schema(dataset):
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    rsux__uzp = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for kvnw__ukr in dataset.partitions.partition_names:
            if rsux__uzp.get_field_index(kvnw__ukr) != -1:
                yavj__ika = rsux__uzp.get_field_index(kvnw__ukr)
                rsux__uzp = rsux__uzp.remove(yavj__ika)
    return rsux__uzp


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
        except Exception as qmuey__sxmt:
            self.exc = qmuey__sxmt
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
        zcako__khvf = VisitLevelThread(self)
        zcako__khvf.start()
        zcako__khvf.join()
        for rwez__crp in self.partition_vals.keys():
            self.partition_vals[rwez__crp] = sorted(self.partition_vals[
                rwez__crp])
        for wsr__ipzsr in self.partitions.levels:
            wsr__ipzsr.keys = sorted(wsr__ipzsr.keys)
        for kibc__bvvbc in self.pieces:
            if kibc__bvvbc.partition_keys is not None:
                kibc__bvvbc.partition_keys = [(kav__hiyat, self.
                    partition_vals[kav__hiyat].index(jigdd__bec)) for 
                    kav__hiyat, jigdd__bec in kibc__bvvbc.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, gaio__vyirb, base_path, ixp__pvuj):
        fs = self.filesystem
        bnimy__zowd, txk__gttu, dyua__gpog = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if gaio__vyirb == 0 and '_delta_log' in txk__gttu:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        umzm__qfjrc = []
        for vjn__ahf in dyua__gpog:
            if vjn__ahf == '':
                continue
            nueqg__onmxd = self.pathsep.join((base_path, vjn__ahf))
            if vjn__ahf.endswith('_common_metadata'):
                self.common_metadata_path = nueqg__onmxd
            elif vjn__ahf.endswith('_metadata'):
                self.metadata_path = nueqg__onmxd
            elif self._should_silently_exclude(vjn__ahf):
                continue
            elif self.delta_lake_filter and nueqg__onmxd not in self.delta_lake_filter:
                continue
            else:
                umzm__qfjrc.append(nueqg__onmxd)
        xrst__zgs = [self.pathsep.join((base_path, qtj__dlsue)) for
            qtj__dlsue in txk__gttu if not pq._is_private_directory(qtj__dlsue)
            ]
        umzm__qfjrc.sort()
        xrst__zgs.sort()
        if len(umzm__qfjrc) > 0 and len(xrst__zgs) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(xrst__zgs) > 0:
            await self._visit_directories(gaio__vyirb, xrst__zgs, ixp__pvuj)
        else:
            self._push_pieces(umzm__qfjrc, ixp__pvuj)

    async def _visit_directories(self, gaio__vyirb, txk__gttu, ixp__pvuj):
        lnnf__gica = []
        for vjn__ahf in txk__gttu:
            jpjc__lyap, qmbq__wti = pq._path_split(vjn__ahf, self.pathsep)
            kav__hiyat, svym__mqho = pq._parse_hive_partition(qmbq__wti)
            cdwmd__ycguv = self.partitions.get_index(gaio__vyirb,
                kav__hiyat, svym__mqho)
            self.partition_vals[kav__hiyat].add(svym__mqho)
            sbffr__wwj = ixp__pvuj + [(kav__hiyat, svym__mqho)]
            lnnf__gica.append(self._visit_level(gaio__vyirb + 1, vjn__ahf,
                sbffr__wwj))
        await asyncio.wait(lnnf__gica)


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
