from src.deriver.prompts import minimal_deriver_prompt


def test_minimal_deriver_prompt_includes_social_brain_guidance():
    prompt = minimal_deriver_prompt(
        peer_id="Alice", messages="Alice: Bob is my manager"
    )

    assert "[SOCIAL-BRAIN]" in prompt
    assert "social_category" in prompt
    assert "Preserve perspective" in prompt
    assert "Alice believes/reported/perceived" in prompt
