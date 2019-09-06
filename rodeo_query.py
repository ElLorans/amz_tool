import pandas as pd
import requests
import urllib3
from requests_kerberos import OPTIONAL, HTTPKerberosAuth

from constants import COLOR


def rodeo_query(fc, pallet):      # 3.5-4 seconds for 150 elem
    """
    Get pd DataFrame with info from rodeo about pallet/tote in TS Out.
    :param fc:          str
    :param pallet:      Pallet or Tote are accepted.
    :return:            df or "No data was found" if status_code = 200, "There was an error while connecting to {url}"
                        otherwise.
    """

    url = f"https://rodeo-dub.amazon.com/{fc}/Search?_enabledColumns=on&enabledColumns=ASIN_TITLES&enabledColumns" \
          f"=FC_SKU&enabledColumns=OUTER_SCANNABLE_ID&&searchKey={pallet} "

    urllib3.disable_warnings()  # prevent warnings for unverified request

    print(COLOR + "Downloading manifested pallet's content from Rodeo.")
    with requests.Session() as req:
        resp = req.get(url,
                       timeout=30,
                       verify=False,
                       allow_redirects=True,
                       auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL))

    if resp.status_code == 200:
        data = pd.read_html(resp.text, flavor=None, header=0, parse_dates=["Need To Ship By Date"])

        if data is not None and len(data[0]) > 0:
            df = pd.concat(data, sort=False)
            df = df.drop(columns='Unnamed: 0')
            return df

        else:
            return f"No data was found at {url}\nPlease check that {pallet} is correct.\nIf the error persists, " \
                   f"please check Rodeo status for your FC: {fc}."

    else:
        # return resp.raise_for_status()            # to see error
        return f"There was an error while connecting to {url}"
