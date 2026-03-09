import sys
import argparse
from pathlib import Path

def is_flutter_project():
    """Checks if the current directory contains a pubspec.yaml file."""
    return Path("pubspec.yaml").exists()

def get_bloc_templates(feature):
    name = feature.capitalize()
    return {
        f"presentation/bloc/{feature}_event.dart": f"abstract class {name}Event {{}}",
        f"presentation/bloc/{feature}_state.dart": (
            f"abstract class {name}State {{}}\n\n"
            f"class {name}Initial extends {name}State {{}}"
        ),
        f"presentation/bloc/{feature}_bloc.dart": (
            f"import 'package:flutter_bloc/flutter_bloc.dart';\n"
            f"import '{feature}_event.dart';\n"
            f"import '{feature}_state.dart';\n\n"
            f"class {name}Bloc extends Bloc<{name}Event, {name}State> {{\n"
            f"  {name}Bloc() : super({name}Initial()) {{\n"
            f"    on<{name}Event>((event, emit) {{\n"
            f"      // TODO: implement event handler\n"
            f"    }});\n"
            f"  }}\n}}"
        )
    }

def get_cubit_templates(feature):
    name = feature.capitalize()
    return {
        f"presentation/cubit/{feature}_state.dart": (
            f"abstract class {name}State {{}}\n\n"
            f"class {name}Initial extends {name}State {{}}"
        ),
        f"presentation/cubit/{feature}_cubit.dart": (
            f"import 'package:flutter_bloc/flutter_bloc.dart';\n"
            f"import '{feature}_state.dart';\n\n"
            f"class {name}Cubit extends Cubit<{name}State> {{\n"
            f"  {name}Cubit() : super({name}Initial());\n}}"
        )
    }

def get_riverpod_templates(feature):
    return {
        f"presentation/providers/{feature}_provider.dart": (
            f"import 'package:flutter_riverpod/flutter_riverpod.dart';\n\n"
            f"final {feature}Provider = Provider((ref) => null);"
        )
    }

def get_getx_templates(feature):
    name = feature.capitalize()
    return {
        f"presentation/controller/{feature}_controller.dart": (
            f"import 'package:get/get.dart';\n\n"
            f"class {name}Controller extends GetxController {{}}"
        ),
        f"presentation/bindings/{feature}_binding.dart": (
            f"import 'package:get/get.dart';\n"
            f"import '../controller/{feature}_controller.dart';\n\n"
            f"class {name}Binding extends Bindings {{\n"
            f"  @override\n"
            f"  void dependencies() {{\n"
            f"    Get.lazyPut(() => {name}Controller());\n"
            f"  }}\n}}"
        )
    }

def create_feature(feature_arg, state_type):
    parts = feature_arg.split(":")
    feature_name = parts[0]
    entity_name = parts[1] if len(parts) > 1 else None

    base_path = Path("lib/features") / feature_name
    
    sub_dirs = [
        "data/datasources", "data/models", "data/repository",
        "domain/repository", "domain/usecases", "domain/entities",
        "presentation/pages", "presentation/widgets"
    ]

    for sub_dir in sub_dirs:
        (base_path / sub_dir).mkdir(parents=True, exist_ok=True)

    files_to_create = {
        base_path / f"data/datasources/{feature_name}_remote_datasource.dart": 
            f"abstract class {feature_name.capitalize()}RemoteDataSource {{}}",
        base_path / f"data/datasources/{feature_name}_local_datasource.dart": 
            f"abstract class {feature_name.capitalize()}LocalDataSource {{}}",
        base_path / f"data/repository/{feature_name}_repository_impl.dart": 
            f"import '../../domain/repository/{feature_name}_repository.dart';\n\n"
            f"class {feature_name.capitalize()}RepositoryImpl implements {feature_name.capitalize()}Repository {{}}",
        base_path / f"domain/repository/{feature_name}_repository.dart": 
            f"abstract class {feature_name.capitalize()}Repository {{}}",
    }

    if entity_name:
        files_to_create[base_path / f"domain/entities/{entity_name}.dart"] = \
            f"class {entity_name.capitalize()} {{}}"
        files_to_create[base_path / f"data/models/{entity_name}_model.dart"] = \
            f"import '../../domain/entities/{entity_name}.dart';\n\n" \
            f"class {entity_name.capitalize()}Model extends {entity_name.capitalize()} {{}}"

    state_map = {
        "bloc": get_bloc_templates,
        "cubit": get_cubit_templates,
        "riverpod": get_riverpod_templates,
        "getx": get_getx_templates
    }

    if state_type in state_map:
        templates = state_map[state_type](feature_name)
        for rel_path, content in templates.items():
            files_to_create[base_path / rel_path] = content

    for path, content in files_to_create.items():
        if path.exists():
            print(f"Skipping: {path.relative_to(Path.cwd())} already exists.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    print(f"Generated feature: {feature_name} (State: {state_type if state_type else 'None'})")

def main():
    parser = argparse.ArgumentParser(description="fclean: Flutter Clean Architecture Generator")
    parser.add_argument("--features", nargs="+", required=True)
    parser.add_argument("--state", choices=["bloc", "cubit", "riverpod", "getx"], help="State management library")
    
    args = parser.parse_args()

    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.")
        sys.exit(1)

    for feature in args.features:
        create_feature(feature, args.state)

if __name__ == "__main__":
    main()