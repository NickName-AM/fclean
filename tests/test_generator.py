from fclean import get_bloc_templates, create_feature


def test_bloc_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content
    assert "User_profileBloc" not in all_content


def test_create_feature_creates_expected_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_bloc.dart").exists()


def test_create_feature_skip_existing_does_not_crash(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    create_feature("auth", "bloc")  # second run must not crash (validates CR-01 fix)
