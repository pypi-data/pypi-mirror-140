
# This variable sets the save file for the function including usernames
savefile_wu = 'highscore_wu.txt'

# This variable sets the value file for the function including usernames
savefile = "highscores.txt"



# This function checks if the project contains a savefile_wu and creates one if there is not

def highscore_wu_file():
    try:
        with open(savefile_wu, 'r') as file:
            fileinput = file.readlines()
    except:
        with open(savefile_wu, 'w') as file:
            file.write("This is the highscore file\n")
            file.write("Here are all hightscores saved\n")
            file.write("\n")
            file.write(("Player\n" + "0\n") * 3)




def readhighscore_wu():
    for i in range (6):
        with open(savefile_wu, 'r') as file:
            print(file.readlines()[i + 3], end="")


# This function inserts the username and highscore to the savefile_wu file

def highscore_wu(score, username):
    savescore = []
    highscore = []


    with open(savefile_wu, 'r') as file:
        savescore = file.readlines()
    for i in range(3):
        highscore.append(savescore[i * 2 + 4])
    # Copies the entire highscore_wu file and creates a highscore values list
    print(int(max(highscore)))

    if score > int(max(highscore)):
    # Checks if the score if higer than any highscore
        for i in range(3):
            if score > int(highscore[i]):
                savescore[i * 2 + 3] = username + "\n"
                highscore.insert(i, str(score) + "\n")
                del highscore[-1]
                # Replaces the old player name with the new one

                for i in range(3):
                    savescore[i * 2 + 4] = highscore[i]
                # Updates the highscore list to savescore

                break

        with open(savefile_wu, 'w', encoding='utf-8') as file:
            file.writelines(savescore)
        # Updates the highscore_wu file


# --------------------------------------------------------------------------------------------------------------


def highscore_file():
    global savefile

    savefile = 'highscore.txt'

    try:
        with open(savefile, 'r') as file:
            fileinput = file.readlines()
    except:
        with open(savefile, 'w') as file:
            file.write("This is the highscore file\n")
            file.write("Here are all hightscores saved\n")
            file.write("\n")
            file.write("0\n" * 3)


def highscore(score):

    with open(savefile, 'r') as file:
        highscore = file.readlines()

    for i in range(3):
        if score > int(highscore[i + 3]):
            highscore.insert(i + 3, str(score) + "\n")
            del highscore[-1]
            break

    with open(savefile, 'w', encoding='utf-8') as file:
        file.writelines(highscore)
