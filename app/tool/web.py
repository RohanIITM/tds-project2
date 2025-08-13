import pandas as pd
import requests
from bs4 import BeautifulSoup
from app.config import USER_AGENT

class Web:
    @staticmethod
    def get(url: str) -> str:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        return r.text

    @staticmethod
    def read_html_tables(url: str) -> list[pd.DataFrame]:
        return pd.read_html(url, flavor="lxml")

    @staticmethod
    def soup(url: str) -> BeautifulSoup:
        html = Web.get(url)
        return BeautifulSoup(html, "lxml")
