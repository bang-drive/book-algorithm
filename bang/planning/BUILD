load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "dragon_planner",
    srcs = ["dragon_planner.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
    ],
)

py_import_test("dragon_planner")

py_binary(
    name = "planning",
    srcs = ["planning.py"],
    deps = [
        ":quintic_planner",
        "//bang/common:timer",
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("opencv-python"),
        requirement("numpy"),
    ],
)

py_import_test("planning")

py_library(
    name = "quintic_planner",
    srcs = ["quintic_planner.py"],
    deps = [
        requirement("numpy"),
    ],
)

lint()
