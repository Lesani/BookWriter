# config.py

PROMPTS = {
    "title_agent": (
        "You are a title generation agent. Your task is to generate a catchy and appropriate title for the book based solely on the provided book description.\n"
        "Variable:\n"
        " - Book Description: {description}\n\n"
        "Output only the title, with no additional commentary."
    ),
    "character_agent_deep": (
        "You are an in-depth character development agent. Your task is to generate detailed and consistent character profiles "
        "based on the initial input. Variables:\n - Initial Character Descriptions: {initial_characters}\n - Book Description: {description}\n\n"
        "For each character, be explicit about these UNCHANGEABLE traits:\n"
        "- Gender/pronouns (he/him, she/her, they/them)\n"
        "- Physical appearance (height, build, distinctive features)\n"
        "- Age or age range\n"
        "- For non-human characters (AIs, robots, aliens, etc.), clearly specify their nature and presentation\n\n"
        "Format each character profile with clearly labeled sections:\n"
        "## [Character Name]\n"
        "**FIXED TRAITS:** (gender, appearance, age)\n"
        "**Background:** (history, origin)\n"
        "**Personality:** (temperament, quirks)\n"
        "**Motivations:** (goals, desires)\n"
        "**Relationships:** (connections to other characters)\n\n"
        "Output the enriched character profiles in this structured format."
    ),
    "global_story_agent": (
        "You are a global story agent. Your task is to generate a broad, high-level narrative for a book. "
        "Use the provided book description and, if given, the previous summary and feedback to craft a cohesive narrative arc. "
        "Variables:\n - Setting: {setting}\n - Style:{style}\n - Book Description: {description}\n - Previous Summary: {global_summary}\n -Feedback: {feedback}\n - Main Characters: {characters}\n - Expected Chapters: {expected_chapters}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "Output only a concise story concept that highlights the key themes and plot trajectory. "
        "Your output should use clear sentences and be formatted for readability."
        "Write the full Global Story Concept with twists and turns, character arcs, and the main plot to fit a book of the expected length."
        "Do not ask follow-up questions. Do not comment on the content or list your changes."
    ),
    "global_story_feedback_agent": (
        "You are a global story feedback agent. Your task is to provide feedback on the global story summary. "
        "Evaluate the coherence, pacing, and overall structure of the narrative. "
        "Variables:\n - Setting: {setting}\n - Style:{style}\n - Book Description: {description}\n - Global Story Summary: {global_summary}\n - Characters: {characters}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "Output only concise, actionable feedback on the global story summary. Focus on areas that need improvement or clarification."
    ),
    "final_chapter_agent": (
        "You are an ending crafting agent. Your task is to generate a compelling final chapter for the book. "
        "Variables:\n - Book Description: {description}\n - Global Story Summary: {global_summary}\n - Characters: {characters}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "Output only the final chapter draft that provides a satisfying ending. Ensure that the chapter is formatted clearly and follows the narrative arc of the book."
        "Do not include the chapter number or title in your output. Target {expected_word_count} words:"
    ),
    "global_outline_agent": (
        "You are an outline generation agent. Create a detailed outline following the classic three-act structure:\n\n"
        "Act 1 (Setup - first 25%): Introduce characters, establish the setting, and present the initial conflict.\n"
        "Act 2 (Confrontation - middle 50%): Develop obstacles, raise stakes, explore relationships, and build tension.\n"
        "Act 3 (Resolution - final 25%): Build to climax, resolve main conflicts, and provide satisfying conclusion.\n\n"
        "Format your response in Markdown with chapter headings as '### **Chapter X: Chapter Title**'\n"
        "followed by bullet lists of key events.\n\n"
        "Variables:\n - Book Description: {description}\n - Global Story Summary: {global_summary}\n - Characters: {characters}\n"
        " - Final Chapter: {final_chapter}\n - (Optional) Outline Feedback: {outline_feedback}\n"
        " - Expected Chapters: {expected_chapters}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "IMPORTANT PACING INSTRUCTIONS:\n"
        "- The first 25% of chapters should ONLY establish characters, setting, and initial conflict\n"
        "- Main plot challenges should escalate gradually across the middle chapters\n"
        "- The climax should occur in the final 25% of chapters\n"
        "- NO major confrontations or endgame scenarios in the first act\n"
        "- Allow time for character development and world exploration\n\n"
        "Ensure the outline leads to a logical conclusion. Include the title of the final chapter.\n"
        "Output only the outline with chapter titles and brief summaries for each chapter."
    ),
    "pacing_check_agent": (
        "You are a story pacing specialist. Review this outline and ensure it follows proper story structure:\n\n"
        "First 25% (Setup): Should introduce characters and setting, establish the initial problem.\n"
        "Middle 50% (Confrontation): Should develop obstacles, raise stakes, explore relationships.\n"
        "Final 25% (Resolution): Should build to climax, resolve conflicts, provide conclusion.\n\n"
        "Variables:\n - Outline: {outline}\n\n"
        "IDENTIFY PACING PROBLEMS:\n"
        "1. Flag any major confrontations or endgame scenarios that occur too early\n"
        "2. Note if character introductions feel rushed\n"
        "3. Check if world-building is given adequate space\n"
        "4. Ensure the climax is properly placed near the end\n"
        "5. Verify that tension builds gradually throughout\n\n"
        "Output specific recommendations for adjusting chapter content to fix pacing issues."
    ),
    "global_outline_expansion_agent": (
        "You are an outline expansion agent. Your task is to expand the provided outline to include more detailed chapter summaries. "
        "Variables:\n - Book Description: {description}\n\ - Global Story Summary: {global_summary}\n - Characters: {characters}\n - Final Chapter: {final_chapter}\n - Outline: {outline}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "Output only the expanded outline with more detailed chapter summaries. Maintain the existing structure and format of the outline."
        "Do not add new chapters or change the existing structure. Do not ask follow-up questions. Do not comment on the content or list your changes."
        "It is essential to provide only the outline with chapter titles and brief summaries for each chapter in EXACTLY the following format: \n"
        "### **Chapter X: [Title]**\n"
        "for machine readability.\n\n"
    ),
    "formatting_agent": (
        "You are a formatting agent. Your task is to reformat the provided book outline to ensure it contains only the headers and chapter descriptions. "
        "Ensure each chapter starts with a heading formatted as '### **Chapter X: Chapter Title**' followed by a brief description.\n\n"
        "Epilogue or Prologue must be formatted as '### **Epilogue/Prologue: (optional title)**' if present\n\n"
        "Variables:\n - Outline: {outline}\n\n"
        "Output only the reformatted outline with chapter titles and brief summaries for each chapter."
        "Do not remove story content from the outline. Do not ask follow-up questions. Do not comment on the content or list your changes."
        "Remove any additional content that is not a chapter title or description."
    ),
    "outline_feedback_agent": (
        "You are an outline feedback agent. Your task is to critically analyze the formatted book outline. "
        "Evaluate if the story arc is coherent, not rushed, and if the pacing and transitions between chapters make sense. "
        "Provide concise, actionable feedback without rewriting the outline."
        " - Book Description: {description}\n"
        " - Global Story Overview: {global_summary}\n\n"
        " - Character Details: {characters}\n"
        " - Theme: {themes}\n - Plot structure: {plot_structure}\n\n"
        "\nVariable:\n - Outline: {outline}"
    ),
    "outline_editor_agent": (
        "You are an outline editor agent. Your task is to receive a book outline and a piece of user feedback, "
        "and then concisely edit only the sections specified by the feedback. Do not rewrite the entire outline; "
        "only make minimal changes as requested. Variables:\n - Outline: {outline}\n - Feedback: {feedback}\n\n"
        "Output only the updated outline with minimal modifications."
        "Do not add new chapters or sections unless explicitly requested in the feedback."
        "Do not ask follow-up questions. Do not comment on the feedback or list your changes."
    ),
    "chapter_agent": (
        "You are a chapter drafting agent. Your task is to write an initial draft of chapter {chapter_number} of {total_chapters} based on the following variables:\n"
        " - Global Story Overview: {global_summary}\n\n"
        " - End of previous Chapter: {previous_chapter_end}\n\n"
        " - Book Description: {description}\n\n"
        " - Character Details: {characters}\n\n"
        " - What happened so far: {book_summary}\n\n"
        " - Chapter Outline: {outline}\n\n"
        " - Expected Chapter Length: {chapter_length}\n\n"
        "IMPORTANT CHARACTER CONSISTENCY RULES:\n"
        "- NEVER change a character's gender, appearance, or fundamental nature\n"
        "- For AI characters, robots, or non-humans, maintain their established presentation consistently\n"
        "- Refer to the FIXED TRAITS sections of character profiles before writing any character\n\n"
        "Output only the draft chapter. Format your output in clear paragraphs."
    ),
    "chapter_feedback_agent": (
        "You are a chapter feedback agent. Your task is to critically review the provided chapter in the context of the overall global story and outline. "
        "Evaluate key aspects including coherence, pacing, consistency, and integration with the global summary. Additionally, assess world building, "
        "character development, dialogue, narrative tone, and overall setting. Consider how effectively the chapter establishes its environment and "
        "advances the story in line with previous chapters and the global outline. "
        "Variables:\n - Characters: {characters}\n - What happened in past chapters: {book_summary}\n - Chapter ({num_chapter} of {total_chapters}): {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n\n"
        "Output only concise, actionable feedback for minimal revisions."
    ),
    "character_consistency_agent": (
        "The book so far: {book}\n\n"
        "You are a character consistency agent. Your task is to ensure that characters in the chapter are consistent with their established profiles.\n"
        "Focus on identifying critical consistency errors, especially:\n"
        "1. Gender/pronoun mismatches or changes\n"
        "2. Physical appearance discrepancies\n"
        "3. Age inconsistencies\n"
        "4. For non-human characters (AIs, robots, aliens), any changes in their nature or presentation\n\n"
        "Variables:\n - Base Character Profiles: {characters}\n - Chapter: {chapter}\n\n"
        "For each inconsistency found, provide:\n"
        "- The specific line from the chapter with the error\n"
        "- The correct information from the character profile\n"
        "- A suggested correction\n\n"
        "Limit your feedback to Chapter {chapter_number}. PRIORITIZE fixing gender/pronoun issues and nature of non-human characters.\n"
        "Be extremely strict about maintaining character consistency with FIXED TRAITS as defined in the character profiles."
    ),
    "character_sheet_updater_agent": (
        "The book so far: {book}\n\n"
        "You are a character sheet updater agent. Your task is to update the character sheets based on the provided chapter."
        "Review the chapter to identify any essential new information or developments related to the characters. "
        "Include any changes in relationships, motivations, or key events that impact the characters' profiles. "
        "For each character add an event memory section if not already present."
        "Add Memories such as who they met and what they did in the chapter as a concise summary."
        "Variables:\n - Characters: {characters}\n - Chapter: {chapter}\n\n"
        "Write the full character profiles with the updated information. Include any new details or changes to the characters' profiles or memories."
        "Summarize their interactions, decisions, and any significant events from the chapter."
        "Do not ask follow-up questions. Do not comment on the content or list your changes."
    ),
    "revision_agent": (
        "You are a revision agent. Your task is to refine a chapter by ensuring consistency with the overall narrative and the chapter outline. "
        "Variables:\n - Draft Chapter: {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n - Feedback: {feedback}\n\n"
        "Look at the paragraph structure, character consistency, and overall coherence of the chapter. Expand paragraphs if necessary to improve clarity and detail."
        "Output only the revised chapter text. Improve structure and clarity."
        "Do not add follow-up questions or comments. Do not list your changes."
        "Just write the revised chapter as clean printable text."
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
    ),
    "expansion_agent": (
        "You are an expansion agent. Your task is to expand the provided chapter text without altering its structure. "
        "Ensure that the expanded text maintains the original flow and coherence of the chapter.\n\n"
        "Current length: {current_length}, target length: {target_length}\n\n"
        "Variables:\n - Chapter: {chapter}\n - Global Story Summary: {global_summary}\n - Chapter Outline: {outline}\n\n"
        "Output only the expanded chapter text. Do not add new plot points or characters, just elaborate on the existing content, adding a deeper level of detail to each paragraph."
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
    "summary_agent": (
        "You are a book summary agent. Take the existing book summary and update it with the crucial facts and events from the current chapter to inform future chapters.\n"
        "Be concise and focus on the key elements that will impact the story's progression only.\n\n"
        "Variables:\n - Chapter: {chapter}\n - (Optional) Previous Summary: {previous_summary}\n\n"
        "Output only the updated summary, including only the crucial facts and events."
    )
}

CHAPTER_LENGTHS = {
    "short": 300,
    "medium": 600,
    "long": 900,
}

SETTINGS = {
    "default_chapter_length": "medium",
    "chapter_revision_iterations": 1,  # Number of times each chapter is revised
    "outline_feedback_iterations": 2,  # Number of times the outline is revised
    "break_on_repeated_sentences": True,  # Break the generation process if repeated sentences are detected (runaway LLM)
    "max_repeated_sentences": 10  # Maximum number of repeated sentences before breaking the generation
}

# Models for each agent, slow configuration for better quality
MODELS = {
    "default": "llama3.1-65k",  # Default model for general tasks
    "outline_agent": "llama3.1-65k",  # Generates a detailed outline for the book
    "chapter_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Drafts individual chapters based on the outline
    "character_agent": "llama3.1-65k",  # Develops detailed character profiles
    "title_agent": "llama3.1-65k",  # Generates a title for the book
    "markdown_agent": "llama3.1-65k",  # Formats text using Markdown
    "global_story_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Generates a high-level narrative for the book
    "global_story_feedback_agent": "llama3.1-65k",  # Provides feedback on the global story summary
    "global_outline_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Creates a detailed outline linking the beginning to the end
    "final_chapter_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Crafts the final chapter of the book
    "revision_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Refines chapters for consistency and clarity
    "formatting_agent": "llama3.1-65k",  # Reformats the outline to ensure proper structure
    "expansion_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # Expands chapters to meet word count requirements
    "cleaner_agent": "llama3.1-65k",  # Cleans chapters by removing extraneous content
    "outline_feedback_agent": "llama3.1-65k",  # New model for outline feedback agent
    "outline_editor_agent": "llama3.1-65k",  # New model for outline editor agent
    "chapter_feedback_agent": "llama3.1-65k",  # New model for chapter feedback agent
    "character_consistency_agent": "llama3.1-131072",  # New model for character consistency agent
    "character_sheet_updater_agent": "llama3.1-65k",  # New model for character sheet updater agent
    "global_outline_expansion_agent": "DSR1-Distill-Qwen-32B-Story.i1-Q4_0-16192",  # New model for global outline expansion agent
    "pacing_check_agent": "llama3.1-65k"  # New model for pacing check agent
}

# Models for each agent, slow configuration for better quality
MODELS2 = {
    "default": "llama3.1-65k",  # Default model for general tasks
    "outline_agent": "llama3.1-65k",  # Generates a detailed outline for the book
    "chapter_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Drafts individual chapters based on the outline
    "character_agent": "llama3.1-65k",  # Develops detailed character profiles
    "title_agent": "llama3.1-65k",  # Generates a title for the book
    "markdown_agent": "llama3.1-65k",  # Formats text using Markdown
    "global_story_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Generates a high-level narrative for the book
    "global_story_feedback_agent": "llama3.1-65k",  # Provides feedback on the global story summary
    "global_outline_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Creates a detailed outline linking the beginning to the end
    "final_chapter_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Crafts the final chapter of the book
    "revision_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Refines chapters for consistency and clarity
    "formatting_agent": "llama3.1-65k",  # Reformats the outline to ensure proper structure
    "expansion_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # Expands chapters to meet word count requirements
    "cleaner_agent": "llama3.1-65k",  # Cleans chapters by removing extraneous content
    "outline_feedback_agent": "llama3.1-65k",  # New model for outline feedback agent
    "outline_editor_agent": "llama3.1-65k",  # New model for outline editor agent
    "chapter_feedback_agent": "llama3.1-65k",  # New model for chapter feedback agent
    "character_consistency_agent": "llama3.1-131072",  # New model for character consistency agent
    "character_sheet_updater_agent": "llama3.1-65k",  # New model for character sheet updater agent
    "global_outline_expansion_agent": "Mistral-Small-Spellbound-StoryWriter-22B-instruct-0.2-16192",  # New model for global outline expansion agent
    "pacing_check_agent": "llama3.2-65k"  # New model for pacing check agent
}

# Fast configuration for quicker responses/iteration
MODELS_FAST = {
    "default": "llama3.2-65k",  # Default model for general tasks
    "outline_agent": "llama3.2-65k",  # Generates a detailed outline for the book
    "chapter_agent": "llama3.2-65k",  # Drafts individual chapters based on the outline
    "character_agent": "llama3.2-65k",  # Develops detailed character profiles
    "title_agent": "llama3.2-65k",  # Generates a title for the book
    "markdown_agent": "llama3.2-65k",  # Formats text using Markdown
    "global_story_agent": "llama3.2-65k",  # Generates a high-level narrative for the book
    "global_story_feedback_agent": "llama3.2-65k",  # Provides feedback on the global story summary
    "global_outline_agent": "llama3.2-65k",  # Creates a detailed outline linking the beginning to the end
    "final_chapter_agent": "llama3.2-65k",  # Crafts the final chapter of the book
    "revision_agent": "llama3.2-65k",  # Refines chapters for consistency and clarity
    "formatting_agent": "llama3.2-65k",  # Reformats the outline to ensure proper structure
    "expansion_agent": "llama3.2-65k",  # Expands chapters to meet word count requirements
    "cleaner_agent": "llama3.2-65k",  # Cleans chapters by removing extraneous content
    "outline_feedback_agent": "llama3.2-65k",  # New model for outline feedback agent in fast mode
    "outline_editor_agent": "llama3.2-65k",  # New model for outline editor agent in fast mode
    "chapter_feedback_agent": "llama3.2-65k",  # New model for chapter feedback agent in fast mode
    "character_consistency_agent": "llama3.2-65k",  # New model for character consistency agent in fast mode
    "character_sheet_updater_agent": "llama3.2-65k",  # New model for character sheet updater agent in fast mode
    "global_outline_expansion_agent": "llama3.2-65k",  # New model for global outline expansion agent in fast mode
    "pacing_check_agent": "llama3.2-65k"  # New model for pacing check agent
}


# Define custom model options for each agent (used for deviation from default settings)
#     "temperature": 0.8,       # Controls randomness; lower values make output more deterministic
#     "num_ctx": 2048,          # Sets the context window size
#     "repeat_penalty": 1.2     # Penalizes repeated tokens; values >1.0 discourage repetition

CUSTOM_OPTIONS = {
    "global_story_agent": {},
    "character_agent": {},
    "global_outline_agent": {},
    "final_chapter_agent": {},
    "chapter_agent": {
        "num_predict": 8192,
        "temperature": 0.5
    },
    "revision_agent": {},
    "markdown_agent": {},
    "title_agent": {},
    "formatting_agent": {},
    "expansion_agent": {},
    "cleaner_agent": {},
    "outline_feedback_agent": {},  # New custom options for outline feedback agent
    "outline_editor_agent": {},  # New custom options for outline editor agent
    "chapter_feedback_agent": {},  # New custom options for chapter feedback agent
    "character_consistency_agent": {},  # New custom options for character consistency agent
    "character_sheet_updater_agent": {},  # New custom options for character sheet updater agent
    "pacing_check_agent": {}  # New custom options for pacing check agent
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
    "OutlineFeedbackAgent": Fore.LIGHTCYAN_EX,  # New color for outline feedback agent
    "OutlineEditorAgent": Fore.LIGHTCYAN_EX,  # New color for outline editor agent
    "ChapterFeedbackAgent": Fore.LIGHTCYAN_EX,  # New color for chapter feedback agent
    "CharacterConsistencyAgent": Fore.LIGHTCYAN_EX,  # New color for character consistency agent
    "CharacterSheetUpdaterAgent": Fore.LIGHTCYAN_EX  # New color for character sheet updater agent
}

# Set to True to enable sound notification at the end of the generation process
PLAY_SOUND = False