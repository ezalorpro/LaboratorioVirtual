entradas = [
    {
        'nombre': 'error',
        'numeroE': 3,
        'etiquetas':
            [
                {
                    'nombre': 'bajo',
                    'mf': 'triam',
                    'definicion': [-11, -10, 0],},
                {
                    'nombre': 'medio',
                    'mf': 'triam',
                    'definicion': [-10, 0, 10],},
                {
                    'nombre': 'alto',
                    'mf': 'triam',
                    'definicion': [0, 10, 11],},
            ],
        'rango': [-10, 10],
        'metadata': None
    },
    {
        'nombre': 'd_error',
        'numeroE': 3,
        'etiquetas':
            [
                {
                    'nombre': 'bajo',
                    'mf': 'triam',
                    'definicion': [-11, -10, 0],},
                {
                    'nombre': 'medio',
                    'mf': 'triam',
                    'definicion': [-10, 0, 10],},
                {
                    'nombre': 'alto',
                    'mf': 'triam',
                    'definicion': [0, 10, 11],},
            ],
        'rango': [-10, 10],
        'metadata': None
    }
]

inputIndex = 1
etiquetaInputIndex = 1

for i in entradas[inputIndex]['etiquetas']:
    for k, v in i.items():
        print(f'{k} : {v}')
    print('\n')