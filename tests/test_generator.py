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
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_event.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_state.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bloc/auth_bloc.dart").exists()


def test_create_feature_skip_existing_does_not_crash(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "bloc")
    create_feature("auth", "bloc")  # second run must not crash (validates CR-01 fix)


def test_create_feature_cubit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "cubit")
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_state.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/cubit/auth_cubit.dart").exists()


def test_create_feature_riverpod(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "riverpod")
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/providers/auth_provider.dart").exists()


def test_create_feature_getx(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", "getx")
    assert (tmp_path / "lib/features/auth/data/datasources/auth_remote_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/datasources/auth_local_datasource.dart").exists()
    assert (tmp_path / "lib/features/auth/data/repository/auth_repository_impl.dart").exists()
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/controller/auth_controller.dart").exists()
    assert (tmp_path / "lib/features/auth/presentation/bindings/auth_binding.dart").exists()


def test_create_feature_no_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth", None)
    assert (tmp_path / "lib/features/auth/domain/repository/auth_repository.dart").exists()
    assert not (tmp_path / "lib/features/auth/presentation/bloc").exists()
    assert not (tmp_path / "lib/features/auth/presentation/cubit").exists()
    assert not (tmp_path / "lib/features/auth/presentation/providers").exists()
    assert not (tmp_path / "lib/features/auth/presentation/controller").exists()


def test_create_feature_with_entity(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_feature("auth:user", "bloc")
    assert (tmp_path / "lib/features/auth/domain/entities/user.dart").exists()
    assert (tmp_path / "lib/features/auth/data/models/user_model.dart").exists()
