from skfuzzy import control as fuzz
from skfuzzy.membership import generatemf
import numpy as np

entrada = fuzz.Antecedent(np.linspace(-10, 10, 5), 'Velocidad')
entrada['hola'] = generatemf.trimf(entrada.universe, [0, 1, 2])
print(entrada.terms.pop('hola'))
entrada.label = 'error'
print(entrada['hola'])