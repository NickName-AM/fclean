# fclean

fclean is a Python-based CLI tool designed to automate the creation of Clean Architecture structures for Flutter projects. It eliminates the repetitive task of manually setting up directories and boilerplate files for new features.

## Project Status: v1.0.0

The current version of the tool provides automated scaffolding for Flutter features, ensuring consistency across the codebase while enforcing a strict separation of concerns.

## Core Capabilities

### 1. Flutter Project Validation
The tool identifies if the execution context is a valid Flutter project. It checks for the existence of a `pubspec.yaml` file; if the file is missing, the tool notifies the user and terminates to prevent accidental file generation in incorrect directories.

### 2. Automated Directory Scaffolding
When a feature is generated, the tool creates a standardized hierarchy within `lib/features/`. Each feature includes the following structure:

* **Data Layer**: `datasources`, `models`, and `repository` (implementation).
* **Domain Layer**: `entities`, `repository` (interfaces), and `usecases`.
* **Presentation Layer**: `pages` and `widgets`.

### 3. Smart Boilerplate Generation
fclean generates the necessary `.dart` files with basic class definitions. This includes:
* Remote and Local Data Sources.
* Repository interfaces and their corresponding implementations.
* **Conditional Entities/Models**: If an entity name is provided (e.g., `auth:user`), the tool generates `user.dart` in the domain layer and `user_model.dart` in the data layer. If no entity name is provided, these specific files are skipped.

## Usage

Execute the script from the root of your Flutter project:

```bash
python3 fclean.py --features <feature_name>:<entity_name>