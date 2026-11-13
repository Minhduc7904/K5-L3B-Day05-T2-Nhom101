import pytest

from app import state


@pytest.fixture(autouse=True)
def clean_state():
    state.reset()
    yield
    state.reset()


@pytest.fixture
def s():
    """Session lúc 22:40 ngày 13/11/2026 (giờ demo mặc định): Bài 3 đang mở, TA đã hết trực."""
    return state.create_session()


@pytest.fixture
def make_session():
    return state.create_session
