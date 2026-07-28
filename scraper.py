# Telecharge 40 images produit dans le dossier /images (pour apercu)
import os, urllib.request, time
os.makedirs('images', exist_ok=True)
IMAGES = [
  ('5905342298670', 'https://media.zooplus.com/bilder/8/400/615701_pla_wiejska_zagroda_wet_dog_food_adult_500g_beef_with_duck_1000x1000_hs_01_8.jpg'),
  ('052742201108', 'https://media.zooplus.com/bilder/7/400/106011_605138_105941_pla_hill_s_science_plan_puppy_1_large_mit_huhn_hs_01_jpg_7.jpg'),
  ('8425402686683', 'https://media.zooplus.com/bilder/5/800/274594_pla_natural_greatnessdiet_vet_renaloxalate_6kg_hs_01_5.jpg'),
  ('8437023818046', 'https://media.zooplus.com/media/sms-article-assets-prod/9990052059/pictures/caa3ae6514da7dbf8f4a85da9374fd42/w800.jpg'),
  ('4062911013155', 'https://media.zooplus.com/bilder/6/400/66952_pla_concept_for_life_large_light_1_5kg_6.jpg'),
  ('4260488281087', 'https://media.zooplus.com/bilder/4/200/68445_pla_2_alpha_spirit_sc_4.jpg'),
  ('4048422152750', 'https://media.zooplus.com/bilder/2/400/330896_pla_tetra_8in1_tasties_huhn_twisters_85g_hs_01_2.jpg'),
  ('4060629100761', 'https://media.zooplus.com/media/sms-article-assets-prod/9990019756/pictures/366cb30d86778384a215d7c236787dda/w400.jpg'),
  ('4000158923622', 'https://media.zooplus.com/bilder/8/800/392702_pla_rinti_sensible_800g_lamm_kartoffel_1000x1000_hs_01_8.jpg'),
  ('4260488284514', 'https://media.zooplus.com/media/sms-article-assets-prod/9991935467/pictures/741b9a133b5d3f33f24b0b3a5ee9af6a/w800.jpg'),
  ('4062911066786', 'https://media.zooplus.com/bilder/9/400/2025_09_purizon_dog_df_original_chickenfish_senior_1kg_1000x1000_9.jpg'),
  ('4062911056701', 'https://media.zooplus.com/bilder/4/800/2024_08_rocco_dietcare_renal_chicken_150g_top_1000x1000_4.jpg'),
  ('8595602558926', 'https://media.zooplus.com/bilder/5/400/301296_pla_britcare_grainfree_adult_largebreed_lachskartoffel_12kg_hs_01_5.jpg'),
  ('4260077045335', 'https://media.zooplus.com/bilder/5/400/28011_28012_28013_28015_5.jpg'),
  ('9120100970018', 'https://media.zooplus.com/media/sms-article-assets-prod/9990005897/pictures/9f5d8638b345f955d50c67d8b5d90f70/w400.jpg'),
  ('4260697462178', 'https://media.zooplus.com/media/sms-article-assets-prod/9990084232/pictures/ba3de2a2c66fb58701a33026dc188b35/w800.jpg'),
  ('52742865201', 'https://media.zooplus.com/media/sms-article-assets-prod/9990065158/pictures/21bea8a2590e78b4d18a1d99b0a192a7/w400.jpg'),
  ('5012113002982', 'https://media.zooplus.com/media/sms-article-assets-prod/9990004963/pictures/cb101d7a6aac988b63aa4f1092c0972c/w400.jpg'),
  ('8020245017009', 'https://media.zooplus.com/bilder/3/400/542096_pla_forza10_mini_puppy_fisch_2kg_hs_02_3.jpg'),
  ('3700469697823', 'https://media.zooplus.com/media/sms-article-assets-prod/9990000601/pictures/09c1d257b3db3354b149b99e76b7bcee/w400.jpg'),
  ('4062911059474', 'https://media.zooplus.com/bilder/3/400/20435c_1_3.jpg'),
  ('4016598064207', 'https://media.zooplus.com/bilder/9/800/609309_pla_karlie_rinderkopfhaut_lose_ware_hs_01_9.jpg'),
  ('4260697462666', 'https://media.zooplus.com/media/sms-article-assets-prod/9990085489/pictures/5380f1a26066874144727443413efec8/w400.jpg'),
  ('0052742043166', 'https://media.zooplus.com/media/sms-article-assets-prod/9990065158/pictures/21bea8a2590e78b4d18a1d99b0a192a7/w400.jpg'),
  ('4260488282220', 'https://media.zooplus.com/media/sms-article-assets-prod/9991935473/pictures/eb1bbc06d98972b5c811595de5f92dcb/w800.jpg'),
  ('4262500460081', 'https://media.zooplus.com/media/sms-article-assets-prod/9990083905/pictures/1b9ed4f57c277831451f28f92c1cc755/w400.jpg'),
  ('5900951315923', 'https://media.zooplus.com/bilder/3/400/501798_pla_mars_frolic_rind_hs_01_3.jpg'),
  ('3664499000377', 'https://media.zooplus.com/media/sms-article-assets-prod/9990021103/pictures/bf9bf318ef124e8e0f2b1e3f44728d3d/w800.jpg'),
  ('3760368528529', 'https://media.zooplus.com/media/sms-article-assets-prod/9990018247/pictures/fff8dc84f28c49cf3ba40b450af6fe06/w800.jpg'),
  ('4260275024439', 'https://media.zooplus.com/bilder/4/200/527204_pla_feines_gefluegel_fleischeslust_lunch_box_8x400g_hs_01_4.jpg'),
  ('9003579008737', 'https://media.zooplus.com/bilder/0/800/94692_pla_royal_canin_ccn_sterilised_wet_0.jpg'),
  ('4262459380850', 'https://media.zooplus.com/bilder/5/400/607704_pla_george_bobs_h_hnerh_lse_5.jpg'),
  ('3182550748315', 'https://media.zooplus.com/bilder/3/400/69638_pla_rc_vet_urinary_uc_hund_14kg_3.jpg'),
  ('4260361031594', 'https://media.zooplus.com/media/sms-article-assets-prod/9990019771/pictures/a057a0f51045e28ec2e0fe2d8f69e48c/w800.jpg'),
  ('7613035114869', 'https://media.zooplus.com/bilder/8/400/07613035114869_h1n1_01_fr_44142661_8.jpg'),
  ('4000158925282', 'https://media.zooplus.com/bilder/2/400/3132_pla_rinti_kf_rind_400g_hs_01_2.jpg'),
  ('8445290975713', 'https://media.zooplus.com/bilder/1/400/500920_pla_friskies_active_dog_meat_3kg_01_500920_1000106_1.jpg'),
  ('4260488280356', 'https://media.zooplus.com/bilder/4/200/68445_pla_2_alpha_spirit_sc_4.jpg'),
  ('3760401053698', 'https://media.zooplus.com/media/sms-article-assets-prod/9990021654/pictures/72a862582ace1819efd70027eec493b4/w400.jpg'),
  ('4032326019288', 'https://media.zooplus.com/bilder/6/800/285896_pla_markusmuehle_luposan_lupo_gelenkoel_250ml_hs_01_6.jpg'),
]

ok=0; ko=0
for i,(bc,url) in enumerate(IMAGES,1):
    try:
        req=urllib.request.Request(url, headers={
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
            'Referer':'https://www.zooplus.fr/'})
        data=urllib.request.urlopen(req,timeout=30).read()
        if len(data)<800: raise ValueError('reponse vide')
        open('images/%s.jpg'%bc,'wb').write(data)
        ok+=1; print('[%d/40] OK %s (%d Ko)'%(i,bc,len(data)//1024))
    except Exception as e:
        ko+=1; print('[%d/40] ECHEC %s : %s'%(i,bc,e))
    time.sleep(0.4)
print('\nTERMINE. Images:',ok,'| echecs:',ko)
