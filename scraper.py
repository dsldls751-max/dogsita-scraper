#!/usr/bin/env python3
# Scraper poli pour les valeurs nutritionnelles Zooplus (via Playwright).
# Lit urls.csv (colonnes: code_barre, url), ouvre chaque fiche une par une,
# ouvre la section "constituants analytiques", extrait les valeurs, et ecrit
# au fur et a mesure dans produits_nutrition.csv. Reprend via state.json.
import csv, json, os, re, sys, time, pathlib

DELAY = 1.5                       # secondes entre chaque fiche (poli)
LIMIT = int(os.environ.get("TEST_LIMIT", "30"))   # 30 = test ; mets 0 pour tout
IN   = "urls.csv"
OUT  = "produits_nutrition.csv"
STATE= "state.json"

FIELDS = ["proteines","matieres_grasses","cellulose","cendres","humidite",
          "calcium","phosphore","sodium","omega_3","omega_6","calories"]
# mots-cles reperes dans le texte de la section analytique -> notre champ
PATTERNS = {
 "proteines":       r"prot[eé]ine",
 "matieres_grasses":r"mati[eè]res?\s+grasses|teneur\s+en\s+mati[eè]res\s+grasses|lipides",
 "cellulose":       r"cellulose",
 "cendres":         r"cendres",
 "humidite":        r"humidit[eé]",
 "calcium":         r"calcium",
 "phosphore":       r"phosphore",
 "sodium":          r"sodium",
 "omega_3":         r"om[eé]ga.?3",
 "omega_6":         r"om[eé]ga.?6",
 "calories":        r"kcal|[eé]nergie",
}

def load_state():
    if pathlib.Path(STATE).exists():
        try: return set(json.load(open(STATE)))
        except Exception: return set()
    return set()

def save_state(done):
    json.dump(sorted(done), open(STATE,"w"))

def parse_num(s):
    m = re.search(r"(\d+[.,]?\d*)", s)
    return m.group(1).replace(",", ".") if m else ""

def extract_from_text(txt):
    """Cherche 'protéine brute 26 %' etc. dans le texte de la section."""
    out = {}
    # decoupe en lignes/segments pour limiter les faux positifs
    segs = re.split(r"[\n;•|]", txt)
    for seg in segs:
        low = seg.lower()
        for field, pat in PATTERNS.items():
            if field in out: continue
            if re.search(pat, low) and re.search(r"\d", seg):
                val = parse_num(seg)
                if val: out[field] = val
    return out

def main():
    rows = list(csv.DictReader(open(IN, newline="", encoding="utf-8")))
    # dedup par URL, on garde la liste des code_barre par URL
    by_url = {}
    for r in rows:
        u = (r.get("url") or "").strip()
        b = (r.get("code_barre") or "").strip()
        if u: by_url.setdefault(u, []).append(b)
    urls = list(by_url.keys())

    done = load_state()
    todo = [u for u in urls if u not in done]
    if LIMIT: todo = todo[:LIMIT]
    print(f"URLs totales: {len(urls)} | deja faites: {len(done)} | a faire ce run: {len(todo)}")

    # ouvre le CSV de sortie en mode append (cree l'entete si absent)
    new_file = not pathlib.Path(OUT).exists()
    fout = open(OUT, "a", newline="", encoding="utf-8")
    writer = csv.writer(fout)
    if new_file:
        writer.writerow(["code_barre","url"] + FIELDS)

    from playwright.sync_api import sync_playwright
    got_nut = 0; blocked = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            locale="fr-FR",
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0 Safari/537.36"))
        page = ctx.new_page()
        for i, url in enumerate(todo, 1):
            try:
                resp = page.goto(url, timeout=30000, wait_until="domcontentloaded")
                status = resp.status if resp else 0
                if status == 403 or status == 429:
                    blocked += 1
                    print(f"[{i}] BLOQUE ({status}) sur {url}")
                    if blocked >= 3:
                        print(">>> Bloque 3 fois de suite -> arret propre (IP probablement bannie).")
                        break
                    time.sleep(10); continue
                blocked = 0
                # essaie d'ouvrir la section analytique si un bouton existe
                for label in ["Voir les constituants analytiques",
                              "constituants analytiques", "Analyse nutritionnelle"]:
                    try:
                        el = page.get_by_text(re.compile(label, re.I)).first
                        if el and el.is_visible():
                            el.click(timeout=2000); page.wait_for_timeout(800)
                            break
                    except Exception:
                        pass
                body = page.inner_text("body")
                vals = extract_from_text(body)
                for b in by_url[url]:
                    writer.writerow([b, url] + [vals.get(f,"") for f in FIELDS])
                fout.flush()
                done.add(url); save_state(done)
                if vals.get("proteines"): got_nut += 1
                print(f"[{i}/{len(todo)}] {'OK nutrition' if vals.get('proteines') else 'sans nutrition'} | {url.split('/')[-1]}")
            except Exception as e:
                print(f"[{i}] erreur: {e}")
            time.sleep(DELAY)
        browser.close()
    fout.close()
    print(f"\nTERMINE ce run. Fiches avec nutrition ce run: {got_nut}/{len(todo)}")
    if LIMIT:
        print(">>> C'ETAIT UN TEST (30 fiches). Si la nutrition est remplie, "
              "mets TEST_LIMIT=0 dans le workflow pour tout lancer.")

if __name__ == "__main__":
    main()
