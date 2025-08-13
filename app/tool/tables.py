import re
import pandas as pd

class Tables:
    @staticmethod
    def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [re.sub(r"\W+", "_", str(c)).strip("_").lower() for c in df.columns]
        return df

    @staticmethod
    def find_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        out = df.copy()
        for c in cols:
            if c in out.columns:
                out[c] = pd.to_numeric(out[c], errors="coerce")
        return out
