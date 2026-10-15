# 同一个 Notebook 中运行 Module 02：路径修正说明

你的总 Notebook 在 `/Users/dadabaibaidegoose/Desktop/JupyterProject/retail_growth_and_profitability_comparison.ipynb`。第一模块的函数定义与第二模块运行在同一个 kernel 中，所以第二模块 Cell 02 直接调用已定义的 `load_study_config`，无需再导入外部 `study_config.py`。

已直接修改这个现有 Notebook：第一模块 Cell 05 中的三个保存路径改为 `data/...` 和 `results`；第二模块 Cell 02 用 `Path.cwd() / "study.json"` 读取项目根目录的配置。已同步修改现有 JSON，并在项目的 `data/raw/` 中补齐两份原始转录 CSV 和来源清单。未计算指标，未创建财务数据库。

## 重新运行

1. 若 PyCharm 仍显示旧代码，请从磁盘重新加载 Notebook；如提示选择编辑器版本或磁盘版本，选择本次修改后的磁盘版本。第二模块 Cell 02 应不再出现 `candidate_directories` 或 `from study_config import ...`。
2. 重启 kernel，顺序运行第一模块 Cell 01—08，让函数定义和保存的配置一致。
3. 再运行第二模块 Cell 01—02。预期为 12 条计划记录、2019 基期，数据库路径在 `Desktop/JupyterProject/data/` 里。
4. 后续 Cell 03—12 继续使用第二模块 guide 的原有代码。

`Path.cwd()` 获取 kernel 工作目录。`/ "study.json"` 将目录与文件名拼接。`load_study_config(CONFIG_PATH)` 调用第一模块已经定义的函数，读取 JSON 并创建配置对象；它不会自行读取财务 CSV。`config.resolve_paths(CONFIG_PATH)` 按 JSON 所在目录解析数据路径。

为什么也修改第一模块 Cell 05？因为第一模块 Cell 08 每次会把 Cell 05 的设置写入 JSON。如果只手改 JSON，重新运行第一模块就会恢复旧路径。JSON 在项目根目录时，`../data/...` 指向项目之外的 `Desktop/data/`；`data/...` 才指向项目内的 `JupyterProject/data/`。

此方法依赖先运行第一模块的函数定义，kernel 重启后仍需要重新运行。独立运行第二模块的 Notebook 时，原完整包中使用配套 Python 文件的方式仍适用。

`module_02_cell_02.py` 保存修正后的完整英文 cell 代码，可按需复制；不是需要单独运行的完整程序。`before_fix_backup.zip` 保存修改前的 Notebook 和 JSON。原始数字及免费官方来源见 `source_notes.md`。
