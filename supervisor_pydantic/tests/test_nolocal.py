import sys


def test_no_local_import_supervisor():
    import supervisor_pydantic  # noqa: F401

    assert "supervisor" not in sys.modules
