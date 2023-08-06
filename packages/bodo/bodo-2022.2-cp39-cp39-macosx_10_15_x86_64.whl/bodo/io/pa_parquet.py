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
    except Exception as qcf__ayplg:
        raise ImportError(
            "Bodo Error: please pip install the 'deltalake' package to read parquet from delta lake"
            )
    lhxp__njuu = None
    tmmno__awqwm = delta_lake_path.rstrip('/')
    wvqm__dkn = 'AWS_DEFAULT_REGION' in os.environ
    hyebk__nfne = os.environ.get('AWS_DEFAULT_REGION', '')
    teyt__mwizw = False
    if delta_lake_path.startswith('s3://'):
        ampy__ltl = get_s3_bucket_region_njit(delta_lake_path, parallel=False)
        if ampy__ltl != '':
            os.environ['AWS_DEFAULT_REGION'] = ampy__ltl
            teyt__mwizw = True
    esxvj__vlqj = DeltaTable(delta_lake_path)
    lhxp__njuu = esxvj__vlqj.files()
    lhxp__njuu = [(tmmno__awqwm + '/' + evcs__icn) for evcs__icn in sorted(
        lhxp__njuu)]
    if teyt__mwizw:
        if wvqm__dkn:
            os.environ['AWS_DEFAULT_REGION'] = hyebk__nfne
        else:
            del os.environ['AWS_DEFAULT_REGION']
    return lhxp__njuu


def get_dataset_schema(dataset):
    if dataset.metadata is None and dataset.schema is None:
        if dataset.common_metadata is not None:
            dataset.schema = dataset.common_metadata.schema
        else:
            dataset.schema = dataset.pieces[0].get_metadata().schema
    elif dataset.schema is None:
        dataset.schema = dataset.metadata.schema
    vqwz__vhs = dataset.schema.to_arrow_schema()
    if dataset.partitions is not None:
        for rkxs__cmci in dataset.partitions.partition_names:
            if vqwz__vhs.get_field_index(rkxs__cmci) != -1:
                sfgn__stbiz = vqwz__vhs.get_field_index(rkxs__cmci)
                vqwz__vhs = vqwz__vhs.remove(sfgn__stbiz)
    return vqwz__vhs


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
        except Exception as qcf__ayplg:
            self.exc = qcf__ayplg
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
        yxvor__zxid = VisitLevelThread(self)
        yxvor__zxid.start()
        yxvor__zxid.join()
        for bya__mtiks in self.partition_vals.keys():
            self.partition_vals[bya__mtiks] = sorted(self.partition_vals[
                bya__mtiks])
        for vlvy__cyocb in self.partitions.levels:
            vlvy__cyocb.keys = sorted(vlvy__cyocb.keys)
        for ksj__xwany in self.pieces:
            if ksj__xwany.partition_keys is not None:
                ksj__xwany.partition_keys = [(pnfg__ylf, self.
                    partition_vals[pnfg__ylf].index(nnw__nakmr)) for 
                    pnfg__ylf, nnw__nakmr in ksj__xwany.partition_keys]
        self.pieces.sort(key=lambda piece: piece.path)
        if self.common_metadata_path is None:
            self.common_metadata_path = self.metadata_path
        self._thread_pool.shutdown()

    async def _visit_level(self, eqtjh__jeubl, base_path, eqdlt__sxmye):
        fs = self.filesystem
        jwy__gfi, olrbs__buh, aiufc__jiuz = await self.loop.run_in_executor(
            self._thread_pool, lambda fs, base_bath: next(fs.walk(base_path
            )), fs, base_path)
        if eqtjh__jeubl == 0 and '_delta_log' in olrbs__buh:
            self.delta_lake_filter = set(get_parquet_filesnames_from_deltalake
                (base_path))
        bqdhk__bny = []
        for tmmno__awqwm in aiufc__jiuz:
            if tmmno__awqwm == '':
                continue
            mfxca__jcafc = self.pathsep.join((base_path, tmmno__awqwm))
            if tmmno__awqwm.endswith('_common_metadata'):
                self.common_metadata_path = mfxca__jcafc
            elif tmmno__awqwm.endswith('_metadata'):
                self.metadata_path = mfxca__jcafc
            elif self._should_silently_exclude(tmmno__awqwm):
                continue
            elif self.delta_lake_filter and mfxca__jcafc not in self.delta_lake_filter:
                continue
            else:
                bqdhk__bny.append(mfxca__jcafc)
        evv__tlhgj = [self.pathsep.join((base_path, lnpul__yhcl)) for
            lnpul__yhcl in olrbs__buh if not pq._is_private_directory(
            lnpul__yhcl)]
        bqdhk__bny.sort()
        evv__tlhgj.sort()
        if len(bqdhk__bny) > 0 and len(evv__tlhgj) > 0:
            raise ValueError('Found files in an intermediate directory: {}'
                .format(base_path))
        elif len(evv__tlhgj) > 0:
            await self._visit_directories(eqtjh__jeubl, evv__tlhgj,
                eqdlt__sxmye)
        else:
            self._push_pieces(bqdhk__bny, eqdlt__sxmye)

    async def _visit_directories(self, eqtjh__jeubl, olrbs__buh, eqdlt__sxmye):
        ucloh__atas = []
        for tmmno__awqwm in olrbs__buh:
            ben__uqn, iknkb__ftu = pq._path_split(tmmno__awqwm, self.pathsep)
            pnfg__ylf, gcuhy__xrmv = pq._parse_hive_partition(iknkb__ftu)
            imc__wecgs = self.partitions.get_index(eqtjh__jeubl, pnfg__ylf,
                gcuhy__xrmv)
            self.partition_vals[pnfg__ylf].add(gcuhy__xrmv)
            qzh__kja = eqdlt__sxmye + [(pnfg__ylf, gcuhy__xrmv)]
            ucloh__atas.append(self._visit_level(eqtjh__jeubl + 1,
                tmmno__awqwm, qzh__kja))
        await asyncio.wait(ucloh__atas)


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
