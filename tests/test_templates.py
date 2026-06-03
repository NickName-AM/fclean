from fclean import get_riverpod_templates


def test_riverpod_typed():
    templates = get_riverpod_templates("user_profile")
    content = list(templates.values())[0]
    assert "StateNotifierProvider<" in content
    assert "UserProfileNotifier" in content
    assert "UserProfileState" in content
    assert "Provider((ref) => null)" not in content
