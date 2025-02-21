from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass, field
from typing import Optional
from typing_extensions import Literal, override

from rich.prompt import Prompt

from rich.text import Text
from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Static, _markdown

from typing import Any


class PresentationApp(App):
    """A Textual app for the presentation."""

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        (".", "run", "Run"),
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
        yield Container(Markdown("Loading..."), id="content")
        yield Footer()

    def on_mount(self) -> None:
        """Hook called when the app is mounted."""
        self.theme = "textual-dark"
        self.update_slide()

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
        self.current_slide.run(self)
        self.refresh()

    def update_slide(self):
        container_widget = self.query_one("#content", Container)
        content_widget = SLIDES[self.slide_index].render()
        container_widget.remove_children()
        container_widget.mount(content_widget)


def main():
    app = PresentationApp()
    app.run()


@dataclass()
class Slide(ABC):
    path: Optional[str | Path] = field(default=None, kw_only=True)
    source: str = ""

    def __post_init__(self):
        if self.path:
            self.source = Path(self.path).read_text(encoding="utf-8")

    @abstractmethod
    def render(self) -> Widget:
        ...

    def is_runnable(self) -> bool:
        return False

    def run(self, app: PresentationApp) -> None:
        pass


@dataclass
class CodeSlide(Slide):
    language: str = "python"

    def render(self) -> Widget:
        return self._render_code()

    def _render_code(self) -> Markdown:
        return Markdown(f"```{self.language}\n{self.source.strip()}\n```")

    def run(self, app: PresentationApp) -> None:
        with app.suspend():
            console = Console()
            console.clear()
            exec(self.source)
            Prompt.ask("[yellow]Press Enter to continue...[/yellow]")


@dataclass
class DynamicSlide(CodeSlide):
    mode: Literal["code", "output"]= "output"

    def _render_output(self) -> Widget:
        console = Console()
        with console.capture() as capture:
            exec(self.source)
        return Static(Text.from_ansi(capture.get()))

    def render(self):
        match self.mode:
            case "code":
                return self._render_code()
            case "output":
                return self._render_output()


class MarkdownSlide(Slide):
    def render(self):
        return Markdown(dedent(self.source))


SLIDES = [
    MarkdownSlide(path="slides/title.md"),
    # DynamicSlide(path="examples/spurious_correlations.py"),
    CodeSlide(path="slides/colours1.py"),
    CodeSlide(path="slides/hello.py"),
    CodeSlide(path="slides/hello2.py"),
    CodeSlide(path="slides/kitty.py"),
    MarkdownSlide("Thank you!")
]


if __name__ == "__main__":
    main()
