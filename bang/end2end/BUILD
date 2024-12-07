load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "common",
    srcs = ["common.py"],
)

py_binary(
    name = "data_recorder",
    srcs = ["data_recorder.py"],
    deps = [
        ":common",
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("data_recorder")

py_binary(
    name = "data_sampler",
    srcs = ["data_sampler.py"],
    deps = [
        ":common",
        "//bang/common:topic",
        requirement("absl-py"),
    ],
)

py_import_test("data_sampler")

py_binary(
    name = "train",
    srcs = ["train.py"],
    deps = [
        ":common",
        requirement("absl-py"),
        requirement("torch"),
        requirement("torchvision"),
    ],
)

py_import_test("train")

py_binary(
    name = "run",
    srcs = ["run.py"],
    data = ["model.pt"],
    deps = [
        "//bang/common:timer",
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("pillow"),
        requirement("torch"),
        requirement("torchvision"),
    ],
)

py_import_test("run")

lint()
