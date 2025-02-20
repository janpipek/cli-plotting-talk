marp-package := "@marp-team/marp-cli@4.1.1"
marp-flags := "--allow-local-files --browser chrome --browser-path `which brave-browser`"

pdf:
    npx {{ marp-package }} presentation/talk.md --pdf {{ marp-flags }}

run:
    uv run presentation.py

watch:
    npx {{ marp-package }} -w presentation/talk.md

example-spurious:
    uv run examples/spurious_correlations.py
