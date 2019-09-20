import json

import pandas as pd

from asin_info import update_database
from constants import COLOR, COLOR_RED, FOLDER
from rodeo_query import rodeo_query
from tote import Tote


class Pallet:
    """
    Create Pallet instance with all infos and self.audit() method to handle audit process.
    """
    def __init__(self, fc, pallet_code, database, domain):
        """
        :param fc:              str of FC (e.g.: "MXP5")
        :param pallet_code:     str of SCANNABLE OUTER ID (e.g.: "PALLET_a34sfe4_Z")
        :param database:        dict {asin: {"price": float, "hrv": bool, "gl": str}, ...}
        :param domain:          str of relevant amazon website's domain (e.g.: "it", "com", "fr", etc. )
        """
        self.fc = fc
        self.pallet_code = pallet_code
        self.database = database  # dict {asin: {"price": float, "hrv": bool, "gl": str}, ...}
        self.content = rodeo_query(self.fc, self.pallet_code)
        self.get_info(domain)  # add price, hrv and gl to self.content
        self.priority = self.get_audit_priority()
        self.relevant_totes = "Totes not loaded yet."  # set of totes containing HRV
        self.comment = None

    def get_info(self, domain):
        """
        Update and save database.json; add 3 columns (price, hrv, gl) to self.content if is pd.core.frame.DataFrame .
        :param domain:    str of relevant amazon website's domain (e.g.: "it", "com", "fr", etc. )
        :return:          None
        """
        if type(self.content) is not pd.core.frame.DataFrame:
            print(COLOR_RED + self.content)

        else:
            print(COLOR + "\nData downloaded from Rodeo. Getting prices, hrv and gl from FcResearch.\n")
            asin_set = set(self.content["FN SKU"])          # remove duplicates

            self.database = update_database(self.database, asin_set, domain, self.fc)
            print(COLOR + "\nData downloaded.")

            print(COLOR + "Updating database.json .")
            # waste of time updating every time, but otherwise process could be terminated before saving
            file = FOLDER + "database.json"
            with open(file, "w") as json_write:
                json.dump(self.database, json_write)
            print(COLOR + f"{file} updated.")

            prices = {asin: self.database[asin]["price"] for asin in asin_set}
            hrvs = {asin: self.database[asin]["hrv"] for asin in asin_set}
            gl = {asin: self.database[asin]["gl"] for asin in asin_set}

            self.content["list_price"] = self.content["FN SKU"].map(prices)
            self.content["hrv"] = self.content["FN SKU"].map(hrvs)
            self.content["gl"] = self.content["FN SKU"].map(gl)

    def get_audit_priority(self):
        """
        Get df priority for audit.
        :param self: self.content must be pd DataFrame with 'hrv' and 'list_price' columns.
        :return:     str
        """
        if type(self.content) is pd.core.frame.DataFrame:
            if True not in self.content.values:
                priority = "Not relevant"
            else:
                only_hrv = self.content.loc[self.content["hrv"] == True]
                # Replace empty cells with 0 to avoid errors
                hrv_value_series = only_hrv["list_price"].replace("", 0) * only_hrv["Quantity"]
                hrv_value = hrv_value_series.sum()
                if hrv_value > 500:
                    priority = "High"
                elif hrv_value > 300:
                    priority = "Medium"
                else:
                    priority = "Low"
            return priority

    def audit(self, escalation_msg):
        """
        Handle audit process by creating an instance of Tote class for every relevant tote.
        :param escalation_msg: str with error message
        :return:               None
        """
        if type(self.content) is pd.core.frame.DataFrame:
            no_audit_needed = "No Audit Needed"
            no_comment_needed = "No Comment Needed"
            self.content["Pallet_Priority"] = self.priority

            if True not in self.content["hrv"].values:
                print(COLOR + f"There are no totes containing HRV in {self.pallet_code}.")
                self.content["Audit_Result"] = no_audit_needed
                self.content["Comment"] = no_comment_needed
                # print(df["hrv"])
            else:
                # get pd Series of totes containing HRV
                df_hrv = self.content.loc[self.content["hrv"] == True, "Scannable ID"]
                self.relevant_totes = set(df_hrv)  # remove duplicates

                # audit_checklist = {"tsX..." : class Tote(tsX...), ... }  dict with tote codes and class Tote
                audit_checklist = {tote_code: Tote(tote_code, self.content.loc[self.content["Scannable ID"] ==
                                   tote_code]) for tote_code in self.relevant_totes}

                # is_audited = {"tsX..." : False, "tsX...": "Passed", ...} dict with audit result.
                is_audited = {tote: False for tote in audit_checklist}         # Keep track if need to audit other totes

                while False in is_audited.values():
                    print(COLOR + "Please insert exit to leave menu or scan one among:")
                    for tote_code in audit_checklist:
                        if audit_checklist[tote_code].audited is False:
                            print(COLOR + f"Tote: {tote_code}")
                    print(COLOR + "->", end="")
                    auditing = input()

                    if auditing.lower() == "exit":
                        right_answer = False                # used for while loop: wait for valid answer

                        while not right_answer:
                            for tote_code in audit_checklist:
                                if audit_checklist[tote_code].audited is False:
                                    print(COLOR + f"Tote: {tote_code}")

                            print(COLOR + "Have not been audited. Are you sure you want to interrupt auditing?(yes/no)"
                                          "\n->", end="")
                            confirm = input()
                            if confirm.lower() == "yes":
                                print(COLOR_RED + f"{self.pallet_code} audit was not completed. Please start audit "
                                                  f"again or start escalation procedure. Was audit interrupted because "
                                                  f"a tote was missing? (yes/no)\n->", end="")
                                is_failed = input()
                                if is_failed.lower() == "yes":
                                    for tote_code in audit_checklist:
                                        if audit_checklist[tote_code].audited is False:
                                            audit_checklist[tote_code].audited = "Tote missing"
                                            print(COLOR_RED + f"{tote_code} is registered as missing.")
                                    for tote_code in is_audited:
                                        if is_audited[tote_code] is False:
                                            is_audited[tote_code] = "Tote missing"

                                    right_answer = True
                                elif 'n' in is_failed:
                                    print(COLOR + "Insert a comment explaining why the audit was interrupted (e.g.: "
                                                  "@login requested the pallet to be transshipped immediately)?")
                                    for tote_code in audit_checklist:
                                        if audit_checklist[tote_code].audited is False:
                                            audit_checklist[tote_code].audited = "Audit Interrupted"
                                    for tote_code in is_audited:
                                        if is_audited[tote_code] is False:
                                            is_audited[tote_code] = "Audit Interrupted"
                                    right_answer = True
                            elif 'n' in confirm:
                                print(COLOR + "Audit has not been interrupted.")
                                break

                    elif auditing not in self.relevant_totes:
                        print(COLOR_RED + f"{auditing} is not a tote containing HRV.")

                    else:  # start tote audit
                        audit_checklist[auditing].audit(escalation_msg, self.fc)
                        is_audited[auditing] = audit_checklist[auditing].audited

                print(COLOR + "Insert a brief comment. If someone showed suspicious behaviour, please signal it here"
                              " (WATCH OUT: you will not be able to modify the comment!).\n->", end="")
                comment = input()
                self.comment = comment
                self.content["Comment"] = self.comment
                self.content["Audit_Result"] = self.content["Scannable ID"].map(is_audited)
                self.content["Audit_Result"] = self.content["Audit_Result"].fillna(no_audit_needed)


if __name__ == "__main__":
    print("Testing Pallet.get_audit_priority()")
    test = {"ASIN": ["A", "B", "C"], "Quantity": [1, 2, 3], "hrv": [True, False, True], "list_price": [1, 10, 2]}
    test = pd.DataFrame(test)
    print(test)
    if True not in test.values:
        priorit = "Not relevant"
    else:
        hrv_only = test.loc[test["hrv"] == True]
        # Replace empty cells with 0 to avoid errors
        hrv_value_series = hrv_only["list_price"].replace("", 0) * hrv_only["Quantity"]
        hrv_value = hrv_value_series.sum()
        if hrv_value > 500:
            priorit = "High"
        elif hrv_value > 300:
            priorit = "Medium"
        else:
            priorit = "Low"

    print(f"Test total hrv value is {hrv_value}\nTest priority is {priorit}.")
    breakpoint()
