load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "topic",
    srcs = ["topic.py"],
    deps = [
        requirement("redis"),
    ],
)

lint()
