import re, time
from playwright.sync_api import sync_playwright
URLS=[
"https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980002411",
"https://www.zooplus.fr/shop/chiens/croquettes_chien/royal_canin_veterinary_diet/reins_voies_urinaires_chien_croquettes_royal_canin/2557030",
"https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980002969",
"https://www.zooplus.fr/shop/chiens/croquettes_chien_races/races_moyennes/9980009725",
"https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980063654",
]
dbg=open("debug.txt","w",encoding="utf-8")
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    ctx=b.new_context(locale="fr-FR",user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
    page=ctx.new_page()
    consent=False
    for i,url in enumerate(URLS,1):
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
            page.wait_for_timeout(2500)
            # deroule toute la page pour declencher les chargements
            for _ in range(6):
                page.mouse.wheel(0,3000); page.wait_for_timeout(500)
            html=page.content()
            dbg.write("\n\n########## FICHE "+str(i)+" ##########\n"+url+"\n")
            # 1) montre tous les <table> de la page
            for j,t in enumerate(re.findall(r"<table.*?</table>",html,re.S)):
                txt=re.sub(r"<[^>]+>"," ",t)
                txt=re.sub(r"\s+"," ",txt).strip()
                if any(k in txt.lower() for k in ["prot","brut","cendre","humid","graisse"]):
                    dbg.write("\n[TABLE "+str(j)+"]\n"+txt[:800]+"\n")
            # 2) montre chaque endroit ou apparait un nombre suivi de %
            for m in re.finditer(r".{0,45}\d+[.,]?\d*\s*%.{0,10}",re.sub(r"<[^>]+>"," ",html)):
                s=m.group(0)
                if any(k in s.lower() for k in ["prot","brut","cendre","humid","graisse","cellulose","mati"]):
                    dbg.write("[%] "+re.sub(r'\s+',' ',s).strip()+"\n")
            dbg.flush()
            print(i,"ok")
        except Exception as e:
            print(i,"err",e)
        time.sleep(1)
    b.close()
dbg.close()
print("FINI")
