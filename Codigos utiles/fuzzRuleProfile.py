from skfuzzy import control as ctrl
import numpy as np


class ControladorFuzzy:
# Creando controlador
    def __init__(self):
    # Creacion del controlador difuso    ---------------------------------------------------------------------------
    # Variables

        self.e_entrada = ctrl.Antecedent(np.linspace(-2500, 2500, 15), 'e_entrada') 	# Entrada error
        self.de_entrada = ctrl.Antecedent(np.linspace(-2500, 2500, 15), 'de_entrada') 	# Entrada desviacion de error

        self.fKp = ctrl.Consequent(np.linspace(0.5, 2, 25), 'fKp') 						# Ganancia Kp
        self.fKi = ctrl.Consequent(np.linspace(5, 100, 25), 'fKi') 						# Ganancia Ki
        self.fKd = ctrl.Consequent(np.linspace(0, 0.01, 25), 'fKd') 					# Ganancia Kd

        # Funciones de membresia ( triangulares )

        self.e_entrada.automf(3, names=["negativo", "cero", "positivo"])
        self.de_entrada.automf(3, names=["negativa", "cero", "positiva"])

        self.fKp.automf(3, names=["cero", "alto", "muy alto"])
        self.fKi.automf(3, names=["cero", "alto", "muy alto"])
        self.fKd.automf(3, names=["cero", "alto", "muy alto"])

        # Reglas -------------------------------------------------------------------------------------------------------

        rule1 = ctrl.Rule(self.e_entrada['negativo'] & self.de_entrada['negativa'],
                            consequent=[self.fKp['cero'], self.fKi['cero'], self.fKd['alto']])
        rule2 = ctrl.Rule(self.e_entrada['negativo'] & self.de_entrada['cero'],
                            consequent=[self.fKp['alto'], self.fKi['alto'], self.fKd['alto']])
        rule3 = ctrl.Rule(self.e_entrada['negativo'] & self.de_entrada['positiva'],
                            consequent=[self.fKp['muy alto'], self.fKi['muy alto'], self.fKd['alto']])

        rule4 = ctrl.Rule(self.e_entrada['cero'] & self.de_entrada['negativa'],
                            consequent=[self.fKp['cero'], self.fKi['cero'], self.fKd['cero']])
        rule5 = ctrl.Rule(self.e_entrada['cero'] & self.de_entrada['cero'],
                            consequent=[self.fKp['alto'], self.fKi['alto'], self.fKd['cero']])
        rule6 = ctrl.Rule(self.e_entrada['cero'] & self.de_entrada['positiva'],
                            consequent=[self.fKp['alto'], self.fKi['alto'], self.fKd['cero']])

        rule7 = ctrl.Rule(self.e_entrada['positivo'] & self.de_entrada['negativa'],
                            consequent=[self.fKp['muy alto'], self.fKi['muy alto'], self.fKd['muy alto']])
        rule8 = ctrl.Rule(self.e_entrada['positivo'] & self.de_entrada['cero'],
                            consequent=[self.fKp['muy alto'], self.fKi['muy alto'], self.fKd['alto']])
        rule9 = ctrl.Rule(self.e_entrada['positivo'] & self.de_entrada['positiva'],
                            consequent=[self.fKp['cero'], self.fKi['cero'], self.fKd['alto']])

        ganancia_control = ctrl.ControlSystem([rule1, rule2, rule3,
                                                rule4, rule5, rule6,
                                                rule7, rule8, rule9 ])

        self.ganancia_final = ctrl.ControlSystemSimulation(ganancia_control, flush_after_run=20000)

    def calcular_valor(self, valores):
        self.ganancia_final.input['e_entrada'] = valores[0]
        self.ganancia_final.input['de_entrada'] = valores[1]
        self.ganancia_final.compute()

def ejecutar():       
    # Crea el controlador
    Controlador = ControladorFuzzy()
    error = np.linspace(-2500, 2500, 1000)
    derror = np.linspace(-2500, 2500, 1000)
    return Controlador, error, derror
    
if __name__ == '__main__':
    ejecutar()