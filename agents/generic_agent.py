import re
from colorama import Fore, Style, init
from config import THINKING_TOKENS, AGENT_COLORS
from agents.base import BaseAgent

init(autoreset=False)

class GenericAgent(BaseAgent):
    def __init__(self, prompt_template, agent_name, debug=False, model="default",
                streaming=False, step_by_step=False, options=None):
        self.options = options or {}
        self.agent_name = agent_name
        super().__init__(prompt_template, name=agent_name, debug=debug, model=model,
                        streaming=streaming, step_by_step=step_by_step)
        self.thinking_enabled = "## THINKING PHASE" in prompt_template
        base_agent_name = agent_name.split('-')[0] if '-' in agent_name else agent_name
        self.color = AGENT_COLORS.get(base_agent_name, Fore.WHITE)
        self.thinking_color = AGENT_COLORS.get("thinking_color", Fore.WHITE)
        
    def run(self, **kwargs):
        prompt = self.generate_prompt(**kwargs)
        if self.thinking_enabled:
            print(f"{self.color}[{self.agent_name} thinking...]{Style.RESET_ALL}")
        # Call BaseAgent’s call_model to get the full response (streaming handled there)
        response_text = super().call_model(prompt)
        if self.thinking_enabled:
            final_response = self.get_final_output_from_response(response_text)
            if self.debug:
                thinking_response = self.get_thinking_from_response(response_text)
                print(f"{Fore.YELLOW}[Thinking Process]{Style.RESET_ALL}\n{thinking_response}")
            return final_response
        else:
            return response_text
        
    def get_thinking_from_response(self, text):
        try:
            for start_pattern in THINKING_TOKENS["start_patterns"]:
                for end_pattern in THINKING_TOKENS["end_patterns"]:
                    pattern = f"{start_pattern}(.*?)(?:{end_pattern})"
                    thinking_match = re.search(pattern, text, re.DOTALL)
                    if thinking_match:
                        return f"{start_pattern}{thinking_match.group(1)}"
            return ""
        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error extracting thinking phase: {e}{Style.RESET_ALL}")
            return ""
    
    def get_final_output_from_response(self, text):
        try:
            for end_pattern in THINKING_TOKENS["end_patterns"]:
                pattern = f"(?:{end_pattern})(.*)"
                final_match = re.search(pattern, text, re.DOTALL)
                if final_match:
                    return final_match.group(1).strip()
            for start_pattern in THINKING_TOKENS["start_patterns"]:
                thinking_content = re.search(f"{start_pattern}.*", text, re.DOTALL)
                if thinking_content:
                    text_parts = text.split(thinking_content.group(0), 1)
                    if len(text_parts) > 1 and text_parts[1].strip():
                        return text_parts[1].strip()
            return text
        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error extracting final output: {e}{Style.RESET_ALL}")
            return text