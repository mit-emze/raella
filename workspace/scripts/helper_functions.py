from typing import Dict, List, Optional, Tuple
import yaml
from matplotlib import pyplot as plt
import time


def get_energy_cycles(path: str) -> Tuple[dict, int]:
    """!@brief Read the energy stats from a file.
    !@returns A dictionary of energy stats.
    """
    time.sleep(1)  # In case the file is still being written
    lines = open(path, "r").readlines()
    cycles = 1
    for i, l in enumerate(lines):
        if "Computes =" in l:
            computes = int(l.split()[-1])
            break
        if "Cycles: " in l:
            cycles = int(l.split()[-1])
    energy = {}
    for l in lines[i + 1 :]:
        if "=" in l:
            energy[l.rsplit("=", 1)[0].strip()] = (
                float(l.rsplit("=", 1)[1].strip()) * computes
            )
    return energy, cycles


def get_area_from_art(path: str) -> dict:
    """!@brief Read the area stats from a file.
    !@returns A dictionary of area stats.
    """
    time.sleep(1)  # In case the file is still being written
    d = yaml.load(open(path, "r").read(), Loader=yaml.FullLoader)
    name2area = {}
    for x in d["ART"]["tables"]:
        namecount = x["name"].split(".", 1)[1]
        name = namecount.split("[", 1)[0]
        count = int(namecount.split("[", 1)[1].split(".")[-1][:-1])
        name2area[name] = count * x["area"]
    name2area["Total"] = sum(name2area.values())
    return name2area


def prep_numbers_for_plot(stats_dict: dict) -> dict:
    """!@brief Convert the stats to a format that can be plotted.
    !@param stats_dict: The stats to convert.
    !@returns A dictionary of stats nicely formatted for plotting.
    """

    def grab(*args):
        return sum([stats_dict.pop(s, 0) for s in args])

    new_stats = {
        "ADC": grab("column_readout", "shift_add", "timely_psubbuf"),
        "Crossbar": grab("pim_cell"),
        "Input Drivers / DAC": grab("input_drivers"),
        "Input Buf.": grab("input_buffer"),
        "Output Buf.": grab("output_register", "output_center_offset_correct"),
        "Quantization": grab("output_quantize"),
        "Global Data Movement": grab(
            "on_chip_network", "eDRAM_buf", "inter_tile_network"
        ),
        "Other": grab("dff"),
        "Total": grab("Total"),
    }
    # Grab any remaining stats
    new_stats.update({k: v for k, v in stats_dict.items() if v != 0})
    return new_stats


PLOT_COLORS = [
    # Blue, red, green, purple, teal, orange, navy, brown, pink, gray
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#17becf",
    "#ff7f0e",
    "#000080",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]


def plot_results(
    energy: Optional[Dict[dict, float]] = None,
    area: Optional[Dict[dict, float]] = None,
    cycles: Optional[Dict[dict, float]] = None,
    throughput: Optional[Dict[dict, float]] = None,
    energy_mj: bool = False,
):
    all = {
        "Energy": energy,
        "Area": area,
        "Time": cycles,
        "Throughput": throughput,
    }

    all = {k: v for k, v in all.items() if v is not None}
    plt.figure(figsize=(6 * len(all), 6))
    plt.subplots_adjust(hspace=0.5, wspace=0.5)
    for i, (plotname, v) in enumerate(all.items()):
        plt.subplot(1, len(all), i + 1)
        plt.title(plotname)
        keys = []
        for d in v.values():
            for k in d.keys():
                if k not in keys:
                    keys.append(k)
        if "Total" in keys:
            keys.remove("Total")

        if plotname == "Area":
            scale = 1e-6
        elif plotname == "Time":
            scale = 1e-3
        elif plotname == "Throughput":
            scale = 1e-6
        else:
            scale = 1e-9 if energy_mj else 1e-6

        x = list(range(len(v)))
        bottom = [0] * len(v)
        colors = [p for p in PLOT_COLORS]
        for k in keys:
            plt.bar(
                x,
                [d.get(k, 0) * scale for d in v.values()],
                bottom=bottom,
                label=k,
                width=0.8,
                color=colors.pop(0) if colors else None,
            )
            bottom = [
                bottom[i] + d.get(k, 0) * scale
                for i, d in enumerate(v.values())
            ]
        plt.xticks(x, v.keys(), rotation=90)

        if plotname == "Area":
            plt.ylabel("Architecture Area (mm^2)")
        elif plotname == "Time":
            plt.ylabel("Time per Batch (us)")
        elif plotname == "Throughput":
            plt.ylabel("Throughput (million batches/s)")
        else:
            plt.ylabel(f"Energy per Batch ({'m' if energy_mj else 'u'}J)")
        if plotname != "Time" and plotname != "Throughput":
            plt.legend()
    plt.show()
    plt.close()
