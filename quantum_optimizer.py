# Zyntra - QUBO Drone Assignment Model

import numpy as np

# -----------------------------
# Problem Data
# -----------------------------

drones = ["D1", "D2", "D3"]
zones = ["A", "B", "C", "D"]

battery = {
    "D1": 90,
    "D2": 65,
    "D3": 40
}

priority = {
    "A": 120,
    "B": 80,
    "C": 46,
    "D": 115
}


# -----------------------------
# Create Binary Variables
# -----------------------------

variables = []

for drone in drones:
    for zone in zones:
        variables.append((drone, zone))


# -----------------------------
# Build QUBO
# -----------------------------

def build_qubo():

    n = len(variables)

    Q = np.zeros((n, n))

    # Large penalty for violating constraints
    PENALTY = 150

    # ---------------------------------
    # 1. Assignment Cost
    # ---------------------------------

    for i, (drone, zone) in enumerate(variables):

        battery_cost = (100 - battery[drone])

        # Higher priority = lower cost
        assignment_cost = battery_cost - priority[zone]

        Q[i][i] += assignment_cost


    # ---------------------------------
    # 2. Each Drone → At Most One Zone
    # ---------------------------------

    for drone in drones:

        drone_variables = [
            i for i, (d, z) in enumerate(variables)
            if d == drone
        ]

        for i in drone_variables:
            for j in drone_variables:

                if i != j:
                    Q[i][j] += PENALTY


    # ---------------------------------
    # 3. Each Zone → At Most One Drone
    # ---------------------------------

    for zone in zones:

        zone_variables = [
            i for i, (d, z) in enumerate(variables)
            if z == zone
        ]

        for i in zone_variables:
            for j in zone_variables:

                if i != j:
                    Q[i][j] += PENALTY


    return Q


# -----------------------------
# Display QUBO
# -----------------------------

def display_qubo():

    Q = build_qubo()

    print("\n===================================")
    print("       ZYNTRA QUBO MODEL")
    print("===================================")

    print("\nBinary Variables:")

    for index, variable in enumerate(variables):
        print(
            f"x{index} = "
            f"{variable[0]} -> Zone {variable[1]}"
        )

    print("\nQUBO Matrix:")

    np.set_printoptions(
        precision=1,
        suppress=True
    )

    print(Q)

    print("\nConstraints:")
    print("✓ Each drone assigned to at most one zone")
    print("✓ Each zone assigned to at most one drone")
    print("✓ Emergency priority included")
    print("✓ Battery cost included")

    print("\nQUBO model created successfully!")


if __name__ == "__main__":
    display_qubo()