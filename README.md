# ELEC5516 Lab 5：集成光子设计 - 微环谐振器

本仓库用于保存 ELEC5516 Electrical and Optical Sensor Design 的 Lab 5 项目文件，主题为：

**Integrated Photonics Design of an SOI Microring Resonator Sensor**

项目内容包括课程资料、原始 Lumerical 模型、Overleaf-ready LaTeX 报告工程、已编译 PDF 报告、生成脚本与结果占位目录。

## 项目结构

```text
ELEC5516_Lab5_Microring/
├─ docs/                 # Lab 说明和 Lecture 12 讲义
├─ models_original/      # 原始 Lumerical 模型，不应覆盖
├─ work/                 # 本地临时工作区
├─ scripts/              # 报告生成脚本
├─ results/              # 仿真结果导出目录
├─ figures/              # 原始或后续导出的图像
└─ report/
   ├─ overleaf_project/  # 可上传到 Overleaf 的 LaTeX 工程
   ├─ ELEC5516_Lab5_Microring_Report.pdf
   ├─ ELEC5516_Lab5_Microring_Overleaf.zip
   ├─ compile_log.txt
   └─ report_generation_summary.md
```

## 已生成文件

- `report/ELEC5516_Lab5_Microring_Report.pdf`：已编译的 PDF 报告
- `report/ELEC5516_Lab5_Microring_Overleaf.zip`：可直接上传到 Overleaf 的压缩包
- `report/overleaf_project/main.tex`：LaTeX 主文件
- `scripts/generate_report_package.py`：生成报告工程、图表和摘要文件的脚本

## Overleaf 上传方法

1. 打开 Overleaf。
2. 选择 **New Project**。
3. 选择 **Upload Project**。
4. 上传：

```text
report/ELEC5516_Lab5_Microring_Overleaf.zip
```

5. 在 Overleaf 中编译 `main.tex`。

## 当前报告状态

报告已经可以编译，但因为当前 `results/` 和 `figures/` 中没有真实导出的仿真结果，报告中没有伪造数值。以下内容已在报告中标记为 TODO 或 “Not available from current simulation output”：

- INTERCONNECT through/drop port transfer function
- 实际 resonance wavelength、FSR、FWHM、Q factor、finesse
- FDE 提取的 `n_eff` 和 `n_g`
- symmetric/anti-symmetric coupled-mode index
- `Delta n` 和 coupling length `L_c`
- varFDTD field profile 和 drop-port spectrum
- gap sweep 数据，例如 80 nm、100 nm、120 nm、150 nm

## 后续建议

完成 Lumerical 仿真后，建议将导出的 CSV、JSON 或图片放入：

- `results/`：数值结果，例如 spectrum、mode index、sweep table
- `figures/`：仿真截图或导出的图像

然后重新运行：

```powershell
python .\scripts\generate_report_package.py
```

再重新编译报告并提交更新。

## 注意事项

- 不要覆盖 `models_original/` 中的原始模型。
- 不要把本地工具缓存或 LaTeX 编译器文件提交到仓库。
- 报告中的目标值和公式推导值与真实仿真输出已明确区分。
