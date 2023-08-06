from decimal import Decimal, ROUND_HALF_UP
def round(x,digit):
    digit = 10**((-1*(digit)))

    return float(Decimal(x).quantize(Decimal(str(digit)), ROUND_HALF_UP))

def test():
    return  '0.038'
