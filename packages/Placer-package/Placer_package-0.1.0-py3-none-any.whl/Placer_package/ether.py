# Welcome to ether
# How to use:
# 1 import ether into your python file
# 2 use the ether.newlog() to insert unrecognized inputs to the etherlogs
# Done!


savefile = 'logs/ether_logs.txt'

ether_initiated = False


def newlog(var):
    global ether_initiated

    if not ether_initiated:
        ether_initiated = True

        # Creates a ether_logs.txt file if non is present
        try:
            with open(savefile, "x") as f:
                f.write("This is the ether_logs file\n" + "Here all the unrecognized words are stored\n")
                f.write("It currently holds\n" + "0\n" + "logs" + "\n\n")

        except:
            pass


        # changes the number of logs in the header of the file
        with open(savefile, 'r') as file:
            fileinput = file.readlines()

        event_number = str(int(fileinput[3]) + 1)
        fileinput[3] = event_number + "\n"

        with open(savefile, 'w', encoding='utf-8') as file:
            file.writelines(fileinput)

        # Adds a new section for logs
        with open(savefile, "a") as f:
            f.write("\n\n" + "Event number " + str(event_number) + ":\n")

    # Inserts the word into the ether_logs
    with open(savefile, "a") as f:
        f.write(str(var) + "\n")
