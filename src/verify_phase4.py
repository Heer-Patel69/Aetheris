"""verify_phase4.py — Import-check all Phase 4 modules."""
import sys
sys.path.insert(0, ".")

MODULES = [
    "runtime.event_store",
    "runtime.replay_engine",
    "runtime.projection_engine",
    "runtime.analytics_engine",
    "runtime.memory_engine",
    "runtime.observability",
    "runtime.runtime_gateway",
    "runtime.runtime_daemon",
    "runtime.dashboard_api",
    "intelligence.mie",
    "intelligence.pce",
    "intelligence.poe",
    "intelligence.ere",
    "intelligence.sre",
    "intelligence.fve",
    "intelligence.hde",
    "intelligence.optimization_engines",
    "intelligence.toe",
    "intelligence.coe",
    "intelligence.ple",
    "intelligence.eoe",
    "intelligence.io",
    "intelligence.insights",
    "intelligence.lce",
    "intelligence.kre",
    "intelligence.mmce",
    "intelligence.dsee",
    "intelligence.sbe",
    "kernel.mission_control",
    "kernel.cli_phase4",
    "kernel.core_phase4_patch",
]

ok = 0
errors = []

for m in MODULES:
    try:
        __import__(m)
        print(f"  OK   {m}")
        ok += 1
    except Exception as e:
        print(f"  ERR  {m}: {e}")
        errors.append((m, str(e)))

print()
print(f"Result: {ok}/{len(MODULES)} modules imported cleanly")
if errors:
    print("\nFailed:")
    for m, e in errors:
        print(f"  {m}: {e}")
sys.exit(0 if not errors else 1)
