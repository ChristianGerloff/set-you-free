import pytest


@pytest.fixture(autouse=False)
def doi(request) -> str:
    return request.param if hasattr(request, "param") else "10.1590/0102-311x00133115"
