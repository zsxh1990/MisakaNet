---
domain: "contrib"
title: "fanuc roboguide does not support profinet simulation"
verification: "metadata-normalized"
{"title": "FANUC Roboguide Does Not Support Profinet Simulation", "domain": "fanuc", "subdomain": "roboguide", "tags": ["roboguide", "profinet", "simulation", "gsdml", "tia-portal", "ethernet-ip"], "source": "robot-forum.com", "status": "draft", "confidence": "0.95", "created": "2026-07-01", "verified_date": "", "domain_expert": ""}
---

## Problem

User tries to connect Roboguide to Siemens TIA Portal via Profinet for basic IO testing. Cannot find the FANUC GSDML file anywhere in the Roboguide installation.

## Root Cause

Roboguide does not support Profinet simulation. This is a product limitation, not a configuration issue. The GSDML file is not included because the protocol is not simulated.

## Solution

### For Virtual/Simulation Testing

Use Ethernet/IP instead of Profinet in Roboguide:

1. Enable Ethernet/IP on the virtual robot controller
2. Configure IO mapping via Ethernet/IP
3. Test basic IO toggling between PLC ↔ robot in simulation

### For Profinet Testing

Profinet testing requires the physical robot and controller:

1. Install the FANUC Profinet GSDML on the engineering workstation
2. Import GSDML into TIA Portal
3. Configure device name + IP on the real controller
4. Map IO (rack/slot) in TIA Portal
5. Verify IO toggling on the real hardware

## Verification

1. In Roboguide: Ethernet/IP IO toggles work between virtual robot and simulated PLC
2. On real hardware: Profinet communication established, IO exchanges correctly
3. GSDML file version matches controller firmware version

## Notes

- Roboguide supports Ethernet/IP simulation but NOT Profinet
- Always check simulation software protocol support before starting integration
- For Profinet commissioning, plan for real-hardware testing time
- Source: https://www.robot-forum.com/robotforum/thread/55025/
