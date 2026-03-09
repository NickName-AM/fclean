# fclean

fclean is a Python tool that automates the generation of Clean Architecture folders and files for Flutter projects. It removes the manual effort of creating repetitive directory structures and boilerplate code.

## Project Status

The tool currently supports automated scaffolding for core Clean Architecture layers and integrates popular state management libraries into the presentation layer.

## Features

* Validation: Ensures the script is running in a Flutter project by checking for pubspec.yaml.
* Layered Scaffolding: Automatically creates data, domain, and presentation folders.
* State Management: Supports automated boilerplate for bloc, cubit, riverpod, and getx.
* Conditional Generation: Entities and models are created only if an entity name is provided.
* Data Safety: Prevents overwriting existing files to protect manual changes.
* Automatic Imports: Correctly handles imports between models and entities, as well as repository implementations and interfaces.

## Usage

Run the tool from your project root:
```
python3 fclean.py --features feature_name:entity_name --state state_library
```


### Commands

* --features: Accepts multiple arguments in the format name:entity. The entity is optional.
* --state: Optional flag to generate state management boilerplate. Options include bloc, cubit, riverpod, and getx.

### Examples
- Single feature 
```
python3 fclean.py --features auth:user --state bloc
```

- Multiple features
```
python3 fclean.py --features auth:user place:place --state bloc
```