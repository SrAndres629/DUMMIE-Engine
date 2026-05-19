from __future__ import annotations

from layers.l2_brain.creator_context_runtime import CreatorContextRuntime


def test_creator_profile_loading() -> None:
    ctx = CreatorContextRuntime()
    assert ctx.get_creator_name() == "Jorge Andrés Aguirre Cordero"
    assert ctx.get_preferred_name() == "Jorge"
    assert "mentor estratégico" in ctx.get_dummie_roles()
