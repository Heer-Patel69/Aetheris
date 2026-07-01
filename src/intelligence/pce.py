class PromptCompilerEngine:
    def __init__(self):
        pass
        
    def compile_prompt(self, template_name: str, variables: dict) -> dict:
        template = "Goal: {goal}\nContext: {context}"
        compiled = template.format(
            goal=variables.get("goal", "Undefined Goal"),
            context=variables.get("context", "No Context")
        )
        return {
            "template_used": template_name,
            "prompt": compiled,
            "version": "1.0.0"
        }
