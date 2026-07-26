import csv, json, os, re, time, pathlib
DELAY=1.5
LIMIT=int(os.environ.get("TEST_LIMIT","30"))
IN,OUT,STATE,DEBUG="urls.csv","produits_nutrition.csv","state.json","debug.txt"
FIELDS=["proteines","matieres_grasses","cellulose","cendres","humidite","calcium","phosphore","sodium","omega_3","omega_6","calories"]
LABELS={"proteines":r"prot[eé]ine","matieres_grasses":r"mati[eè]res?\s+grasses","cellulose":r"cellulose","cendres":r"cendres","humidite":r"humidit[eé]","calcium":r"calcium","phosphore":r"phosphore","sodium":r"sodium","omega_3":r"om[eé]ga.?3","omega_6":r"om[eé]ga.?6","calories":r"kcal|[eé]nergie"}
def load_state():
    try: return set(json.load(open(STATE)))
    except Exception: return set()
def parse_block(txt):
    out={}
    for f,pat in LABELS.items():
        m=re.search(pat+r"[^\d%]{0,20}(\d+[.,]?\d*)\s*%",txt,re.I)
        if m: out[f]=m.group(1).replace(",",".")
    return out
def main():
    rows=list(csv.DictReader(open(IN,newline="",encoding="utf-8")))
    by_url={}
    for r in rows:
        u=(r.get("url") or "").strip(); b=(r.get("code_barre") or "").strip()
        if u: by_url.setdefault(u,[]).append(b)
    urls=list(by_url.keys())
    done=load_state()
    todo=[u for u in urls if u not in done]
    if LIMIT: todo=todo[:LIMIT]
    print("URLs:",len(urls),"ce run:",len(todo))
    new=not pathlib.Path(OUT).exists()
    fout=open(OUT,"a",newline="",encoding="utf-8"); w=csv.writer(fout)
    if new: w.writerow(["code_barre","url"]+FIELDS)
    dbg=open(DEBUG,"w",encoding="utf-8")
    from playwright.sync_api import sync_playwright
    got=0; blocked=0
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        page=ctx.new_page()
        for i,url in enumerate(todo,1):
            try:
                resp=page.goto(url,timeout=45000,wait_until="domcontentloaded")
                st=resp.status if resp else 0
                if st in (403,429):
                    blocked+=1; print(i,"BLOQUE",st)
                    if blocked>=3: break
                    time.sleep(10); continue
                blocked=0
                page.wait_for_timeout(1500)
                for lab in ["Voir les constituants analytiques","constituants analytiques","Analyse nutritionnelle","Composants analytiques"]:
                    try:
                        el=page.get_by_text(re.compile(lab,re.I)).first
                        if el and el.is_visible():
                            el.click(timeout=1500); page.wait_for_timeout(1000); break
                    except Exception: pass
                html=page.content(); body=page.inner_text("body")
                json_hit=""
                for m in re.finditer(r'\{[^{}]*(?:protein|analyt|constituant)[^{}]*\}',html,re.I):
                    json_hit=m.group(0)[:500]; break
                block=""
                mi=re.search(r"analyt",body,re.I)
                if mi:
                    s=max(0,mi.start()-50); block=body[s:s+700]
                vals=parse_block(block) if block else {}
                if not vals.get("proteines"):
                    m=re.search(r"prot[eé]ine[s]?\s*brute[^\d%]{0,15}(\d+[.,]?\d*)\s*%",body,re.I)
                    if m: vals["proteines"]=m.group(1).replace(",",".")
                for bc in by_url[url]:
                    w.writerow([bc,url]+[vals.get(f,"") for f in FIELDS])
                fout.flush(); done.add(url); json.dump(sorted(done),open(STATE,"w"))
                if vals.get("proteines"): got+=1
                if i<=8:
                    dbg.write("\n===== FICHE "+str(i)+" : "+url+" =====\n")
                    dbg.write("[valeurs] "+str(vals)+"\n")
                    dbg.write("[bloc analytique]\n"+block+"\n")
                    dbg.write("[json]\n"+json_hit+"\n"); dbg.flush()
                print(i,"OK" if vals.get("proteines") else "--",vals.get("proteines",""))
            except Exception as e:
                print(i,"err",e)
            time.sleep(DELAY)
        b.close()
    fout.close(); dbg.close()
    print("TERMINE. avec proteines:",got,"/",len(todo))
if __name__=="__main__":
    main()
