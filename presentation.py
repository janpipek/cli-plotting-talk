# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "plotext",
#     "plottypus[kitty,notcurses]",
#     "textual",
# ]
# ///
import io
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass, field
from typing import Optional, ClassVar, Literal, Callable

import click
from rich.text import Text
from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Static
from rich.panel import Panel

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
        # yield Header(show_clock=True)
        yield Center(Markdown("Loading..."), id="content")
        yield Footer()

    def on_mount(self) -> None:
        """Hook called when the app is mounted."""
        self.theme = "textual-light"
        self.update_slide()

    def on_resize(self) -> None:
        """Hook called when the app is resized."""
        self.update_slide()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_next_slide(self) -> None:
        self.switch_to_slide(min(self.slide_index + 1, len(SLIDES) - 1))

    def action_prev_slide(self) -> None:
        self.switch_to_slide(max(self.slide_index - 1, 0))

    def action_home(self) -> None:
        self.switch_to_slide(0)
        
    def switch_to_slide(self, index: int) -> None:
        curent_index = self.slide_index
        if index != curent_index:
            self.slide_index = index
            self.update_slide()

    def action_edit(self) -> None:
        if self.current_slide.path:
            with self.suspend():
                import os
                os.system(f"$EDITOR {self.current_slide.path}")
            self.current_slide.reload()
        self.update_slide()

    @property
    def current_slide(self) -> "Slide":
        return SLIDES[self.slide_index]

    def action_run(self) -> None:
        if self.current_slide.runnable:
            self.current_slide.run()
            self.update_slide()
            self.refresh()

    def update_slide(self):
        container_widget = self.query_one("#content", Center)
        content_widget = SLIDES[self.slide_index].render(app=self)
        container_widget.remove_children()
        container_widget.mount(content_widget)
        Path(".current_slide").write_text(str(self.slide_index))


@click.command()
@click.option("--continue", "-c", "continue_", is_flag=True, help="Enable debug mode.")
def main(continue_):
    app = PresentationApp()
    if continue_ and Path(".current_slide").exists():
        app.slide_index = int(Path(".current_slide").read_text())
    app.slide_index = min(app.slide_index, len(SLIDES) - 1)
    app.run()


@dataclass()
class Slide(ABC):
    path: Optional[str | Path] = field(default=None, kw_only=True)
    source: str = ""
    runnable: ClassVar[bool] = False

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
    runnable: ClassVar[bool] = True
    wait_for_key: bool = True

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
            plt.plotsize(
                width=50,
                height=15
            )
            self._exec()
        output = f.getvalue()
        output = "\n".join(line.rstrip() for line in output.splitlines())
        return Static(Text.from_ansi(output))
    
    def _exec(self):
        match self.language:
            case "python":
                exec(self.source)
            case "shell":
                import os
                os.system(self.source)

    def run(self):
        self.mode = "output" if self.mode == "code" else "code"

    def _exec_in_alternate_screen(self, app):
        with app.suspend():
            console = Console()
            console.clear()
            self._exec()
            if self.wait_for_key:
                self._wait_for_key()
            self.mode = "code"
            console.clear()

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

@dataclass
class FuncSlide(Slide):
    f: Callable[[App], Markdown | Text | str] = field(kw_only=True)
    source = ""   # ignored
    path = None   # ignored

    def render(self, app: App):
        rendered = self.f(app)
        if isinstance(rendered, Widget):
            return rendered
        elif isinstance(rendered, str):
            return Markdown(dedent(rendered))
        elif isinstance(rendered, (Text, Panel)):
            return Static(rendered)


def dyn_md(f: Callable[[App], Any]):
    return FuncSlide(f=f)


@dyn_md
def terminal_is_your_weapon(app: App):
    dims = app.size

    return f"""\
    ## Terminal is your weapon:

    Reported size: *{dims.width}* x *{dims.height}*
    """

@dyn_md
def colours(app: App):
    out = io.StringIO()
    out.write("## Colours\n\n")

    for high in range(16):
        for low in range(16):
            colour = low + high * 16
            out.write(f"\033[38;5;{colour}m██\033[0m")
        out.write("\n")
    return Text.from_ansi(out.getvalue())


def md(path_or_text: str, **kwargs):
    if Path(path_or_text).exists():
        kwargs["path"] = path_or_text
    else:
        kwargs["source"] = path_or_text
    return MarkdownSlide(**kwargs)

def py(path_or_text: str, **kwargs):
    kwargs = {
        "language": "python",
        **kwargs,
    }
    if Path(path_or_text).exists():
        kwargs["path"] = path_or_text
    else:
        kwargs["source"] = path_or_text
    return CodeSlide(**kwargs)

def sh(cmd, **kwargs):
    kwargs = {
        "language": "shell",
        **kwargs,
    }
    return CodeSlide(source=cmd, **kwargs)


SLIDES = [
    # TODO: Read from toml/yaml, ...
    md("slides/title.md"),
    py("examples/spurious_correlations.py", mode="output"),
    md("## Why?"),
    sh("# Others use it too\n\nytop -I 1/20", language="shell", requires_alt_screen=True, wait_for_key=False),
    md("## How?"),
    terminal_is_your_weapon,
    py("slides/simple_bar.py"),
    py("slides/simple_bar_unicode.py", mode="output"),
    py("slides/colours1.py"),
    py("slides/colours2.py", mode="output"),
    py("slides/colours_rich.py", mode="output"),
    py("slides/simple_bar_color.py", mode="output"),
    md("## Aren't we reinventing the wheel?"),
    py("slides/hello.py"),
    py("slides/hello2.py"),
    md("## What if..."),
    md("## ...we could actually use matplotlib in the terminal?"),
    py("slides/kitty.py", requires_alt_screen=True),
    md("# Thank you!")
]


if __name__ == "__main__":
    main()
