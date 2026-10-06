# ZYNTRA

## Smarter Coordination. Faster Rescue.

**Quantum-Assisted Autonomous Drone Coordination for Disaster Response**

> Q-HACK INDIA 2026 • Open Quantum Innovation • Team QubitXians

---

## 🚨 Problem Statement

During floods, earthquakes, landslides, and other disasters, multiple emergency zones may require immediate assistance while only a limited number of drones are available.

Traditional nearest-drone or manual assignment approaches may not consider multiple factors simultaneously, such as:

- Emergency severity
- Number of people affected
- Drone battery level
- Travel distance
- Limited drone availability
- Avoiding duplicate assignments
- Prioritizing critical emergencies

Zyntra addresses this challenge using optimization-based drone coordination.

---

## 💡 Our Solution

**Zyntra** is a quantum-assisted disaster-response coordination prototype that determines suitable drone-to-emergency-zone assignments using optimization.

The system considers:

- Emergency priority
- Affected population
- Drone battery
- Travel distance
- Assignment constraints
- QUBO formulation
- QAOA circuit exploration
- Classical baseline comparison

The result is displayed through an interactive dashboard.

---

## ⚛️ Quantum Approach

The drone coordination problem is formulated as a **Quadratic Unconstrained Binary Optimization (QUBO)** problem.

For every possible drone-zone combination, a binary variable is created:

```text
x(drone, zone) ∈ {0,1}
```

Where:

- `1` = drone is assigned to the zone
- `0` = drone is not assigned

The optimization objective considers:

```text
Emergency Priority
        +
Affected Population
        -
Travel Cost
        -
Battery Cost
```

The constrained problem is converted into a QUBO and then into an Ising Hamiltonian.

A **QAOA ansatz** is explored using a quantum simulator.

> Zyntra is a quantum-optimization prototype and does not claim a demonstrated quantum speedup over classical optimization.

---

## 🔄 System Workflow

```text
Emergency Data
      ↓
Drone & Location Data
      ↓
Priority + Cost Calculation
      ↓
QUBO Formulation
      ↓
QAOA Circuit
      ↓
Quantum Simulator
      ↓
Best Valid Assignment
      ↓
Dashboard
      ↓
Classical vs QAOA Comparison
```

---

## 🖥️ Prototype

The current prototype simulates:

- 3 drones
- 4 emergency zones
- Dynamic drone battery
- Dynamic affected population
- Dynamic emergency severity
- QUBO optimization
- QAOA parameter sweep
- Classical baseline
- Interactive dashboard

Example assignment:

```text
D1 → Zone A
D2 → Zone D
D3 → Zone B
```

---

## 📊 Example Scenario

### Drones

| Drone | Battery | Location |
|---|---:|---|
| D1 | 90% | Base-A |
| D2 | 65% | Base-B |
| D3 | 40% | Base-C |

### Emergency Zones

| Zone | People | Severity |
|---|---:|---|
| A | 20 | Critical |
| B | 10 | High |
| C | 6 | Medium |
| D | 15 | Critical |

---

## 🧪 Dynamic Disaster Simulation

Zyntra allows disaster conditions to be changed directly from the dashboard.

Example:

```text
D1 Battery: 90% → 20%

Zone C:
People: 6 → 20
Severity: Medium → Critical
```

After updating the scenario, Zyntra rebuilds the optimization problem and executes the QAOA workflow using the updated data.

---

## 📈 Scalability Test

A larger scenario was tested with:

```text
5 Drones
6 Emergency Zones
30 Binary Variables
11 Constraints
30 QUBO Variables
165 Ising Hamiltonian Terms
```

The larger problem was successfully formulated and converted into an Ising Hamiltonian.

Full 30-qubit QAOA execution was not used in the local prototype because simulator cost increases significantly with problem size.

---

## 🛠️ Tech Stack

### Quantum

- Qiskit
- Qiskit Aer
- QAOA
- QUBO
- Ising Hamiltonian

### Backend

- Python
- Flask
- Flask-CORS
- NumPy
- Pandas

### Frontend

- HTML
- CSS
- JavaScript

### Development

- Visual Studio Code
- Git
- GitHub

---

## 📂 Project Structure

```text
Zyntra/
├── api.py
├── app.py
├── data.py
├── optimizer.py
├── classical_baseline.py
├── comparison.py
├── qaoa_solver.py
├── quantum_optimizer.py
├── scenario_test.py
├── stress_test.py
├── dashboard.html
└── README.md
```

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/abi8270/Zyntra.git
cd Zyntra
```

### 2. Install dependencies

```bash
py -m pip install qiskit qiskit-aer numpy pandas
py -m pip install qiskit-algorithms
py -m pip install qiskit-optimization
py -m pip install flask flask-cors
```

### 3. Run QAOA

```bash
py qaoa_solver.py
```

### 4. Run comparison

```bash
py comparison.py
```

### 5. Run scalability test

```bash
py stress_test.py
```

### 6. Start the API

```bash
py api.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

Then open `dashboard.html` in a browser.

---

## 🔌 API Endpoints

```text
GET  /
GET  /api/status
GET  /api/data
POST /api/update
GET  /api/classical
GET  /api/optimize
GET  /api/compare
```

---

## 🧠 Classical vs Quantum-Assisted

Zyntra includes a classical baseline for comparison.

The comparison considers:

- Drone-zone assignment
- Travel cost
- Battery cost
- People covered
- Overall optimization score

The prototype does **not** artificially force QAOA to win.

If QAOA matches the classical solution, the result is reported as a tie. If the classical approach performs better, that result is also reported honestly.

---

## 🌍 Real-World Applications

Potential applications include:

- Flood response
- Landslide response
- Earthquake response
- Emergency medical delivery
- Food and essential supply delivery
- Search and rescue operations

In a real deployment, Zyntra would act as a **decision-support and mission-planning layer**, with human or authorized mission-control approval before drone execution.

---

## 🚀 Future Scope

- Live drone GPS
- Real-time battery telemetry
- Weather APIs
- Disaster monitoring feeds
- Dynamic route planning
- Drone swarm coordination
- IoT sensor integration
- Edge computing
- Larger hybrid quantum-classical optimization
- Real quantum hardware
- Voice-based emergency coordination

---

## 👥 Team QubitXians

**Abinaya K** — Team Leader

**Madhesh S**

**Mugunthan S**

**Gunasri KM**

---

## 🏆 Q-HACK INDIA 2026

**Track:** Open Quantum Innovation

**Project:** ZYNTRA – Quantum-Assisted Autonomous Drone Coordination for Disaster Response

**Tagline:** *Smarter Coordination. Faster Rescue.*

---

## ⚠️ Prototype Disclaimer

Zyntra is currently a hackathon prototype using simulated disaster data and quantum simulation.

It does not directly control physical drones or perform autonomous emergency deployment.

Real-world deployment would require validated hardware integration, communication infrastructure, safety systems, regulatory approval, and human oversight.

---

## 📜 License

This project is developed as a hackathon prototype for Q-HACK INDIA 2026.
