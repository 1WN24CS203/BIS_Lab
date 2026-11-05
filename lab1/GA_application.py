import random

fit = lambda x: x * x  
pop = [random.randint(1, 30) for _ in range(4)]  

for gen in range(5):
    pop = sorted(pop, key=fit)
    print(f"Gen {gen}: {pop}")

    p1, p2 = pop[-1], pop[-2]

    next_gen = []
    for _ in range(4):
        child = (p1 + p2) // 2  

        if random.random() < 0.2:  
            child += random.choice([-1, 1])  

        next_gen.append(child)

    pop = next_gen

print("Best:", sorted(pop, key=fit)[-1])
