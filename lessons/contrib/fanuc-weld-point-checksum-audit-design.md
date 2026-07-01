---
domain: "contrib"
title: "fanuc weld point checksum audit background design"
verification: "metadata-normalized"
{"title": "FANUC Weld Point Checksum Audit — Background Execution Design", "domain": "fanuc", "subdomain": "arc-welding", "tags": ["arc-welding", "checksum", "audit", "quality", "background-task", "pr-register", "ignition"], "source": "robot-forum.com", "status": "draft", "confidence": "0.75", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

Need to detect if arc welding points have been modified/touched on a FANUC robot, and log changes to PLC/Ignition/SQL — without pausing or faulting the production program.

## Root Cause

FANUC BG Logic has restrictions on PR access and TP instructions. Inline checksum calls risk blocking production. There is no native "background audit" feature in TP programming.

## Solution

### Architecture: Robot Calculates, PLC Decides

The robot only computes a lightweight checksum and sets a warning bit. The PLC handles logging and decision-making.

### Step 1: Copy Weld Points to Temporary PRs

```fanuc
-- In main weld program, before each weld:
R[91]=1              -- weld index
R[90]=3              -- total weld points
PR[85]=P[3]          -- copy weld point to temp PR
PR[86]=P[25]
PR[87]=P[4]
CALL CHECKXYZ
```

### Step 2: Checksum Program

```fanuc
/PROG CHECKXYZ
-- Read PR coordinates and compute checksum
-- R[92] = calculated checksum
-- Compare with saved baseline R[102]+
-- If mismatch: set DO[audit_warning]=ON
-- Send weld_number + checksum via GO to PLC
```

### Step 3: PLC-Side (Ignition/SQL)

- Receive weld_number + checksum via GO
- Compare against saved baseline in database
- Log mismatch event with timestamp
- Decide: log-only, warn, or hold next cycle

### Decision Matrix

| Audit Failure | Robot Action | PLC Action |
|---------------|-------------|------------|
| Checksum mismatch | Set DO warning ON | Log to SQL, alert operator |
| Checksum match | Continue welding | No action |
| Critical mismatch | — | HOLD next cycle, require manual reset |

## Verification

1. Manually modify a weld point PR on the robot
2. Run the weld program — CHECKXYZ detects the change
3. DO[audit_warning] turns ON
4. PLC logs the event with correct weld_number and coordinates
5. Production continues without interruption

## Notes

- BG Logic cannot access PRs or TP instructions — inline CALL is the only option
- Keep CHECKXYZ execution time minimal (< 10ms per call)
- Consider KAREL watcher task if TP performance is insufficient
- The "background" aspect is achieved by making the audit non-blocking: robot sets a bit, PLC decides
- No community replies yet (990 views) — design is unverified, treat as reference architecture
- Source: https://www.robot-forum.com/robotforum/thread/55071/
