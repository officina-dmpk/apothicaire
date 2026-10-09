#!/usr/bin/env python
"""Generates the invented out-of-distribution exercises of decision/ood/exercises/<id>/ (data.csv + meta.json).

They are synthetic and deterministic (no random noise): a concentration-time table is written from a PK model with fixed
parameters, so the route, dose, units and model in meta.json are exact. The NCA oracle of the benchmark exercises
(ground_truth.nca) is NOT reproduced here: Part 1 is written blind of the engine, so meta.json carries the simulation truth
and a note instead. Run `python decision/ood/make_ood_exercises.py` to (re)write the 12 folders.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exercises")


def pk1_bolus(t, dose, cl, v):
    return (dose / v) * math.exp(-(cl / v) * t)


def pk1_oral(t, dose, cl, v, ka, tlag=0.0):
    t = max(0.0, t - tlag)
    k = cl / v
    return (dose / v) * (ka / (ka - k)) * (math.exp(-k * t) - math.exp(-ka * t))


def pk1_infusion(t, dose, cl, v, dur):
    k = cl / v
    r = dose / dur
    if t <= dur:
        return (r / cl) * (1 - math.exp(-k * t))
    return (r / cl) * (1 - math.exp(-k * dur)) * math.exp(-k * (t - dur))


def pk2_oral_like(t, dose, a, alpha, b, beta, ka):
    return dose * (a * math.exp(-alpha * t) + b * math.exp(-beta * t) - (a + b) * math.exp(-ka * t))


def sig(x, n=5):
    return float(f"{x:.{n}g}")


EXERCISES = [
    dict(id="oodx01_oral_mg_ugml", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(250, "mg"),
         units=("h", "µg/mL"), times=[0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 24],
         fn=lambda t: pk1_oral(t, 250, 4.5, 38, 0.9), params={"cl": 4.5, "v": 38, "ka": 0.9}),
    dict(id="oodx02_iv_bolus_tlag", family="iv_bolus", model="pk1.iv_bolus", route="iv_bolus", dose=(120, "mg"),
         units=("h", "mg/L"), times=[0.25, 0.5, 1, 2, 3, 4, 6, 8, 12],
         fn=lambda t: pk1_bolus(t, 120, 3.1, 22), params={"cl": 3.1, "v": 22}),
    dict(id="oodx03_oral_c0", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(200, "mg"),
         units=("h", "ng/mL"), times=[0.5, 1, 2, 3, 4, 6, 8, 12, 24],
         fn=lambda t: 1000 * pk1_oral(t, 200, 5.0, 40, 1.1), params={"cl": 5.0, "v": 40, "ka": 1.1}),
    dict(id="oodx04_infusion_dur_h", family="iv_infusion", model="pk1.iv_infusion",
         route={"iv_infusion": {"duration": 90.0}}, dose=(75, "mg"), units=("min", "ng/mL"),
         times=[15, 30, 60, 90, 120, 180, 240, 360],
         fn=lambda t: 1000 * pk1_infusion(t, 75, 6.0, 30.0, 90.0), params={"cl": 6.0, "v": 30.0, "dur": 1.5},
         time_scale_to_csv=60, conc_factor_to_csv=1000),
    dict(id="oodx05_two_subjects", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(300, "mg"),
         units=("h", "ng/mL"), times=[0.5, 1, 2, 4, 6, 8, 12, 24], subjects=[(1, 5.5, 42.0, 1.0), (2, 4.0, 33.0, 0.8)],
         fn=None, params={"note": "subject 1: cl 5.5, v 42, ka 1.0; subject 2: cl 4.0, v 33, ka 0.8"}),
    dict(id="oodx06_steady_state", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(100, "mg"),
         units=("h", "ng/mL"), times=[0.5, 1, 2, 4, 6, 8, 10, 12],
         fn=lambda t: 1000 * sum(pk1_oral(t + 12 * j, 100, 6.0, 45.0, 1.0) for j in range(6)),
         params={"cl": 6.0, "v": 45.0, "ka": 1.0, "regimen": "100 mg every 12 h, steady state (6 doses superposed)"}),
    dict(id="oodx07_urine", family="urine", model="urine_recovery", route="unknown", dose=(50, "mg"),
         units=("h", "mL"), times=[0, 1, 2, 4, 6, 8, 12, 24], urine=True,
         params={"note": "urine recovery: cumulative amount (mg) and volume (mL), no concentration column"}),
    dict(id="oodx08_pk2_oral_fit", family="pk2_oral_1", model="pk2.oral_1", route="extravascular", dose=(400, "mg"),
         units=("h", "ng/mL"), times=[0.5, 1, 2, 3, 4, 6, 8, 12, 24, 36],
         fn=lambda t: 1000 * pk2_oral_like(t, 400, 0.008, 1.6, 0.006, 0.12, 0.8),
         params={"a": 0.008, "alpha": 1.6, "b": 0.006, "beta": 0.12, "ka": 0.8}),
    dict(id="oodx09_oral_min_ng", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(1200, "mg"),
         units=("min", "ng/mL"), times=[30, 60, 90, 120, 180, 240, 360, 480, 720, 1440],
         fn=lambda t: 1000 * pk1_oral(t, 1200, 7.0, 50.0, 0.8), params={"cl": 7.0, "v": 50.0, "ka": 0.8},
         time_scale_to_csv=60, conc_factor_to_csv=1000),
    dict(id="oodx10_oral_blq", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(80, "mg"),
         units=("h", "ng/mL"), times=[0.5, 1, 2, 3, 4, 6, 8, 12, 18, 24],
         fn=lambda t: 1000 * pk1_oral(t, 80, 4.0, 28.0, 1.2), params={"cl": 4.0, "v": 28.0, "ka": 1.2},
         blq={"lloq": 1.0, "unit": "ng/mL", "n_blq": 2, "written_as": 0}),
    dict(id="oodx11_oral_dose_g", family="oral_1", model="pk1.oral_1", route="extravascular", dose=(250, "mg"),
         units=("h", "mg/L"), times=[0.5, 1, 2, 4, 6, 8, 12, 24],
         fn=lambda t: pk1_oral(t, 250, 3.3, 26.0, 1.0), params={"cl": 3.3, "v": 26.0, "ka": 1.0}),
    dict(id="oodx12_iv_infusion_mcg", family="iv_infusion", model="pk1.iv_infusion",
         route={"iv_infusion": {"duration": 1.0}}, dose=(750, "ug"), units=("h", "ng/mL"),
         times=[0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6],
         fn=lambda t: 1000 * pk1_infusion(t, 0.75, 3.0, 25.0, 1.0), params={"cl": 3.0, "v": 25.0, "dur": 1.0},
         conc_factor_to_csv=1000),
]


def columns(ex):
    cols = []
    if ex.get("subjects"):
        cols.append({"name": "subject"})
    if ex.get("urine"):
        cols = [{"name": "time", "unit": ex["units"][0]}, {"name": "volume", "unit": "mL"}, {"name": "amount", "unit": "mg"}]
        return cols
    cols.append({"name": "time", "unit": ex["units"][0]})
    cols.append({"name": "conc", "unit": ex["units"][1]})
    return cols


def rows_for(ex):
    out = []
    if ex.get("urine"):
        cum = 0.0
        for i, t in enumerate(ex["times"]):
            amt = 0.0 if i == 0 else 3.0 * math.exp(-0.25 * t)
            cum += amt
            out.append([t, 0.0 if i == 0 else 120 + 40 * i, sig(cum, 3)])
        return out
    if ex.get("subjects"):
        for sid, cl, v, ka in ex["subjects"]:
            for t in ex["times"]:
                out.append([sid, t, sig(1000 * pk1_oral(t, 300, cl, v, ka))])
        return out
    for t in ex["times"]:
        c = ex["fn"](t)
        if ex.get("blq") and c < ex["blq"]["lloq"]:
            c = 0.0
        out.append([t, sig(c)])
    return out


def write_exercise(ex):
    d = os.path.join(OUT, ex["id"])
    os.makedirs(d, exist_ok=True)
    cols = columns(ex)
    header = ",".join(c["name"] + (f" ({c['unit']})" if "unit" in c else "") for c in cols)
    lines = [header]
    for r in rows_for(ex):
        lines.append(",".join(str(x) for x in r))
    with open(os.path.join(d, "data.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    params = ex.get("params") or {}
    hl = None
    if ex["model"] in ("pk1.iv_bolus", "pk1.oral_1", "pk1.iv_infusion") and "v" in params and "cl" in params:
        hl = math.log(2) * params["v"] / params["cl"]
    meta = {
        "id": ex["id"], "index": None, "family": ex["family"], "model": ex["model"], "route": ex["route"],
        "dose": {"amount": ex["dose"][0], "unit": ex["dose"][1]},
        "units": {"time": ex["units"][0], "conc": ex["units"][1] if not ex.get("urine") else None},
        "n_points": len(ex["times"]),
        "noise": {"type": "none", "note": "deterministic, no random noise"},
        "blq": ex.get("blq"),
        "simulation": {"parameters": params, "parameter_units": "times and rates in h, volumes in L, clearances in L/h, dose in the dose unit",
                       "time_scale_to_csv": ex.get("time_scale_to_csv", 1), "conc_factor_to_csv": ex.get("conc_factor_to_csv", 1),
                       "terminal_half_life_h": sig(hl) if hl else None},
        "ground_truth": {
            "data_import_columns": cols,
            "oracle_note": ("Part 1 is written blind of the engine: the NCA oracle (ground_truth.nca of the benchmark "
                            "exercises) was not generated here. The truth carried by this file is route, dose, units and "
                            "model; regenerate the oracle with Caladrius before comparing values."),
            "source": "decision/ood/make_ood_exercises.py",
        },
    }
    with open(os.path.join(d, "meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)


def main():
    for ex in EXERCISES:
        write_exercise(ex)
    print(f"{len(EXERCISES)} invented exercises written under {OUT}")


if __name__ == "__main__":
    main()
