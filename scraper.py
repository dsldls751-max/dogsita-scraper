import csv, re, time, os
from playwright.sync_api import sync_playwright
BASE="https://www.maxizoo.fr/c/chien/nourriture-pour-chien/nourriture-seche/"
MAXPAGES=int(os.environ.get("MAXPAGES","2"))
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
    w.writerow(["nom","ref","url","composition"]+FIELDS)
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        page=ctx.new_page(); consent=False
        links=[]
        for pg in range(1,MAXPAGES+1):
            page.goto(BASE+f"?currentPage={pg}",timeout=60000,wait_until="domcontentloaded")
            if not consent:
                for t in ["Tout accepter","Accepter","J'accepte","Accept"]:
                    try:
                        btn=page.get_by_role("button",name=re.compile(t,re.I)).first
                        if btn and btn.is_visible(): btn.click(timeout=3000); consent=True; break
                    except Exception: pass
            page.wait_for_timeout(2500)
            hrefs=page.eval_on_selector_all("a[href*='/p/']","els=>els.map(e=>e.getAttribute('href'))")
            links+=["https://www.maxizoo.fr"+h if h.startswith("/") else h for h in hrefs if h and "/p/" in h]
        links=sorted(set(links))
        dbg.write(f"TOTAL liens: {len(links)}\n"); dbg.flush()
        got=0
        for i,url in enumerate(links,1):
            try:
                page.goto(url,timeout=60000,wait_until="domcontentloaded")
                page.wait_for_timeout(1200)
                # deroule TOUTES les sections repliees (clique tous les entetes/accordeons)
                for sel in ["text=/Ingr[ée]dients/i","text=/D[ée]tails du produit/i","[aria-expanded='false']","button:has-text('Ingrédients')"]:
                    try:
                        for el in page.locator(sel).all()[:8]:
                            try:
                                el.click(timeout=1000); page.wait_for_timeout(300)
                            except Exception: pass
                    except Exception: pass
                page.wait_for_timeout(800)
                body=page.inner_text("body")
                vals=extract(body)
                nom=(page.title() or "").split("|")[0].strip()
                mref=re.search(r"R[ée]f\.?\s*art\.?\s*:?\s*(\d+)",body,re.I)
                mcomp=re.search(r"Composition\s+(.{0,400}?)(?:Teneur|Additifs|Composants|$)",body,re.I|re.S)
                w.writerow([nom,mref.group(1) if mref else "",url,(mcomp.group(1).strip() if mcomp else "")]+[vals.get(f,"") for f in FIELDS])
                fout.flush()
                if vals.get("proteines"): got+=1
                if i<=8:
                    dbg.write(f"\n=== {i} ===\n{url}\nnom:{nom}\nvaleurs:{vals}\n")
                    k=re.search(r"composants analytiques|prot[eé]ines?\s*:",body,re.I)
                    dbg.write((body[max(0,k.start()-20):k.start()+300] if k else "(pas de nutrition)")+"\n"); dbg.flush()
                print(i,"OK" if vals.get("proteines") else "--")
            except Exception as e:
                print(i,"err",e)
            time.sleep(1)
        b.close()
    fout.close(); dbg.close()
    print("TERMINE. fiches:",len(links),"avec nutrition:",got)
if __name__=="__main__": main()
