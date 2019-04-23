import utils
import random
from statistics import mean, median, mode, StatisticsError


def getdist():
    low = None
    while low == None:
        low = input("Enter Low Value:")
        try:
            low = int(low)
        except ValueError:
            low = None
          
    high = None
    while high == None:
        high = input("Enter High Value:")
        try:
            high = int(high)
        except ValueError:
            high = None

    mode = None
    while mode == None:
        mode = input("Enter Mode Value:")
        try:
            mode = int(mode)
        except ValueError:
            mode = None
    return (low, high, mode)

def __main__():
#a program to run the util.bimodal function to get an idea of the range of numbers it
#produces for given distributions. utils.bimodal is the function used to set commodities prices
#for the stations during the bigbang

    dist1 = None
    dist2 = None
    if dist1 == None:
        print ("Enter Distribution 1:")
        dist1 = (low1, high1, mode1) = getdist()
        print(dist1)

    if dist2 == None:
        print ("Enter Distribution 2:")
        dist2 = (low2, high2, mode2) = getdist()
        print(dist2)

    n = None
    while n == None:
        n = input("number of values:")
        try:
            n = int(n)
        except ValueError:
            n = None
    values = []
    count = 0
    while count < n:
        count += 1
        x = round(utils.bimodal(*dist1, *dist2), 0)
        values.append(x)
  
    print(f"Bimodal: {dist1} {dist2}") 
    print(f"Values: {len(values)}") 
    print(f"Max: {max(values)}")
    print(f"Min: {min(values)}")
    print(f"Mean: {mean(values)}")
    print(f"Median: {median(values)}")
    try:
        print(f"Mode: {mode(values)}")
    except StatisticsError:
        print(f"Mode: {max(values, key=values.count)}")
    
    values = []
    count = 0
    while count < n:
        count += 1
        x =  random.triangular(*dist1)
        values.append(x)
   
    print(f"Dist1: {dist1}") 
    print(f"Values: {len(values)}") 
    print(f"Max: {max(values)}")
    print(f"Min: {min(values)}")
    print(f"Mean: {mean(values)}")
    print(f"Median: {median(values)}")
    try:
        print(f"Mode: {mode(values)}")
    except StatisticsError:
        print(f"Mode: {max(values, key=values.count)}")

    values = []
    count = 0
    while count < n:
        count += 1
        x =  random.triangular(*dist2)
        values.append(x)
   
    print(f"Dist2: {dist2}") 
    print(f"Values: {len(values)}") 
    print(f"Max: {max(values)}")
    print(f"Min: {min(values)}")
    print(f"Mean: {mean(values)}")
    print(f"Median: {median(values)}")
    try:
        print(f"Mode: {mode(values)}")
    except StatisticsError:
        print(f"Mode: {max(values, key=values.count)}")


if __name__ == "__main__":
    # execute only if run as a script
    __main__()
