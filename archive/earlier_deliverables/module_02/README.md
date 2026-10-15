# Module 02: Data and Database Management

本模块对应“获取基础数据 → DataFrame 清洗与检查 → SQLite 保存 → 查询回读核对”。正式研究仍为 2019—2024 六年，2019 为疫情前参照和销售指数基期。

## 先打开哪个文件

module_02_code_explanation_guide.html 是排版阅读版：完整英文代码使用浅灰底、等宽字体和行号，中文逐句说明使用白底正文；支持宽屏左右对照、上下切换及代码行定位。对应的 module_02_combined_notebook_detailed_guide.md 已改为同样的 210 条代码说明，覆盖所有非空代码行。英文 Python 代码保持不变。双击 HTML 用浏览器打开即可，不需网络或安装软件。

如果 Module 01 和 Module 02 放在同一个总 Notebook 中，优先阅读 `module_02_combined_notebook_detailed_guide.md`。这是更详细的学习版，包含 12 格完整英文代码和中文逐句解释；其中 Cell 02 直接复用第一模块已定义的函数，按项目根目录中的 study.json 安排路径。先运行第一模块，再运行第二模块。该版已在临时项目中完整执行并检查重复导入，执行记录见 `combined_notebook_guide_verification.txt`。

`guide.md` 将 12 个 cells 的完整英文代码、中文解释和每个函数/方法的构建思路放在一起。`module_02_data_and_database_management.ipynb` 包含相同代码及中文 Markdown 说明，可以直接在 Jupyter 或 PyCharm 打开。

`data_management.py` 是清洗函数和数据库类的配套 Python 版本。Notebook 内已包含这些定义，运行 Notebook 不需要导入它；后续拆分代码时可以复用此文件。

`source_notes.md` 记录四份官方年报、采用的历史年度列、逐年转录金额与日期推导依据。`run_summary.txt` 是本次代码执行的记录，其中宿主机器路径已替换为 `<project_root>`，便于阅读。

## 完整包目录

```text
project/
    module_01/
        study_config.py
        study.json
        guide.md
        module_01_research_configuration.ipynb
        README.md
    module_02/
        module_02_data_and_database_management.ipynb
        data_management.py
        guide.md
        source_notes.md
        requirements.txt
        run_summary.txt
        README.md
    data/
        raw/
            amazon_segment_raw.csv
            walmart_segment_raw.csv
            source_manifest.json
            reports/README.md
        clean/financial_records.csv
        financial_data.csv
        retail_comparison.sqlite
        README.md
    project_plan.md
```

## 运行方法

1. 解压完整包，保持三个文件夹的相对位置，不要只移动 Notebook 文件。
2. 打开第二模块的 Notebook，让 kernel 的工作目录为 `module_02`。
3. 若 pandas 未安装，在额外的 Notebook cell 中运行 `%pip install pandas`，安装后重启 kernel。SQLite 使用标准库，不必另装服务。
4. 从 Cell 01 到 Cell 12 顺序运行；Cell 02 打印的配置和数据库路径应与目录安排一致。
5. 修正版 Cell 02 会检查当前目录的 module_01、上一级的 module_01 和当前目录本身，要求 study_config.py 与 study.json 同时存在；总 Notebook 在项目根目录也可以直接运行。找不到时会显示实际工作目录。若单独移动 JSON，还需核对 JSON 内的数据相对路径。

第二模块使用第一模块的 `study_config.py` 读取并检查 JSON，因此完整包同时附带这一配套文件。Module 01 的 Notebook 不需要事先在同一 kernel 中执行；已保存的配置文件即可作为入口。

## 当前数据与产出

原始 CSV 是核对官方财报后人工转录的真实分部数据，不是模拟值，也不是自动抓取代码输出。每家分部六行。所有金额原表均为 USD millions，原始括号、逗号和来源字段保留。

完整包中的 SQLite 数据库已经实际生成：business_units 为 2 行，financial_records 为 12 行，metric_results 为 0 行。重复运行相同输入时，写入计数显示 12 行 unchanged 属于正常行为；在新文件上重建时显示 12 行 inserted。

数据库可从这两份原始 CSV 和 Module 01 配置重新生成。若想在新文件上练习，可在 Module 01 设置中将 database_file 改为另一个 SQLite 文件名，再保存配置；已有数据库不必删除。

已检查完整执行、逐字段回读、重复导入不增行、负营业利润保留、错误记录拒绝、写入事务回滚、基础数据更新后的旧指标失效、外键及数据库重新打开。

本模块不计算销售同比、营业利润率或销售指数。下一模块将读取已保存基础数据，再加入分析年度与比较阶段，使用配置中的 2019 基期计算指标。

## 来源材料范围

包内提供原始转录 CSV、官方 URL、采用章节及来源清单，未附完整官方 HTML 文件。浏览器核对可使用 source_notes.md 的四个官方链接；完整 HTML 可按需另行保存到 data/raw/reports/。Notebook 的导入步骤无需联网，不能把本地 CSV 读取描述为网页自动抓取。
