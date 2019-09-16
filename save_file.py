import time

from constants import COLOR, COLOR_RED


def save_xlsx(df, filename):
    """
    Handle some possible pitfalls when saving a pd DataFrame. If first input does not work, defaults to '.xlsx'.
    :param df:          pd DataFrame
    :param filename:    must include file extension
    :return:            None
    """
    while True:     # assign valid file name
        try:
            df.to_excel(filename, index=False)
            print(COLOR + f"Pallet content has been exported to {filename}")
            break

        except PermissionError:
            time.sleep(2.0)                          # wait. Useful if another instance of the tool is saving the excel
            try:                                                    # try again
                df.to_excel(filename, index=False)
                print(COLOR + f"Pallet content has been exported to {filename}")
                break
            except PermissionError:
                print(COLOR_RED + f"Query result cannot be saved because {filename} is already open. Insert a "
                                  f"different file name to try again\n->", end="")
                filename = input()
                while len(filename) < 1:
                    print(COLOR_RED + "Insert a valid file name!")
                    filename = input()
                if filename[-5:] != '.xlsx':
                    filename += '.xlsx'

        except BaseException as e:
            print(COLOR_RED + f"There was an error, please try again. FATAL ERROR: {e}")
            print(COLOR + "Please try with a different file name:\n->")
            while len(filename) < 1:
                print(COLOR_RED + "Insert a valid file name!")
                filename = input()
            if filename[-5:] != '.xlsx':
                filename += '.xlsx'
