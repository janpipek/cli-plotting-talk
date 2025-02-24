# cli-plotting-talk

This is a live presentation about plotting in terminal which I gave at Python Pizza Brno 2025.
The presentation itself is a Python app that uses [Textual](https://textual.textualize.io/) to drive the display
of Markdown slides and run code snippets in a terminal window.

## Install & run

As a first step, clone the repository:

```
git clone https://github.com/janpipek/cli-plotting-talk
```

### uv & just

If you have [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just) on your system, you don't have to install anything to run the presentation.
Just run:

```sh
just present
```

### Otherwise

Just do (ideally in a virtual environment)

```
pip install -e .
python presentation.py
```

## References

See [slides/references.md](slides/references.md).
