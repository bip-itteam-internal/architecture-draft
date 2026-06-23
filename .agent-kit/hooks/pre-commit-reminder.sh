#!/usr/bin/env bash
# pre-commit-reminder.sh — PreToolUse(Bash) reminder non-blocking sebelum git commit
raw="$(cat)"
case "$raw" in
  *"git commit"*)
    msg='Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau?'
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"%s"}}\n' "$msg"
    ;;
esac
exit 0
