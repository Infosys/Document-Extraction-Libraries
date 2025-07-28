#!/bin/bash

# Activate the virtual environment (NOTE: Change bin to Scripts for Windows)
source .venv/Scripts/activate 
echo "Virtual environment activated"

# >>>>>> Task Functions >>>>>>
function start_ray_and_deploy {
    echo "Starting Ray and deploying models..."
    
    cd src
    export PYTHONPATH=$(pwd)
    echo "PYTHONPATH is set to: $PYTHONPATH"

    # Check if Ray is running
    if ! ray status > /dev/null 2>&1; then
        echo "Starting Ray..."
        ray start --head --num-cpus=3 --num-gpus=0 --dashboard-host 0.0.0.0
        echo "Ray started"
    else
        echo "Ray is already running."
    fi

    # Deploy the models(NOTE: Change deploy to run for testing, Currently using run for both as deploy gives error)
    serve run config.yaml
    echo "Models deployed"
}

function stop_ray {
    echo "Stopping Ray server"
    ray stop
    echo "Ray server stopped"
}

# <<<<<< Task Functions <<<<<<

case "$1" in
  start)
    start_ray_and_deploy
    ;;
  stop)
    stop_ray
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
esac