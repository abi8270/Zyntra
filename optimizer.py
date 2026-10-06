# Zyntra - Drone Assignment Optimizer

from data import drones, emergency_zones


severity_score = {
    "Critical": 100,
    "High": 70,
    "Medium": 40
}


def calculate_priority(zone):
    severity = emergency_zones[zone]["severity"]
    people = emergency_zones[zone]["people"]

    return severity_score[severity] + people


def optimize_assignments():
    assignments = {}

    # Rank emergency zones by priority
    ranked_zones = sorted(
        emergency_zones,
        key=calculate_priority,
        reverse=True
    )

    # Rank drones by battery
    ranked_drones = sorted(
        drones,
        key=lambda drone: drones[drone]["battery"],
        reverse=True
    )

    # Assign highest battery drones to highest priority zones
    for drone, zone in zip(ranked_drones, ranked_zones):
        assignments[drone] = zone

    return assignments


def display_assignments():
    assignments = optimize_assignments()

    print("\n=== ZYNTRA OPTIMIZED ASSIGNMENT ===")

    for drone, zone in assignments.items():
        priority = calculate_priority(zone)

        print(
            f"{drone} --> Zone {zone} | "
            f"Priority Score: {priority}"
        )


if __name__ == "__main__":
    display_assignments()