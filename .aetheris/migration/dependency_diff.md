# Dependency Diff

- **Before:** Direct imports of planners inside pre.py (Execution -> Planning layer violation).
- **After:** decoupled pre.py via event bus emission.