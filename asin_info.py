import requests
from bs4 import BeautifulSoup
from requests_kerberos import OPTIONAL, HTTPKerberosAuth
from num_to_asin import num_to_asin
from constants import COLOR, COLOR_RED


def update_database(database, asin_set, country, fc):
    """
    Get infos (price, hrv, gl) for a set of SKUs and update database.
    :param database:    dict {asin: {"price": float, "hrv": Bool, "gl": str}, ... }
    :param asin_set:    set of ASINs to get_info of
    :param country:     str (e.g.: "it")
    :param fc:          str (e.g.: "MXP5")
    :return:            dict {asin: {"price": float, "hrv": Bool, "gl": str}, ... }
    """
    # for sku in self.asin_set:
    for sku in asin_set.difference(database):           # get SKUs not in database
        database[sku] = fc_research(sku, fc)
        if database[sku]["hrv"] is True:               # if is hrv but price not found, get price from amazon.country
            if database[sku]["price"] is None:
                if sku[0] == "B":                           # if an asin
                    print(COLOR + f"Scraping {sku} price from amazon.it .")
                    database[sku]["price"] = amz_scrape(sku, country)
                else:                                       # if not an asin
                    print(COLOR + f"Converting {sku} to ASIN.")
                    asin = num_to_asin(sku, fc)
                    print(COLOR + f"ASIN found: {asin}")
                    database[sku]["price"] = amz_scrape(asin, country)
                    database[asin] = database[sku]        # save infos for ASIN as well, so next time no need to convert
    return database


def amz_scrape(asin, country):
    """
    Scrape price of ASIN on amazon.country . Only ASINs are sure to work.
    :param asin:        str
    :param country:     str (e.g.: "it")
    :param country:     str (e.g.: "MXP5")
    :return:            float or None
    """
    url = f"https://www.amazon.{country}/s?k={asin}"
    r = requests.get(url)
    if "Nessun risultato" in r.text:
        print(f"{asin} not found on amazon.{country}")
        return None
    scraped = BeautifulSoup(r.text, features="lxml")
    price_tag = scraped.find_all('span', {'class': 'a-offscreen'})
    string = price_tag[0].text
    price = string.replace("\xa0€", "")
    price = price.replace(".", "")          # only for Italian numbers!!!
    price = price.replace(",", ".")         # only for Italian numbers!!!
    try:
        price = float(price)
        print(COLOR + "Price found.")
    except ValueError:
        print(COLOR_RED + f"Could not convert price {price} to float from {url}")
        price = None
    return price


def fc_research(asin, fc):  # 26-32 sec for 150 elem
    """
    Scrape list price, if hrv and gl (in fc language) from fcresearch-eu.
    :param asin:    str
    :param fc:      str
    :return:        {"price": float, "hrv": bool, "gl": str} if successful, None otherwise.
    """

    url = f"http://fcresearch-eu.aka.amazon.com/{fc}/results/product?s={asin}"

    cookie = {"fcmenu-employeeLogin": "null", "fcmenu-warehouseId": fc,
              "fcmenu-locale": "en_US", "fcmenu-isAdvanced": "true",
              "fcmenu-authMode": "openid", "fcmenu-employeePermissionLevel": ""}

    r = requests.get(url, auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL),
                     cookies=cookie)

    if r.status_code == 200:
        sp = BeautifulSoup(r.text, "html.parser")
        rows = sp.find_all("tr")
        price = None
        hrv = None
        gl = None
        for row in rows:
            if row.find_all("th")[0].text == "Binding":
                gl = row.find_all("td")[0].text
            elif row.find_all("th")[0].text == "List Price":
                currency_price = row.find_all("td")[0].text
                try:
                    price = currency_price[4:]  # remove currency
                    price = float(price)
                except ValueError:
                    price = None
            elif row.find_all("th")[0].text == "Very High Value":
                hrv = row.find_all("td")[0].text
                if hrv == "true":
                    hrv = True
                elif hrv == "false":
                    hrv = False
                break
        return {"price": price, "hrv": hrv, "gl": gl}


if __name__ == "__main__":
    # inp = input("Insert ASIN ->")
    inp = "X000JDSDD7"
    fc = "MXP5"
    print(fc_research(inp, fc))
