import os
from pathlib import Path

class TechnologyIntelligence:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        
    def evaluate_tech_stack(self, goal_tree):
        """
        Evaluates tech selections and justifies choices based on goal properties.
        """
        selections = {
          "database": {
              "choice": "PostgreSQL",
              "reason": "Structured relations with foreign keys and strict RLS requirements",
              "alternatives": ["MongoDB", "SQLite"],
              "confidence": 0.95
          },
          "frontend": {
              "choice": "Next.js",
              "reason": "Server Component rendering and native routing speed optimization",
              "alternatives": ["React+Vite", "Vue"],
              "confidence": 0.88
          },
          "orm": {
              "choice": "Prisma",
              "reason": "Provides type-safe access and seamless migration management with PostgreSQL",
              "alternatives": ["TypeORM", "Drizzle"],
              "confidence": 0.92
          },
          "deployment": {
              "choice": "Docker",
              "reason": "Ensures environment portability across development and production staging",
              "alternatives": ["Serverless", "Bare-metal"],
              "confidence": 0.90
          }
        }
        
        # Check if the goal specifies special overrides
        goal_text = goal_tree.get("original_goal", "").lower()
        if "mongo" in goal_text or "nosql" in goal_text:
            selections["database"] = {
                "choice": "MongoDB",
                "reason": "User explicitly requested NoSQL document schema design",
                "alternatives": ["PostgreSQL"],
                "confidence": 0.99
            }
            selections["orm"] = {
                "choice": "Mongoose",
                "reason": "Standard ODM mapping library for MongoDB",
                "alternatives": ["Prisma"],
                "confidence": 0.95
            }
            
        return selections
