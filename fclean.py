import os
import sys
import argparse
from pathlib import Path

def is_flutter_project():
    """
    Checks if the current directory contains a pubspec.yaml file.
    """
    return Path("pubspec.yaml").exists()

def create_feature(feature_arg):
    """
    Parses 'feature[:entity]' and builds the Clean Architecture structure.
    """
    # Split the argument into feature and entity (if provided)
    parts = feature_arg.split(":")
    feature_name = parts[0]
    entity_name = parts[1] if len(parts) > 1 else None

    base_path = Path("lib/features") / feature_name
    
    # Define the standard directory structure 
    sub_dirs = [
        "data/datasources", "data/models", "data/repository",
        "domain/repository", "domain/usecases", "domain/entities",
        "presentation/pages", "presentation/widgets"
    ]

    for sub_dir in sub_dirs:
        (base_path / sub_dir).mkdir(parents=True, exist_ok=True)

    # Core boilerplate files (Always created)
    files_to_create = {
        base_path / f"data/datasources/{feature_name}_remote_datasource.dart": 
            f"abstract class {feature_name.capitalize()}RemoteDataSource {{}}",
        base_path / f"data/datasources/{feature_name}_local_datasource.dart": 
            f"abstract class {feature_name.capitalize()}LocalDataSource {{}}",
        base_path / f"data/repository/{feature_name}_repository_impl.dart": 
            f"class {feature_name.capitalize()}RepositoryImpl implements {feature_name.capitalize()}Repository {{}}",
        base_path / f"domain/repository/{feature_name}_repository.dart": 
            f"abstract class {feature_name.capitalize()}Repository {{}}",
    }

    # Conditional Entity/Model creation
    if entity_name:
        files_to_create[base_path / f"domain/entities/{entity_name}.dart"] = \
            f"class {entity_name.capitalize()} {{}}"
        files_to_create[base_path / f"data/models/{entity_name}_model.dart"] = \
            f"class {entity_name.capitalize()}Model extends {entity_name.capitalize()} {{}}"

    # Bulk writing
    for path, content in files_to_create.items():
        if not path.exists():
            path.write_text(content)
        else:
            print(f"Skipping: {path.name} already exists.")
    
    print(f"Generated feature: {feature_name}" + (f" with entity: {entity_name}" if entity_name else ""))

def main():
    parser = argparse.ArgumentParser(description="fclean: Flutter Clean Architecture Generator")
    parser.add_argument("--features", nargs="+", required=True, help="Format: feature_name[:entity_name] ")
    
    args = parser.parse_args()

    #Exit if not a flutter project
    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.")
        sys.exit(1)

    for feature in args.features:
        create_feature(feature)

if __name__ == "__main__":
    main()