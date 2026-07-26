import csv, json, os, re, time, pathlib
DELAY=1.5
LIMIT=int(os.environ.get("TEST_LIMIT","30"))
IN,OUT,STATE,DEBUG="urls.csv","produits_nutrition.csv","state.json","debug.txt"
FIELDS=["proteines","matieres_grasses","cellulose","cendres","humidite","calcium","phosphore","sodium","omega_3","omega_6","calories"]
LABELS={"proteines":r"prot[eé]ines?(?:\s*brutes?)?","matieres_grasses":r"(?:mati[eè]res?\s+grasses|teneur\s+en\s+mati[eè]res\s+grasses|lipides)","cellulose":r"cellulose(?:\s*brute)?|fibres?","cendres":r"cendres(?:\s*brutes?)?","humidite":r"humidit[eé]","calcium":r"calcium","phosphore":r"phosphore","sodium":r"sodium","omega_3":r"om[eé]ga.?3","omega_6":r"om[eé]ga.?6","calories":r"kcal"}
def load_state():
    try: return set(json.load(open(STATE)))
    except Exception: return set()
def extract(body):
    out={}
    for f,pat in LABELS.items():
        # attrape "Protéines : 22 %", "protéine brute 22%", "Protéines 22 %"
        m=re.search(r"(?:"+pat+r")\s*[:=]?\s*(\d+[.,]?\d*)\s*%",body,re.I)
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
    got=0; consent=False
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        page=ctx.new_page()
        for i,url in enumerate(todo,1):
            try:
                page.goto(url,timeout=60000,wait_until="domcontentloaded")
                if not consent:
                    for t in ["Tout accepter","Accepter","J'accepte","Accept all"]:
                        try:
                            btn=page.get_by_role("button",name=re.compile(t,re.I)).first
                            if btn and btn.is_visible():
                                btn.click(timeout=3000); consent=True; break
                        except Exception: pass
                try: page.wait_for_load_state("networkidle",timeout=15000)
                except Exception: pass
                page.wait_for_timeout(2000)
                body=page.inner_text("body")
                vals=extract(body)
                for bc in by_url[url]:
                    w.writerow([bc,url]+[vals.get(f,"") for f in FIELDS])
                fout.flush(); done.add(url); json.dump(sorted(done),open(STATE,"w"))
                if vals.get("proteines"): got+=1
                if i<=8:
                    dbg.write("\n===== "+str(i)+" =====\n"+url+"\nvaleurs: "+str(vals)+"\n")
                    k=re.search(r"analyse nutritionnelle|prot[eé]ines?\s*[:=]",body,re.I)
                    dbg.write((body[max(0,k.start()-20):k.start()+400] if k else "(pas de bloc nutrition)")+"\n"); dbg.flush()
                print(i,"OK" if vals.get("proteines") else "--",vals.get("proteines",""))
            except Exception as e:
                print(i,"err",e)
            time.sleep(DELAY)
        b.close()
    fout.close(); dbg.close()
    print("TERMINE avec proteines:",got,"/",len(todo))
if __name__=="__main__":
    main()
