from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass, field
from typing import Optional
from typing_extensions import Literal


from rich.text import Text
from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Static

from typing import Any


class PresentationApp(App):
    """A Textual app for the presentation."""

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        (".", "run", "Run"),
        ("q", "quit", "Quit"),
        ("home", "home", "First slide"),
        ("e", "edit", "Edit"),
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
        yield Center(Markdown("Loading..."), id="content")
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

    def action_edit(self) -> None:
        if self.current_slide.path:
            with self.suspend():
                import os
                os.system(f"$EDITOR {self.current_slide.path}")
            self.current_slide.reload()
        self.update_slide()

    @property
    def current_slide(self) -> Any:
        return SLIDES[self.slide_index]

    def action_run(self) -> None:
        self.current_slide.run()
        self.update_slide()
        self.refresh()

    def update_slide(self):
        container_widget = self.query_one("#content", Center)
        content_widget = SLIDES[self.slide_index].render(app=self)
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


    def reload(self):
        if self.path:
            self.source = Path(self.path).read_text(encoding="utf-8")

    @abstractmethod
    def render(self, app: App) -> Widget:
        ...

    def is_runnable(self) -> bool:
        return False

    def run(self) -> None:
        pass


@dataclass
class CodeSlide(Slide):
    language: str = "python"
    mode: Literal["code", "output"]= "code"
    requires_alt_screen: bool = False

    def render(self, app) -> Widget:
        match self.mode:
            case "code":
                return self._render_code()
            case "output":
                if self.requires_alt_screen:
                    self._exec_in_alternate_screen(app)
                    return self._render_code()
                return self._render_output()

    def _render_code(self) -> Markdown:
        return Markdown(f"```{self.language}\n{self.source.strip()}\n```")

    def _render_output(self) -> Widget:
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            import plotext as plt
            plt.plotsize()
            exec(self.source)
        output = f.getvalue()
        output = "\n".join(line.rstrip() for line in output.splitlines())
        return Static(Text.from_ansi(output))

    def run(self):
        self.mode = "output" if self.mode == "code" else "code"

    def _exec_in_alternate_screen(self, app):
        with app.suspend():
            console = Console()
            console.clear()
            exec(self.source)
            console.control()
            self._wait_for_key()

    def _wait_for_key(self):
        import sys
        import tty
        import os
        import termios

        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            os.read(sys.stdin.fileno(), 3).decode()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)



class MarkdownSlide(Slide):
    def render(self, app: App) -> Markdown:
        return Markdown(dedent(self.source))


SLIDES = [
    MarkdownSlide(path="slides/title.md"),
    CodeSlide(path="examples/spurious_correlations.py", mode="output"),
    MarkdownSlide("## Colours"),
    CodeSlide('print("\\033[31m Red text \\033[0m")  # Red text'),
    CodeSlide(path="slides/colours1.py"),
    CodeSlide(path="slides/hello.py"),
    CodeSlide(path="slides/hello2.py"),
    CodeSlide(path="slides/kitty.py", requires_alt_screen=True),
    MarkdownSlide("Thank you!")
]


if __name__ == "__main__":
    main()
