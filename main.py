"""
Software Tool to audit Transshipment Sort Out Audit process.
"""

import json
import os
import traceback

import pandas as pd
from colorama import init
from requests import exceptions

from ask_is_strapped import ask_is_strapped
from constants import ask_badge, ask_amz_domain, ask_fc, load_logs, ESCALATION_MSG, COLOR, COLOR_RED, COLOR_GREEN, \
    FOLDER
from create_report import create_report, create_bug_report
from get_valid_sites import get_valid_sites
from pallet import Pallet
from version import __title__


def main(fc, prices_db, domain, excel_file, badge):
    """
    Audit TS Out Process: ask for Pallet Manifest Label (Outer Scannable ID) and for inputs during audit process.
    :param fc:                  str of FC (e.g.: "MXP5")
    :param prices_db:           dict {asin: {"price": float, "hrv": bool, "gl": str}, ...}
    :param domain:              str of relevant amazon website's domain (e.g.: "it", "com", "fr", etc. )
    :param excel_file:          pd Dataframe
    :param badge:               str of badge bar code (E.g.: "12264605")
    :return:                    None
    """
    print(COLOR + "\nInsert Manifest Label (Pallet Outer Scannable ID):\n->", end="")
    pallet_code = input()

    #  remove the next three lines ("else:" included) and deindent the following block to analyze every kind of
    #  input
    if pallet_code[:7] != "PALLET_":
        print(COLOR_RED + "Only manifested pallets are accepted. To change this setting, contact an administrator"
                          "\n(Manifest labels start with 'PALLET_').")

    else:
        try:
            pallet = Pallet(fc, pallet_code, prices_db, domain)

            if type(pallet.content) is pd.core.frame.DataFrame:
                prices_db = pallet.database                                     # update PRICES_DATABASE
                print(COLOR_GREEN + f"\n{pallet_code} has {pallet.priority} priority.\n")
                pallet.audit(ESCALATION_MSG)
                excel_file = create_report(pallet.content, excel_file, badge)   # update SUPER_LOG and overwrite xlsx
                print(COLOR + "Report created.")

                if pallet.priority != "Not relevant":
                    ask_is_strapped(pallet.content, pallet_code)

                return prices_db, excel_file

        except exceptions.RequestException as err:
            print(COLOR_RED + f"\nCONNECTION ERROR!!. Please verify your internet connection.\n{err}")

        except BaseException as basic_error:
            generic_error = traceback.format_exc()
            print(COLOR_RED + f"\nFATAL ERROR: {basic_error}.\nPlease signal the bug to lcerreta@amazon.it and start "
                              f"again {pallet_code}'s audit.")
            create_bug_report(pallet_code, generic_error)


if __name__ == "__main__":
    init(autoreset=True)                       # no need to change back to default color. COMMENT TO REMOVE COLOR
    print(COLOR + f"{__title__}\n")

    try:                        # create Folder for reports
        os.mkdir(FOLDER)
        print(COLOR_RED + f"Folder {FOLDER} not found.")
        print(COLOR_GREEN + f"Folder {FOLDER} created.")
    except FileExistsError:
        pass

    while True:                  # ask Badge, FC, load Excel file with previous Audits and json with prices database
        try:
            BADGE = ask_badge()
            FC = ask_fc(FOLDER)
            super_log, prices_database = load_logs()         # try to load .xlsx with audits and .json with prices
            break
        except exceptions.RequestException as e:
            print(COLOR_RED + f"\nCONNECTION ERROR!!. Please verify your internet connection.\n{e}")

        except BaseException as e:
            error = traceback.format_exc()
            print(COLOR_RED + f"\nFATAL ERROR: {e}.\nPlease signal the bug to lcerreta@amazon.it .")
            create_bug_report("LOADING CONSTANTS", error)

    while True:
        try:
            with open(FOLDER + "sites.json") as json_sites:
                sites_to_domain = json.load(json_sites)
            DOMAIN = sites_to_domain[FC]
            print(COLOR + f"Do you want to download prices from https://www.amazon.{DOMAIN}/ ?(yes/no)\n->", end="")
            confirmation = input().lower()
            if confirmation == "yes":
                break
            elif confirmation == "no":
                DOMAIN = ask_amz_domain()
                break
            else:
                print(COLOR_RED + "This answer is not valid. Please insert yes or no.")

        except FileNotFoundError:
            print(COLOR_RED + "sites.json not found.")
            sites_to_domain = get_valid_sites(FOLDER)     # get_valid_sites(folder) returns empty dict in case of error

        except KeyError:
            DOMAIN = ask_amz_domain()
            break

    while True:
        updates = main(FC, prices_database, DOMAIN, super_log, BADGE)

        if type(updates) is tuple and len(updates) == 2:
            prices_database = updates[0]        # update PRICES_DATABASE
            super_log = updates[1]              # update SUPER_LOG and overwrite xlsx
