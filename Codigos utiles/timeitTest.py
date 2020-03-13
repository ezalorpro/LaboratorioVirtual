from time import time
import numpy as np

x = np.linspace(0, 10,500)
y = np.linspace(0, 10, 500)

start = time()

for i in range(3000):
    sum([a*b for a,b in zip(x,y)])/sum(y)

print(f'Tiempo: {time() - start}')