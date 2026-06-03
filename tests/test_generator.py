import sys
sys.path.insert(0, ".")
from fclean import get_bloc_templates  # NOTE: import path changes after Phase 2 package restructure


def test_bloc_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content
    assert "User_profileBloc" not in all_content
