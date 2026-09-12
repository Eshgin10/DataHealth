import pandas as pd
import numpy as np

def validate_dataframe(df: pd.DataFrame, profiles: dict) -> list:
    issues = []

    # 1. Missing Data
    for col in df.columns:
        missing_mask = df[col].isna() | (df[col] == "")
        missing_count = missing_mask.sum()
        if missing_count > 0:
            issues.append({
                "category": "MISSING DATA",
                "column_name": col,
                "issue_type": "missing values",
                "severity": "medium",
                "affected_rows": int(missing_count)
            })

    # 2. Duplicates
    dup_mask = df.duplicated(keep=False)
    dup_count = dup_mask.sum()
    if dup_count > 0:
        issues.append({
            "category": "DUPLICATES",
            "column_name": None,
            "issue_type": "exact duplicates",
            "severity": "high",
            "affected_rows": int(dup_count)
        })

    for col, prof in profiles.items():
        s = df[col].dropna()
        if len(s) == 0:
            continue

        sem_type = prof['type']
        s_str = s.astype(str)

        # 3. Format Issues (Email)
        if sem_type == "email":
            invalid_mask = ~s_str.str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', regex=True)
            invalid_count = invalid_mask.sum()
            if invalid_count > 0:
                issues.append({
                    "category": "INVALID VALUES",
                    "column_name": col,
                    "issue_type": "malformed email",
                    "severity": "high",
                    "affected_rows": int(invalid_count)
                })

        # 4. Format Issues (Phone)
        elif sem_type == "phone":
            invalid_mask = ~s_str.str.contains(r'^\+?[\d\s\-\(\)]+$', regex=True)
            invalid_count = invalid_mask.sum()
            if invalid_count > 0:
                issues.append({
                    "category": "INVALID VALUES",
                    "column_name": col,
                    "issue_type": "invalid phone number format",
                    "severity": "medium",
                    "affected_rows": int(invalid_count)
                })

        # 5. Outliers (Numeric)
        elif sem_type == "numeric":
            s_num = pd.to_numeric(s, errors='coerce')
            q1 = s_num.quantile(0.25)
            q3 = s_num.quantile(0.75)
            iqr = q3 - q1
            outlier_mask = (s_num < (q1 - 1.5 * iqr)) | (s_num > (q3 + 1.5 * iqr))
            outlier_count = outlier_mask.sum()

            neg_mask = s_num < 0
            neg_count = neg_mask.sum()

            if outlier_count > 0:
                issues.append({
                    "category": "NUMERIC ANOMALIES",
                    "column_name": col,
                    "issue_type": "statistical outlier (IQR)",
                    "severity": "low",
                    "affected_rows": int(outlier_count)
                })
            if neg_count > 0 and 'value' in col.lower():
                issues.append({
                    "category": "LOGICAL CONFLICTS",
                    "column_name": col,
                    "issue_type": "negative monetary value",
                    "severity": "high",
                    "affected_rows": int(neg_count)
                })

        # 6. Categorical Inconsistencies
        elif sem_type in ["categorical", "free text"]:
            s_lower = s_str.str.lower()
            if s_lower.nunique() < s_str.nunique():
                issues.append({
                    "category": "CATEGORICAL INCONSISTENCIES",
                    "column_name": col,
                    "issue_type": "case inconsistencies",
                    "severity": "medium",
                    "affected_rows": int((s_str != s_lower).sum())
                })

            s_stripped = s_str.str.strip()
            whitespace_issues = (s_str != s_stripped).sum()
            if whitespace_issues > 0:
                issues.append({
                    "category": "WHITESPACE / CASE ISSUES",
                    "column_name": col,
                    "issue_type": "leading or trailing whitespace",
                    "severity": "low",
                    "affected_rows": int(whitespace_issues)
                })

    return issues
