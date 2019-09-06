"""
Handle the constants for the entire project and the functions to retrieve/ask them.
"""


import json
import os

import pandas as pd
from colorama import Fore, Style

from get_fc import get_fc


def load_logs():
    """
    Get the log file TsOutAudits.xlsx and the database database.json . In case the files are not in the folder FOLDER
    where the main file is stored, generate empty pd DataFrame and empty dict.
    :return: (pd.DataFrame, dict())
    """
    try:
        os.mkdir(FOLDER)                        # create Folder for reports
    except FileExistsError:
        pass

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


def ask_fc():
    while True:
        default_fc = get_fc(os.getlogin())
        print(COLOR + f"Are you auditing Transshipment Out in {default_fc}?(yes/no)\n->", end="")
        is_default_fc_correct = input().lower()    # colorama doesn't work with input, so need to split input from print
        if is_default_fc_correct.lower() == "yes":
            fc = default_fc
            return fc
        elif is_default_fc_correct.lower() == "no":
            print(COLOR + "Please provide the site in which you are auditing.\n->", end="")
            fc = input().upper()
            if len(fc) == 4:
                return fc
            else:
                print(COLOR_RED + "This site is not recognized. Please insert site again. If the problem persists, "
                                  "please contact an administrator.")
        else:
            print(COLOR_RED + "Invalid answer. Please insert yes or no.")


def ask_amz_domain():
    domains = ("it", "cn", "in", "jp", "sg", "tr", "ae", "fr", "de", "nl", "es", "uk", "ca", "mx", "com", "au", "br")
    while True:
        print(COLOR + "Please provide the domain of the relevant amazon website (fr, it, com etc.).\n->", end="")
        domain = input().lower()

        if domain in domains:
            return domain
        else:
            print(COLOR_RED + f"This domain is not recognized. Are you sure {domain} is correct?(yes/no)\n->",
                  end="")
            confirmation = input().lower()
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
