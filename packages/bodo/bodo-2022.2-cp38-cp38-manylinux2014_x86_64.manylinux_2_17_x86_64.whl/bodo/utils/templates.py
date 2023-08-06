"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            wgsbb__xco = set()
            mkrt__lim = list(self.context._get_attribute_templates(self.key))
            fxkg__zrmqf = mkrt__lim.index(self) + 1
            for dlvt__prb in range(fxkg__zrmqf, len(mkrt__lim)):
                if isinstance(mkrt__lim[dlvt__prb], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    wgsbb__xco.add(mkrt__lim[dlvt__prb]._attr)
            self._attr_set = wgsbb__xco
        return attr_name in self._attr_set
