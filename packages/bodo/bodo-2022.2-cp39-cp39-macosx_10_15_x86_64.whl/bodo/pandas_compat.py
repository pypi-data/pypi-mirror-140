import hashlib
import inspect
import warnings
import pandas as pd
_check_pandas_change = False


def _set_noconvert_columns(self):
    assert self.orig_names is not None
    tuv__yiuv = {rts__kudw: oocws__djbex for oocws__djbex, rts__kudw in
        enumerate(self.orig_names)}
    sbydh__jfcw = [tuv__yiuv[rts__kudw] for rts__kudw in self.names]
    ikn__dvpwf = self._set_noconvert_dtype_columns(sbydh__jfcw, self.names)
    for ercjx__xuggo in ikn__dvpwf:
        self._reader.set_noconvert(ercjx__xuggo)


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
