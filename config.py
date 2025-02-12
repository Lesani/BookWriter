# config.py

PROMPTS = {
    # Title Agent remains unchanged.
    "title_agent": (
        "You are a title generation agent. Your task is to generate a catchy and appropriate title for the book based solely on the provided book description.\n"
        "Variable:\n"
        " - Book Description: {description}\n\n"
        "Output only the title, with no additional commentary."
    ),
    "chapter_agent": (
        " - Previous Chapter: {previous_chapter}\n\n"
        "You are a chapter drafting agent. Your task is to write an initial draft of chapter {chapter_number} of {total_chapters} strictly based on the following variables:\n"
        " - Book Description: {description}\n"
        " - Character Details: {characters}\n"
        " - Global Story Summary: {global_summary}\n\n"
        " - Chapter Outline: {outline}\n"
        " - Expected Chapter Length: {chapter_length}\n\n"
        "Use long paragraphs to maintain the flow of the chapter.\n"
        "Output only the draft chapter. Format your output in clear paragraphs. Do not include any additional comments or questions."
        "Do not incorporate any feedback at this stage. Do not ask follow-up questions."
        "Only draft the chapter content based on the provided information, do not add additional chapters or change the existing structure."
        "Chapter {chapter_number}:"
    ),
    "global_story_agent": (
        "You are a global story agent. Your task is to generate a broad, high-level narrative for a book. "
        "Use the provided book description and, if given, the previous global summary to craft a cohesive narrative arc. "
        "Variables:\n - Book Description: {description}\n - Previous Summary: {previous_summary}\n - Main Characters: {characters}\n\n"
        "Output only a concise story concept that highlights the key themes and plot trajectory. "
        "Your output should use clear sentences and be formatted for readability."
    ),
    "character_agent_deep": (
        "You are an in-depth character development agent. Your task is to generate detailed and consistent character profiles "
        "based on the initial input. Variables:\n - Initial Character Descriptions: {initial_characters}\n - Book Description: {description}\n\n"
        "Output the enriched character profiles in a concise format. Use bullet points or short paragraphs if necessary."
    ),
    "global_outline_agent": (
        "You are an outline generation agent. Your task is to create a detailed outline for the book that connects the beginning to a predetermined ending. "
        "Format your response in Markdown following these instructions:\n"
        "  - Each chapter in the outline must start with a heading formatted as '### **Chapter X: Chapter Title**'.\n"
        "  - Follow each chapter heading with a bullet list of key events or summary points for that chapter.\n\n"
        "Variables:\n - Book Description: {description}\n - Global Story Summary: {global_summary}\n - Characters: {characters}\n"
        " - Final Chapter: {final_chapter}\n - (Optional) Outline Feedback: {outline_feedback}\n"
        " - Expected Chapters: {expected_chapters}\n"
        "Ensure that the outline leads to a logical conclusion towards the final chapter. Include the title of the final chapter in the outline. An epilogue can optionally be added after the final chapter if it fits the story."
        "Output only the outline with chapter titles and brief summaries for each chapter in EXACTLY the following format: \n"
        "### **Chapter X: [Title]**\n"
        "for machine readability.\n\n"
        "Sample outline for formatting:\n\n"
        "### **Chapter 1: Introduction**\n"
        "- Introduce the protagonist and their main goal.\n"
        "- Set the scene and establish the main conflict.\n\n"
        "### **Chapter 2: Rising Action**\n"
        "- Protagonist encounters the first obstacle.\n"
        "- Introduce a key supporting character.\n\n"
        "### **Chapter 3: Conflict Deepens**\n"
        "- Protagonist faces a major setback.\n"
        "- Supporting character provides crucial help.\n\n"
    ),
    "final_chapter_agent": (
        "You are an ending crafting agent. Your task is to generate a compelling final chapter for the book. "
        "Variables:\n - Book Description: {description}\n - Global Story Summary: {global_summary}\n - Characters: {characters}\n\n"
        "Output only the final chapter draft that provides a satisfying ending. Ensure that the chapter is formatted clearly and follows the narrative arc of the book."
        "Do not include the chapter number or title in your output."
    ),
    "revision_agent": (
        "You are a revision agent. Your task is to refine a chapter by ensuring consistency with the overall narrative and the chapter outline. "
        "Variables:\n - Draft Chapter: {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n\n"
        "Look at the paragraph structure, character consistency, and overall coherence of the chapter. Expand paragraphs if necessary to improve clarity and detail."
        "Output only the revised chapter text. Improve structure and clarity, and format your revised chapter as clean printable text."
        "Do not add follow-up questions or comments. Do not list your changes."
    ),
    "markdown_agent": (
        "Previous Chapter: {previous_chapter}\n\n"
        "You are a Markdown formatting agent. Your task is to lightly reformat the provided chapter text using Markdown syntax. "
        "Ensure the output follows lightweight, structured formatting for printed books.\n\n"
        "Variables:\n - Chapter: {chapter}\n\n"
        "### Formatting Guidelines:\n"
        "- Use `#` for the book title. if present\n"
        "- Use `##` for chapter title.\n"
        "- Use `**bold**` for emphasis.\n"
        "- Use `*italic*` for thoughts.\n"
        "Remove any other formatting\n\n"
        "Output only clean formatted text."
        "Do not add or remove content from the chapter."
        "Do not ask follow-up questions. Do not comment on the content or list your changes."
    ),
    "formatting_agent": (
        "You are a formatting agent. Your task is to reformat the provided book outline to ensure it contains only the headers and chapter descriptions. "
        "Remove any extraneous content and ensure each chapter starts with a heading formatted as '### **Chapter X: Chapter Title**' followed by a brief description.\n\n"
        "Variables:\n - Outline: {outline}\n\n"
        "Output only the reformatted outline with chapter titles and brief summaries for each chapter."
    ),
    "expansion_agent": (
        "You are an expansion agent. Your task is to expand the provided chapter text without altering its structure. "
        "Ensure that the expanded text maintains the original flow and coherence of the chapter.\n\n"
        "Current length: {current_length}, target length: {target_length}\n\n"
        "Variables:\n - Chapter: {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n\n"
        "Output only the expanded chapter text. Do not add new plot points or characters, just elaborate on the existing content, adding a deeper level of detail to each paragraph."
    ),
    "cleaner_agent": (
        "{outline}"
        "You are a cleaner agent. Your task is to clean the provided chapter text by removing any extraneous comments, debugging information, or other non-chapter content. "
        "Ensure that the cleaned text maintains the original flow and coherence of the chapter.\n\n"
        "Chapter number {chapter_number} of {total_chapters}\n\n"
        "Variables:\n - Chapter Text: {chapter}\n\n"
        "Output only the cleaned chapter text. Do not add new content or alter the structure of the chapter."
        "Correct or add the Chapter number and title if missing in the text or 'Prologue' or 'Epilogue'."
        "Do not ask follow-up questions. Do not comment on the content or list your changes."
    )
}

CHAPTER_LENGTHS = {
    "short": 300,
    "medium": 600,
    "long": 900,
}

SETTINGS = {
    "default_chapter_length": "medium",
    "revision_iterations": 1  # Number of times each chapter is revised
}

# Models for each agent, slow configuration for better quality
MODELS = {
    "default": "llama3.1-65k",  # Default model for general tasks
    "outline_agent": "llama3.1-65k",  # Generates a detailed outline for the book
    "chapter_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Drafts individual chapters based on the outline
    "character_agent": "llama3.1-65k",  # Develops detailed character profiles
    "title_agent": "llama3.1-65k",  # Generates a title for the book
    "markdown_agent": "llama3.1-65k",  # Formats text using Markdown
    "final_revision_agent": "llama3.1-65k",  # Performs final revisions on the text
    "global_story_agent": "llama3.1-65k",  # Generates a high-level narrative for the book
    "global_outline_agent": "llama3.1-65k",  # Creates a detailed outline linking the beginning to the end
    "final_chapter_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Crafts the final chapter of the book
    "revision_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Refines chapters for consistency and clarity
    "formatting_agent": "llama3.1-65k",  # Reformats the outline to ensure proper structure
    "expansion_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Expands chapters to meet word count requirements
    "cleaner_agent": "llama3.1-65k"  # Cleans chapters by removing extraneous content
}

# Fast configuration for quicker responses/iteration
MODELS_FAST = {
    "default": "llama3.2-65k",  # Default model for general tasks
    "outline_agent": "llama3.2-65k",  # Generates a detailed outline for the book
    "chapter_agent": "llama3.2-65k",  # Drafts individual chapters based on the outline
    "character_agent": "llama3.2-65k",  # Develops detailed character profiles
    "title_agent": "llama3.2-65k",  # Generates a title for the book
    "markdown_agent": "llama3.2-65k",  # Formats text using Markdown
    "final_revision_agent": "llama3.2-65k",  # Performs final revisions on the text
    "global_story_agent": "llama3.2-65k",  # Generates a high-level narrative for the book
    "global_outline_agent": "llama3.2-65k",  # Creates a detailed outline linking the beginning to the end
    "final_chapter_agent": "llama3.2-65k",  # Crafts the final chapter of the book
    "revision_agent": "llama3.2-65k",  # Refines chapters for consistency and clarity
    "formatting_agent": "llama3.2-65k",  # Reformats the outline to ensure proper structure
    "expansion_agent": "llama3.2-65k",  # Expands chapters to meet word count requirements
    "cleaner_agent": "llama3.2-65k"  # Cleans chapters by removing extraneous content
}


# Define custom model options for each agent (used for deviation from default settings)
#     "temperature": 0.7,       # Controls randomness; lower values make output more deterministic
#     "num_ctx": 2048,          # Sets the context window size
#     "repeat_penalty": 1.2     # Penalizes repeated tokens; values >1.0 discourage repetition

CUSTOM_OPTIONS = {
    "global_story_agent": {},
    "character_agent": {},
    "global_outline_agent": {},
    "final_chapter_agent": {},
    "chapter_agent": {},
    "revision_agent": {},
    "markdown_agent": {},
    "title_agent": {},
    "formatting_agent": {},
    "expansion_agent": {},
    "cleaner_agent": {},
}

DB_FILE = "book_project_db.sqlite"

from colorama import Fore
AGENT_COLORS = {
    "OutlineAgent": Fore.BLUE,
    "ChapterAgent": Fore.MAGENTA,
    "FeedbackAgent-coherence": Fore.CYAN,
    "FeedbackAgent-length": Fore.CYAN,
    "FeedbackAgent-characters": Fore.CYAN,
    "FeedbackAgent-flow": Fore.CYAN,
    "WriterAgent": Fore.GREEN,
    "SummaryAgent": Fore.YELLOW,
    "OverallSummaryAgent": Fore.LIGHTBLUE_EX,
    "CharacterAgent": Fore.RED,
    "TitleAgent": Fore.LIGHTGREEN_EX,
    "MarkdownAgent": Fore.LIGHTMAGENTA_EX,
    "FinalRevisionAgent": Fore.LIGHTBLUE_EX,
    "FormattingAgent": Fore.LIGHTCYAN_EX,
    "ExpansionAgent": Fore.LIGHTCYAN_EX,
    "CleanerAgent": Fore.LIGHTCYAN_EX,
}
