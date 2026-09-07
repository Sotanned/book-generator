#!/bin/bash
set -euo pipefail

# Only needed in Claude Code on the web — plugin installs there don't
# persist across containers, so re-install on every fresh session.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! claude plugin list 2>/dev/null | grep -q "superpowers@claude-plugins-official"; then
  claude plugin install superpowers@claude-plugins-official
fi
