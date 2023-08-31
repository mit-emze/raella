# **RAELLA Artifact**
This repository contains the Timeloop/Accelergy models for RAELLA
Processing-In-Memory (PIM) Deep Neural Network (DNN) accelerator architecture
from "RAELLA: Reforming the Arithmetic for Efficient, Low-Resolution, and
Low-Loss Analog PIM: No Retraining Required!" by Tanner Andrulis, Vivienne Sze,
and Joel Emer (https://dl.acm.org/doi/10.1145/3579371.3589062).

This repository also includes supporting code to help you model new
architectures or test architectures with new DNN workloads.

## **Starting the Container**
Only x86 CPUs are currently supported. To start the container, run the
following commands:
```
git clone https://github.com/mit-emze/raella.git
cd raella
# FOLLOW THE INSTRUCTIONS IN THE docker-compose.yaml FILE
docker pull timeloopaccelergy/timeloop-accelergy-pytorch:raella-pim-amd64
export DOCKER_ARCH=amd64
docker-compose up
```

Click on the link that appears in the terminal to open Jupyter,
navigate to the artifact.ipynb notebook, and follow through the instructions
there.

## **Future Plans**
We are working on adding area, energy, and throughput models of other PIM
architectures as well as models of DNN accuracy running on these architectures.
