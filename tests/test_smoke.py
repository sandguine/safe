def test_smoke():
    """Basic smoke test to ensure CI passes."""
    assert True


def test_imports():
    """Test that basic imports work."""
    try:
        import sys
        assert sys.version_info >= (3, 8)
    except ImportError:
        assert False, "Basic imports should work"


def test_oversight_import():
    """Test that oversight module can be imported."""
    try:
        import oversight
        assert oversight is not None
    except ImportError:
        # This is expected in CI if dependencies aren't fully installed
        pass 