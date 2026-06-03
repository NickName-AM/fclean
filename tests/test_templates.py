import pytest
from fclean import (
    get_bloc_templates,
    get_cubit_templates,
    get_riverpod_templates,
    get_getx_templates,
)


def test_riverpod_typed():
    templates = get_riverpod_templates("user_profile")
    content = list(templates.values())[0]
    assert "StateNotifierProvider<" in content
    assert "UserProfileNotifier" in content
    assert "UserProfileState" in content
    assert "Provider((ref) => null)" not in content


def test_bloc_template_class_names():
    templates = get_bloc_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileBloc" in all_content
    assert "UserProfileEvent" in all_content
    assert "UserProfileState" in all_content


def test_bloc_template_bloc_file_content():
    templates = get_bloc_templates("auth")
    content = templates["presentation/bloc/auth_bloc.dart"]
    assert "import 'package:flutter_bloc/flutter_bloc.dart';" in content
    assert "class AuthBloc extends Bloc<AuthEvent, AuthState>" in content


def test_cubit_template_class_names():
    templates = get_cubit_templates("user_profile")
    all_content = " ".join(templates.values())
    assert "UserProfileCubit" in all_content
    assert "UserProfileState" in all_content


def test_cubit_template_keys():
    templates = get_cubit_templates("auth")
    assert "presentation/cubit/auth_cubit.dart" in templates
    assert "presentation/cubit/auth_state.dart" in templates


def test_getx_template_keys():
    templates = get_getx_templates("auth")
    assert "presentation/controller/auth_controller.dart" in templates
    assert "presentation/bindings/auth_binding.dart" in templates


@pytest.mark.skip(reason="Phase 5: provider/ChangeNotifier template pending STATE-01")
def test_provider_template_class_names():
    from fclean import get_provider_templates
    templates = get_provider_templates("auth")
    all_content = " ".join(templates.values())
    assert "AuthChangeNotifier" in all_content
