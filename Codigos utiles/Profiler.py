import cProfile
from fuzzRuleProfile import ejecutar
import time
Controlador, error, derror = ejecutar()

cProfile.runctx(
    '''start = time.time()
for valores in zip(error, derror):
    Controlador.calcular_valor(valores)
print(f"Total time: {time.time() - start}")''',
    globals(),
    locals(),
    'myProfilingFile.pstats')
