"""Word Counter & Text Analyzer — an offline Tkinter desktop application."""

from __future__ import annotations

import re
import math
import csv
import tkinter as tk
# Collections module: Counter efficiently tallies repeated, normalized words.
from collections import Counter
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any


APP_TITLE = "Word Counter & Text Analyzer"
# Regular expressions (Regex): match Unicode words and sentence boundaries.
WORD_PATTERN = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
SENTENCE_PATTERN = re.compile(r"[^.!?…]+(?:[.!?…]+|$)")
BG = "#F3F6FB"
NAVY = "#172B4D"
MUTED = "#66758A"
ACCENT = "#4968E8"
CARD = "#FFFFFF"
# Common English function words can be hidden to make keyword patterns easier to see.
STOP_WORDS = frozenset("a an and are as at be been but by for from had has have he her hers him his i if in into is it its me my of on or our ours she so than that the their theirs them they this to too us was we were what when where which who will with you your yours".split())


def analyze_text(text: str) -> dict[str, Any]:
    """Return calculated text metrics and a case-insensitive frequency Counter.

    Concepts: string manipulation, Regex, lists, dictionaries, and Counter.
    """
    # Regex produces a list of word tokens; casefold makes matching case-insensitive.
    words = WORD_PATTERN.findall(text)
    normalized = [word.casefold() for word in words]
    frequencies = Counter(normalized)
    # Regex splits sentences and blank-line-separated paragraphs for their counts.
    sentences = [part for part in SENTENCE_PATTERN.findall(text) if WORD_PATTERN.search(part)]
    paragraphs = [part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
    lengths = [len(word) for word in words]
    most_common = frequencies.most_common(1)
    # A dictionary keeps related analysis results together for the GUI and report.
    return {
        "total_words": len(words),
        "characters_with_spaces": len(text),
        "characters_without_whitespace": len(re.sub(r"\s", "", text)),
        "total_sentences": len(sentences),
        "total_paragraphs": len(paragraphs),
        "average_word_length": sum(lengths) / len(lengths) if lengths else 0.0,
        "average_words_per_sentence": len(words) / len(sentences) if sentences else 0.0,
        "longest_word": max(words, key=len) if words else "—",
        "shortest_word": min(words, key=len) if words else "—",
        "most_frequent_word": most_common[0][0] if most_common else "—",
        "unique_words": len(frequencies),
        "reading_time_minutes": math.ceil(len(words) / 200) if words else 0,
        "speaking_time_minutes": math.ceil(len(words) / 130) if words else 0,
        "frequencies": frequencies,
    }


def format_report(text: str, metrics: dict[str, Any], source: str = "Typed text") -> str:
    """Build a readable report. Concepts: functions, lists, dictionaries, strings."""
    labels = [
        ("Total words", "total_words"),
        ("Characters (with spaces)", "characters_with_spaces"),
        ("Characters (without whitespace)", "characters_without_whitespace"),
        ("Total sentences", "total_sentences"),
        ("Total paragraphs", "total_paragraphs"),
        ("Average word length", "average_word_length"),
        ("Average words per sentence", "average_words_per_sentence"),
        ("Longest word", "longest_word"),
        ("Shortest word", "shortest_word"),
        ("Most frequently used word", "most_frequent_word"),
        ("Unique words", "unique_words"),
        ("Estimated reading time (minutes)", "reading_time_minutes"),
        ("Estimated speaking time (minutes)", "speaking_time_minutes"),
    ]
    lines = [APP_TITLE, "=" * len(APP_TITLE), f"Source: {source}", f"Generated: {datetime.now():%Y-%m-%d %H:%M}", "", "SUMMARY"]
    for label, key in labels:
        value = metrics[key]
        if isinstance(value, float):
            value = f"{value:.2f}"
        lines.append(f"{label}: {value}")
    lines.extend(["", "WORD FREQUENCY (most common first)"])
    if metrics["frequencies"]:
        lines.extend(f"{word}: {count}" for word, count in metrics["frequencies"].most_common())
    else:
        lines.append("No words to count.")
    return "\n".join(lines)


class WordCounterApp(tk.Tk):
    """Responsive Tkinter GUI; each button is connected to an operation callback."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1120x820")
        self.minsize(760, 620)
        self.configure(bg=BG)
        self.current_source = "Typed text"
        self.metrics: dict[str, Any] | None = None
        self.report = ""
        self.frequency_query = tk.StringVar(self)
        self.frequency_sort = tk.StringVar(self, value="Most frequent")
        self.hide_common_words = tk.BooleanVar(self, value=False)
        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=NAVY, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground=NAVY)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=MUTED)
        style.configure("CardValue.TLabel", background=CARD, foreground=NAVY, font=("Segoe UI", 21, "bold"))
        style.configure("CardName.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 10), background=ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", "#3855CF")])
        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), padding=(12, 9))

    def _build_ui(self) -> None:
        # Tkinter frames, labels, buttons, text widgets, and grid weights form the UI.
        shell = ttk.Frame(self, padding=(28, 22, 28, 20))
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)

        header = ttk.Frame(shell)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="A clear, private workspace for understanding your writing.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.live_counts = ttk.Label(header, text="Live count: 0 words  |  0 characters", style="Subtitle.TLabel")
        self.live_counts.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

        self._build_stats(shell)

        work = ttk.Frame(shell)
        work.grid(row=2, column=0, sticky="nsew", pady=(18, 0))
        work.columnconfigure(0, weight=3, uniform="pane")
        work.columnconfigure(1, weight=2, uniform="pane")
        work.rowconfigure(1, weight=1)
        top = ttk.Frame(work)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="Your text", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w")
        self.source_label = ttk.Label(top, text="Typed text", style="Subtitle.TLabel")
        self.source_label.grid(row=0, column=1, sticky="e")

        input_card = ttk.Frame(work, style="Card.TFrame", padding=12)
        input_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        input_card.rowconfigure(0, weight=1)
        input_card.columnconfigure(0, weight=1)
        self.text_input = tk.Text(input_card, wrap="word", undo=True, font=("Segoe UI", 11), bg=CARD, fg=NAVY, insertbackground=ACCENT, relief="flat", padx=12, pady=12, spacing1=2, spacing3=2)
        input_scroll = ttk.Scrollbar(input_card, orient="vertical", command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=input_scroll.set)
        self.text_input.grid(row=0, column=0, sticky="nsew")
        input_scroll.grid(row=0, column=1, sticky="ns")
        self.text_input.insert("1.0", "Paste or type your text here, or upload a .txt file to get started.")
        self.text_input.bind("<FocusIn>", self._remove_placeholder)
        self.text_input.bind("<KeyRelease>", self._update_live_counts)
        self.text_input.bind("<<Paste>>", self._update_live_counts)
        self.text_input.bind("<<Cut>>", self._update_live_counts)

        results_card = ttk.Frame(work, style="Card.TFrame", padding=14)
        results_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        results_card.rowconfigure(2, weight=1)
        results_card.columnconfigure(0, weight=1)
        ttk.Label(results_card, text="Word frequency", font=("Segoe UI", 13, "bold"), background=CARD).grid(row=0, column=0, sticky="w", pady=(0, 8))
        controls = ttk.Frame(results_card, style="Card.TFrame")
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        controls.columnconfigure(0, weight=1)
        search = ttk.Entry(controls, textvariable=self.frequency_query)
        search.insert(0, "")
        search.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        search.configure(takefocus=True)
        self.frequency_query.trace_add("write", lambda *_: self._render_frequency())
        sort_box = ttk.Combobox(controls, textvariable=self.frequency_sort, values=("Most frequent", "Least frequent", "A to Z"), state="readonly", width=14)
        sort_box.grid(row=0, column=1, sticky="e")
        sort_box.bind("<<ComboboxSelected>>", lambda _event: self._render_frequency())
        ttk.Checkbutton(controls, text="Hide common words", variable=self.hide_common_words, command=self._render_frequency).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.frequency_text = tk.Text(results_card, wrap="none", state="disabled", font=("Consolas", 10), bg="#F8FAFD", fg=NAVY, relief="flat", padx=10, pady=10)
        freq_y = ttk.Scrollbar(results_card, orient="vertical", command=self.frequency_text.yview)
        self.frequency_text.configure(yscrollcommand=freq_y.set)
        self.frequency_text.grid(row=2, column=0, sticky="nsew")
        freq_y.grid(row=2, column=1, sticky="ns")
        ttk.Label(results_card, text="Search and sort the case-insensitive word list.", background=CARD, style="Subtitle.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 0))

        actions = ttk.Frame(shell)
        actions.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        for i in range(6):
            actions.columnconfigure(i, weight=1)
        ttk.Button(actions, text="Upload TXT", style="Action.TButton", command=self.upload_file).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(actions, text="Clear All", style="Action.TButton", command=self.clear_all).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(actions, text="Analyze Text", style="Primary.TButton", command=self.analyze).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(actions, text="Copy Results", style="Action.TButton", command=self.copy_results).grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Button(actions, text="Export Report", style="Action.TButton", command=self.export_report).grid(row=0, column=4, sticky="ew", padx=4)
        ttk.Button(actions, text="Export CSV", style="Action.TButton", command=self.export_frequency_csv).grid(row=0, column=5, sticky="ew", padx=(4, 0))
        self.status = ttk.Label(shell, text="Ready · Your text stays on this device", style="Subtitle.TLabel")
        self.status.grid(row=4, column=0, sticky="w", pady=(9, 0))

    def _build_stats(self, parent: ttk.Frame) -> None:
        self.stat_values: dict[str, ttk.Label] = {}
        stats = [("total_words", "Total words"), ("characters_with_spaces", "Characters"), ("total_sentences", "Sentences"), ("unique_words", "Unique words"), ("average_word_length", "Avg. word length"), ("total_paragraphs", "Paragraphs")]
        grid = ttk.Frame(parent)
        grid.grid(row=1, column=0, sticky="ew")
        for col in range(4):
            grid.columnconfigure(col, weight=1, uniform="stats")
        stats.extend([("reading_time_minutes", "Read time (min)"), ("speaking_time_minutes", "Speak time (min)")])
        for idx, (key, label) in enumerate(stats):
            card = ttk.Frame(grid, style="Card.TFrame", padding=(14, 12))
            card.grid(row=idx // 4, column=idx % 4, sticky="ew", padx=(0 if idx % 4 == 0 else 6, 6 if idx % 4 < 3 else 0), pady=(0, 8))
            value = ttk.Label(card, text="—", style="CardValue.TLabel")
            value.pack(anchor="w")
            ttk.Label(card, text=label, style="CardName.TLabel").pack(anchor="w", pady=(2, 0))
            self.stat_values[key] = value

    def _remove_placeholder(self, _event: tk.Event) -> None:
        if self.text_input.get("1.0", "end-1c") == "Paste or type your text here, or upload a .txt file to get started.":
            self.text_input.delete("1.0", "end")
            self.text_input.unbind("<FocusIn>")

    def _input_value(self) -> str:
        value = self.text_input.get("1.0", "end-1c")
        if value == "Paste or type your text here, or upload a .txt file to get started.":
            return ""
        return value

    def _update_live_counts(self, _event: tk.Event | None = None) -> None:
        text = self._input_value()
        word_count = len(WORD_PATTERN.findall(text))
        self.live_counts.configure(text=f"Live count: {word_count:,} words  |  {len(text):,} characters")

    def _render_frequency(self) -> None:
        # Filter and sort the Counter entries, then render them in the scrollable list.
        if not hasattr(self, "frequency_text"):
            return
        items = self._visible_frequencies()
        self.frequency_text.configure(state="normal")
        self.frequency_text.delete("1.0", "end")
        self.frequency_text.insert("1.0", f"{'WORD':<32} {'COUNT':>5}\n" + "-" * 39 + "\n")
        for word, count in items:
            self.frequency_text.insert("end", f"{word[:30]:<32} {count:>5}\n")
        if not items:
            self.frequency_text.insert("end", "No matching words.")
        self.frequency_text.configure(state="disabled")

    def _visible_frequencies(self) -> list[tuple[str, int]]:
        """Apply the dashboard search, common-word filter, and sort order."""
        frequencies = self.metrics["frequencies"] if self.metrics else Counter()
        query = self.frequency_query.get().strip().casefold()
        items = [(word, count) for word, count in frequencies.items() if query in word]
        if self.hide_common_words.get():
            items = [(word, count) for word, count in items if word not in STOP_WORDS]
        if self.frequency_sort.get() == "A to Z":
            items.sort(key=lambda item: item[0])
        elif self.frequency_sort.get() == "Least frequent":
            items.sort(key=lambda item: (item[1], item[0]))
        else:
            items.sort(key=lambda item: (-item[1], item[0]))
        return items

    def analyze(self) -> None:
        """Validate the input, calculate metrics, and refresh dashboard widgets."""
        text = self._input_value()
        if not text.strip():
            messagebox.showinfo("Nothing to analyze", "Enter or upload some text first.", parent=self)
            return
        self.metrics = analyze_text(text)
        self.report = format_report(text, self.metrics, self.current_source)
        for key, label in self.stat_values.items():
            value = self.metrics[key]
            label.configure(text=f"{value:.2f}" if isinstance(value, float) else str(value))
        self._render_frequency()
        self.status.configure(text=f"Analysis complete · {self.metrics['total_words']:,} words")

    def upload_file(self) -> None:
        """Read a selected text file with encoding fallbacks and error handling."""
        filename = filedialog.askopenfilename(title="Choose a text file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], parent=self)
        if not filename:
            return
        try:
            path = Path(filename)
            # File handling: prefer UTF-8 (including BOM), fall back to Windows text.
            try:
                content = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                content = path.read_text(encoding="cp1252")
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", content)
            self._update_live_counts()
            self.current_source = path.name
            self.source_label.configure(text=path.name)
            self.status.configure(text=f"Loaded {path.name} · {len(content):,} characters")
            self.metrics = None
        # Exception handling keeps unreadable or inaccessible files from crashing UI.
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("Could not open file", f"The file could not be read.\n\n{exc}", parent=self)

    def clear_all(self) -> None:
        self.text_input.delete("1.0", "end")
        self.frequency_text.configure(state="normal")
        self.frequency_text.delete("1.0", "end")
        self.frequency_text.configure(state="disabled")
        for label in self.stat_values.values():
            label.configure(text="—")
        self.metrics = None
        self.report = ""
        self.frequency_query.set("")
        self.frequency_sort.set("Most frequent")
        self.current_source = "Typed text"
        self._update_live_counts()
        self.source_label.configure(text=self.current_source)
        self.status.configure(text="Ready · Your text stays on this device")

    def copy_results(self) -> None:
        """Copy the generated report using Tkinter's system clipboard interface."""
        if not self.report:
            messagebox.showinfo("No results yet", "Analyze some text before copying results.", parent=self)
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.report)
            self.update()
            self.status.configure(text="Analysis report copied to clipboard")
        except tk.TclError as exc:
            messagebox.showerror("Clipboard unavailable", f"Could not copy results.\n\n{exc}", parent=self)

    def export_report(self) -> None:
        """Write the report to a user-selected path using pathlib file handling."""
        if not self.report:
            messagebox.showinfo("No results yet", "Analyze some text before exporting a report.", parent=self)
            return
        filename = filedialog.asksaveasfilename(title="Export analysis report", defaultextension=".txt", initialfile="text_analysis_report.txt", filetypes=[("Text report", "*.txt")], parent=self)
        if not filename:
            return
        try:
            Path(filename).write_text(self.report + "\n", encoding="utf-8")
            self.status.configure(text=f"Report saved · {Path(filename).name}")
        except OSError as exc:
            messagebox.showerror("Could not save report", f"The report could not be written.\n\n{exc}", parent=self)

    def export_frequency_csv(self) -> None:
        """Export the currently filtered and sorted frequency list as CSV."""
        if not self.metrics:
            messagebox.showinfo("No results yet", "Analyze some text before exporting word frequencies.", parent=self)
            return
        filename = filedialog.asksaveasfilename(title="Export word frequencies", defaultextension=".csv", initialfile="word_frequencies.csv", filetypes=[("CSV spreadsheet", "*.csv")], parent=self)
        if not filename:
            return
        try:
            # CSV module handles delimiters and quoting for spreadsheet-friendly output.
            with Path(filename).open("w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(("Word", "Count"))
                writer.writerows(self._visible_frequencies())
            self.status.configure(text=f"Frequency CSV saved · {Path(filename).name}")
        except OSError as exc:
            messagebox.showerror("Could not save CSV", f"The frequency file could not be written.\n\n{exc}", parent=self)


def main() -> None:
    """Application entry point: create the GUI and start Tkinter's event loop."""
    try:
        app = WordCounterApp()
        app.mainloop()
    except tk.TclError as exc:
        messagebox.showerror(APP_TITLE, f"The application could not start.\n\n{exc}")


if __name__ == "__main__":
    main()
