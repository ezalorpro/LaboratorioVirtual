import control as ctrl
from matplotlib import pyplot as plt

pid = ctrl.tf([1, 1, 1], [1, 0])
Gs = ctrl.tf([1], [1, 1, 1])
feedgs = ctrl.feedback(pid * Gs)
# ctrl.gangof4_plot(Gs, pid)
# plt.show()
ctrl.damp(feedgs)