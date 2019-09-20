"""
Handle the constants for the entire project and the functions to retrieve/ask them.
"""


import json
import os

import pandas as pd
from colorama import Fore, Style

from get_fc import get_fc
from get_valid_sites import get_valid_sites
from version import __title__


def load_logs():
    """
    Get the log file TsOutAudits.xlsx and the database database.json . In case the files are not in the folder FOLDER
    where the main file is stored, generate empty pd DataFrame and empty dict.
    :return: (pd.DataFrame, dict())
    """
    try:
        super_log = pd.read_excel(f"{FOLDER}TsOutAuditsLog.xlsx")
    except FileNotFoundError:
        print("WARNING: TsOutAuditsLog.xlsx not found.")
        super_log = pd.DataFrame()

    try:
        with open(f"{FOLDER}database.json") as json_file:
            prices_database = json.load(json_file)
    except FileNotFoundError:
        print("WARNING: database.json not found.")
        prices_database = dict()

    return super_log, prices_database


def ask_badge():
    while True:                                                         # ask for badge
        print(COLOR + "Please scan your badge\n->", end="")
        login = input()
        if len(login) > 0 and login.isdigit():
            return login
        else:
            print(COLOR_RED + "Invalid badge. Please try again.")


def download_fc(fc, folder):
    print(COLOR_RED + f"{fc} not recognized. Downloading valid FCs from https://rodeo-dub.amazon.com .")
    sites = get_valid_sites(folder)
    return sites


def ask_fc(folder):
    while True:
        default_fc = get_fc(os.getlogin())
        print(COLOR + f"Are you auditing Transshipment Out in {default_fc}?(yes/no)\n->", end="")
        # colorama doesn't work with input, so need to split input from print
        is_default_fc_correct = input().strip().lower()
        if is_default_fc_correct == "yes":
            fc = default_fc
            return fc

        elif is_default_fc_correct == "no":
            print(COLOR + "Please provide the site in which you are auditing.\n->", end="")
            fc = input().strip().upper()

            try:
                with open(folder + "sites.json") as json_file:
                    sites = json.load(json_file)
                if fc in sites:
                    return fc

                else:
                    sites = download_fc(fc, folder)
                    if fc in sites:
                        return fc
                    else:
                        print(COLOR_RED + f"{fc} is not recognized. Are you sure {fc} is correct?(yes/no)\n->", end="")
                        confirm = input().strip().lower()
                        if confirm == "yes":
                            return fc

            except FileNotFoundError:
                fc = download_fc(fc, folder)
                if fc is not None:
                    return fc

            except:
                print(COLOR_RED + f"ERROR: impossible to check if {fc} is a valid site. If {fc} is not correct, "
                                  f"please restart {__title__} .")
                return fc

        else:
            print(COLOR_RED + "Invalid answer. Please insert yes or no.")


def ask_amz_domain():
    while True:
        domains = ('ae', 'cn', 'in', 'ca', 'co.uk', 'com.br', None, 'fr', 'es', 'de', 'it', 'co.jp', 'com.mx', 'sg',
                   'com')

        print(COLOR + "Please provide the domain of the relevant amazon website.\n(E.g.: if the FC is in Italy, "
                      "amazon.it is the relevant amazon website, so insert: it ; if the FC is in the US, amazon.com is "
                      "the relevant website, so insert: com ; etc.)\n->", end="")
        domain = input().strip().lower()

        if domain in domains:
            return domain
        else:
            print(COLOR_RED + f"This domain is not recognized. Are you sure {domain} is correct?(yes/no)\n->",
                  end="")
            confirmation = input().strip().lower()
            if confirmation == "yes":
                return domain


ESCALATION_MSG = "Please check again. If the error persists, start escalation procedure."
FOLDER = "Audit_Files/"         # folder where logs are saved
COLOR = Style.BRIGHT + Fore.MAGENTA               # easily change all colours
# COLOR = ""                    # uncomment to remove colors
COLOR_RED = Style.BRIGHT + Fore.RED
# COLOR_RED = ""                  # uncomment to remove colors
COLOR_GREEN = Style.BRIGHT + Fore.GREEN
# COLOR_GREEN = ""              # uncomment to remove colors
