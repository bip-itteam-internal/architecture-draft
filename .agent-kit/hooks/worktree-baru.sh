#!/usr/bin/env bash
# worktree-baru.sh — cermin worktree-baru.ps1 (alasan desain di sana).
# pakai: worktree-baru.sh <repo> <slug> [domain=fix] [base=origin/main] [akar=~/wt] [--tanpa-install]
set -u
repo="${1:?repo}"; slug="${2:?slug}"; domain="${3:-fix}"; base="${4:-origin/main}"; akar="${5:-$HOME/wt}"
tanpa_install=0; for a in "$@"; do [ "$a" = "--tanpa-install" ] && tanpa_install=1; done
top="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || { echo "Bukan repo git: $repo" >&2; exit 2; }
common="$(git -C "$top" rev-parse --path-format=absolute --git-common-dir)"
nama="$(basename "$(dirname "$common")")"
case "$nama" in erp-frontend) prefix=fe;; bip-erp) prefix=be;; mybharata-app) prefix=mb;; architecture-draft) prefix=ad;; *) prefix="$(printf '%s' "$nama" | tr -cd 'a-z0-9' | cut -c1-3)";; esac
slug="$(printf '%s' "$slug" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' | cut -c1-30 | sed 's/-$//')"
[ -n "$slug" ] || { echo "Slug kosong setelah dibersihkan" >&2; exit 2; }
domain="$(printf '%s' "$domain" | tr -cd 'a-z')"
case "$domain" in fix|refactor|test|docs|feat|chore) ;; *) domain=fix;; esac
path="$akar/$prefix-$slug"; branch="$domain/$slug"
[ "${#path}" -le 60 ] || { echo "Path worktree terlalu panjang (${#path} > 60): $path" >&2; exit 2; }
case "$path" in *" "*) echo "Path worktree mengandung spasi: $path" >&2; exit 2;; esac
[ ! -e "$path" ] || { echo "Sudah ada: $path" >&2; exit 2; }
mkdir -p "$akar"
git -C "$top" fetch origin --quiet 2>/dev/null
if git -C "$top" rev-parse --verify --quiet "refs/heads/$branch" >/dev/null; then echo "Branch sudah ada: $branch" >&2; exit 2; fi
git -C "$top" worktree add -b "$branch" "$path" "$base" || { echo "git worktree add gagal" >&2; exit 1; }
jenis=lain; [ -f "$path/package.json" ] && [ -f "$path/pnpm-lock.yaml" ] && jenis=node; ls "$path"/services/*/go.mod >/dev/null 2>&1 && jenis=go
install_json=null
if [ "$jenis" = node ] && [ "$tanpa_install" -eq 0 ]; then
  t0=$(date +%s); (cd "$path" && pnpm install --prefer-offline --frozen-lockfile >/tmp/wt-install.log 2>&1); rc=$?; t1=$(date +%s)
  [ $rc -eq 0 ] && lolos=true || { lolos=false; echo "pnpm install GAGAL di worktree; lihat /tmp/wt-install.log" >&2; }
  install_json="{\"lolos\": $lolos, \"durasi_detik\": $((t1-t0))}"
fi
printf '{"repo":"%s","jenis":"%s","path":"%s","branch":"%s","base":"%s","install":%s}\n' "$nama" "$jenis" "$path" "$branch" "$base" "$install_json"
exit 0
