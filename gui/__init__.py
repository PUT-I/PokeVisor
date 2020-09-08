from random import randint
from tkinter import *
rows = []
cols = []


def players_number(players):
    for j in range(players):
        e = Entry(relief=RIDGE)
        e.grid(row=1, column=j, sticky=NSEW)
        e.insert(END, 'Player' + str(j + 1))
        cols.append(e)
    rows.append(cols)

    for j in range(players):
        e = Entry(relief=RIDGE)
        e.grid(row=2, column=j, sticky=NSEW)
        e.insert(END, randint(1, 1000))
        cols.append(e)
    rows.append(cols)

    for j in range(players):
        e = Entry(relief=RIDGE)
        e.grid(row=3, column=j, sticky=NSEW)
        s = ['AsSpades', 'KingHearts', 'TwoDiamonds']
        e.insert(END, listToString(s))
        cols.append(e)
    rows.append(cols)


def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
        str1 += ", "
    return str1


players_number(5)
mainloop()
