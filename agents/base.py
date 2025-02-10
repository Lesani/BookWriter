import logging
from tqdm import tqdm  # Correctly import the tqdm function
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

    def download_model_with_progress(self, model_name):
        client = ollama.Client()
        
        progress_bar = None  # Initialize progress bar
        
        for response in client.pull(model_name, stream=True):
            if response.total and response.completed:
                percentage = (response.completed / response.total) * 100
                
                # Initialize progress bar if it's the first response
                if progress_bar is None:
                    progress_bar = tqdm(total=response.total, unit="B", unit_scale=True)
                
                # Update progress bar
                progress_bar.update(response.completed - progress_bar.n)

            else:
                print(f"{response.status}", end="\r")  # Overwrite the same line
            
        if progress_bar:
            progress_bar.close()  # Close progress bar when done

    def check_and_pull_model(self):
        try:
            # Retrieve available models
            available_models_response = ollama.list()
            available_models = available_models_response.models  # Extract the list of models

            self.log(f"Raw available models data: {available_models}")

            # Ensure we're working with correct attribute names
            available_model_names = [model.model.lower() for model in available_models]
            target_model = self.model.lower()

            self.log(f"Available models: {available_model_names}")
            self.log(f"Checking if model '{self.model}' is available...")

            if target_model not in available_model_names and f"{target_model}:latest" not in available_model_names:
                print(f"Model '{self.model}' not found. Pulling model...")
                self.download_model_with_progress(self.model)
                print(f"Model '{self.model}' pulled successfully.")
            else:
                self.log(f"Model '{self.model}' is already available.")
        except Exception as e:
            self.logger.error(f"Error checking or pulling model '{self.model}': {e}")
            raise RuntimeError(f"Model '{self.model}' is not available and could not be pulled.")


    def call_model(self, prompt):
        self.check_and_pull_model()
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
