from agents.base import BaseAgent

class GenericAgent(BaseAgent):
    def __init__(self, prompt_template, agent_name, debug=False, model=None, streaming=False, step_by_step=False):
        super().__init__(
            prompt_template,
            name=agent_name,
            debug=debug,
            model=model,
            streaming=streaming,
            step_by_step=step_by_step
        )

    def run(self, **variables):
        prompt = self.generate_prompt(**variables)
        return self.call_model(prompt)