import random

m = 10000  # Number of points to generate
d = 50   # Dimension of each point

with open("database.txt", "w") as file:
    for _ in range(m):
        point = [random.randint(-10000, 10000) for _ in range(d)]
        line = " ".join(str(coord) for coord in point)
        file.write(line + "\n")
