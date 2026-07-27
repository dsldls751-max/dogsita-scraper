import csv, json, re, time, pathlib
from playwright.sync_api import sync_playwright
BASE="https://www.maxizoo.fr/c/chien/nourriture-pour-chien/nourriture-seche/"
MAXPAGES=int(__import__("os").environ.get("MAXPAGES","2"))  # 2 = test, 40 = tout
OUT="maxizoo_nutrition.csv"; DBG="debug_maxizoo.txt"
FIELDS=["proteines","matieres_grasses","cellulose","cendres","humidite","calcium","phosphore","sodium"]
LABELS={"proteines":r"prot[eé]ines?","matieres_grasses":r"mati[eè]res?\s+grasses","cellulose":r"(?:cellulose|fibres?)\s*brutes?","cendres":r"cendres\s*brutes?","humidite":r"humidit[eé]","calcium":r"calcium","phosphore":r"phosphore","sodium":r"sodium"}
def extract(txt):
    out={}
    for f,pat in LABELS.items():
        m=re.search(pat+r"\s*[:=]?\s*(\d+[.,]?\d*)\s*%",txt,re.I)
        if m: out[f]=m.group(1).replace(",",".")
    return out
def main():
    dbg=open(DBG,"w",encoding="utf-8")
    fout=open(OUT,"w",newline="",encoding="utf-8"); w=csv.writer(fout)
    w.writerow(["nom","marque","ref","url","composition"]+FIELDS)
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        page=ctx.new_page(); consent=False
        # 1) collecte les liens produits sur les pages de listing
        links=[]
        for pg in range(1,MAXPAGES+1):
            url=BASE+f"?currentPage={pg}"
            page.goto(url,timeout=60000,wait_until="domcontentloaded")
            if not consent:
                for t in ["Tout accepter","Accepter","J'accepte","Accept"]:
                    try:
                        btn=page.get_by_role("button",name=re.compile(t,re.I)).first
                        if btn and btn.is_visible(): btn.click(timeout=3000); consent=True; break
                    except Exception: pass
            page.wait_for_timeout(2500)
            hrefs=page.eval_on_selector_all("a[href*='/p/']","els=>els.map(e=>e.getAttribute('href'))")
            pagelinks=sorted(set("https://www.maxizoo.fr"+h if h.startswith("/") else h for h in hrefs if h and "/p/" in h))
            dbg.write(f"PAGE {pg}: {len(pagelinks)} liens produits\n")
            links+=pagelinks
            if not pagelinks: break
        links=sorted(set(links))
        dbg.write(f"TOTAL liens uniques: {len(links)}\n"); dbg.flush()
        # 2) visite chaque fiche
        got=0
        for i,url in enumerate(links,1):
            try:
                page.goto(url,timeout=60000,wait_until="domcontentloaded")
                page.wait_for_timeout(1500)
                # deroule les sections repliees
                for lab in ["Ingrédients","Détails du produit"]:
                    try:
                        el=page.get_by_text(re.compile(lab,re.I)).first
                        if el and el.is_visible(): el.click(timeout=1500); page.wait_for_timeout(500)
                    except Exception: pass
                body=page.inner_text("body")
                vals=extract(body)
                nom=""; 
                try: nom=page.title().split("|")[0].strip()
                except: pass
                mref=re.search(r"R[ée]f\.?\s*art\.?\s*:\s*(\d+)",body,re.I)
                mcomp=re.search(r"Composition\s*(.{0,400}?)(?:Teneur|Additifs|$)",body,re.I|re.S)
                w.writerow([nom,"",mref.group(1) if mref else "",url,(mcomp.group(1).strip() if mcomp else "")]+[vals.get(f,"") for f in FIELDS])
                fout.flush()
                if vals.get("proteines"): got+=1
                if i<=8:
                    dbg.write(f"\n=== FICHE {i} ===\n{url}\nnom:{nom}\nvaleurs:{vals}\n")
                    k=re.search(r"analytiques|prot[eé]ines?\s*:",body,re.I)
                    dbg.write((body[max(0,k.start()-20):k.start()+300] if k else "(pas de nutrition)")+"\n"); dbg.flush()
                print(i,"OK" if vals.get("proteines") else "--")
            except Exception as e:
                print(i,"err",e)
            time.sleep(1.2)
        b.close()
    fout.close(); dbg.close()
    print("TERMINE. fiches:",len(links),"avec nutrition:",got)
if __name__=="__main__": main()
