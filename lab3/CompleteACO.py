import numpy as np
import matplotlib.pyplot as plt

class CompleteACO:
    def __init__(self, num_cities, distance_matrix, num_ants=10, alpha=1.0, beta=4.0, rho=0.5, Q=100.0):
        self.num_cities = num_cities
        self.distance_matrix = distance_matrix
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.pheromone_matrix = np.ones((num_cities, num_cities)) * 0.1

    def _select_next_city(self, current_city, unvisited, pheromone, heuristic):
        unvisited_list = list(unvisited)
        pheromone_factor = pheromone[current_city, unvisited_list] ** self.alpha
        heuristic_factor = heuristic[current_city, unvisited_list] ** self.beta
        probabilities = pheromone_factor * heuristic_factor
        
        total_weight = np.sum(probabilities)
        if total_weight == 0:
            return np.random.choice(unvisited_list)
        
        probabilities /= total_weight
        return np.random.choice(unvisited_list, p=probabilities)

    def run_baseline(self, max_iterations):
        """Standard Unoptimized Baseline Ant System"""
        self.pheromone_matrix = np.ones((self.num_cities, self.num_cities)) * 0.1
        best_tour = None
        best_tour_length = float('inf')
        heuristic = 1.0 / (self.distance_matrix + np.eye(self.num_cities) * 1e-9)

        for _ in range(max_iterations):
            all_tours = []
            all_lengths = []
            for ant in range(self.num_ants):
                current_city = 0
                unvisited = set(range(self.num_cities))
                unvisited.remove(current_city)
                tour = [current_city]
                
                while unvisited:
                    next_city = self._select_next_city(current_city, unvisited, self.pheromone_matrix, heuristic)
                    tour.append(next_city)
                    unvisited.remove(next_city)
                    current_city = next_city
                
                tour.append(0) # Complete loop back to start
                tour_length = sum(self.distance_matrix[tour[i], tour[i+1]] for i in range(self.num_cities))
                
                all_tours.append(tour)
                all_lengths.append(tour_length)
                
                if tour_length < best_tour_length:
                    best_tour_length = tour_length
                    best_tour = tour

            self.pheromone_matrix *= (1.0 - self.rho)
            for tour, length in zip(all_tours, all_lengths):
                for i in range(self.num_cities):
                    self.pheromone_matrix[tour[i], tour[i+1]] += self.Q / length
                    
        return best_tour, best_tour_length

    def _apply_2opt(self, tour, length):
        """Dynamic local search filtering layer to unwrap edge intersections"""
        best_tour = tour[:]
        best_length = length
        improved = True
        while improved:
            improved = False
            for i in range(1, self.num_cities - 1):
                for j in range(i + 1, self.num_cities):
                    old_cost = self.distance_matrix[best_tour[i-1], best_tour[i]] + self.distance_matrix[best_tour[j], best_tour[j+1]]
                    new_cost = self.distance_matrix[best_tour[i-1], best_tour[j]] + self.distance_matrix[best_tour[i], best_tour[j+1]]
                    
                    if new_cost < old_cost:
                        best_tour[i:j+1] = list(reversed(best_tour[i:j+1]))
                        best_length = best_length - old_cost + new_cost
                        improved = True
        return best_tour, best_length

    def run_optimized_memetic(self, max_iterations):
        """Optimized Memetic ACO with integrated 2-opt search"""
        self.pheromone_matrix = np.ones((self.num_cities, self.num_cities)) * 0.1
        best_tour = None
        best_tour_length = float('inf')
        heuristic = 1.0 / (self.distance_matrix + np.eye(self.num_cities) * 1e-9)

        for _ in range(max_iterations):
            all_tours = []
            all_lengths = []
            for ant in range(self.num_ants):
                current_city = 0
                unvisited = set(range(self.num_cities))
                unvisited.remove(current_city)
                tour = [current_city]
                
                while unvisited:
                    next_city = self._select_next_city(current_city, unvisited, self.pheromone_matrix, heuristic)
                    tour.append(next_city)
                    unvisited.remove(next_city)
                    current_city = next_city
                
                tour.append(0) # Complete loop back to start
                tour_length = sum(self.distance_matrix[tour[i], tour[i+1]] for i in range(self.num_cities))
                
                optimized_tour, optimized_length = self._apply_2opt(tour, tour_length)
                all_tours.append(optimized_tour)
                all_lengths.append(optimized_length)
                
                if optimized_length < best_tour_length:
                    best_tour_length = optimized_length
                    best_tour = optimized_tour

            self.pheromone_matrix *= (1.0 - self.rho)
            for tour, length in zip(all_tours, all_lengths):
                for i in range(self.num_cities):
                    self.pheromone_matrix[tour[i], tour[i+1]] += self.Q / length
                    
        return best_tour, best_tour_length

def plot_graph_paths(num_cities, baseline_route, optimized_route):
    """Generates geometric circular nodes and draws full route networks correctly"""
    plt.figure(figsize=(12, 5))
    
    # Space cities evenly in a circle layout
    angles = np.linspace(0, 2 * np.pi, num_cities, endpoint=False)
    coords = np.column_stack((np.cos(angles) * 100, np.sin(angles) * 100))
    
    # Plot 1: Baseline Layout
    plt.subplot(1, 2, 1)
    plt.scatter(coords[:, 0], coords[:, 1], color='red', zorder=5, s=150)
    for idx, (x, y) in enumerate(coords):
        plt.text(x * 1.18 - 8, y * 1.18 - 5, f"City {idx}", fontsize=11, weight='bold')
    
    # FIX: Correct line segment extraction syntax mapping
    for i in range(len(baseline_route) - 1):
        pt1 = coords[baseline_route[i]]
        pt2 = coords[baseline_route[i+1]]
        plt.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], color='blue', alpha=0.7, linewidth=2)
    plt.title("Baseline Route (Stochastic Ant Path)")
    plt.axis('equal')
    plt.axis('off')

    # Plot 2: Optimized Layout
    plt.subplot(1, 2, 2)
    plt.scatter(coords[:, 0], coords[:, 1], color='red', zorder=5, s=150)
    for idx, (x, y) in enumerate(coords):
        plt.text(x * 1.18 - 8, y * 1.18 - 5, f"City {idx}", fontsize=11, weight='bold')
        
    # FIX: Correct line segment extraction syntax mapping
    for i in range(len(optimized_route) - 1):
        pt1 = coords[optimized_route[i]]
        pt2 = coords[optimized_route[i+1]]
        plt.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], color='green', alpha=0.9, linewidth=2.5)
    plt.title("Optimized Route (2-Opt Loop-Free Path)")
    plt.axis('equal')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("--- Ant Colony Optimization Adjacency Matrix Solver ---")
    cities_count = int(input("Enter total number of cities: "))
    
    print(f"\nEnter the distance matrix row by row ({cities_count} numbers per row, separated by spaces):")
    matrix_list = []
    for idx in range(cities_count):
        row = list(map(float, input(f"Row {idx}: ").split()))
        matrix_list.append(row)
        
    dist_matrix = np.array(matrix_list)

    solver = CompleteACO(num_cities=cities_count, distance_matrix=dist_matrix, num_ants=10)
    
    print("\nProcessing algorithms...")
    base_path, base_dist = solver.run_baseline(max_iterations=1)
    opt_path, opt_dist = solver.run_optimized_memetic(max_iterations=1)
    
    print("\n================== OUTPUT METRICS ==================")
    print(f"[Baseline Result] Minimum Distance: {base_dist:.2f}")
    print(f"[Baseline Result] Optimal Route: {' -> '.join(map(str, base_path))}")
    print("-" * 52)
    print(f"[Optimized Result] Minimum Distance: {opt_dist:.2f}")
    print(f"[Optimized Result] Optimal Route: {' -> '.join(map(str, opt_path))}")
    print("====================================================")
    
    plot_graph_paths(cities_count, base_path, opt_path)
