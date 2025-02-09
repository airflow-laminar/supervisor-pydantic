from supervisor_pydantic.utils import _get_calling_file


def get_calling_file(offset=2):
    return _get_calling_file(offset)
