import numpy as np
import matplotlib.pyplot as plt

q = 1.602176634e-19
k = 1.380649e-23
T = 306.15

v_input = input("Enter Voltage values (comma-separated) or press Enter for default: ").strip()
i_input = input("Enter Current values (comma-separated) or press Enter for default: ").strip()

if v_input and i_input:
    V_exp = np.array([float(x) for x in v_input.split(",")])
    I_exp = np.array([float(x) for x in i_input.split(",")])
else:
    V_exp = np.array([
        0.0, 1.26, 2.52, 3.78, 5.04, 6.30, 7.56, 8.82, 10.08, 11.34, 12.60, 13.86, 14.50, 15.10, 15.70, 16.30, 16.80
    ])
    I_exp = np.array([
        1.030, 1.030, 1.029, 1.028, 1.026, 1.024, 1.020, 1.012, 0.998, 0.970, 0.920, 0.825, 0.740, 0.620, 0.460, 0.260, 0.080
    ])

I_max = float(np.max(I_exp))
V_max = float(np.max(V_exp))

Ns = int(np.round(V_max / 0.6)) if V_max > 2.0 else 1
V_th = (Ns * k * T) / q

def calculate_pv_current(V, Iph, I0, n, Rs, Rsh):
    I = np.ones_like(V) * Iph
    for _ in range(100):
        f = Iph - I0 * (np.exp((V + I * Rs) / (n * V_th)) - 1) - (V + I * Rs) / Rsh
        I = 0.5 * I + 0.5 * f
    return np.maximum(I, 0)

def objective_rmse(params):
    Iph, I0, n, Rs, Rsh = params
    I_calc = calculate_pv_current(V_exp, Iph, I0, n, Rs, Rsh)
    return np.sqrt(np.mean((I_exp - I_calc)**2))

def run_gwo_pso_optimization(num_wolves=40, max_iter=200):
    lb = np.array([I_max * 0.8, 1e-10, 0.8, 1e-4, 10.0])
    ub = np.array([I_max * 1.5, 1e-3, 2.5, 5.0, 10000.0])
    dim = 5

    X = lb + (ub - lb) * np.random.rand(num_wolves, dim)
    V_particle = np.zeros((num_wolves, dim))

    Alpha_pos, Alpha_score = np.zeros(dim), float("inf")
    Beta_pos,  Beta_score  = np.zeros(dim), float("inf")
    Delta_pos, Delta_score = np.zeros(dim), float("inf")

    initial_guess = X[0].copy()
    initial_rmse = objective_rmse(initial_guess)

    convergence_history = []

    print(f"\nAuto-detected Series Cells (Ns): {Ns}")
    print("Running GWO-PSO Solar Optimization...")

    for t in range(max_iter):
        for i in range(num_wolves):
            X[i] = np.clip(X[i], lb, ub)
            fitness = objective_rmse(X[i])

            if fitness < Alpha_score:
                Alpha_score, Alpha_pos = fitness, X[i].copy()
            elif fitness < Beta_score:
                Beta_score, Beta_pos = fitness, X[i].copy()
            elif fitness < Delta_score:
                Delta_score, Delta_pos = fitness, X[i].copy()

        convergence_history.append(Alpha_score)

        a = 2 - t * (2 / max_iter)

        for i in range(num_wolves):
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            A1, C1 = 2 * a * r1 - a, 2 * r2
            D_alpha = np.abs(C1 * Alpha_pos - X[i])
            X1 = Alpha_pos - A1 * D_alpha

            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            A2, C2 = 2 * a * r1 - a, 2 * r2
            D_beta = np.abs(C2 * Beta_pos - X[i])
            X2 = Beta_pos - A2 * D_beta

            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            A3, C3 = 2 * a * r1 - a, 2 * r2
            D_delta = np.abs(C3 * Delta_pos - X[i])
            X3 = Delta_pos - A3 * D_delta

            X_gwo = (X1 + X2 + X3) / 3.0

            w, c1 = 0.5, 1.2
            V_particle[i] = w * V_particle[i] + c1 * np.random.rand() * (X_gwo - X[i])
            
            X[i] = X[i] + V_particle[i]

    return initial_guess, initial_rmse, Alpha_pos, Alpha_score, convergence_history

initial_params, initial_rmse, optimal_params, best_rmse, history = run_gwo_pso_optimization(num_wolves=40, max_iter=200)

I_fitted = calculate_pv_current(V_exp, *optimal_params)
P_exp = V_exp * I_exp
P_fitted = V_exp * I_fitted

param_names = ["Photocurrent (Iph)", "Saturation Current (I0)", "Diode Ideality (n)", "Series Res. (Rs)", "Shunt Res. (Rsh)"]
units = ["A", "A", "-", "Ω", "Ω"]

print("\n" + "="*65)
print("              GWO-PSO OPTIMIZATION OUTPUT RESULTS")
print("="*65)
print(f"{'Parameter':<25} | {'Initial Value':<15} | {'Optimized Value':<15}")
print("-" * 65)
for name, unit, init_v, opt_v in zip(param_names, units, initial_params, optimal_params):
    print(f"{name + ' (' + unit + ')':<25} | {init_v:<15.5e} | {opt_v:<15.5e}")
print("-" * 65)
print(f"Initial RMSE : {initial_rmse:.6e} A")
print(f"Final RMSE   : {best_rmse:.6e} A")
print("="*65)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].scatter(V_exp, I_exp, color='red', s=35, label='Input Experimental Data', zorder=3)
axes[0].plot(V_exp, I_fitted, color='navy', linewidth=2, label='GWO-PSO Optimized Model')
axes[0].set_title("Current–Voltage (I–V) Characteristic")
axes[0].set_xlabel("Voltage (V)")
axes[0].set_ylabel("Current (A)")
axes[0].grid(True, linestyle='--', alpha=0.6)
axes[0].legend()

axes[1].scatter(V_exp, P_exp, color='red', s=35, label='Input Experimental Data', zorder=3)
axes[1].plot(V_exp, P_fitted, color='darkgreen', linewidth=2, label='GWO-PSO Optimized Model')
axes[1].set_title("Power–Voltage (P–V) Characteristic")
axes[1].set_xlabel("Voltage (V)")
axes[1].set_ylabel("Power (W)")
axes[1].grid(True, linestyle='--', alpha=0.6)
axes[1].legend()

axes[2].plot(range(1, len(history) + 1), history, color='crimson', linewidth=2)
axes[2].set_title("GWO-PSO Optimization Convergence")
axes[2].set_xlabel("Iteration")
axes[2].set_ylabel("Best RMSE Error (A)")
axes[2].set_yscale('log')
axes[2].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()