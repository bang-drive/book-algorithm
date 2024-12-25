load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

py_binary(
    name = "draw_cubic",
    srcs = ["draw_cubic.py"],
    deps = [
        "//bang/planning:conf",
        requirement("absl-py"),
        requirement("opencv-python"),
        requirement("numpy"),
    ],
)

py_import_test("draw_cubic")

py_binary(
    name = "random_cubic",
    srcs = ["random_cubic.py"],
    deps = [
        "//bang/planning:conf",
        requirement("absl-py"),
        requirement("numpy"),
    ],
)

py_import_test("random_cubic")

lint()
