from fclean.generators.validator import to_pascal_case


def get_cubit_templates(feature):
    name = to_pascal_case(feature)
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
