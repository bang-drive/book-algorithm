#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")

IMAGE="xiangquan/bang-algorithm:0.1"
docker build --network host -t ${IMAGE} $@ .
