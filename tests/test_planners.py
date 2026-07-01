import unittest
import shutil
import json
from pathlib import Path
from intelligence.ekb import EngineeringKnowledgeBase
from intelligence.planners import (
    DesignPlanningEngine,
    FrontendPlanningEngine,
    BackendPlanningEngine
)

class TestPlanners(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_planners_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.ekb = EngineeringKnowledgeBase(str(self.workspace_path))
        
        self.design_planner = DesignPlanningEngine(str(self.workspace_path), self.ekb)
        self.frontend_planner = FrontendPlanningEngine(str(self.workspace_path), self.ekb)
        self.backend_planner = BackendPlanningEngine(str(self.workspace_path), self.ekb)

        self.product_plan = {
            "domain": "Web Front-End SaaS Domain",
            "flows": [
                {"flow_id": "flow:auth_login", "name": "Login flow"},
                {"flow_id": "flow:billing_transactions", "name": "Billing flow"}
            ]
        }
        
        self.architecture_plan = {
            "boundaries": [
                {"context": "IdentityAccessContext", "features": ["Login", "Logout"]},
                {"context": "BillingContext", "features": ["Charge", "Invoice"]}
            ]
        }

    def tearDown(self):
        if self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

    def test_design_planning_engine(self):
        plan = self.design_planner.plan_design(self.product_plan)
        
        self.assertEqual(plan["style"], "Modern Glassmorphism")
        self.assertEqual(plan["tokens"]["colors"]["primary"], "hsl(140, 70%, 35%)")
        
        # Verify workspace files written
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "design" / "tokens.json").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "design" / "guidelines.md").exists())

    def test_frontend_planning_engine(self):
        design_plan = self.design_planner.plan_design(self.product_plan)
        fe_plan = self.frontend_planner.plan_frontend(self.product_plan, design_plan)
        
        # Should have routes for root, login, billing
        routes = fe_plan["routing"]["routes"]
        paths = {r["path"] for r in routes}
        self.assertIn("/", paths)
        self.assertIn("/login", paths)
        self.assertIn("/billing_transactions", paths)
        
        # Verify protected flag on dashboard routes
        billing_route = next(r for r in routes if r["path"] == "/billing_transactions")
        self.assertEqual(billing_route["type"], "protected")

    def test_backend_planning_engine(self):
        be_plan = self.backend_planner.plan_backend(self.product_plan, self.architecture_plan)
        
        # Verify modules, services, controllers exist and map context names
        modules = be_plan["modules"]["modules"]
        self.assertEqual(len(modules), 2)
        names = {m["name"] for m in modules}
        self.assertIn("IdentityAccessContext", names)
        self.assertIn("BillingContext", names)
        
        # Verify services map feature methods
        services = be_plan["services"]["services"]
        billing_service = next(s for s in services if s["name"] == "BillingContextService")
        self.assertIn("execute_charge", billing_service["methods"])
        self.assertIn("execute_invoice", billing_service["methods"])

    def test_tdd_compiler_reports(self):
        from intelligence.planners import TechnicalDesignDocumentCompiler
        compiler = TechnicalDesignDocumentCompiler(str(self.workspace_path), self.ekb)
        compiler.compile_tdd_reports()
        
        # Verify files created
        planning_dir = self.workspace_path / ".aetheris" / "planning"
        self.assertTrue((planning_dir / "engineering_review.json").exists())
        self.assertTrue((planning_dir / "resource.plan.json").exists())
        self.assertTrue((planning_dir / "dependency.plan.json").exists())
        self.assertTrue((planning_dir / "risk.plan.json").exists())
        self.assertTrue((planning_dir / "cost.plan.json").exists())
        self.assertTrue((planning_dir / "tradeoffs.json").exists())

        # Verify EKB registry
        review = self.ekb.query_objects({"type": "engineering_review"})
        self.assertEqual(len(review), 1)
        self.assertIn("tier_10000000_users", review[0]["content"]["scalability"])

        cost = self.ekb.query_objects({"type": "cost_plan"})
        self.assertEqual(cost[0]["content"]["monthly_estimate_usd"], 130.00)

    def test_database_and_api_planning_engines(self):
        from intelligence.planners import DatabasePlanningEngine, APIPlanningEngine
        db_engine = DatabasePlanningEngine(str(self.workspace_path), self.ekb)
        api_engine = APIPlanningEngine(str(self.workspace_path), self.ekb)
        
        db_res = db_engine.plan(self.product_plan)
        api_res = api_engine.plan(self.product_plan)
        
        self.assertEqual(db_res["database"]["engine"], "PostgreSQL")
        self.assertEqual(api_res["api"]["protocol"], "REST")
        
        # Verify file presence
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "database" / "entities.plan.json").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "api" / "endpoint.plan.json").exists())

    def test_security_planning_engine(self):
        from intelligence.planners import SecurityPlanningEngine
        sec_engine = SecurityPlanningEngine(str(self.workspace_path), self.ekb)
        res = sec_engine.plan(self.product_plan)
        
        self.assertEqual(res["auth"]["token_standard"], "JWT")
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "security" / "threat.model.json").exists())

    def test_final_engineering_blueprint_compiler(self):
        from intelligence.planners import (
            DesignPlanningEngine, FrontendPlanningEngine,
            DatabasePlanningEngine, APIPlanningEngine, SecurityPlanningEngine,
            DisasterRecoveryPlanningEngine, CostPlanningEngine, FinalEngineeringBlueprintCompiler
        )
        # Seed dependencies
        dp = DesignPlanningEngine(str(self.workspace_path), self.ekb).plan_design(self.product_plan)
        FrontendPlanningEngine(str(self.workspace_path), self.ekb).plan_frontend(self.product_plan, dp)
        DatabasePlanningEngine(str(self.workspace_path), self.ekb).plan(self.product_plan)
        APIPlanningEngine(str(self.workspace_path), self.ekb).plan(self.product_plan)
        SecurityPlanningEngine(str(self.workspace_path), self.ekb).plan(self.product_plan)
        DisasterRecoveryPlanningEngine(str(self.workspace_path), self.ekb).plan(self.product_plan)
        CostPlanningEngine(str(self.workspace_path), self.ekb).plan(self.product_plan)

        febc = FinalEngineeringBlueprintCompiler(str(self.workspace_path), self.ekb)
        blueprint = febc.compile_blueprint()

        self.assertEqual(blueprint["summary"]["validation_status"], "PASSED_WITH_WARNINGS")
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "engineering.blueprint.json").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "engineering.blueprint.md").exists())
        
        # Verify SPEC-031 Validation scores & cross checks
        val_report = blueprint["validation_report"]
        self.assertEqual(val_report["scores"]["Architecture"], 98)
        self.assertIn("RPO vs Backup Strategy: PASS", val_report["validation_passes"])

        # Verify Resource/KPI metrics
        self.assertEqual(blueprint["kpis"]["estimated_lines_of_code"], 1500)
        self.assertEqual(blueprint["complexity"]["complexity_level"], "Medium")

        # Verify Memory versioning & Diff creation on subsequent compile
        blueprint2 = febc.compile_blueprint()
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "blueprint.diff.json").exists())
        self.assertTrue((self.workspace_path / ".aetheris" / "planning" / "history" / "blueprint_v2.json").exists())

if __name__ == "__main__":
    unittest.main()
