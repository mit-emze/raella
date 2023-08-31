import os, sys
import yaml

THIS_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

for d in os.listdir(f"{THIS_SCRIPT_DIR}/torch_values"):
    print(f"{d}")
    f2v = []
    pr = None
    for root, dirs, files in os.walk(f"{THIS_SCRIPT_DIR}/torch_values/{d}"):
        for f in files:
            if pr != root and pr is not None:
                print(f"  {pr}")
                pr = root
                avg = {
                    k: sum([float(f[k]) for f in f2v]) / len(f2v)
                    for k in f2v[0].keys()
                }
                print(avg)
                f2v = []
            pr = root
            lines = open(f"{root}/{f}", "r").readlines()
            result = {
                l.split("=")[0]: l.split("=")[1] for l in lines if "=" in l
            }
            f2v.append(result)
    avg = {
        k: sum([float(f[k]) for f in f2v]) / len(f2v) for k in f2v[0].keys()
    }
    print(avg)

f2v_all = []
for d in os.listdir(f"{THIS_SCRIPT_DIR}/layer_shapes_more_composite"):
    print(f"{d}")
    f2v = []
    for root, dirs, files in os.walk(
        f"{THIS_SCRIPT_DIR}/layer_shapes_more_composite/{d}"
    ):
        for f in files:
            y = yaml.load(
                open(f"{root}/{f}", "r").read(), Loader=yaml.FullLoader
            )
            w = y["problem"]["densities"]["Weights"][
                "unsigned_offset_invert_dense"
            ]
            i = y["problem"]["densities"]["Inputs"]["unsigned_offset"]
            avg_w = sum(w) / len(w)
            avg_i = sum(i) / len(i)

            result = {"weights": avg_w, "inputs": avg_i}
            f2v.append(result)
            f2v_all.append(result)
    avg = {
        k: sum([float(f[k]) for f in f2v]) / len(f2v) for k in f2v[0].keys()
    }
    print(avg)
avg = {
    k: sum([float(f[k]) for f in f2v_all]) / len(f2v_all)
    for k in f2v_all[0].keys()
}
print(avg)
