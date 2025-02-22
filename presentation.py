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
from textual.containers import Container, VerticalScroll
from textual.widget import Widget
from textual.widgets import Footer, Markdown, Static
from rich.panel import Panel
from textual.css.query import QueryError

from typing import Any


from textual.theme import Theme

my_theme = Theme(
    name="my",
    primary="#0000c0",
    secondary="#4040ff",
    accent="#00ff00",
    foreground="#444444",
    background="#ffffff",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#ffffff",
    panel="#ffffff",
    dark=False,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)


class PresentationApp(App):
    """A Textual app for the presentation."""

    enable_footer: bool = True

    CSS_PATH = Path("presentation.css")

    BINDINGS = [
        ("pageup", "prev_slide", "Previous"),
        ("pagedown", "next_slide", "Next"),
        (".", "run", "Run"),
        ("q", "quit", "Quit"),
        ("home", "home", "First slide"),
        ("e", "edit", "Edit"),
        ("r", "reload", "Reload"),
        # ("d", "toggle_dark", "Toggle dark mode")
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
        yield VerticalScroll(
            Markdown("Loading..."), id="content", can_focus=False
        )
        if self.enable_footer:
            yield Footer()

    def on_mount(self) -> None:
        """Hook called when the app is mounted."""
        self.register_theme(my_theme)
        self.theme = "my"
        self.update_slide()

    def on_resize(self) -> None:
        """Hook called when the app is resized."""
        self.update_slide()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_reload(self) -> None:
        self.current_slide.reload()
        self.update_slide()

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
        try:
            container_widget = self.query_one("#content", VerticalScroll)
            content_widget = SLIDES[self.slide_index].render(app=self)
            container_widget.remove_children()
            container_widget.mount(content_widget)
            Path(".current_slide").write_text(str(self.slide_index))
        except QueryError:
            pass


@click.command()
@click.option(
    "--continue", "-c", "continue_", is_flag=True, help="Enable debug mode."
)
@click.option("--disable-footer", is_flag=True, help="Disable footer.")
def main(continue_, disable_footer):
    app = PresentationApp()
    app.enable_footer = not disable_footer
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
    def render(self, app: App) -> Widget: ...

    def is_runnable(self) -> bool:
        return False

    def run(self) -> None:
        pass


@dataclass
class CodeSlide(Slide):
    language: str = "python"
    mode: Literal["code", "output"] = "code"
    requires_alt_screen: bool = False
    runnable: ClassVar[bool] = True
    wait_for_key: bool = True
    title: Optional[str] = None

    def render(self, app) -> Widget:
        match self.mode:
            case "code":
                return self._render_code()
            case "output":
                if self.requires_alt_screen:
                    self._exec_in_alternate_screen(app)
                    return self._render_code()
                return self._render_output(app=app)

    def _render_code(self) -> Markdown:
        code = "\n".join(
            " " + line.rstrip()
            for line in self.source.splitlines()
            if "# HIDE" not in line
        )
        if self.title:
            return Markdown(
                f"## {self.title}\n\n```{self.language}\n{code}\n```"
            )
        return Markdown(f"```{self.language}\n{code}\n```")

    def _render_output(self, app) -> Widget:
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        try:
            with redirect_stdout(f):
                import plotext as plt

                plt.plotsize(width=50, height=15)
                self._exec(app=app)
            output = f.getvalue()
        except Exception as ex:
            output = f"Error: {ex}"
        else:
            output = "\n".join(
                " " + line.rstrip() for line in output.splitlines()
            )
        output_widget = Static(Text.from_ansi(output))
        if self.title:
            return Container(Markdown(f"## {self.title}"), output_widget)
        return output_widget

    def _exec(self, app: App) -> None:
        match self.language:
            case "python":
                exec(
                    self.source,
                    globals=globals()
                    | {
                        "WIDTH": app.size.width - 4,
                        "HEIGHT": app.size.height - 2,
                    },
                )
                import plotext as plt

                plt.clear_figure()
            case "shell":
                import os

                os.system(self.source)

    def run(self):
        self.mode = "output" if self.mode == "code" else "code"

    def _exec_in_alternate_screen(self, app):
        with app.suspend():
            console = Console()
            console.clear()
            self._exec(app)
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
    source = ""  # ignored
    path = None  # ignored

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

    console = Console()
    console.color_system

    return f"""\
    ## (Modern) Terminal is your weapon

    - reports size: *{dims.width}* x *{dims.height}*

    - supports colours: {console.color_system}

    - supports ASCII: 

        \* # o . - | x
    
    - supports Unicode symbols:

        │ ─┌ ┐ └ ┘ ┼ ┴ ┬ █ 

    - supports alternate screen
        
    """


@dyn_md
def colours(app: App):
    out = io.StringIO()
    out.write("## Colours\n\n")

    for high in range(16):
        for low in range(16):
            colour = low + high * 16
            out.write(f"\033[38;5;{colour}m███\033[0m")
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
        if "title" not in kwargs:
            kwargs["title"] = path_or_text
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
    py(
        "examples/spurious_correlations.py",
        title="Czech jet fuel consumption vs successful climbs of Mt. Everest\n\n"
        "from Spurious correlations by Tyler Vigen",
        mode="output",
    ),
    md("# Why?"),
    py("slides/neo.py", title="1) It's cool.", mode="output"),
    # md("## 2) Others use it too."),
    sh(
        "ytop -I 1/20",
        title="2) Others use it too.",
        language="shell",
        requires_alt_screen=True,
        wait_for_key=False,
    ),
    md("## 3) Quickly visualise your script output"),
    md("## 4) Create embeddable ASCII plots"),
    md("# How?"),
    terminal_is_your_weapon,
    md("## Example: Simple barchart\nPopulation of Czech cities"),
    py("slides/simple_bar.py"),
    py("slides/simple_bar_unicode.py", mode="output"),
    md("slides/colours.md"),
    py("slides/colours1.py"),
    py("slides/colours256.py", mode="output"),
    # py("slides/colours_rich.py"),
    md("## Example: Simple scatter plot\nMap of Czech cities"),
    py("slides/simple_scatter.py"),
    md("## Example: Add the path of my train trip to Brno"),
    md("# Aren't we reinventing the wheel?\n\nI actually was/am..."),
    md("slides/libraries.md"),
    py("slides/plotille_line.py", requires_alt_screen=True),
    py("slides/plotille_hist.py"),
    py("examples/spurious_correlations.py"),
    py("slides/plotext_hist.py"),
    py("slides/plotext_lines.py", requires_alt_screen=True),
    md("## What if..."),
    md(
        "## ...we could actually use matplotlib in the terminal?\nkitty save us!"
    ),
    py("slides/kitty.py", requires_alt_screen=True),
    md("slides/final.md"),
    md("slides/references.md"),
]


if __name__ == "__main__":
    main()
