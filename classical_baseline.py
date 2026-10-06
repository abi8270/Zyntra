# Zyntra - Classical Baseline
# Used to compare classical greedy assignment
# with the quantum-assisted QAOA approach.

from data import drones, emergency_zones, distance_cost


# ============================================================
# SEVERITY SCORES
# ============================================================

severity_score = {
    "Critical": 100,
    "High": 70,
    "Medium": 40
}


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(zone):

    severity = emergency_zones[zone]["severity"]
    people = emergency_zones[zone]["people"]

    return severity_score[severity] + people


# ============================================================
# CLASSICAL GREEDY ASSIGNMENT
# ============================================================

def classical_assignment():

    assignments = {}

    available_drones = set(drones.keys())
    available_zones = set(emergency_zones.keys())

    # --------------------------------------------------------
    # Rank emergency zones by priority
    # Highest priority first
    # --------------------------------------------------------

    ranked_zones = sorted(
        available_zones,
        key=calculate_priority,
        reverse=True
    )

    # --------------------------------------------------------
    # For each emergency zone, select the best available drone
    #
    # Classical decision:
    # priority + distance + battery
    # --------------------------------------------------------

    for zone in ranked_zones:

        best_drone = None
        best_score = float("-inf")

        for drone in available_drones:

            priority = calculate_priority(zone)

            distance = distance_cost[drone][zone]

            battery = drones[drone]["battery"]

            battery_cost = 100 - battery

            score = (
                (priority * 1.5)
                - (distance * 2.0)
                - (battery_cost * 0.5)
            )

            if score > best_score:

                best_score = score
                best_drone = drone

        if best_drone is not None:

            assignments[best_drone] = zone

            available_drones.remove(
                best_drone
            )

    return assignments


# ============================================================
# CALCULATE TOTAL METRICS
# ============================================================

def calculate_metrics(assignments):

    total_distance = 0
    total_battery_cost = 0
    total_priority = 0
    total_score = 0

    for drone, zone in assignments.items():

        distance = distance_cost[drone][zone]

        battery = drones[drone]["battery"]

        battery_cost = 100 - battery

        priority = calculate_priority(zone)

        score = (
            (priority * 1.5)
            - (distance * 2.0)
            - (battery_cost * 0.5)
        )

        total_distance += distance
        total_battery_cost += battery_cost
        total_priority += priority
        total_score += score

    return {
        "distance": total_distance,
        "battery_cost": total_battery_cost,
        "priority": total_priority,
        "score": total_score
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(assignments):

    print("\n===================================")
    print("       CLASSICAL BASELINE")
    print("===================================")

    for drone, zone in assignments.items():

        priority = calculate_priority(zone)

        distance = distance_cost[drone][zone]

        battery = drones[drone]["battery"]

        print(
            f"{drone} -> Zone {zone} | "
            f"Priority: {priority} | "
            f"Distance: {distance} | "
            f"Battery: {battery}%"
        )

    metrics = calculate_metrics(
        assignments
    )

    print("\n===================================")
    print("       CLASSICAL METRICS")
    print("===================================")

    print(
        f"Total Travel Cost : "
        f"{metrics['distance']} units"
    )

    print(
        f"Battery Cost      : "
        f"{metrics['battery_cost']}"
    )

    print(
        f"Priority Covered  : "
        f"{metrics['priority']}"
    )

    print(
        f"Overall Score     : "
        f"{metrics['score']:.2f}"
    )

    assigned_zones = set(
        assignments.values()
    )

    uncovered = (
        set(emergency_zones.keys())
        - assigned_zones
    )

    if uncovered:

        print(
            "Uncovered Zones   :",
            ", ".join(sorted(uncovered))
        )

    else:

        print(
            "Uncovered Zones   : None"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n===================================")
    print("             ZYNTRA")
    print("===================================")
    print("Classical Greedy Baseline")
    print("===================================")

    assignments = classical_assignment()

    display_result(
        assignments
    )


if __name__ == "__main__":
    main()