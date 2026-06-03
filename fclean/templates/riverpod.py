from fclean.generators.validator import to_pascal_case


def get_riverpod_templates(feature):
    name = to_pascal_case(feature)
    return {
        f"presentation/providers/{feature}_provider.dart": (
            f"import 'package:flutter_riverpod/flutter_riverpod.dart';\n\n"
            f"class {name}State {{}}\n\n"
            f"class {name}Notifier extends StateNotifier<{name}State> {{\n"
            f"  {name}Notifier() : super({name}State());\n"
            f"}}\n\n"
            f"final {feature}Provider =\n"
            f"    StateNotifierProvider<{name}Notifier, {name}State>((ref) {{\n"
            f"  return {name}Notifier();\n"
            f"}});"
        )
    }
