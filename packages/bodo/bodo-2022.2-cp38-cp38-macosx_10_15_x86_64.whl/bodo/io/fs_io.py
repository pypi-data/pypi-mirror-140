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
            bbzn__pbt = self.fs.open_input_file(path)
        except:
            bbzn__pbt = self.fs.open_input_stream(path)
    elif mode == 'wb':
        bbzn__pbt = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, bbzn__pbt, path, mode, block_size, **kwargs)


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
    vyana__lgci = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    uhtx__bukxy = False
    gytno__spvck = get_proxy_uri_from_env_vars()
    if storage_options:
        uhtx__bukxy = storage_options.get('anon', False)
    return S3FileSystem(anonymous=uhtx__bukxy, region=region,
        endpoint_override=vyana__lgci, proxy_options=gytno__spvck)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    vyana__lgci = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    uhtx__bukxy = False
    gytno__spvck = get_proxy_uri_from_env_vars()
    if storage_options:
        uhtx__bukxy = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=vyana__lgci,
        anonymous=uhtx__bukxy, proxy_options=gytno__spvck)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    lxwnb__ssm = urlparse(path)
    if lxwnb__ssm.scheme in ('abfs', 'abfss'):
        pha__bpi = path
        if lxwnb__ssm.port is None:
            ykky__xnb = 0
        else:
            ykky__xnb = lxwnb__ssm.port
        hfv__iebhx = None
    else:
        pha__bpi = lxwnb__ssm.hostname
        ykky__xnb = lxwnb__ssm.port
        hfv__iebhx = lxwnb__ssm.username
    try:
        fs = HdFS(host=pha__bpi, port=ykky__xnb, user=hfv__iebhx)
    except Exception as ntz__xeiw:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            ntz__xeiw))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        ozjs__ibcqb = fs.isdir(path)
    except gcsfs.utils.HttpError as ntz__xeiw:
        raise BodoError(
            f'{ntz__xeiw}. Make sure your google cloud credentials are set!')
    return ozjs__ibcqb


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [aon__dfnrp.split('/')[-1] for aon__dfnrp in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        lxwnb__ssm = urlparse(path)
        xnay__tpt = (lxwnb__ssm.netloc + lxwnb__ssm.path).rstrip('/')
        vtufg__une = fs.get_file_info(xnay__tpt)
        if vtufg__une.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not vtufg__une.size and vtufg__une.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as ntz__xeiw:
        raise
    except BodoError as fltc__vzf:
        raise
    except Exception as ntz__xeiw:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ntz__xeiw).__name__}: {str(ntz__xeiw)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    dkvhi__fyg = None
    try:
        if s3_is_directory(fs, path):
            lxwnb__ssm = urlparse(path)
            xnay__tpt = (lxwnb__ssm.netloc + lxwnb__ssm.path).rstrip('/')
            tgay__qhez = pa_fs.FileSelector(xnay__tpt, recursive=False)
            fxfk__cbne = fs.get_file_info(tgay__qhez)
            if fxfk__cbne and fxfk__cbne[0].path in [xnay__tpt, f'{xnay__tpt}/'
                ] and int(fxfk__cbne[0].size or 0) == 0:
                fxfk__cbne = fxfk__cbne[1:]
            dkvhi__fyg = [qsmk__borg.base_name for qsmk__borg in fxfk__cbne]
    except BodoError as fltc__vzf:
        raise
    except Exception as ntz__xeiw:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ntz__xeiw).__name__}: {str(ntz__xeiw)}
{bodo_error_msg}"""
            )
    return dkvhi__fyg


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    lxwnb__ssm = urlparse(path)
    qdml__esd = lxwnb__ssm.path
    try:
        ookmq__urb = HadoopFileSystem.from_uri(path)
    except Exception as ntz__xeiw:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            ntz__xeiw))
    adr__mudqz = ookmq__urb.get_file_info([qdml__esd])
    if adr__mudqz[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not adr__mudqz[0].size and adr__mudqz[0].type == FileType.Directory:
        return ookmq__urb, True
    return ookmq__urb, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    dkvhi__fyg = None
    ookmq__urb, ozjs__ibcqb = hdfs_is_directory(path)
    if ozjs__ibcqb:
        lxwnb__ssm = urlparse(path)
        qdml__esd = lxwnb__ssm.path
        tgay__qhez = FileSelector(qdml__esd, recursive=True)
        try:
            fxfk__cbne = ookmq__urb.get_file_info(tgay__qhez)
        except Exception as ntz__xeiw:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qdml__esd, ntz__xeiw))
        dkvhi__fyg = [qsmk__borg.base_name for qsmk__borg in fxfk__cbne]
    return ookmq__urb, dkvhi__fyg


def abfs_is_directory(path):
    ookmq__urb = get_hdfs_fs(path)
    try:
        adr__mudqz = ookmq__urb.info(path)
    except OSError as fltc__vzf:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if adr__mudqz['size'] == 0 and adr__mudqz['kind'].lower() == 'directory':
        return ookmq__urb, True
    return ookmq__urb, False


def abfs_list_dir_fnames(path):
    dkvhi__fyg = None
    ookmq__urb, ozjs__ibcqb = abfs_is_directory(path)
    if ozjs__ibcqb:
        lxwnb__ssm = urlparse(path)
        qdml__esd = lxwnb__ssm.path
        try:
            ijxev__brjxw = ookmq__urb.ls(qdml__esd)
        except Exception as ntz__xeiw:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(qdml__esd, ntz__xeiw))
        dkvhi__fyg = [fname[fname.rindex('/') + 1:] for fname in ijxev__brjxw]
    return ookmq__urb, dkvhi__fyg


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype):
    from urllib.parse import urlparse
    lbv__cabjh = urlparse(path)
    fname = path
    fs = None
    urx__hthg = 'read_json' if ftype == 'json' else 'read_csv'
    unvw__opsow = (
        f'pd.{urx__hthg}(): there is no {ftype} file in directory: {fname}')
    flufp__gahiq = directory_of_files_common_filter
    if lbv__cabjh.scheme == 's3':
        wlpva__kbw = True
        fs = get_s3_fs_from_path(path)
        tri__rvtw = s3_list_dir_fnames(fs, path)
        xnay__tpt = (lbv__cabjh.netloc + lbv__cabjh.path).rstrip('/')
        fname = xnay__tpt
        if tri__rvtw:
            tri__rvtw = [(xnay__tpt + '/' + aon__dfnrp) for aon__dfnrp in
                sorted(filter(flufp__gahiq, tri__rvtw))]
            pwud__lxa = [aon__dfnrp for aon__dfnrp in tri__rvtw if int(fs.
                get_file_info(aon__dfnrp).size or 0) > 0]
            if len(pwud__lxa) == 0:
                raise BodoError(unvw__opsow)
            fname = pwud__lxa[0]
        tlhjs__xzeso = int(fs.get_file_info(fname).size or 0)
        ordh__pkyp = fs.open_input_file(fname)
    elif lbv__cabjh.scheme == 'hdfs':
        wlpva__kbw = True
        fs, tri__rvtw = hdfs_list_dir_fnames(path)
        tlhjs__xzeso = fs.get_file_info([lbv__cabjh.path])[0].size
        if tri__rvtw:
            path = path.rstrip('/')
            tri__rvtw = [(path + '/' + aon__dfnrp) for aon__dfnrp in sorted
                (filter(flufp__gahiq, tri__rvtw))]
            pwud__lxa = [aon__dfnrp for aon__dfnrp in tri__rvtw if fs.
                get_file_info([urlparse(aon__dfnrp).path])[0].size > 0]
            if len(pwud__lxa) == 0:
                raise BodoError(unvw__opsow)
            fname = pwud__lxa[0]
            fname = urlparse(fname).path
            tlhjs__xzeso = fs.get_file_info([fname])[0].size
        ordh__pkyp = fs.open_input_file(fname)
    elif lbv__cabjh.scheme in ('abfs', 'abfss'):
        wlpva__kbw = True
        fs, tri__rvtw = abfs_list_dir_fnames(path)
        tlhjs__xzeso = fs.info(fname)['size']
        if tri__rvtw:
            path = path.rstrip('/')
            tri__rvtw = [(path + '/' + aon__dfnrp) for aon__dfnrp in sorted
                (filter(flufp__gahiq, tri__rvtw))]
            pwud__lxa = [aon__dfnrp for aon__dfnrp in tri__rvtw if fs.info(
                aon__dfnrp)['size'] > 0]
            if len(pwud__lxa) == 0:
                raise BodoError(unvw__opsow)
            fname = pwud__lxa[0]
            tlhjs__xzeso = fs.info(fname)['size']
            fname = urlparse(fname).path
        ordh__pkyp = fs.open(fname, 'rb')
    else:
        if lbv__cabjh.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {lbv__cabjh.scheme}. Please refer to https://docs.bodo.ai/latest/source/file_io.html'
                )
        wlpva__kbw = False
        if os.path.isdir(path):
            ijxev__brjxw = filter(flufp__gahiq, glob.glob(os.path.join(os.
                path.abspath(path), '*')))
            pwud__lxa = [aon__dfnrp for aon__dfnrp in sorted(ijxev__brjxw) if
                os.path.getsize(aon__dfnrp) > 0]
            if len(pwud__lxa) == 0:
                raise BodoError(unvw__opsow)
            fname = pwud__lxa[0]
        tlhjs__xzeso = os.path.getsize(fname)
        ordh__pkyp = fname
    return wlpva__kbw, ordh__pkyp, tlhjs__xzeso, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    fpbs__yolb = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            wsp__ezjqv, yaa__gbuua = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = wsp__ezjqv.region
        except Exception as ntz__xeiw:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{ntz__xeiw}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = fpbs__yolb.bcast(bucket_loc)
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
        iun__hzthl = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        acw__ivlnp, wpdde__qjj = unicode_to_utf8_and_len(D)
        kzf__rre = 0
        if is_parallel:
            kzf__rre = bodo.libs.distributed_api.dist_exscan(wpdde__qjj, np
                .int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), acw__ivlnp, kzf__rre,
            wpdde__qjj, is_parallel, unicode_to_utf8(iun__hzthl))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl
