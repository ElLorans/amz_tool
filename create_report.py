import getpass
from datetime import datetime

import pandas as pd

from constants import FOLDER
from save_file import save_xlsx


def create_report(df_rodeo, df_to_update, badge_id):
    """
    Save log files and return df_to_update updated.
    :param df_to_update:
    :param df_rodeo:
    :param badge_id:       str (e.g.: "12264605")
    :return:            df_updated
    """
    username = getpass.getuser()
    time_completed = datetime.now()
    df_rodeo["Username"] = username
    df_rodeo["Badge ID"] = badge_id
    df_rodeo["Audit_Time"] = time_completed
    df_updated = pd.concat([df_to_update, df_rodeo], sort=False)

    save_xlsx(df_updated, "Audit_Files/TsOutAuditsLog.xlsx")
    df_relevant_info = df_updated[["Username", "Badge ID", "Audit_Time", "Outer Scannable ID", "Pallet_Priority",
                                   "Scannable ID", "FN SKU", "list_price", "hrv", "Audit_Result", "Comment"]]

    save_xlsx(df_relevant_info, "Audit_Files/TsOutAudits.xlsx")

    return df_updated


def create_bug_report(pallet_code, e):
    username = getpass.getuser()
    time_completed = datetime.now()
    bug_log_file = FOLDER + "Bug_log.txt"
    with open(bug_log_file, "a") as bug_file:
        bug_file.write("\n")
        bug_file.write(str([pallet_code, time_completed, username, e]))
