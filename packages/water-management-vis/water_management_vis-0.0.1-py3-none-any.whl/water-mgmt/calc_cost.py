import math
from .tankwater_slabcalc import tank_water_slab

"""
Exception class to raise exception
"""
class NotAllowed(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message

"""
    If the apartment type is 2, then consumption is 900 (3 (persons) * 30 (days) * 10 (litres))
    If the apartment type is 3, then consumption is 1500 (5 (persons) * 30 (days) * 10 (litres))
    Calculates cost consumption for corporate water and borewell water based on input ratio extracted
    Calls calculate_guest_cost() on condition and returns output with total consumption and cost
"""
class CalcCost:
    def calculate_cost(self,apartment_type:int,corporate_ratio:int,bore_ratio:int,guests:int):
        if apartment_type == 2:
            water_consumption = 900
        elif apartment_type == 3:
            water_consumption = 1500
        else:
            raise NotAllowed("Invalid apartment type")

        cal_corp_consump = round((water_consumption*corporate_ratio)/(corporate_ratio+bore_ratio))
        cal_bore_consump = round((water_consumption*bore_ratio)/(corporate_ratio+bore_ratio))

        cal_corp_cost = math.ceil(cal_corp_consump * 1)
        cal_bore_cost = math.ceil(cal_bore_consump * 1.5)
        
        if guests > 0:
            guest_cost = self.calculate_guest_cost(guests)
        else:
            guest_cost = 0

        total_consumption = water_consumption + guests*30*10
        total_cost = round(guest_cost) + cal_corp_cost + cal_bore_cost
        return total_consumption,total_cost 

    """
    Calculate the cost and consumption for the guests if any guests are present
    """

    def calculate_guest_cost(self,guests:int) -> int:
        guests_consumption = guests*30*10
        return tank_water_slab(guests_consumption)