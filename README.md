# Cross-Platform HID Attack Detection & Response

A lightweight cross-platform host-based detection and response prototype for detecting
USB Rubber Ducky-style HID keystroke-injection attacks on Windows 11 and Ubuntu Linux.

The system correlates USB/HID device activity, keystroke timing behaviour, and process
creation events using transparent rule-based scoring. It can generate alerts, maintain
structured audit logs, and optionally perform controlled response actions.

> Final Year Project for the Bachelor of Science (Honours) in Computer Science
> (Cyber Security) at Asia Pacific University of Technology & Innovation (APU).

---

## Overview

USB Human Interface Devices (HIDs), such as keyboards, are normally trusted automatically
by modern operating systems. A malicious programmable USB device can abuse this trust by
presenting itself as a keyboard and injecting pre-programmed keystrokes at high speed.

This project implements a host-based detection and response prototype that monitors several
behavioural indicators instead of relying on a single detection method.

The prototype was developed and tested on:

- Windows 11 Pro
- Ubuntu 24.04 LTS
- VMware Workstation Pro
- Arduino Leonardo for safe HID simulation

The system is implemented mainly in Python and uses platform-specific mechanisms for
device monitoring while sharing common scoring, logging, and response logic.

---

## Problem Statement

USB Rubber Ducky-style attacks are difficult to distinguish from legitimate keyboard activity
because the operating system treats the connected HID device as a trusted input source.

A single indicator is not sufficient for reliable detection:

- A newly connected keyboard may be legitimate.
- Rapid typing may come from macros or accessibility software.
- A command shell may be opened normally by the user.

This project therefore correlates multiple host-observed indicators:

1. A newly detected USB/HID keyboard device
2. Rapid or highly regular keystroke activity
3. Relevant process creation shortly after suspicious input

The combination of these signals provides stronger evidence than any individual event.

---

## Key Features

- Cross-platform monitoring for Windows 11 and Ubuntu Linux
- USB/HID connection detection
- Privacy-preserving keystroke timing analysis
- Process creation monitoring
- Multi-signal event correlation
- Transparent weighted scoring
- Three classification levels:
  - Normal
  - Suspicious
  - Attack-related
- Desktop and console alerts
- CSV and JSONL structured security logging
- Optional Windows session locking
- Allowlisted suspicious-process termination
- Configurable detection thresholds
- Safe Arduino Leonardo HID simulation
- Automated unit, functional, black-box, and user acceptance testing

---

## System Architecture

The system follows a multi-stage host-based detection pipeline:

USB/HID Device Event
        |
        v
Keystroke Timing Monitor
        |
        v
Process Monitor
        |
        v
Event Correlation
        |
        v
Rule-Based Scoring Engine
        |
        +------------------+
        |                  |
        v                  v
   Classification       Logging
        |
        +----------+-----------+
        |          |           |
      Normal   Suspicious   Attack-related
                   |           |
                   v           v
                 Alert       Alert
                              Log
                              Optional Response

The Windows and Ubuntu agents normalise platform-specific observations into a common event
representation before they are processed by the shared scoring engine.

---

## Detection Logic

The detection engine combines three main evidence groups.

### 1. HID Device Evidence

The system detects newly connected keyboard-class HID devices and records the event as
context for subsequent activity.

A new keyboard connection alone is not treated as an attack.

### 2. Keystroke Timing Evidence

The keystroke monitor records timing metadata rather than the actual characters typed.

The system evaluates characteristics such as:

- number of keystrokes in a burst
- mean inter-key interval
- timing regularity
- coefficient of variation

Very rapid or highly regular input contributes to the suspicion score.

### 3. Process Evidence

The system monitors for newly created processes that match configured categories such as:

- command shells
- scripting hosts
- interpreters
- terminal applications

Examples used during testing include:

- `cmd.exe` on Windows
- `bash` on Ubuntu

Process activity occurring shortly after suspicious HID input receives additional correlation
weight.

### Classification

The final score determines the classification:

- Normal: below suspicious threshold
- Suspicious: score >= 40
- Attack-related: score >= 70

The thresholds are configurable and can be adjusted without modifying the source code.

---

## Windows 11 Agent

The Windows agent uses user-space monitoring mechanisms and does not require a custom
kernel driver.

USB/HID monitoring uses PowerShell PnP/CIM queries to enumerate keyboard-class devices.

At startup, existing devices are treated as the baseline. When a previously unseen device
instance is detected, the system generates a HID connection event.

The implementation also excludes processes created internally by the monitoring agent to prevent
its own PowerShell device queries from generating false security alerts.

The Windows implementation supports:

- HID device monitoring
- keystroke timing analysis
- process monitoring
- desktop alerts
- CSV/JSONL logging
- optional session locking
- controlled allowlisted process termination

---

## Ubuntu Agent

The Ubuntu implementation monitors Linux input-subsystem activity and uses `udev` information
to identify keyboard-class devices.

The project uses `pyudev` for Linux device-event monitoring while sharing the same higher-level
event model and scoring engine used by the Windows implementation.

The Ubuntu agent supports:

- HID connection monitoring
- keystroke timing analysis
- process monitoring
- desktop notifications
- CSV/JSONL logging
- cross-platform scoring and classification

Device re-enumeration caused by Arduino resets, sketch uploads, or VMware USB ownership
changes is treated as genuine device-state activity rather than automatically being considered
an attack.

---

## Safe HID Simulation

An Arduino Leonardo was used to safely simulate keyboard-style HID activity.

Four controlled scenarios were created:

### AS-01 - Human-like Automated Typing

Produces automated input using variable delays.

Purpose:
Evaluate false-positive behaviour when automated typing more closely resembles human input.

### AS-02 - Rapid Harmless Text Injection

Produces high-speed non-destructive text input.

Purpose:
Test detection of rapid keystroke injection.

### AS-03 - Repetitive-Key Injection

Generates highly regular automated key activity.

Purpose:
Test detection based on timing regularity and low variability.

### AS-04 - Safe Shell-Process Launch

Produces a controlled input sequence that launches a harmless shell process.

Purpose:
Test full correlation between:

HID connection -> keystroke burst -> process creation

All simulations used in this repository are intended to remain visible, reversible, and
non-destructive.

They do not perform credential theft, malware installation, persistence, security-control
bypass, or data exfiltration.

---

## Installation

### Requirements

- Python 3
- Windows 11 or Ubuntu 24.04
- VMware Workstation Pro is optional but recommended for isolated testing
- Arduino Leonardo is required only for the hardware simulation scenarios

### Clone the repository

```bash
git clone https://github.com/zijet/cross-platform-hid-detection-response.git
cd cross-platform-hid-detection-response
