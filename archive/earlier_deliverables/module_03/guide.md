# Module 03 Metrics and Comparative Analysis

本模块从第二模块已保存的 SQLite 基础表读取数据，加入分析年度与阶段，计算销售同比、营业利润率、销售指数，保存并回读核对，再导出年度表、指标长表与阶段汇总。代码使用英文，中文逐句说明与完整代码分开排版，行号是本格内部的位置。

优先使用项目根目录的总 Notebook：先顺序运行 Module 01、Module 02，再运行本模块。Module 03 复用第一模块的 load_study_config，以及第二模块的 DatabaseManager 和 validate_records，不额外引入导入路径设置。只打开本模块参考 Notebook 并重启 kernel 后，前两个模块名称尚未定义；应使用完整总 Notebook，或先在同一 kernel 执行前面定义。kernel 工作目录应为包含 study.json 的项目根目录。

2019 为当前配置基期，正式比较年度为 2019—2024。两家公司首年同比没有样本内前一年数据，保留缺失；营业利润为负时，利润率也保留负数。所有百分比结果已乘 100，数值 5 表示 5%。阶段平均为有效年度的非加权算术平均，并同时保存有效年份数。它不是 CAGR，也不是合并利润率，不作为疫情因果效应估计。

## 阅读与执行

Cell 01—02 准备工具与路径，Cell 03—07 定义通用工具，Cell 08—12 实际读库、计算、保存、回读、汇总与关闭。完整代码可以复制；说明中的行号及中文不要复制到 Python 格里。

HTML 阅读版把完整英文代码放在浅灰底等宽字体区域，把中文逐句说明放在白底区域。宽屏可左右对照；点击说明中的行号可定位语句；复制按钮只使用原始英文代码。


## Cell 01: Import Libraries

### 完整代码

```python
# Cell 01: Import Libraries

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 01: Import Libraries`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜导入输入标识工具**

对应语句：`import hashlib`

**语法和执行含义：** hashlib 提供 sha256 等函数，后面将配置与源数据生成固定长度的文本标识。

**为什么这样写：** 记录本次结果对应的输入版本；它不改变金额，也不计算业务指标。

---

**第 4 行｜导入 JSON 工具**

对应语句：`import json`

**语法和执行含义：** json 用于把普通字典转换成一致的 JSON 文本，以及保存本次分析清单。

**为什么这样写：** 现有配置与输出说明使用普通 JSON，便于查看和复用。

---

**第 5 行｜导入数值检查工具**

对应语句：`import math`

**语法和执行含义：** math 提供 isfinite 和 isclose。前者确认有限数值，后者比较浮点数是否在小容差内相等。

**为什么这样写：** 保存和回读时检查数值；避免正常的浮点表示差异被误判为错误。

---

**第 6 行｜导入时间类型和时区**

对应语句：`from datetime import datetime, timezone`

**语法和执行含义：** 从 datetime 模块取 datetime 与 timezone。后面 datetime.now(timezone.utc) 得到带 UTC 时区的当前时间。

**为什么这样写：** 指标结果保存计算时刻，UTC 让不同机器的记录使用一致时间基准。

---

**第 7 行｜导入路径类型**

对应语句：`from pathlib import Path`

**语法和执行含义：** Path 表示文件或文件夹位置；cwd、is_file、mkdir 等操作通过它执行。

**为什么这样写：** 沿用前两个模块的路径写法。导入不会创建文件。

---

**第 9 行｜导入 pandas 并起简称**

对应语句：`import pandas as pd`

**语法和执行含义：** as pd 给 pandas 一个简短名称，后面 pd.DataFrame、pd.isna、pd.read_sql_query 都通过它调用。

**为什么这样写：** 处理现有数据库查询结果、年度指标与阶段汇总，不增加新的第三方库。

---

## Cell 02: Reload Configuration and Set Analysis Paths

### 完整代码

```python
# Cell 02: Reload Configuration and Set Analysis Paths

CONFIG_PATH = Path.cwd() / "study.json"
if not CONFIG_PATH.is_file():
    raise FileNotFoundError("Run the combined notebook from the project root containing study.json.")
config = load_study_config(CONFIG_PATH)
paths = config.resolve_paths(CONFIG_PATH)
DATABASE_FILE = paths["database_file"]
RESULTS_DIRECTORY = paths["results_directory"]
if not DATABASE_FILE.is_file():
    raise FileNotFoundError("The database is missing. Complete Module 02 before Module 03.")

print(f"Configuration: {CONFIG_PATH}")
print(f"Database: {DATABASE_FILE}")
print(f"Results directory: {RESULTS_DIRECTORY}")
print(f"Configured base year: {config.index_base_year}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 02: Reload Configuration and Set Analysis Paths`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜定位根目录 JSON**

对应语句：`CONFIG_PATH = Path.cwd() / "study.json"`

**语法和执行含义：** Path.cwd() 取得 kernel 当前目录，/ 拼上 study.json，结果赋给 CONFIG_PATH。

**为什么这样写：** 总 Notebook 从项目根目录运行，继续复用根目录配置。

---

**第 4—5 行｜在错误目录时明确停止**

对应语句：`if not CONFIG_PATH.is_file(): ⏐ raise FileNotFoundError("Run the combined notebook from the project root containing study.json.")`

**语法和执行含义：** is_file 判断该位置是否已有文件；not 让不存在时进入 if，并抛出 FileNotFoundError。

**为什么这样写：** 及时告诉你切换到包含 study.json 的项目根目录，避免再次出现难以定位的路径报错。

---

**第 6 行｜重新读入当前研究设置**

对应语句：`config = load_study_config(CONFIG_PATH)`

**语法和执行含义：** 调用第一模块定义的 load_study_config，读取并校验 JSON，返回新的 config 对象。

**为什么这样写：** 如果配置刚修改过，本模块使用磁盘上当前设置；先运行第一模块使函数定义存在。

---

**第 7—9 行｜取出数据库和结果路径**

对应语句：`paths = config.resolve_paths(CONFIG_PATH) ⏐ DATABASE_FILE = paths["database_file"] ⏐ RESULTS_DIRECTORY = paths["results_directory"]`

**语法和执行含义：** resolve_paths 返回三个路径的字典；第 8 行取 database_file，第 9 行取 results_directory。

**为什么这样写：** 基础数据由数据库提供，结果单独导出到配置指定的目录。

---

**第 10—11 行｜要求基础数据库已经存在**

对应语句：`if not DATABASE_FILE.is_file(): ⏐ raise FileNotFoundError("The database is missing. Complete Module 02 before Module 03.")`

**语法和执行含义：** 检查 DATABASE_FILE 对应的文件是否存在，不存在就报错，提示先完成第二模块。

**为什么这样写：** SQLite connect 会创建新文件，因此先检查，防止误建一个没有基础数据的空库。

---

**第 13—16 行｜显示本次采用位置和基期**

对应语句：`print(f"Configuration: {CONFIG_PATH}") ⏐ print(f"Database: {DATABASE_FILE}") ⏐ print(f"Results directory: {RESULTS_DIRECTORY}") ⏐ print(f"Configured base year: {config.index_base_year}")`

**语法和执行含义：** 四个 f-string 分别插入配置位置、数据库位置、结果目录、index_base_year 属性。

**为什么这样写：** 运行前人工核对路径和基期；这里只显示设置，还没有计算任何指标。

---

## Cell 03: Define Metric Rules and the Input Signature

### 完整代码

```python
# Cell 03: Define Metric Rules and the Input Signature

CALCULATION_VERSION = "1.0"
METRIC_SPECS = {
    "sales_growth": {"column": "sales_growth_pct", "unit": "percent"},
    "operating_margin": {"column": "operating_margin_pct", "unit": "percent"},
    "sales_index": {"column": "sales_index", "unit": "index_points"},
}
METRIC_COLUMNS = [
    "study_id", "config_signature", "unit_id", "analysis_year", "metric_name",
    "metric_value", "value_unit", "calculation_time", "missing_reason",
]


def make_run_signature(config, financial_df):
    """Identify the settings, calculation version and selected source records."""
    records = financial_df.sort_values(["unit_id", "fiscal_year"]).to_dict("records")
    payload = {
        "calculation_version": CALCULATION_VERSION,
        "settings": config.to_dict(),
        "financial_records": records,
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 03: Define Metric Rules and the Input Signature`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜记录公式版本**

对应语句：`CALCULATION_VERSION = "1.0"`

**语法和执行含义：** 把文字 1.0 保存到 CALCULATION_VERSION。大写名称表示这是本版通用规则。

**为什么这样写：** 以后公式逻辑改变时更新这个版本，让新旧计算能够区分。

---

**第 4—8 行｜把指标标识对应到列名与单位**

对应语句：`METRIC_SPECS = { ⏐ "sales_growth": {"column": "sales_growth_pct", "unit": "percent"}, ⏐ "operating_margin": {"column": "operating_margin_pct", "unit": "percent"}, ⏐ "sales_index": {"column": "sales_index", "unit": "index_points"}, ⏐ }`

**语法和执行含义：** 外层字典用 sales_growth 等配置标识查询；内层字典有 column 与 unit。两个百分比列用 percent，销售指数用 index_points。

**为什么这样写：** 同一套规则用于计算、长表、验证、汇总。百分比结果已乘 100，数字 5 表示 5%，不是 0.05。

---

**第 9—12 行｜规定九个结果字段及顺序**

对应语句：`METRIC_COLUMNS = [ ⏐ "study_id", "config_signature", "unit_id", "analysis_year", "metric_name", ⏐ "metric_value", "value_unit", "calculation_time", "missing_reason", ⏐ ]`

**语法和执行含义：** 列表依次保存研究标识、输入签名、分部、分析年度、指标名、数值、单位、计算时刻、缺失原因。

**为什么这样写：** 顺序匹配第二模块建立的 metric_results 表，后面参数和 SQL 统一使用它。

---

**第 15—16 行｜定义本次输入签名函数**

对应语句：`def make_run_signature(config, financial_df): ⏐ """Identify the settings, calculation version and selected source records."""`

**语法和执行含义：** make_run_signature 接收配置对象与财务 DataFrame，返回文本标识。三引号只是函数用途说明。

**为什么这样写：** 让结果能追溯到选用的研究设置、源记录和计算规则；这里并不读取或写数据库。

---

**第 17 行｜让源记录顺序稳定**

对应语句：`records = financial_df.sort_values(["unit_id", "fiscal_year"]).to_dict("records")`

**语法和执行含义：** 先按 unit_id 与 fiscal_year 排序，再 to_dict("records") 转为行字典列表，保存到 records。

**为什么这样写：** 同一组源数据仅换了行排列时，不应生成不同标识。

---

**第 18—22 行｜组合需要标识的全部内容**

对应语句：`payload = { ⏐ "calculation_version": CALCULATION_VERSION, ⏐ "settings": config.to_dict(), ⏐ "financial_records": records, ⏐ }`

**语法和执行含义：** payload 是普通字典，包含公式版本、config.to_dict() 返回的设置，以及排序后的源记录。

**为什么这样写：** 不仅包含基期和公司，还包含实际数值与来源；任一输入变化都可以得到不同签名。

---

**第 23 行｜把字典转换成稳定的文本**

对应语句：`text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`

**语法和执行含义：** json.dumps 返回字符串；sort_keys=True 按字典键排序，separators 去除不必要空白，ensure_ascii=True 用 ASCII 表示。

**为什么这样写：** 防止字典键排列或排版空格导致同一内容生成不同标识。它与把文件写入磁盘的 json.dump 不同。

---

**第 24 行｜生成并返回 SHA256 文本**

对应语句：`return hashlib.sha256(text.encode("utf-8")).hexdigest()`

**语法和执行含义：** encode("utf-8") 将文本转换成字节；sha256 接收字节；hexdigest 输出十六进制文字，最后 return 交回。

**为什么这样写：** 数据库已有字段名 config_signature，本版实际保存的是配置、数据和公式版本的共同签名，不只是配置本身。

---

## Cell 04: Define the Metric Calculator

### 完整代码

```python
# Cell 04: Define the Metric Calculator

class MetricCalculator:
    """Keep study settings while using the same formulas for every business unit."""

    def __init__(self, config):
        self.config = config

    def build_analysis_frame(self, financial_df):
        records_by_key = {}
        for row in financial_df.to_dict("records"):
            records_by_key[(row["unit_id"], row["fiscal_year"])] = row
        rows = []
        for period in self.config.periods:
            stage = period.get("comparison_stage")
            if not isinstance(stage, str) or not stage.strip():
                raise ValueError("Every analysis period needs a comparison_stage label.")
            for unit in self.config.business_units:
                key = (unit["unit_id"], period["fiscal_years"][unit["unit_id"]])
                row = records_by_key[key].copy()
                row["analysis_year"] = period["analysis_year"]
                row["comparison_stage"] = stage.strip()
                rows.append(row)
        return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)

    def calculate(self, analysis_df):
        rows = []
        for unit in self.config.business_units:
            unit_df = analysis_df[analysis_df["unit_id"] == unit["unit_id"]]
            unit_df = unit_df.sort_values("analysis_year")
            base_rows = unit_df[unit_df["analysis_year"] == self.config.index_base_year]
            if len(base_rows) != 1:
                raise ValueError(f"Exactly one base-year record is required: {unit['unit_id']}")
            base_sales = float(base_rows.iloc[0]["net_sales_usd_m"])
            previous_sales = None
            for source_row in unit_df.to_dict("records"):
                row = source_row.copy()
                sales = float(row["net_sales_usd_m"])
                income = float(row["operating_income_usd_m"])
                row["previous_sales_usd_m"] = previous_sales
                for metric in self.config.metrics:
                    column = METRIC_SPECS[metric]["column"]
                    if metric == "sales_growth":
                        if previous_sales is None:
                            value = None
                        else:
                            value = (sales / previous_sales - 1) * 100
                    elif metric == "operating_margin":
                        value = income / sales * 100
                    elif metric == "sales_index":
                        value = sales / base_sales * 100
                    row[column] = value
                rows.append(row)
                previous_sales = sales
        return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)

    def to_metric_records(self, analysis_df, signature, calculation_time):
        records = []
        for row in analysis_df.to_dict("records"):
            for metric in self.config.metrics:
                spec = METRIC_SPECS[metric]
                value = row[spec["column"]]
                reason = None
                if pd.isna(value):
                    value = None
                    reason = "No previous analysis-year record in the study."
                else:
                    value = float(value)
                record = {
                    "study_id": self.config.study_id,
                    "config_signature": signature,
                    "unit_id": row["unit_id"],
                    "analysis_year": row["analysis_year"],
                    "metric_name": metric,
                    "metric_value": value,
                    "value_unit": spec["unit"],
                    "calculation_time": calculation_time,
                    "missing_reason": reason,
                }
                records.append(record)
        return pd.DataFrame(records, columns=METRIC_COLUMNS)
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 04: Define the Metric Calculator`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜定义指标计算类**

对应语句：`class MetricCalculator: ⏐ """Keep study settings while using the same formulas for every business unit."""`

**语法和执行含义：** class 定义 MetricCalculator，执行定义时没有开始计算。类说明强调相同公式用于所有分部。

**为什么这样写：** 保存本次 config 供多个方法复用，研究公司名称不写成计算分支。

---

**第 6—7 行｜初始化并保存配置**

对应语句：`def __init__(self, config): ⏐ self.config = config`

**语法和执行含义：** 创建 MetricCalculator(config) 时自动调用 __init__。self 是当前对象，self.config 保存传入的 config 引用。

**为什么这样写：** 后面各方法能使用同一基期、年度映射与指标列表；初始化不连接数据库。

---

**第 9 行｜定义年度映射方法**

对应语句：`def build_analysis_frame(self, financial_df):`

**语法和执行含义：** build_analysis_frame 接收数据库查询得到的 financial_df，返回增加分析年度与阶段的表。

**为什么这样写：** 数据库保留真实报告财年，如何配对属于本研究配置，不能在基础表中永久写死。

---

**第 10—12 行｜按分部财年建立查询字典**

对应语句：`records_by_key = {} ⏐ for row in financial_df.to_dict("records"): ⏐ records_by_key[(row["unit_id"], row["fiscal_year"])] = row`

**语法和执行含义：** 先创建空字典，再逐行生成 (unit_id, fiscal_year) 元组作为键，值为该行字典。

**为什么这样写：** 后面可以用配置直接找对应记录。输入已在 Cell 08 由 validate_records 拒绝重复及缺失，不能跳过那项检查。

---

**第 13 行｜准备分析行列表**

对应语句：`rows = []`

**语法和执行含义：** rows = [] 创建空列表，稍后每个时期每家分部各加入一行。

**为什么这样写：** 最后可一次构建 DataFrame，避免在循环中反复拼表。

---

**第 14—15 行｜从每个时期读取阶段标签**

对应语句：`for period in self.config.periods: ⏐ stage = period.get("comparison_stage")`

**语法和执行含义：** for 遍历 self.config.periods；get 取得 comparison_stage，没有该键时返回 None。

**为什么这样写：** 阶段由配置决定，普通函数不把疫情年份或英文阶段文字写成固定条件。

---

**第 16—17 行｜拒绝未填写的阶段**

对应语句：`if not isinstance(stage, str) or not stage.strip(): ⏐ raise ValueError("Every analysis period needs a comparison_stage label.")`

**语法和执行含义：** isinstance 要求 stage 是字符串；not stage.strip() 拒绝只有空格的标签。or 任一条件成立就抛出 ValueError，且非字符串时短路不调用 strip。

**为什么这样写：** 第一模块允许保存附加阶段字段，本模块要分组，所以这里明确要求每期有有效标签。

---

**第 18—19 行｜取得该分部对应的实际财年**

对应语句：`for unit in self.config.business_units: ⏐ key = (unit["unit_id"], period["fiscal_years"][unit["unit_id"]])`

**语法和执行含义：** 内层循环遍历分部。先读标识，再到 period 的 fiscal_years 映射查对应财年，两者组合为 key。

**为什么这样写：** 分析年度 2019 在配置中配对 Amazon 2019 与 Walmart 2020，不需要根据公司名称猜年份。

---

**第 20 行｜复制对应基础记录**

对应语句：`row = records_by_key[key].copy()`

**语法和执行含义：** records_by_key[key] 查询行字典，copy 创建新字典，赋给 row。

**为什么这样写：** 下面增加研究字段时不改变原始查询表或源记录索引。

---

**第 21—22 行｜增加分析年度和阶段**

对应语句：`row["analysis_year"] = period["analysis_year"] ⏐ row["comparison_stage"] = stage.strip()`

**语法和执行含义：** 两个字典赋值新增 analysis_year、comparison_stage；阶段 strip 去掉外围空格。

**为什么这样写：** 保留 fiscal_year 同时加入统一比较年度，实际财年与分析年度是两个不同概念。

---

**第 23—24 行｜收集并返回年度分析表**

对应语句：`rows.append(row) ⏐ return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)`

**语法和执行含义：** append 将扩展记录加入列表；循环完用 pd.DataFrame 构表，按分部和分析年度排序，再重置索引并 return。

**为什么这样写：** 本案例由十六个基础字段增加两个研究字段，成为十二行十八列的映射表。

---

**第 26—27 行｜定义计算方法及输出容器**

对应语句：`def calculate(self, analysis_df): ⏐ rows = []`

**语法和执行含义：** calculate 接收已经映射好的 analysis_df，创建 rows 列表保存计算后的记录。

**为什么这样写：** 计算结果由方法返回，不覆盖数据库的基础字段。

---

**第 28—29 行｜每家分部单独计算**

对应语句：`for unit in self.config.business_units: ⏐ unit_df = analysis_df[analysis_df["unit_id"] == unit["unit_id"]]`

**语法和执行含义：** 外层 for 遍历配置分部；analysis_df["unit_id"] == unit["unit_id"] 得到布尔 Series，外层方括号按 True 筛选行。

**为什么这样写：** 同比和指数必须使用该分部自己的销售额，不能把另一家上一行当成前一年。

---

**第 30 行｜按年份排列单家记录**

对应语句：`unit_df = unit_df.sort_values("analysis_year")`

**语法和执行含义：** sort_values("analysis_year") 将该分部从早到晚排序。

**为什么这样写：** 下面逐行更新 previous_sales，必须按时间顺序进行。

---

**第 31—33 行｜定位配置中的基期行**

对应语句：`base_rows = unit_df[unit_df["analysis_year"] == self.config.index_base_year] ⏐ if len(base_rows) != 1: ⏐ raise ValueError(f"Exactly one base-year record is required: {unit['unit_id']}")`

**语法和执行含义：** 布尔筛选选中 analysis_year 等于 index_base_year 的行；len 要求恰好一行，否则 raise。

**为什么这样写：** 通用公式不写死 2019。缺少或重复基期就不能正确建立指数。

---

**第 34 行｜读取本分部基期销售额**

对应语句：`base_sales = float(base_rows.iloc[0]["net_sales_usd_m"])`

**语法和执行含义：** iloc[0] 按位置取得基期第一行，再用字段名取销售额，float 转为普通浮点数。

**为什么这样写：** 整个分部各年的销售指数都除以同一个基期值；基础检查已要求销售额为正。

---

**第 35 行｜在每家分部开始时重设前期值**

对应语句：`previous_sales = None`

**语法和执行含义：** previous_sales = None 放在分部循环内部、年度循环之前。

**为什么这样写：** 每家公司首年都没有样本内前一年，不能继承另一家最后一年的销售额。

---

**第 36—37 行｜按年取得并复制一行**

对应语句：`for source_row in unit_df.to_dict("records"): ⏐ row = source_row.copy()`

**语法和执行含义：** to_dict("records") 生成该分部行字典列表，for 逐年取 source_row，copy 给 row 一个独立字典。

**为什么这样写：** 后面添加金额前期值和指标列，保留输入映射表。

---

**第 38—39 行｜取得本期两个基础金额**

对应语句：`sales = float(row["net_sales_usd_m"]) ⏐ income = float(row["operating_income_usd_m"])`

**语法和执行含义：** 分别把净销售额与营业利润转为 float，保存到 sales、income。

**为什么这样写：** 三项公式共用同一期销售额；营业利润允许为负，不能使用绝对值。

---

**第 40 行｜保留当前行采用的前期销售额**

对应语句：`row["previous_sales_usd_m"] = previous_sales`

**语法和执行含义：** 把还未更新的 previous_sales 存入 row 的审查字段，首年为 None。

**为什么这样写：** 让你可以检查同比到底用了哪一个分母；它不是另外一项业务指标。

---

**第 41—42 行｜按配置选择要算的指标**

对应语句：`for metric in self.config.metrics: ⏐ column = METRIC_SPECS[metric]["column"]`

**语法和执行含义：** 遍历 self.config.metrics，查询 METRIC_SPECS 中该指标的输出列名。

**为什么这样写：** 换成只算营业利润率时，不创建另两项指标列，通用框架仍可使用。

---

**第 43—45 行｜首年同比保留缺失**

对应语句：`if metric == "sales_growth": ⏐ if previous_sales is None: ⏐ value = None`

**语法和执行含义：** 指标是 sales_growth 时，检查 previous_sales 是否为 None；如果是，将 value 设为 None。

**为什么这样写：** 当前研究从 2019 开始，没有 2018 记录，所以两家 2019 同比不可计算，不能填成 0%。

---

**第 46—47 行｜有前一年时计算同比**

对应语句：`else: ⏐ value = (sales / previous_sales - 1) * 100`

**语法和执行含义：** else 中销售额除以前一年销售额，减一，再乘 100。先括号内运算，再转成百分比数值。

**为什么这样写：** 例如从 100 增至 120，结果 (120/100-1)*100 为 20，即 20%。这是单年同比，不是累计增长或 CAGR。

---

**第 48—49 行｜计算营业利润率**

对应语句：`elif metric == "operating_margin": ⏐ value = income / sales * 100`

**语法和执行含义：** elif 表示前面的指标分支未匹配时再判断；营业利润除以当期净销售额，再乘 100。

**为什么这样写：** 例如利润 8、销售 100，结果 8%。利润为负时，利润率也应为负。

---

**第 50—51 行｜计算销售指数**

对应语句：`elif metric == "sales_index": ⏐ value = sales / base_sales * 100`

**语法和执行含义：** 当指标为 sales_index，当前销售额除以本分部基期销售额，再乘 100。

**为什么这样写：** 基期自身必为 100。指数 150 表示销售额为基期 1.5 倍，不表示同比增长 150%。

---

**第 52 行｜把本次指标放入对应列**

对应语句：`row[column] = value`

**语法和执行含义：** row[column] = value 使用变量中的列名作为字典键。

**为什么这样写：** 只需一条赋值就能保存不同指标，不必给每家公司的列各写一套代码。

---

**第 53—54 行｜保存完整年度行再更新前期值**

对应语句：`rows.append(row) ⏐ previous_sales = sales`

**语法和执行含义：** 退出指标循环后 append 一行；再令 previous_sales = sales，供下一个年度使用。

**为什么这样写：** 先算本期再更新，顺序相反会用本期除以本期而错误得到零增长。阶段变化时不重设前期值，所以 2022 同比仍与 2021 比较。

---

**第 55 行｜返回含指标的年度表**

对应语句：`return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)`

**语法和执行含义：** 用列表建表、按身份排序、重置索引并 return。

**为什么这样写：** 本案例保留十八个映射字段，再加前期销售额和三项指标，共十二行二十二列。

---

**第 57—58 行｜定义宽表转长表的方法**

对应语句：`def to_metric_records(self, analysis_df, signature, calculation_time): ⏐ records = []`

**语法和执行含义：** 接收年度表、输入签名和计算时刻，创建 records 空列表。

**为什么这样写：** 年度宽表一行有三项指标，数据库长表一行只存一个指标。

---

**第 59—61 行｜每条年度记录展开多个指标**

对应语句：`for row in analysis_df.to_dict("records"): ⏐ for metric in self.config.metrics: ⏐ spec = METRIC_SPECS[metric]`

**语法和执行含义：** 外层循环每个分部年度，内层循环配置指标，再取该指标的 spec 字典。

**为什么这样写：** 十二条年度记录乘三项指标，得到三十六条结果，增加或减少指标通过配置决定。

---

**第 62—63 行｜取得指标值并先设无缺失原因**

对应语句：`value = row[spec["column"]] ⏐ reason = None`

**语法和执行含义：** 通过 spec 的 column 查 row 中的指标；reason 初始化为 None。

**为什么这样写：** 正常可计算结果不应带缺失原因，缺失情况下面单独处理。

---

**第 64—66 行｜统一 pandas 的缺失表示**

对应语句：`if pd.isna(value): ⏐ value = None ⏐ reason = "No previous analysis-year record in the study."`

**语法和执行含义：** pd.isna 同时识别 None、NaN 等；缺失值统一为 None，并设置首年缺少前一年记录的英文原因。

**为什么这样写：** 当前合法缺失仅是首年同比；后面的验证会拒绝其他年份或其他指标的缺失，避免误用这条原因。

---

**第 67—68 行｜统一有效指标数值**

对应语句：`else: ⏐ value = float(value)`

**语法和执行含义：** else 对非缺失指标用 float 转为普通浮点数。

**为什么这样写：** 后面验证有限性并写入 SQLite REAL，避免把数值格式化成带百分号的字符串。

---

**第 69—79 行｜建立单个指标结果字典**

对应语句：`record = { ⏐ "study_id": self.config.study_id, ⏐ "config_signature": signature, ⏐ "unit_id": row["unit_id"], ⏐ "analysis_year": row["analysis_year"], ⏐ "metric_name": metric, ⏐ "metric_value": value, ⏐ "value_unit": spec["unit"], ⏐ "calculation_time": calculation_time, ⏐ "missing_reason": reason, ⏐ }`

**语法和执行含义：** 依次填写九个字段：研究标识、当前签名、分部、分析年度、指标名、数值、单位、计算时刻和原因。字段名与 METRIC_COLUMNS 一致。

**为什么这样写：** 一行能独立识别本次哪个对象哪年的哪个指标，也能解释为什么某个值缺失。

---

**第 80—81 行｜收集结果并规定列序**

对应语句：`records.append(record) ⏐ return pd.DataFrame(records, columns=METRIC_COLUMNS)`

**语法和执行含义：** append 收集一条长记录；最后 pd.DataFrame(records, columns=METRIC_COLUMNS) 按固定九列顺序建表并 return。

**为什么这样写：** 方便 SQL 参数、导出和回读核对采用一致接口。

---

## Cell 05: Define Metric Validation

### 完整代码

```python
# Cell 05: Define Metric Validation

def validate_metric_records(metric_df, analysis_df, config, signature):
    """Check exact metric coverage, missing growth and base-year indexes."""
    expected_keys = set()
    expected_values = {}
    first_year = config.periods[0]["analysis_year"]
    for row in analysis_df.to_dict("records"):
        for metric in config.metrics:
            key = (row["unit_id"], row["analysis_year"], metric)
            expected_keys.add(key)
            expected_values[key] = row[METRIC_SPECS[metric]["column"]]
    if metric_df.duplicated(["unit_id", "analysis_year", "metric_name"]).any():
        raise ValueError("Duplicate metric records were found.")
    actual_keys = set()
    for row in metric_df.to_dict("records"):
        key = (row["unit_id"], row["analysis_year"], row["metric_name"])
        actual_keys.add(key)
        if key not in expected_values:
            raise ValueError(f"Unexpected metric record: {key}")
        metric = row["metric_name"]
        if row["study_id"] != config.study_id or row["config_signature"] != signature:
            raise ValueError(f"Metric run identity does not match: {key}")
        if row["value_unit"] != METRIC_SPECS[metric]["unit"]:
            raise ValueError(f"Metric unit does not match: {key}")
        if not str(row["calculation_time"]).strip():
            raise ValueError(f"Missing calculation time: {key}")
        value = row["metric_value"]
        expected = expected_values[key]
        if metric == "sales_growth" and row["analysis_year"] == first_year:
            if not pd.isna(value) or pd.isna(row["missing_reason"]):
                raise ValueError(f"First-year growth must be missing with a reason: {key}")
        else:
            if pd.isna(value) or not math.isfinite(float(value)):
                raise ValueError(f"A finite metric value is required: {key}")
            if not pd.isna(row["missing_reason"]):
                raise ValueError(f"Available metric must not have a missing reason: {key}")
            if pd.isna(expected) or not math.isclose(float(value), float(expected), rel_tol=1e-12, abs_tol=1e-10):
                raise ValueError(f"Metric value does not match annual calculations: {key}")
        if metric == "sales_index" and row["analysis_year"] == config.index_base_year:
            if not math.isclose(float(value), 100.0, abs_tol=1e-10):
                raise ValueError(f"The configured base-year sales index must be 100: {key}")
    if actual_keys != expected_keys:
        raise ValueError("Metric records do not cover exactly the configured analysis.")
    if len(metric_df) != config.get_observation_count() * len(config.metrics):
        raise ValueError("Metric row count does not match the configured study.")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 05: Define Metric Validation`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜定义长结果表检查函数**

对应语句：`def validate_metric_records(metric_df, analysis_df, config, signature): ⏐ """Check exact metric coverage, missing growth and base-year indexes."""`

**语法和执行含义：** 四个参数分别提供待检查长表、年度计算表、研究配置和当前签名；通过不返回新表，失败抛出异常。

**为什么这样写：** 检查长表展开、身份、单位和缺失规则，调用时不把 None 返回值赋给原 DataFrame。

---

**第 5—7 行｜准备期望身份和值**

对应语句：`expected_keys = set() ⏐ expected_values = {} ⏐ first_year = config.periods[0]["analysis_year"]`

**语法和执行含义：** set 用于覆盖名单，字典用于按身份查年度值；config.periods[0] 取得研究的第一期，再取 analysis_year。

**为什么这样写：** 首年缺失规则依据研究起点，不与销售指数的 index_base_year 混为一谈；基期换成 2021，首年仍是 2019。

---

**第 8—12 行｜由年度表生成正确名单**

对应语句：`for row in analysis_df.to_dict("records"): ⏐ for metric in config.metrics: ⏐ key = (row["unit_id"], row["analysis_year"], metric) ⏐ expected_keys.add(key) ⏐ expected_values[key] = row[METRIC_SPECS[metric]["column"]]`

**语法和执行含义：** 嵌套循环每个年度和指标，以 (unit_id, analysis_year, metric) 为身份；add 保存身份，expected_values 保存对应宽表列的值。

**为什么这样写：** 检查展开后的长表是否与年度计算结果逐项对应，而不是只看总行数。

---

**第 13—14 行｜拒绝重复指标身份**

对应语句：`if metric_df.duplicated(["unit_id", "analysis_year", "metric_name"]).any(): ⏐ raise ValueError("Duplicate metric records were found.")`

**语法和执行含义：** duplicated 用分部、分析年度、指标名组成的组合检查重复，any 发现一条就 raise。

**为什么这样写：** 同一年度有三项指标是合法的，但同一年度同一指标重复不合法。

---

**第 15—18 行｜收集实际长表身份**

对应语句：`actual_keys = set() ⏐ for row in metric_df.to_dict("records"): ⏐ key = (row["unit_id"], row["analysis_year"], row["metric_name"]) ⏐ actual_keys.add(key)`

**语法和执行含义：** 创建 actual_keys，遍历 metric_df 的行字典，再组合当前身份并加入集合。

**为什么这样写：** 循环结束后与期望集合比较，不依赖原有排列顺序。

---

**第 19—21 行｜确认当前指标属于期望名单**

对应语句：`if key not in expected_values: ⏐ raise ValueError(f"Unexpected metric record: {key}") ⏐ metric = row["metric_name"]`

**语法和执行含义：** 身份不存在于 expected_values 就报错；存在时取得当前 metric_name，供下面查询单位与规则。

**为什么这样写：** 防止多出未配置公司、年份或指标，也避免查询未知指标规则。

---

**第 22—23 行｜核对研究与输入版本**

对应语句：`if row["study_id"] != config.study_id or row["config_signature"] != signature: ⏐ raise ValueError(f"Metric run identity does not match: {key}")`

**语法和执行含义：** 两个 != 判断通过 or 连接，study_id 或 config_signature 任一不同就 raise。

**为什么这样写：** 数值看似合理也可能属于另一次配置或源数据，本次结果身份必须一致。

---

**第 24—25 行｜核对数值单位**

对应语句：`if row["value_unit"] != METRIC_SPECS[metric]["unit"]: ⏐ raise ValueError(f"Metric unit does not match: {key}")`

**语法和执行含义：** METRIC_SPECS 根据指标名查询应有 unit，与实际 value_unit 比较。

**为什么这样写：** 百分比与指数含义不同，不能把 sales_index 的 100 当成百分比增长。

---

**第 26—27 行｜确认有计算时刻文字**

对应语句：`if not str(row["calculation_time"]).strip(): ⏐ raise ValueError(f"Missing calculation time: {key}")`

**语法和执行含义：** 将 calculation_time 转文字、去空白，空文本时抛出错误。实际正常值由 Cell 09 的 UTC 时间生成。

**为什么这样写：** 结果有计算记录；这一句主要检查空文本，不是一套对任意时间输入的完整校验。

---

**第 28—29 行｜取实际值和对应年度值**

对应语句：`value = row["metric_value"] ⏐ expected = expected_values[key]`

**语法和执行含义：** value 来自本条长记录，expected 通过身份从期望字典查询。

**为什么这样写：** 两种表的值需要一致，后面按缺失和正常结果分别比较。

---

**第 30—32 行｜只有首年同比允许缺失**

对应语句：`if metric == "sales_growth" and row["analysis_year"] == first_year: ⏐ if not pd.isna(value) or pd.isna(row["missing_reason"]): ⏐ raise ValueError(f"First-year growth must be missing with a reason: {key}")`

**语法和执行含义：** and 要求同时为销售增长和研究首年。pd.isna 判断值或原因是否缺失：数值不是缺失，或者原因缺失，都报错。

**为什么这样写：** 样本没有上一年时保留缺失并注明原因，不能用 0 代替。原因文本由展开方法生成。

---

**第 33—35 行｜其他结果必须是有限数值**

对应语句：`else: ⏐ if pd.isna(value) or not math.isfinite(float(value)): ⏐ raise ValueError(f"A finite metric value is required: {key}")`

**语法和执行含义：** else 处理所有非首年同比项。pd.isna 为真或 float 后不是有限数都会 raise，or 的短路避免先对缺失做不必要转换。

**为什么这样写：** 不能把后续年份或利润率的异常缺失当作首年缺数据处理。有限负利润率允许。

---

**第 36—37 行｜有效值不应附带缺失原因**

对应语句：`if not pd.isna(row["missing_reason"]): ⏐ raise ValueError(f"Available metric must not have a missing reason: {key}")`

**语法和执行含义：** not pd.isna 检查 missing_reason 是否实际存在；可计算值带原因时拒绝。

**为什么这样写：** 避免一条记录同时声称“有结果”和“因缺失无法算”。

---

**第 38—39 行｜比较长表与年度表的金额**

对应语句：`if pd.isna(expected) or not math.isclose(float(value), float(expected), rel_tol=1e-12, abs_tol=1e-10): ⏐ raise ValueError(f"Metric value does not match annual calculations: {key}")`

**语法和执行含义：** isclose 允许很小的浮点误差；rel_tol 是相对容差，abs_tol 是接近零时的绝对容差。expected 缺失或不接近时 raise。

**为什么这样写：** 检查转成长表没有错列或错年。这是两种表示的一致性核对，公式正确性另用独立计算验证。

---

**第 40—42 行｜核对每家配置基期指数为一百**

对应语句：`if metric == "sales_index" and row["analysis_year"] == config.index_base_year: ⏐ if not math.isclose(float(value), 100.0, abs_tol=1e-10): ⏐ raise ValueError(f"The configured base-year sales index must be 100: {key}")`

**语法和执行含义：** 检查当前为销售指数且分析年度等于基期时，再 isclose(value,100)；不符合则报错。

**为什么这样写：** 基期各自除以自身应得到 100，是一项直接的公式约束。

---

**第 43—44 行｜循环结束后核对完整覆盖**

对应语句：`if actual_keys != expected_keys: ⏐ raise ValueError("Metric records do not cover exactly the configured analysis.")`

**语法和执行含义：** 集合比较要求实际与期望身份完全相同，不同则 raise；缩进已退回到逐行循环外。

**为什么这样写：** 避免缺一项、多一项或换错年份，仅总数相同仍不能通过。

---

**第 45—46 行｜核对长记录数量**

对应语句：`if len(metric_df) != config.get_observation_count() * len(config.metrics): ⏐ raise ValueError("Metric row count does not match the configured study.")`

**语法和执行含义：** 配置的年度记录数乘选定指标数，与 len(metric_df) 比较。

**为什么这样写：** 当前十二乘三为三十六；仅选择一个指标时自动变成十二，不写死数量。

---

## Cell 06: Define Metric Storage and Read-Back Verification

### 完整代码

```python
# Cell 06: Define Metric Storage and Read-Back Verification

def save_metric_results(database, config, metric_df, signature):
    """Replace this run atomically without mixing source versions."""
    columns_sql = ", ".join(METRIC_COLUMNS)
    placeholders = ", ".join(["?"] * len(METRIC_COLUMNS))
    with database.connection:
        current_sources = database.read_selected_records(config)
        if make_run_signature(config, current_sources) != signature:
            raise ValueError("Source records changed. Reload and recalculate before saving.")
        database.connection.execute(
            "DELETE FROM metric_results WHERE study_id = ? AND config_signature = ?",
            (config.study_id, signature),
        )
        for row in metric_df.to_dict("records"):
            values = []
            for column in METRIC_COLUMNS:
                value = row[column]
                if pd.isna(value):
                    value = None
                values.append(value)
            database.connection.execute(
                f"INSERT INTO metric_results ({columns_sql}) VALUES ({placeholders})",
                tuple(values),
            )
    return len(metric_df)


def read_metric_results(database, config, signature):
    """Query only the selected study and input signature."""
    query = """
        SELECT study_id, config_signature, unit_id, analysis_year, metric_name,
               metric_value, value_unit, calculation_time, missing_reason
        FROM metric_results
        WHERE study_id = ? AND config_signature = ?
        ORDER BY unit_id, analysis_year, metric_name
    """
    return pd.read_sql_query(query, database.connection, params=[config.study_id, signature])


def verify_metric_copy(metric_df, stored_metric_df):
    """Compare all persisted fields, treating missing values consistently."""
    keys = ["unit_id", "analysis_year", "metric_name"]
    left = metric_df.sort_values(keys).reset_index(drop=True).to_dict("records")
    right = stored_metric_df.sort_values(keys).reset_index(drop=True).to_dict("records")
    if len(left) != len(right):
        raise ValueError("Persisted metric count does not match.")
    for left_row, right_row in zip(left, right):
        for column in METRIC_COLUMNS:
            first = left_row[column]
            second = right_row[column]
            if pd.isna(first) and pd.isna(second):
                continue
            if pd.isna(first) or pd.isna(second):
                raise ValueError(f"Persisted missing status differs: {column}")
            if column == "metric_value":
                if not math.isclose(float(first), float(second), rel_tol=1e-12, abs_tol=1e-10):
                    raise ValueError("Persisted metric value differs.")
            elif first != second:
                raise ValueError(f"Persisted metric metadata differs: {column}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 06: Define Metric Storage and Read-Back Verification`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜定义结果保存函数**

对应语句：`def save_metric_results(database, config, metric_df, signature): ⏐ """Replace this run atomically without mixing source versions."""`

**语法和执行含义：** database 提供已连接对象，config 和 signature 指定当前研究版本，metric_df 为已验证结果；成功返回保存行数。

**为什么这样写：** 使用第二模块的连接和已建立结果表，不增加新 ORM 或数据库类。

---

**第 5—6 行｜准备固定列名和参数位置**

对应语句：`columns_sql = ", ".join(METRIC_COLUMNS) ⏐ placeholders = ", ".join(["?"] * len(METRIC_COLUMNS))`

**语法和执行含义：** join 连接九个字段名；["?"] 乘字段数生成九个问号再连接。

**为什么这样写：** 列名来自固定框架，实际结果通过参数传入 SQL，列序与值序一致。

---

**第 7 行｜对本次替换使用事务**

对应语句：`with database.connection:`

**语法和执行含义：** with 管理这一批 DML 写入，正常完成提交，异常回滚；它不自动关闭连接。

**为什么这样写：** 先删除再插入也必须作为一批操作，否则中途失败会丢失原结果。

---

**第 8—10 行｜保存前再确认源输入未变化**

对应语句：`current_sources = database.read_selected_records(config) ⏐ if make_run_signature(config, current_sources) != signature: ⏐ raise ValueError("Source records changed. Reload and recalculate before saving.")`

**语法和执行含义：** 重新查询配置所选基础数据，重新生成签名，与本次计算签名不同就报错。

**为什么这样写：** 发现读入后基础数据发生改变的情况，要求重新加载计算，不把旧计算结果保存成当前结果。这不是并发数据库的完整锁定方案。

---

**第 11—14 行｜只替换本研究本签名的结果**

对应语句：`database.connection.execute( ⏐ "DELETE FROM metric_results WHERE study_id = ? AND config_signature = ?", ⏐ (config.study_id, signature), ⏐ )`

**语法和执行含义：** DELETE 的 WHERE 同时筛选 study_id 和 config_signature；两个问号按元组顺序接收值。

**为什么这样写：** 相同输入重跑只替换本组记录，不增加重复行；其他研究或签名版本不被这条语句删除。

---

**第 15—18 行｜按固定顺序取每项值**

对应语句：`for row in metric_df.to_dict("records"): ⏐ values = [] ⏐ for column in METRIC_COLUMNS: ⏐ value = row[column]`

**语法和执行含义：** 逐行转为字典，为当前行创建 values 列表，内层循环按 METRIC_COLUMNS 依次取 row[column]。

**为什么这样写：** SQL 九个问号必须得到同样顺序的九个值，不能按临时字典排列猜顺序。

---

**第 19—21 行｜把 pandas 缺失统一成 SQL 可保存值**

对应语句：`if pd.isna(value): ⏐ value = None ⏐ values.append(value)`

**语法和执行含义：** pd.isna 检测 NaN、None 等，统一改成 Python None，再 append。

**为什么这样写：** sqlite3 将 None 保存为 SQL NULL。只依靠 pandas 的 NaN 不能清楚表达所有字段的缺失语义。

---

**第 22—25 行｜插入一条长结果**

对应语句：`database.connection.execute( ⏐ f"INSERT INTO metric_results ({columns_sql}) VALUES ({placeholders})", ⏐ tuple(values), ⏐ )`

**语法和执行含义：** f-string 放入固定列名与问号文本，tuple(values) 作为参数传入 execute。

**为什么这样写：** 循环保存三十六行；字段值没有直接拼进 SQL 文本，主键和外键继续保护结构。

---

**第 26 行｜提交后返回本次行数**

对应语句：`return len(metric_df)`

**语法和执行含义：** return 在 with 块之外，正常提交后把 len(metric_df) 交给调用者。

**为什么这样写：** 这是本次签名的保存数，不是数据库所有版本的累计行数。

---

**第 29—31 行｜定义查询函数及 SQL 文本**

对应语句：`def read_metric_results(database, config, signature): ⏐ """Query only the selected study and input signature.""" ⏐ query = """`

**语法和执行含义：** read_metric_results 接收连接、配置和签名，三引号开始 SQL 字符串。

**为什么这样写：** 查询入口必须明确当前研究和输入版本，避免混合旧结果。

---

**第 32—34 行｜选择九个结果字段**

对应语句：`SELECT study_id, config_signature, unit_id, analysis_year, metric_name, ⏐ metric_value, value_unit, calculation_time, missing_reason ⏐ FROM metric_results`

**语法和执行含义：** SELECT 按 METRIC_COLUMNS 相同顺序取全部字段，FROM 指定 metric_results 表。

**为什么这样写：** 回读包括计算时间、原因等，不只读取业务数值。

---

**第 35—37 行｜筛选版本并稳定排序**

对应语句：`WHERE study_id = ? AND config_signature = ? ⏐ ORDER BY unit_id, analysis_year, metric_name ⏐ """`

**语法和执行含义：** WHERE 两个条件用 AND 同时满足，ORDER BY 按分部、年度、指标排序；三引号结束字符串。

**为什么这样写：** 数据库可能保留其他签名版本，本次查询仍只返回对应三十六行。

---

**第 38 行｜查询并直接返回 DataFrame**

对应语句：`return pd.read_sql_query(query, database.connection, params=[config.study_id, signature])`

**语法和执行含义：** pd.read_sql_query 接收 SQL、连接和两个 params 值，输出 DataFrame，再 return。

**为什么这样写：** 数据来自 SQLite 保存结果，不是 metric_df 的别名。

---

**第 41—43 行｜定义回读比较与排序身份**

对应语句：`def verify_metric_copy(metric_df, stored_metric_df): ⏐ """Compare all persisted fields, treating missing values consistently.""" ⏐ keys = ["unit_id", "analysis_year", "metric_name"]`

**语法和执行含义：** verify_metric_copy 接收保存前后两表，keys 规定分部、分析年度和指标的排序规则。

**为什么这样写：** 每年有多个指标，不能只按分部与年排序而遗漏指标身份。

---

**第 44—45 行｜把两边都整理成行字典列表**

对应语句：`left = metric_df.sort_values(keys).reset_index(drop=True).to_dict("records") ⏐ right = stored_metric_df.sort_values(keys).reset_index(drop=True).to_dict("records")`

**语法和执行含义：** sort_values 和 reset_index 统一位置，再 to_dict("records") 生成 left、right 列表。

**为什么这样写：** 便于用普通 for 和字典逐字段比较；不修改传入 DataFrame。

---

**第 46—47 行｜先拒绝数量不一致**

对应语句：`if len(left) != len(right): ⏐ raise ValueError("Persisted metric count does not match.")`

**语法和执行含义：** len(left) 和 len(right) 是行列表长度，不同就 raise。

**为什么这样写：** 下面 zip 只遍历较短的一边，因此必须先确认数量一致，防止漏掉多出来的行。

---

**第 48—51 行｜每对对应记录逐列比较**

对应语句：`for left_row, right_row in zip(left, right): ⏐ for column in METRIC_COLUMNS: ⏐ first = left_row[column] ⏐ second = right_row[column]`

**语法和执行含义：** zip 配对两边同一位置记录；内层遍历九个字段，分别取 first 和 second。

**为什么这样写：** 核对业务值、身份、单位、计算时刻与原因，逐字段有明确上下文。

---

**第 52—53 行｜两边都缺失时进入下一字段**

对应语句：`if pd.isna(first) and pd.isna(second): ⏐ continue`

**语法和执行含义：** and 要求 first、second 都是缺失；continue 跳过当前字段剩余检查，继续内层 column 循环。

**为什么这样写：** Python None 与查询后的 NaN 可能表现不同，但都代表缺失，不应误报差异。

---

**第 54—55 行｜一边缺失时报告差异**

对应语句：`if pd.isna(first) or pd.isna(second): ⏐ raise ValueError(f"Persisted missing status differs: {column}")`

**语法和执行含义：** 到这里两边不是同时缺失，or 检查任意一边缺失则 raise。

**为什么这样写：** 防止数据库把缺失同比变成零，或丢失原本有效数值。

---

**第 56—58 行｜数值使用小容差比较**

对应语句：`if column == "metric_value": ⏐ if not math.isclose(float(first), float(second), rel_tol=1e-12, abs_tol=1e-10): ⏐ raise ValueError("Persisted metric value differs.")`

**语法和执行含义：** metric_value 字段用 float 转数值，再 math.isclose；超出容差就报错。

**为什么这样写：** 对 SQLite REAL 回读的小浮点表示差异保留合理容差，不放宽身份与来源元数据。

---

**第 59—60 行｜其他元数据精确一致**

对应语句：`elif first != second: ⏐ raise ValueError(f"Persisted metric metadata differs: {column}")`

**语法和执行含义：** elif 只处理非数值字段，first != second 则 raise 并提示字段。

**为什么这样写：** 研究标识、单位和计算时刻不能用数值容差掩盖错误；通过时函数默认返回 None。

---

## Cell 07: Define the Stage Summary

### 完整代码

```python
# Cell 07: Define the Stage Summary

def build_stage_summary(analysis_df, config):
    """Report unweighted means and the number of available annual values."""
    stages = []
    for period in config.periods:
        stage = period["comparison_stage"].strip()
        if stage not in stages:
            stages.append(stage)
    rows = []
    for unit in config.business_units:
        for stage in stages:
            selected = analysis_df[
                (analysis_df["unit_id"] == unit["unit_id"])
                & (analysis_df["comparison_stage"] == stage)
            ]
            years = []
            for year in selected["analysis_year"]:
                years.append(str(year))
            row = {
                "unit_id": unit["unit_id"],
                "company_name": unit["company_name"],
                "segment_name": unit["segment_name"],
                "comparison_stage": stage,
                "analysis_years": ", ".join(years),
                "record_count": len(selected),
            }
            for metric in config.metrics:
                column = METRIC_SPECS[metric]["column"]
                values = selected[column].dropna()
                row[column + "_valid_years"] = len(values)
                if len(values) == 0:
                    row[column + "_mean"] = None
                else:
                    row[column + "_mean"] = float(values.mean())
            rows.append(row)
    return pd.DataFrame(rows)
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 07: Define the Stage Summary`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜定义阶段汇总函数**

对应语句：`def build_stage_summary(analysis_df, config): ⏐ """Report unweighted means and the number of available annual values."""`

**语法和执行含义：** 输入年度计算表与配置，返回每家分部每个阶段的一行汇总。

**为什么这样写：** 比较阶段来自第一模块，汇总方法明确为有效年度的非加权算术平均。

---

**第 5—9 行｜按配置顺序收集阶段**

对应语句：`stages = [] ⏐ for period in config.periods: ⏐ stage = period["comparison_stage"].strip() ⏐ if stage not in stages: ⏐ stages.append(stage)`

**语法和执行含义：** 空列表 stages；逐期取阶段并 strip；列表没有该阶段时 append。

**为什么这样写：** 去掉重复标签同时保留首次出现顺序，阶段数量与名称不在函数中写死。

---

**第 10—12 行｜依次组合分部与阶段**

对应语句：`rows = [] ⏐ for unit in config.business_units: ⏐ for stage in stages:`

**语法和执行含义：** 准备 rows；外层遍历每家分部，内层遍历去重后的阶段。

**为什么这样写：** 当前两家乘三个阶段产生六行汇总，换相同接口的案例仍可复用。

---

**第 13—16 行｜同时筛选分部和阶段**

对应语句：`selected = analysis_df[ ⏐ (analysis_df["unit_id"] == unit["unit_id"]) ⏐ & (analysis_df["comparison_stage"] == stage) ⏐ ]`

**语法和执行含义：** 两个比较各产生一列布尔值，括号把条件包起来，& 对应位置同时为真时选中。这里不是 Python 对整个对象判断的 and。

**为什么这样写：** pandas 多行筛选要使用带括号的逐元素 &，不能直接用 and，否则会出现布尔值不明确的错误。

---

**第 17—19 行｜把参与年度变成文字列表**

对应语句：`years = [] ⏐ for year in selected["analysis_year"]: ⏐ years.append(str(year))`

**语法和执行含义：** years 是空列表；遍历所选 analysis_year，str 转文字并 append。

**为什么这样写：** 汇总中显示实际包含的年，便于核对阶段划分。

---

**第 20—27 行｜建立阶段身份与覆盖记录**

对应语句：`row = { ⏐ "unit_id": unit["unit_id"], ⏐ "company_name": unit["company_name"], ⏐ "segment_name": unit["segment_name"], ⏐ "comparison_stage": stage, ⏐ "analysis_years": ", ".join(years), ⏐ "record_count": len(selected), ⏐ }`

**语法和执行含义：** 字典保存分部标识、名称、阶段、逗号连接的年份和所选总行数。

**为什么这样写：** record_count 表示阶段有几个年度，并不代表每项指标有几个有效值，下面另计。

---

**第 28—30 行｜取得每项指标的有效年度值**

对应语句：`for metric in config.metrics: ⏐ column = METRIC_SPECS[metric]["column"] ⏐ values = selected[column].dropna()`

**语法和执行含义：** 按配置遍历指标、查列名，从所选 Series 调用 dropna 返回移除缺失后的新 Series。

**为什么这样写：** 不把首年缺失同比填零；这里的缺失已通过前面规则验证，不是静默删除未知错误。

---

**第 31 行｜保存有效年份数量**

对应语句：`row[column + "_valid_years"] = len(values)`

**语法和执行含义：** len(values) 数实际参与这项平均的值，键名在列名后拼 _valid_years。

**为什么这样写：** 2019 基线有一条年度记录，但增长率有效年份数为零，两种数量要区分。

---

**第 32—33 行｜没有有效值时平均仍缺失**

对应语句：`if len(values) == 0: ⏐ row[column + "_mean"] = None`

**语法和执行含义：** 若长度为零，_mean 字段保存 None。

**为什么这样写：** 完全缺失不能写成平均增长 0%，缺失保留到导出。

---

**第 34—35 行｜计算有效年度的算术平均**

对应语句：`else: ⏐ row[column + "_mean"] = float(values.mean())`

**语法和执行含义：** else 调用 Series.mean，结果转 float，保存到对应 _mean 字段。

**为什么这样写：** 每个有效年度权重相同。阶段平均增长不是 CAGR，平均年度利润率也不是合并利润除以合并销售额。

---

**第 36—37 行｜收集并返回阶段表**

对应语句：`rows.append(row) ⏐ return pd.DataFrame(rows)`

**语法和执行含义：** 每个分部阶段 append 一行，全部循环结束后用 DataFrame 构表并 return。

**为什么这样写：** 当前为六行十二列，包括三个指标的平均值和各自有效年份数。

---

## Cell 08: Query Source Records and Calculate Annual Metrics

### 完整代码

```python
# Cell 08: Query Source Records and Calculate Annual Metrics

database = DatabaseManager(DATABASE_FILE)
database.connect()
financial_df = database.read_selected_records(config)
validate_records(financial_df, config)

signature = make_run_signature(config, financial_df)
calculator = MetricCalculator(config)
analysis_df = calculator.build_analysis_frame(financial_df)
analysis_df = calculator.calculate(analysis_df)

print(f"Selected source records: {len(financial_df)}")
print(f"Annual metric rows: {len(analysis_df)}")
print(f"Input signature: {signature}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 08: Query Source Records and Calculate Annual Metrics`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜重新创建并连接数据库对象**

对应语句：`database = DatabaseManager(DATABASE_FILE) ⏐ database.connect()`

**语法和执行含义：** 使用第二模块已定义的 DatabaseManager，创建对象后调用 connect。

**为什么这样写：** 第二模块最后已关闭连接，本模块不能继续使用一个 None 连接；路径仍来自本次配置。

---

**第 5—6 行｜真实查询基础数据并检查**

对应语句：`financial_df = database.read_selected_records(config) ⏐ validate_records(financial_df, config)`

**语法和执行含义：** read_selected_records 从 SQLite 生成 financial_df，再调用第二模块 validate_records 检查研究覆盖、身份、金额与来源字段。

**为什么这样写：** 本模块不依赖第二模块遗留在内存的 clean_df；重新启动后也可以从持久化数据库计算。

---

**第 8 行｜标识当前采用输入**

对应语句：`signature = make_run_signature(config, financial_df)`

**语法和执行含义：** make_run_signature 对当前设置、版本、选中源记录生成文本并赋给 signature。

**为什么这样写：** 下面展开、保存、回读和清单都使用同一个输入身份。

---

**第 9 行｜创建本次计算器**

对应语句：`calculator = MetricCalculator(config)`

**语法和执行含义：** MetricCalculator(config) 自动初始化 self.config，得到对象 calculator。

**为什么这样写：** 配置内容与通用计算方法分开，创建对象本身不计算数值。

---

**第 10 行｜将真实财年映射为分析年度**

对应语句：`analysis_df = calculator.build_analysis_frame(financial_df)`

**语法和执行含义：** 调用 build_analysis_frame，返回增加 analysis_year 与 comparison_stage 的表，赋给 analysis_df。

**为什么这样写：** 先得到统一比较年份，再按年份排序计算；真实 fiscal_year 仍保留。

---

**第 11 行｜计算并接收扩展后的年度表**

对应语句：`analysis_df = calculator.calculate(analysis_df)`

**语法和执行含义：** calculate 返回增加前期销售额和选定指标的表，用同一变量 analysis_df 接收。

**为什么这样写：** 输入 financial_df 不变；最终每家每年仍一行，三项指标在列中。

---

**第 13—15 行｜显示数量和输入身份**

对应语句：`print(f"Selected source records: {len(financial_df)}") ⏐ print(f"Annual metric rows: {len(analysis_df)}") ⏐ print(f"Input signature: {signature}")`

**语法和执行含义：** 分别显示基础记录数、年度指标行数和签名；没有把哈希当成财务指标。

**为什么这样写：** 当前应是十二条基础记录和十二条年度行。三十六条长结果在下一格展开。

---

## Cell 09: Build and Validate the Long Metric Records

### 完整代码

```python
# Cell 09: Build and Validate the Long Metric Records

calculation_time = datetime.now(timezone.utc).isoformat(timespec="seconds")
metric_df = calculator.to_metric_records(analysis_df, signature, calculation_time)
validate_metric_records(metric_df, analysis_df, config, signature)

display_columns = ["unit_id", "analysis_year", "comparison_stage"]
for metric in config.metrics:
    display_columns.append(METRIC_SPECS[metric]["column"])
annual_view = analysis_df[display_columns].sort_values(["analysis_year", "unit_id"])

print("Annual metric checks passed.")
print(annual_view.round(4).to_string(index=False))
print(f"Long metric records: {len(metric_df)}")
print(f"Missing metric values: {int(metric_df['metric_value'].isna().sum())}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 09: Build and Validate the Long Metric Records`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜记录当前 UTC 计算时间**

对应语句：`calculation_time = datetime.now(timezone.utc).isoformat(timespec="seconds")`

**语法和执行含义：** datetime.now(timezone.utc) 取得带 UTC 时区的时间；isoformat(timespec="seconds") 转成保留到秒的 ISO 字符串。

**为什么这样写：** 所有本次指标使用同一个时刻，不让每一行单独生成不同时间。

---

**第 4—5 行｜展开长记录并校验**

对应语句：`metric_df = calculator.to_metric_records(analysis_df, signature, calculation_time) ⏐ validate_metric_records(metric_df, analysis_df, config, signature)`

**语法和执行含义：** to_metric_records 返回长表，validate_metric_records 检查覆盖、版本、单位、缺失及年度值一致性。

**为什么这样写：** 先检查后写库，当前产生三十六行，合法缺失只含两条首年同比。

---

**第 7—9 行｜准备需要显示的列**

对应语句：`display_columns = ["unit_id", "analysis_year", "comparison_stage"] ⏐ for metric in config.metrics: ⏐ display_columns.append(METRIC_SPECS[metric]["column"])`

**语法和执行含义：** 先用列表放身份和阶段，再逐个把配置指标对应列名 append。

**为什么这样写：** 只显示当前配置选定的指标，不硬编码三个输出列一定存在。

---

**第 10 行｜将两家按同一年度排列**

对应语句：`annual_view = analysis_df[display_columns].sort_values(["analysis_year", "unit_id"])`

**语法和执行含义：** 按列列表取视图，再先按 analysis_year、后按 unit_id 排序，赋给 annual_view。

**为什么这样写：** 同一个分析年度的两个分部相邻，方便比较；底层 analysis_df 保持原排序。

---

**第 12—13 行｜显示年度计算核对表**

对应语句：`print("Annual metric checks passed.") ⏐ print(annual_view.round(4).to_string(index=False))`

**语法和执行含义：** 前面校验通过才显示成功。round(4) 对显示用表返回四位小数版本，to_string 隐藏索引，print 输出。

**为什么这样写：** 只对打印结果舍入，不覆盖 analysis_df，所以数据库和 CSV 仍保存计算值。NaN 表示缺失，不是零。

---

**第 14—15 行｜显示长记录和缺失数量**

对应语句：`print(f"Long metric records: {len(metric_df)}") ⏐ print(f"Missing metric values: {int(metric_df['metric_value'].isna().sum())}")`

**语法和执行含义：** len 数长表行数；isna 为每项数值产生布尔标记，sum 数 True，int 转普通整数再输出。

**为什么这样写：** 应看到三十六条结果、两项缺失，说明首年同比按要求保留。

---

## Cell 10: Save Metrics and Verify the Database Query

### 完整代码

```python
# Cell 10: Save Metrics and Verify the Database Query

saved_count = save_metric_results(database, config, metric_df, signature)
stored_metric_df = read_metric_results(database, config, signature)
validate_metric_records(stored_metric_df, analysis_df, config, signature)
verify_metric_copy(metric_df, stored_metric_df)

print(f"Saved records for this run: {saved_count}")
print(f"Read-back records for this run: {len(stored_metric_df)}")
print("Metric database verification passed.")
print(f"All metric rows in the database: {database.get_table_counts()['metric_results']}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 10: Save Metrics and Verify the Database Query`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜提交本次结果到既有表**

对应语句：`saved_count = save_metric_results(database, config, metric_df, signature)`

**语法和执行含义：** 调用 save_metric_results，成功返回本签名写入行数，赋给 saved_count。

**为什么这样写：** 真正写入 metric_results，重复相同输入替换本组而不增加行数。

---

**第 4 行｜只查询当前研究与签名**

对应语句：`stored_metric_df = read_metric_results(database, config, signature)`

**语法和执行含义：** read_metric_results 返回数据库选定版本的结果，赋给 stored_metric_df。

**为什么这样写：** 保留旧签名版本的数据库中也不混入旧数据。

---

**第 5—6 行｜再检查并逐字段回读比较**

对应语句：`validate_metric_records(stored_metric_df, analysis_df, config, signature) ⏐ verify_metric_copy(metric_df, stored_metric_df)`

**语法和执行含义：** 先按当前研究要求验证查询表，再与保存前 metric_df 比较九个字段。

**为什么这样写：** 实际保存结果必须与本次接受的结果一致，单独打印 metric_df 不能证明写库成功。

---

**第 8—10 行｜显示本次保存与回读数量**

对应语句：`print(f"Saved records for this run: {saved_count}") ⏐ print(f"Read-back records for this run: {len(stored_metric_df)}") ⏐ print("Metric database verification passed.")`

**语法和执行含义：** print 显示两个数量及核对通过文字；这些输出只有前面操作成功才执行。

**为什么这样写：** 当前签名应写入、回读三十六条；空值在 SQL 中为 NULL，回读可以显示 NaN。

---

**第 11 行｜另外显示结果表全表数量**

对应语句：`print(f"All metric rows in the database: {database.get_table_counts()['metric_results']}")`

**语法和执行含义：** database.get_table_counts() 返回全表计数字典，取 metric_results 键。

**为什么这样写：** 新本案例库为三十六，但保留其他研究或旧签名版本时可以更多；全表数不等于当前签名数。

---

## Cell 11: Summarize Stages and Export the Results

### 完整代码

```python
# Cell 11: Summarize Stages and Export the Results

stage_summary_df = build_stage_summary(analysis_df, config)
RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

ANNUAL_FILE = RESULTS_DIRECTORY / "annual_metrics.csv"
METRIC_FILE = RESULTS_DIRECTORY / "metric_records.csv"
STAGE_FILE = RESULTS_DIRECTORY / "stage_summary.csv"
MANIFEST_FILE = RESULTS_DIRECTORY / "analysis_manifest.json"

analysis_df.to_csv(ANNUAL_FILE, index=False)
stored_metric_df.to_csv(METRIC_FILE, index=False)
stage_summary_df.to_csv(STAGE_FILE, index=False)

manifest = {
    "study_id": config.study_id,
    "config_signature": signature,
    "calculation_version": CALCULATION_VERSION,
    "calculation_time": calculation_time,
    "index_base_year": config.index_base_year,
    "annual_rows": len(analysis_df),
    "metric_rows": len(stored_metric_df),
    "missing_metric_values": int(stored_metric_df["metric_value"].isna().sum()),
    "summary_method": "Unweighted arithmetic means of available annual metric values.",
    "percentage_convention": "Values are multiplied by 100; 5 means 5 percent.",
    "files": {
        "annual_metrics": ANNUAL_FILE.name,
        "metric_records": METRIC_FILE.name,
        "stage_summary": STAGE_FILE.name,
    },
}
with open(MANIFEST_FILE, "w", encoding="utf-8") as file:
    json.dump(manifest, file, indent=2, ensure_ascii=True)
    file.write("\n")

print(stage_summary_df.round(4).to_string(index=False))
print(f"Annual results saved: {ANNUAL_FILE}")
print(f"Metric query saved: {METRIC_FILE}")
print(f"Stage summary saved: {STAGE_FILE}")
print(f"Analysis manifest saved: {MANIFEST_FILE}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 11: Summarize Stages and Export the Results`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3—4 行｜生成阶段表并准备目录**

对应语句：`stage_summary_df = build_stage_summary(analysis_df, config) ⏐ RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)`

**语法和执行含义：** 先 build_stage_summary 返回汇总表；mkdir 创建 RESULTS_DIRECTORY 及缺少的上级目录，已有目录也可用。

**为什么这样写：** 汇总与保存属于不同动作，先有内存表，再写磁盘。

---

**第 6—9 行｜规定三个 CSV 和清单的位置**

对应语句：`ANNUAL_FILE = RESULTS_DIRECTORY / "annual_metrics.csv" ⏐ METRIC_FILE = RESULTS_DIRECTORY / "metric_records.csv" ⏐ STAGE_FILE = RESULTS_DIRECTORY / "stage_summary.csv" ⏐ MANIFEST_FILE = RESULTS_DIRECTORY / "analysis_manifest.json"`

**语法和执行含义：** 用结果目录依次拼上 annual_metrics.csv、metric_records.csv、stage_summary.csv、analysis_manifest.json。

**为什么这样写：** 每个文件有明确职责和固定名称，下一模块可以按清单取得入口。

---

**第 11 行｜导出年度宽表**

对应语句：`analysis_df.to_csv(ANNUAL_FILE, index=False)`

**语法和执行含义：** analysis_df.to_csv 保存所有二十二列，index=False 不加行索引；默认写模式覆盖同名导出。

**为什么这样写：** 保留基础金额、来源、真实财年、研究年度、前期销售额及三项指标，便于审查公式输入。

---

**第 12 行｜导出真实数据库结果**

对应语句：`stored_metric_df.to_csv(METRIC_FILE, index=False)`

**语法和执行含义：** stored_metric_df 是刚查询并核对的三十六行九列结果，保存为 metric_records.csv。

**为什么这样写：** 导出的长表来自已保存数据库；缺失数值通常在 CSV 中留空，不写零。

---

**第 13 行｜导出阶段均值与样本量**

对应语句：`stage_summary_df.to_csv(STAGE_FILE, index=False)`

**语法和执行含义：** 将六行十二列阶段表保存为 CSV，不导出索引。

**为什么这样写：** 下阶段报告能同时看到均值、所含年和有效年份数。三个 CSV 写入不属于前面的数据库事务。

---

**第 15—23 行｜记录本次运行身份与规模**

对应语句：`manifest = { ⏐ "study_id": config.study_id, ⏐ "config_signature": signature, ⏐ "calculation_version": CALCULATION_VERSION, ⏐ "calculation_time": calculation_time, ⏐ "index_base_year": config.index_base_year, ⏐ "annual_rows": len(analysis_df), ⏐ "metric_rows": len(stored_metric_df), ⏐ "missing_metric_values": int(stored_metric_df["metric_value"].isna().sum()),`

**语法和执行含义：** manifest 普通字典依次保存研究、签名、规则版本、计算时刻、基期以及年度数、长结果数、缺失数。

**为什么这样写：** 导出文件有共同分析版本说明，避免以后只找到 CSV 却不知道基期或采用输入。

---

**第 24—25 行｜记录平均方法和百分比约定**

对应语句：`"summary_method": "Unweighted arithmetic means of available annual metric values.", ⏐ "percentage_convention": "Values are multiplied by 100; 5 means 5 percent.",`

**语法和执行含义：** 两项英文说明写明有效年非加权算术平均，以及数值已乘 100。

**为什么这样写：** 数字 5 表示 5%；若在 Excel 对数字 5 直接套百分号格式会显示 500%，不要误读 CSV 单位。

---

**第 26—31 行｜将输出文件名登记到清单**

对应语句：`"files": { ⏐ "annual_metrics": ANNUAL_FILE.name, ⏐ "metric_records": METRIC_FILE.name, ⏐ "stage_summary": STAGE_FILE.name, ⏐ }, ⏐ }`

**语法和执行含义：** 内层 files 字典保存三项结果的文件名，.name 只取文件名；随后结束内层和外层字典。

**为什么这样写：** 清单与 CSV 在同一目录，移动整个项目仍可查相对文件，不写死原机器绝对路径。

---

**第 32—34 行｜将清单写成 JSON 文件**

对应语句：`with open(MANIFEST_FILE, "w", encoding="utf-8") as file: ⏐ json.dump(manifest, file, indent=2, ensure_ascii=True) ⏐ file.write("\n")`

**语法和执行含义：** open 的 w 模式创建或覆盖 UTF8 文本文件；with 在结束后关闭文件；json.dump 按两空格缩进写内容，最后写一个换行。

**为什么这样写：** 不同于 json.dumps 返回字符串，此处确实保存文件。文件关闭与 SQLite 连接关闭是两件事。

---

**第 36 行｜显示阶段核对视图**

对应语句：`print(stage_summary_df.round(4).to_string(index=False))`

**语法和执行含义：** round(4) 只生成打印用舍入结果，to_string 隐藏索引。

**为什么这样写：** 均值和各指标有效年份数可人工核对，保存的 stage_summary_df 没有被舍入覆盖。

---

**第 37—40 行｜显示四个保存位置**

对应语句：`print(f"Annual results saved: {ANNUAL_FILE}") ⏐ print(f"Metric query saved: {METRIC_FILE}") ⏐ print(f"Stage summary saved: {STAGE_FILE}") ⏐ print(f"Analysis manifest saved: {MANIFEST_FILE}")`

**语法和执行含义：** 四行分别将对应 Path 放入 f-string 再 print。

**为什么这样写：** 确认年度、长表、阶段及分析清单文件已完成写入，后续可从这些位置读取。

---

## Cell 12: Close the Database and Prepare Reporting

### 完整代码

```python
# Cell 12: Close the Database and Prepare Reporting

database.close()
print("Database connection closed.")
print("Module 03 completed.")
print("Next: create charts and write a descriptive report using the saved results.")
print("Stage averages are not CAGR, pooled margins or estimates of a causal pandemic effect.")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 12: Close the Database and Prepare Reporting`

**语法和执行含义：** # 开始注释，标题不作为 Python 操作执行。Cell 编号是本模块的位置，执行次数由 Notebook 另行显示。

**为什么这样写：** 每格代码有明确英文入口，中文讲解单独放在说明区。

---

**第 3 行｜关闭本模块连接**

对应语句：`database.close()`

**语法和执行含义：** 调用第二模块数据库对象的 close，释放连接并把 connection 设回 None。

**为什么这样写：** Cell 10 的成功事务已经提交，关闭不删除结果文件或指标行。

---

**第 4—5 行｜显示模块执行结束**

对应语句：`print("Database connection closed.") ⏐ print("Module 03 completed.")`

**语法和执行含义：** 两句英文 print 报告关闭连接与 Module 03 完成。

**为什么这样写：** 这些状态依赖前面的真实执行；单独运行 print 不能作为保存成功证据。

---

**第 6 行｜交接后续报告工作**

对应语句：`print("Next: create charts and write a descriptive report using the saved results.")`

**语法和执行含义：** 输出下一模块使用已保存结果生成图表和描述性报告的提示。

**为什么这样写：** 第三模块计算与保存，第四模块负责可视化和研究解释。

---

**第 7 行｜说明阶段平均的含义边界**

对应语句：`print("Stage averages are not CAGR, pooled margins or estimates of a causal pandemic effect.")`

**语法和执行含义：** 输出阶段平均不是 CAGR、合并口径利润率或疫情因果效应的英文提示。

**为什么这样写：** 平均方法与研究限制需要一致。阶段均值可以描述不同阶段，不能单凭这些值证明疫情导致变化。

---

## DataFrame 与持久化文件

financial_df 从 SQLite 的 financial_records JOIN business_units 查询得到，当前十二行十六列。build_analysis_frame 加分析年度与阶段，成为十二行十八列。calculate 再加前期销售额和三项指标，analysis_df 为十二行二十二列。to_metric_records 展开为 metric_df 三十六行九列，其中两条首年同比缺失。

Cell 10 保存到 metric_results，查询为 stored_metric_df 并逐字段核对；SQL 中首年同比为 NULL。Cell 11 从年度表生成 stage_summary_df，当前六行十二列，三项指标各有平均值和有效年份数。

results/annual_metrics.csv 保存年度宽表和原始来源字段；results/metric_records.csv 保存实际数据库查询的长结果；results/stage_summary.csv 保存阶段平均及样本量；results/analysis_manifest.json 保存输入身份、时间、基期、单位约定和文件清单。CSV 缺失值留空，不用零补齐。

## 计算规则与版本

销售同比为 (本期销售额 / 前一年销售额 - 1) * 100，按本分部分析年度排序；previous_sales 在分部开始时清空，在阶段边界不清空。利润率为本期营业利润 / 本期净销售额 * 100。销售指数为本期净销售额 / 本分部配置基期净销售额 * 100，基期应为 100。

数据库沿用字段名 config_signature，但本模块签名包含配置、所选基础记录和 CALCULATION_VERSION。同一源记录仅调换行序时签名不变；基期、数值或来源等变化时重新生成签名。保存前再次检查所选基础数据。相同签名重跑原子替换本组结果，其他签名可能保留，因此全表数量不一定等于当前版本三十六行。

之后修改公式逻辑应更新 CALCULATION_VERSION。修改原始财务数据应先重跑第二模块导入，再完整重跑第三模块。直接改 CSV 不会自动更新 SQLite；导出的结果也不会自动重新计算。

## 常见运行问题

NameError 首先检查是否已执行前两个模块定义。FileNotFoundError 核对根目录 JSON 和现有数据库，不要直接建立空库绕过问题。阶段缺失错误回到 Module 01 的 periods 中填写 comparison_stage，再创建配置并保存。遇到 Source records changed，重新查询并计算，不继续保存旧的内存结果。

一次计算失败不会自动清除 kernel 里的旧变量。不要跳过失败格继续写库。连接未关闭时可执行 database.close()；修正后从必要的准备与执行格重新运行。CSV 导出不与数据库事务绑定，导出失败时修正目录权限后重新导出；数据库成功提交的结果仍保留。

## 来源与方法文档

基础金额及报告期间口径沿用第二模块，见 [source_notes.md](../module_02/source_notes.md)。本模块使用本地免费来源数据，不增加付费 API 或网页抓取依赖。Amazon 北美分部与 Walmart 美国分部的地理和收入确认口径不同，报告财年近似配对，只有一个疫情前年份，结论仍为描述性比较。

工具语义核对：[pandas mean](https://pandas.pydata.org/docs/reference/api/pandas.Series.mean.html)、[pandas dropna](https://pandas.pydata.org/docs/reference/api/pandas.Series.dropna.html)、[Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html)。独立数值测试、重复导入、事务回滚与旧输入拒绝的记录见 verification.txt。Module 04 将负责图表和研究报告。
