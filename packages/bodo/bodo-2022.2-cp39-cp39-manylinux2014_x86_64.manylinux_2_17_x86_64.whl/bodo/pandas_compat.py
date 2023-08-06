import hashlib
import inspect
import warnings
import pandas as pd
_check_pandas_change = False


def _set_noconvert_columns(self):
    assert self.orig_names is not None
    nvxk__sain = {nfg__oufbo: chach__bnbj for chach__bnbj, nfg__oufbo in
        enumerate(self.orig_names)}
    knwf__lrr = [nvxk__sain[nfg__oufbo] for nfg__oufbo in self.names]
    cjj__iztj = self._set_noconvert_dtype_columns(knwf__lrr, self.names)
    for owgp__alrwm in cjj__iztj:
        self._reader.set_noconvert(owgp__alrwm)


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
