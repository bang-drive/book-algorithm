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

py_binary(
    name = "draw_trapezoid",
    srcs = ["draw_trapezoid.py"],
    deps = [
        requirement("absl-py"),
        requirement("opencv-python"),
    ],
)

py_import_test("draw_trapezoid")

py_binary(
    name = "warp_birds_eye_view",
    srcs = ["warp_birds_eye_view.py"],
    deps = [
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("warp_birds_eye_view")

py_binary(
    name = "yolo_viewer",
    srcs = ["yolo_viewer.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("lapx"),
        requirement("numpy"),
        requirement("opencv-python"),
        requirement("ultralytics"),
    ],
)

py_import_test("yolo_viewer")

py_binary(
    name = "bev_viewer",
    srcs = ["bev_viewer.py"],
    deps = [
        "//bang/common:topic",
        requirement("absl-py"),
        requirement("numpy"),
        requirement("opencv-python"),
    ],
)

py_import_test("bev_viewer")

lint()
