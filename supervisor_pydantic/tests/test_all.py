from supervisor_pydantic import __version__


def test_all():
    assert isinstance(__version__, str)
    assert True
