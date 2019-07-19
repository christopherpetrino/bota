import re, requests
from web_scrap import scrap_constant
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs


def reshape_heroes_result(results, section_name):
    results = np.reshape(np.array(results), (len(results) // scrap_constant.section_column_count[section_name],
                                             scrap_constant.section_column_count[section_name]))
    return results


def clean_header(section_headers, section_name):
    new_headers = []
    for header in section_headers:
        if header in scrap_constant.section_column_wanted[section_name]:
            new_headers.append(header)
    return new_headers


def get_heroes_section(section_name, html):
    section = re.search(f'<section><header>{section_name}.+?</section>', html).group()
    headers = re.findall(r'<th[^>]*>([^<]+)', section)
    rows = re.findall(r'<td>(?:<a[^>]*>)?([^<]+)', section)
    return rows, headers


def scrap_heroes(url):
    r = requests.get(url, headers=scrap_constant.browser_headers)
    html = r.text
    sections = scrap_constant.heroes_section_wanted
    panda_results = []
    for section_name in sections:
        results, section_header = get_heroes_section(section_name, html)
        results = reshape_heroes_result(results, section_name)
        section_header = clean_header(section_header, section_name)
        panda_result = pd.DataFrame(results, columns=section_header)
        panda_results.append(panda_result)
    return panda_results


def get_current_hero_trends():
    r = requests.get(scrap_constant.heroes_trend_url, headers=scrap_constant.browser_headers)
    html = r.text
    soup = bs(html, "html.parser")
    trend_list = [item[scrap_constant.trend_attribute_key_name]
              for item in soup.find_all() if scrap_constant.trend_attribute_key_name in item.attrs]
    trend_list = np.array(trend_list)
    total_columns = len(scrap_constant.heroes_trend_columns)
    trend_list = np.reshape(trend_list, (len(trend_list) // total_columns, total_columns))
    panda_result = pd.DataFrame(trend_list, columns=scrap_constant.heroes_trend_columns)
    return panda_result


if __name__ == '__main__':
    r = get_current_hero_trends()
    print(r)


