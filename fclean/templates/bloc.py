from fclean.generators.validator import to_pascal_case


def get_bloc_templates(feature):
    name = to_pascal_case(feature)
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
