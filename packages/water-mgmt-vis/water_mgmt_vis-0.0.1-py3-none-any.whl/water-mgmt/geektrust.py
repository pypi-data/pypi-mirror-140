import sys
from .calc_cost import CalcCost, NotAllowed


class WaterManagement:
    """
    WaterManagement class calculates total water consumption and the cost 
    depending on the inputs provided.
    a)  Method read_input() reads through the input file and extracts the information from the input file 
        like ALLOT_WATER, GUESTS and BILL where GUESTS can appear multiple times where as others 
        should appear only once and at the correct positions.
        new Exception class has been imported for checking on various exceptions like 
        1. If ALLOT_WATER has been at the start of the input
        2. If BILL has been at the end of the input 
    b)  Once all the variables are extracted from input, calculate_cost() is called which returns the 
        total amount of consumption and total cost
    """
    def read_input(self,inputfile):
        guests = 0
        ALLOT_WATER_FLAG = 'N'
        GUESTS_FLAG = 'N'
        BILL_FLAG = 'N'
        for line in inputfile.readlines():
            if (ALLOT_WATER_FLAG == 'N') & (BILL_FLAG == 'Y'):
                raise NotAllowed("BILL allowed only at end")
            if (GUESTS_FLAG == 'Y') & (ALLOT_WATER_FLAG == 'N'):
                raise NotAllowed("ALLOT_WATER should be at the start")

            if 'ALLOT_WATER' in line:
                if ALLOT_WATER_FLAG == 'N':
                    ALLOT_WATER_FLAG = 'Y'
                else:
                    raise NotAllowed("Allowed Only once")
                apartment_type = int(line.split(" ")[1])
                corporate_ratio = int(line.split(" ")[2].split(":")[0])
                bore_ratio = int(line.split(" ")[2].split(":")[1])

            elif 'ADD_GUESTS' in line:
                guests += int(line.split(" ")[1])

            elif 'BILL' == line:
                if BILL_FLAG == 'N':
                    BILL_FLAG = 'Y'
                else:
                    raise NotAllowed("Allowed Only once")

        if ALLOT_WATER_FLAG == 'N' or BILL_FLAG == 'N':
            raise NotAllowed("Allowed atleast once")

        costfn = CalcCost()
        consumption,cost = costfn.calculate_cost(apartment_type,corporate_ratio,bore_ratio,guests) 

        if BILL_FLAG == 'Y':
            print(*[consumption,cost])
    

""" def main():
    input_file = sys.argv[1]
    input_file = open(input_file, 'r+')
    x = WaterManagement()
    x.read_input(input_file)
    input_file.close()
    
if __name__ == "__main__":
    main()
 """

