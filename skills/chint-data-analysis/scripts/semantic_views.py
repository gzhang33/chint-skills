"""
semantic_views.py — DuckDB 统一 SQL 语义视图层 (Semantic Layer)

职责：
在 data/database/<dept>.duckdb 中建立标准 SQL 语义视图 v_china_sales_monthly 与 v_overseas_sales_monthly，
确保 Metabase 零代码看板与 Agent Text-to-SQL 深度归因计算口径 100% 同源对齐。
"""
import sys
import os
from pathlib import Path
import duckdb


# 确保能找到项目根目录与 etl 目录
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "etl") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "etl"))
if str(ROOT_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "scripts"))

try:
    from config_loader import get_skill_duckdb_path
    DUCKDB_PATH = str(get_skill_duckdb_path())
except (ImportError, FileNotFoundError):
    try:
        from config import DUCKDB_PATH
    except ImportError:
        DUCKDB_PATH = str(ROOT_DIR / "data" / "sales.duckdb")

SEMANTIC_VIEW_CN = "v_china_sales_monthly"
SEMANTIC_VIEW_INTL = "v_overseas_sales_monthly"



def apply_semantic_views(db_path: str = DUCKDB_PATH, read_only: bool = False, all_depts: bool = False):
    """向指定的 DuckDB 数据库注入统一语义视图及 DataEase 分类隔离视图"""
    paths = []
    if all_depts:
        db_dirs = [
            ROOT_DIR / "data",
            ROOT_DIR / "data" / "database",
            Path(__file__).parent.parent / "data"
        ]
        for db_dir in db_dirs:
            if db_dir.exists():
                paths.extend(list(db_dir.glob("*.duckdb")))
    if not paths:
        cand = Path(db_path)
        if not cand.exists():
            for alt in [
                ROOT_DIR / "data" / "database" / "acb.duckdb",
                ROOT_DIR / "data" / "sales.duckdb",
            ]:
                if alt.exists():
                    cand = alt
                    break
        paths = [cand]

    views_sql_file = Path(__file__).parent / "dataease_views.sql"
    if not views_sql_file.exists():
        print(f"[Warning] SQL view file missing at {views_sql_file}")
        return

    sql_content = views_sql_file.read_text(encoding="utf-8")

    for p in paths:
        try:
            con = duckdb.connect(str(p), read_only=read_only)
            con.execute("""
                CREATE TABLE IF NOT EXISTS product_mappings (
                    id VARCHAR, department VARCHAR, mapping_type VARCHAR, material_code VARCHAR,
                    material_desc VARCHAR, product_series VARCHAR, source_value VARCHAR,
                    target_value VARCHAR, status VARCHAR, updated_at VARCHAR, updated_by VARCHAR,
                    UNIQUE (department, mapping_type, source_value)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_mappings_dept_type_source ON product_mappings(department, mapping_type, source_value);
                CREATE INDEX IF NOT EXISTS idx_mappings_desc ON product_mappings(material_desc);
                CREATE INDEX IF NOT EXISTS idx_mappings_code ON product_mappings(material_code);
            """)
            con.execute(sql_content)
            con.close()
            print(f"[Semantic Layer] Successfully updated views in {p.name}")
        except Exception as e:
            print(f"[Semantic Layer Error] Failed to update views in {p.name}: {e}")


if __name__ == "__main__":
    apply_semantic_views(all_depts=True)

