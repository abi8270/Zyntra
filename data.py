# Zyntra - Disaster Response Data

drones = {
    "D1": {
        "battery": 90,
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
}


emergency_zones = {
    "A": {
        "severity": "Critical",
        "people": 20
    },
    "B": {
        "severity": "High",
        "people": 10
    },
    "C": {
        "severity": "Medium",
        "people": 6
    },
    "D": {
        "severity": "Critical",
        "people": 15
    }
}


# Estimated travel distance/cost
# from each drone base to each emergency zone

distance_cost = {

    "D1": {
        "A": 10,
        "B": 25,
        "C": 40,
        "D": 18
    },

    "D2": {
        "A": 22,
        "B": 12,
        "C": 28,
        "D": 15
    },

    "D3": {
        "A": 30,
        "B": 14,
        "C": 10,
        "D": 20
    }
}


def display_data():

    print("\n=== ZYNTRA DISASTER SCENARIO ===")

    print("\nDrones:")

    for drone, info in drones.items():

        print(
            f"{drone} | "
            f"Battery: {info['battery']}% | "
            f"Location: {info['location']}"
        )

    print("\nEmergency Zones:")

    for zone, info in emergency_zones.items():

        print(
            f"Zone {zone} | "
            f"Severity: {info['severity']} | "
            f"People: {info['people']}"
        )

    print("\nTravel Cost:")

    for drone in distance_cost:

        for zone in distance_cost[drone]:

            print(
                f"{drone} -> Zone {zone} : "
                f"{distance_cost[drone][zone]} units"
            )


if __name__ == "__main__":
    display_data()