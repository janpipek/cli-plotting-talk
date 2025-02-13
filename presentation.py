from textwrap import dedent

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown


class PresentationApp(App):
    """A Textual app for the presentation."""

    BINDINGS = [("pageup", "prev_slide", "Previous"), ("pagedown", "next_slide", "Next"), ("q", "quit", "Quit"), ("home", "home", "First slide"), ("d", "toggle_dark", "Toggle dark mode")]

    TITLE = "▃█▅ Terminal plotting"

    slide_index: int = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(name="", show_clock=True)
        yield Markdown(dedent(SLIDES[0]), id="content")
        yield Footer()

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

    def update_slide(self):
        content_widget = self.query_one("#content", Markdown)
        content_widget.update(dedent(SLIDES[self.slide_index]))


def main():
    app = PresentationApp()
    app.run()


SLIDES = [
    """
    # ▃█▅ Terminal plotting

    Jan Pipek

    Python Pizza Brno 2025

    """,

    """
    Thank you
    """,



]


if __name__ == "__main__":
    main()
