---
domain: "contrib"
title: "fanuc roboguide v10 import tp rotary a not loadable"
verification: "metadata-normalized"
{"title": "FANUC Roboguide v10 Import TP — Rotary_A Not Loadable", "domain": "fanuc", "subdomain": "roboguide", "tags": ["roboguide", "tp-import", "workcell", "vrc", "rotary-a", "aoa-backup"], "source": "robot-forum.com", "status": "draft", "confidence": "0.9", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

Creating a new Workcell in Roboguide v10 and importing TP files from a real robot backup fails with "Rotary_A not loadable" error. The virtual robot configuration matches the real one.

## Root Cause

Roboguide v10 ships with only R-50iA VRC (Virtual Robot Controller) by default. If the real robot uses R-30iB Plus or other controller versions, the required VRC simulator is not installed, causing import failures.

## Solution

### Step 1: Use AOA Backup Instead of Manual Import

Do NOT create a Workcell from scratch and import TP files. Instead:

1. Create new Workcell → select "Create from Robot Backup"
2. Point to the AOA (full backup) directory from the real robot
3. Roboguide recreates the robot exactly: TP programs, IO, registers, system variables — everything

### Step 2: Install Missing VRC Versions

1. Insert or mount the Roboguide installation media
2. Browse to root directory → `FVRC930/` or `FVRC9XX/`
3. Run `setup.exe` to install the required controller version
4. Restart Roboguide, verify in: Menu bar → Bottom left → Version Info

### Step 3: Windows 11 Compatibility

Some older VRC installers may not run on Windows 11. Check Roboguide 10 release notes for known exceptions or contact FANUC support.

## Verification

1. After installing VRC, Version Info should list the target controller (e.g., R-30iB Plus V9.40)
2. Create Workcell from AOA backup succeeds without "Rotary_A" error
3. All TP programs, IO mapping, and registers match the real robot

## Notes

- .TP file import ≠ .LS file import — different mechanisms, different failure modes
- AOA backup restore is always preferred over manual TP import
- "Create from Robot Backup" is the recommended workflow for new Workcells
- Source: https://www.robot-forum.com/robotforum/thread/55008/
