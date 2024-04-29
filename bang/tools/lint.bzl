def _get_labels_and_files_by_extensions(labels, extensions):
    result_labels = []
    result_files = []
    for label in labels:
        for ext in extensions:
            if label.endswith(ext):
                result_labels.append(label)
                result_files.append("$(location %s)" % label)
    return (result_labels, result_files)

def _add_py_rules(labels, name):
    py_labels, files = _get_labels_and_files_by_extensions(labels, [".py"])
    if len(files) == 0:
        return

    native.sh_test(
        name = name + "_flake8",
        srcs = ["//bang/tools:flake8.sh"],
        data = py_labels + ["//:tox.ini"],
        args = files,
        size = "small",
        tags = ["lint"],
    )

def lint():
    for rule in native.existing_rules().values():
        if "NOLINT" in rule["tags"]:
            continue

        # Extract the list of source code labels and convert to filenames.
        labels = list(rule.get("srcs", ())) + list(rule.get("hdrs", ()))
        _add_py_rules(labels, rule["name"])

py_import_test_template = """import unittest

class ImportTest(unittest.TestCase):
    def test_import(self):
        try:
            import PLACEHOLDER
        except Exception as e:
            # Fail iff ModuleNotFoundError occurs.
            self.assertFalse(isinstance(e, ModuleNotFoundError))

if __name__ == "__main__":
    unittest.main()
"""

def py_import_test(target):
    name = target + "_import_test"
    srcs = native.existing_rule(target).get("srcs")
    to_import = ", ".join([
        (native.package_name() + src).replace("/", ".").replace(":", ".").replace(".py", "")
        for src in srcs
    ])
    test_content = py_import_test_template.replace("PLACEHOLDER", to_import)
    native.genrule(
        name = name + "_rule",
        outs = [name + ".py"],
        tags = ["NOLINT"],
        cmd = "echo '%s' > $@" % test_content,
    )

    native.py_test(
        name = name,
        srcs = [name + ".py"],
        tags = ["NOLINT"],
        deps = [target],
    )
