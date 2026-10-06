# Zyntra - Main Application

from data import display_data
from optimizer import optimize_assignments, calculate_priority


def run_zyntra():
    print("\n===================================")
    print("        ZYNTRA DISASTER AI")
    print("   Smarter Coordination. Faster Rescue.")
    print("===================================")

    # Show disaster information
    display_data()

    # Run optimization
    assignments = optimize_assignments()

    print("\n=== ZYNTRA FINAL DECISION ===")

    for drone, zone in assignments.items():
        priority = calculate_priority(zone)

        print(
            f"{drone} -> Zone {zone} | "
            f"Priority: {priority}"
        )

    assigned_zones = set(assignments.values())

    from data import emergency_zones

    unassigned = set(emergency_zones.keys()) - assigned_zones

    print("\n=== COVERAGE STATUS ===")

    if unassigned:
        print(
            "Uncovered Zones:",
            ", ".join(sorted(unassigned))
        )
    else:
        print("All emergency zones covered.")

    print("\nZyntra optimization completed successfully!")


if __name__ == "__main__":
    run_zyntra()