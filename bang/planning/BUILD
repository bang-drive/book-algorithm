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

lint()
