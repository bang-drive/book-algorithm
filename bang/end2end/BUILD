load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "data_recorder",
    srcs = ["data_recorder.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("data_recorder")

py_binary(
    name = "balanced_sampling",
    srcs = ["balanced_sampling.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("balanced_sampling")

py_binary(
    name = "train",
    srcs = ["train.py"],
    deps = [
        requirement("absl-py"),
	requirement("torch"),
	requirement("torchvision"),
    ],
)

py_import_test("train")

lint()
