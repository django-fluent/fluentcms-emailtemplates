from unittest import TestCase
from fluentcms_emailtemplates.rendering import replace_fields


class ReplaceFieldsTests(TestCase):
    """
    Test how replace fields syntax works.
    It emulates a subset of str.format()
    and supports missing fields
    """

    def test_replace_scalar(self):
        result = replace_fields('Hello {subject}!', {'subject': "TEST"}, raise_errors=True)
        self.assertEqual("Hello TEST!", result)

        result = replace_fields('Hello {aa} or {bb} and others', {'aa': 11, 'bb': 22}, raise_errors=True)
        self.assertEqual("Hello 11 or 22 and others", result)

    def test_replace_scalar_format(self):
        result = replace_fields('Hello {subject:s}!', {'subject': "TEST"}, raise_errors=True)
        self.assertEqual("Hello TEST!", result)

        result = replace_fields('Hello {aa:.02f}', {'aa': 1.5}, raise_errors=True)
        self.assertEqual("Hello 1.50", result)

    def test_replace_object(self):
        class Foo(object):
            def __init__(self):
                self.x = 2

        result = replace_fields('test {foo.x}!', {'foo': Foo()}, raise_errors=True)
        self.assertEqual("test 2!", result)
