import numpy as np
import matplotlib.pyplot as plt

class CauchyCuckooWSN:
    def __init__(self, num_sensors, field_size, sensing_radius, num_nests=15, pa=0.25):
        self.num_sensors = num_sensors      
        self.field_size = field_size        
        self.sensing_radius = sensing_radius 
        self.num_nests = num_nests          
        self.pa = pa                        
        
        # Initialize nest matrices mapping prospective coordinate layouts
        self.nests = np.random.rand(num_nests, num_sensors, 2) * field_size
        self.best_nest = None
        self.best_coverage = -1
        self.initial_nest = None
        self.initial_coverage = -1

    def calculate_coverage(self, nest_layout):
        """Calculates grid mesh network coverage index percentage"""
        grid_points = 30  # Resolution scale for monitoring coverage loops
        x_ticks = np.linspace(0, self.field_size, grid_points)
        y_ticks = np.linspace(0, self.field_size, grid_points)
        
        covered_points = 0
        total_points = grid_points * grid_points
        
        for x in x_ticks:
            for y in y_ticks:
                distances = np.sqrt(np.sum((nest_layout - np.array([x, y])) ** 2, axis=1))
                if np.any(distances <= self.sensing_radius):
                    covered_points += 1
                    
        return (covered_points / total_points) * 100.0

    def optimize_coverage(self, iterations=15):
        """Executes Cauchy Distribution mutation step perturbations"""
        fitness = np.zeros(self.num_nests)
        for idx in range(self.num_nests):
            fitness[idx] = self.calculate_coverage(self.nests[idx])
            if fitness[idx] > self.best_coverage:
                self.best_coverage = fitness[idx]
                self.best_nest = self.nests[idx].copy()
        
        # Store the initial state for the final comparison plot
        self.initial_nest = self.best_nest.copy()
        self.initial_coverage = self.best_coverage

        for _ in range(iterations):
            for i in range(self.num_nests):
                # Cauchy step generation to break out of sub-optimal local traps
                cauchy_step = np.random.standard_cauchy(size=(self.num_sensors, 2)) * 2.0
                new_nest = np.clip(self.nests[i] + cauchy_step, 0, self.field_size)
                
                new_fit = self.calculate_coverage(new_nest)
                random_index = np.random.randint(0, self.num_nests)
                
                if new_fit > fitness[random_index]:
                    self.nests[random_index] = new_nest
                    fitness[random_index] = new_fit
                    
                if new_fit > self.best_coverage:
                    self.best_coverage = new_fit
                    self.best_nest = new_nest.copy()

            # Evade discovery adjustments (Discard poor configurations)
            for i in range(self.num_nests):
                if np.random.rand() < self.pa:
                    self.nests[i] = np.random.rand(self.num_sensors, 2) * self.field_size
                    fitness[i] = self.calculate_coverage(self.nests[i])

        return self.best_coverage

def plot_wsn_coverage(initial_layout, optimized_layout, radius, field_size, c1, c2):
    """Plots initial and final optimized layouts side-by-side with coverage circles"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # --- Plot 1: Initial Layout ---
    ax1.set_xlim(0, field_size)
    ax1.set_ylim(0, field_size)
    ax1.set_title(f"Initial Deployment (Coverage: {c1:.2f}%)", weight='bold', fontsize=12)
    # Scatter plot for sensor node centers
    ax1.scatter(initial_layout[:, 0], initial_layout[:, 1], color='darkred', zorder=5, s=40, label='Sensor Nodes')
    # Add coverage boundary circles
    for x, y in initial_layout:
        circle = plt.Circle((x, y), radius, color='red', alpha=0.15, zorder=2)
        ax1.add_patch(circle)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right')

    # --- Plot 2: Optimized Layout ---
    ax2.set_xlim(0, field_size)
    ax2.set_ylim(0, field_size)
    ax2.set_title(f"CD-CSA Optimized Deployment (Coverage: {c2:.2f}%)", weight='bold', fontsize=12)
    # Scatter plot for optimized sensor node centers
    ax2.scatter(optimized_layout[:, 0], optimized_layout[:, 1], color='darkgreen', zorder=5, s=40, label='Optimized Nodes')
    # Add optimized coverage boundary circles
    for x, y in optimized_layout:
        circle = plt.Circle((x, y), radius, color='green', alpha=0.15, zorder=2)
        ax2.add_patch(circle)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_aspect('equal')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.show()

# --- Handling Terminal Configuration Input ---
if __name__ == "__main__":
    np.random.seed(42)
    
    print("--- CD-CSA Wireless Sensor Network Parameter Inputs ---")
    sensors = int(input("Enter total number of sensor nodes (e.g., 30): "))
    field = float(input("Enter deployment field boundary width in meters (e.g., 100): "))
    radius = float(input("Enter node sensing coverage radius in meters (e.g., 15): "))
    iters = int(input("Enter optimization tuning iterations (e.g., 20): "))
    
    # Instantiate simulation layout
    wsn_optimizer = CauchyCuckooWSN(num_sensors=sensors, field_size=field, sensing_radius=radius)
    
    print("\nProcessing Cauchy-mutation vector tracking loops...")
    final_coverage = wsn_optimizer.optimize_coverage(iterations=iters)
    
    print("\n================== CD-CSA SYSTEM LOGS ==================")
    print(f"[Execution Mode] Cauchy Distribution Improved Cuckoo Search")
    print(f"[Initial Metrics] Random Layout Coverage: {wsn_optimizer.initial_coverage:.2f}%")
    print(f"[Final Metrics] Optimized Sensor Network Field Coverage: {final_coverage:.2f}%")
    print("========================================================")
    
    # Launch visual graphics plotting layout
    plot_wsn_coverage(
        wsn_optimizer.initial_nest, 
        wsn_optimizer.best_nest, 
        radius, 
        field, 
        wsn_optimizer.initial_coverage, 
        final_coverage
    )
