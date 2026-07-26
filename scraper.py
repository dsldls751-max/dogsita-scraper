import csv, json, os, re, time, pathlib
DELAY=1.5
LIMIT=int(os.environ.get("TEST_LIMIT","30"))
IN,OUT,STATE,DEBUG="urls.csv","produits_nutrition.csv","state.json","debug.txt"
FIELDS=["proteines","matieres_grasses","cellulose","cendres","humidite","calcium","phosphore","sodium","omega_3","omega_6","calories"]
LABELS={"proteines":r"prot[eé]ine","matieres_grasses":r"mati[eè]res?\s+grasses","cellulose":r"cellulose","cendres":r"cendres","humidite":r"humidit[eé]","calcium":r"calcium","phosphore":r"phosphore","sodium":r"sodium","omega_3":r"om[eé]ga.?3","omega_6":r"om[eé]ga.?6","calories":r"kcal"}
def load_state():
    try: return set(json.load(open(STATE)))
    except Exception: return set()
def parse_block(txt):
    out={}
    for f,pat in LABELS.items():
        m=re.search(pat+r"[^\d%]{0,25}(\d+[.,]?\d*)\s*%",txt,re.I)
        if m: out[f]=m.group(1).replace(",",".")
    return out
def main():
    rows=list(csv.DictReader(open(IN,newline="",encoding="utf-8")))
    by_url={}
    for r in rows:
        u=(r.get("url") or "").strip(); b=(r.get("code_barre") or "").strip()
        if u: by_url.setdefault(u,[]).append(b)
    todo=[u for u in by_url if u not in load_state()]
    if LIMIT: todo=todo[:LIMIT]
    done=load_state()
    new=not pathlib.Path(OUT).exists()
    fout=open(OUT,"a",newline="",encoding="utf-8"); w=csv.writer(fout)
    if new: w.writerow(["code_barre","url"]+FIELDS)
    dbg=open(DEBUG,"w",encoding="utf-8")
    from playwright.sync_api import sync_playwright
    got=0; consent_done=False
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        page=ctx.new_page()
        for i,url in enumerate(todo,1):
            try:
                page.goto(url,timeout=60000,wait_until="domcontentloaded")
                # accepter les cookies (une fois suffit)
                if not consent_done:
                    for t in ["Tout accepter","Accepter","J'accepte","Accept all","Tout autoriser"]:
                        try:
                            btn=page.get_by_role("button",name=re.compile(t,re.I)).first
                            if btn and btn.is_visible():
                                btn.click(timeout=3000); consent_done=True; break
                        except Exception: pass
                try: page.wait_for_load_state("networkidle",timeout=15000)
                except Exception: pass
                page.wait_for_timeout(2500)
                for lab in ["Voir les constituants analytiques","constituants analytiques","Composants analytiques"]:
                    try:
                        el=page.get_by_text(re.compile(lab,re.I)).first
                        if el and el.is_visible():
                            el.click(timeout=1500); page.wait_for_timeout(1200); break
                    except Exception: pass
                body=page.inner_text("body")
                vals={}
                mi=re.search(r"constituant|analyt",body,re.I)
                if mi:
                    blk=body[max(0,mi.start()-40):mi.start()+700]
                    vals=parse_block(blk)
                if not vals.get("proteines"):
                    m=re.search(r"prot[eé]ine[s]?\s*brute[^\d%]{0,20}(\d+[.,]?\d*)\s*%",body,re.I)
                    if m: vals["proteines"]=m.group(1).replace(",",".")
                for bc in by_url[url]:
                    w.writerow([bc,url]+[vals.get(f,"") for f in FIELDS])
                fout.flush(); done.add(url); json.dump(sorted(done),open(STATE,"w"))
                if vals.get("proteines"): got+=1
                if i<=8:
                    dbg.write("\n===== FICHE "+str(i)+" =====\n"+url+"\n")
                    dbg.write("taille body: "+str(len(body))+" | contient 'protéine': "+str("prot" in body.lower())+" | 'constituant': "+str("constituant" in body.lower())+" | 'composition': "+str("composition" in body.lower())+"\n")
                    dbg.write("valeurs: "+str(vals)+"\n")
                    k=re.search(r"constituant|analyt|prot[eé]ine",body,re.I)
                    dbg.write("extrait autour nutrition:\n"+(body[max(0,k.start()-60):k.start()+600] if k else "(rien trouvé)")+"\n")
                    dbg.flush()
                print(i,"OK" if vals.get("proteines") else "--")
            except Exception as e:
                print(i,"err",e)
            time.sleep(DELAY)
        b.close()
    fout.close(); dbg.close()
    print("TERMINE avec proteines:",got,"/",len(todo))
if __name__=="__main__":
    main()
