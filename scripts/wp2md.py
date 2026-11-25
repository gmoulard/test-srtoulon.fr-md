"""Convertit l'export WordPress de la SRT en Markdown.

Usage :
    python3 scripts/wp2md.py backupInitialSRT/<export>.xml

Écrit :
- backupInitialSRT/MD/      tout le contenu publié (articles et pages), tel quel ;
- production/_posts/        les articles publics, prêts pour Jekyll ;
- production/_data/fonds.yml les photos de fond tirées au hasard en page d'accueil.

Les articles de la catégorie « Accès privé » et les pages réservées aux membres
ne vont jamais dans production/.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from markdownify import markdownify

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}
PRIVATE_CATEGORY = "Accès privé"
PRIVATE_PAGES = {
    "acces-reserve", "accueil-espace-prive", "annuaire", "menu-de-gestion",
    "connect-srt", "assemblees-generales",
}
PRODUCTION_PAGES = {
    "presentation-club": ("la-srt", "La SRT"),
    "organigramme": ("organigramme", "Organigramme"),
    "contacts": ("contacts", "Contacts"),
    "regates-voile-habitable": ("regates", "Liste des régates"),
    "commission-voile": ("commission-voile", "Commission voile"),
    "commission-peche": ("commission-peche", "Commission pêche"),
    "commission-animation": ("commission-animation", "Commission animation"),
    "environement": ("environnement", "Environnement"),
    "preservation-de-lenvironnement": ("preservation-environnement", "Préservation de l'environnement"),
    "clupipp": ("clupipp", "CLUPIPP"),
    "upncr": ("upncr", "UPNCR"),
    "politique-de-confidentialite": ("politique-de-confidentialite", "Politique de confidentialité"),
}
ACTIVITIES = [
    ("Commission pêche", "Pêche"),
    ("Commission voile", "Régate"),
    ("Commission animation", "Vie du club"),
    ("CLUPIPP", "Port"),
    ("UPNCR", "Port"),
]
IMAGE = re.compile(r"\.(jpe?g|png|webp|gif)$", re.I)


def text(item, path):
    node = item.find(path, NS)
    return (node.text or "") if node is not None else ""


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for tag in soup.find_all(["script", "style", "iframe", "form", "noscript"]):
        tag.decompose()
    for h in soup.find_all("h6"):
        h.name = "p"
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and not IMAGE.search(src.split("?")[0]):
            link = soup.new_tag("a", href=src)
            link.string = img.get("alt") or "Document"
            img.replace_with(link)
            continue
        for attr in list(img.attrs):
            if attr not in ("src", "alt"):
                del img[attr]
    return str(soup)


def to_markdown(html):
    md = markdownify(clean_html(html), heading_style="ATX", bullets="-", strip=["span", "div"])
    md = md.replace(" ", " ")
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"(!\[[^\]]*\]\([^)]+\))\s*\n\s*\n(?=!\[)", r"\1\n", md)
    return md.strip() + "\n"


def images_in(md):
    return re.findall(r"!\[[^\]]*\]\(([^)\s]+)", md)


def yaml_str(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def front_matter(fields):
    lines = ["---"]
    for key, value in fields.items():
        if value is None or value == [] or value == "":
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {yaml_str(v)}" for v in value)
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {yaml_str(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def excerpt_of(md, limit=180):
    for block in md.split("\n\n"):
        plain = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)|[#*_>`]", r"\1", block).strip()
        if len(plain) > 40:
            return plain if len(plain) <= limit else plain[:limit].rsplit(" ", 1)[0] + "…"
    return ""


def main(export):
    root = Path(export).resolve().parent.parent
    channel = ET.parse(export).getroot().find("channel")
    items = channel.findall("item")
    attachments = {
        text(i, "wp:post_id"): text(i, "wp:attachment_url")
        for i in items if text(i, "wp:post_type") == "attachment"
    }

    backup = root / "backupInitialSRT" / "MD"
    posts_dir = root / "production" / "_posts"
    for d in (backup / "articles", backup / "pages", posts_dir, root / "production" / "_data"):
        d.mkdir(parents=True, exist_ok=True)

    backgrounds = []
    count = {"articles": 0, "pages": 0, "publics": 0, "pages_site": 0}
    for item in items:
        kind = text(item, "wp:post_type")
        if kind not in ("post", "page") or text(item, "wp:status") != "publish":
            continue
        title = text(item, "title").strip()
        slug = text(item, "wp:post_name")
        date = text(item, "wp:post_date")
        categories = [c.text for c in item.findall("category") if c.get("domain") == "category"]
        tags = [c.text for c in item.findall("category") if c.get("domain") == "post_tag"]
        meta = {text(m, "wp:meta_key"): text(m, "wp:meta_value") for m in item.findall("wp:postmeta", NS)}
        image = attachments.get(meta.get("_thumbnail_id", ""), "")
        md = to_markdown(text(item, "content:encoded"))
        private = PRIVATE_CATEGORY in categories or slug in PRIVATE_PAGES

        fields = {
            "title": title, "date": date, "slug": slug,
            "categories": categories, "tags": tags,
            "image": image, "original": text(item, "link"), "prive": private,
        }
        if kind == "post":
            (backup / "articles" / f"{date[:10]}-{slug}.md").write_text(front_matter(fields) + md)
            count["articles"] += 1
            if private:
                continue
            photos = images_in(md)
            activity = next((label for cat, label in ACTIVITIES if cat in categories), "Actualité")
            (posts_dir / f"{date[:10]}-{slug}.md").write_text(front_matter({
                "title": title, "date": date, "activite": activity,
                "categories": categories, "image": image or (photos[0] if photos else ""),
                "photos": len(photos), "resume": excerpt_of(md), "original": text(item, "link"),
            }) + md)
            count["publics"] += 1
            if image:
                backgrounds.append(image)
        else:
            (backup / "pages" / f"{slug}.md").write_text(front_matter(fields) + md)
            count["pages"] += 1
            if slug in PRODUCTION_PAGES and not private:
                name, label = PRODUCTION_PAGES[slug]
                (root / "production" / f"{name}.md").write_text(front_matter({
                    "layout": "page", "title": label, "permalink": f"/{name}/", "original": text(item, "link"),
                }) + md)
                count["pages_site"] += 1

    (root / "production" / "_data" / "fonds.yml").write_text(
        "".join(f"- {yaml_str(u)}\n" for u in sorted(set(backgrounds), reverse=True))
    )
    print(count)


if __name__ == "__main__":
    main(sys.argv[1])
