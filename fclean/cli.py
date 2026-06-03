import sys
import argparse

from fclean.generators.feature import create_feature, is_flutter_project


def main():
    parser = argparse.ArgumentParser(description="fclean: Flutter Clean Architecture Generator")
    parser.add_argument("--features", nargs="+", required=True)
    parser.add_argument("--state", choices=["bloc", "cubit", "riverpod", "getx"], help="State management library")

    args = parser.parse_args()

    if not is_flutter_project():
        print("Error: This tool must be run from the root of a Flutter project.")
        sys.exit(1)

    if args.state is None:
        print("No state management files generated. Pass --state <lib> to scaffold a state layer.")

    for feature in args.features:
        create_feature(feature, args.state)


if __name__ == "__main__":
    main()
