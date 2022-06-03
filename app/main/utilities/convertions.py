def convert_tank_parameters(tank_parameters=["sa"]):
    tank_parameters_list = []
    for tank_parameter in tank_parameters:
        tank_parameter_dictionary = {
            "tankId": "E1001",
            "parameter": "WtrLvl",
            "tankMinValue": "2",
            "tankMaxValue": "3"
        }
        tank_parameters_list.append(tank_parameter_dictionary)

    return tank_parameters_list
