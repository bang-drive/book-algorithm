load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "control",
    srcs = ["control.py"],
    deps = [
        "//bang/common:timer",
        "//bang/common:topic",
        requirement("absl-py"),
    ],
)

py_import_test("control")

lint()
