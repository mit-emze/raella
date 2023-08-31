import os, sys
import yaml

THIS_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAYERDIR = f"{THIS_SCRIPT_DIR}/../dnn_layers/"
ISAACDIR = f"{THIS_SCRIPT_DIR}/torch_values/isaac_like"

# Iterate through recorded_statistics/torch_values/isaac_like
for dnn in os.listdir(LAYERDIR):
    avg_avg_i = 0
    n_layers = 0
    for layer in os.listdir(f"{LAYERDIR}/{dnn}"):
        layer = f"{LAYERDIR}/{dnn}/{layer}"
        y = yaml.load(open(f"{layer}", "r").read(), Loader=yaml.FullLoader)[
            "problem"
        ]
        layer_name = y["layer_name"]
        avg_w = 0
        avg_i = 0
        for i, v in enumerate(
            y["densities"]["Weights"]["unsigned_offset_invert_dense"]
        ):
            avg_w += v if i % 2 == 0 else v * 2
        for i, v in enumerate(y["densities"]["Inputs"]["unsigned_offset"]):
            avg_i += v
        avg_w /= 4 * 3
        avg_i /= 8
        avg_avg_i += avg_i
        # print(f"{layer_name} {avg_w} {avg_i}")
        # Open the corresponding isaac_like file
        # isaac_layer = f"{ISAACDIR}/{dnn}/{layer_name}"
        # lines = open(isaac_layer, "r").readlines()
        # for i, l in enumerate(lines):
        #     if "AVERAGE_WEIGHT_VALUE" in l:
        #         lines[i] = f"AVERAGE_WEIGHT_VALUE={avg_w}\n"
        #     if "bert" in dnn.lower() and "AVERAGE_INPUT_VALUE" in l:
        #         lines[i] = f"AVERAGE_INPUT_VALUE={avg_i}\n"
        # open(isaac_layer, "w").writelines(lines)
        n_layers += 1
    avg_avg_i /= n_layers
    print(f"{dnn} {avg_avg_i}")
