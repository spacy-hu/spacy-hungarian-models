#!/bin/bash

# Check if an argument was provided
if [ -z "$1" ]; then
  echo "No directory path provided."
  exit 1
fi

if [ ! -d "$1" ]; then
  echo "The path '$1' is not a valid directory."
  exit 1
fi

model_dir=$1

docker buildx build -t trainer "${model_dir}" --build-context root="." -f ./Dockerfile
docker run -it --rm --name trainer \
  --runtime=nvidia \
  -v "$(pwd)/${model_dir}"/data:/app/model/data \
  -v "$(pwd)/${model_dir}"/models:/app/model/models \
  -v "$(pwd)/${model_dir}"/configs:/app/model/configs \
  -v "$(pwd)/${model_dir}"/packages:/app/model/packages \
  -v "$(pwd)/${model_dir}"/wandb:/app/model/wandb \
  -v "$(pwd)/${model_dir}"/project.lock:/app/model/project.lock \
  -v "$(pwd)/${model_dir}"/../huspacy:/app/huspacy \
  -v "$(pwd)/${model_dir}"/../scripts:/app/scripts \
  trainer "./train.sh"