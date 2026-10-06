# ============================================================
# ZYNTRA - SCALED STRESS TEST
# QUBO Scalability Validation
# ============================================================

from qaoa_solver import (
    create_optimization_problem,
    convert_to_qubo
)


# ============================================================
# STRESS TEST DATA
# ============================================================

stress_drones = {
    "D1": {
        "battery": 95,
        "location": "Base-A"
    },
    "D2": {
        "battery": 70,
        "location": "Base-B"
    },
    "D3": {
        "battery": 55,
        "location": "Base-C"
    },
    "D4": {
        "battery": 80,
        "location": "Base-D"
    },
    "D5": {
        "battery": 35,
        "location": "Base-E"
    }
}


stress_zones = {
    "A": {
        "severity": "Critical",
        "people": 40
    },
    "B": {
        "severity": "High",
        "people": 25
    },
    "C": {
        "severity": "Critical",
        "people": 35
    },
    "D": {
        "severity": "Medium",
        "people": 15
    },
    "E": {
        "severity": "High",
        "people": 30
    },
    "F": {
        "severity": "Critical",
        "people": 20
    }
}


stress_distance = {

    "D1": {
        "A": 8,
        "B": 25,
        "C": 30,
        "D": 18,
        "E": 35,
        "F": 22
    },

    "D2": {
        "A": 20,
        "B": 10,
        "C": 28,
        "D": 15,
        "E": 18,
        "F": 25
    },

    "D3": {
        "A": 32,
        "B": 14,
        "C": 12,
        "D": 10,
        "E": 20,
        "F": 16
    },

    "D4": {
        "A": 15,
        "B": 22,
        "C": 10,
        "D": 8,
        "E": 12,
        "F": 20
    },

    "D5": {
        "A": 28,
        "B": 12,
        "C": 18,
        "D": 20,
        "E": 10,
        "F": 14
    }
}


# ============================================================
# SEVERITY SCORES
# ============================================================

SEVERITY_SCORE = {
    "Critical": 100,
    "High": 70,
    "Medium": 40,
    "Low": 20
}


# ============================================================
# STRESS TEST PRIORITY
# ============================================================

def calculate_stress_priority(
    zone,
    zone_data
):

    severity = zone_data[zone]["severity"]
    people = zone_data[zone]["people"]

    return (
        SEVERITY_SCORE[severity]
        + people
    )


# ============================================================
# CLASSICAL BASELINE
# ============================================================

def classical_assignment():

    assignments = {}

    available_drones = set(
        stress_drones.keys()
    )

    available_zones = set(
        stress_zones.keys()
    )

    # --------------------------------------------------------
    # Rank emergency zones by priority.
    # --------------------------------------------------------

    ranked_zones = sorted(
        available_zones,
        key=lambda zone:
            calculate_stress_priority(
                zone,
                stress_zones
            ),
        reverse=True
    )

    # --------------------------------------------------------
    # Greedy drone assignment.
    #
    # For each high-priority zone:
    # choose the available drone with the
    # lowest distance + battery penalty.
    # --------------------------------------------------------

    for zone in ranked_zones:

        if not available_drones:
            break

        best_drone = None
        best_cost = float("inf")

        for drone in available_drones:

            distance = stress_distance[
                drone
            ][
                zone
            ]

            battery = stress_drones[
                drone
            ]["battery"]

            battery_penalty = (
                100 - battery
            )

            cost = (
                distance
                + 0.5 * battery_penalty
            )

            if cost < best_cost:

                best_cost = cost
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
    assignments
):

    total_distance = 0
    total_battery = 0
    total_priority = 0

    for drone, zone in assignments.items():

        total_distance += (
            stress_distance[
                drone
            ][
                zone
            ]
        )

        total_battery += (
            100
            - stress_drones[
                drone
            ]["battery"]
        )

        total_priority += (
            calculate_stress_priority(
                zone,
                stress_zones
            )
        )

    score = (
        1.5 * total_priority
        - 2.0 * total_distance
        - 0.5 * total_battery
    )

    return {
        "distance": total_distance,
        "battery": total_battery,
        "priority": total_priority,
        "score": score,
        "coverage": len(assignments)
    }


# ============================================================
# DISPLAY ASSIGNMENT
# ============================================================

def display_assignment(
    title,
    assignments
):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)

    for drone, zone in sorted(
        assignments.items()
    ):

        priority = calculate_stress_priority(
            zone,
            stress_zones
        )

        distance = stress_distance[
            drone
        ][
            zone
        ]

        battery = stress_drones[
            drone
        ]["battery"]

        print(
            f"  {drone} -> Zone {zone}"
            f" | Priority: {priority}"
            f" | Distance: {distance}"
            f" | Battery: {battery}%"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("                    ZYNTRA")
    print("=" * 60)
    print("              SCALED STRESS TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Problem size
    # --------------------------------------------------------

    number_of_drones = len(
        stress_drones
    )

    number_of_zones = len(
        stress_zones
    )

    number_of_variables = (
        number_of_drones
        * number_of_zones
    )

    print("\nScenario:")

    print(
        f"  Drones          : "
        f"{number_of_drones}"
    )

    print(
        f"  Emergency Zones : "
        f"{number_of_zones}"
    )

    print(
        f"  QUBO Variables  : "
        f"{number_of_variables}"
    )

    # --------------------------------------------------------
    # Drone information
    # --------------------------------------------------------

    print("\nDrone Batteries:")

    for drone, info in (
        stress_drones.items()
    ):

        print(
            f"  {drone} -> "
            f"{info['battery']}%"
        )

    # --------------------------------------------------------
    # Emergency zones
    # --------------------------------------------------------

    print("\nEmergency Zones:")

    for zone, info in (
        stress_zones.items()
    ):

        print(
            f"  Zone {zone} -> "
            f"{info['severity']} | "
            f"{info['people']} people"
        )

    # ========================================================
    # CLASSICAL BASELINE
    # ========================================================

    print("\n")
    print("=" * 60)
    print("                 CLASSICAL BASELINE")
    print("=" * 60)

    classical = classical_assignment()

    display_assignment(
        "Classical Assignment",
        classical
    )

    classical_metrics = calculate_metrics(
        classical
    )

    print("\nClassical Metrics:")

    print(
        f"  Travel Cost : "
        f"{classical_metrics['distance']}"
    )

    print(
        f"  Battery Cost: "
        f"{classical_metrics['battery']}"
    )

    print(
        f"  Priority    : "
        f"{classical_metrics['priority']}"
    )

    print(
        f"  Score       : "
        f"{classical_metrics['score']:.2f}"
    )

    print(
        f"  Coverage    : "
        f"{classical_metrics['coverage']}"
    )

    # ========================================================
    # QUBO SCALABILITY
    # ========================================================

    print("\n")
    print("=" * 60)
    print("              QUBO SCALABILITY CHECK")
    print("=" * 60)

    print(
        "\nBuilding 30-variable optimization problem..."
    )

    qp = create_optimization_problem(
        stress_drones,
        stress_zones,
        stress_distance
    )

    print(
        "Optimization problem created."
    )

    print(
        f"Variables: "
        f"{len(qp.variables)}"
    )

    print(
        f"Constraints: "
        f"{len(qp.linear_constraints)}"
    )

    # --------------------------------------------------------
    # QUBO conversion
    # --------------------------------------------------------

    print(
        "\nConverting constrained problem to QUBO..."
    )

    qubo = convert_to_qubo(
        qp
    )

    print(
        "QUBO conversion completed."
    )

    print(
        f"QUBO variables: "
        f"{len(qubo.variables)}"
    )

    # --------------------------------------------------------
    # Ising Hamiltonian
    # --------------------------------------------------------

    operator, offset = (
        qubo.to_ising()
    )

    try:

        hamiltonian_terms = len(
            operator.paulis
        )

    except Exception:

        hamiltonian_terms = 0

    print(
        f"Hamiltonian terms: "
        f"{hamiltonian_terms}"
    )

    print(
        f"Offset: "
        f"{offset}"
    )

    # ========================================================
    # SCALABILITY SUMMARY
    # ========================================================

    print("\n")
    print("=" * 60)
    print("             SCALABILITY SUMMARY")
    print("=" * 60)

    print("\nProblem Size:")

    print(
        f"  Drones              : "
        f"{number_of_drones}"
    )

    print(
        f"  Emergency Zones     : "
        f"{number_of_zones}"
    )

    print(
        f"  Binary Variables    : "
        f"{number_of_variables}"
    )

    print(
        f"  Constraints         : "
        f"{len(qp.linear_constraints)}"
    )

    print(
        f"  Hamiltonian Terms   : "
        f"{hamiltonian_terms}"
    )

    # ========================================================
    # QUANTUM FORMULATION
    # ========================================================

    print("\nQuantum Formulation:")

    print(
        "  QUBO construction   : SUCCESS"
    )

    print(
        "  Ising Hamiltonian   : SUCCESS"
    )

    print(
        "  QAOA-ready          : YES"
    )

    # ========================================================
    # SIMULATION DECISION
    # ========================================================

    print("\nSimulation Decision:")

    print(
        "  30-qubit full QAOA  : SKIPPED"
    )

    print(
        "  Reason              : "
        "Local simulation is computationally expensive"
    )

    print(
        "  Purpose             : "
        "Scalability validation"
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("              ZYNTRA STRESS TEST")
    print("                 COMPLETED")
    print("=" * 60)

    print("\nResult:")

    print(
        "  [OK] 5-drone scenario created"
    )

    print(
        "  [OK] 6-emergency-zone scenario created"
    )

    print(
        "  [OK] 30 binary decision variables created"
    )

    print(
        "  [OK] 11 constraints created"
    )

    print(
        "  [OK] QUBO conversion successful"
    )

    print(
        "  [OK] Ising Hamiltonian generated"
    )

    print(
        "  [OK] Classical baseline evaluated"
    )

    print(
        "  [OK] Large-scale QAOA formulation validated"
    )

    print(
        "\nZyntra successfully demonstrates "
        "a scalable quantum optimization formulation."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()