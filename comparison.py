# ============================================================
# ZYNTRA
# Classical vs Quantum Comparison
# ============================================================

from data import (
    drones,
    emergency_zones,
    distance_cost
)


# ============================================================
# WEIGHTS
# ============================================================

PRIORITY_WEIGHT = 1.5
DISTANCE_WEIGHT = 2.0
BATTERY_WEIGHT = 0.5


SEVERITY_SCORE = {

    "Critical": 100,

    "High": 70,

    "Medium": 40
}


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(
    zone,
    zone_data
):

    severity = zone_data[
        zone
    ]["severity"]

    people = zone_data[
        zone
    ]["people"]

    return (
        SEVERITY_SCORE[severity]
        + people
    )


# ============================================================
# ASSIGNMENT SCORE
# ============================================================

def calculate_assignment_score(
    drone,
    zone,
    drone_data,
    zone_data,
    distance_data
):

    priority = calculate_priority(
        zone,
        zone_data
    )

    distance = distance_data[
        drone
    ][zone]

    battery_cost = (
        100
        - drone_data[drone]["battery"]
    )

    score = (

        priority * PRIORITY_WEIGHT

        - distance * DISTANCE_WEIGHT

        - battery_cost * BATTERY_WEIGHT

    )

    return score


# ============================================================
# CLASSICAL GREEDY BASELINE
# ============================================================

def classical_assignment(
    drone_data,
    zone_data,
    distance_data
):

    assignments = {}

    available_drones = set(
        drone_data.keys()
    )

    available_zones = set(
        zone_data.keys()
    )

    # Highest priority first
    ranked_zones = sorted(

        available_zones,

        key=lambda zone:
            calculate_priority(
                zone,
                zone_data
            ),

        reverse=True
    )

    # Assign best available drone
    for zone in ranked_zones:

        if not available_drones:
            break

        best_drone = None

        best_score = float("-inf")

        for drone in available_drones:

            score = calculate_assignment_score(

                drone,

                zone,

                drone_data,

                zone_data,

                distance_data

            )

            if score > best_score:

                best_score = score

                best_drone = drone

        if best_drone is not None:

            assignments[
                best_drone
            ] = zone

            available_drones.remove(
                best_drone
            )

    return assignments


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    assignments,
    drone_data,
    zone_data,
    distance_data
):

    total_distance = 0

    total_battery_cost = 0

    total_priority = 0

    for drone, zone in assignments.items():

        distance = distance_data[
            drone
        ][zone]

        battery_cost = (
            100
            - drone_data[drone]["battery"]
        )

        priority = calculate_priority(
            zone,
            zone_data
        )

        total_distance += distance

        total_battery_cost += (
            battery_cost
        )

        total_priority += priority

    total_score = (

        total_priority * PRIORITY_WEIGHT

        - total_distance * DISTANCE_WEIGHT

        - total_battery_cost * BATTERY_WEIGHT

    )

    return {

        "distance":
            total_distance,

        "battery_cost":
            total_battery_cost,

        "priority":
            total_priority,

        "score":
            total_score,

        "coverage":
            len(assignments)
    }


# ============================================================
# IMPROVEMENT
# ============================================================

def calculate_improvement(
    classical_score,
    quantum_score
):

    if classical_score == 0:

        return 0

    return (

        (
            quantum_score
            - classical_score
        )

        / abs(classical_score)

    ) * 100


# ============================================================
# SCENARIO EVALUATION
# ============================================================

def evaluate_scenario(
    scenario_name,
    drone_data,
    zone_data,
    distance_data,
    run_quantum=True
):

    print("\n")
    print("=" * 60)

    print(
        f"                 {scenario_name}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Classical
    # --------------------------------------------------------

    print("\n=== CLASSICAL BASELINE ===")

    classical = classical_assignment(

        drone_data,

        zone_data,

        distance_data

    )

    classical_metrics = calculate_metrics(

        classical,

        drone_data,

        zone_data,

        distance_data

    )

    for drone, zone in sorted(
        classical.items()
    ):

        print(
            f"{drone} -> Zone {zone}"
        )

    print("\nClassical Metrics:")

    print(
        f"Travel Cost : "
        f"{classical_metrics['distance']}"
    )

    print(
        f"Battery Cost: "
        f"{classical_metrics['battery_cost']}"
    )

    print(
        f"Priority    : "
        f"{classical_metrics['priority']}"
    )

    print(
        f"Score       : "
        f"{classical_metrics['score']:.2f}"
    )

    print(
        f"Coverage    : "
        f"{classical_metrics['coverage']}"
    )

    # --------------------------------------------------------
    # Quantum
    # --------------------------------------------------------

    if not run_quantum:

        return {

            "classical":
                classical_metrics,

            "quantum":
                None
        }

    print("\n=== QAOA ===")

    from qaoa_solver import run_qaoa

    quantum = run_qaoa(

        drone_data,

        zone_data,

        distance_data

    )

    quantum_assignment = quantum[
        "assignments"
    ]

    quantum_metrics = calculate_metrics(

        quantum_assignment,

        drone_data,

        zone_data,

        distance_data

    )

    print("\nQuantum Assignment:")

    for drone, zone in sorted(
        quantum_assignment.items()
    ):

        print(
            f"{drone} -> Zone {zone}"
        )

    print("\nQuantum Metrics:")

    print(
        f"Travel Cost : "
        f"{quantum_metrics['distance']}"
    )

    print(
        f"Battery Cost: "
        f"{quantum_metrics['battery_cost']}"
    )

    print(
        f"Priority    : "
        f"{quantum_metrics['priority']}"
    )

    print(
        f"Score       : "
        f"{quantum_metrics['score']:.2f}"
    )

    print(
        f"Coverage    : "
        f"{quantum_metrics['coverage']}"
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    improvement = calculate_improvement(

        classical_metrics["score"],

        quantum_metrics["score"]

    )

    print("\n=== COMPARISON ===")

    print(
        f"Classical Score : "
        f"{classical_metrics['score']:.2f}"
    )

    print(
        f"QAOA Score      : "
        f"{quantum_metrics['score']:.2f}"
    )

    print(
        f"QAOA Change     : "
        f"{improvement:+.2f}%"
    )

    if (
        quantum_metrics["score"]
        > classical_metrics["score"]
    ):

        winner = "QAOA"

    elif (
        quantum_metrics["score"]
        < classical_metrics["score"]
    ):

        winner = "CLASSICAL"

    else:

        winner = "TIE"

    print(
        f"Winner          : {winner}"
    )

    return {

        "classical":
            classical_metrics,

        "quantum":
            quantum_metrics,

        "winner":
            winner,

        "improvement":
            improvement
    }


# ============================================================
# STANDARD COMPARISON
# ============================================================

def run_standard_comparison():

    scenarios = []

    # --------------------------------------------------------
    # Scenario 1
    # --------------------------------------------------------

    scenarios.append({

        "name":
            "NORMAL FLOOD",

        "drones":
            drones,

        "zones":
            emergency_zones,

        "distance":
            distance_cost

    })

    # --------------------------------------------------------
    # Scenario 2
    # --------------------------------------------------------

    zones_2 = {

        zone: info.copy()

        for zone, info
        in emergency_zones.items()

    }

    zones_2["C"] = {

        "severity":
            "Critical",

        "people":
            25
    }

    scenarios.append({

        "name":
            "ZONE C CRITICAL",

        "drones":
            drones,

        "zones":
            zones_2,

        "distance":
            distance_cost

    })

    # --------------------------------------------------------
    # Scenario 3
    # --------------------------------------------------------

    drones_3 = {

        drone: info.copy()

        for drone, info
        in drones.items()

    }

    drones_3["D1"]["battery"] = 25

    scenarios.append({

        "name":
            "D1 LOW BATTERY",

        "drones":
            drones_3,

        "zones":
            emergency_zones,

        "distance":
            distance_cost

    })

    # --------------------------------------------------------
    # Scenario 4
    # --------------------------------------------------------

    zones_4 = {

        zone: info.copy()

        for zone, info
        in emergency_zones.items()

    }

    zones_4["A"]["people"] = 50

    zones_4["D"]["people"] = 40

    zones_4["B"]["people"] = 25

    scenarios.append({

        "name":
            "LARGE EMERGENCY",

        "drones":
            drones,

        "zones":
            zones_4,

        "distance":
            distance_cost

    })

    results = []

    for scenario in scenarios:

        result = evaluate_scenario(

            scenario["name"],

            scenario["drones"],

            scenario["zones"],

            scenario["distance"]

        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n")

    print("=" * 70)

    print(
        "                    FINAL SUMMARY"
    )

    print("=" * 70)

    qaoa_wins = 0

    classical_wins = 0

    ties = 0

    for index, result in enumerate(
        results,
        1
    ):

        winner = result[
            "winner"
        ]

        if winner == "QAOA":

            qaoa_wins += 1

        elif winner == "CLASSICAL":

            classical_wins += 1

        else:

            ties += 1

        print(
            f"Scenario {index}: "
            f"{winner}"
        )

    print(
        "\nQAOA Wins      :",
        qaoa_wins
    )

    print(
        "Classical Wins :",
        classical_wins
    )

    print(
        "Ties           :",
        ties
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_standard_comparison()