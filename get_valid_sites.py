import json
import requests
from bs4 import BeautifulSoup
from requests_kerberos import OPTIONAL, HTTPKerberosAuth
import urllib3


def get_valid_sites(folder):
    url = "https://rodeo-dub.amazon.com"
    urllib3.disable_warnings()  # prevent warnings for unverified request

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

    dic = dic.replace("'", '"')         # single quotes with double quotes
    dic = dic.replace(" ", "")          # remove whitespace
    dic = dic.replace("\n", "")         # remove "\n"
    dic = dic.replace(":", '":')        # add final double quote
    dic = dic.replace(",s", ', "s')     # add initial double quote to keys starting with s (all keys)
    dic = dic.replace("{", '{"')        # add initial double quotes

    dictionary = json.loads(dic)        # list of dictionary {"org": "COUNTRY_CODE", "sites": ["site_1", "site_2", ...]}
    sites = list()
    for elem in dictionary:
        sites += elem["sites"]

    with open(folder + "sites.json", "w") as json_file:
        json.dump(sites, json_file)

    return sites
