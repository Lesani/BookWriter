#!/usr/bin/env python
import argparse
import os
import json
import re
import logging
import time  # Add this import for tracking time
import shutil  # Add this import for copying files
from colorama import Fore, Style

# Check if config.py exists, if not copy from config.sample.py
if not os.path.exists("config.py"):
    shutil.copy("config.sample.py", "config.py")

from config import PROMPTS, SETTINGS, MODELS, MODELS_FAST, DB_FILE, CHAPTER_LENGTHS, CUSTOM_OPTIONS
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
    get_chapter_count
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
        "chapter_length": content.get("chapter_length", "medium"),
        "expected_chapters": int(content.get("expected_chapters", 10)),
        "characters": content.get("characters", "No character details provided.")
    }, plot_dir

def prompt_for_input_details():
    print(f"{Fore.GREEN}Welcome to BookWriter!{Style.RESET_ALL}")
    setting = input("Enter the setting/genre (e.g., sci-fi, cyberpunk): ").strip()
    description = input("Enter additional book details: ").strip()
    chapter_length = input("Enter desired chapter length (short/medium/long) [default: medium]: ").strip() or "medium"
    expected_chapters = input("Approximately how many chapters? (default 10): ").strip()
    try:
        expected_chapters = int(expected_chapters) if expected_chapters else 10
    except ValueError:
        expected_chapters = 10
    characters = input("Enter initial character details (names, traits, background): ").strip()
    return {
        "setting": setting,
        "description": description,
        "chapter_length": chapter_length,
        "expected_chapters": expected_chapters,
        "characters": characters,
    }, os.getcwd()

def initialize_project(args, input_details, plot_dir, writer_instance):
    if args.resume:
        projects = get_incomplete_projects(args.db_file)
        if not projects:
            print("No incomplete projects found. Starting a new project.")
            args.resume = False
        else:
            project = projects[0]
            project_id = project["id"]
            existing_outline = project.get("outline")
            output_filename = project.get("output_filename", os.path.join(plot_dir, "book.txt"))
            return project_id, existing_outline, output_filename
    # Generate a title and save project.
    title = writer_instance.title_agent.run(description=input_details["description"])
    project_name = title.strip().replace('"', '').replace("'", '')
    output_filename = os.path.join(plot_dir, f"{sanitize_filename(project_name.replace(' ', '_'))}.txt")
    project_id = save_project(args.db_file, project_name,
                              input_details["setting"],
                              input_details["description"],
                              status="in_progress")
    return project_id, None, output_filename

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

class BookWriter:
    def __init__(self, debug=False, streaming=False, step_by_step=False, fast=False):
        self.debug = debug
        self.streaming = streaming
        self.step_by_step = step_by_step
        self.logger = logging.getLogger("BookWriter")

        models = MODELS_FAST if fast else MODELS

        # New workflow agents using custom options:
        self.global_story_agent = GenericAgent(
            PROMPTS["global_story_agent"], "GlobalStoryAgent",
            debug=debug,
            model=models["global_story_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_story_agent", {})
        )
        self.character_agent = GenericAgent(
            PROMPTS["character_agent_deep"], "CharacterAgentDeep",
            debug=debug,
            model=models["character_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("character_agent", {})
        )
        self.global_outline_agent = GenericAgent(
            PROMPTS["global_outline_agent"], "GlobalOutlineAgent",
            debug=debug,
            model=models["global_outline_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("global_outline_agent", {})
        )
        self.final_chapter_agent = GenericAgent(
            PROMPTS["final_chapter_agent"], "FinalChapterAgent",
            debug=debug,
            model=models["final_chapter_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("final_chapter_agent", {})
        )
        self.chapter_agent = GenericAgent(
            PROMPTS["chapter_agent"], "ChapterAgent",
            debug=debug,
            model=models["chapter_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("chapter_agent", {})
        )
        self.revision_agent = GenericAgent(
            PROMPTS["revision_agent"], "RevisionAgent",
            debug=debug,
            model=models["revision_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("revision_agent", {})
        )
        self.markdown_agent = GenericAgent(
            PROMPTS["markdown_agent"], "MarkdownAgent",
            debug=debug,
            model=models["markdown_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("markdown_agent", {})
        )
        self.title_agent = GenericAgent(
            PROMPTS["title_agent"], "TitleAgent",
            debug=debug,
            model=models["title_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("title_agent", {})
        )
        self.formatting_agent = GenericAgent(
            PROMPTS["formatting_agent"], "FormattingAgent",
            debug=debug,
            model=models["formatting_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("formatting_agent", {})
        )
        self.expansion_agent = GenericAgent(
            PROMPTS["expansion_agent"], "ExpansionAgent",
            debug=debug,
            model=models["expansion_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("expansion_agent", {})
        )
        self.cleaner_agent = GenericAgent(
            PROMPTS["cleaner_agent"], "CleanerAgent",
            debug=debug,
            model=models["cleaner_agent"],
            streaming=streaming,
            step_by_step=step_by_step,
            options=CUSTOM_OPTIONS.get("cleaner_agent", {})
        )

    def parse_outline(self, outline_text):
        # This regex matches headings like:
        # "### **Chapter 1:" or "#### Chapter 1", "### **Epilogue", "### **Prologue", etc.
        chapter_pattern = re.compile(
            r'^\s*#{3,}\s*\*{0,2}\s*(Chapter\s*\d+\s*:|Epilogue\s*:|Prologue\s*:?)',
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

    def run(self, input_details, db_file, project_id, output_filename, existing_outline=None):
        description = input_details["description"]
        chapter_length = input_details.get("chapter_length", "medium")
        expected_word_count = CHAPTER_LENGTHS.get(chapter_length, CHAPTER_LENGTHS["medium"])

        # Step 1: Build overall story via iterative refinement.
        print(f"{Fore.GREEN}Step 1: Building overall story concept...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Iteration 0: Generating initial global story concept...{Style.RESET_ALL}")
        characters=input_details.get("characters", "")
        global_summary = self.global_story_agent.run(description=description, previous_summary="",characters=characters)
        if not self.streaming:
            print(f"\n{Fore.CYAN}Initial Global Story Concept:{Style.RESET_ALL}\n{global_summary}\n")
        for iteration in range(1, 2):
            print(f"{Fore.YELLOW}Iteration {iteration}: Refining global story concept...{Style.RESET_ALL}")
            global_summary = self.global_story_agent.run(description=description, previous_summary=global_summary, characters=characters)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Refined Global Story Concept (Iteration {iteration}):{Style.RESET_ALL}\n{global_summary}\n")

        # Step 2: Generate rich character profiles.
        print(f"{Fore.GREEN}Step 2: Generating rich character profiles...{Style.RESET_ALL}")
        characters = self.character_agent.run(initial_characters=input_details.get("characters", ""),
                                               description=description)
        if not self.streaming:
            print(f"\n{Fore.CYAN}Defined Characters:{Style.RESET_ALL}\n{characters}\n")
        
        # Step 1b: Revise the global story concept based on character profiles.
        print(f"{Fore.YELLOW}Revising global story concept based on character profiles...{Style.RESET_ALL}")
        global_summary = self.global_story_agent.run(description=description, previous_summary=global_summary, characters=characters)
        if not self.streaming:
            print(f"\n{Fore.CYAN}Revised Global Story Concept:{Style.RESET_ALL}\n{global_summary}\n")
        for iteration in range(3, 5):
            print(f"{Fore.YELLOW}Iteration {iteration}: Refining global story concept...{Style.RESET_ALL}")
            global_summary = self.global_story_agent.run(description=description, previous_summary=global_summary, characters=characters)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Refined Global Story Concept (Iteration {iteration}):{Style.RESET_ALL}\n{global_summary}\n")

        # Step 3: Draft the final chapter first to determine the desired ending.
        print(f"{Fore.GREEN}Step 3: Drafting the final chapter to determine the ending...{Style.RESET_ALL}")
        final_chapter = self.final_chapter_agent.run(description=description,
                                                     global_summary=global_summary,
                                                     characters=characters)
        if not self.streaming:
            print(f"\n{Fore.CYAN}Drafted Final Chapter:{Style.RESET_ALL}\n{final_chapter}\n")

        # Step 4: Generate a detailed outline linking the beginning to the final chapter.
        print(f"{Fore.GREEN}Step 4: Generating detailed outline linking the beginning to the final chapter...{Style.RESET_ALL}")
        outline = self.global_outline_agent.run(
            description=description,
            global_summary=global_summary,
            characters=characters,
            final_chapter=final_chapter,
            outline_feedback="",
            expected_chapters=input_details.get("expected_chapters", ""),
            chapter_length=input_details.get("chapter_length", "")
        )
        if not self.streaming:
            print(f"\n{Fore.CYAN}Generated Outline:{Style.RESET_ALL}\n{outline}\n")

        # Allow for feedback on the outline before proceeding.
        while True:
            fb = input(f"{Fore.MAGENTA}Provide feedback on the outline (or press Enter if satisfied): {Style.RESET_ALL}").strip()
            if not fb:
                break
            print(f"{Fore.YELLOW}Updating outline based on feedback...{Style.RESET_ALL}")
            outline = self.global_outline_agent.run(
                description=description,
                global_summary=global_summary,
                characters=characters,
                final_chapter=final_chapter,
                outline_feedback=fb,
                expected_chapters=input_details.get("expected_chapters", ""),
                chapter_length=input_details.get("chapter_length", "")
            )
            update_project_outline(db_file, project_id, outline)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Updated Outline:{Style.RESET_ALL}\n{outline}\n")

        # Reformat the outline once before detecting chapters
        print(f"{Fore.YELLOW}Re-formatting the outline to remove any extraneous text...{Style.RESET_ALL}")
        outline = self.formatting_agent.run(outline=outline)

        # Detect chapter amount and ask for user confirmation
        chapters_outline = self.parse_outline(outline)
        print(f"{Fore.GREEN}Detected {len(chapters_outline)} chapters (including any epilogue or prologue if present) in the outline.{Style.RESET_ALL}")
        while True:
            correct_chapters = input(f"{Fore.MAGENTA}Is this correct? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()
            if correct_chapters in ['yes', 'y', 'no', 'n']:
                break
            print(f"{Fore.RED}Please enter 'yes', 'y', 'no', or 'n'.{Style.RESET_ALL}")
        if correct_chapters in ['no', 'n']:
            print(f"{Fore.YELLOW}Re-formatting the outline...{Style.RESET_ALL}")
            outline = self.formatting_agent.run(outline=outline)
            chapters_outline = self.parse_outline(outline)
            print(f"{Fore.GREEN}Re-detected {len(chapters_outline)} chapters in the outline.{Style.RESET_ALL}")

        final_chapters = []
        total = len(chapters_outline)
        has_epilogue = any("epilogue" in ch[:20].lower() for ch in chapters_outline)

        # Generate chapters for all chapters.
        for idx, chapter_outline in enumerate(chapters_outline, 1):
            chapter = None
            # Check if this is the final chapter and replace with the drafted final chapter.
            if (has_epilogue and idx == total-1) or (not has_epilogue and idx == total):
                chapter=final_chapter

            # Generate chapter if not already drafted.
            if (chapter is None):
                print(f"{Fore.GREEN}Step 5: Generating Chapter {idx} of {total}.{Style.RESET_ALL}")
                chapter = self.chapter_agent.run(
                    previous_chapter=final_chapters[-1] if final_chapters else "No previous chapter.",
                    outline=chapter_outline,
                    description=description,
                    characters=characters,
                    global_summary=global_summary,
                    chapter_length=chapter_length,
                    final_chapter=final_chapter,
                    chapter_number=idx,
                    total_chapters=total
                )
            # Retrieve configurable number of revision iterations from config
            revision_iterations = SETTINGS.get("revision_iterations", 2)
            for iteration in range(1, revision_iterations + 1):
                print(f"{Fore.YELLOW}Revising Chapter {idx}, iteration {iteration} of {revision_iterations}...{Style.RESET_ALL}")
                chapter = self.revision_agent.run(chapter=chapter,
                                                  global_summary=global_summary,
                                                  outline=chapter_outline)
            # Clean the chapter
            print(f"{Fore.YELLOW}Cleaning Chapter {idx}...{Style.RESET_ALL}")
            chapter = self.cleaner_agent.run(chapter=chapter, outline=chapter_outline, chapter_number=idx, total_chapters=total)

            # Check word count and expand if necessary
            chapter_word_count = len(chapter.split())
            if chapter_word_count < expected_word_count * 0.8:
                print(f"{Fore.RED}Chapter {idx} is too short ({chapter_word_count} words, requires {expected_word_count} words).{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Expanding Chapter {idx} to meet word count requirements...{Style.RESET_ALL}")
                chapter = self.expansion_agent.run(
                    chapter=chapter,
                    global_summary=global_summary,
                    outline=chapter_outline,
                    current_length=chapter_word_count,
                    target_length=expected_word_count
                )
                
                print(f"{Fore.CYAN}Revision after expansion:{Style.RESET_ALL}")
                chapter = self.revision_agent.run(chapter=chapter,
                                                  global_summary=global_summary,
                                                  outline=chapter_outline)
                
                print(f"{Fore.CYAN}Cleaning after expansion:{Style.RESET_ALL}")
                chapter = self.cleaner_agent.run(chapter=chapter, outline=chapter_outline, chapter_number=idx, total_chapters=total)

            print(f"{Fore.CYAN}Committing Chapter {idx} to final chapters...{Style.RESET_ALL}")
            final_chapters.append(chapter)
            if not self.streaming:
                print(f"\n{Fore.CYAN}Draft for Chapter {idx}:{Style.RESET_ALL}\n{chapter}\n")
            try:
                save_chapter(db_file, project_id, idx, chapter_outline, chapter)
            except Exception as e:
                print(f"{Fore.RED}Error saving chapter {idx}:{Style.RESET_ALL} {e}")
            # Write partial book draft.
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(self.compile_book(outline, final_chapters))
            except Exception as e:
                print(f"{Fore.RED}Error writing partial book:{Style.RESET_ALL} {e}")

        final_book = self.compile_book(outline, final_chapters)
        # After chapters have been generated:
        final_markdown_chapters = []
        for i, ch in enumerate(final_chapters):
            previous = final_markdown_chapters[i-1] if i > 0 else ""
            formatted = self.markdown_agent.run(chapter=ch, previous_chapter=previous)
            final_markdown_chapters.append(formatted)
        markdown_book = self.compile_markdown_book(outline, final_markdown_chapters)
        return final_book, markdown_book, outline

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

    if args.plot:
        input_details, plot_dir = load_input_details_from_plot(args.plot)
    else:
        input_details, plot_dir = prompt_for_input_details()

    bw_temp = BookWriter(debug=args.debug, streaming=args.stream, step_by_step=args.step, fast=args.fast)
    project_id, existing_outline, output_filename = initialize_project(args, input_details, plot_dir, bw_temp)
    starting_chapter = get_chapter_count(args.db_file, project_id) if args.resume else 0

    bw = BookWriter(debug=args.debug, streaming=args.stream, step_by_step=args.step, fast=args.fast)
    
    start_time = time.time()  # Start tracking time
    final_book, final_markdown, outline = bw.run(input_details, args.db_file, project_id, output_filename, existing_outline)
    end_time = time.time()  # End tracking time

    # Print summary
    chapter_count = len(bw.parse_outline(final_book))
    word_count = len(final_book.split())
    book_name = os.path.basename(output_filename).rsplit('.', 1)[0]
    elapsed_time = end_time - start_time

    summary = (
        f"{Fore.GREEN}=== SUMMARY ==={Style.RESET_ALL}\n"
        f"{Fore.CYAN}Book Name: {book_name}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Chapters: {chapter_count}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Word Count: {word_count}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Time Taken: {elapsed_time:.2f} seconds{Style.RESET_ALL}"
    )

    write_output_files(output_filename, final_book, final_markdown, summary)
    update_project_status(args.db_file, project_id, "completed")
    
    print(final_book)
    print(summary)

if __name__ == "__main__":
    main()