load("@pip//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "topic_viewer",
    srcs = ["topic_viewer.py"],
    deps = [
        requirement("absl-py"),
        "//bang/common:topic",
    ],
)
