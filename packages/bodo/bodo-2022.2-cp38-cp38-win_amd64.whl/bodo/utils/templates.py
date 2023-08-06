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
            psabf__whw = set()
            tos__nvj = list(self.context._get_attribute_templates(self.key))
            nut__bph = tos__nvj.index(self) + 1
            for mch__uuig in range(nut__bph, len(tos__nvj)):
                if isinstance(tos__nvj[mch__uuig], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    psabf__whw.add(tos__nvj[mch__uuig]._attr)
            self._attr_set = psabf__whw
        return attr_name in self._attr_set
