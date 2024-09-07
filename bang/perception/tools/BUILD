load("@pip//:requirements.bzl", "requirement")
load("//bang/tools:lint.bzl", "lint", "py_import_test")

py_binary(
    name = "camera_saver",
    srcs = ["camera_saver.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("getkey"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("camera_saver")

lint()
