import logging
import ollama  # Uses the Ollama Python library (pip install ollama)
from config import MODELS
from colorama import Style

class BaseAgent:
    def __init__(self, prompt_template, name="BaseAgent", debug=False, model=None, streaming=False, step_by_step=False):
        self.prompt_template = prompt_template
        self.name = name
        self.debug = debug
        self.streaming = streaming
        self.step_by_step = step_by_step
        # Use the provided model override or fallback to the default model from config.
        self.model = model if model is not None else MODELS.get("default", "default-model")
        self.logger = logging.getLogger(self.name)

    def log(self, message, level=logging.DEBUG):
        if self.debug:
            self.logger.log(level, message)

    def generate_prompt(self, **kwargs):
        prompt = self.prompt_template.format(**kwargs)
        self.log(f"Generated prompt: {prompt}")
        return prompt

    def call_model(self, prompt):
        self.log(f"Calling Ollama model '{self.model}' with prompt...")
        if self.streaming:
            try:
                print(f"{self.name} is streaming output...")
                response_stream = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=True
                )
                response_text = ""
                for chunk in response_stream:
                    chunk_text = chunk.get('message', {}).get('content', '')
                    print(chunk_text, end='', flush=True)
                    response_text += chunk_text
                print()  # Newline after streaming output.
                self.log(f"Received streaming response: {response_text}")
                return response_text
            except Exception as e:
                self.logger.error(f"Error streaming from Ollama: {e}")
                return ""
        else:
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                )
                response_text = response.get('message', {}).get('content', '')
                self.log(f"Received response: {response_text}")
                return response_text
            except Exception as e:
                self.logger.error(f"Error calling Ollama: {e}")
                return ""

    def run(self, **kwargs):
        prompt = self.generate_prompt(**kwargs)
        if self.step_by_step:
            print(f"\n----- {self.name} Prompt -----\n{prompt}\n------------------------------")
            input("Press Enter to send this prompt...")
        return self.call_model(prompt)
