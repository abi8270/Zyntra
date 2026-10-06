from flask import Flask, jsonify, request
from flask_cors import CORS

from qaoa_solver import run_qaoa
from data import drones, emergency_zones, distance_cost

app = Flask(__name__)
CORS(app)


# ============================================================
# ZYNTRA - HELPER FUNCTIONS
# ============================================================

SEVERITY_SCORE = {
    "Critical": 100,
    "High": 70,
    "Medium": 40,
    "Low": 20
}


def calculate_priority(zone):
    severity = emergency_zones[zone]["severity"]
    people = emergency_zones[zone]["people"]

    return SEVERITY_SCORE[severity] + people


def calculate_score(assignments):
    total_priority = 0
    total_distance = 0
    total_battery_cost = 0

    for drone, zone in assignments.items():

        priority = calculate_priority(zone)

        distance = distance_cost[drone][zone]

        battery_cost = 100 - drones[drone]["battery"]

        total_priority += priority
        total_distance += distance
        total_battery_cost += battery_cost

    score = (
        total_priority * 1.5
        - total_distance * 2.0
        - total_battery_cost * 0.5
    )

    return score


def calculate_metrics(assignments):

    travel_cost = 0
    battery_cost = 0
    people_covered = 0

    for drone, zone in assignments.items():

        travel_cost += distance_cost[drone][zone]

        battery_cost += 100 - drones[drone]["battery"]

        people_covered += emergency_zones[zone]["people"]

    score = calculate_score(assignments)

    return {
        "travel_cost": travel_cost,
        "battery_cost": battery_cost,
        "people_covered": people_covered,
        "score": score
    }


# ============================================================
# CLASSICAL BASELINE
# ============================================================

def run_classical():

    assignments = {}

    available_drones = set(drones.keys())
    available_zones = set(emergency_zones.keys())

    # Highest priority zones first
    ranked_zones = sorted(
        available_zones,
        key=lambda zone: calculate_priority(zone),
        reverse=True
    )

    for zone in ranked_zones:

        if not available_drones:
            break

        best_drone = None
        best_score = float("-inf")

        for drone in available_drones:

            priority = calculate_priority(zone)

            distance = distance_cost[drone][zone]

            battery_cost = 100 - drones[drone]["battery"]

            score = (
                priority * 1.5
                - distance * 2.0
                - battery_cost * 0.5
            )

            if score > best_score:
                best_score = score
                best_drone = drone

        if best_drone is not None:

            assignments[best_drone] = zone

            available_drones.remove(best_drone)

    return assignments


def format_assignments(assignments):

    result = []

    for drone, zone in assignments.items():

        result.append({
            "drone": drone,
            "zone": zone,
            "battery": drones[drone]["battery"],
            "distance": distance_cost[drone][zone],
            "severity": emergency_zones[zone]["severity"],
            "people": emergency_zones[zone]["people"]
        })

    return result


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "system": "Zyntra",
        "status": "online",
        "message": "Quantum-Assisted Drone Coordination API"
    })


# ============================================================
# STATUS
# ============================================================

@app.route("/api/status")
def status():

    return jsonify({
        "status": "online",
        "drones": len(drones),
        "emergency_zones": len(emergency_zones),
        "qaoa": "ready",
        "classical": "ready"
    })


# ============================================================
# CURRENT DATA
# ============================================================

@app.route("/api/data")
def get_data():

    return jsonify({
        "drones": drones,
        "emergency_zones": emergency_zones,
        "distance_cost": distance_cost
    })


# ============================================================
# UPDATE DISASTER DATA
# ============================================================

@app.route("/api/update", methods=["POST"])
def update_data():

    try:

        data = request.get_json()

        # -------------------------------
        # Update drone data
        # -------------------------------

        if "drones" in data:

            for drone, drone_data in data["drones"].items():

                if drone in drones:

                    if "battery" in drone_data:

                        battery = int(
                            drone_data["battery"]
                        )

                        battery = max(
                            0,
                            min(100, battery)
                        )

                        drones[drone]["battery"] = battery

        # -------------------------------
        # Update emergency zones
        # -------------------------------

        if "emergency_zones" in data:

            for zone, zone_data in data[
                "emergency_zones"
            ].items():

                if zone in emergency_zones:

                    if "people" in zone_data:

                        people = int(
                            zone_data["people"]
                        )

                        people = max(0, people)

                        emergency_zones[
                            zone
                        ]["people"] = people

                    if "severity" in zone_data:

                        allowed_severity = [
                            "Critical",
                            "High",
                            "Medium",
                            "Low"
                        ]

                        severity = zone_data[
                            "severity"
                        ]

                        if severity in allowed_severity:

                            emergency_zones[
                                zone
                            ]["severity"] = severity

        print("\n==========================================")
        print("        ZYNTRA DATA UPDATED")
        print("==========================================")

        print("\nDrone Batteries:")

        for drone, info in drones.items():

            print(
                f"{drone} -> "
                f"{info['battery']}%"
            )

        print("\nEmergency Zones:")

        for zone, info in emergency_zones.items():

            print(
                f"Zone {zone} -> "
                f"{info['severity']} | "
                f"{info['people']} people"
            )

        return jsonify({

            "status": "success",

            "message":
                "Disaster data updated successfully",

            "drones": drones,

            "emergency_zones":
                emergency_zones

        })

    except Exception as error:

        print("\nDATA UPDATE ERROR:")
        print(error)

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 400


# ============================================================
# CLASSICAL OPTIMIZATION
# ============================================================

@app.route("/api/classical")
def classical():

    print("\n")
    print("=" * 50)
    print("Starting Classical optimization...")
    print("=" * 50)

    assignments = run_classical()

    metrics = calculate_metrics(
        assignments
    )

    response = {

        "status": "success",

        "method": "Classical Baseline",

        "score": metrics["score"],

        "travel_cost":
            metrics["travel_cost"],

        "battery_cost":
            metrics["battery_cost"],

        "people_covered":
            metrics["people_covered"],

        "assignments":
            format_assignments(assignments)

    }

    print("\nClassical Assignment:")

    for drone, zone in assignments.items():

        print(
            f"{drone} -> Zone {zone}"
        )

    print(
        f"Classical Score: "
        f"{metrics['score']:.2f}"
    )

    return jsonify(response)


# ============================================================
# QAOA OPTIMIZATION
# ============================================================

@app.route("/api/optimize")
def optimize():

    print("\n")
    print("=" * 50)
    print("Starting Zyntra QAOA optimization...")
    print("=" * 50)

    result = run_qaoa(

        drone_data=drones,

        zone_data=emergency_zones,

        distance_data=distance_cost

    )

    assignments = result.get(
        "assignments",
        {}
    )

    metrics = calculate_metrics(
        assignments
    )

    response = {

        "status": "success",

        "method": "QAOA",

        "score":
            metrics["score"],

        "travel_cost":
            metrics["travel_cost"],

        "battery_cost":
            metrics["battery_cost"],

        "people_covered":
            metrics["people_covered"],

        "bitstring":
            result.get("bitstring"),

        "frequency":
            result.get("frequency"),

        "successful_runs":
            result.get("successful_runs"),

        "total_runs":
            result.get("total_runs"),

        "assignments":
            format_assignments(assignments)

    }

    print("\nQAOA Assignment:")

    for drone, zone in assignments.items():

        print(
            f"{drone} -> Zone {zone}"
        )

    print(
        f"QAOA Score: "
        f"{metrics['score']:.2f}"
    )

    return jsonify(response)


# ============================================================
# CLASSICAL VS QAOA
# ============================================================

@app.route("/api/compare")
def compare():

    print("\n")
    print("=" * 60)
    print("        ZYNTRA CLASSICAL vs QAOA")
    print("=" * 60)

    # -------------------------------
    # Classical
    # -------------------------------

    classical_assignments = run_classical()

    classical_metrics = calculate_metrics(
        classical_assignments
    )

    # -------------------------------
    # QAOA
    # -------------------------------

    qaoa_result = run_qaoa(

        drone_data=drones,

        zone_data=emergency_zones,

        distance_data=distance_cost

    )

    qaoa_assignments = qaoa_result.get(
        "assignments",
        {}
    )

    qaoa_metrics = calculate_metrics(
        qaoa_assignments
    )

    # -------------------------------
    # Winner
    # -------------------------------

    classical_score = classical_metrics[
        "score"
    ]

    qaoa_score = qaoa_metrics[
        "score"
    ]

    if qaoa_score > classical_score:

        winner = "QAOA"

    elif classical_score > qaoa_score:

        winner = "Classical"

    else:

        winner = "Tie"

    # -------------------------------
    # Response
    # -------------------------------

    response = {

        "status": "success",

        "winner": winner,

        "classical": {

            "score":
                classical_metrics["score"],

            "travel_cost":
                classical_metrics[
                    "travel_cost"
                ],

            "battery_cost":
                classical_metrics[
                    "battery_cost"
                ],

            "people_covered":
                classical_metrics[
                    "people_covered"
                ],

            "assignments":
                format_assignments(
                    classical_assignments
                )

        },

        "qaoa": {

            "score":
                qaoa_metrics["score"],

            "travel_cost":
                qaoa_metrics[
                    "travel_cost"
                ],

            "battery_cost":
                qaoa_metrics[
                    "battery_cost"
                ],

            "people_covered":
                qaoa_metrics[
                    "people_covered"
                ],

            "bitstring":
                qaoa_result.get(
                    "bitstring"
                ),

            "frequency":
                qaoa_result.get(
                    "frequency"
                ),

            "successful_runs":
                qaoa_result.get(
                    "successful_runs"
                ),

            "total_runs":
                qaoa_result.get(
                    "total_runs"
                ),

            "assignments":
                format_assignments(
                    qaoa_assignments
                )

        }

    }

    print("\n")
    print("CLASSICAL SCORE:",
          f"{classical_score:.2f}")

    print("QAOA SCORE:",
          f"{qaoa_score:.2f}")

    print("WINNER:",
          winner)

    print("=" * 60)

    return jsonify(response)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("==========================================")
    print("              ZYNTRA API")
    print("==========================================")

    print(
        "Server  : "
        "http://127.0.0.1:5000"
    )

    print(
        "Status  : "
        "http://127.0.0.1:5000/api/status"
    )

    print(
        "Data    : "
        "http://127.0.0.1:5000/api/data"
    )

    print(
        "Classical: "
        "http://127.0.0.1:5000/api/classical"
    )

    print(
        "Optimize: "
        "http://127.0.0.1:5000/api/optimize"
    )

    print(
        "Compare : "
        "http://127.0.0.1:5000/api/compare"
    )

    print("==========================================")
    print("          ZYNTRA API ONLINE")
    print("==========================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )