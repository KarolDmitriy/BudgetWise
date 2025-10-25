import pandas as pd
from .database import get_conn

def read_operations():
    conn = get_conn()
    df = pd.read_sql_query("SELECT o.*, c.name as category, c.type as cat_type FROM operations o LEFT JOIN categories c ON o.category_id = c.id ORDER BY date DESC", conn, parse_dates=["date"])
    conn.close()
    if df.empty:
        return pd.DataFrame(columns=["id","date","amount","category","cat_type","note"])
    # ensure correct dtypes
    df["date"] = pd.to_datetime(df["date"])
    return df

def summary_by_month(df):
    if df.empty:
        return pd.DataFrame()
    df2 = df.copy()
    df2["month"] = df2["date"].dt.to_period("M").dt.to_timestamp()
    agg = df2.groupby(["month", "cat_type"])["amount"].sum().unstack(fill_value=0).reset_index()
    if "expense" not in agg.columns: agg["expense"] = 0
    if "income" not in agg.columns: agg["income"] = 0
    agg["net"] = agg["income"] - agg["expense"]
    return agg

def by_category(df, top_n=10):
    if df.empty:
        return pd.DataFrame()
    agg = df.groupby(["category"])["amount"].sum().abs().sort_values(ascending=False).head(top_n).reset_index()
    return agg
