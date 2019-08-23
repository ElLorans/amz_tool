import os
import pandas as pd
import numpy.random.common                      # needed when compiling. can be removed when numpy goes to .1
import numpy.random.bounded_integers            # needed when compiling. can be removed when numpy goes to .1
import numpy.random.entropy                     # needed when compiling. can be removed when numpy goes to .1
from requests import exceptions
import getpass
from datetime import datetime
from colorama import init, Back
from constants import FC, COUNTRY_CODE, load_logs, ESCALATION_MSG, COLOR, COLOR_RED, FOLDER
from create_report import create_report
from pallet import Pallet
from version import __title__


if __name__ == "__main__":
    init(autoreset=True)                       # no need to change back to default color. COMMENT TO REMOVE COLOR
    print(COLOR + __title__ + "\n")
    #print(Back.RED + __title__ , "\n")

    try:
        os.mkdir(FOLDER)                        # create Folder for reports
    except FileExistsError:
        pass

    while True:                                                         # ask for badge
        print(COLOR + "Please scan your badge\n->", end="")
        LOGIN = input()
        if len(LOGIN) > 0 and LOGIN.isdigit():
            break
        else:
            print(COLOR_RED + "Invalid badge. Please try again.")

    super_log, prices_database = load_logs()               # try to load .xlsx with audits and .json with prices

    while True:
        print(COLOR + "\nInsert Pallet Outer Scannable ID\n->", end="")
        pallet_code = input()

        if pallet_code[:7] != "PALLET_":            # remove these 2 lines to allow every input to be analysed
            print(COLOR_RED + "Only manifested pallets are accepted. To change this setting, contact an administrator."
                              "\nHint: manifest labels start with 'PALLET_'")

        else:
            try:
                pallet = Pallet(FC, pallet_code, prices_database, COUNTRY_CODE)
                if type(pallet.content) is pd.core.frame.DataFrame:
                    prices_database = pallet.database  # update PRICES_DATABASE
                    print(COLOR + f"{pallet_code} has {pallet.priority} priority.")
                    pallet.audit(ESCALATION_MSG)

                    super_log = create_report(pallet.content, super_log, LOGIN)  # updating SUPER_LOG
                    print(COLOR + "Report created.")

                    if pallet.priority != "Not relevant":
                        while True:
                            print(COLOR + f"Have you checked that {pallet_code} has been strapped?(y/n)\n->", end="")
                            is_strapping_checked = input()
                            is_strapping_checked = is_strapping_checked.lower()
                            if 'y' in is_strapping_checked:
                                break
                            else:
                                print(COLOR + f"Please verify that {pallet_code} has been strapped correctly.")

                else:
                    print(COLOR + "There was an error, please try again.")

            except exceptions.RequestException as e:
                print(COLOR_RED + f"\nCONNECTION ERROR!!. Please verify the internet connection.\n{e}")

            except Exception as e:
                print(COLOR_RED + f"FATAL ERROR: {e}.\nPlease signal the bug to lcerreta@amazon.it and start again"
                      f"auditing {pallet_code}.")
                username = getpass.getuser()
                time_completed = datetime.now()
                bug_log_file = FOLDER + "Bug_log.txt"
                with open(bug_log_file, "a") as bug_file:
                    bug_file.write(f"{pallet_code}\t{time_completed}\t{username}\t{e}")
