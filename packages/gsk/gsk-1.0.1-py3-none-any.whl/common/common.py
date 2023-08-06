import math

def isset(variable):
	return variable in locals() or variable in globals()

def round_up(n, decimals=0):
    '''
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier
    '''
    return round_up1(n, decimals)

def round_up1(n, decimals=0):
    multiplier = 10 ** decimals
    nn = n*multiplier
    r1 = round(nn,0)
    if nn - r1 > 0.4999999999999:
        r1 = r1 + 1

    r1 = r1 / multiplier
    return r1


def  Array2Sql(ar):
    s = "','"
    # print(ar)
    out = "'"+s.join(ar)+"'"
    # print(out)
    return out
    