import argparse
import os
from datetime import datetime, timezone
from typing import Any
import json
import contextlib

from xml_to_markdown_converter import (
    get_system_language, t, select_xml_file, load_xml, extract_text_content
)
from split_markdown_file import split_and_save_markdown, LAST_ENTRY_TIME_FILE


def load_json(filepath: str) -> list[dict[str, Any]]:
    """Load a JSON file"""
    if not os.path.exists(filepath):
        print(t("file_not_found", filepath))
        return []

    with open(filepath, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(t("json_decode_error", e))
            return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert XML notes to Markdown for NotebookLM")
    parser.add_argument(
        "--output_file",
        metavar="FILE",
        type="str",
        default="Notebook_Notes.md",
        help="Path to output Markdown file",
    )
    parser.add_argument("--limit", type=int, default=1500000, help="Split file size limit in bytes")

    args = parser.parse_args()
    output_md_filename: str = args.output_file
    md_file_size_limit: int = args.limit

    input_xml_filename = select_xml_file()
    if not input_xml_filename:
        print("XMLファイルが選択されませんでした。処理を中断します。")
        return

    try:
        print(t("start_processing", input_xml_filename))

        root_element = load_xml(input_xml_filename)
        if root_element is None:
            return

        channel_element = root_element.find("channel")
        if channel_element is None:
            print(t("error_occurred", "No <channel> element found in XML."))
            return

        entries = channel_element.findall("item")

        print(t("extracted_entries", len(entries), len(entries)))
        print(t("converting_markdown"))

        last_entry_time_loaded: datetime = datetime.min.replace(tzinfo=timezone.utc)
        last_entry_time_processed: datetime = datetime.min.replace(tzinfo=timezone.utc)
        if os.path.exists(LAST_ENTRY_TIME_FILE):
            with open(LAST_ENTRY_TIME_FILE, encoding="utf-8") as f:
                time_str = f.read().strip()
                with contextlib.suppress(ValueError):
                    last_entry_time_loaded = datetime.fromisoformat(time_str)

        markdown_output_texts = []
        for entry_element in entries:
            dt, text = extract_text_content(entry_element, last_entry_time_loaded)
            if text == "":
                continue
            last_entry_time_processed = dt
            markdown_output_texts.append(text)
        
        base_name, ext = os.path.splitext(output_md_filename)

        total_files_written = split_and_save_markdown(
            markdown_output_texts,
            base_name,
            ext,
            md_file_size_limit,
            last_entry_time_processed
        )

        print(t("processing_complete", last_entry_time_loaded, last_entry_time_processed, total_files_written))
    except Exception as e:
        print(t("error_occurred", e))


if __name__ == "__main__":
    main()
