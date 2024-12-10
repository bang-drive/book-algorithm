load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "prediction",
    srcs = ["prediction.py"],
    deps = [
        "//bang/common:timer",
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
    ],
)

py_import_test("prediction")

lint()
