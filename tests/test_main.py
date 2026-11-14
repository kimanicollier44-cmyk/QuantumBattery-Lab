import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main as qb


def test_population_zero(): assert qb.charge_population(0.0) == 0.0
def test_population_full(): assert abs(qb.charge_population(math.pi) - 1.0) < 1e-12
def test_population_half(): assert abs(qb.charge_population(math.pi / 2.0) - 0.5) < 1e-12
def test_population_negative_time():
    try:
        qb.charge_population(-1.0); assert False
    except ValueError:
        assert True
def test_stored_energy_full(): assert abs(qb.stored_energy_ev(math.pi) - qb.CELL_GAP_EV) < 1e-12
def test_full_charge_time(): assert abs(qb.full_charge_time() - math.pi) < 1e-12
def test_avg_power(): assert abs(qb.average_charging_power(math.pi) - qb.CELL_GAP_EV / math.pi) < 1e-12
def test_peak_power(): assert abs(qb.peak_charging_power() - qb.CELL_GAP_EV / 2.0) < 1e-12
def test_ergotropy_ground(): assert qb.ergotropy_ev(0.0) == 0.0
def test_ergotropy_excited(): assert abs(qb.ergotropy_ev(1.0) - qb.CELL_GAP_EV) < 1e-12
def test_ergotropy_maximally_mixed(): assert qb.ergotropy_ev(0.5, 0.0) == 0.0
def test_ergotropy_diagonal_075(): assert abs(qb.ergotropy_ev(0.75) - 0.5 * qb.CELL_GAP_EV) < 1e-12
def test_ergotropy_superposition(): assert abs(qb.ergotropy_ev(0.5, 0.5) - 0.5 * qb.CELL_GAP_EV) < 1e-12
def test_ergotropy_plus_passive():
    assert abs(qb.ergotropy_ev(0.8, 0.2) + qb.passive_energy_ev(0.8, 0.2) - 0.8 * qb.CELL_GAP_EV) < 1e-9
def test_ergotropy_never_exceeds_energy():
    for i in range(11):
        p = i / 10.0
        assert qb.ergotropy_ev(p, 0.3) <= p * qb.CELL_GAP_EV + 1e-9
def test_efficiency_pure(): assert abs(qb.extraction_efficiency(0.5, 0.5) - 1.0) < 1e-12
def test_efficiency_passive(): assert qb.extraction_efficiency(0.25, 0.0) == 0.0
def test_efficiency_empty(): assert qb.extraction_efficiency(0.0) == 0.0
def test_speedup_parallel(): assert qb.collective_speedup(100, "parallel") == 1.0
def test_speedup_dicke(): assert abs(qb.collective_speedup(25, "dicke_sqrt") - 5.0) < 1e-12
def test_speedup_global(): assert qb.collective_speedup(25, "global_entangling") == 25.0
def test_speedup_bad_model():
    try:
        qb.collective_speedup(4, "magic"); assert False
    except ValueError:
        assert True
def test_collective_time_dicke(): assert abs(qb.collective_charge_time(16, "dicke_sqrt") - math.pi / 4.0) < 1e-12
def test_collective_time_parallel(): assert abs(qb.collective_charge_time(16, "parallel") - math.pi) < 1e-12
def test_collective_power_order():
    assert qb.collective_power(16, "global_entangling") > qb.collective_power(16, "dicke_sqrt") > qb.collective_power(16, "parallel")
def test_collective_table_models(): assert set(qb.collective_table(4)) == {"parallel", "dicke_sqrt", "global_entangling"}
def test_dicke_rate(): assert qb.dicke_bright_rate(9) == 9.0
def test_superabsorption_per_cell(): assert qb.superabsorption_per_cell_power(9) == 9.0
def test_superabsorption_total_n2(): assert qb.superabsorption_total_power(9) == 81.0
def test_superabsorption_single(): assert qb.superabsorption_total_power(1) == 1.0
def test_superabsorption_time(): assert abs(qb.superabsorption_charge_time(4) - math.pi / 4.0) < 1e-12
def test_entanglement_start():
    s = qb.charger_battery(0.0); assert s["concurrence"] == 0.0 and s["battery_population"] == 0.0
def test_entanglement_peak():
    s = qb.charger_battery(qb.max_entanglement_time())
    assert abs(s["concurrence"] - 1.0) < 1e-12 and abs(s["battery_population"] - 0.5) < 1e-12
def test_entanglement_full():
    s = qb.charger_battery(math.pi / 2.0)
    assert abs(s["concurrence"]) < 1e-12 and abs(s["battery_population"] - 1.0) < 1e-12
def test_self_discharge_half_life():
    assert abs(qb.self_discharge_energy(qb.energy_half_life(10.0), 2.0, 10.0) - 1.0) < 1e-9
def test_self_discharge_monotonic():
    assert qb.self_discharge_energy(1.0, 2.0, 10.0) > qb.self_discharge_energy(5.0, 2.0, 10.0)
def test_decayed_ergotropy_falls(): assert qb.decayed_ergotropy(5.0, 1.0, 0.0, 10.0, 4.0) < qb.ergotropy_ev(1.0)
def test_decayed_state_bounds():
    pop, coh = qb.decayed_state(3.0, 0.5, 0.5, 10.0, 2.0)
    assert 0.0 <= pop <= 0.5 and coh <= math.sqrt(pop * (1.0 - pop)) + 1e-12
def test_liion_month(): assert abs(qb.liion_self_discharge(1) - 0.98) < 1e-12
def test_liion_year(): assert abs(qb.liion_self_discharge(12) - 0.98 ** 12) < 1e-12
def test_unitary_extraction_full(): assert abs(qb.unitary_extraction(1.0)["work_ev"] - qb.CELL_GAP_EV) < 1e-12
def test_unitary_extraction_leftover(): assert qb.unitary_extraction(0.25)["leftover_ev"] > 0
def test_daemonic_half(): assert abs(qb.daemonic_ergotropy(0.5) - 0.5 * qb.CELL_GAP_EV) < 1e-12
def test_daemonic_gain_half(): assert abs(qb.daemonic_gain(0.5) - 0.5 * qb.CELL_GAP_EV) < 1e-12
def test_daemonic_gain_nonnegative():
    assert all(qb.daemonic_gain(i / 20.0) >= -1e-12 for i in range(21))
def test_daemonic_gain_zero_at_full(): assert abs(qb.daemonic_gain(1.0)) < 1e-12
def test_density_theory(): assert abs(qb.theoretical_energy_density_wh_per_kg() - 536.03) < 0.1
def test_ev_to_joules(): assert qb.ev_to_joules(1.0) == qb.EV_J
def test_comparison_table():
    rows = qb.comparison_table()
    assert len(rows) == 5 and any("quantum battery" in r["name"] for r in rows)
def test_comparison_liion():
    rows = {r["name"]: r["wh_per_kg"] for r in qb.comparison_table()}
    assert rows["Li-ion battery"] == 250.0
def test_classifier_unitary(): assert qb.regime_report()["ideal_lab_cell"] == "unitary-optimal"
def test_classifier_decoherence(): assert qb.regime_report()["warm_noisy_cell"] == "decoherence-limited"
def test_classifier_extraction(): assert qb.regime_report()["good_cell_bad_extractor"] == "extraction-limited"
def test_hold_gates_count():
    assert len(qb.HOLD_GATES) == 14 and all(v.startswith("HOLD") for v in qb.HOLD_GATES.values())
def test_gate_free_energy(): assert qb.gate("free_energy_claim") == "HOLD"
def test_gate_perpetual(): assert qb.gate("perpetual_motion_claim") == "HOLD"
def test_gate_product(): assert qb.gate("commercial_product_claim") == "HOLD"
def test_gate_sandbox(): assert qb.gate("run_simulation") == "PROCEED"
def test_carbon4_seat():
    d = qb.carbon4_decide(); assert d["can_override_hold"] is False and d["live_calls"] == 0
def test_claude_seat(): assert qb.claude_advisor()["can_override_hold"] is False
def test_flow_seat():
    f = qb.google_flow_plan(); assert f["rendered"] is False and f["live"] == 0
def test_checks_all_pass():
    checks = qb.run_checks(); assert all(ok for _, ok in checks) and len(checks) == 48
def test_determinism():
    import io, contextlib
    a, b = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(a): qb.demo()
    with contextlib.redirect_stdout(b): qb.demo()
    assert a.getvalue() == b.getvalue()
