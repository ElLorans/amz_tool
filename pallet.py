import pandas as pd
import json
from asin_info import update_database
from rodeo_query import rodeo_query
from tote import Tote
from constants import COLOR, COLOR_RED, FOLDER


class Pallet:
    def __init__(self, fc, pallet_code, database, country_code):
        self.fc = fc
        self.pallet_code = pallet_code
        self.database = database  # dict {asin: {"price": float, "hrv": bool, "gl": str}, ...}
        self.content = rodeo_query(self.fc, self.pallet_code)
        self.get_info(country_code)  # add price, hrv and gl to self.content
        self.priority = self.get_audit_priority()
        self.relevant_totes = "Totes not loaded yet."  # set of totes containing HRV
        self.comment = None

    def get_info(self, country_code):
        """
        Update and save database.json; add 3 columns (price, hrv, gl) to self.content if is pd.core.frame.DatFrame .
        :param country_code:    str (e.g.: "it")
        :return:                None
        """
        if type(self.content) is not pd.core.frame.DataFrame:
            print(COLOR + self.content)
        else:
            print(COLOR + "\nData downloaded from Rodeo. Getting prices, hrv and gl from FcResearch.\n")
            asin_set = set(self.content["FN SKU"])
            self.database = update_database(self.database, asin_set, country_code, self.fc)
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
            hrv_prices = self.content.loc[self.content["hrv"] == True, "list_price"]
            hrv_tot_price = hrv_prices.replace("", 0).sum()
            if hrv_tot_price > 500:
                priority = "High"
            elif hrv_tot_price > 300:
                priority = "Medium"
            elif len(hrv_prices) > 0:
                priority = "Low"
            else:
                priority = "Not relevant"
            return priority

    def audit(self, escalation_msg):
        if type(self.content) is pd.core.frame.DataFrame:
            if True not in self.content["hrv"].values:
                print(COLOR + f"There are no totes containing HRV in {self.pallet_code}.")
                self.content["Pallet_Priority"] = self.priority
                self.content["Audit_Result"] = "Not needed"
                self.content["Comment"] = "Not needed"
                # print(df["hrv"])
            else:
                # get pd Series of totes containing HRV
                df_hrv = self.content.loc[self.content["hrv"] == True, "Scannable ID"]
                self.relevant_totes = set(df_hrv)  # remove duplicates

                # audit_checklist = {"tsX..." : class Tote(tsX...), ... }  dict with tote codes and class Tote
                audit_checklist = {tote_code: Tote(tote_code, self.content.loc[self.content["Scannable ID"] ==
                                                                               tote_code]) for tote_code in
                                   self.relevant_totes}
                # is_audited = {"tsX..." : False, "tsX...": "Passed", ...} dict with audit result.
                # Keep track if need to audit other totes
                is_audited = {tote: False for tote in audit_checklist}

                while False in is_audited.values():
                    print(COLOR + "Please insert exit to leave menu or scan one among:")
                    for tote_code in audit_checklist:
                        if audit_checklist[tote_code].audited is False:
                            print(COLOR + f"Tote: {tote_code}")
                    print(COLOR + "->", end="")
                    auditing = input()

                    if auditing.lower() == "exit":
                        right_answer = False  # wait for valid answer

                        while not right_answer:
                            for tote_code in audit_checklist:
                                if audit_checklist[tote_code].audited is False:
                                    print(COLOR + f"Tote: {tote_code}")

                            print(COLOR + "Have not been audited. Are you sure you want to interrupt auditing?(y/n)\n"
                                          "->", end="")
                            confirm = input()
                            confirm = confirm.lower()
                            if 'y' in confirm:
                                print(COLOR_RED + f"{self.pallet_code} audit was not completed. Please start audit "
                                                  f"again or start escalation procedure. Was audit interrupted because a"
                                                  f" tote was missing? (y/n)\n->")
                                is_failed = input()
                                is_failed = is_failed.lower()
                                if 'y' in is_failed:
                                    print(COLOR + "Please insert a comment stating also which tote was missing.")
                                    for tote_code in audit_checklist:
                                        if audit_checklist[tote_code].audited is False:
                                            audit_checklist[tote_code].audited = "Tote missing"
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

                        self.content["Audit_Result"] = self.content["Scannable ID"].map(is_audited)
                        self.content["Audit_Result"] = self.content["Audit_Result"].fillna("No Audit Needed")
                        print(COLOR + "->", end="")
                        self.comment = input()
                        self.content["Comment"] = self.comment

                    elif auditing not in self.relevant_totes:
                        print(COLOR_RED + f"{auditing} is not a tote containing HRV.")

                    else:  # start tote audit
                        audit_checklist[auditing].audit(escalation_msg, self.fc)
                        is_audited[auditing] = audit_checklist[auditing].audited

                print(COLOR + "Insert a brief comment. (WATCH OUT: you will not be able to modify the comment!)\n->",
                      end="")
                comment = input()
                self.comment = comment
                self.content["Comment"] = self.comment
                self.content["Audit_Result"] = self.content["Scannable ID"].map(is_audited)
                self.content["Audit_Result"] = self.content["Audit_Result"].fillna("No Audit Needed")
