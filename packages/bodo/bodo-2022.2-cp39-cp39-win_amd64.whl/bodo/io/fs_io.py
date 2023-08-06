"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from numba.core import types
from numba.extending import overload
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning
from bodo.utils.utils import check_java_installation
from fsspec.implementations.arrow import ArrowFSWrapper, ArrowFile, wrap_exceptions


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            spuq__lmuu = self.fs.open_input_file(path)
        except:
            spuq__lmuu = self.fs.open_input_stream(path)
    elif mode == 'wb':
        spuq__lmuu = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, spuq__lmuu, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    wremz__jtoy = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    kcygt__pkhx = False
    fbmez__rqifw = get_proxy_uri_from_env_vars()
    if storage_options:
        kcygt__pkhx = storage_options.get('anon', False)
    return S3FileSystem(anonymous=kcygt__pkhx, region=region,
        endpoint_override=wremz__jtoy, proxy_options=fbmez__rqifw)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    wremz__jtoy = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    kcygt__pkhx = False
    fbmez__rqifw = get_proxy_uri_from_env_vars()
    if storage_options:
        kcygt__pkhx = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=wremz__jtoy,
        anonymous=kcygt__pkhx, proxy_options=fbmez__rqifw)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    xxivi__bauyg = urlparse(path)
    if xxivi__bauyg.scheme in ('abfs', 'abfss'):
        kkuz__qfm = path
        if xxivi__bauyg.port is None:
            lpnc__nsynh = 0
        else:
            lpnc__nsynh = xxivi__bauyg.port
        pms__ssfuk = None
    else:
        kkuz__qfm = xxivi__bauyg.hostname
        lpnc__nsynh = xxivi__bauyg.port
        pms__ssfuk = xxivi__bauyg.username
    try:
        fs = HdFS(host=kkuz__qfm, port=lpnc__nsynh, user=pms__ssfuk)
    except Exception as rjkum__nvsoy:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            rjkum__nvsoy))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        qgnet__niej = fs.isdir(path)
    except gcsfs.utils.HttpError as rjkum__nvsoy:
        raise BodoError(
            f'{rjkum__nvsoy}. Make sure your google cloud credentials are set!'
            )
    return qgnet__niej


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [hxkip__aoy.split('/')[-1] for hxkip__aoy in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        xxivi__bauyg = urlparse(path)
        mnr__ediu = (xxivi__bauyg.netloc + xxivi__bauyg.path).rstrip('/')
        ayk__ybrs = fs.get_file_info(mnr__ediu)
        if ayk__ybrs.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not ayk__ybrs.size and ayk__ybrs.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as rjkum__nvsoy:
        raise
    except BodoError as hzmz__dzn:
        raise
    except Exception as rjkum__nvsoy:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(rjkum__nvsoy).__name__}: {str(rjkum__nvsoy)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    jeq__ywqc = None
    try:
        if s3_is_directory(fs, path):
            xxivi__bauyg = urlparse(path)
            mnr__ediu = (xxivi__bauyg.netloc + xxivi__bauyg.path).rstrip('/')
            rev__jqdg = pa_fs.FileSelector(mnr__ediu, recursive=False)
            cnb__mdxfz = fs.get_file_info(rev__jqdg)
            if cnb__mdxfz and cnb__mdxfz[0].path in [mnr__ediu, f'{mnr__ediu}/'
                ] and int(cnb__mdxfz[0].size or 0) == 0:
                cnb__mdxfz = cnb__mdxfz[1:]
            jeq__ywqc = [eun__bsln.base_name for eun__bsln in cnb__mdxfz]
    except BodoError as hzmz__dzn:
        raise
    except Exception as rjkum__nvsoy:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(rjkum__nvsoy).__name__}: {str(rjkum__nvsoy)}
{bodo_error_msg}"""
            )
    return jeq__ywqc


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    xxivi__bauyg = urlparse(path)
    dmry__ppw = xxivi__bauyg.path
    try:
        camr__lgrdc = HadoopFileSystem.from_uri(path)
    except Exception as rjkum__nvsoy:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            rjkum__nvsoy))
    igu__zojm = camr__lgrdc.get_file_info([dmry__ppw])
    if igu__zojm[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not igu__zojm[0].size and igu__zojm[0].type == FileType.Directory:
        return camr__lgrdc, True
    return camr__lgrdc, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    jeq__ywqc = None
    camr__lgrdc, qgnet__niej = hdfs_is_directory(path)
    if qgnet__niej:
        xxivi__bauyg = urlparse(path)
        dmry__ppw = xxivi__bauyg.path
        rev__jqdg = FileSelector(dmry__ppw, recursive=True)
        try:
            cnb__mdxfz = camr__lgrdc.get_file_info(rev__jqdg)
        except Exception as rjkum__nvsoy:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(dmry__ppw, rjkum__nvsoy))
        jeq__ywqc = [eun__bsln.base_name for eun__bsln in cnb__mdxfz]
    return camr__lgrdc, jeq__ywqc


def abfs_is_directory(path):
    camr__lgrdc = get_hdfs_fs(path)
    try:
        igu__zojm = camr__lgrdc.info(path)
    except OSError as hzmz__dzn:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if igu__zojm['size'] == 0 and igu__zojm['kind'].lower() == 'directory':
        return camr__lgrdc, True
    return camr__lgrdc, False


def abfs_list_dir_fnames(path):
    jeq__ywqc = None
    camr__lgrdc, qgnet__niej = abfs_is_directory(path)
    if qgnet__niej:
        xxivi__bauyg = urlparse(path)
        dmry__ppw = xxivi__bauyg.path
        try:
            ldz__vmur = camr__lgrdc.ls(dmry__ppw)
        except Exception as rjkum__nvsoy:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(dmry__ppw, rjkum__nvsoy))
        jeq__ywqc = [fname[fname.rindex('/') + 1:] for fname in ldz__vmur]
    return camr__lgrdc, jeq__ywqc


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype):
    from urllib.parse import urlparse
    qzxw__dou = urlparse(path)
    fname = path
    fs = None
    wrpzb__otge = 'read_json' if ftype == 'json' else 'read_csv'
    dwpmn__zvc = (
        f'pd.{wrpzb__otge}(): there is no {ftype} file in directory: {fname}')
    opxjt__pxg = directory_of_files_common_filter
    if qzxw__dou.scheme == 's3':
        zgznj__pqabb = True
        fs = get_s3_fs_from_path(path)
        rcqp__tczlq = s3_list_dir_fnames(fs, path)
        mnr__ediu = (qzxw__dou.netloc + qzxw__dou.path).rstrip('/')
        fname = mnr__ediu
        if rcqp__tczlq:
            rcqp__tczlq = [(mnr__ediu + '/' + hxkip__aoy) for hxkip__aoy in
                sorted(filter(opxjt__pxg, rcqp__tczlq))]
            rhi__oezx = [hxkip__aoy for hxkip__aoy in rcqp__tczlq if int(fs
                .get_file_info(hxkip__aoy).size or 0) > 0]
            if len(rhi__oezx) == 0:
                raise BodoError(dwpmn__zvc)
            fname = rhi__oezx[0]
        bpcp__sag = int(fs.get_file_info(fname).size or 0)
        kdu__khbk = fs.open_input_file(fname)
    elif qzxw__dou.scheme == 'hdfs':
        zgznj__pqabb = True
        fs, rcqp__tczlq = hdfs_list_dir_fnames(path)
        bpcp__sag = fs.get_file_info([qzxw__dou.path])[0].size
        if rcqp__tczlq:
            path = path.rstrip('/')
            rcqp__tczlq = [(path + '/' + hxkip__aoy) for hxkip__aoy in
                sorted(filter(opxjt__pxg, rcqp__tczlq))]
            rhi__oezx = [hxkip__aoy for hxkip__aoy in rcqp__tczlq if fs.
                get_file_info([urlparse(hxkip__aoy).path])[0].size > 0]
            if len(rhi__oezx) == 0:
                raise BodoError(dwpmn__zvc)
            fname = rhi__oezx[0]
            fname = urlparse(fname).path
            bpcp__sag = fs.get_file_info([fname])[0].size
        kdu__khbk = fs.open_input_file(fname)
    elif qzxw__dou.scheme in ('abfs', 'abfss'):
        zgznj__pqabb = True
        fs, rcqp__tczlq = abfs_list_dir_fnames(path)
        bpcp__sag = fs.info(fname)['size']
        if rcqp__tczlq:
            path = path.rstrip('/')
            rcqp__tczlq = [(path + '/' + hxkip__aoy) for hxkip__aoy in
                sorted(filter(opxjt__pxg, rcqp__tczlq))]
            rhi__oezx = [hxkip__aoy for hxkip__aoy in rcqp__tczlq if fs.
                info(hxkip__aoy)['size'] > 0]
            if len(rhi__oezx) == 0:
                raise BodoError(dwpmn__zvc)
            fname = rhi__oezx[0]
            bpcp__sag = fs.info(fname)['size']
            fname = urlparse(fname).path
        kdu__khbk = fs.open(fname, 'rb')
    else:
        if qzxw__dou.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {qzxw__dou.scheme}. Please refer to https://docs.bodo.ai/latest/source/file_io.html'
                )
        zgznj__pqabb = False
        if os.path.isdir(path):
            ldz__vmur = filter(opxjt__pxg, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            rhi__oezx = [hxkip__aoy for hxkip__aoy in sorted(ldz__vmur) if 
                os.path.getsize(hxkip__aoy) > 0]
            if len(rhi__oezx) == 0:
                raise BodoError(dwpmn__zvc)
            fname = rhi__oezx[0]
        bpcp__sag = os.path.getsize(fname)
        kdu__khbk = fname
    return zgznj__pqabb, kdu__khbk, bpcp__sag, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    wuit__pbdp = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            znofn__aypna, kke__ybi = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = znofn__aypna.region
        except Exception as rjkum__nvsoy:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{rjkum__nvsoy}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = wuit__pbdp.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, is_parallel=False):

    def impl(path_or_buf, D, is_parallel=False):
        fhjzn__grzq = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        pdnei__kjbbh, gtbuh__grh = unicode_to_utf8_and_len(D)
        jhuy__roc = 0
        if is_parallel:
            jhuy__roc = bodo.libs.distributed_api.dist_exscan(gtbuh__grh,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), pdnei__kjbbh, jhuy__roc,
            gtbuh__grh, is_parallel, unicode_to_utf8(fhjzn__grzq))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl
