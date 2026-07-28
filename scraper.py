# UN SEUL COPIER-COLLER. Telecharge les images et les met dans debug_maxizoo.txt
# (que le workflow telecharge deja). Rien d'autre a changer.
import urllib.request, time, base64
IMAGES = [
  ('5905342298670', 'https://media.zooplus.com/bilder/8/400/615701_pla_wiejska_zagroda_wet_dog_food_adult_500g_beef_with_duck_1000x1000_hs_01_8.jpg', 'https://www.zooplus.fr/shop/chiens/boites_sachets_barquettes_chien/wiejska_zagroda/2510288'),
  ('052742201108', 'https://media.zooplus.com/bilder/7/400/106011_605138_105941_pla_hill_s_science_plan_puppy_1_large_mit_huhn_hs_01_jpg_7.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/hills_science_plan_croquettes_chien/hills_science_plan_junior_croquettes_chien/15201'),
  ('8425402686683', 'https://media.zooplus.com/bilder/5/800/274594_pla_natural_greatnessdiet_vet_renaloxalate_6kg_hs_01_5.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/natural_greatness/1746480'),
  ('8437023818046', 'https://media.zooplus.com/media/sms-article-assets-prod/9990052059/pictures/caa3ae6514da7dbf8f4a85da9374fd42/w800.jpg', 'https://www.zooplus.fr/shop/chiens/pathologies_canines/croquettes_boites_chien_sterilise_castre/9980041672'),
  ('4062911013155', 'https://media.zooplus.com/bilder/6/400/66952_pla_concept_for_life_large_light_1_5kg_6.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/concept_for_life_dogs/1971391'),
  ('4260488281087', 'https://media.zooplus.com/bilder/4/200/68445_pla_2_alpha_spirit_sc_4.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/friandises_sans_cereales_chien/9980062320'),
  ('4048422152750', 'https://media.zooplus.com/bilder/2/400/330896_pla_tetra_8in1_tasties_huhn_twisters_85g_hs_01_2.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/friandises_batonnet_chien/batonnets_enrobes/1418215'),
  ('4060629100761', 'https://media.zooplus.com/media/sms-article-assets-prod/9990019756/pictures/366cb30d86778384a215d7c236787dda/w400.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/chiens_ages/9980012265'),
  ('4000158923622', 'https://media.zooplus.com/bilder/8/800/392702_pla_rinti_sensible_800g_lamm_kartoffel_1000x1000_hs_01_8.jpg', 'https://www.zooplus.fr/shop/chiens/boites_sachets_barquettes_chien/rinti_boites_chien/rinti_boites_patee_sensible_chien/1746049'),
  ('4260488284514', 'https://media.zooplus.com/media/sms-article-assets-prod/9991935467/pictures/741b9a133b5d3f33f24b0b3a5ee9af6a/w800.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/friandises_sans_cereales_chien/9980062238'),
  ('4062911066786', 'https://media.zooplus.com/bilder/9/400/2025_09_purizon_dog_df_original_chickenfish_senior_1kg_1000x1000_9.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/croquettes_chien_purizon/purizon_senior/1013449'),
  ('4062911056701', 'https://media.zooplus.com/bilder/4/800/2024_08_rocco_dietcare_renal_chicken_150g_top_1000x1000_4.jpg', 'https://www.zooplus.fr/shop/chiens/boites_sachets_barquettes_chien/rocco_boites_chien/diet_care/2152291'),
  ('8595602558926', 'https://media.zooplus.com/bilder/5/400/301296_pla_britcare_grainfree_adult_largebreed_lachskartoffel_12kg_hs_01_5.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/brit/lots_economiques/612495'),
  ('4260077045335', 'https://media.zooplus.com/bilder/5/400/28011_28012_28013_28015_5.jpg', 'https://www.zooplus.fr/shop/chiens/boites_sachets_barquettes_chien/rocco_boites_chien/rocco_classic_boites_chien/158351'),
  ('9120100970018', 'https://media.zooplus.com/media/sms-article-assets-prod/9990005897/pictures/9f5d8638b345f955d50c67d8b5d90f70/w400.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980002969'),
  ('4260697462178', 'https://media.zooplus.com/media/sms-article-assets-prod/9990084232/pictures/ba3de2a2c66fb58701a33026dc188b35/w800.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980063654'),
  ('52742865201', 'https://media.zooplus.com/media/sms-article-assets-prod/9990065158/pictures/21bea8a2590e78b4d18a1d99b0a192a7/w400.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien_races/races_moyennes/9980009725'),
  ('5012113002982', 'https://media.zooplus.com/media/sms-article-assets-prod/9990004963/pictures/cb101d7a6aac988b63aa4f1092c0972c/w400.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/adulte/9980002411'),
  ('8020245017009', 'https://media.zooplus.com/bilder/3/400/542096_pla_forza10_mini_puppy_fisch_2kg_hs_02_3.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/forza10_croquettes_chien/forza10_maintenance_croquettes_chien/2136033'),
  ('3700469697823', 'https://media.zooplus.com/media/sms-article-assets-prod/9990000601/pictures/09c1d257b3db3354b149b99e76b7bcee/w400.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/bois_corne_sabot/9980000201'),
  ('4062911059474', 'https://media.zooplus.com/bilder/3/400/20435c_1_3.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien/rocco_croquettes/a_decouvrir/2402401'),
  ('4016598064207', 'https://media.zooplus.com/bilder/9/800/609309_pla_karlie_rinderkopfhaut_lose_ware_hs_01_9.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/karlie_friandises/2366776'),
  ('4260697462666', 'https://media.zooplus.com/media/sms-article-assets-prod/9990085489/pictures/5380f1a26066874144727443413efec8/w400.jpg', 'https://www.zooplus.fr/shop/chiens/friandises_chien/biscuit_gateau_sec_friandises_chien/9980064452'),
  ('0052742043166', 'https://media.zooplus.com/media/sms-article-assets-prod/9990065158/pictures/21bea8a2590e78b4d18a1d99b0a192a7/w400.jpg', 'https://www.zooplus.fr/shop/chiens/croquettes_chien_races/races_moyennes/9980009725'),
]

out=open('debug_maxizoo.txt','w',encoding='utf-8')
ok=0; ko=0
for i,(bc,url,ref) in enumerate(IMAGES,1):
    try:
        req=urllib.request.Request(url, headers={
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile Safari/604.1',
            'Referer': ref,
            'Accept':'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'})
        data=urllib.request.urlopen(req,timeout=30).read()
        if len(data)<800: raise ValueError('vide/bloque')
        out.write(bc+'|'+base64.b64encode(data).decode()+'\n')
        ok+=1; print('[%d/24] OK %s (%d Ko)'%(i,bc,len(data)//1024))
    except Exception as e:
        ko+=1; print('[%d/24] ECHEC %s : %s'%(i,bc,e))
    time.sleep(0.4)
out.close()
print('\nTERMINE. Images recuperees:',ok,'| echecs:',ko)
