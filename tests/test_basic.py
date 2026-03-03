"""Basic tests to verify pytest configuration is working."""

def test_import():
    """Test that the package can be imported."""
    from pyshort import __version__
    assert isinstance(__version__, str)


def test_version_format():
    """Test that version follows semantic versioning."""
    from pyshort import __version__
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert parts[0].isdigit()