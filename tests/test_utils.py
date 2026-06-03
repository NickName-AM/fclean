import sys
sys.path.insert(0, ".")
from fclean import to_pascal_case  # NOTE: import path changes after Phase 2 package restructure


def test_to_pascal_case_single_word():
    assert to_pascal_case("auth") == "Auth"


def test_to_pascal_case_snake():
    assert to_pascal_case("user_profile") == "UserProfile"


def test_to_pascal_case_with_digit():
    assert to_pascal_case("my_feature2") == "MyFeature2"
