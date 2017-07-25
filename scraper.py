import requests
from bs4 import BeautifulSoup as bs
import re
import unicodecsv as csv
import os


BASE_URL = "http://gamli.rvk.is/vefur/owa/{}"
year_url = "http://gamli.rvk.is/vefur/owa/edutils.parse_page?nafn=BN2MEN{}"
years = ["96", "97", "98", "99", "00", "01", "02", "03", "04", "05", "06",
         "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]


def scrape(url):
    r = requests.get(url)
    soup = bs(r.text, "lxml")
    filename = soup.h2.next_sibling.strip().replace(" ", "_").replace(".", "") + ".csv"
    links = soup.find_all(href=re.compile("edutils.parse_page"))
    result = []
    for link in links:
        data = {}
        b1 = link.find_previous("b")
        b2 = b1.find_previous("b")
        data["nr"] = b2.text.replace("Umsókn nr.", "").strip()
        data["url"] = BASE_URL.format(link.get('href'))
        data["heimilisfang"] = link.text
        tegund = link.find_next("i")
        data["tegund"] = tegund.text
        text = ""
        for el in tegund.find_next_siblings():
            if el.name == "i":
                break
            if not el.name == "i":
                try:
                    text = text + str(el.next_sibling)
                except AttributeError:
                    pass
        data["nidurstada"] = tegund.find_next("i").get_text().strip().replace("\r\r\n", " ")
        data["spurning"] = (text.strip().replace("\r\r\n", " "))
        result.append(data)
    return (filename, result)


def collect_all():
    for year in years:
        r = requests.get(year_url.format(year))
        soup = bs(r.text, "lxml")
        for link in soup.find_all('a'):
            filename, result = scrape(BASE_URL.format(link.get('href')))
            keys = result[0].keys()
            if not os.path.exists(year):
                os.makedirs(year)
            filepath = os.path.join(year, filename)
            with open(filepath, "wb") as f:
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
                dict_writer.writerows(result)
            print("Sótti {}".format(filepath))
        print("------")
        print("Sótti {}".format(year))


if __name__ == '__main__':
    collect_all()

