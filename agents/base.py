import logging
import os
import re
from tqdm import tqdm  # Correctly import the tqdm function
import ollama  # Uses the Ollama Python library (pip install ollama)
from config import MODELS, SETTINGS
from colorama import Style, Fore
from collections import Counter

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
                tqdm.write(f"{response.status}", end="\r")  # Overwrite the same line
            
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
                tqdm.write(f"Model '{self.model}' not found. Pulling model...")
                self.download_model_with_progress(self.model)
                tqdm.write(f"Model '{self.model}' pulled successfully.")
            else:
                self.log(f"Model '{self.model}' is already available.")
        except Exception as e:
            self.logger.error(f"Error checking or pulling model '{self.model}': {e}")
            raise RuntimeError(f"Model '{self.model}' is not available and could not be pulled.")


    def call_model(self, prompt):
        break_on_repeated_sentences=SETTINGS.get("break_on_repeated_sentences", False)
        self.check_and_pull_model()
        self.log(f"Calling Ollama model '{self.model}' with prompt...")
        if self.streaming:
            try:
                while True:
                    print("-" * os.get_terminal_size().columns)
                    print(f"{Fore.BLUE}{self.name}{Fore.RESET} using {Fore.BLUE}{self.model}{Fore.RESET} is streaming...\n")
                    response_stream = ollama.chat(
                        model=self.model,
                        messages=[{'role': 'user', 'content': prompt}],
                        stream=True,
                        options=getattr(self, "options", {})  # Pass additional options
                    )
                    response_text = ""
                    loop_detected = False

                    count_store = 0
                    for chunk in response_stream:
                        chunk_text = chunk.get('message', {}).get('content', '')
                        print(chunk_text, end='', flush=True)
                        response_text += chunk_text

                        sentences = re.split(r'(?<=[.!?])\s+', response_text)
                        # Count the occurrences of each sentence
                        sentence_counts = Counter(sentences)
                        # Find sentences that repeat
                        repeated_sentences = [sentence for sentence, count in sentence_counts.items() if count > 1 and len(sentence) > SETTINGS.get("max_repeated_sentences", 10)]
                        # print a red "REPEAT" warning when a new repeated sentence is found
                        if len(repeated_sentences) > count_store:
                            print(f"{Fore.RED}REPEAT{Style.RESET_ALL}")
                            count_store = len(repeated_sentences)


                        if (len(repeated_sentences) > 10 and break_on_repeated_sentences) or len(repeated_sentences) > 100:
                            print(f"{Fore.RED}Warning: Found {len(repeated_sentences)} repeated sentences in generation, assuming a looping LLM generation, regenerating.{Style.RESET_ALL}")
                            loop_detected = True
                            break

                    if loop_detected:
                        # Optionally, add a short pause or logging
                        continue  # Retry the while loop to regenerate a response
                    else:
                        print("\n")  # Newline after streaming output.
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
                    options=getattr(self, "options", {})  # Pass additional options
                )
                response_text = response.get('message', {}).get('content', '')
                self.log(f"Received response: {response_text}")
                return response_text
            except Exception as e:
                self.logger.error(f"Error calling Ollama: {e}")
                return ""

    def estimate_tokens(self, text):
        # very basic estimation: count whitespace-separated words
        return len(text.split())

    def run(self, **kwargs):
        prompt = self.generate_prompt(**kwargs)
        estimated = self.estimate_tokens(prompt)
        tqdm.write(f"{self.name} prompt estimated tokens: {estimated}")
        if self.step_by_step:
            tqdm.write(f"\n----- {self.name} Prompt -----\n{prompt}\n------------------------------")
            input("Press Enter to send this prompt...")
        return self.call_model(prompt)
