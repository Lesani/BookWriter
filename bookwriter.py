#!/usr/bin/env python
import argparse
import os
import json
import re
import logging
import platform
import time  # Add this import for tracking time
import shutil  # Add this import for copying files
from colorama import Fore, Style
import ebooklib
from ebooklib import epub


# Check if config.py exists, if not copy from config.sample.py
if not os.path.exists("config.py"):
    shutil.copy("config.sample.py", "config.py")

from config import PROMPTS, SETTINGS, MODELS, MODELS_FAST, DB_FILE, CHAPTER_LENGTHS, CUSTOM_OPTIONS, PLAY_SOUND
from utils import setup_logging
from agents.generic_agent import GenericAgent
from database import (
    create_project_database,
    initialize_project_schema,
    save_project,
    update_project_outline,
    save_chapter,
    update_project_status,
    get_incomplete_projects,
    get_chapter_count,
    update_project_story_details,   # new function (see database.py)
    get_project_details,            # new function (see database.py)
    retrieve_saved_chapter          # new function (see database.py)
)

# Suppress httpx logging messages
logging.getLogger("httpx").setLevel(logging.WARNING)

def sanitize_filename(output_filename, replacement="_"):
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    sanitized_filename = re.sub(invalid_chars, replacement, output_filename)
    return sanitized_filename.strip(" .")

def load_input_details_from_plot(plot_path):
    with open(plot_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    plot_dir = os.path.dirname(os.path.abspath(plot_path))
    return {
        "setting": content.get("setting", "Unknown Genre"),
        "description": content.get("description", "No description provided."),
        "style": content.get("style", "Unknown Style"),
        "chapter_length": content.get("chapter_length", "medium"),
        "expected_chapters": int(content.get("expected_chapters", 10)),
        "characters": content.get("characters", "No character details provided.")
    }, plot_dir

def prompt_for_input_details():
    print(f"{Fore.GREEN}Welcome to BookWriter!{Style.RESET_ALL}")
    setting = input("Enter the setting/genre (e.g., sci-fi, cyberpunk): ").strip()
    description = input("Enter additional book details:").strip()
    style = input("Enter the writing style (e.g., dark, humorous): ").strip()
    chapter_length = input("Enter desired chapter length (short/medium/long) [default: medium]: ").strip() or "medium"
    expected_chapters = input("Approximately how many chapters? (default 10): ").strip()
    try:
        expected_chapters = int(expected_chapters) if expected_chapters else 10
    except ValueError:
        expected_chapters = 10
    characters = input("(optional) Enter initial character details (names, traits, background): ").strip()
    return {
        "setting": setting,
        "description": description,
        "style": style,
        "chapter_length": chapter_length,
        "expected_chapters": expected_chapters,
        "characters": characters,
    }, os.getcwd()

def initialize_project(args, input_details, plot_dir, writer_instance):
    if args.resume:
        projects = get_incomplete_projects(args.db_file)
        if not projects:
            print("No incomplete projects found. Exiting.")
            exit(1)
        else:
            print(f"{Fore.CYAN}Incomplete Projects:{Style.RESET_ALL}")
            for idx, proj in enumerate(projects, start=1):
                chapter_count = get_chapter_count(args.db_file, proj["id"])
                print(f"{idx}. ID: {proj['id']}, Name: {proj['project_name']}, Chapters: {chapter_count}")
            selection = input("Enter the number of the project to resume: ").strip()
            try:
                sel = int(selection) - 1
                if sel < 0 or sel >= len(projects):
                    raise ValueError
            except ValueError:
                print("Invalid selection. Exiting resume mode.")
                exit(1)
            project = projects[sel]
            project_id = project["id"]
            saved_data = get_project_details(args.db_file, project_id)
            output_filename = saved_data.get("output_filename")
            if not output_filename:
                output_filename = os.path.join(plot_dir, "book.txt")
            return project_id, True, output_filename

    # New project case – don't create the DB entry yet.
    # Assume that the title has already been generated and stored in input_details.
    project_name = input_details["title"].strip().replace('"', '').replace("'", '')
    output_filename = os.path.join(plot_dir, f"{sanitize_filename(project_name.replace(' ', '_'))}.txt")
    return None, False, output_filename

def write_output_files(output_filename, final_book, final_markdown, summary):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    clean_book = ansi_escape.sub('', final_book)
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(summary + "\n\n" + clean_book)
        print(f"\n{Fore.CYAN}=== FINAL BOOK DRAFT SAVED TO: {output_filename} ==={Style.RESET_ALL}\n")
    except Exception as e:
        print(f"Error writing final book: {e}")

    base, _ = output_filename.rsplit('.', 1)
    md_filename = f"{base}.md"
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(summary + "\n\n" + final_markdown)
        print(f"{Fore.CYAN}=== FINAL BOOK MARKDOWN SAVED TO: {md_filename} ==={Style.RESET_ALL}")
    except Exception as e:
        print(f"Error writing final markdown: {e}")

    epub_filename = f"{base}.epub"
    try:
        book = epub.EpubBook()
        book.set_identifier('id123456')
        book.set_title('My Book')
        book.set_language('en')
        book.add_author('Author Name')

        # Add summary as the first chapter
        c1 = epub.EpubHtml(title='Summary', file_name='summary.xhtml', lang='en')
        c1.content = f"<h1>Summary</h1><p>{summary}</p>"
        book.add_item(c1)

        # Add chapters
        chapters = final_book.split('\nChapter ')
        for i, chapter in enumerate(chapters):
            if chapter.strip():
                c = epub.EpubHtml(title=f'Chapter {i+1}', file_name=f'chap_{i+1}.xhtml', lang='en')
                c.content = f"<h1>Chapter {i+1}</h1><p>{chapter}</p>"
                book.add_item(c)

        # Define Table Of Contents
        book.toc = (epub.Link('summary.xhtml', 'Summary', 'summary'),
                    (epub.Section('Chapters'), tuple(epub.Link(f'chap_{i+1}.xhtml', f'Chapter {i+1}', f'chap_{i+1}') for i in range(len(chapters)))))

        # Add default NCX and Nav files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # Create spine
        book.spine = ['nav', c1] + [book.get_item_with_id(f'chap_{i+1}') for i in range(len(chapters))]

        # Write to the file
        epub.write_epub(epub_filename, book, {})
        print(f"{Fore.CYAN}=== FINAL BOOK EPUB SAVED TO: {epub_filename} ==={Style.RESET_ALL}")
    except Exception as e:
        print(f"Error writing EPUB: {e}")

def play_chime():
    system = platform.system()
    if system == "Windows":
        try:
            import winsound
            # Play a system sound (e.g., the 'Asterisk' sound)
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except ImportError:
            print('\a')  # fallback to system beep
    elif system == "Darwin":  # macOS
        # Use the built-in 'Ping' sound
        os.system("afplay /System/Library/Sounds/Ping.aiff")
    else:  # Assume Linux
        # Try to use paplay to play a built-in sound. Path may vary by distribution.
        if os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga") != 0:
            print('\a')  # fallback to system beep

class BookWriter:
    def __init__(self, debug=False, streaming=False, step_by_step=False, fast=False):
        self.debug = debug
        self.streaming = streaming
        self.step_by_step = step_by_step
        self.logger = logging.getLogger("BookWriter")

        models = MODELS_FAST if fast else MODELS

        # Title Agent (used in project initialization)
        self.title_agent = GenericAgent(
            PROMPTS["title_agent"], "TitleAgent",
            debug=debug,
            model=models["title_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("title_agent", {})
        )

        # Characters
        self.character_agent = GenericAgent(
            PROMPTS["character_agent_deep"], "CharacterAgentDeep",
            debug=debug,
            model=models["character_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("character_agent", {})
        )

        # Character update agent
        self.character_sheet_updater_agent = GenericAgent(
            PROMPTS["character_sheet_updater_agent"], "CharacterSheetUpdaterAgent",
            debug=debug,
            model=models["character_sheet_updater_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("character_sheet_updater_agent", {})
        )

        # Global Story
        self.global_story_agent = GenericAgent(
            PROMPTS["global_story_agent"], "GlobalStoryAgent",
            debug=debug,
            model=models["global_story_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_story_agent", {})
        )

        # Global Story Feedback
        self.global_story_feedback_agent = GenericAgent(
            PROMPTS["global_story_feedback_agent"], "GlobalStoryFeedbackAgent",
            debug=debug,
            model=models["global_story_feedback_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_story_feedback_agent", {})
        )

        # Final Chapter
        self.final_chapter_agent = GenericAgent(
            PROMPTS["final_chapter_agent"], "FinalChapterAgent",
            debug=debug,
            model=models["final_chapter_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("final_chapter_agent", {})
        )

        # Outline Generation and Formatting
        self.global_outline_agent = GenericAgent(
            PROMPTS["global_outline_agent"], "GlobalOutlineAgent",
            debug=debug,
            model=models["global_outline_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_outline_agent", {})
        )
        self.global_outline_expansion_agent = GenericAgent(
            PROMPTS["global_outline_expansion_agent"], "GlobalOutlineExpansionAgent",
            debug=debug,
            model=models["global_outline_expansion_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_outline_expansion_agent", {})
        )
        self.formatting_agent = GenericAgent(
            PROMPTS["formatting_agent"], "FormattingAgent",
            debug=debug,
            model=models["formatting_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("formatting_agent", {})
        )
        self.outline_feedback_agent = GenericAgent(
            PROMPTS["outline_feedback_agent"], "OutlineFeedbackAgent",
            debug=debug,
            model=models["outline_feedback_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("outline_feedback_agent", {})
        )
        self.outline_editor_agent = GenericAgent(
            PROMPTS["outline_editor_agent"], "OutlineEditorAgent",
            debug=debug,
            model=models["outline_feedback_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("outline_feedback_agent", {})
        )
        self.pacing_check_agent = GenericAgent(
            PROMPTS["pacing_check_agent"], "PacingCheckAgent",
            debug=debug,
            model=models["outline_feedback_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("pacing_check_agent", {})
        )
        # Chapter Generation and Revision
        self.chapter_agent = GenericAgent(
            PROMPTS["chapter_agent"], "ChapterAgent",
            debug=debug,
            model=models["chapter_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("chapter_agent", {})
        )
        self.chapter_feedback_agent = GenericAgent(
            PROMPTS["chapter_feedback_agent"], "ChapterFeedbackAgent",
            debug=debug,
            model=models["chapter_feedback_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("chapter_feedback_agent", {})
        )
        self.character_consistency_agent = GenericAgent(
            PROMPTS["character_consistency_agent"], "CharacterConsistencyAgent",
            debug=debug,
            model=models["character_consistency_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("character_consistency_agent", {})
        )
        self.revision_agent = GenericAgent(
            PROMPTS["revision_agent"], "RevisionAgent",
            debug=debug,
            model=models["revision_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("revision_agent", {})
        )
        self.cleaner_agent = GenericAgent(
            PROMPTS["cleaner_agent"], "CleanerAgent",
            debug=debug,
            model=models["cleaner_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("cleaner_agent", {})
        )
        self.expansion_agent = GenericAgent(
            PROMPTS["expansion_agent"], "ExpansionAgent",
            debug=debug,
            model=models["expansion_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("expansion_agent", {})
        )

        # Markdown Formatting
        self.markdown_agent = GenericAgent(
            PROMPTS["markdown_agent"], "MarkdownAgent",
            debug=debug,
            model=models["markdown_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("markdown_agent", {})
        )

        # Summary Agent
        self.summary_agent = GenericAgent(
            PROMPTS["summary_agent"], "SummaryAgent",
            debug=debug,
            model=models["default"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("summary_agent", {})
        )

    def parse_outline(self, outline_text):
        # This regex matches headings like:
        # "### **Chapter 1:" or "#### Chapter 1", "### **Epilogue", "### **Prologue", etc.
        chapter_pattern = re.compile(
            r'^\s*#{1,3}\s*\*{0,2}\s*(Chapter\s*\d+\s*:|Epilogue\s*:|Prologue\s*:?)',
            re.IGNORECASE | re.MULTILINE
        )
        matches = list(chapter_pattern.finditer(outline_text))
        if not matches:
            # Fallback: return entire outline if no headings found
            return [outline_text.strip()]
        chapters = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(outline_text)
            chapter_text = outline_text[start:end].strip()
            if chapter_text:
                chapters.append(chapter_text)
        return chapters

    def compile_book(self, outline, chapters):
        content = f"{Fore.CYAN}Book Outline:{Style.RESET_ALL}\n{outline}\n\n"
        for idx, chapter in enumerate(chapters, 1):
            content += f"{Fore.MAGENTA}\n--- Chapter {idx} ---{Style.RESET_ALL}\n{chapter}\n"
        return content

    def compile_markdown_book(self, outline, markdown_chapters):
        md = "# Book Outline\n\n" + outline + "\n\n"
        for idx, chapter in enumerate(markdown_chapters, 1):
            md += f"\n## Chapter {idx}\n\n{chapter}\n"
        return md

    def run(self, input_details, db_file, project_id, output_filename, resume_mode=False):
        revision_iterations = SETTINGS.get("chapter_revision_iterations", 2)
        setting = input_details["setting"]
        description = input_details["description"]
        style = input_details["style"]
        themes = input_details.get("themes", "")
        plot_structure = input_details.get("plot_structure", "")
        chapter_length = input_details.get("chapter_length", "medium")
        expected_word_count = CHAPTER_LENGTHS.get(chapter_length, CHAPTER_LENGTHS["medium"])
        expected_chapters=input_details.get("expected_chapters", ""),

        if resume_mode:
            saved_data = get_project_details(db_file, project_id)
            from database import get_project_outline
            saved_outline = get_project_outline(db_file, project_id)
        else:
            saved_data = {}
            saved_outline = ""

        # Initialize other story parts (default to empty string)
        global_summary = saved_data.get("global_summary", "").strip() if resume_mode else ""
        final_chapter  = saved_data.get("final_chapter", "").strip() if resume_mode else ""
        # NEW: Retrieve saved cumulative book summary if resuming.
        book_summary = saved_data.get("book_summary", "").strip() if resume_mode else ""

        # Step: Characters
        characters = saved_data.get("characters", "").strip() if resume_mode else ""
        if not characters:
            print(f"{Fore.GREEN}Generating rich character profiles...{Style.RESET_ALL}")
            characters = self.character_agent.run(initial_characters=input_details.get("characters", ""), description=description)
            # Save characters immediately (other parts remain as-is for now)
            update_project_story_details(db_file, project_id, global_summary, final_chapter, characters)

        # Step: Global Story Concept (global_summary)
        if not global_summary:
            feedback = ""
            print(f"{Fore.GREEN}Generating global story concept...{Style.RESET_ALL}")
            global_summary = self.global_story_agent.run(setting=setting, style=style, description=description, global_summary="", characters=characters, feedback=feedback,
                    expected_chapters=expected_chapters, themes=themes, plot_structure=plot_structure)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Initial Global Story Concept:{Style.RESET_ALL}\n{global_summary}\n")
            for iteration in range(1, 2):
                feedback = self.global_story_feedback_agent.run(global_summary=global_summary,setting=setting, style=style, description=description, characters=characters, themes=themes, plot_structure=plot_structure)
                print(f"{Fore.YELLOW}Iteration {iteration}: Refining global story concept...{Style.RESET_ALL}")
                global_summary = self.global_story_agent.run(setting=setting, style=style, description=description, global_summary=global_summary, characters=characters, feedback=feedback,
                    expected_chapters=expected_chapters, themes=themes, plot_structure=plot_structure)
                if not self.streaming:
                    print(f"\n{Fore.CYAN}Refined Global Story Concept (Iteration {iteration}):{Style.RESET_ALL}\n{global_summary}\n")
            # Save updated global_summary immediately
            update_project_story_details(db_file, project_id, global_summary, final_chapter, characters)

        # Step: Final Chapter
        if not final_chapter:
            print(f"{Fore.GREEN}Drafting the final chapter to determine the ending...{Style.RESET_ALL}")
            final_chapter = self.final_chapter_agent.run(description=description, global_summary=global_summary, characters=characters, expected_word_count=expected_word_count, themes=themes, plot_structure=plot_structure)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Drafted Final Chapter:{Style.RESET_ALL}\n{final_chapter}\n")
            # Save updated final_chapter immediately
            update_project_story_details(db_file, project_id, global_summary, final_chapter, characters)

        # Step: Outline
        outline = saved_outline.strip() if resume_mode else ""
        if not outline:
            feedback = ""
            outline_revisions = SETTINGS.get("outline_feedback_iterations", 2)
            for iteration in range(1, outline_revisions + 1):
                print(f"{Fore.GREEN}Generating detailed outline linking the beginning to the final chapter... Iteration {iteration} of {outline_revisions}.{Style.RESET_ALL}")
                outline = self.global_outline_agent.run(
                    description=description,
                    global_summary=global_summary,
                    characters=characters,
                    final_chapter=final_chapter,
                    outline_feedback=feedback,
                    expected_chapters=expected_chapters,
                    chapter_length=chapter_length,
                    themes=themes,
                    plot_structure=plot_structure
                )
                
                print(f"{Fore.YELLOW}Expanding outline...{Style.RESET_ALL}")
                outline = self.global_outline_expansion_agent.run(outline=outline, description=description, global_summary=global_summary, characters=characters, final_chapter=final_chapter, themes=themes, plot_structure=plot_structure)
                
                if not self.streaming:
                    print(f"\n{Fore.CYAN}Generated Outline:{Style.RESET_ALL}\n{outline}\n")
                
                if iteration < outline_revisions:
                    # Analyze the formatted outline using the outline feedback agent.
                    print(f"{Fore.GREEN}Analyzing outline for story coherence...{Style.RESET_ALL}")
                    feedback = self.outline_feedback_agent.run(
                        outline=outline,
                        description=description,
                        global_summary=global_summary,
                        characters=characters,
                        themes=themes,
                        plot_structure=plot_structure
                    )

            # Add after the outline is generated but before user feedback
            print(f"{Fore.GREEN}Checking outline for proper pacing...{Style.RESET_ALL}")
            pacing_feedback = self.pacing_check_agent.run(outline=outline)
            if not self.streaming:
                print(f"\n{Fore.YELLOW}Pacing Analysis:{Style.RESET_ALL}\n{pacing_feedback}\n")

            # Apply pacing feedback automatically
            print(f"{Fore.YELLOW}Adjusting outline based on pacing analysis...{Style.RESET_ALL}")
            outline = self.outline_editor_agent.run(outline=outline, feedback=pacing_feedback)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Pacing-Adjusted Outline:{Style.RESET_ALL}\n{outline}\n")

            # Update the outline based on concise user feedback using the Outline Editor Agent.
            while True:
                fb = input(f"{Fore.MAGENTA}Provide feedback on the outline (or press Enter if satisfied): {Style.RESET_ALL}").strip()
                if not fb:
                    break
                print(f"{Fore.YELLOW}Updating outline based on feedback...{Style.RESET_ALL}")
                outline = self.outline_editor_agent.run(
                    outline=outline,
                    feedback=fb
                )
                if not self.streaming:
                    print(f"\n{Fore.CYAN}Updated Outline:{Style.RESET_ALL}\n{outline}\n")
                


            chapters_outline = self.parse_outline(outline)
            print(f"{Fore.GREEN}Detected {len(chapters_outline)} chapters (including any epilogue or prologue) in the outline.{Style.RESET_ALL}")
            # Confirm chapter count if not resuming (always allow user feedback)
            while True:
                correct_chapters = input(f"{Fore.MAGENTA}Is this correct? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()
                if correct_chapters in ['yes', 'y']:
                    break
                if correct_chapters in ['no', 'n']:
                    print(f"{Fore.YELLOW}Re-formatting the outline...{Style.RESET_ALL}")
                    outline = self.formatting_agent.run(outline=outline)
                    chapters_outline = self.parse_outline(outline)
                    print(f"{Fore.GREEN}Re-detected {len(chapters_outline)} chapters in the outline.{Style.RESET_ALL}")

            # For new projects, create the DB entry only after outline acceptance.
            if not resume_mode and project_id is None:
                project_id = save_project(db_file,
                                        input_details["title"].strip(),
                                        input_details["setting"],
                                        input_details["description"],
                                        input_details["style"],
                                        status="in_progress",
                                        output_filename=output_filename)

            update_project_outline(db_file, project_id, outline)

        
        chapters_outline = self.parse_outline(outline)
        final_chapters = []
        total = len(chapters_outline)
        has_epilogue = any("epilogue" in ch[:20].lower() for ch in chapters_outline)

        # Initialize cumulative summary variable.
        book_summary = ""

        # Determine how many chapters have been saved already.
        starting_chapter = get_chapter_count(db_file, project_id) if resume_mode else 0

        book = ""

        # Generate chapters.
        for idx, chapter_outline in enumerate(chapters_outline, 1):
            # If resuming and chapter already exists, retrieve it.
            if resume_mode and idx <= starting_chapter:
                print(f"{Fore.GREEN}Skipping Chapter {idx} (retrieving saved version)...{Style.RESET_ALL}")
                chapter = retrieve_saved_chapter(db_file, project_id, idx)
                final_chapters.append(chapter)
                continue

            # For the final chapter, use the drafted final chapter.
            if (has_epilogue and idx == total-1) or (not has_epilogue and idx == total):
                chapter = final_chapter
            else:
                # last 250 characters of the previous chapter
                previous_chapter_end = final_chapters[-1][-250:] if final_chapters else ""

                print(f"{Fore.GREEN}Step 5: Generating Chapter {idx} of {total}.{Style.RESET_ALL}")
                chapter = self.chapter_agent.run(
                    previous_chapter_end=previous_chapter_end,
                    outline=chapter_outline,
                    description=description,
                    characters=characters,
                    global_summary=global_summary,
                    book_summary=book_summary,
                    chapter_length=chapter_length,
                    final_chapter=final_chapter,
                    chapter_number=idx,
                    total_chapters=total,
                    expected_word_count=expected_word_count
                )

            for iteration in range(1, revision_iterations + 1):
                print(f"{Fore.YELLOW}Revising Chapter {idx}, iteration {iteration} of {revision_iterations}...{Style.RESET_ALL}")
                # Use chapter feedback agent to get critical review.
                print(f"{Fore.YELLOW}Reviewing Chapter {idx} with critical feedback...{Style.RESET_ALL}")
                feedback = "Chapter feedback:\n" + self.chapter_feedback_agent.run(
                    chapter=chapter,
                    global_summary=global_summary,
                    outline=chapter_outline,
                    book_summary=book_summary,
                    characters=characters,
                    num_chapter=idx,
                    total_chapters=total
                ) + "\n\n"
                print(f"{Fore.YELLOW}Reviewing Chapter {idx} for character consistency...{Style.RESET_ALL}")
                feedback += "Character feedback:\n" + self.character_consistency_agent.run(book=book, chapter=chapter, characters=characters, chapter_number=idx)
                # Incorporate the feedback with one additional revision.
                print(f"{Fore.YELLOW}Revising Chapter {idx} based on feedback...{Style.RESET_ALL}")
                chapter = self.revision_agent.run(chapter=chapter, global_summary=global_summary, outline=chapter_outline, feedback=feedback)
            
            # Clean the chapter after revisions to remove comments and other extraneous text.
            print(f"{Fore.YELLOW}Cleaning Chapter {idx}...{Style.RESET_ALL}")
            chapter = self.cleaner_agent.run(chapter=chapter, outline=chapter_outline, chapter_number=idx, total_chapters=total)

            chapter_word_count = len(chapter.split())
            # If the chapter is too short, expand it once.
            if chapter_word_count < expected_word_count * 0.8:
                print(f"{Fore.RED}Chapter {idx} is too short ({chapter_word_count} words, requires {expected_word_count} words).{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Expanding Chapter {idx}...{Style.RESET_ALL}")
                chapter = self.expansion_agent.run(chapter=chapter, global_summary=global_summary, outline=chapter_outline, current_length=chapter_word_count, target_length=expected_word_count)
                # Review the expanded chapter.
                print(f"{Fore.YELLOW}Reviewing Chapter {idx} with critical feedback...{Style.RESET_ALL}")
                feedback = "Chapter feedback:\n" + self.chapter_feedback_agent.run(chapter=chapter, global_summary=global_summary, outline=chapter_outline, book_summary=book_summary, characters=characters,
                    num_chapter=idx,
                    total_chapters=total) + "\n\n"
                print(f"{Fore.YELLOW}Reviewing Chapter {idx} for character consistency...{Style.RESET_ALL}")
                feedback += "Character feedback:\n" + self.character_consistency_agent.run(book=book, chapter=chapter, characters=characters, chapter_number=idx)
                # Incorporate the feedback with one additional revision.
                print(f"{Fore.CYAN}Revising after expansion:{Style.RESET_ALL}")
                chapter = self.revision_agent.run(chapter=chapter, global_summary=global_summary, outline=chapter_outline, feedback=feedback)
                # Clean the chapter after revisions to remove comments and other extraneous text.
                print(f"{Fore.CYAN}Cleaning after expansion:{Style.RESET_ALL}")
                chapter = self.cleaner_agent.run(chapter=chapter, outline=chapter_outline, chapter_number=idx, total_chapters=total)

            final_chapters.append(chapter)
            if not self.streaming:
                print(f"{Fore.MAGENTA}Chapter {idx} ({chapter_word_count} words):{Style.RESET_ALL}\n{chapter}")

            # Update cumulative book summary after each chapter.
            print(f"{Fore.YELLOW}Updating book summary...{Style.RESET_ALL}")
            book_summary = self.summary_agent.run(chapter=chapter, previous_summary=book_summary)
            if not self.streaming:
                print(f"{Fore.MAGENTA}Updated Book Summary:{Style.RESET_ALL} {book_summary}")

            # Update characters
            print(f"{Fore.YELLOW}Updating character details...{Style.RESET_ALL}")
            characters = self.character_sheet_updater_agent.run(book=book, chapter=chapter, characters=characters)
            if not self.streaming:
                print(f"{Fore.MAGENTA}Updated Characters:{Style.RESET_ALL}\n{characters}")

            book += f"\nChapter {idx}\n{chapter}\n"

            print(f"{Fore.CYAN}Committing Chapter {idx}...{Style.RESET_ALL}")
            try:
                save_chapter(db_file, project_id, idx, chapter_outline, chapter)
                update_project_story_details(db_file, project_id, global_summary, final_chapter, characters, book_summary)
            except Exception as e:
                print(f"{Fore.RED}Error saving chapter {idx}:{Style.RESET_ALL} {e}")
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(self.compile_book(outline, final_chapters))
            except Exception as e:
                print(f"{Fore.RED}Error writing partial book:{Style.RESET_ALL} {e}")

        final_book = self.compile_book(outline, final_chapters)
        final_markdown_chapters = []
        for i, ch in enumerate(final_chapters):
            previous = final_markdown_chapters[i-1] if i > 0 else ""
            formatted = self.markdown_agent.run(chapter=ch, previous_chapter=previous)
            final_markdown_chapters.append(formatted)
        markdown_book = self.compile_markdown_book(outline, final_markdown_chapters)
        return final_book, markdown_book, outline

def resume_project(args):
    projects = get_incomplete_projects(args.db_file)
    if not projects:
        print(f"{Fore.YELLOW}No incomplete projects found. Starting a new project.{Style.RESET_ALL}")
        return None, None, None, False
    print(f"{Fore.CYAN}Incomplete Projects:{Style.RESET_ALL}")
    for idx, proj in enumerate(projects, start=1):
        print(f"{idx}: {proj.get('title', 'Untitled')} (ID: {proj.get('id')})")
    while True:
        sel = input("Enter the number of the project to resume: ").strip()
        try:
            sel = int(sel) - 1
            if 0 <= sel < len(projects):
                break
            else:
                print(f"{Fore.RED}Invalid selection. Try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
    project = projects[sel]
    project_id = project["id"]
    saved_data = get_project_details(args.db_file, project_id)
    output_filename = saved_data.get("output_filename")
    # Load saved details – these should include the title and other data necessary to resume.
    input_details = {
        "title": saved_data.get("title", ""),
        "setting": saved_data.get("setting", ""),
        "description": saved_data.get("description", ""),
        "style": saved_data.get("style", ""),
        "chapter_length": saved_data.get("chapter_length", "medium"),
        "expected_chapters": saved_data.get("expected_chapters", 10),
        "characters": saved_data.get("characters", ""),
    }
    # Use the output file's directory as the plot_dir fallback.
    plot_dir = os.path.dirname(output_filename) if output_filename else os.getcwd()
    return project_id, input_details, output_filename, True

def main():
    parser = argparse.ArgumentParser(description="BookWriter: An iterative multi-agent book writing tool.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("--db-file", type=str, default=DB_FILE, help="SQLite database file.")
    parser.add_argument("--resume", action="store_true", help="Resume an existing project.")
    parser.add_argument("--stream", action="store_true", help="Stream generation output with colors.")
    parser.add_argument("--step", action="store_true", help="Enable step-by-step mode.")
    parser.add_argument("--plot", type=str, help="Path to a plot.json file with overall plot information.")
    parser.add_argument("--fast", action="store_true", help="Use fast models for generation.")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    create_project_database(args.db_file)
    initialize_project_schema(args.db_file)


    bw = BookWriter(debug=args.debug, streaming=args.stream, step_by_step=args.step, fast=args.fast)

    # Determine if we are resuming an existing project.
    resume_mode = False
    if args.resume:
        project_id, input_details, output_filename, resume_mode = resume_project(args)

    if not resume_mode:
        # No incomplete project found; fall back to new project inputs.
        if args.plot:
            input_details, plot_dir = load_input_details_from_plot(args.plot)
        else:
            input_details, plot_dir = prompt_for_input_details()
        project_id = None
        if not input_details.get("title"):
            input_details["title"] = input("(optional) Enter the book title: ").strip()
            if not input_details["title"]:
                input_details["title"] = bw.title_agent.run(description=input_details["description"])
        output_filename = os.path.join(plot_dir, f"{sanitize_filename(input_details.get('title', 'Untitled').replace(' ', '_'))}.txt")

    # For new projects, the database entry will be created later (e.g. after outline approval).
    start_time = time.time()
    final_book, final_markdown, outline = bw.run(input_details, args.db_file, project_id, output_filename, resume_mode)
    end_time = time.time()

    chapter_count = len(bw.parse_outline(final_book))
    word_count = len(final_book.split())
    book_name = os.path.basename(output_filename).rsplit('.', 1)[0]
    elapsed_time = end_time - start_time
    elapsed_hours = int(elapsed_time // 3600)
    elapsed_minutes = int((elapsed_time % 3600) // 60)
    elapsed_seconds = int(elapsed_time % 60)

    summary = (
        f"{Fore.GREEN}=== SUMMARY ==={Style.RESET_ALL}\n"
        f"{Fore.CYAN}Book Name: {book_name}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Chapters: {chapter_count}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Word Count: {word_count}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Time Taken: {elapsed_hours}h {elapsed_minutes}m {elapsed_seconds}s{Style.RESET_ALL}"
    )

    write_output_files(output_filename, final_book, final_markdown, summary)
    if project_id:
        update_project_status(args.db_file, project_id, "completed")
    print(final_book)
    print(summary)

    if PLAY_SOUND:
        play_chime()

if __name__ == "__main__":
    main()