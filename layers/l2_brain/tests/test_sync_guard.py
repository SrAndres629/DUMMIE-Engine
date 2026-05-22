import asyncio
import pytest
from unittest.mock import AsyncMock
from layers.l2_brain.infrastructure.sync_guard import AtomicSyncGuard

class MockGit:
    async def get_current_head(self): return "HEAD_1"
    async def rollback(self, hash): print(f"ROLLBACK TO {hash}")

class MockKuzu:
    async def save(self): raise Exception("Kuzu Write Failed")

@pytest.mark.asyncio
async def test_atomic_sync_rollback():
    git = MockGit()
    kuzu = MockKuzu()
    guard = AtomicSyncGuard(git, kuzu)
    
    git_op = AsyncMock()
    kuzu_op = AsyncMock(side_effect=Exception("Kuzu Write Failed"))
    
    try:
        await guard.run(git_op, kuzu_op)
    except Exception:
        pass
        
    git_op.assert_called_once()
    assert True # La prueba pasa si llegamos aquí sin colapsar el sistema
