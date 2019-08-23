from num_to_asin import num_to_asin
from constants import COLOR, COLOR_RED, COLOR_GREEN


class Tote:
    """
    Create Tote object with .audit() method.
    """
    def __init__(self, tote_code, df_content):
        """
        :param tote_code:   str (e.g.: tsX... )
        :param df_content:  pd DataFrame
        """
        self.tote_code = tote_code
        self.df_content = df_content        # pd DataFrame
        self.asins_dict = False             # dict of ASINs in tote
        self.asins_checked = False          # deep copy of self.asins_dict to count ASINs audited
        self.missing_asins = False          # deep copy of asins_checked but keys with value == 0 removed
        self.audited = False

    def audit(self, escalation_msg, fc):
        print(COLOR + f"Auditing {self.tote_code}. Please scan all items in tote. Insert 'exit' to stop.")

        self.df_content = self.df_content.reset_index(drop=True)  # reset index to allow enumerate to work

        # create dict with ASINs
        self.asins_dict = dict()        # {Scannable ID: Quantity} add duplicates in pd DataFrame
        self.asins_checked = dict()     # deep copy of self.asins_dict
        for row, elem in enumerate(self.df_content["FN SKU"]):
            if elem in self.asins_dict:
                self.asins_dict[elem] += self.df_content["Quantity"][row]
                self.asins_checked[elem] += self.df_content["Quantity"][row]
            else:
                self.asins_dict[elem] = self.df_content["Quantity"][row]
                self.asins_checked[elem] = self.df_content["Quantity"][row]
        #

        print(COLOR + f"{self.tote_code} contains:")
        for asin in self.asins_dict:
            print(COLOR + f"{asin} : {self.asins_dict[asin]}")

        while sum(self.asins_checked.values()) > 0:
            print(COLOR + "Please scan item or insert 'exit' to stop\n->", end="")
            item = input()

            if item.lower() == "exit":
                for elem in self.asins_checked:
                    if self.asins_checked[elem] != 0:
                        print(COLOR + f"{elem} : {self.asins_checked[elem]}")
                print(COLOR + f"are still missing. If these items are not in {self.tote_code}, {escalation_msg}")
                print(COLOR + f"Do you want to stop auditing {self.tote_code}?(y/n)\n->")
                confirmation = input()
                if 'y' in confirmation.lower():
                    break
                else:
                    print(COLOR + f"Please keep auditing {self.tote_code}.")

            elif item in self.asins_checked:
                if self.asins_checked[item] > 0:
                    print(COLOR_GREEN + "\nSUCCESS!")
                    print(COLOR + f"Audited: {item}")
                    self.asins_checked[item] -= 1

                else:  # elif tote_content[item] == 0:  # over quantity
                    print(COLOR + "\nERROR!!!")
                    print(COLOR + f"All the items with this ASIN have been already scanned. {escalation_msg}")

            else:  # elif item != "exit" and item not in tote_content:
                try:
                    right_code = num_to_asin(item, fc)
                    if right_code is None:
                        print(COLOR + f"This product number or ASIN was not recognised. {escalation_msg}")

                    elif right_code in self.asins_checked:
                        if self.asins_checked[right_code] > 0:
                            print(COLOR_GREEN + f"{item} converted to {right_code}.\nSUCCESS!!")
                            self.asins_checked[right_code] -= 1
                        else:  # over quantity
                            print(COLOR + f"All the items with this ASIN have been already scanned {escalation_msg}")

                    else:
                        print(COLOR + f"{item} was recognized as ASIN {right_code}, but this item should not be in "
                              f"{self.tote_code}. {escalation_msg}")

                except BaseException as e:
                    print(COLOR + f"\nERROR!! {e.message}\n. Wrong ASIN: {item}. {escalation_msg}")

        print(COLOR + f"Finished auditing {self.tote_code}")

        if sum(self.asins_checked.values()) == 0:
            print(COLOR_GREEN + f"{self.tote_code} audit was successful!")
            self.audited = "Audit Passed"
        else:
            answer = False
            while not answer:
                print(COLOR_RED + f"{self.tote_code} audit was not completed. Please start audit again or start "
                                  f"escalation procedure. Was audit interrupted because audit FAILED? (y/n)\n->", end="")
                is_failed = input()
                is_failed = is_failed.lower()
                if 'y' in is_failed:
                    print(COLOR_RED + f"These items were not found in {self.tote_code}:")
                    self.missing_asins = dict()
                    for elem in self.asins_checked:
                        if self.asins_checked[elem] != 0:
                            self.missing_asins[elem] = self.asins_checked[elem]
                            print(COLOR + f"{elem} : {self.asins_checked[elem]}")
                    self.audited = "Failed. Missing:" + str(self.missing_asins)
                    answer = True

                elif 'n' in is_failed:
                    self.audited = "Interrupted"
                    print(COLOR + "Why was the audit interrupted (e.g.: @login requested the pallet to be transshipped "
                          "immediately)?")
                    answer = True


if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame({"FN SKU": [1, 2], "Quantity": [3, 4]})
    a = Tote("a", df)
    a.audit("AA", "MXP5")
