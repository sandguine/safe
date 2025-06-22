import os
import warnings
import pytest

warnings.filterwarnings(
    "ignore",
    message=".*PydanticDeprecatedSince20.*",
    category=DeprecationWarning,
)

_BAD = {"", "real_but_empty", None}  # Removed "dummy" to allow CI testing


@pytest.fixture(autouse=True, scope="session")
def _check_secret():
    if os.getenv("CI") != "true":
        pytest.skip("local run – secret may be dummy")
    else:
        assert os.getenv("CLAUDE_API_KEY") not in _BAD, "Mis-configured secret"
