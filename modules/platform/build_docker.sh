#!/usr/bin/env bash

monitorName="sample-monitor"
tag="v1"

docker build -t $monitorName:$tag .