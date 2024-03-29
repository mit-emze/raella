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
cp docker-compose.yaml.example docker-compose.yaml
# FOLLOW THE INSTRUCTIONS IN THE docker-compose.yaml FILE
docker-compose up
```

Click on the link that appears in the terminal to open Jupyter, navigate to the
artifact.ipynb notebook, and follow through the instructions there.

## **FAQ**
### `docker-compose up` yields ERROR: Service 'labs' failed to build : Build failed
Pull the docker image manually and try again:
```
docker pull timeloopaccelergy/timeloop-accelergy-pytorch:raella-pim-amd64
```

## **Future Plans**
We are working on adding area, energy, and throughput models of other PIM
architectures as well as models of DNN accuracy running on these architectures.
