import pandas as pd

from constants import COLOR, COLOR_RED
from version import __mail__


def ask_is_strapped(pallet_content, pallet_code):
    """
    Makes final question depending on audit result.
    :param pallet_content: pd dataframe
    :param pallet_code: str
    :return:
    """
    confirm_anyway = f"please signal the bug to {__mail__} and confirm anyway."
    while True:
        if "Tote missing" in pallet_content["Audit_Result"].values or True in \
                pallet_content["Audit_Result"].str.contains("Failed").values:
            print(COLOR_RED + f"\nHave you started escalation procedure?(yes/no)\n->", end="")
            confirm = input().lower()
            if confirm == "yes":
                break
            else:
                print(COLOR_RED + f"Please start escalation procedure for {pallet_code}. Contact a problem "
                                  f"solver or an Area Manager.\nIf the audit was not interrupted, {confirm_anyway}")

        elif "Audit Interrupted" in pallet_content["Audit_Result"].values:
            print(COLOR + f"\nPlease confirm that audit was interrupted.(y/n)\n->", end="")
            confirm = input().lower()
            if confirm[0] == "y":
                break
            else:
                print(COLOR_RED + f"You did not confirm that the audit was interrupted.\nIf the audit was not "
                                  f"interrupted, {confirm_anyway}")

        else:
            print(COLOR + f"\nHave you checked that {pallet_code} has been strapped?(yes/no)\n->", end="")
            confirm = input().lower()
            if confirm == "yes":
                break
            else:
                print(COLOR_RED + f"Please check that {pallet_code} has been strapped.\nIf the audit was not "
                                  f"successful, {confirm_anyway}")


if __name__ == "__main__":
    from colorama import init


    class FakePallet:
        def __init__(self, pallet_code, content):
            self.pallet_code = pallet_code
            self.content = content

    init(autoreset=True)
    df = pd.DataFrame({"Audit_Result": [""]})
    ask_is_strapped(FakePallet("PALLET__4zcxxNf_Z", df))
