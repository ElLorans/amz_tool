__author__ = "jabaker"


import requests
import urllib3
from requests_kerberos import HTTPKerberosAuth, OPTIONAL


def get_fc(user: str) -> str:
    """
    Return FC of user.
    :param user: str of login (e.g.: "lcerreta")
    :return:     str of FC (e.g.: "MXP5")
    """
    url = f"https://hrwfs.amazon.com/?Operation=empInfoByUid&ContentType=JSON&employeeUid={user}"

    urllib3.disable_warnings()  # prevent warnings for unverified request

    # with requests_retry_session() as req:
    with requests.Session() as req:
        resp = req.get(url,
                       timeout=30,
                       verify=False,
                       allow_redirects=True,
                       auth=HTTPKerberosAuth(mutual_authentication=OPTIONAL))

        if resp.status_code == 200:
            fc = str(str(resp.text).split('"locName":"')[1]).split("-")[0]
            # fc = resp.text
            return fc
        else:
            print(resp.raise_for_status())


if __name__ == "__main__":
    import os
    print("Testing the function: which_fc(user)")
    fc = get_fc(os.getlogin())
    print(f"The fc of the user logged at this PC is {fc}")
