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
        " - Chapter Outline: {outline}\n"
        " - Book Description: {description}\n"
        " - Character Details: {characters}\n"
        " - Global Story Summary: {global_summary}\n\n"
        "Output only the draft chapter. Format your output in clear paragraphs using Markdown if appropriate. "
        "Do not incorporate any feedback at this stage. Do not ask follow-up questions."
    ),
    "global_story_agent": (
        "You are a global story agent. Your task is to generate a broad, high-level narrative for a book. "
        "Use the provided book description and, if given, the previous global summary to craft a cohesive narrative arc. "
        "Variables:\n - Book Description: {description}\n - Previous Summary: {previous_summary}\n\n"
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
        " - Expected Chapters (if specified): {expected_chapters}\n - Chapter Length: {chapter_length}\n\n"
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
        "Output only the final chapter draft that provides a satisfying ending. Ensure that the chapter is formatted clearly, using paragraphs and, if needed, Markdown syntax."
    ),
    "revision_agent": (
        "You are a revision agent. Your task is to refine a chapter by ensuring consistency with the overall narrative and the chapter outline. "
        "Variables:\n - Draft Chapter: {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n\n"
        "Output only the revised chapter text. Improve structure and clarity, and format your revised chapter using Markdown if appropriate."
    ),
    "markdown_agent": (
        ""
        "Previous Chapter: {previous_chapter}\n\n"
        "You are a Markdown formatting agent. Your task is to reformat the provided chapter text using Markdown syntax. "
        "Ensure the output follows lightweight, structured formatting for books.\n\n"
        "### Formatting Guidelines:\n"
        "- Use `#` for the book title.\n"
        "- Use `##` for chapter titles.\n"
        "- Use `###` for sections within chapters.\n"
        "- Separate paragraphs with a blank line for readability.\n"
        "- Use `**bold**` for emphasis and `*italic*` for light emphasis.\n"
        "- Use `-` for unordered lists and numbers (`1.`) for ordered lists.\n"
        "- Use `>` for blockquotes when appropriate.\n"
        "- Insert `---` to indicate section breaks.\n\n"
        "Variables:\n - Chapter: {chapter}\n\n"
        "Output only clean Markdown-formatted text, ensuring that headings, bullet points, and paragraphs are correctly represented."
        "Do not add or remove content from the chapter."
        "Do not ask follow-up questions. Do not comment on the content or list your changes."
    ),
    "formatting_agent": (
        "You are a formatting agent. Your task is to reformat the provided book outline to ensure it contains only the headers and chapter descriptions. "
        "Remove any extraneous content and ensure each chapter starts with a heading formatted as '### **Chapter X: Chapter Title**' followed by a brief description.\n\n"
        "Variables:\n - Outline: {outline}\n\n"
        "Output only the reformatted outline with chapter titles and brief summaries for each chapter."
    )
}

CHAPTER_LENGTHS = {
    "short": 300,
    "medium": 600,
    "long": 1200,
}

SETTINGS = {
    "default_chapter_length": "medium"
}


MODELS2 = {
    "default": "llama3.1",
    "outline_agent": "Llama-3.1-Spellbound-StoryWriter-70b-instruct-0.4-16bit.i1-IQ4_XS",
    "chapter_agent": "Llama-3.1-Spellbound-StoryWriter-70b-instruct-0.4-16bit.i1-IQ4_XS",
    "feedback_agent": "llama3.1",
    "writer_agent": "L3-SMB-Grand-STORY-F32-Ultra-Quality-16_5B-NEO-V2-D_AU-Q6_K-imat13",
    "summary_agent": "llama3.1",
    "overall_summary_agent": "llama3.1",
    "character_agent": "llama3.1",
    "title_agent": "llama3.1",
    "markdown_agent": "llama3.1",
    "scene_agent": "llama3.1",
    "final_revision_agent": "Llama-3.1-Spellbound-StoryWriter-70b-instruct-0.4-16bit.i1-IQ4_XS"
}

MODELS = {
    "default": "llama3.1",
    "outline_agent": "llama3.1",
    "chapter_agent": "llama3.1",
    "feedback_agent": "llama3.1",
    "writer_agent": "llama3.1",
    "summary_agent": "llama3.1",
    "overall_summary_agent": "llama3.1",
    "character_agent": "llama3.1",
    "title_agent": "llama3.1",
    "markdown_agent": "llama3.1",
    "scene_agent": "llama3.1",
    "final_revision_agent": "llama3.1",
    "global_story_agent": "llama3.1",
    "global_outline_agent": "llama3.1",
    "final_chapter_agent": "llama3.1",
    "revision_agent": "llama3.1",
    "formatting_agent": "llama3.1"
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
}
