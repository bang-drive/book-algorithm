load("@pip//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "dragon_planner",
    srcs = ["dragon_planner.py"],
    deps = [
        requirement("absl-py"),
        "//bang/common:topic",
    ],
)
