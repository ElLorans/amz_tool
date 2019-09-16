import json

import requests
import urllib3
from bs4 import BeautifulSoup
from requests_kerberos import OPTIONAL, HTTPKerberosAuth
from colorama import Fore, Style


COLOR_GREEN = Style.BRIGHT + Fore.GREEN

COLOR_RED = Style.BRIGHT + Fore.RED


def get_valid_sites(folder):
    """
    Create sites.json in folder with valid FCs from https://rodeo-dub.amazon.com and return valid FCs
    :param folder:  folder
    :return:        dict {site: amz_domain, ...} (E.g.: {"DXB3": "ae", "BWU1": "de", ... }) amz_domain set to None if
                    not clear.
    """
    url = "https://rodeo-dub.amazon.com"
    urllib3.disable_warnings()  # prevent warnings for unverified request

    country_to_domain = {"AE": "ae", "AU": "de", "BR": "com.br", "CA": "ca", "CN": "cn", "DE": "de", "ES": "es",
                         "FR": "fr", "GB": "co.uk", "IN": "in", "IT": "it", "JP": "co.jp", "MX": "com.mx", "SG": "sg",
                         "US": "com"}
    try:
        with requests.Session() as req:
            resp = req.get(url,
                           timeout=30,
                           verify=False,
                           allow_redirects=True,
                           auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL))

        soup = BeautifulSoup(resp.text, "lxml")

        js_list = soup.find_all("script", {"type": "text/javascript"})

        nav = [x for x in js_list if "fcpnav.render" in x.text][0].text
        start = "orglist: "
        end = "\n    },\n    searchbox:"

        without_end_nav = str(nav).split(end)[0]
        dic = without_end_nav.split(start)[1]

        # make dic JSON valid
        dic = dic.replace("'", '"')         # single quotes with double quotes
        dic = dic.replace(" ", "")          # remove whitespace
        dic = dic.replace("\n", "")         # remove "\n"
        dic = dic.replace(":", '":')        # add final double quote
        dic = dic.replace(",s", ', "s')     # add initial double quote to keys starting with s (all keys)
        dic = dic.replace("{", '{"')        # add initial double quotes

        dictionary = json.loads(dic)   # list of dictionary {"org": "COUNTRY_CODE", "sites": ["site_1", "site_2", ...]}
        sites = dict()
        for dic in dictionary:              # dic {'org': 'AE', 'sites': ['DXB3']}
            for site in dic["sites"]:
                sites[site] = country_to_domain.get(dic["org"])

        with open(folder + "sites.json", "w") as json_file:
            json.dump(sites, json_file)
        print(COLOR_GREEN + "Valid sites downloaded.")

    except:
        print(COLOR_RED + f"Impossible to retrieve valid FCs from {url} .")
        sites = dict()

    return sites


if __name__ == "__main__":
    a = get_valid_sites("TEST")
    print(a)
    breakpoint()
