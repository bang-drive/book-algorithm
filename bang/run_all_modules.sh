#!/usr/bin/env bash

bazel run //bang/perception &
bazel run //bang/prediction &
bazel run //bang/planning -- --show
