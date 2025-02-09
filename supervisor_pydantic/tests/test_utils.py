from helpers import get_calling_file


def test_get_calling_file_path():
    assert get_calling_file(0).endswith("supervisor_pydantic/utils.py")
    assert get_calling_file(1).endswith("helpers.py")
    assert get_calling_file(2).endswith("test_utils.py")
