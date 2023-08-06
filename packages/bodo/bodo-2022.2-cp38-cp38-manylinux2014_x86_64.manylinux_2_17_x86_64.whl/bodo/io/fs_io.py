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
            gcl__rtox = self.fs.open_input_file(path)
        except:
            gcl__rtox = self.fs.open_input_stream(path)
    elif mode == 'wb':
        gcl__rtox = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, gcl__rtox, path, mode, block_size, **kwargs)


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
    hbc__xtz = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wbadj__zhbsc = False
    bikwc__xohi = get_proxy_uri_from_env_vars()
    if storage_options:
        wbadj__zhbsc = storage_options.get('anon', False)
    return S3FileSystem(anonymous=wbadj__zhbsc, region=region,
        endpoint_override=hbc__xtz, proxy_options=bikwc__xohi)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    hbc__xtz = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    wbadj__zhbsc = False
    bikwc__xohi = get_proxy_uri_from_env_vars()
    if storage_options:
        wbadj__zhbsc = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=hbc__xtz, anonymous=
        wbadj__zhbsc, proxy_options=bikwc__xohi)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    qbfx__nzhwd = urlparse(path)
    if qbfx__nzhwd.scheme in ('abfs', 'abfss'):
        hkqb__eybd = path
        if qbfx__nzhwd.port is None:
            ehg__jtjo = 0
        else:
            ehg__jtjo = qbfx__nzhwd.port
        cdwus__pvz = None
    else:
        hkqb__eybd = qbfx__nzhwd.hostname
        ehg__jtjo = qbfx__nzhwd.port
        cdwus__pvz = qbfx__nzhwd.username
    try:
        fs = HdFS(host=hkqb__eybd, port=ehg__jtjo, user=cdwus__pvz)
    except Exception as tldg__slziz:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            tldg__slziz))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        ecso__tfd = fs.isdir(path)
    except gcsfs.utils.HttpError as tldg__slziz:
        raise BodoError(
            f'{tldg__slziz}. Make sure your google cloud credentials are set!')
    return ecso__tfd


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [wgkj__azrw.split('/')[-1] for wgkj__azrw in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        qbfx__nzhwd = urlparse(path)
        epovf__avuc = (qbfx__nzhwd.netloc + qbfx__nzhwd.path).rstrip('/')
        xclou__soimv = fs.get_file_info(epovf__avuc)
        if xclou__soimv.type in (pa_fs.FileType.NotFound, pa_fs.FileType.
            Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not xclou__soimv.size and xclou__soimv.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as tldg__slziz:
        raise
    except BodoError as yuyn__rdw:
        raise
    except Exception as tldg__slziz:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(tldg__slziz).__name__}: {str(tldg__slziz)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    nab__zasss = None
    try:
        if s3_is_directory(fs, path):
            qbfx__nzhwd = urlparse(path)
            epovf__avuc = (qbfx__nzhwd.netloc + qbfx__nzhwd.path).rstrip('/')
            jxdf__hreb = pa_fs.FileSelector(epovf__avuc, recursive=False)
            uyeyt__hxfa = fs.get_file_info(jxdf__hreb)
            if uyeyt__hxfa and uyeyt__hxfa[0].path in [epovf__avuc,
                f'{epovf__avuc}/'] and int(uyeyt__hxfa[0].size or 0) == 0:
                uyeyt__hxfa = uyeyt__hxfa[1:]
            nab__zasss = [vlkw__mzy.base_name for vlkw__mzy in uyeyt__hxfa]
    except BodoError as yuyn__rdw:
        raise
    except Exception as tldg__slziz:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(tldg__slziz).__name__}: {str(tldg__slziz)}
{bodo_error_msg}"""
            )
    return nab__zasss


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    qbfx__nzhwd = urlparse(path)
    xkpx__wwyj = qbfx__nzhwd.path
    try:
        gbywn__xdkio = HadoopFileSystem.from_uri(path)
    except Exception as tldg__slziz:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            tldg__slziz))
    okrtz__zkb = gbywn__xdkio.get_file_info([xkpx__wwyj])
    if okrtz__zkb[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not okrtz__zkb[0].size and okrtz__zkb[0].type == FileType.Directory:
        return gbywn__xdkio, True
    return gbywn__xdkio, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    nab__zasss = None
    gbywn__xdkio, ecso__tfd = hdfs_is_directory(path)
    if ecso__tfd:
        qbfx__nzhwd = urlparse(path)
        xkpx__wwyj = qbfx__nzhwd.path
        jxdf__hreb = FileSelector(xkpx__wwyj, recursive=True)
        try:
            uyeyt__hxfa = gbywn__xdkio.get_file_info(jxdf__hreb)
        except Exception as tldg__slziz:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(xkpx__wwyj, tldg__slziz))
        nab__zasss = [vlkw__mzy.base_name for vlkw__mzy in uyeyt__hxfa]
    return gbywn__xdkio, nab__zasss


def abfs_is_directory(path):
    gbywn__xdkio = get_hdfs_fs(path)
    try:
        okrtz__zkb = gbywn__xdkio.info(path)
    except OSError as yuyn__rdw:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if okrtz__zkb['size'] == 0 and okrtz__zkb['kind'].lower() == 'directory':
        return gbywn__xdkio, True
    return gbywn__xdkio, False


def abfs_list_dir_fnames(path):
    nab__zasss = None
    gbywn__xdkio, ecso__tfd = abfs_is_directory(path)
    if ecso__tfd:
        qbfx__nzhwd = urlparse(path)
        xkpx__wwyj = qbfx__nzhwd.path
        try:
            asgw__clawf = gbywn__xdkio.ls(xkpx__wwyj)
        except Exception as tldg__slziz:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(xkpx__wwyj, tldg__slziz))
        nab__zasss = [fname[fname.rindex('/') + 1:] for fname in asgw__clawf]
    return gbywn__xdkio, nab__zasss


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype):
    from urllib.parse import urlparse
    jzjho__yurp = urlparse(path)
    fname = path
    fs = None
    nwgo__jmbs = 'read_json' if ftype == 'json' else 'read_csv'
    tuu__yzyof = (
        f'pd.{nwgo__jmbs}(): there is no {ftype} file in directory: {fname}')
    fea__yjal = directory_of_files_common_filter
    if jzjho__yurp.scheme == 's3':
        kyc__nvlk = True
        fs = get_s3_fs_from_path(path)
        vah__plcf = s3_list_dir_fnames(fs, path)
        epovf__avuc = (jzjho__yurp.netloc + jzjho__yurp.path).rstrip('/')
        fname = epovf__avuc
        if vah__plcf:
            vah__plcf = [(epovf__avuc + '/' + wgkj__azrw) for wgkj__azrw in
                sorted(filter(fea__yjal, vah__plcf))]
            kbp__entb = [wgkj__azrw for wgkj__azrw in vah__plcf if int(fs.
                get_file_info(wgkj__azrw).size or 0) > 0]
            if len(kbp__entb) == 0:
                raise BodoError(tuu__yzyof)
            fname = kbp__entb[0]
        yrcy__hegv = int(fs.get_file_info(fname).size or 0)
        ipah__eqtih = fs.open_input_file(fname)
    elif jzjho__yurp.scheme == 'hdfs':
        kyc__nvlk = True
        fs, vah__plcf = hdfs_list_dir_fnames(path)
        yrcy__hegv = fs.get_file_info([jzjho__yurp.path])[0].size
        if vah__plcf:
            path = path.rstrip('/')
            vah__plcf = [(path + '/' + wgkj__azrw) for wgkj__azrw in sorted
                (filter(fea__yjal, vah__plcf))]
            kbp__entb = [wgkj__azrw for wgkj__azrw in vah__plcf if fs.
                get_file_info([urlparse(wgkj__azrw).path])[0].size > 0]
            if len(kbp__entb) == 0:
                raise BodoError(tuu__yzyof)
            fname = kbp__entb[0]
            fname = urlparse(fname).path
            yrcy__hegv = fs.get_file_info([fname])[0].size
        ipah__eqtih = fs.open_input_file(fname)
    elif jzjho__yurp.scheme in ('abfs', 'abfss'):
        kyc__nvlk = True
        fs, vah__plcf = abfs_list_dir_fnames(path)
        yrcy__hegv = fs.info(fname)['size']
        if vah__plcf:
            path = path.rstrip('/')
            vah__plcf = [(path + '/' + wgkj__azrw) for wgkj__azrw in sorted
                (filter(fea__yjal, vah__plcf))]
            kbp__entb = [wgkj__azrw for wgkj__azrw in vah__plcf if fs.info(
                wgkj__azrw)['size'] > 0]
            if len(kbp__entb) == 0:
                raise BodoError(tuu__yzyof)
            fname = kbp__entb[0]
            yrcy__hegv = fs.info(fname)['size']
            fname = urlparse(fname).path
        ipah__eqtih = fs.open(fname, 'rb')
    else:
        if jzjho__yurp.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {jzjho__yurp.scheme}. Please refer to https://docs.bodo.ai/latest/source/file_io.html'
                )
        kyc__nvlk = False
        if os.path.isdir(path):
            asgw__clawf = filter(fea__yjal, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            kbp__entb = [wgkj__azrw for wgkj__azrw in sorted(asgw__clawf) if
                os.path.getsize(wgkj__azrw) > 0]
            if len(kbp__entb) == 0:
                raise BodoError(tuu__yzyof)
            fname = kbp__entb[0]
        yrcy__hegv = os.path.getsize(fname)
        ipah__eqtih = fname
    return kyc__nvlk, ipah__eqtih, yrcy__hegv, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    ghsya__hykd = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            ljb__qtk, vcxp__ynnpc = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = ljb__qtk.region
        except Exception as tldg__slziz:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{tldg__slziz}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = ghsya__hykd.bcast(bucket_loc)
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
        dmf__bresm = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        hdonm__htca, pcc__koe = unicode_to_utf8_and_len(D)
        rzvy__vzoa = 0
        if is_parallel:
            rzvy__vzoa = bodo.libs.distributed_api.dist_exscan(pcc__koe, np
                .int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), hdonm__htca, rzvy__vzoa,
            pcc__koe, is_parallel, unicode_to_utf8(dmf__bresm))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl
