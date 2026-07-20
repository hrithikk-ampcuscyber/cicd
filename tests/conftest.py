import os

import pytest


@pytest.fixture
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://localhost:8000")
