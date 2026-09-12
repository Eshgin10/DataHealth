import pandas as pd
import numpy as np
import re
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")


def infer_semantic_type(series: pd.Series) -> str:
    """Infer the semantic type of a column based on its content."""
    s = series.dropna()
    if len(s) == 0:
        return "unknown"

    s_str = s.astype(str).str.strip()

    # Check boolean
    bool_vals = {"true", "false", "yes", "no", "1", "0", "t", "f"}
    if s_str.str.lower().isin(bool_vals).all():
        return "boolean"

    # Check if column name hints at identifier
    col_name = str(series.name).lower()
    if "id" in col_name and ("customer" in col_name or "user" in col_name or "order" in col_name or col_name.endswith("_id")):
        return "identifier"

    # Check if mostly numeric
    numeric_coerced = pd.to_numeric(s, errors="coerce")
    numeric_ratio = numeric_coerced.notna().mean()
    if numeric_ratio > 0.8:
        return "numeric"

    # Email pattern
    email_pattern = r"^[\w\.\+\-]+@[\w\.\-]+\.\w{2,}$"
    if s_str.str.contains(email_pattern, regex=True, na=False).mean() > 0.7:
        return "email"

    # Phone pattern
    phone_pattern = r"^[\+\d\s\-\(\)\.]{7,}$"
    if s_str.str.contains(phone_pattern, regex=True, na=False).mean() > 0.7:
        return "phone"

    # Date detection — try parsing a sample
    try:
        sample = s_str.head(200)
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        if parsed.notna().mean() > 0.7:
            return "date"
    except Exception:
        pass

    # Check cardinality for categorical
    unique_count = s.nunique()
    unique_pct = unique_count / len(s) if len(s) > 0 else 0
    if unique_count < 30 or unique_pct < 0.05:
        return "categorical"

    # High-cardinality identifier
    if unique_pct > 0.95:
        return "identifier"

    return "free text"


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Profile every column in the DataFrame."""
    profile = {}
    total_rows = len(df)

    for col in df.columns:
        s = df[col]
        null_count = int(s.isna().sum() + (s.astype(str).str.strip() == "").sum())
        unique_count = int(s.nunique())

        mc = s.value_counts().head(5)
        most_common_dict = {str(k): int(v) for k, v in mc.items()}

        col_profile = {
            "name": col,
            "type": infer_semantic_type(s),
            "null_count": null_count,
            "null_pct": round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0,
            "unique_count": unique_count,
            "unique_pct": round((unique_count / total_rows) * 100, 2) if total_rows > 0 else 0,
            "most_common": most_common_dict,
        }

        # Numeric stats
        if pd.api.types.is_numeric_dtype(s):
            col_profile["min"] = str(s.min()) if not pd.isna(s.min()) else None
            col_profile["max"] = str(s.max()) if not pd.isna(s.max()) else None
            col_profile["mean"] = round(float(s.mean()), 2) if not pd.isna(s.mean()) else None

        profile[col] = col_profile

    return profile
