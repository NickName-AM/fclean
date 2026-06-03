import sys
from pathlib import Path

from fclean.generators.validator import validate_name, to_pascal_case
from fclean.templates.bloc import get_bloc_templates
from fclean.templates.cubit import get_cubit_templates
from fclean.templates.riverpod import get_riverpod_templates
from fclean.templates.getx import get_getx_templates


def is_flutter_project():
    """Checks if the current directory contains a pubspec.yaml file."""
    return Path("pubspec.yaml").exists()


def create_feature(feature_arg, state_type, dry_run=False):
    parts = feature_arg.split(":")
    if len(parts) > 2:
        print(
            f"Error: Invalid feature argument '{feature_arg}'. "
            "Expected format: <feature> or <feature>:<entity>.",
            file=sys.stderr,
        )
        sys.exit(1)
    feature_name = parts[0]
    entity_name = parts[1] if len(parts) == 2 else None

    validate_name(feature_name)
    if entity_name is not None:
        validate_name(entity_name)

    base_path = Path("lib/features") / feature_name

    sub_dirs = [
        "data/datasources", "data/models", "data/repository",
        "domain/repository", "domain/usecases", "domain/entities",
        "presentation/pages", "presentation/widgets"
    ]

    if not dry_run:
        for sub_dir in sub_dirs:
            (base_path / sub_dir).mkdir(parents=True, exist_ok=True)

    files_to_create = {
        base_path / f"data/datasources/{feature_name}_remote_datasource.dart":
            f"abstract class {to_pascal_case(feature_name)}RemoteDataSource {{}}",
        base_path / f"data/datasources/{feature_name}_local_datasource.dart":
            f"abstract class {to_pascal_case(feature_name)}LocalDataSource {{}}",
        base_path / f"data/repository/{feature_name}_repository_impl.dart":
            f"import '../../domain/repository/{feature_name}_repository.dart';\n\n"
            f"class {to_pascal_case(feature_name)}RepositoryImpl implements {to_pascal_case(feature_name)}Repository {{}}",
        base_path / f"domain/repository/{feature_name}_repository.dart":
            f"abstract class {to_pascal_case(feature_name)}Repository {{}}",
    }

    if entity_name:
        files_to_create[base_path / f"domain/entities/{entity_name}.dart"] = \
            f"class {to_pascal_case(entity_name)} {{}}"
        files_to_create[base_path / f"data/models/{entity_name}_model.dart"] = \
            f"import '../../domain/entities/{entity_name}.dart';\n\n" \
            f"class {to_pascal_case(entity_name)}Model extends {to_pascal_case(entity_name)} {{}}"

    state_map = {
        "bloc": get_bloc_templates,
        "cubit": get_cubit_templates,
        "riverpod": get_riverpod_templates,
        "getx": get_getx_templates
    }

    if state_type is not None and state_type not in state_map:
        print(
            f"Error: Unknown state type '{state_type}'. "
            f"Valid choices: {', '.join(sorted(state_map))}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if state_type in state_map:
        templates = state_map[state_type](feature_name)
        for rel_path, content in templates.items():
            files_to_create[base_path / rel_path] = content

    for path, content in files_to_create.items():
        if dry_run:
            print(path)
            continue
        if path.exists():
            print(f"Skipping: {path} already exists.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"Generated feature: {feature_name} (State: {state_type if state_type else 'None'})")
