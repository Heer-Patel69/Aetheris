# Aetheris System Architecture Diagrams

This document contains Mermaid sources representing the system architecture.

## 1. Overall Component Architecture
```mermaid
graph TD
    User["User Goal / Objective"] --> Auth["Enterprise Auth (platform.py)"]
    Auth --> Sandbox["Sandbox Activation (sandbox.py)"]
    Sandbox --> Kernel["Aetheris Kernel (core.py)"]
    Kernel --> Org["AI Org Collaboration (agents.py)"]
    Org --> Planner["Planner (planner.py)"]
    Planner --> Exec["Execution Scheduler (es.py)"]
    Exec --> Quality["Quality Gate (qia.py)"]
    Quality --> EKB["EKB Persistence (ekb.py)"]
    EKB --> Learn["Learning Loop (engine.py)"]
    Learn --> Evol["Self-Evolution Loop (orchestrator.py)"]
    Evol --> Exit["Sandbox Shutdown & Exit"]
```

## 2. Sequence Diagram: Sandbox Execution
```mermaid
sequenceDiagram
    participant K as Kernel
    participant S as Sandbox
    participant E as SandboxedExecutor
    
    K->>S: start()
    S-->>K: Status ACTIVE
    K->>E: execute(cmd)
    E->>E: Check path is_safe()
    E-->>K: Execution Result
    K->>S: stop()
```
