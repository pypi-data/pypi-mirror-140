yes = ["Yes", "yes", "Y", "y", "Yes!", "yes!", "Ja", "ja"]
no = ["No", "no", "N", "n", "No!", "no!", "Nej", "nej"]
stop = ["Stop", "stop", "Stop!", "stop!"]
cancel = ["Cancel", "cancel"]

def s(var):
    global yes
    global no
    global stop
    global cancel

    if var in yes:
        var = "yes"

    elif var in no:
        var = "no"

    elif var == stop:
        var = "stop"

    elif var in cancel:
        var = "cancel"


    return var


#---------------------------------------------------------------------------------------------#


def sf(var):
    global yes
    global no
    global stop
    global cancel

    if var in yes:
        var = "yes"

    elif var in no:
        var = "no"

    elif var == stop:
        var = "stop"

    elif var in cancel:
        var = "cancel"

    else:
        var = "error"

    return var
