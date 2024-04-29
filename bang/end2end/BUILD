load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "data_recorder",
    srcs = ["data_recorder.py"],
    deps = [
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
        "//bang/common:topic",
    ],
)

py_import_test("data_recorder")

lint()
