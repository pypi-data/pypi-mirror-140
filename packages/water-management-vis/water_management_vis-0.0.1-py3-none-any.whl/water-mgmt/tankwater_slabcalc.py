"""
Calculate the tank wanter based on the slab (brackets)
Calculation is as below:
    0 to 500 - 2 rupees 
    501 to 1500 - 3 rupees
    1501 to 3000 - 5 rupees
    3001 above - 8 rupees
The method calculates similar to how tax gets calculated
""" 
def tank_water_slab(consumption:int) -> int:
    brackets = {(1,500):2,(501,1500):3,(1501,3000):5,(3001,1000000):8 }
    total = 0
    for i in brackets:
        if consumption > 0:
            total += (min(consumption,(i[1]-i[0]+1)) * brackets[i])
            consumption -= min(consumption,(i[1]-i[0]+1))
    return round(total)