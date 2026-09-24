#!/usr/bin/env python3
"""Build and install the jkt-writing-system skill.

  python build_and_install.py                 # validate + build ZIP + install for Claude Code and Codex (user level)
  python build_and_install.py --zip-only      # validate + build ZIP only
  python build_and_install.py --project PATH  # also install into PATH/.claude/skills and PATH/.agents/skills

Targets
  Claude Code (user) : ~/.claude/skills/jkt-writing-system
  Codex CLI/IDE (user): ~/.agents/skills/jkt-writing-system
  claude.ai / ChatGPT: upload dist/jkt-writing-system.zip
Re-run after editing the skill to update every copy.
"""
import argparse, os, re, shutil, sys, zipfile

NAME = "jkt-writing-system"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, NAME)
DIST = os.path.join(HERE, "dist")


def validate():
    p = os.path.join(SRC, "SKILL.md")
    t = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    assert m, "SKILL.md must start with YAML frontmatter"
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M).group(1).strip()
    desc = re.search(r"^description:\s*(.+)$", fm, re.M).group(1).strip()
    assert name == NAME, f"name must be {NAME}"
    assert re.fullmatch(r"[a-z0-9-]{1,64}", name), "name: lowercase letters, digits, hyphens, <= 64 chars"
    assert 0 < len(desc) <= 1024 and "<" not in desc, "description: 1-1024 chars, no angle brackets"
    missing = [f for f in re.findall(r"`((?:references|scripts)/[^`]+)`", t) if not os.path.exists(os.path.join(SRC, f))]
    assert not missing, f"SKILL.md references missing files: {missing}"
    print(f"OK  SKILL.md valid (name={name}, description={len(desc)} chars)")


def build_zip():
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, f"{NAME}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(SRC):
            if "__pycache__" in root:
                continue
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.join(NAME, os.path.relpath(full, SRC)).replace(os.sep, "/"))
    print(f"OK  ZIP built: {out} ({os.path.getsize(out) // 1024} KB)")


def install(dest_root):
    dest = os.path.join(dest_root, NAME)
    os.makedirs(dest_root, exist_ok=True)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"OK  installed: {dest}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip-only", action="store_true")
    ap.add_argument("--project", help="also install into <project>/.claude/skills and <project>/.agents/skills")
    a = ap.parse_args()
    validate()
    build_zip()
    if a.zip_only:
        return
    home = os.path.expanduser("~")
    install(os.path.join(home, ".claude", "skills"))   # Claude Code
    install(os.path.join(home, ".agents", "skills"))   # Codex
    if a.project:
        install(os.path.join(a.project, ".claude", "skills"))
        install(os.path.join(a.project, ".agents", "skills"))
    print("\nNext: upload dist/jkt-writing-system.zip in claude.ai (Customize > Skills) and ChatGPT (Skills > Create > Upload).")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        sys.exit(f"ERROR {e}")
