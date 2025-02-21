marp-package := "@marp-team/marp-cli@4.1.1"
marp-flags := "--allow-local-files --browser chrome --browser-path `which brave-browser`"

run:
    uv run --offline presentation.py

sync:
    uv sync

continue:
    uv run --offline presentation.py --continue

pdf:
    npx {{ marp-package }} presentation/talk.md --pdf {{ marp-flags }}

watch:
    npx {{ marp-package }} -w presentation/talk.md

example-spurious:
    uv run examples/spurious_correlations.py
