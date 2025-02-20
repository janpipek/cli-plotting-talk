from abc import ABC
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass

from rich.prompt import Prompt
from plotext import sleep
from plottypus.core import PlotType, Backend
from plottypus.plotting import plot

from rich import console
from rich.text import Text
from rich.console import Capture, Console
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown

from typing import Any


class PresentationApp(App):
    """A Textual app for the presentation."""

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        ("r", "run", "Run"),
        ("q", "quit", "Quit"),
        ("home", "home", "First slide"),
        ("d", "toggle_dark", "Toggle dark mode")
    ]

    TITLE = "▃█▅ Terminal plotting"

    CSS = """
        Screen {
            align: center middle;
        }
        """

    slide_index: int = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Markdown("Loading...", id="content")
        yield Footer()

    def on_mount(self) -> None:
        """Hook called when the app is mounted."""
        self.theme = "textual-light"
        self.update_slide()

    @staticmethod
    def render_slide(s: Any) -> str:
        if isinstance(s, str):
            return dedent(s)
        if isinstance(s, Path):
            return s.read_text()
        return str(s)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_next_slide(self) -> None:
        self.slide_index = min(self.slide_index + 1, len(SLIDES) - 1)
        self.update_slide()

    def action_prev_slide(self) -> None:
        self.slide_index = max(self.slide_index - 1, 0)
        self.update_slide()

    def action_home(self) -> None:
        self.slide_index = 0
        self.update_slide()

    @property
    def current_slide(self) -> Any:
        return SLIDES[self.slide_index]

    def action_run(self) -> None:
        code_path = self.current_slide.path
        with self.suspend():
            console = Console()
            console.clear()
            code = Code(code_path)
            code.run()
            Prompt.ask("[yellow]Press Enter to continue...[/yellow]")
        # self.action_next_slide()
        self.refresh()

    def update_slide(self):
        content_widget = self.query_one("#content", Markdown)
        content_widget.update(self.render_slide(SLIDES[self.slide_index]))


def main():
    app = PresentationApp()
    app.run()


@dataclass
class Code():
    path: str

    @cached_property
    def source(self) -> str:
        return Path(self.path).read_text(encoding="utf-8")

    def __str__(self) -> str:
        return f"```python\n{self.source}\n```"

    def run(self) -> None:
        exec(self.source)


SLIDES = [
    Path("slides/title.md"),
    Code("slides/colours1.py"),
    Code("slides/hello.py"),
    Code("slides/hello2.py"),
    Code("slides/kitty.py"),
    "Thank you!"
]


if __name__ == "__main__":
    main()
