import re
from pathlib import Path


EXPECTED_SKILLS = {
    "ml-stack",
    "ml-stack-research",
    "ml-stack-data",
    "ml-stack-model",
    "ml-stack-training",
    "ml-stack-experiment",
    "ml-stack-evaluation",
    "ml-stack-tracking",
    "ml-stack-compute",
    "ml-stack-deployment",
    "ml-stack-hub",
    "ml-stack-audit",
}
LOCAL_LINK = re.compile(r"\]\(([^)]+)\)")


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---"
    end = lines.index("---", 1)
    values = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        assert separator and key in {"name", "description"}
        values[key] = value.strip()
    return values


def test_canonical_catalog_and_frontmatter_are_complete():
    root = Path(__file__).resolve().parents[1]
    skills = root / "skills"
    assert {path.name for path in skills.iterdir() if path.is_dir()} == EXPECTED_SKILLS

    for name in EXPECTED_SKILLS:
        skill_dir = skills / name
        metadata = frontmatter(skill_dir / "SKILL.md")
        assert metadata["name"] == name
        assert metadata["description"]
        for href in LOCAL_LINK.findall((skill_dir / "SKILL.md").read_text(encoding="utf-8")):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (skill_dir / href).resolve()
            target.relative_to(skill_dir.resolve())
            assert target.is_file(), href


def test_canonical_and_generated_trees_have_no_stale_source_name():
    root = Path(__file__).resolve().parents[1]
    stale_name = "skills" + "-src"
    for tree in (root / "skills", root / "adapters"):
        assert all(stale_name not in path.name for path in tree.rglob("*"))
        for path in tree.rglob("*"):
            if path.is_file():
                assert stale_name not in path.read_bytes().decode("utf-8", errors="ignore")
