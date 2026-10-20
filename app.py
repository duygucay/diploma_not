import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime
import io

# --- BASİT ŞİFRE KORUMASI ---
PAROLA = "dp2026"  # İstediğiniz şifreyi buraya yazabilirsiniz

if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.title("🔒 Diploma Projesi - Giriş Paneli")
    girilen_sifre = st.text_input("Lütfen erişim şifresini giriniz:", type="password")
    if st.button("Giriş Yap"):
        if girilen_sifre == PAROLA:
            st.session_state.giris_yapildi = True
            st.success("Giriş başarılı!")
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()  # Şifre doğru girilene kadar kodun geri kalanını çalıştırmaz


# --- SAYFA VE ARAYÜZ AYARLARI ---
st.set_page_config(page_title="2026-27 Güz Dönemi Diploma Projesi Notları", layout="wide")

# --- DİNAMİK DOSYA YOLU TESPİTİ ---
CALISMA_KLASORU = os.path.dirname(os.path.abspath(__file__))
DOSYA_ADI = os.path.join(CALISMA_KLASORU, "notlar_kayit.json")
YEDEK_KLASOR = os.path.join(CALISMA_KLASORU, "yedekler")

# 1. GERÇEK ÖĞRENCİ LİSTESİ VE VERİ YAPISI
ogrenci_ham_verileri = [
    ("PEM 440", "Beste AYTİN", "1191702035", "BUSE SOFUCAN"),
    ("PEM 440", "Beste AYTİN", "1201702040", "EMİR UÇGUN"),
    ("PEM 440", "Beste AYTİN", "1201702049", "GÜLCE KARAKOÇ"),
    ("PMB 443", "Beste AYTİN", "1221702029", "ATAKAN ÇAKIR"),
    ("PMB 443", "Beste AYTİN", "1221702035", "AYŞEGÜL İLAYDA ERŞEN"),
    ("PMB 443", "Beste AYTİN", "1221702058", "EMRE AKMAN"),
    ("PMB 443", "Beste AYTİN", "1221702060", "YAREN ÇABALAR"),
    ("PMB 443", "Beste AYTİN", "1221702061", "KÜBRA YÜKSEL"),
    ("PMB 443", "Beste AYTİN", "1221702613", "AYŞE ÖZCAN"),
    ("PEM 440", "Duygu ÇAY", "1191702055", "BERİVAN DEMİR"),
    ("PEM 440", "Duygu ÇAY", "1201702043", "İREM YUNUSLAR"),
    ("PEM 440", "Duygu ÇAY", "1201702070", "BUSE YILMAZ"),
    ("PMB 443", "Duygu ÇAY", "1221702031", "SİMGE ERDEM"),
    ("PMB 443", "Duygu ÇAY", "1221702037", "ZEYNEP BAYRAM"),
    ("PMB 443", "Duygu ÇAY", "1221702039", "SEVGİ SÖZGEN"),
    ("PMB 443", "Duygu ÇAY", "1221702047", "RÜMEYSA AĞAYA"),
    ("PMB 443", "Duygu ÇAY", "1221702062", "KAAN MERT SOLAKOĞLU"),
    ("PMB 443", "Duygu ÇAY", "1221702074", "EZGİ ÇİFÇİ"),
    ("PEM 440", "Damla ATİK", "1181702029", "HALİT BUĞRA AYAZ"),
    ("PEM 440", "Damla ATİK", "1201702007", "BELİS NUR GÜNERİ"),
    ("PEM 440", "Damla ATİK", "1201702036", "DERYA DURSUN"),
    ("PMB 443", "Damla ATİK", "1211702016", "NESLİHAN ALKAN"),
    ("PMB 443", "Damla ATİK", "1211702017", "DİCLE KARAYILDIRIM"),
    ("PMB 443", "Damla ATİK", "1211702804", "GÖRKEM ŞENER"),
    ("PMB 443", "Damla ATİK", "1231702902", "DİYAR TÜSÜ"),
    ("PMB 443", "Damla ATİK", "1231702907", "KÜBRA GÜRBÜZ"),
    ("PMB 443", "Damla ATİK", "1221702016", "GAMZE ÇETİNKAYA"),
    ("PMB 443", "Damla ATİK", "1221702040", "İREM NUR AKTAŞ"),
    ("PMB 443", "Damla ATİK", "1221702053", "NİLAY AYKUT"),
    ("PMB 443", "Damla ATİK", "1221702064", "GONCA CAMCI"),
    ("PMB 443", "Damla ATİK", "1221702068", "ASYA ÇAĞLAYAN")
]

not_anahtarlari = ["1_eskiz", "2_eskiz", "1_juri", "2_juri", "3_juri", "final", "butunleme"]

# --- VERİ YÜKLEME VE İLKLENDİRME ---
def verileri_yukle():
    ogrenciler = {}
    for idx, (kod, yurutucu, numara, ad) in enumerate(ogrenci_ham_verileri, start=1):
        ogrenciler[numara] = {
            "sira": idx, "kod": kod, "yurutucu": yurutucu, "ad": ad,
            "hoca1": {k: "" for k in not_anahtarlari},
            "hoca2": {k: "" for k in not_anahtarlari},
            "hoca3": {k: "" for k in not_anahtarlari}
        }
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                kayitli_veri = json.load(dosya)
                for no in kayitli_veri:
                    if no in ogrenciler:
                        ogrenciler[no].update(kayitli_veri[no])
        except Exception:
            pass
    return ogrenciler

if 'ogrenciler' not in st.session_state:
    st.session_state.ogrenciler = verileri_yukle()

# --- GÜVENLİ VE YEDEKLEMELİ KAYIT SİSTEMİ ---
def verileri_kaydet(veri_sozlugu):
    try:
        temp_dosya = DOSYA_ADI + ".tmp"
        with open(temp_dosya, "w", encoding="utf-8") as dosya:
            json.dump(veri_sozlugu, dosya, ensure_ascii=False, indent=4)
        
        if os.path.exists(DOSYA_ADI):
            os.replace(temp_dosya, DOSYA_ADI)
        else:
            os.rename(temp_dosya, DOSYA_ADI)

        if not os.path.exists(YEDEK_KLASOR):
            os.makedirs(YEDEK_KLASOR, exist_ok=True)
            
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        yedek_adi = os.path.join(YEDEK_KLASOR, f"notlar_yedek_{zaman_damgasi}.json")
        shutil.copy2(DOSYA_ADI, yedek_adi)
        
        yedekler = sorted([os.path.join(YEDEK_KLASOR, f) for f in os.listdir(YEDEK_KLASOR)])
        if len(yedekler) > 40:
            os.remove(yedekler[0])
    except Exception as e:
        st.error(f"Kayıt veya yedekleme hatası: {e}")

# --- STRICT 0-100 VE 'G' DOĞRULAMA FONKSİYONU ---
def guvenli_float(val):
    if val is None: return ""
    s = str(val).strip().upper()
    if s in ["", "-", "NAN", "NONE", "NULL"]: return ""
    if "GEÇ" in s: return "Geçti"
    if s == "G": return "G" # 'g' yazılsa dahi 'G' yapar
    try:
        num = float(s.replace(",", "."))
        num_round = round(num)
        if 0 <= num_round <= 100:
            return num_round
        else:
            return None # 0-100 aralığı dışındaki sayılar reddedilir
    except:
        return None # Sayı veya 'G' dışında kalan tüm girdiler reddedilir

# --- HESAPLAMA MANTIĞI ---
def ana_sayfa_ortalama_hesapla(h1_notlari, h2_notlari, h3_notlari):
    str_notlar = {}
    sayisal_notlar_dict = {}
    
    for anahtar in not_anahtarlari:
        notlar = [h1_notlari[anahtar], h2_notlari[anahtar], h3_notlari[anahtar]]
        
        is_g = False
        for n in notlar:
            if str(n).strip().upper() == "G":
                is_g = True
                break
                
        if is_g:
            str_notlar[anahtar] = "G"
            sayisal_notlar_dict[anahtar] = 0
        else:
            sayisal = [float(n) for n in notlar if str(n).strip() != "" and str(n).strip().upper() != "G"]
            if not sayisal:
                str_notlar[anahtar] = ""
                sayisal_notlar_dict[anahtar] = 0
            else:
                ort = round(sum(sayisal) / len(sayisal))
                str_notlar[anahtar] = ort
                sayisal_notlar_dict[anahtar] = ort

    # Jüri Düşme
    j_vals = [("1", str_notlar["1_juri"]), ("2", str_notlar["2_juri"]), ("3", str_notlar["3_juri"])]
    sayisal_juriler = [j for j in j_vals if j[1] != "G" and j[1] != ""]
    
    if len(sayisal_juriler) >= 2:
        sayisal_juriler.sort(key=lambda x: float(x[1]))
        juri_1_etkin = float(sayisal_juriler[-2][1])
        juri_2_etkin = float(sayisal_juriler[-1][1])
    elif len(sayisal_juriler) == 1:
        juri_1_etkin = float(sayisal_juriler[0][1])
        juri_2_etkin = float(sayisal_juriler[0][1])
    else:
        juri_1_etkin, juri_2_etkin = 0, 0

    e1 = float(sayisal_notlar_dict["1_eskiz"])
    e2 = float(sayisal_notlar_dict["2_eskiz"])
    final_notu = float(sayisal_notlar_dict["final"])
    
    final_ortalama = (e1 * 0.08) + (e2 * 0.08) + (juri_1_etkin * 0.12) + (juri_2_etkin * 0.12) + (final_notu * 0.60)
    final_ort_val = round(final_ortalama)
    
    if final_ort_val >= 60:
        str_notlar["butunleme"] = "Geçti"
        but_ort_val = "Geçti"
    else:
        but_val = str_notlar["butunleme"]
        if but_val != "" and but_val != "G" and but_val != "Geçti":
            but_notu = float(sayisal_notlar_dict["butunleme"])
            but_ortalama = (e1 * 0.08) + (e2 * 0.08) + (juri_1_etkin * 0.12) + (juri_2_etkin * 0.12) + (but_notu * 0.60)
            but_ort_val = round(but_ortalama)
        else:
            but_ort_val = "-"

    return str_notlar, final_ort_val, but_ort_val

# --- EXCEL AKTARIM YARDIMCISI ---
def excel_olustur(df_ana, df_h1, df_h2, df_h3):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_ana.to_excel(writer, sheet_name='Genel Ortalama', index=False)
        df_h1.to_excel(writer, sheet_name='Beste AYTİN', index=False)
        df_h2.to_excel(writer, sheet_name='Duygu ÇAY', index=False)
        df_h3.to_excel(writer, sheet_name='Damla ATİK', index=False)
    processed_data = output.getvalue()
    return processed_data

# --- ARAYÜZ TASARIMI ---
st.title("🎓 Trakya Üniversitesi - Proje Değerlendirme Sistemi")

tab_ana, tab_hoca1, tab_hoca2, tab_hoca3 = st.tabs([
    "🏠 ANA SAYFA (Genel Sonuçlar)", 
    "👤 Beste AYTİN", 
    "👤 Duygu ÇAY", 
    "👤 Damla ATİK"
])

ana_liste = []
h1_liste, h2_liste, h3_liste = [], [], []

for no, veri in sorted(st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]):
    str_notlar, final_ort, but_ort = ana_sayfa_ortalama_hesapla(veri["hoca1"], veri["hoca2"], veri["hoca3"])
    
    j_verileri = [("1", str_notlar['1_juri']), ("2", str_notlar['2_juri']), ("3", str_notlar['3_juri'])]
    sayisal_j = [item for item in j_verileri if item[1] != "G" and item[1] != ""]
    
    en_dusuk_anahtar = None
    if sayisal_j:
        sayisal_j.sort(key=lambda x: float(x[1]))
        en_dusuk_anahtar = sayisal_j[0][0]
        
    j1_str = f"[{str_notlar['1_juri']}]" if (en_dusuk_anahtar == "1" and str_notlar['1_juri'] != "G") else str(str_notlar['1_juri'])
    j2_str = f"[{str_notlar['2_juri']}]" if (en_dusuk_anahtar == "2" and str_notlar['2_juri'] != "G") else str(str_notlar['2_juri'])
    j3_str = f"[{str_notlar['3_juri']}]" if (en_dusuk_anahtar == "3" and str_notlar['3_juri'] != "G") else str(str_notlar['3_juri'])
    
    but_hucre_degeri = "Geçti" if final_ort >= 60 else str_notlar['butunleme']
    
    ana_liste.append({
        "Sıra": veri["sira"], "Ders Kodu": veri["kod"], "Yürütücü": veri["yurutucu"], 
        "No": no, "Ad Soyad": veri["ad"], 
        "1. Eskiz": str_notlar['1_eskiz'], "2. Eskiz": str_notlar['2_eskiz'], 
        "1. jüri": j1_str, "2. jüri": j2_str, "3. jüri": j3_str, 
        "Final": str_notlar['final'], "Final ORTALAMA": final_ort, 
        "Bütünleme": but_hucre_degeri, "Büt ORTALAMA": but_ort
    })

df_ana = pd.DataFrame(ana_liste)

with tab_ana:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("")
    with col2:
        st.info("💡 Tablodaki başlıklara tıklayarak verileri sıralayabilirsiniz.")
        
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

# OTOMATİK KAYITLI & SIKI DOĞRULAMALI HOCA SEKMESİ
def hoca_sekmesi_olustur(hoca_kodu, hoca_adi, hedef_liste):
    st.markdown(f"### 🔍 {hoca_adi} Not Giriş Ekranı")
    st.caption("⚡ Sadece **0-100** arası notlar veya **'G'** / **'g'** harfi kabul edilir. Notlar anında kaydedilir.")
    
    arama_metni = st.text_input("Öğrenci Ara (İsim veya No):", key=f"arama_{hoca_kodu}").lower()
    
    gosterilecek_veriler = []
    for no, veri in sorted(st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]):
        notlar = veri[hoca_kodu]
        _, final_ort_kontrol, but_ort_kontrol = ana_sayfa_ortalama_hesapla(veri["hoca1"], veri["hoca2"], veri["hoca3"])
        
        gosterilecek_but = "Geçti" if (final_ort_kontrol >= 60 or but_ort_kontrol == "Geçti") else notlar["butunleme"]
        
        satir = {
            "Sıra": veri["sira"], "Ders Kodu": veri["kod"], "Yürütücü": veri["yurutucu"], 
            "No": no, "Ad Soyad": veri["ad"],
            "1. Eskiz": str(notlar["1_eskiz"]), "2. Eskiz": str(notlar["2_eskiz"]), 
            "1. Jüri": str(notlar["1_juri"]), "2. Jüri": str(notlar["2_juri"]), "3. Jüri": str(notlar["3_juri"]), 
            "Final": str(notlar["final"]), "Bütünleme": str(gosterilecek_but)
        }
        hedef_liste.append(satir)
        
        if arama_metni in veri["ad"].lower() or arama_metni in str(no):
            gosterilecek_veriler.append(satir)
            
    df_hoca = pd.DataFrame(gosterilecek_veriler)
    kilitli_sutunlar = ["Sıra", "Ders Kodu", "Yürütücü", "No", "Ad Soyad"]
    
    duzenlenen_df = st.data_editor(
        df_hoca,
        use_container_width=True,
        hide_index=True,
        disabled=kilitli_sutunlar,
        key=f"editor_{hoca_kodu}"
    )
    
    sutun_haritasi = [
        ("1. Eskiz", "1_eskiz"), ("2. Eskiz", "2_eskiz"), 
        ("1. Jüri", "1_juri"), ("2. Jüri", "2_juri"), ("3. Jüri", "3_juri"), 
        ("Final", "final"), ("Bütünleme", "butunleme")
    ]
    
    degisiklik_var_mi = False
    hata_mesaji = None
    
    for index, row in duzenlenen_df.iterrows():
        ogr_no = str(row["No"])
        for sutun_adi, k in sutun_haritasi:
            ham_val = row[sutun_adi]
            islenmis_deger = guvenli_float(ham_val)
            
            if islenmis_deger == "Geçti": 
                continue
                
            # Eğer 0-100 dışı sayı veya geçersiz karakter girildiyse reddet
            if islenmis_deger is None:
                hata_mesaji = f"❌ **{row['Ad Soyad']}** öğrencisinin **{sutun_adi}** sütununa girilen **'{ham_val}'** değeri geçersizdir! Lütfen sadece **0-100** arası bir not veya **'G'** harfi giriniz."
                break
                
            eski_deger = st.session_state.ogrenciler[ogr_no][hoca_kodu][k]
            if islenmis_deger != eski_deger:
                st.session_state.ogrenciler[ogr_no][hoca_kodu][k] = islenmis_deger
                degisiklik_var_mi = True
                
        if hata_mesaji:
            break
            
    if hata_mesaji:
        st.error(hata_mesaji)
    elif degisiklik_var_mi:
        verileri_kaydet(st.session_state.ogrenciler)
        st.toast("⚡ Değişiklikler anında otomatik kaydedildi!", icon="✅")
        st.rerun()

with tab_hoca1: hoca_sekmesi_olustur("hoca1", "Beste AYTİN", h1_liste)
with tab_hoca2: hoca_sekmesi_olustur("hoca2", "Duygu ÇAY", h2_liste)
with tab_hoca3: hoca_sekmesi_olustur("hoca3", "Damla ATİK", h3_liste)

df_h1 = pd.DataFrame(h1_liste)
df_h2 = pd.DataFrame(h2_liste)
df_h3 = pd.DataFrame(h3_liste)

with tab_ana:
    excel_verisi = excel_olustur(df_ana, df_h1, df_h2, df_h3)
    st.download_button(
        label="📥 Tüm Tabloları Excel Olarak İndir",
        data=excel_verisi,
        file_name=f"Proje_Notlari_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
