import requests
from bs4 import BeautifulSoup
from requests_kerberos import OPTIONAL, HTTPKerberosAuth


def num_to_asin(prod_num, fc):  # 26-32 sec for 150 elem
    """
    FAILS IF PROD_NUM HAS 2 ASINS. SOLVE IT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Get ASIN from product number on fcresearch-eu.
    :param prod_num:    str
    :param fc:          str
    :return:            str if success, None if prod_num not on fcresearch or connection not succesful
    """

    url = f"http://fcresearch-eu.aka.amazon.com/{fc}/results/product?s={prod_num}"

    cookie = {"fcmenu-employeeLogin": "null", "fcmenu-warehouseId": fc,
              "fcmenu-locale": "en_US", "fcmenu-isAdvanced": "true",
              "fcmenu-authMode": "openid", "fcmenu-employeePermissionLevel": ""}

    r = requests.get(url, auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL),
                     cookies=cookie)

    if r.status_code == 200:
        sp = BeautifulSoup(r.text, "html.parser")
        rows = sp.find_all("tr")
        for row in rows:
            if row.find_all("th")[0].text == "ASIN":
                asin = row.find_all("td")[0].text
                return asin


if __name__ == "__main__":
    product_number = "3474636333226"
    fc = "MXP5"
    print(num_to_asin(product_number, fc))
    print(num_to_asin("4006501723284", "MXP5"))
