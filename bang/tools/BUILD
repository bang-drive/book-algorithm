load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

exports_files([
    "flake8.sh",
])

py_binary(
    name = "topic_viewer",
    srcs = ["topic_viewer.py"],
    deps = [
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
        "//bang/common:topic",
    ],
)

py_import_test("topic_viewer")

lint()
