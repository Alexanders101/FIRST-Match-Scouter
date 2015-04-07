import numpy as np

def string_to_bool(inp):
    inp = str(inp)
    if inp == "True":
        return True
    else:
        return False

def create_csv(rankings, name):
        np.savetxt("%s.csv" % name, rankings, delimiter=",")
