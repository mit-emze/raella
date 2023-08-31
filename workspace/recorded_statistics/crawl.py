# Crawl through the following two directories:
# THIS_SCRIPT_DIR/torch_values/raella_no_speculation
# THIS_SCRIPT_DIR/typical_values/raella_no_speculation_2b_cells

# For each file in the directory, append the following line:
# SPECULATION_ENABLED=0
import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
for target in ["raella_no_speculation", "raella_no_speculation_2b_cells"]:
    for f in os.listdir(f"{thisdir}/torch_values/{target}"):
        for g in os.listdir(f"{thisdir}/torch_values/{target}/{f}"):
            with open(f"{thisdir}/torch_values/{target}/{f}/{g}", "a") as df:
                df.write("SPECULATION_ENABLED=0\n")
