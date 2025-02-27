import logging
import os
import re
from collections import Counter
from tqdm import tqdm
import ollama
from config import MODELS, SETTINGS, THINKING_TOKENS, AGENT_COLORS
from colorama import Style, Fore
                        
class BaseAgent:
    def __init__(self, prompt_template, name="BaseAgent", debug=False, model=None, streaming=False, step_by_step=False):
        self.prompt_template = prompt_template
        self.name = name
        self.debug = debug
        self.streaming = streaming
        self.step_by_step = step_by_step
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
        progress_bar = None
        for response in client.pull(model_name, stream=True):
            if response.total and response.completed:
                percentage = (response.completed / response.total) * 100
                if progress_bar is None:
                    progress_bar = tqdm(total=response.total, unit="B", unit_scale=True)
                progress_bar.update(response.completed - progress_bar.n)
            else:
                tqdm.write(f"{response.status}", end="\r")
        if progress_bar:
            progress_bar.close()
    
    def check_and_pull_model(self):
        try:
            available_models_response = ollama.list()
            available_models = available_models_response.models
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
        """Core method for calling the model. All Ollama API calls and streaming logic reside here."""
        self.check_and_pull_model()
        self.log(f"Calling Ollama model '{self.model}' with prompt...")
        if self.streaming:
            try:
                while True:
                    print("-" * os.get_terminal_size().columns)
                    print(f"{Fore.BLUE}{self.name}{Fore.RESET} using {Fore.BLUE}{self.model}{Fore.RESET} is streaming...\n")
                    # Determine initially if we start in thinking phase based on the prompt.
                    in_thinking_phase = "## THINKING PHASE" in prompt
                    messages = [{'role': 'user', 'content': prompt}]
                    if in_thinking_phase:
                        messages.append({'role': 'assistant', 'content': '<think>'})
                    response_stream = ollama.chat(
                        model=self.model,
                        messages=messages,
                        stream=True,
                        options=getattr(self, "options", {})
                    )
                    response_text = ""
                    loop_detected = False
                    count_store = 0

                    if in_thinking_phase:
                        print(f"{Fore.MAGENTA}Thinking: {AGENT_COLORS.get('thinking_color', Fore.WHITE)}", end='', flush=True)

                    buffer = ""
                    final_output_text = ""  # Only text outside the thinking phase will be accumulated here.
                    for chunk in response_stream:
                        chunk_text = chunk.get('message', {}).get('content', '')
                        response_text += chunk_text
                        buffer += chunk_text

                        # Always print the current chunk.
                        print(chunk_text, end='', flush=True)

                        if getattr(self, "thinking_enabled", False):
                            # Check for end token: if detected, exit thinking phase.
                            for pattern in THINKING_TOKENS["end_patterns"]:
                                if re.search(pattern, buffer, re.DOTALL):
                                    if in_thinking_phase:
                                        print(f"{Fore.MAGENTA}Finished Thinking, writing:\n {Fore.WHITE}", end='', flush=True)
                                    in_thinking_phase = False
                                    break
                        
                        # If we're not in the thinking phase, accumulate chunk_text for repeat detection.
                        if not in_thinking_phase:
                            final_output_text += chunk_text
                        
                        # Perform repeat detection on final_output_text only.
                        sentences = re.split(r'(?<=[.!?])\s+', final_output_text)
                        sentences = [sentence for sentence in sentences if len(sentence) > SETTINGS.get("min_sentence_length", 10)]
                        sentence_counts = Counter(sentences)
                        repeated_sentences = [sentence for sentence, count in sentence_counts.items() if count > 1 and len(sentence) > SETTINGS.get("max_repeated_sentences", 10)]
                        if len(repeated_sentences) > count_store:
                            print(f"{Fore.RED}REPEAT{Style.RESET_ALL}")
                            count_store = len(repeated_sentences)
                        if (len(repeated_sentences) > 10 and SETTINGS.get("break_on_repeated_sentences", False)) or len(repeated_sentences) > 100:
                            print(f"{Fore.RED}Warning: Loop detected, regenerating output.{Style.RESET_ALL}")
                            loop_detected = True
                            break
                    
                    if loop_detected:
                        continue
                    else:
                        # Return final_output_text, or response_text if final_output_text is empty.
                        if final_output_text:
                            print("\n")
                            self.log(f"Received streaming response: {response_text}")
                            return final_output_text
                        else:
                            print("\n")
                            self.log(f"Received streaming response: {response_text}")
                            print(f"{Fore.RED}No post thinking writing detected, returning full response")
                            return response_text

            except Exception as e:
                self.logger.error(f"Error streaming from Ollama: {e}")
                return ""
        else:
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}],
                    options=getattr(self, "options", {})
                )
                response_text = response.get('message', {}).get('content', '')
                self.log(f"Received response: {response_text}")
                return response_text
            except Exception as e:
                self.logger.error(f"Error calling Ollama: {e}")
                return ""
    
    def estimate_tokens(self, text):
        return len(text.split())
    
    def run(self, **kwargs):
        prompt = self.generate_prompt(**kwargs)
        estimated = self.estimate_tokens(prompt)
        tqdm.write(f"{self.name} prompt estimated tokens: {estimated}")
        if self.step_by_step:
            tqdm.write(f"\n----- {self.name} Prompt -----\n{prompt}\n------------------------------")
            input("Press Enter to send this prompt...")
        return self.call_model(prompt)