# BookWriter

BookWriter is an iterative multi-agent book writing tool that helps you generate a complete book using various AI agents. The tool allows you to define the setting, characters, and plot, and then generates chapters, outlines, and summaries.

## Features

- Generate a high-level narrative for the book
- Create detailed character profiles
- Generate a detailed outline linking the beginning to the end
- Draft individual chapters based on the outline
- Perform iterative revisions for improved consistency
- Format text using Markdown
- Expand chapters to meet word count requirements
- Generate a title for the book
- Output the book in .txt and .md formats

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Lesani/BookWriter.git
    cd BookWriter
    ```

2. Create a Python virtual environment:

    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```sh
        source venv/bin/activate
        ```

4. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the BookWriter script:

    ```sh
    python bookwriter.py
    ```

2. Follow the prompts to enter the setting, description, chapter length, expected chapters, and character details.

3. The tool will generate the book iteratively, allowing you to provide feedback on the outline and chapters.

4. The final book draft and markdown will be saved to the specified output files.

## Command-Line Arguments

- `--debug`: Enable debug logging.
- `--db-file`: SQLite database file (default: `book_project_db.sqlite`).
- `--resume`: Resume an existing project.
- `--stream`: Stream generation output with colors.
- `--step`: Enable step-by-step mode.
- `--plot`: Path to a plot.json file with overall plot information.
- `--fast`: Use fast models for generation.

## Configuration

The configuration for the BookWriter tool is defined in the `config.py` file. This includes the prompts for various agents, model definitions, chapter lengths, and settings.

### Prompts

The `PROMPTS` dictionary contains the prompt templates for different agents. Each agent has a specific task, such as generating a title, drafting chapters, or creating a global story summary.

### Models

The `MODELS` and `MODELS_FAST` dictionaries define the models used by the agents. The `MODELS` dictionary contains the default models, while the `MODELS_FAST` dictionary contains models optimized for faster generation with '--fast' args.
The default model is "llama3.1" however much better generations can be created with bigger models.

### Chapter Lengths

The `CHAPTER_LENGTHS` dictionary defines the word count for short, medium, and long chapters.

## Ollama

BookWriter uses the [Ollama](https://ollama.com) for model interactions. Ensure you have the Ollama installed:
Install for your OS and pull the models you need.

## Using Models with Larger Contexts

For best results, use models with larger context windows. When importing such models with Ollama, create a modelfile. For example, create a file named "Modelfile" (no extension) with the following content:
Suggest 8k+ tokens for the writer, and as many as you can handle for the character consistency agent

Modelfile:
```
FROM llama3.1
PARAMETER num_ctx 64768
```

Then, import the model using:
```
ollama create -f Modelfile llama3.1-65k
```

"llama3.1-65k" in this case is the descriptive name that denotes that this instance will run with 64768 Tokens context window.
Ollama will not re-download the model if a "llama3.1" already exists.

Custom models can be imported by downloading a .gguf from huggingface.com and placing a modelfile next to it, then importing it the same way as shown above

Modelfile:
```
FROM filename.gguf
PARAMETER num_ctx 64768
```

Replace the context token amount with an appropriate amount for your model.

## Example

```sh
python bookwriter.py --stream --plot sample/sample.json
```

Models used in example generation (see config.py)
https://huggingface.co/mradermacher/Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-chkpt-200-16-bit-i1-GGUF
https://ollama.com/library/llama3.1

## License

This project is licensed under the GPL-3 License. See the [LICENSE](LICENSE) file for details.