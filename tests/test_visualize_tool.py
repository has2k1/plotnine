import importlib.util
import sys
from pathlib import Path
from textwrap import dedent

_path = Path(__file__).parent.parent / "tools" / "_testcode.py"
_spec = importlib.util.spec_from_file_location("_testcode", _path)
assert _spec is not None and _spec.loader is not None
_testcode = importlib.util.module_from_spec(_spec)
# dataclass field-annotation resolution looks the module up by name
sys.modules["_testcode"] = _testcode
_spec.loader.exec_module(_testcode)

extract_test_code = _testcode.extract_test_code
get_test_code = _testcode.get_test_code


def test_module_level_function():
    source = dedent(
        """
        import pandas as pd

        def test_params():
            p = ggplot(data, aes("x"))
            assert p == "params"
        """
    )
    snippet = extract_test_code(source, "params")
    assert snippet is not None
    assert snippet.source == (
        "def test_params():\n"
        '    p = ggplot(data, aes("x"))\n'
        '    assert p == "params"'
    )
    assert snippet.lineno == 4


def test_method_includes_class_setup():
    source = dedent(
        """
        class TestAesthetics:
            p = ggplot(data, aes("x")) + geom_boxplot()

            def test_aesthetics(self):
                assert self.p == "aesthetics"

            def test_other(self):
                assert self.p + coord_flip() == "other"
        """
    )
    snippet = extract_test_code(source, "aesthetics")
    assert snippet is not None
    assert snippet.source == (
        "class TestAesthetics:\n"
        '    p = ggplot(data, aes("x")) + geom_boxplot()\n'
        "\n"
        "    def test_aesthetics(self):\n"
        '        assert self.p == "aesthetics"'
    )


def test_module_setup_for_referenced_names():
    source = dedent(
        """
        import pandas as pd

        m = 10
        data = pd.DataFrame({"x": range(m)})
        unused = 42

        def test_weight():
            p = ggplot(data, aes("x"))
            assert p == "weight"
        """
    )
    snippet = extract_test_code(source, "weight")
    assert snippet is not None
    chunks = snippet.source.split("\n\n")
    assert chunks[0] == 'data = pd.DataFrame({"x": range(m)})'
    assert chunks[1].startswith("def test_weight():")
    # `m` is only read by data's assignment, not by the function;
    # setup gathering is one level deep. `unused` is not referenced.
    assert "m = 10" not in snippet.source
    assert "unused" not in snippet.source
    assert "import pandas" not in snippet.source


def test_bare_constant_fallback_match():
    source = dedent(
        """
        def test_listed():
            names = ["several", "images"]
            for name in names:
                assert make_plot(name) == name
        """
    )
    snippet = extract_test_code(source, "images")
    assert snippet is not None
    assert snippet.source.startswith("def test_listed():")


def test_compare_match_preferred_over_constant():
    source = dedent(
        """
        def test_mentions():
            do_setup("params")

        def test_params():
            assert p == "params"
        """
    )
    snippet = extract_test_code(source, "params")
    assert snippet is not None
    assert snippet.source.startswith("def test_params():")


def test_no_match_returns_none():
    assert extract_test_code("def test_a():\n    pass", "nope") is None


def test_unparseable_source_returns_none():
    assert extract_test_code("def broken(:\n", "params") is None


def test_missing_file_returns_none(tmp_path):
    assert get_test_code(tmp_path / "no_such.py", "params") is None


def test_get_test_code_reads_file(tmp_path):
    test_file = tmp_path / "test_x.py"
    test_file.write_text(
        'def test_a():\n    assert p == "a"\n', encoding="utf-8"
    )
    snippet = get_test_code(test_file, "a")
    assert snippet is not None
    assert snippet.lineno == 1
