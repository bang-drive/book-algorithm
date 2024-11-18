load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "perception",
    srcs = ["perception.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
        requirement("ultralytics"),
    ],
)

py_import_test("perception")

lint()
