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
pip3 install -r third_party/requirements.txt
```

But note that you should always run in the project root directory.

```bash
python3 bang/planning/dragon_planner.py
```
