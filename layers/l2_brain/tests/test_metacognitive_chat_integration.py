from layers.l2_brain.mission.dummie_chat_cli import DummieChatCli


def test_chat_metacognition():
    cli = DummieChatCli()
    resp = cli.handle_query("what should I do next?")
    assert hasattr(resp, "metacognitive_loop")
    assert resp.metacognitive_loop["decision"] == "PASS"
