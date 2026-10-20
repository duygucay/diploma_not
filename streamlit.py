import streamlit as st
import pandas as pd
import json
import os

# Sayfa Ayarları
st.set_page_config(page_title="Trakya Üniv. - Proje Not Sistemi", layout="wide")

DOSYA_ADI = "notlar_kayit.json"

# Öğrenci Ham Verileri
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

# Verileri Yükle / İlklendir
def verileri_yukle():
    ogrenciler = {}
    for idx, (kod, yurutucu, numara, ad) in enumerate(ogrenci_ham_verileri, start=1):
        ogrenciler[numara] = {
            "sira": idx, "kod": kod, "yurutucu": yurutucu, "ad": ad,
            "hoca1": {k: 0 for k in not_anahtarlari},
            "hoca2": {k: 0 for k in not_anahtarlari},
            "hoca3": {k: 0 for k in not_anahtarlari}
        }
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                for no in kayitli:
                    if no in ogrenciler:
                        ogrenciler[no].update(kayitli[no])
        except Exception as e:
            st.error(f"Veri yükleme hatası: {e}")
    return ogrenciler

def verileri_kaydet(ogrenciler):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(ogrenciler, f, ensure_ascii=False, indent=4)

if "ogrenciler" not in st.session_state:
    st.session_state.ogrenciler = verileri_yukle()

# Hesaplama Mantığı
def hesapla(h1, h2, h3):
    def ort_al(key):
        vals = [h1[key], h2[key], h3[key]]
        if any(str(v).upper() == "G" for v in vals): return "G", 0
        num = [float(v) for v in vals if str(v).isdigit() or isinstance(v, (int, float))]
        return (round(sum(num)/len(num)), round(sum(num)/len(num))) if num else (0, 0)

    res = {}
    s_dict = {}
    for k in not_anahtarlari:
        val, num_val = ort_al(k)
        res[k] = val
        s_dict[k] = num_val

    # Jüri hesaplama (en düşük düşme mantığı)
    j_vals = [s_dict["1_juri"], s_dict["2_juri"], s_dict["3_juri"]]
    j_vals.sort()
    j1_etkin, j2_etkin = j_vals[1], j_vals[2]

    e1, e2, fn = s_dict["1_eskiz"], s_dict["2_eskiz"], s_dict["final"]
    final_ort = round((e1 * 0.08) + (e2 * 0.08) + (j1_etkin * 0.12) + (j2_etkin * 0.12) + (fn * 0.60))

    if final_ort >= 60:
        but_ort = "Geçti"
    else:
        bt = s_dict["butunleme"]
        but_ort = round((e1 * 0.08) + (e2 * 0.08) + (j1_etkin * 0.12) + (j2_etkin * 0.12) + (bt * 0.60)) if bt > 0 else "-"

    return res, final_ort, but_ort

# Arayüz Başlığı
st.title("🎓 Trakya Üniversitesi - Proje Değerlendirme Sistemi")

tab_ana, tab_h1, tab_h2, tab_h3 = st.tabs([
    "🏠 ANA SAYFA (Genel Sonuçlar)", 
    "👤 Beste AYTİN", 
    "👤 Duygu ÇAY", 
    "👤 Damla ATİK"
])

# ANA SAYFA
with tab_ana:
    st.subheader("Genel Sonuç Tablosu")
    rows = []
    for no, v in sorted(st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]):
        r_notlar, f_ort, b_ort = hesapla(v["hoca1"], v["hoca2"], v["hoca3"])
        rows.append({
            "Sıra": v["sira"], "Ders Kodu": v["kod"], "Yürütücü": v["yurutucu"],
            "Öğrenci No": no, "Ad Soyad": v["ad"],
            "Eskiz 1": r_notlar["1_eskiz"], "Eskiz 2": r_notlar["2_eskiz"],
            "Jüri 1": r_notlar["1_juri"], "Jüri 2": r_notlar["2_juri"], "Jüri 3": r_notlar["3_juri"],
            "Final": r_notlar["final"], "Final ORT": f_ort,
            "Bütünleme": r_notlar["butunleme"], "Büt ORT": b_ort
        })
    df_ana = pd.DataFrame(rows)
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

# HOCA GİRİŞ SEKMELERİ
def hoca_ekrani(hoca_key, hoca_adi):
    st.subheader(f"{hoca_adi} - Not Giriş Paneli")
    st.info("💡 Notları tablodan doğrudan güncelleyip aşağıdaki 'Değişiklikleri Kaydet' butonuna basabilirsiniz.")
    
    list_data = []
    for no, v in sorted(st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]):
        item = {"Öğrenci No": no, "Ad Soyad": v["ad"]}
        item.update(v[hoca_key])
        list_data.append(item)
        
    df = pd.DataFrame(list_data)
    edited_df = st.data_editor(df, key=f"editor_{hoca_key}", use_container_width=True, hide_index=True)
    
    if st.button(f"💾 {hoca_adi} Notlarını Kaydet", type="primary"):
        for _, row in edited_df.iterrows():
            no = str(row["Öğrenci No"])
            for k in not_anahtarlari:
                val = row[k]
                st.session_state.ogrenciler[no][hoca_key][k] = val
        verileri_kaydet(st.session_state.ogrenciler)
        st.success("Notlar başarıyla kaydedildi!")
        st.rerun()

with tab_h1: hoca_ekrani("hoca1", "Beste AYTİN")
with tab_h2: hoca_ekrani("hoca2", "Duygu ÇAY")
with tab_h3: hoca_ekrani("hoca3", "Damla ATİK")