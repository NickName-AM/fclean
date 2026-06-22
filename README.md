# fclean

A CLI tool that scaffolds Flutter Clean Architecture feature directories and Dart boilerplate so you don't have to create them by hand.

## What it generates

For each feature, fclean creates the full three-layer directory tree under `lib/features/<feature>/`:

```
lib/features/auth/
├── data/
│   ├── datasources/
│   │   ├── auth_remote_datasource.dart   # abstract class
│   │   └── auth_local_datasource.dart    # abstract class
│   ├── models/
│   │   └── user_model.dart               # extends entity (if entity provided)
│   └── repository/
│       └── auth_repository_impl.dart     # implements domain repository
├── domain/
│   ├── entities/
│   │   └── user.dart                     # plain Dart class (if entity provided)
│   ├── repository/
│   │   └── auth_repository.dart          # abstract class
│   └── usecases/
└── presentation/
    ├── pages/
    ├── widgets/
    └── bloc/ | cubit/ | ...              # state management files (if --state passed)
```

State management files generated per `--state` option:

| `--state` | Files created |
|-----------|---------------|
| `bloc` | `*_event.dart`, `*_state.dart`, `*_bloc.dart` |
| `cubit` | `*_state.dart`, `*_cubit.dart` |
| `riverpod` | `*_provider.dart`, `*_state.dart` |
| `getx` | `*_controller.dart`, `*_binding.dart` |

Existing files are never overwritten.

## Requirements

- Python 3.8+
- Must be run from the root of a Flutter project (directory containing `pubspec.yaml`)

## Installation

### From GitHub

```bash
pip install git+https://github.com/NickName-AM/fclean.git
```

### From source

```bash
git clone https://github.com/NickName-AM/fclean.git
cd fclean
pip install .
```

After installation the `fclean` command is available globally.

## Usage

```
fclean --features <feature>[:<entity>] [<feature>[:<entity>] ...] [--state <lib>]
```

| Argument | Description |
|----------|-------------|
| `--features` | One or more features in `name` or `name:entity` format. Names must be `snake_case`. |
| `--state` | Optional. One of `bloc`, `cubit`, `riverpod`, `getx`. |

### Examples

```bash
# Feature with entity and bloc state management
fclean --features auth:user --state bloc

# Feature without entity, no state layer
fclean --features profile

# Multiple features in one command
fclean --features auth:user settings:preferences --state cubit

# Riverpod with no entity
fclean --features cart --state riverpod
```

## Development

```bash
git clone https://github.com/NickName-AM/fclean.git
cd fclean
pip install -e ".[dev]"
pytest
```