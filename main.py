"""
Software Tool to audit Transshipment Sort Out Audit process.
"""


import traceback

import pandas as pd
from colorama import init
from requests import exceptions
import numpy.random.common                      # needed when compiling. can be removed when numpy goes to .1
import numpy.random.bounded_integers            # needed when compiling. can be removed when numpy goes to .1
import numpy.random.entropy                     # needed when compiling. can be removed when numpy goes to .1

from ask_is_strapped import ask_is_strapped
from constants import ask_badge, ask_amz_domain, ask_fc, load_logs, ESCALATION_MSG, COLOR, COLOR_RED, COLOR_GREEN
from create_report import create_report, create_bug_report
from pallet import Pallet
from version import __title__


def main(fc, prices_database, domain, super_log, badge):
    """
    Audit TS Out Process. Ask for Pallet Manifest Label (Outer Scannable ID) and handle audit process.
    :param fc:                  str of FC (e.g.: "MXP5")
    :param prices_database:
    :param domain:              str of relevant amazon website (e.g.: it, com, fr, etc. )
    :param super_log:
    :param badge:               str of badge bar code
    :return:                    None
    """
    print(COLOR + "\nInsert Pallet Outer Scannable ID\n->", end="")
    pallet_code = input()

    #  remove the next three lines (until "else:" included) and deindent the following block to analyze every input
    if pallet_code[:7] != "PALLET_":
        print(COLOR_RED + "Only manifested pallets are accepted. To change this setting, contact an administrator"
                          "\n(Manifest labels start with 'PALLET_').")

    else:
        try:
            pallet = Pallet(fc, pallet_code, prices_database, domain)

            if type(pallet.content) is pd.core.frame.DataFrame:
                prices_database = pallet.database  # update PRICES_DATABASE
                print(COLOR_GREEN + f"\n{pallet_code} has {pallet.priority} priority.\n")
                pallet.audit(ESCALATION_MSG)
                super_log = create_report(pallet.content, super_log, badge)  # update SUPER_LOG and overwrite xlsx
                print(COLOR + "Report created.")

                if pallet.priority != "Not relevant":
                    ask_is_strapped(pallet.content, pallet_code)

        except exceptions.RequestException as e:
            print(COLOR_RED + f"\nCONNECTION ERROR!!. Please verify your internet connection.\n{e}")

        except BaseException as e:
            error = traceback.format_exc()
            print(COLOR_RED + f"\nFATAL ERROR: {e}.\nPlease signal the bug to lcerreta@amazon.it and start "
                              f"again {pallet_code}'s audit.")
            create_bug_report(pallet_code, error)


if __name__ == "__main__":
    init(autoreset=True)                       # no need to change back to default color. COMMENT TO REMOVE COLOR
    print(COLOR + f"{__title__}\n")

    BADGE = ask_badge()
    FC = ask_fc()
    DOMAIN = ask_amz_domain()
    super_log, prices_database = load_logs()               # try to load .xlsx with audits and .json with prices

    while True:
        main(FC, prices_database, DOMAIN, super_log, BADGE)
