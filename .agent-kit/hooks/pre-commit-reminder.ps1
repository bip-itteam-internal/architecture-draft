# pre-commit-reminder.ps1 — PreToolUse(Bash) reminder non-blocking sebelum git commit
$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$cmd = $data.tool_input.command
if ($cmd -and ($cmd -match 'git\s+commit')) {
  $msg = 'Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau?'
  @{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; additionalContext = $msg } } |
    ConvertTo-Json -Compress -Depth 5
}
exit 0
