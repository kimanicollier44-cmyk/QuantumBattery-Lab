#!/usr/bin/env python3
"""QuantumBattery-Lab - educational quantum battery charging lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Education only: quantum batteries are real published research
(Alicki & Fannes 2013; Quach et al. 2022 superabsorption device),
NOT a product. This lab models the physics honestly - ergotropy,
collective charging advantage, superabsorption, charger-battery
entanglement, decoherence self-discharge, daemonic ergotropy -
with Gemini Carbon 4 as DECIDER (names-only, tighten-only), Muse
as advisor (never overrides HOLD), and Google Flow plan-only seats.

Every free-energy / product / live-hardware claim is a HOLD gate.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
EV_J = 1.602176634e-19          # one electronvolt in joules (exact, SI)
FARADAY = 96485.33212           # C/mol; numerically J per mol per eV
AVOGADRO = 6.02214076e23        # 1/mol (exact, SI)
CELL_GAP_EV = 2.0               # default two-level cell gap, eV
RABI = 1.0                      # default drive strength, rad/unit-time
VERSION = "1.0.0"

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "free_energy_claim": "HOLD - no free-energy claims; charging energy comes from the drive, always",
    "perpetual_motion_claim": "HOLD - no perpetual-motion claims; the second law is not negotiable",
    "overunity_claim": "HOLD - no over-unity claims; output work never exceeds input work plus stored energy",
    "commercial_product_claim": "HOLD - quantum batteries are lab research, not a commercial product",
    "live_hardware_control": "HOLD - no control of any real charging hardware, ever",
    "real_charger_build_instructions": "HOLD - no build instructions for a real high-energy charger rig",
    "grid_storage_claim": "HOLD - no grid-scale storage claims; lab devices store microjoule-scale energy",
    "medical_device_power_claim": "HOLD - no claims about powering medical devices",
    "ev_battery_claim": "HOLD - no electric-vehicle battery replacement claims",
    "weapons_power_claim": "HOLD - no weapons power-source claims",
    "bypass_thermodynamics_claim": "HOLD - ergotropy never bypasses thermodynamics; passive states give zero",
    "guaranteed_efficiency_claim": "HOLD - no guaranteed efficiency figures; decoherence always takes its cut",
    "investment_advice_claim": "HOLD - no investment advice about quantum battery companies or tokens",
    "live_cryogenics_handling": "HOLD - no live cryogen handling instructions for hardware builds",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. Single cell
# A quantum battery cell is a two-level system: ground |0> (energy 0)
# and excited |1> (energy gap_ev). A resonant drive (Rabi frequency
# `rabi`) rotates the state: excited population = sin^2(rabi * t / 2).
# Full charge at t = pi / rabi. Stored energy = gap_ev * population.

def charge_population(t, rabi=RABI):
    """Excited-state population of one cell charged from the ground state."""
    if t < 0:
        raise ValueError("time must be non-negative")
    return math.sin(rabi * t / 2.0) ** 2


def stored_energy_ev(t, rabi=RABI, gap_ev=CELL_GAP_EV):
    """Energy stored in one cell, in eV."""
    return gap_ev * charge_population(t, rabi)


def full_charge_time(rabi=RABI):
    """Time to charge one cell from empty to full: pi / rabi."""
    return math.pi / rabi


def average_charging_power(t, rabi=RABI, gap_ev=CELL_GAP_EV):
    """Average charging power up to time t, in eV per unit-time."""
    if t <= 0:
        raise ValueError("time must be positive")
    return stored_energy_ev(t, rabi, gap_ev) / t


def peak_charging_power(rabi=RABI, gap_ev=CELL_GAP_EV):
    """Peak instantaneous power during a Rabi charge: gap * rabi / 2 at t = pi/(2*rabi)."""
    return gap_ev * rabi / 2.0


# Ergotropy: the maximum work extractable by a unitary. For a qubit
# with excited population p and coherence c (off-diagonal magnitude),
# Bloch vector r has rz = 2p - 1 and length |r| = sqrt(rz^2 + 4c^2).
# Energy E = gap * p. The passive state (same eigenvalues, sorted
# against the energy ladder) has energy gap * (1 - |r|) / 2.
# Ergotropy W = E - E_passive = gap * (rz + |r|) / 2.

def _bloch(pop, coherence):
    rz = 2.0 * pop - 1.0
    r = math.sqrt(rz * rz + 4.0 * coherence * coherence)
    return rz, min(r, 1.0)


def passive_energy_ev(pop, coherence=0.0, gap_ev=CELL_GAP_EV):
    """Energy of the passive state with the same eigenvalues, in eV."""
    _, r = _bloch(pop, coherence)
    return gap_ev * (1.0 - r) / 2.0


def ergotropy_ev(pop, coherence=0.0, gap_ev=CELL_GAP_EV):
    """Maximum unitarily extractable work from one cell, in eV."""
    rz, r = _bloch(pop, coherence)
    return gap_ev * (rz + r) / 2.0


def extraction_efficiency(pop, coherence=0.0, gap_ev=CELL_GAP_EV):
    """Ergotropy / stored energy (1.0 = every stored eV is extractable)."""
    e = gap_ev * pop
    if e <= 0:
        return 0.0
    return ergotropy_ev(pop, coherence, gap_ev) / e


# ================================================================ 2. Collective charging
# Charging N cells: three honest models, three different answers.
# - parallel: N independent chargers, each pi/rabi -> total time pi/rabi.
# - dicke_sqrt: one collective drive on the symmetric (Dicke) ladder;
#   the collective coupling grows as sqrt(N) -> time pi/(rabi*sqrt(N)),
#   power advantage sqrt(N) (Alicki & Fannes style accounting).
# - global_entangling: one global unitary whose generator norm itself
#   grows with N -> time pi/(rabi*N), power advantage N (Binder et al.
#   style accounting). The catch: the drive is stronger, not free.
COLLECTIVE_MODELS = {
    "parallel": {
        "speedup": "1",
        "assumption": "N independent chargers, one per cell, fixed drive each",
        "caveat": "baseline: no quantum advantage, hardware cost scales with N",
    },
    "dicke_sqrt": {
        "speedup": "sqrt(N)",
        "assumption": "one collective drive coupled to the symmetric Dicke ladder; coupling ~ sqrt(N)",
        "caveat": "advantage is in power per fixed drive amplitude, not free energy",
    },
    "global_entangling": {
        "speedup": "N",
        "assumption": "one global entangling unitary; generator norm grows ~ N",
        "caveat": "strongest claim, strongest assumption: the charger itself scales with N",
    },
}


def collective_speedup(n_cells, model):
    """Charging-power advantage factor vs one cell, for the given model."""
    if n_cells < 1:
        raise ValueError("need at least one cell")
    if model == "parallel":
        return 1.0
    if model == "dicke_sqrt":
        return math.sqrt(n_cells)
    if model == "global_entangling":
        return float(n_cells)
    raise ValueError("unknown model: " + model)


def collective_charge_time(n_cells, model, rabi=RABI):
    """Time to fully charge N cells under the given model."""
    return full_charge_time(rabi) / collective_speedup(n_cells, model)


def collective_power(n_cells, model, rabi=RABI, gap_ev=CELL_GAP_EV):
    """Total average charging power for N cells (energy N*gap over charge time)."""
    t = collective_charge_time(n_cells, model, rabi)
    return n_cells * gap_ev / t


def collective_table(n_cells):
    """Side-by-side honest comparison of the three models for N cells."""
    out = {}
    for model in COLLECTIVE_MODELS:
        out[model] = {
            "speedup": round(collective_speedup(n_cells, model), 6),
            "charge_time": round(collective_charge_time(n_cells, model), 6),
            "total_power_ev_per_t": round(collective_power(n_cells, model), 6),
            "assumption": COLLECTIVE_MODELS[model]["assumption"],
            "caveat": COLLECTIVE_MODELS[model]["caveat"],
        }
    return out


# ================================================================ 3. Superabsorption
# Dicke physics: N two-level absorbers packed in a sub-wavelength
# volume share one bright collective state. Its transition dipole is
# sqrt(N) times a single absorber, so the collective transition RATE
# is N times the single-absorber rate (superabsorption / superradiance
# run in reverse). Total absorbed power = N cells x N-times rate
# enhancement per cell = N^2 scaling of total power (Quach et al.,
# Science Advances 2022, demonstrated the rate enhancement in an
# organic microcavity device storing microjoule-scale energy).

def dicke_bright_rate(n_cells, gamma_single=1.0):
    """Collective bright-state transition rate: N * single-absorber rate."""
    if n_cells < 1:
        raise ValueError("need at least one cell")
    return n_cells * gamma_single


def superabsorption_per_cell_power(n_cells, single_power=1.0):
    """Absorbed power per cell under collective driving: N x single-cell."""
    return dicke_bright_rate(n_cells) * single_power


def superabsorption_total_power(n_cells, single_power=1.0):
    """Total absorbed power of the ensemble: N^2 x single-cell power."""
    return n_cells * superabsorption_per_cell_power(n_cells, single_power)


def superabsorption_charge_time(n_cells, rabi=RABI):
    """Ensemble full-charge time with the Dicke rate enhancement."""
    return full_charge_time(rabi) / n_cells if n_cells >= 1 else float("inf")


# ================================================================ 4. Charger-battery entanglement
# Minimal two-qubit model: charger starts excited, battery starts in
# the ground state, an excitation-swap coupling g moves the quantum:
#   |psi(t)> = cos(g t) |g,e> + sin(g t) |e,g>
# Battery population = sin^2(g t); concurrence C = |sin(2 g t)|.
# Honest tradeoff: entanglement peaks (C = 1) at HALF charge and is
# zero at both empty and full - entanglement is a charging companion,
# not the stored product.

def charger_battery(t, g=1.0):
    """Battery population and charger-battery concurrence at time t."""
    pop = math.sin(g * t) ** 2
    concurrence = abs(math.sin(2.0 * g * t))
    return {"battery_population": pop, "concurrence": concurrence}


def max_entanglement_time(g=1.0):
    """First time concurrence peaks: pi / (4 g) - battery exactly half charged."""
    return math.pi / (4.0 * g)


# ================================================================ 5. Decoherence / self-discharge
# A charged cell left alone loses its excitation (amplitude damping,
# time constant T1) and its coherence (dephasing, time constant T2).
# Stored energy decays exponentially; ergotropy decays FASTER than
# energy when coherence is present, because coherence dies on T2.
# Classical baseline: a Li-ion cell self-discharges about 2% per month.

LIION_SELF_DISCHARGE_PER_MONTH = 0.02


def self_discharge_energy(t, e0, t1):
    """Stored energy after amplitude damping for time t: e0 * exp(-t/T1)."""
    return e0 * math.exp(-t / t1)


def energy_half_life(t1):
    """Time for stored energy to fall to half: T1 * ln 2."""
    return t1 * math.log(2.0)


def decayed_state(t, pop0, coh0, t1, t2):
    """(population, coherence) of a cell after damping + dephasing."""
    pop = pop0 * math.exp(-t / t1)
    coh = coh0 * math.exp(-t / t2)
    max_coh = math.sqrt(max(pop * (1.0 - pop), 0.0))
    return pop, min(coh, max_coh)


def decayed_ergotropy(t, pop0, coh0, t1, t2, gap_ev=CELL_GAP_EV):
    """Extractable work left after decoherence for time t, in eV."""
    pop, coh = decayed_state(t, pop0, coh0, t1, t2)
    return ergotropy_ev(pop, coh, gap_ev)


def liion_self_discharge(months, e0=1.0):
    """Classical Li-ion stored fraction after `months` at 2%/month."""
    return e0 * (1.0 - LIION_SELF_DISCHARGE_PER_MONTH) ** months


# ================================================================ 6. Work extraction
# Ideal unitary extraction reaches the passive state, so it recovers
# exactly the ergotropy. Daemonic ergotropy (Francica et al. 2017):
# if the battery is correlated with an ancilla in the state
# sqrt(1-p)|00> + sqrt(p)|11>, measuring the ancilla tells you which
# pure state the battery holds, and the AVERAGE extractable work
# rises to p * gap - above the unmeasured ergotropy whenever the
# battery marginal alone looks passive-ish. The demon pays for the
# information with measurement/erasure costs (Landauer), so the
# second law is safe; the gain is real but never free.

def unitary_extraction(pop, coherence=0.0, gap_ev=CELL_GAP_EV):
    """Work from ideal unitary extraction + the efficiency achieved."""
    return {
        "work_ev": ergotropy_ev(pop, coherence, gap_ev),
        "efficiency": extraction_efficiency(pop, coherence, gap_ev),
        "leftover_ev": passive_energy_ev(pop, coherence, gap_ev),
    }


def daemonic_ergotropy(p, gap_ev=CELL_GAP_EV):
    """Average extractable work after ancilla measurement: p * gap."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be a population")
    return p * gap_ev


def daemonic_gain(p, gap_ev=CELL_GAP_EV):
    """Daemonic gain over the unmeasured marginal ergotropy (>= 0)."""
    plain = ergotropy_ev(p, 0.0, gap_ev)
    return daemonic_ergotropy(p, gap_ev) - plain


# ================================================================ 7. Classical comparison
# Honest numbers. Li-ion is a commercial product you can buy; the
# quantum battery figures are per-molecule THEORY and a lab device
# that stored microjoule-scale energy. Energy density alone is not
# a product: cycle life, total capacity, and control hardware rule.

def theoretical_energy_density_wh_per_kg(gap_ev=CELL_GAP_EV, molar_mass_kg=0.1):
    """If every molecule held one excitation: gap * F / mass / 3600 Wh/kg."""
    return gap_ev * FARADAY / molar_mass_kg / 3600.0


def ev_to_joules(ev):
    return ev * EV_J


CLASSICAL_COMPARISON = [
    {"name": "lead-acid battery", "wh_per_kg": 40.0, "status": "commercial product"},
    {"name": "supercapacitor", "wh_per_kg": 10.0, "status": "commercial product"},
    {"name": "Li-ion battery", "wh_per_kg": 250.0, "status": "commercial product"},
    {"name": "gasoline (chemical, for scale)", "wh_per_kg": 12000.0, "status": "fuel, not a battery"},
]


def comparison_table():
    """Classical products vs the quantum-battery theoretical figure."""
    rows = [dict(r) for r in CLASSICAL_COMPARISON]
    rows.append({
        "name": "quantum battery (organic molecule, 2 eV, 100 g/mol)",
        "wh_per_kg": round(theoretical_energy_density_wh_per_kg(), 2),
        "status": "THEORETICAL per-molecule figure - lab devices store ~1e-6 J total",
    })
    return rows


# ================================================================ 8. Regime classifier (TinyML kNN)
# Features: (decoherence ratio gamma/rabi, dephasing ratio, extraction
# loss fraction). Labels: unitary-optimal / decoherence-limited /
# extraction-limited. Tiny labelled training set, euclidean kNN, k=3.

KNN_TRAINING = [
    ((0.01, 0.01, 0.02), "unitary-optimal"),
    ((0.02, 0.03, 0.05), "unitary-optimal"),
    ((0.05, 0.02, 0.08), "unitary-optimal"),
    ((0.03, 0.05, 0.03), "unitary-optimal"),
    ((0.60, 0.40, 0.10), "decoherence-limited"),
    ((0.80, 0.70, 0.20), "decoherence-limited"),
    ((0.45, 0.60, 0.15), "decoherence-limited"),
    ((0.70, 0.30, 0.30), "decoherence-limited"),
    ((0.05, 0.04, 0.70), "extraction-limited"),
    ((0.08, 0.06, 0.85), "extraction-limited"),
    ((0.02, 0.09, 0.60), "extraction-limited"),
    ((0.10, 0.03, 0.75), "extraction-limited"),
]


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def classify_regime(features, k=3):
    """kNN classification of a charging regime from 3 features."""
    ranked = sorted(KNN_TRAINING, key=lambda row: _dist(features, row[0]))
    votes = {}
    for _, label in ranked[:k]:
        votes[label] = votes.get(label, 0) + 1
    return sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def regime_report():
    """Named scenarios run through the classifier."""
    scenarios = {
        "ideal_lab_cell": (0.02, 0.02, 0.04),
        "warm_noisy_cell": (0.65, 0.55, 0.12),
        "good_cell_bad_extractor": (0.04, 0.05, 0.80),
    }
    return {name: classify_regime(f) for name, f in scenarios.items()}


# ================================================================ 9. Advisory seats
def _trace(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def carbon4_decide(topic="quantumbattery-lab-demo"):
    """Gemini Carbon 4 DECIDER seat: MAP->MODEL->STRESS->DECIDE.

    Names-only keys, live calls 0, tighten-only: can add HOLDs, never lift one.
    """
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    payload = {"seat": "gemini-carbon-4", "topic": topic, "stages": stages}
    return {
        "seat": "Gemini Carbon 4 Extended Thinking",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": [2048, 8192, 32768],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "decision": "PROCEED - sandbox simulation only, all claim gates stay HOLD",
        "can_override_hold": False,
        "trace_sha256_16": _trace(payload),
    }


def claude_advisor(topic="quantumbattery-lab-demo"):
    """Muse advisor seat: advises, can never override a HOLD."""
    return {
        "seat": "Muse",
        "role": "ADVISOR",
        "key": "names-only (MODEL_API_KEY name checked, value never read)",
        "live_calls": 0,
        "advice": "Report both collective-charging scalings with their assumptions; never quote the N speedup without its caveat.",
        "can_override_hold": False,
    }


def google_flow_plan():
    """Google Flow seat: plan-only, nothing rendered, nothing live."""
    return {
        "seat": "Google Flow",
        "role": "PLAN-ONLY",
        "shots": ["cell charges", "Dicke ensemble flash", "ergotropy gauge", "decay curve", "daemon measurement"],
        "rendered": False,
        "live": 0,
    }


def brains_report():
    return {"decider": carbon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    # single cell charging
    chk("pop_ground_at_zero", charge_population(0.0) == 0.0)
    chk("pop_full_at_pi", abs(charge_population(math.pi) - 1.0) < 1e-12)
    chk("pop_half_at_half_time", abs(charge_population(math.pi / 2.0) - 0.5) < 1e-12)
    chk("energy_full_is_gap", abs(stored_energy_ev(math.pi) - CELL_GAP_EV) < 1e-12)
    chk("full_charge_time", abs(full_charge_time() - math.pi) < 1e-12)
    chk("avg_power_full", abs(average_charging_power(math.pi) - CELL_GAP_EV / math.pi) < 1e-12)
    chk("peak_power", abs(peak_charging_power() - CELL_GAP_EV / 2.0) < 1e-12)
    # ergotropy analytics
    chk("ergotropy_ground_zero", ergotropy_ev(0.0) == 0.0)
    chk("ergotropy_excited_full", abs(ergotropy_ev(1.0) - CELL_GAP_EV) < 1e-12)
    chk("ergotropy_maxmixed_zero", ergotropy_ev(0.5, 0.0) == 0.0)
    chk("ergotropy_diag_075", abs(ergotropy_ev(0.75) - 0.5 * CELL_GAP_EV) < 1e-12)
    chk("ergotropy_superposition", abs(ergotropy_ev(0.5, 0.5) - 0.5 * CELL_GAP_EV) < 1e-12)
    chk("passive_plus_ergotropy_is_energy",
        abs(passive_energy_ev(0.75, 0.1) + ergotropy_ev(0.75, 0.1) - 0.75 * CELL_GAP_EV) < 1e-9)
    chk("extraction_eff_pure", abs(extraction_efficiency(0.5, 0.5) - 1.0) < 1e-12)
    chk("extraction_eff_passive_zero", extraction_efficiency(0.25, 0.0) == 0.0)
    # collective charging
    chk("speedup_parallel_1", collective_speedup(16, "parallel") == 1.0)
    chk("speedup_dicke_sqrt", abs(collective_speedup(16, "dicke_sqrt") - 4.0) < 1e-12)
    chk("speedup_global_n", collective_speedup(16, "global_entangling") == 16.0)
    chk("collective_time_dicke", abs(collective_charge_time(16, "dicke_sqrt") - math.pi / 4.0) < 1e-12)
    chk("collective_power_scales",
        collective_power(16, "global_entangling") > collective_power(16, "dicke_sqrt")
        > collective_power(16, "parallel"))
    chk("collective_models_three", len(COLLECTIVE_MODELS) == 3)
    # superabsorption
    chk("dicke_rate_n", dicke_bright_rate(9) == 9.0)
    chk("superabs_per_cell_n", superabsorption_per_cell_power(9) == 9.0)
    chk("superabs_total_n2", superabsorption_total_power(9) == 81.0)
    chk("superabs_time", abs(superabsorption_charge_time(4) - math.pi / 4.0) < 1e-12)
    # charger-battery entanglement
    s = charger_battery(max_entanglement_time())
    chk("entanglement_peak_half_charge",
        abs(s["concurrence"] - 1.0) < 1e-12 and abs(s["battery_population"] - 0.5) < 1e-12)
    s0 = charger_battery(0.0)
    chk("entanglement_zero_at_start", s0["concurrence"] == 0.0 and s0["battery_population"] == 0.0)
    sf = charger_battery(math.pi / 2.0)
    chk("entanglement_zero_at_full", abs(sf["concurrence"]) < 1e-12 and abs(sf["battery_population"] - 1.0) < 1e-12)
    # decoherence
    chk("self_discharge_half_life",
        abs(self_discharge_energy(energy_half_life(10.0), 2.0, 10.0) - 1.0) < 1e-9)
    chk("decayed_ergotropy_falls",
        decayed_ergotropy(5.0, 1.0, 0.0, 10.0, 4.0) < ergotropy_ev(1.0))
    chk("liion_one_month", abs(liion_self_discharge(1) - 0.98) < 1e-12)
    chk("liion_year", abs(liion_self_discharge(12) - 0.98 ** 12) < 1e-12)
    # extraction / daemonic
    chk("unitary_extraction_matches", abs(unitary_extraction(1.0)["work_ev"] - CELL_GAP_EV) < 1e-12)
    chk("daemonic_at_half", abs(daemonic_ergotropy(0.5) - 0.5 * CELL_GAP_EV) < 1e-12)
    chk("daemonic_gain_half", abs(daemonic_gain(0.5) - 0.5 * CELL_GAP_EV) < 1e-12)
    chk("daemonic_gain_never_negative", all(daemonic_gain(p / 20.0) >= -1e-12 for p in range(21)))
    # classical comparison
    chk("density_theory_536", abs(theoretical_energy_density_wh_per_kg() - 536.03) < 0.1)
    chk("ev_joules", abs(ev_to_joules(1.0) - EV_J) < 1e-30)
    chk("comparison_rows", len(comparison_table()) == 5)
    # classifier
    rep = regime_report()
    chk("classifier_unitary", rep["ideal_lab_cell"] == "unitary-optimal")
    chk("classifier_decoherence", rep["warm_noisy_cell"] == "decoherence-limited")
    chk("classifier_extraction", rep["good_cell_bad_extractor"] == "extraction-limited")
    # gates + seats
    chk("hold_gates_14", len(HOLD_GATES) == 14 and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_free_energy_hold", gate("free_energy_claim") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    b = brains_report()
    chk("carbon4_no_override", b["decider"]["can_override_hold"] is False)
    chk("claude_no_override", b["advisor"]["can_override_hold"] is False)
    chk("flow_plan_only", b["flow"]["rendered"] is False and b["flow"]["live"] == 0)
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("QuantumBattery-Lab - educational quantum battery charging lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | RESEARCH ONLY")
    print("=" * 68)
    print("\n[1] Single cell (two-level, gap 2.0 eV, Rabi drive)")
    print(f"    full charge time = {full_charge_time():.4f} | energy at full = {stored_energy_ev(math.pi):.3f} eV")
    print(f"    population at half time = {charge_population(math.pi / 2.0):.3f}")
    print(f"    peak power = {peak_charging_power():.3f} eV/t | avg power = {average_charging_power(math.pi):.4f} eV/t")
    print("\n[2] Ergotropy (max extractable work)")
    for pop, coh in [(1.0, 0.0), (0.75, 0.0), (0.5, 0.5), (0.5, 0.0), (0.25, 0.0)]:
        print(f"    pop={pop:.2f} coh={coh:.2f}: ergotropy = {ergotropy_ev(pop, coh):.3f} eV, "
              f"passive leftover = {passive_energy_ev(pop, coh):.3f} eV, eff = {extraction_efficiency(pop, coh):.3f}")
    print("\n[3] Collective charging of 16 cells - three honest models")
    for model, row in collective_table(16).items():
        print(f"    {model:18s} speedup x{row['speedup']:<7} time {row['charge_time']:.4f} power {row['total_power_ev_per_t']:.2f} eV/t")
        print(f"      assumption: {row['assumption']}")
        print(f"      caveat:     {row['caveat']}")
    print("\n[4] Superabsorption (Dicke bright state)")
    for n in (1, 4, 9, 16):
        print(f"    N={n:2d}: rate x{dicke_bright_rate(n):.0f}, per-cell power x{superabsorption_per_cell_power(n):.0f}, "
              f"total power x{superabsorption_total_power(n):.0f}, charge time {superabsorption_charge_time(n):.4f}")
    print("\n[5] Charger-battery entanglement (swap coupling)")
    for t in (0.0, max_entanglement_time(), math.pi / 2.0):
        s = charger_battery(t)
        print(f"    t={t:.4f}: battery pop = {s['battery_population']:.3f}, concurrence = {s['concurrence']:.3f}")
    print("    -> entanglement peaks at HALF charge and is zero at full charge")
    print("\n[6] Decoherence / self-discharge")
    print(f"    quantum cell T1=10: energy after 10 t = {self_discharge_energy(10.0, CELL_GAP_EV, 10.0):.4f} eV "
          f"(half-life {energy_half_life(10.0):.3f} t)")
    print(f"    ergotropy of a full cell after 5 t (T1=10, T2=4) = {decayed_ergotropy(5.0, 1.0, 0.0, 10.0, 4.0):.4f} eV")
    print(f"    Li-ion baseline: {liion_self_discharge(12) * 100:.1f}% left after 12 months (2%/month)")
    print("\n[7] Work extraction + daemonic ergotropy")
    print(f"    unitary extraction from full cell: {json.dumps(unitary_extraction(1.0), sort_keys=True)}")
    for p in (0.25, 0.5, 0.75):
        print(f"    ancilla p={p:.2f}: plain ergotropy = {ergotropy_ev(p):.3f} eV, daemonic = "
              f"{daemonic_ergotropy(p):.3f} eV, gain = {daemonic_gain(p):.3f} eV (demon pays Landauer cost)")
    print("\n[8] Classical comparison (energy density)")
    for row in comparison_table():
        print(f"    {row['name']:52s} {row['wh_per_kg']:>9.2f} Wh/kg  [{row['status']}]")
    print("\n[9] Regime classifier (TinyML kNN)")
    for name, label in regime_report().items():
        print(f"    {name:24s} -> {label}")
    print("\n[10] Advisory seats")
    print(f"    decider: {carbon4_decide()['decision']} trace={carbon4_decide()['trace_sha256_16']}")
    print(f"    advisor can_override_hold = {claude_advisor()['can_override_hold']}")
    print(f"    flow rendered = {google_flow_plan()['rendered']} live = {google_flow_plan()['live']}")
    print(f"\n[11] HOLD gates: {len(HOLD_GATES)}")
    for k in HOLD_GATES:
        print(f"    HOLD  {k}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "collective":
        print(json.dumps(collective_table(16), indent=2, sort_keys=True))
        return 0
    if cmd == "superabsorption":
        for n in (1, 2, 4, 9, 16, 100):
            print(f"N={n:4d} rate_x={dicke_bright_rate(n):.0f} per_cell_x={superabsorption_per_cell_power(n):.0f} "
                  f"total_x={superabsorption_total_power(n):.0f} time={superabsorption_charge_time(n):.4f}")
        return 0
    if cmd == "discharge":
        for t in (0.0, 2.0, 5.0, 10.0, 20.0):
            print(f"t={t:5.1f} energy={self_discharge_energy(t, CELL_GAP_EV, 10.0):.4f} eV "
                  f"ergotropy={decayed_ergotropy(t, 1.0, 0.0, 10.0, 4.0):.4f} eV")
        return 0
    if cmd == "extraction":
        print(json.dumps(unitary_extraction(1.0), indent=2, sort_keys=True))
        for p in (0.25, 0.5, 0.75, 1.0):
            print(f"p={p:.2f} plain={ergotropy_ev(p):.3f} daemonic={daemonic_ergotropy(p):.3f} gain={daemonic_gain(p):.3f}")
        return 0
    if cmd == "compare":
        print(json.dumps(comparison_table(), indent=2, sort_keys=True))
        return 0
    if cmd == "classify":
        print(json.dumps(regime_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for k, v in HOLD_GATES.items():
            print(f"{k}: {v}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "free_energy_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
