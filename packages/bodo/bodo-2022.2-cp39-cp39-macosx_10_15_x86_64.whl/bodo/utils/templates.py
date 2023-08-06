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
            pmp__nuzj = set()
            eqp__iyfn = list(self.context._get_attribute_templates(self.key))
            furf__mzxr = eqp__iyfn.index(self) + 1
            for ctq__xxr in range(furf__mzxr, len(eqp__iyfn)):
                if isinstance(eqp__iyfn[ctq__xxr], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    pmp__nuzj.add(eqp__iyfn[ctq__xxr]._attr)
            self._attr_set = pmp__nuzj
        return attr_name in self._attr_set
