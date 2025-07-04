# Bang Algorithm

## Setup with Bazel

```bash
bash third_party/setup_toolchain.sh
```

Then you can build and run the project with bazel command.

```bash
bazel run //bang/planning:dragon_planner
```

## Setup with pip

Besides Bazel, you can also install dependencies with pip and venv.

```bash
pip3 install --upgrade -r third_party/requirements.txt
```

But note that you should always run in the project root directory.

```bash
python3 bang/planning/dragon_planner.py
```

## Upgrade third-party libraries

From time to time, the third-party libraries may need to be upgraded, especially `ultralytics` which
breaks often on old versions. You can do this easily by running the following command.


```bash
# For Bazel, resolve and freeze the requirements lock file again.
bash third_party/resolve_requirements.sh

# For PIP, just rerun the install command.
pip3 install --upgrade -r third_party/requirements.txt
```
