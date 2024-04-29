load("@pip//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

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
