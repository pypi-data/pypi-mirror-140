import hashlib
import inspect
import warnings
import pandas as pd
_check_pandas_change = False


def _set_noconvert_columns(self):
    assert self.orig_names is not None
    dwje__juy = {aejlq__tvoh: dyaj__bbr for dyaj__bbr, aejlq__tvoh in
        enumerate(self.orig_names)}
    teg__mcy = [dwje__juy[aejlq__tvoh] for aejlq__tvoh in self.names]
    vat__yrr = self._set_noconvert_dtype_columns(teg__mcy, self.names)
    for khwfm__amd in vat__yrr:
        self._reader.set_noconvert(khwfm__amd)


if _check_pandas_change:
    lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.CParserWrapper
        ._set_noconvert_columns)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3':
        warnings.warn(
            'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
            )
pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns = (
    _set_noconvert_columns)
