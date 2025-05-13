# Trois points (x, y)
import numpy as np
import matplotlib.pyplot as plt

x = [0, 340, 640]
y = [33, 0, -33]

# Ajustement polynômial de degré 2
coeffs = np.polyfit(x, y, deg=2)

# Création du polynôme à partir des coefficients
p = np.poly1d(coeffs)

print("Polynôme :", p)

# Génération de points pour l'affichage
x_vals = np.linspace(min(x), max(x), 500)
y_vals = p(x_vals)

# Tracé
plt.plot(x, y, 'ro', label='Points donnés')  # Points d'origine
plt.plot(x_vals, y_vals, 'b-', label='Polynôme interpolé')  # Courbe polynômiale
plt.xlabel('x')
plt.ylabel('y')
plt.title('Interpolation polynomiale de degré 2')
plt.legend()
plt.grid(True)
plt.show()
