# Module 01: Research Configuration — 2019 Baseline Edition

这份 Module 01 是完整版本，不需要先运行旧版，也不需要将旧版与新版拼在一起。

## 文件与使用方式

- `module_01_research_configuration.ipynb`：直接在 Jupyter 或 PyCharm 中打开；包含中文 Markdown 说明和 8 个完整英文 code cells。
- `guide.md`：每个 cell 的完整代码、目的、预期结果、每个函数和方法的详细讲解，以及为什么这样组织项目。
- `study.json`：当前研究设置的预置文件；Notebook 的 Cell 08 会在所选位置保存并回读配置。
- `study_config.py`：相同的通用配置类及普通函数，供之后拆分 Python 文件时参考；运行 Notebook 不需要导入这个文件。

解压后，建议保持 `module_01` 文件夹及其文件。将 Notebook 的 kernel 工作目录设为这个文件夹，重启 kernel，再从 Cell 01 到 Cell 08 顺序运行。在 Cell 08 运行前确认 `Path.cwd()` 指向你想保存配置的位置。

默认相对路径以保存的 `study.json` 为基准：

- `../data/financial_data.csv`：后续财务数据导入文件。
- `../data/retail_comparison.sqlite`：后续 SQLite 数据库。
- `../results`：后续图表及报告目录。

如果将 Notebook 和 JSON 放在项目根目录，请在 Cell 05 将上述路径改为 `data/financial_data.csv`、`data/retail_comparison.sqlite` 和 `results`。

## 2019 基期与研究范围

正式比较为 2019—2024 六年，共 12 条计划分部年度记录。Amazon 2019—2024 与 Walmart FY2020—FY2025 近似配对。2019 同时作为疫情前参照年和销售指数基期；2020—2021 标记为疫情冲击阶段，2022—2024 标记为后续调整阶段。

阶段是研究内容中的可选文字标签，由 `periods` 中的 `comparison_stage` 保存，不在通用类中写死。当前类检查配置结构与年度配对；后续数据模块会核对实际来源与报告日期，分析模块会检查本研究所需的阶段标签。

销售指数在各分部自己的 2019 分析年度设为 100。销售同比仍与上年比较，2019 因未采集 2018 基线而留空。单个疫情前年份和两个业务构成不同的分部支持描述性比较，不能由此识别疫情因果效应。

## 运行后应核对的输出

```text
Configuration is valid.
Business units: 2
Planned observations: 12
Index base year: 2019
Configuration saved and reloaded successfully.
```

这些输出分布在 Cell 06—08，实际还会打印题目、研究问题、各年份映射、阶段标签、口径说明和文件路径。本模块只保存配置，不创建财务数据库或计算财务指标。

完整四模块规划见包内上一级的 `project_plan.md`。
