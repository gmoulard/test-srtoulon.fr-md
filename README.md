# Site de la Société des Régates de Toulon

Nouveau site de la SRT, écrit en Markdown et publié par GitHub Pages.

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `docs/` | Le site publié (Jekyll). C'est le seul dossier à modifier pour faire évoluer le site. |
| `design/` | Les documents de design : maquettes HTML (`design/maquettes/`) et captures (`design/captures/`). |
| `backupInitialSRT/` | La sauvegarde de l'ancien site WordPress : l'export XML et, dans `MD/`, tout son contenu converti en Markdown (articles et pages). |
| `scripts/wp2md.py` | Le script qui convertit l'export WordPress en Markdown. |

## Modifier le site

Tout se fait en Markdown, directement sur github.com (crayon ✏️), sans rien installer.

- **Ajouter un récit de sortie** : créer un fichier dans `docs/_posts/`, nommé `AAAA-MM-JJ-titre-court.md` :

  ```markdown
  ---
  title: "Sortie pêche de juillet"
  date: 2026-07-12
  activite: "Pêche"
  categories: ["Actualités", "Commission pêche"]
  image: "https://…/photo-principale.jpg"
  photos: 12
  resume: "Une phrase qui donne envie de lire le récit."
  ---

  Le récit, en Markdown.

  ![](https://…/photo1.jpg)
  ![](https://…/photo2.jpg)
  ```

  Les photos placées sur des lignes qui se suivent s'affichent en galerie. `activite` vaut `Régate`, `Pêche`, `Vie du club`, `Port` ou `Actualité`. Les récits de la catégorie `Actualités` qui ont une `image` passent dans le carrousel de la page d'accueil.

- **Page d'accueil** : `docs/index.md` (phrase d'accroche, activités, comité, partenaires, texte de bienvenue).
- **Photos de fond de l'accueil**, tirées au hasard à chaque visite : `docs/_data/fonds.yml`.
- **Menu, adresse, téléphone, e-mail** : `docs/_config.yml`.
- **Pages du club** (La SRT, Contacts, Régates…) : les fichiers `.md` de `docs/`.

## Publication

Le site est publié sur https://gmoulard.github.io/test-srtoulon.fr-md/ à chaque modification de `docs/` sur la branche `main` : GitHub Pages construit lui-même le site Jekyll du dossier `docs/`.

À faire une seule fois : **Settings → Pages → Build and deployment → Source : Deploy from a branch**, branche `main`, dossier `/docs`.

Pour un nom de domaine (srtoulon.fr), ajouter `docs/CNAME` contenant `srtoulon.fr`, mettre `baseurl: ""` dans `docs/_config.yml` et faire pointer le DNS vers GitHub Pages.

## Reconvertir l'export WordPress

```bash
pip install beautifulsoup4 markdownify
python3 scripts/wp2md.py backupInitialSRT/socitdesrgatesdetoulon.WordPress.2026-11-23.xml
```

Attention : la reconversion réécrit `docs/_posts/`, les pages de `docs/` issues de WordPress et `docs/_data/fonds.yml`. Les articles « Accès privé » et les pages réservées aux membres ne vont jamais dans `docs/`.

## Tester en local

```bash
gem install jekyll:3.10.0 kramdown-parser-gfm webrick
cd docs && jekyll serve
```
