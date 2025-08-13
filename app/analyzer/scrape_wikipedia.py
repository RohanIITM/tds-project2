import re
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from app.analyzers.plot_utils import scatter_with_regression

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

HEADERS = {"User-Agent": "TDS-Agent/1.0 (+https://example.com)"}

class WikiFilms:
    def __init__(self, url: str = WIKI_URL):
        self.url = url
        self.html = None
        self.tables = None

    def fetch(self):
        r = requests.get(self.url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        self.html = r.text
        self.tables = pd.read_html(self.html)
        return self

    def _find_rank_peak_table(self) -> pd.DataFrame:
        # Heuristic: look for a table with columns containing Rank and Peak
        for df in self.tables:
            cols = [c.lower() for c in df.columns.astype(str)]
            if any("rank" in c for c in cols) and any("peak" in c for c in cols):
                return df
        # fallback: first table
        return self.tables[0]

    def count_two_billion_pre_2000(self) -> int:
        # Find the master list of films with worldwide gross
        # Use the first big table containing Title, Worldwide gross
        cand = None
        for df in self.tables:
            cs = [c.lower() for c in df.columns.astype(str)]
            if any("worldwide" in c and "gross" in c for c in cs) and any("title" in c for c in cs):
                cand = df
                break
        if cand is None:
            cand = self.tables[0]
        df = cand.copy()
        # Parse release year from title if present like "Titanic (1997)"
        def year_from_title(s):
            m = re.search(r"(19|20)\d{2}", str(s))
            return int(m.group()) if m else None
        df["year"] = df.iloc[:, 0].apply(year_from_title)
        # Parse gross as number
        def to_num(v):
            s = str(v).replace(",", "")
            m = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*([mb]n|billion)?", s, re.I)
            if m:
                val = float(m.group(1))
                unit = (m.group(2) or "").lower()
                if unit.startswith("b"):
                    val *= 1_000_000_000
                elif unit.startswith("m"):
                    val *= 1_000_000
                return val
            # fallback strip symbols
            s = re.sub(r"[^0-9.]", "", s)
            return float(s) if s else np.nan
        # Try to find a gross column heuristically
        gross_col = None
        for c in df.columns:
            if re.search(r"worldwide.*gross|gross", str(c), re.I):
                gross_col = c
                break
        if gross_col is None:
            gross_col = df.columns[-1]
        df["gross"] = df[gross_col].apply(to_num)
        return int(((df["gross"] >= 2_000_000_000) & (df["year"].fillna(3000) < 2000)).sum())

    def earliest_over_1_5bn(self) -> str:
        cand = None
        for df in self.tables:
            cs = [c.lower() for c in df.columns.astype(str)]
            if any("worldwide" in c and "gross" in c for c in cs) and any("title" in c for c in cs):
                cand = df
                break
        if cand is None:
            cand = self.tables[0]
        df = cand.copy()
        def year_from_title(s):
            m = re.search(r"(19|20)\d{2}", str(s))
            return int(m.group()) if m else 9999
        def to_num(v):
            s = str(v).replace(",", "")
            m = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*([mb]n|billion)?", s, re.I)
            if m:
                val = float(m.group(1))
                unit = (m.group(2) or "").lower()
                if unit.startswith("b"):
                    val *= 1_000_000_000
                elif unit.startswith("m"):
                    val *= 1_000_000
                return val
            s = re.sub(r"[^0-9.]", "", s)
            return float(s) if s else np.nan
        gross_col = None
        for c in df.columns:
            if re.search(r"worldwide.*gross|gross", str(c), re.I):
                gross_col = c
                break
        if gross_col is None:
            gross_col = df.columns[-1]
        df["gross"] = df[gross_col].apply(to_num)
        df["year"] = df.iloc[:,0].apply(year_from_title)
        hit = df[df["gross"] >= 1_500_000_000].sort_values(["year", "gross"], ascending=[True, True])
        if hit.empty:
            return ""
        # return the title (first column)
        return str(hit.iloc[0, 0])

    def rank_peak_correlation_and_plot(self):
        df = self._find_rank_peak_table().copy()
        # normalize columns
        def to_num(x):
            s = str(x).replace(",", "")
            m = re.search(r"-?\d+", s)
            return int(m.group()) if m else None
        # find columns
        rcol = next(c for c in df.columns if re.search(r"rank", str(c), re.I))
        pcol = next(c for c in df.columns if re.search(r"peak", str(c), re.I))
        r = df[rcol].map(to_num)
        p = df[pcol].map(to_num)
        mask = r.notna() & p.notna()
        r = r[mask].astype(int).to_numpy()
        p = p[mask].astype(int).to_numpy()
        corr = float(np.corrcoef(r, p)[0,1]) if len(r) >= 2 else float("nan")
        data_uri, slope = scatter_with_regression(r, p, "Rank", "Peak", dotted_red=True)
        return corr, data_uri
