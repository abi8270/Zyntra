# ============================================================
# ZYNTRA
# Quantum-Assisted Drone Coordination
# QAOA Solver
# ============================================================

from qiskit import QuantumCircuit
from qiskit.circuit.library import QAOAAnsatz
from qiskit_aer import AerSimulator
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo


# ============================================================
# CONFIGURATION
# ============================================================

SHOTS = 128

PENALTY = 1000

PRIORITY_WEIGHT = 1.5
DISTANCE_WEIGHT = 2.0
BATTERY_WEIGHT = 0.5

GAMMA_VALUES = [0.5, 0.8]
BETA_VALUES = [0.3, 0.6]

SEVERITY_SCORE = {
    "Critical": 100,
    "High": 70,
    "Medium": 40,
    "Low": 20
}


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(zone, zone_data):

    severity = zone_data[zone]["severity"]
    people = zone_data[zone]["people"]

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

    return (
        priority * PRIORITY_WEIGHT
        - distance * DISTANCE_WEIGHT
        - battery_cost * BATTERY_WEIGHT
    )


# ============================================================
# CREATE OPTIMIZATION PROBLEM
# ============================================================

def create_optimization_problem(
    drone_data=None,
    zone_data=None,
    distance_data=None
):

    # --------------------------------------------------------
    # Default scenario
    # --------------------------------------------------------

    if (
        drone_data is None
        or zone_data is None
        or distance_data is None
    ):

        from data import (
            drones,
            emergency_zones,
            distance_cost
        )

        drone_data = drones
        zone_data = emergency_zones
        distance_data = distance_cost

    drones_list = list(
        drone_data.keys()
    )

    zones_list = list(
        zone_data.keys()
    )

    num_drones = len(drones_list)
    num_zones = len(zones_list)

    qp = QuadraticProgram(
        name="Zyntra_Drone_Coordination"
    )

    # --------------------------------------------------------
    # Binary variables
    #
    # x_drone_zone = 1
    # if drone is assigned to zone
    # --------------------------------------------------------

    for drone in drones_list:

        for zone in zones_list:

            variable_name = (
                f"x_{drone}_{zone}"
            )

            qp.binary_var(
                name=variable_name
            )

    # --------------------------------------------------------
    # Objective
    # --------------------------------------------------------

    linear_coefficients = {}

    for drone in drones_list:

        for zone in zones_list:

            variable_name = (
                f"x_{drone}_{zone}"
            )

            score = calculate_assignment_score(
                drone,
                zone,
                drone_data,
                zone_data,
                distance_data
            )

            # QuadraticProgram minimizes.
            # Therefore maximize our score
            # by minimizing negative score.

            linear_coefficients[
                variable_name
            ] = -score

    qp.minimize(
        linear=linear_coefficients
    )

    # --------------------------------------------------------
    # Constraint 1
    #
    # Each drone can be assigned
    # to at most one emergency zone.
    # --------------------------------------------------------

    for drone in drones_list:

        coefficients = {}

        for zone in zones_list:

            variable_name = (
                f"x_{drone}_{zone}"
            )

            coefficients[
                variable_name
            ] = 1

        qp.linear_constraint(

            linear=coefficients,

            sense="<=",

            rhs=1,

            name=f"drone_{drone}_limit"
        )

    # --------------------------------------------------------
    # Constraint 2
    #
    # Each emergency zone can receive
    # at most one drone.
    #
    # This creates the assignment structure.
    # --------------------------------------------------------

    for zone in zones_list:

        coefficients = {}

        for drone in drones_list:

            variable_name = (
                f"x_{drone}_{zone}"
            )

            coefficients[
                variable_name
            ] = 1

        qp.linear_constraint(

            linear=coefficients,

            sense="<=",

            rhs=1,

            name=f"zone_{zone}_limit"
        )

    return qp


# ============================================================
# QUBO CONVERSION
# ============================================================

def convert_to_qubo(qp):

    converter = QuadraticProgramToQubo(
        penalty=PENALTY
    )

    qubo = converter.convert(qp)

    return qubo


# ============================================================
# DECODE BITSTRING
# ============================================================

def decode_bitstring(
    bitstring,
    drone_data,
    zone_data
):

    drones_list = list(
        drone_data.keys()
    )

    zones_list = list(
        zone_data.keys()
    )

    expected_length = (
        len(drones_list)
        * len(zones_list)
    )

    # Qiskit strings are normally returned
    # most-significant bit first.

    if len(bitstring) != expected_length:

        return {}

    assignments = {}

    index = 0

    for drone in drones_list:

        for zone in zones_list:

            if bitstring[index] == "1":

                # Prevent duplicate assignment
                # for a drone.

                if drone not in assignments:

                    assignments[
                        drone
                    ] = zone

            index += 1

    return assignments


# ============================================================
# VALIDATE ASSIGNMENT
# ============================================================

def is_valid_assignment(
    assignments,
    drone_data,
    zone_data
):

    # No drone may appear twice.

    if len(assignments) != len(
        set(assignments.keys())
    ):

        return False

    # No zone may appear twice.

    zones = list(
        assignments.values()
    )

    if len(zones) != len(
        set(zones)
    ):

        return False

    # Every drone must exist.

    for drone in assignments:

        if drone not in drone_data:

            return False

    # Every zone must exist.

    for zone in assignments.values():

        if zone not in zone_data:

            return False

    return True


# ============================================================
# SCORE ASSIGNMENT
# ============================================================

def score_assignment(
    assignments,
    drone_data,
    zone_data,
    distance_data
):

    total_priority = 0
    total_distance = 0
    total_battery_cost = 0

    for drone, zone in assignments.items():

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

        total_priority += priority
        total_distance += distance
        total_battery_cost += battery_cost

    score = (

        total_priority * PRIORITY_WEIGHT

        - total_distance * DISTANCE_WEIGHT

        - total_battery_cost * BATTERY_WEIGHT

    )

    return score


# ============================================================
# QAOA SOLVER
# ============================================================

def run_qaoa(
    drone_data=None,
    zone_data=None,
    distance_data=None
):

    # --------------------------------------------------------
    # Default scenario
    # --------------------------------------------------------

    if (
        drone_data is None
        or zone_data is None
        or distance_data is None
    ):

        from data import (
            drones,
            emergency_zones,
            distance_cost
        )

        drone_data = drones
        zone_data = emergency_zones
        distance_data = distance_cost

    print("\n")
    print("=" * 60)
    print("                    ZYNTRA")
    print("=" * 60)
    print("       Quantum-Assisted Drone Coordination")
    print("=" * 60)

    # --------------------------------------------------------
    # Create optimization problem
    # --------------------------------------------------------

    print("\nCreating optimization problem...")

    qp = create_optimization_problem(
        drone_data,
        zone_data,
        distance_data
    )

    print("Optimization problem created.")

    print(
        f"Variables: {len(qp.variables)}"
    )

    print(
        f"Constraints: {len(qp.linear_constraints)}"
    )

    # --------------------------------------------------------
    # Convert to QUBO
    # --------------------------------------------------------

    print("\nConverting constrained problem to QUBO...")

    qubo = convert_to_qubo(qp)

    print("QUBO conversion completed.")

    print(
        f"QUBO variables: {len(qubo.variables)}"
    )

    # --------------------------------------------------------
    # Convert QUBO to Ising Hamiltonian
    # --------------------------------------------------------

    operator, offset = qubo.to_ising()

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
        f"Offset: {offset}"
    )

    # --------------------------------------------------------
    # Number of qubits
    # --------------------------------------------------------

    num_qubits = len(
        qubo.variables
    )

    # --------------------------------------------------------
    # Create QAOA ansatz
    # --------------------------------------------------------

    ansatz = QAOAAnsatz(
        cost_operator=operator,
        reps=1
    )

    print("\nQAOA ansatz created.")

    print(
        f"Qubits: {num_qubits}"
    )

    print(
        f"Parameters: "
        f"{len(ansatz.parameters)}"
    )

    # --------------------------------------------------------
    # Simulator selection
    # --------------------------------------------------------

    if num_qubits <= 14:

        simulator = AerSimulator(
            method="statevector"
        )

        simulator_mode = "statevector"

    else:

        simulator = AerSimulator(
            method="matrix_product_state"
        )

        simulator_mode = (
            "matrix_product_state"
        )

    print(
        f"\nQAOA parameter sweep: "
        f"{len(GAMMA_VALUES) * len(BETA_VALUES)} combinations"
    )

    print(
        f"Simulator mode: "
        f"{simulator_mode}"
    )

    # --------------------------------------------------------
    # Search variables
    # --------------------------------------------------------

    best_assignment = None
    best_score = float("-inf")
    best_bitstring = None
    best_frequency = 0

    successful_runs = 0

    total_runs = (
        len(GAMMA_VALUES)
        * len(BETA_VALUES)
    )

    run_number = 0

    # --------------------------------------------------------
    # Parameter sweep
    # --------------------------------------------------------

    for gamma in GAMMA_VALUES:

        for beta in BETA_VALUES:

            run_number += 1

            print(
                f"\nRun {run_number}/{total_runs} "
                f"| gamma={gamma} "
                f"| beta={beta}"
            )

            # ------------------------------------------------
            # Assign QAOA parameters
            # ------------------------------------------------

            parameter_values = [
                gamma,
                beta
            ]

            circuit = ansatz.assign_parameters(
                parameter_values
            )

            # ------------------------------------------------
            # Decompose PauliEvolution instructions
            # ------------------------------------------------

            circuit = circuit.decompose(
                reps=10
            )

            # ------------------------------------------------
            # Measurement
            # ------------------------------------------------

            measured_circuit = circuit.copy()

            measured_circuit.measure_all()

            # ------------------------------------------------
            # Execute
            # ------------------------------------------------

            try:

                result = simulator.run(
                    measured_circuit,
                    shots=SHOTS
                ).result()

                counts = result.get_counts()

                successful_runs += 1

            except Exception as error:

                print(
                    f"QAOA execution failed: "
                    f"{error}"
                )

                continue

            # ------------------------------------------------
            # Process measured states
            # ------------------------------------------------

            for raw_state, frequency in counts.items():

                # Remove spaces if present.

                state = raw_state.replace(
                    " ",
                    ""
                )

                assignments = decode_bitstring(
                    state,
                    drone_data,
                    zone_data
                )

                if not is_valid_assignment(
                    assignments,
                    drone_data,
                    zone_data
                ):

                    continue

                score = score_assignment(
                    assignments,
                    drone_data,
                    zone_data,
                    distance_data
                )

                if score > best_score:

                    best_score = score

                    best_assignment = (
                        assignments.copy()
                    )

                    best_bitstring = state

                    best_frequency = frequency

                    print(
                        "\nNew best valid solution:"
                    )

                    print(
                        f"  Score: "
                        f"{score:.2f}"
                    )

                    print(
                        f"  Frequency: "
                        f"{frequency}"
                    )

                    print(
                        f"  State: "
                        f"{state}"
                    )

                    print(
                        f"  Assignment: "
                        f"{assignments}"
                    )

    # --------------------------------------------------------
    # No valid solution
    # --------------------------------------------------------

    if best_assignment is None:

        print("\n")
        print("=" * 60)
        print("                 QAOA FAILED")
        print("=" * 60)

        print(
            "\nNo valid assignment was found."
        )

        return {

            "assignments": {},

            "score": float("-inf"),

            "bitstring": None,

            "frequency": 0,

            "successful_runs":
                successful_runs
        }

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("                 QAOA FINAL RESULT")
    print("=" * 60)

    print(
        f"\nBest QAOA Score: "
        f"{best_score:.2f}"
    )

    print(
        f"Successful runs: "
        f"{successful_runs}/{total_runs}"
    )

    print(
        f"Best bitstring: "
        f"{best_bitstring}"
    )

    print("\nQAOA Assignment:")

    for drone, zone in sorted(
        best_assignment.items()
    ):

        priority = calculate_priority(
            zone,
            zone_data
        )

        distance = distance_data[
            drone
        ][zone]

        battery = drone_data[
            drone
        ]["battery"]

        print(
            f"  {drone} -> Zone {zone}"
            f" | Priority: {priority}"
            f" | Distance: {distance}"
            f" | Battery: {battery}%"
        )

    print("\n")
    print("=" * 60)
    print("                 ZYNTRA COMPLETE")
    print("=" * 60)

    return {

        "assignments":
            best_assignment,

        "score":
            best_score,

        "bitstring":
            best_bitstring,

        "frequency":
            best_frequency,

        "successful_runs":
            successful_runs,

        "total_runs":
            total_runs
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_qaoa()