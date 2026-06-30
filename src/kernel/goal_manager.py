import os
import sys
import re
from pathlib import Path

class GoalManager:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        
    def expand_goal(self, user_goal):
        """
        Parses the user query/goal, infers secondary objectives (auth, DB, APIs),
        detects assumptions, and constructs the Goal Expansion Tree.
        """
        user_goal_lower = user_goal.lower()
        
        # Core base goal parameters
        expanded = {
            "original_goal": user_goal,
            "inferred_subsystems": [],
            "assumptions": [],
            "critical_uncertainties": [],
            "completeness_targets": {
                "database": "Required",
                "auth": "Required",
                "api": "Required",
                "frontend": "Required",
                "tests": "Required",
                "docker": "Required",
                "ci_cd": "Required",
                "documentation": "Required"
            }
        }
        
        # 1. Subsystem Inference based on keyword detection
        if "auth" in user_goal_lower or "login" in user_goal_lower or "user" in user_goal_lower:
            expanded["inferred_subsystems"].append("authentication")
            expanded["assumptions"].append("JWT or OAuth based authentication is required.")
        else:
            # Autonomously infer authentication anyway per ASE-OS rules
            expanded["inferred_subsystems"].append("authentication (inferred)")
            
        if "payment" in user_goal_lower or "stripe" in user_goal_lower or "checkout" in user_goal_lower:
            expanded["inferred_subsystems"].append("payments")
            expanded["completeness_targets"]["payments"] = "Required"
            # Critical uncertainty: require payment gateway keys or model parameters
            expanded["critical_uncertainties"].append({
                "topic": "Payment Gateway",
                "reason": "Missing Stripe API credentials or sandbox keys.",
                "confidence": 0.50
            })
            
        if "search" in user_goal_lower or "find" in user_goal_lower:
            expanded["inferred_subsystems"].append("search_indexing")
            
        if "admin" in user_goal_lower or "dashboard" in user_goal_lower:
            expanded["inferred_subsystems"].append("admin_panel")
            
        # Default inferred engineering subsystems (always inferred autonomously)
        expanded["inferred_subsystems"].extend([
            "database_migrations",
            "api_controllers",
            "frontend_views",
            "unit_testing",
            "dockerization",
            "deployment_pipelines"
        ])
        
        return expanded
