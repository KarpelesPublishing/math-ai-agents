"""The parity checker must ignore XML serialization, never mathematical changes."""
import unittest
from audit_unified import canonical_svg


class SVGComparisonTests(unittest.TestCase):
    def test_namespace_attribute_reordering_is_equivalent(self):
        first = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="20"><text x="0.333333">gain</text></svg>'
        reordered = '<svg height="20" width="10" xmlns="http://www.w3.org/2000/svg"><text x="0.333333">gain</text></svg>'
        self.assertEqual(canonical_svg(first), canonical_svg(reordered))

    def test_coordinates_text_and_styles_are_not_rounded_or_ignored(self):
        first = '<svg xmlns="http://www.w3.org/2000/svg"><text x="0.333333" style="fill:red">gain</text></svg>'
        for modified in (first.replace('0.333333','0.333334'), first.replace('gain','loss'), first.replace('red','blue')):
            with self.subTest(modified=modified):
                self.assertNotEqual(canonical_svg(first), canonical_svg(modified))
