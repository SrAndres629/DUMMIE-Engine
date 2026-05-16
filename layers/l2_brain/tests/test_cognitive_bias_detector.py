from cognitive_bias_detector import detect_cognitive_biases
def test_bias_detection():
    res = detect_cognitive_biases("skill synthesis")
    assert any(f["bias"] == "premature_scaling_bias" for f in res.findings)
