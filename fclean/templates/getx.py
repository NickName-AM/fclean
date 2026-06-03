from fclean.generators.validator import to_pascal_case


def get_getx_templates(feature):
    name = to_pascal_case(feature)
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
