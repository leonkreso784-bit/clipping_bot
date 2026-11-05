"""Lažni `claude -p` za testove: pročita stdin, ispiše JSON kakav vraća pravi Claude Code.

`FAKE_CLAUDE_OUTPUT` nosi `structured_output` (JSON); `FAKE_CLAUDE_EXIT` izlazni kod;
`FAKE_CLAUDE_ARGS` putanja u koju se upisuju primljeni argumenti.
"""

import json
import os
import sys

prompt = sys.stdin.read()
args_file = os.environ.get("FAKE_CLAUDE_ARGS")
if args_file:
    with open(args_file, "w", encoding="utf-8") as handle:
        json.dump({"argv": sys.argv[1:], "prompt_len": len(prompt)}, handle)
code = int(os.environ.get("FAKE_CLAUDE_EXIT", "0"))
if code:
    sys.stderr.write("lažna greška\n")
    sys.exit(code)
output = json.loads(os.environ.get("FAKE_CLAUDE_OUTPUT", '{"kandidati": []}'))
print(
    json.dumps(
        {"type": "result", "subtype": "success", "is_error": False, "structured_output": output}
    )
)
