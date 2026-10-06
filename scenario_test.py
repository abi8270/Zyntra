# Zyntra - Disaster Scenario Testing

from data import drones, emergency_zones, distance_cost


severity_score = {
    "Critical": 100,
    "High": 70,
    "Medium": 40
}


def priority(zone_data):
    return (
        severity_score[zone_data["severity"]]
        + zone_data["people"]
    )


def calculate_score(
    drone,
    zone,
    drone_data,
    zone_data,
    distance
):

    p = priority(zone_data)

    battery_cost = 100 - drone_data["battery"]

    return (
        (p * 1.5)
        - (distance * 2.0)
        - (battery_cost * 0.5)
    )


def greedy_assignment(
    drone_data,
    zone_data,
    distance_data
):

    assignments = {}

    available_drones = set(
        drone_data.keys()
    )

    ranked_zones = sorted(
        zone_data.keys(),
        key=lambda z: priority(zone_data[z]),
        reverse=True
    )

    for zone in ranked_zones:

        if not available_drones:
            break

        best_drone = None
        best_score = float("-inf")

        for drone in available_drones:

            score = calculate_score(
                drone,
                zone,
                drone_data[drone],
                zone_data[zone],
                distance_data[drone][zone]
            )

            if score > best_score:

                best_score = score
                best_drone = drone

        assignments[best_drone] = zone
        available_drones.remove(best_drone)

    return assignments


def calculate_metrics(
    assignments,
    drone_data,
    zone_data,
    distance_data
):

    total_distance = 0
    total_priority = 0
    total_score = 0

    for drone, zone in assignments.items():

        distance = distance_data[drone][zone]

        p = priority(zone_data[zone])

        battery_cost = (
            100 - drone_data[drone]["battery"]
        )

        score = (
            (p * 1.5)
            - (distance * 2.0)
            - (battery_cost * 0.5)
        )

        total_distance += distance
        total_priority += p
        total_score += score

    return (
        total_distance,
        total_priority,
        total_score
    )


# ============================================================
# SCENARIOS
# ============================================================

scenarios = {

    "Scenario 1 - Normal Flood":
    {
        "drones": drones.copy(),
        "zones": emergency_zones.copy()
    },

    "Scenario 2 - Zone C Critical":
    {
        "drones": drones.copy(),

        "zones": {
            "A": {
                "severity": "Critical",
                "people": 20
            },
            "B": {
                "severity": "High",
                "people": 10
            },
            "C": {
                "severity": "Critical",
                "people": 25
            },
            "D": {
                "severity": "Critical",
                "people": 15
            }
        }
    },

    "Scenario 3 - D1 Low Battery":
    {
        "drones": {
            "D1": {
                "battery": 25,
                "location": "Base-A"
            },
            "D2": {
                "battery": 65,
                "location": "Base-B"
            },
            "D3": {
                "battery": 40,
                "location": "Base-C"
            }
        },

        "zones": emergency_zones.copy()
    },

    "Scenario 4 - Large Emergency":
    {
        "drones": drones.copy(),

        "zones": {
            "A": {
                "severity": "Critical",
                "people": 35
            },
            "B": {
                "severity": "High",
                "people": 20
            },
            "C": {
                "severity": "Critical",
                "people": 30
            },
            "D": {
                "severity": "Critical",
                "people": 25
            }
        }
    }
}


# ============================================================
# RUN SCENARIOS
# ============================================================

def main():

    print("\n===================================")
    print("             ZYNTRA")
    print("===================================")
    print("       DISASTER SCENARIO TEST")
    print("===================================")

    for name, scenario in scenarios.items():

        drone_data = scenario["drones"]
        zone_data = scenario["zones"]

        assignments = greedy_assignment(
            drone_data,
            zone_data,
            distance_cost
        )

        distance, priority_total, score = (
            calculate_metrics(
                assignments,
                drone_data,
                zone_data,
                distance_cost
            )
        )

        print("\n===================================")
        print(name)
        print("===================================")

        for drone, zone in assignments.items():

            print(
                f"{drone} -> Zone {zone} | "
                f"Priority: {priority(zone_data[zone])} | "
                f"Battery: {drone_data[drone]['battery']}%"
            )

        print(
            f"\nTravel Cost     : {distance}"
        )

        print(
            f"Priority Total  : {priority_total}"
        )

        print(
            f"Overall Score   : {score:.2f}"
        )

        covered = len(assignments)
        total_zones = len(zone_data)

        print(
            f"Coverage        : "
            f"{covered}/{total_zones}"
        )

    print("\n===================================")
    print("       SCENARIO TEST COMPLETE")
    print("===================================")


if __name__ == "__main__":
    main()