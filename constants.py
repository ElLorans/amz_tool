import pandas as pd
import json
from colorama import Fore, Style


def load_logs():
    """
    Get the log file TsOutAudits.xlsx and the database database.json .
    :return: None
    """
    try:
        super_log = pd.read_excel(f"{FOLDER}TsOutAuditsLog.xlsx")
    except FileNotFoundError:
        print("WARNING: TsOutAuditsLog.xlsx not found.")
        super_log = pd.DataFrame()
    try:
        with open(F"{FOLDER}database.json") as json_file:
            prices_database = json.load(json_file)
    except FileNotFoundError:
        print("WARNING: database.json not found.")
        prices_database = dict()

    return super_log, prices_database


FC = "MXP5"
COUNTRY_CODE = "it"
ESCALATION_MSG = "Please check again. If the error persists, start escalation procedure."
FOLDER = "Audit_Files/"         # folder where logs are saved
COLOR = Style.BRIGHT + Fore.MAGENTA               # easily change all colours
# COLOR = ""                    # uncomment to remove colors
COLOR_RED = Style.BRIGHT + Fore.RED
# COLOR_RED = ""                  # uncomment to remove colors
COLOR_GREEN = Style.BRIGHT + Fore.GREEN
