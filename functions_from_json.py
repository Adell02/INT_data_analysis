import pandas as pd
# -*- coding: utf-8 -*-
import json
from functions import *
from plots_generation import *
from Analytic_functions import*
from consumption_vs_temp import*

def execute_functions_from_json(json_file, dataframe):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    plots = []

    for f in data:
        parameters_list = f.get("parameters", [])
        str_f = f['function'] + '('
        
        for i, parameter in enumerate(parameters_list):
            if parameter in f:
                if isinstance(f[parameter], list):
                    quoted_elements = ["'" + str(element) + "'" for element in f[parameter]]
                    str_f = str_f + parameter + '=[' + ', '.join(quoted_elements) + ']'
                else:
                    str_f = str_f + parameter + '=' + "'" + str(f[parameter]) + "'"
            else:
                str_f = str_f + parameter
            
            if i < len(parameters_list) - 1:
                str_f = str_f + ','
        
        str_f = str_f + ')'
        

        try:
            # Evaluar la cadena de código y agregar el resultado a la lista
            result = eval(str_f)
            plots.append(result)
            print(str_f)
        except Exception as e:
            print(f"Error al ejecutar '{str_f}': {e}")

    return plots

