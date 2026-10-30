"""精简原位吸收光谱：波长筛选 + 时间分箱取峰。"""
import pandas as pd
import numpy as np
from pathlib import Path

# ========== 处理参数 ==========
WL_MIN, WL_MAX, WL_STEP = 400, 500, 2
TIME_BIN = 0.2

base = Path(__file__).resolve().parent.parent
src = base / "2026610(1)(1)_processed.csv"
enc_in = "gb2312"

df = pd.read_csv(src, header=None, encoding=enc_in, low_memory=False)
times = np.array([float(x) for x in df.iloc[0, 1:].tolist()])
data = df.iloc[4:].reset_index(drop=True)
wl_all = pd.to_numeric(data.iloc[:, 0], errors="coerce").values
spec_all = data.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").values

wl_targets = np.arange(WL_MIN, WL_MAX + 1e-9, WL_STEP)
row_idx = [np.argmin(np.abs(wl_all - w)) for w in wl_targets]
wl = wl_all[row_idx]
spec_wl = spec_all[row_idx, :]

band_mean = np.nanmean(spec_wl, axis=0)
edges = np.arange(times[0], times[-1] + TIME_BIN, TIME_BIN)
sel_idx = []
for i in range(len(edges) - 1):
    mask = (times >= edges[i]) & (times < edges[i + 1])
    if not mask.any():
        continue
    sub = np.where(mask)[0]
    sel_idx.append(sub[np.argmax(band_mean[sub])])
if sel_idx[-1] != len(times) - 1:
    sel_idx.append(len(times) - 1)
sel_idx = sorted(set(sel_idx))
times_sel = times[sel_idx]
spec = spec_wl[:, sel_idx]

print(f"波长: {WL_MIN}-{WL_MAX} nm, 步长 {WL_STEP} nm -> {len(wl)} 点")
print(f"时间: {TIME_BIN}s 分箱取峰 -> {len(times_sel)} 条光谱")
print(f"数据量: {spec_all.shape[1]} x {spec_all.shape[0]} -> {spec.shape[1]} x {spec.shape[0]}")

csv_path = base / "2026610_reduced.csv"
out = pd.DataFrame(spec, index=wl)
out.index.name = "Wavelength(nm)"
out.columns = [f"{t:g}" for t in times_sel]
out.to_csv(csv_path, encoding="utf-8-sig", float_format="%.6f")

origin_path = base / "2026610_origin_waterfall_reduced.txt"
with open(origin_path, "w", encoding="utf-8-sig", newline="") as f:
    f.write("Long Name\tWavelength")
    for t in times_sel:
        f.write(f"\t{t:g}")
    f.write("\n")
    f.write("Units\tnm")
    f.write("\tAU" * len(times_sel))
    f.write("\n")
    for i in range(len(wl)):
        f.write(f"{wl[i]:.2f}")
        for j in range(len(times_sel)):
            v = spec[i, j]
            f.write(f"\t{v:.6f}" if pd.notna(v) else "\t")
        f.write("\n")

info_path = base / "2026610_reduced_readme.txt"
info_path.write_text(
    f"""原位吸收光谱精简数据说明
========================

源文件: 2026610(1)(1)_processed.csv

处理策略
--------
1. 波长筛选: {WL_MIN}-{WL_MAX} nm，间隔 {WL_STEP} nm
   - 排除 <400 nm 短波干扰
   - 覆盖材料吸收带 (~415-420 nm)

2. 时间精简: 每 {TIME_BIN} s 时间窗内
   - 选取 400-500 nm 波段平均吸光度最高的光谱
   - 保留 ~10.4 s 瞬态吸收峰

输出规模: {len(wl)} 波长 x {len(times_sel)} 光谱（原 {spec_all.shape[1]} 条）
时间范围: {times_sel[0]:g} - {times_sel[-1]:g} s

文件
----
- 2026610_reduced.csv
- 2026610_origin_waterfall_reduced.txt
""",
    encoding="utf-8",
)

print(f"CSV: {csv_path}")
print(f"Origin: {origin_path}")
