import getpass
from datetime import datetime
import pandas as pd
from save_file import save_xlsx


def create_report(df_rodeo, df_to_update, badge_id):
    """
    Save log files.
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
