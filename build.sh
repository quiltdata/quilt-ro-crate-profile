#!/bin/sh
# Build the publishable form of the profile.
#
#   1. Regenerate VERSION/index.html from spec/profile.md, the source of truth. The
#      Profile Crate declares index.html as its `specification` artifact, so this must
#      be re-run whenever the spec changes.
#
#   2. Create VERSION/ro-crate-metadata.jsonld as a byte-identical copy of
#      ro-crate-metadata.json.
#
#      Why the copy: RO-Crate requires the metadata document to be named
#      ro-crate-metadata.json, but GitHub Pages maps file extensions to content types
#      and serves .json as application/json. A client asking for application/ld+json
#      needs a .jsonld extension to receive the right type. Measured on GitHub Pages:
#        ro-crate-metadata.json   -> application/json; charset=utf-8
#        ro-crate-metadata.jsonld -> application/ld+json
#      The w3id rules therefore negotiate to the .jsonld URL. This is the aliasing the
#      RO-Crate JSON-LD appendix recommends for CDNs; a real symlink is avoided because
#      GitHub Pages does not reliably follow them.
#
# Requires python-markdown:  pip install markdown
set -e
cd "$(dirname "$0")"

VERSION="${1:-0.1}"
[ -d "$VERSION" ] || { echo "no such version directory: $VERSION" >&2; exit 1; }

{
  cat <<'HEAD'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quilt RO-Crate profile</title>
<style>
 body{font-family:system-ui,-apple-system,sans-serif;line-height:1.55;max-width:46rem;
      margin:2rem auto;padding:0 1rem;color:#1b1b1b}
 code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em}
 pre{background:#f6f6f6;padding:.75rem;overflow-x:auto;border-radius:4px}
 table{border-collapse:collapse;width:100%;margin:1rem 0}
 th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;vertical-align:top}
 th{background:#f6f6f6}
 h1,h2,h3{line-height:1.25}
 blockquote{border-left:3px solid #ddd;margin-left:0;padding-left:1rem;color:#555}
 dfn{font-weight:600;font-style:normal}
 a{color:#0b5cad}
</style>
</head>
<body>
<p><em>Generated from <code>spec/profile.md</code> by <code>build.sh</code>.
Do not edit directly.</em></p>
HEAD
  markdown_py -x tables -x fenced_code -x toc spec/profile.md

  # Anchors for the term IRIs. A fragment is never sent to the server, so
  # https://w3id.org/quilt/ro-crate#packageName resolves to this page and the browser
  # scrolls to the matching id. Without these the term IRIs land on the page but
  # nowhere useful.
  cat <<'TERMS'
<h2 id="term-definitions">Term definitions</h2>
<dl>
<dt id="packageName"><dfn>packageName</dfn></dt>
<dd>Identifies a <code>PropertyValue</code> whose value is the fully qualified name of the
Quilt package to build, in the form <code>namespace/name</code>. Used as the value of
<code>propertyID</code>. Takes precedence over <code>packageNamespace</code>.</dd>
<dt id="packageNamespace"><dfn>packageNamespace</dfn></dt>
<dd>Identifies a <code>PropertyValue</code> whose value is the namespace portion only of
the Quilt package name. The name portion is derived from the <code>name</code> of the root
data entity. Used as the value of <code>propertyID</code>.</dd>
<dt id="ELNEntry"><dfn>ELNEntry</dfn></dt>
<dd>An entry in an electronic lab notebook that documents the experiment a crate records.
Used as the value of <code>additionalType</code> on a <code>CreativeWork</code>. The
notebook system is identified by <code>provider</code>, which keeps the term independent of
any one vendor.</dd>
</dl>
TERMS
  printf '</body>\n</html>\n'
} > "$VERSION/index.html"
echo "wrote $VERSION/index.html"

cp "$VERSION/ro-crate-metadata.json" "$VERSION/ro-crate-metadata.jsonld"
echo "wrote $VERSION/ro-crate-metadata.jsonld (content-type alias)"

# Root landing page listing the published versions.
#
# .nojekyll disables Jekyll, which means GitHub Pages does not render README.md as a
# directory index. Without this file the Pages root would 404. Generated here so that
# adding a version directory keeps the list accurate.
{
  cat <<'ROOTHEAD'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quilt RO-Crate profile</title>
<style>
 body{font-family:system-ui,-apple-system,sans-serif;line-height:1.55;max-width:40rem;
      margin:3rem auto;padding:0 1rem;color:#1b1b1b}
 a{color:#0b5cad} code{font-family:ui-monospace,Menlo,monospace;font-size:.9em}
 li{margin:.35rem 0}
</style>
</head>
<body>
<h1>Quilt RO-Crate profile</h1>
<p>An <a href="https://www.researchobject.org/ro-crate/">RO-Crate</a> profile for crates
ingested into <a href="https://docs.quiltdata.com/">Quilt</a> packages.</p>
<h2>Versions</h2>
<ul>
ROOTHEAD
  for d in $(ls -d [0-9]*/ 2>/dev/null | tr -d / | sort -rV); do
    printf '<li><a href="%s/">%s</a> &mdash; ' "$d" "$d"
    printf '<a href="%s/ro-crate-metadata.json">Profile Crate</a>, ' "$d"
    printf '<a href="%s/example1/ro-crate-metadata.json">example</a></li>\n' "$d"
  done
  cat <<'ROOTFOOT'
</ul>
<p>Source, issues and the full specification source:
<a href="https://github.com/quiltdata/quilt-ro-crate-profile">github.com/quiltdata/quilt-ro-crate-profile</a></p>
</body>
</html>
ROOTFOOT
} > index.html
echo "wrote index.html (root version index)"
