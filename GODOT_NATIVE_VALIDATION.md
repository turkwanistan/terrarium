# Godot Native Validation Safety Policy

This policy governs native Godot validation for Terrarium on `mcp-lab`.

## Why this exists

Godot 4.7.2 in the Lab currently renders through Mesa llvmpipe under Xvfb. A previous large batched capture workload became runaway/stuck and drove the host QEMU process to roughly 600% CPU. The VM required a forced stop. Native validation therefore must be bounded and observable.

## Required operating strategy

1. **One capture at a time.** Do not launch the full motion/variant matrix as one shell loop or long synchronous batch.
2. **Hard timeout per capture.** Wrap every Godot/Xvfb capture in an OS timeout. Default: 20 seconds unless a specific capture demonstrably needs more.
3. **Fresh process boundary.** Each capture starts a new bounded Godot process and exits after writing exactly one PNG.
4. **Cleanup after every capture.** After completion or timeout, verify no `godot`, `Xvfb`, `xvfb-run`, or llvmpipe-related process remains. Kill only lingering validation processes if necessary before proceeding.
5. **CPU sanity gate.** Check guest load/top CPU between captures. If validation-related CPU remains elevated after the capture exits, stop the sequence and diagnose before launching another capture.
6. **Prefer representative gates before exhaustive capture.** Validate identity/staging with a small representative set first: idle, walk, inspect contact, sleep settle/curled, wake exit, carry, place contact/release, window-watch; include rain/night idle. Expand only after these pass.
7. **Never treat a tunnel timeout/502 as permission to rerun blindly.** First inspect output files/process state to determine whether the guest command continued.
8. **No native-gate claim without native evidence.** Source hashes/tests can pass while native capture is incomplete; `STATUS.md` must distinguish those states.
9. **Host repo remains authoritative.** Lab is disposable validation infrastructure only. Do not move simulation authority or persistent project state into the Lab.
10. **No automatic VM reboot/restart loop.** If the Lab becomes runaway, stop validation, inspect from the host, and explicitly recover the VM before continuing.

## Current recommended capture form

Use a bounded command equivalent to:

```bash
timeout --signal=TERM --kill-after=3s 20s \
  xvfb-run -a /root/godot472/godot --path <project> -- \
  --variant <variant> --motion <motion> --manual-ms <ms> --capture <png>
```

Then immediately verify:

```bash
pgrep -a -f 'godot|Xvfb|xvfb-run' || true
uptime
ps -eo pid,ppid,%cpu,%mem,etime,comm,args --sort=-%cpu | head -12
```

The exact executable/project path may differ by disposable Lab copy; the safety requirements do not.
