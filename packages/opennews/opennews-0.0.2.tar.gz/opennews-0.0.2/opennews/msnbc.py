"""MSNBC fetcher for OpenNews."""
from .basic import _get_news, _get_news_async


URL = 'https://www.msnbc.com/'


def _extract(soup):
    news = {i.get('href'): i.text for i in soup.find_all('a') if i.get('href').count("/") == 5 and i.get("target") != "_blank" and "/watch/" not in i.get('href')}
    return news


get_news = _get_news(URL, _extract)
get_news_async = _get_news_async(URL, _extract)

