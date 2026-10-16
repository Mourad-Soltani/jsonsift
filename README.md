# JsonSift

A minimal, zero-dependency Python CLI for inspecting JSON.

**Built by Mourad.Soltani**

## What you get

- `pretty` — pretty-print JSON with configurable indent
- `validate` — check that a file (or stdin) is valid JSON (exit code 0/1)
- `extract` — pull a value by simple path (`user.address[0].city`)
- `diff` — structural diff of two JSON documents
- `health` — machine-readable health check

## Requirements

- Python 3.8+
- No external dependencies

## How to run in 30 seconds

```bash
# From the project root
python jsonsift.py health
python jsonsift.py pretty sample.json
python jsonsift.py extract sample.json user.email
python jsonsift.py diff left.json right.json
echo '{"a":1}' | python jsonsift.py validate -
```

Or install editable:

```bash
pip install -e .
jsonsift health
```

## License

MIT — see LICENSE

Built by Mourad.Soltani
