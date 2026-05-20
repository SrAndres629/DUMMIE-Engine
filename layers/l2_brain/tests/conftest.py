import sys
from pathlib import Path
from unittest import mock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
L2_ROOT = REPO_ROOT / "layers" / "l2_brain"

for candidate in (REPO_ROOT, L2_ROOT):
    path = str(candidate)
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture
def mocker(request):
    class _PatchProxy:
        def __call__(self, target, *args, **kwargs):
            patched = mock.patch(target, *args, **kwargs)
            obj = patched.start()
            request.addfinalizer(patched.stop)
            return obj

        def object(self, target, attribute, *args, **kwargs):
            patched = mock.patch.object(target, attribute, *args, **kwargs)
            obj = patched.start()
            request.addfinalizer(patched.stop)
            return obj

    class _Mocker:
        Mock = mock.Mock
        MagicMock = mock.MagicMock
        AsyncMock = mock.AsyncMock

    instance = _Mocker()
    instance.patch = _PatchProxy()
    return instance
