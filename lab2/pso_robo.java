import java.util.*;

public class pso_robo {
    public static double[][] run(double[] s, double[] g, double[][] obs, int nP, int nW, int maxIt) {
        double[][] X = new double[nP][nW], V = new double[nP][nW], pb = new double[nP][nW];
        double[] pbFit = new double[nP], gb = new double[nW];
        int[] stag = new int[nP];
        double gbFit = Double.MAX_VALUE, w = 0.5, c1 = 1.5, c2 = 1.5, al = 0.6;
        Random rng = new Random();

        // Precompute fixed X coordinates across the path span
        double[] xWay = new double[nW + 2];
        for (int j = 0; j <= nW + 1; j++) xWay[j] = s[0] + j * (g[0] - s[0]) / (nW + 1);

        // 1. Initialize Particles (Optimizing Y-coordinates only)
        for (int i = 0; i < nP; i++) {
            for (int j = 0; j < nW; j++) {
                X[i][j] = s[1] + rng.nextDouble() * (g[1] - s[1]);
                V[i][j] = -2.0 + rng.nextDouble() * 4.0;
            }
            pb[i] = X[i].clone();
            pbFit[i] = fitness(X[i], s, g, obs, xWay);
            if (pbFit[i] < gbFit) { gbFit = pbFit[i]; gb = pb[i].clone(); }
        }

        // 2. Optimization Loop with Reflection Strategy
        for (int it = 0; it < maxIt; it++) {
            for (int i = 0; i < nP; i++) {
                for (int j = 0; j < nW; j++) {
                    V[i][j] = w * V[i][j] + c1 * rng.nextDouble() * (pb[i][j] - X[i][j]) + c2 * rng.nextDouble() * (gb[j] - X[i][j]);
                    X[i][j] = Math.max(0, Math.min(100, X[i][j] + V[i][j]));
                }
                double fit = fitness(X[i], s, g, obs, xWay);
                if (fit < pbFit[i]) {
                    pb[i] = X[i].clone(); pbFit[i] = fit; stag[i] = 0;
                    if (fit < gbFit) { gbFit = fit; gb = X[i].clone(); }
                } else if (++stag[i] > 4) { // Reflection step if particle stagnates
                    for (int j = 0; j < nW; j++) X[i][j] = Math.max(0, Math.min(100, (1 + al) * gb[j] - al * X[i][j]));
                    stag[i] = 0;
                }
            }
        }
        System.out.printf("\nBest Fitness Score: %.2f\n", gbFit);
        return rebuildPath(gb, s, g, xWay);
    }

    private static double[][] rebuildPath(double[] yWay, double[] s, double[] g, double[] xWay) {
        int nW = yWay.length;
        double[][] path = new double[nW + 2][2];
        path[0] = s; path[nW + 1] = g;
        for (int i = 0; i < nW; i++) path[i + 1] = new double[]{xWay[i + 1], yWay[i]};
        return path;
    }

    private static double fitness(double[] yWay, double[] s, double[] g, double[][] obs, double[] xWay) {
        double[][] path = rebuildPath(yWay, s, g, xWay);
        double dist = 0, penalty = 0;
        for (int i = 0; i < path.length - 1; i++) {
            double dx = path[i + 1][0] - path[i][0], dy = path[i + 1][1] - path[i][1];
            dist += Math.hypot(dx, dy);
            // Collision validation step along the segment line
            for (int t = 0; t <= 10; t++) {
                double f = t / 10.0, targetX = path[i][0] + f * dx, targetY = path[i][1] + f * dy;
                for (double[] o : obs) {
                    if (Math.hypot(targetX - o[0], targetY - o[1]) <= o[2]) penalty += 500.0;
                }
            }
        }
        return dist + penalty;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter particles, waypoints, iterations (e.g., 30 5 100): ");
        int nP = sc.nextInt(), nW = sc.nextInt(), maxIt = sc.nextInt();

        System.out.print("Enter start coordinates (x y): ");
        double[] start = {sc.nextDouble(), sc.nextDouble()};

        System.out.print("Enter goal coordinates (x y): ");
        double[] goal = {sc.nextDouble(), sc.nextDouble()};

        System.out.print("Enter number of obstacles: ");
        int numObs = sc.nextInt();
        double[][] obstacles = new double[numObs][3];
        for (int i = 0; i < numObs; i++) {
            System.out.printf("Obstacle %d (x y radius): ", i + 1);
            obstacles[i][0] = sc.nextDouble();
            obstacles[i][1] = sc.nextDouble();
            obstacles[i][2] = sc.nextDouble();
        }

        double[][] finalPath = run(start, goal, obstacles, nP, nW, maxIt);
        System.out.println("Optimal Collision-Free Path:");
        for (double[] pt : finalPath) System.out.printf("[%.2f, %.2f]\n", pt[0], pt[1]);
        sc.close();
    }
}
