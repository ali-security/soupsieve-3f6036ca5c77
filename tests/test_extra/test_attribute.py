"""Test attribute selectors."""
from .. import util
import soupsieve as sv
import time


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    # Generous upper bound (seconds) for compiling a malformed selector.
    # The vulnerable pattern backtracks essentially forever, while the fixed pattern
    # bails out in well under a millisecond, so slow runners cannot flake this.
    # `signal.alarm` is not used as it is unavailable on Windows.
    REDOS_TIMEOUT = 5.0

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_no_hang(self, selector):
        """Assert the selector fails with a syntax error promptly instead of backtracking forever."""

        start = time.perf_counter()
        with self.assertRaises(sv.SelectorSyntaxError):
            sv.compile(selector)
        elapsed = time.perf_counter() - start
        self.assertTrue(
            elapsed < self.REDOS_TIMEOUT,
            'Compiling a malformed selector took {:.3f}s, expected less than {:.3f}s'.format(
                elapsed, self.REDOS_TIMEOUT
            )
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_hang('[a="' + ('x' * 300))

    def test_bad_attribute_unclosed_single_quote(self):
        """Test bad attribute with a never closed single quote fails for a syntax error."""

        self.assert_syntax_error_no_hang("[a='" + ('x' * 300))

    def test_bad_contains_unclosed_quote(self):
        """Test a never closed quoted value in `:-soup-contains()` fails for a syntax error."""

        self.assert_syntax_error_no_hang(':-soup-contains("' + ('x' * 300))

    def test_bad_lang_unclosed_quote(self):
        """Test a never closed quoted value in `:lang()` fails for a syntax error."""

        self.assert_syntax_error_no_hang(':lang("' + ('x' * 300))

    def test_bad_attribute_unclosed_bracket(self):
        """Test bad attribute with an unquoted value and no closing bracket fails for a syntax error."""

        self.assert_syntax_error_no_hang('[a=' + ('x' * 300))

    def test_bad_contains_unclosed_paren(self):
        """Test an unquoted value in a never closed `:-soup-contains()` fails for a syntax error."""

        self.assert_syntax_error_no_hang(':-soup-contains(' + ('x' * 300))

    def test_bad_lang_unclosed_paren(self):
        """Test an unquoted value in a never closed `:lang()` fails for a syntax error."""

        self.assert_syntax_error_no_hang(':lang(' + ('x' * 300))

    def test_long_attribute_value_still_matches(self):
        """Test that a well formed, long quoted attribute value still compiles and matches."""

        value = 'x' * 300
        self.assert_selector(
            '<div id="0" data-value="{}"></div>'.format(value),
            '[data-value="{}"]'.format(value),
            ["0"],
            flags=util.HTML
        )

    def test_long_unquoted_attribute_value_still_matches(self):
        """Test that a well formed, long unquoted attribute value still compiles and matches."""

        value = 'x' * 300
        self.assert_selector(
            '<div id="0" data-value="{}"></div>'.format(value),
            '[data-value={}]'.format(value),
            ["0"],
            flags=util.HTML
        )

    def test_identifier_attribute_value_parts_still_match(self):
        """Test that unquoted values with digits, dashes, and escapes still compile and match."""

        self.assert_selector(
            '<div id="0" data-value="de--DE-1996-*"></div>',
            r'[data-value=de--DE-1996-\*]',
            ["0"],
            flags=util.HTML
        )
