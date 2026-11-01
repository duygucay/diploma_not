import io
import json
from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# --- SAYFA VE ARAYÜZ AYARLARI ---
st.set_page_config(
    page_title="2026-2027 Güz Dönemi - Diploma Projesi Not Sistemi",
    layout="wide",
)

# --- GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. GERÇEK ÖĞRENCİ LİSTESİ (TÜM ÖĞRENCİLER)
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
    ("PMB 443", "Damla ATİK", "1221702068", "ASYA ÇAĞLAYAN"),
]

not_anahtarlari = [
    "1_eskiz",
    "2_eskiz",
    "1_juri",
    "2_juri",
    "3_juri",
    "final",
    "butunleme",
]
sinav_etiketleri = {
    "1_eskiz": "1. Eskiz",
    "2_eskiz": "2. Eskiz",
    "1_juri": "1. Jüri",
    "2_juri": "2. Jüri",
    "3_juri": "3. Jüri",
    "final": "Final",
    "butunleme": "Bütünleme",
}


def tr_lower(text):
  if not text:
    return ""
  return str(text).replace("İ", "i").replace("I", "ı").lower()


# --- GOOGLE SHEETS İLE VERİ VE BAREM OKUMA ---
def verileri_sheets_oku():
  ogrenciler = {}
  baremler = {}
  try:
    df = conn.read(ttl=0)
    if not df.empty and "No" in df.columns:
      for _, row in df.iterrows():
        no = str(row["No"])
        barem_detay_str = (
            str(row.get("barem_detaylari", "{}"))
            if pd.notna(row.get("barem_detaylari"))
            else "{}"
        )
        try:
          b_detay = json.loads(barem_detay_str)
        except Exception:
          b_detay = {}

        ogrenciler[no] = {
            "sira": int(row["Sira"]),
            "kod": str(row["Ders Kodu"]),
            "yurutucu": str(row["Yurutucu"]),
            "ad": str(row["Ad Soyad"]),
            "hoca1": {
                k: str(row.get(f"h1_{k}", ""))
                if pd.notna(row.get(f"h1_{k}"))
                else ""
                for k in not_anahtarlari
            },
            "hoca2": {
                k: str(row.get(f"h2_{k}", ""))
                if pd.notna(row.get(f"h2_{k}"))
                else ""
                for k in not_anahtarlari
            },
            "hoca3": {
                k: str(row.get(f"h3_{k}", ""))
                if pd.notna(row.get(f"h3_{k}"))
                else ""
                for k in not_anahtarlari
            },
            "barem_detaylari": b_detay,
        }

      baremler_str = (
          str(df.iloc[0].get("global_baremler", "{}"))
          if "global_baremler" in df.columns
          and pd.notna(df.iloc[0].get("global_baremler"))
          else "{}"
      )
      try:
        baremler = json.loads(baremler_str)
        if any(k in baremler for k in ["hoca1", "hoca2", "hoca3"]):
          duzeltilmis = {}
          for hk in ["hoca1", "hoca2", "hoca3"]:
            if hk in baremler and isinstance(baremler[hk], dict):
              for sk, kl in baremler[hk].items():
                if sk not in duzeltilmis and kl:
                  duzeltilmis[sk] = kl
          baremler = duzeltilmis
      except Exception:
        baremler = {}
      return ogrenciler, baremler
  except Exception:
    pass

  for idx, (kod, yurutucu, numara, ad) in enumerate(
      ogrenci_ham_verileri, start=1
  ):
    ogrenciler[numara] = {
        "sira": idx,
        "kod": kod,
        "yurutucu": yurutucu,
        "ad": ad,
        "hoca1": {k: "" for k in not_anahtarlari},
        "hoca2": {k: "" for k in not_anahtarlari},
        "hoca3": {k: "" for k in not_anahtarlari},
        "barem_detaylari": {},
    }
  return ogrenciler, baremler


# --- GOOGLE SHEETS'E VERİ VE BAREM KAYDETME ---
def verileri_sheets_kaydet(veri_sozlugu, barem_sozlugu):
  rows = []
  global_baremlari_json = json.dumps(barem_sozlugu, ensure_ascii=False)

  for no, v in sorted(veri_sozlugu.items(), key=lambda x: x[1]["sira"]):
    row = {
        "Sira": v["sira"],
        "Ders Kodu": v["kod"],
        "Yurutucu": v["yurutucu"],
        "No": str(no),
        "Ad Soyad": v["ad"],
        "barem_detaylari": json.dumps(
            v.get("barem_detaylari", {}), ensure_ascii=False
        ),
        "global_baremler": global_baremlari_json,
    }
    for k in not_anahtarlari:
      row[f"h1_{k}"] = str(v["hoca1"][k])
      row[f"h2_{k}"] = str(v["hoca2"][k])
      row[f"h3_{k}"] = str(v["hoca3"][k])
    rows.append(row)

  df_kayit = pd.DataFrame(rows)
  conn.update(data=df_kayit)


if "ogrenciler" not in st.session_state or "baremler" not in st.session_state:
  st.session_state.ogrenciler, st.session_state.baremler = (
      verileri_sheets_oku()
  )

if "aktif_barem" not in st.session_state:
  st.session_state.aktif_barem = None


def guvenli_float(val):
  if val is None:
    return ""
  s = str(val).strip().upper()
  if s in ["", "-", "NAN", "NONE", "NULL"]:
    return ""
  if "GEÇ" in s:
    return "Geçti"
  if s == "G":
    return "G"
  try:
    num = float(s.replace(",", "."))
    num_round = round(num)
    if 0 <= num_round <= 100:
      return num_round
    else:
      return None
  except Exception:
    return None


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
      sayisal = [
          float(n)
          for n in notlar
          if str(n).strip() != "" and str(n).strip().upper() != "G"
      ]
      if not sayisal:
        str_notlar[anahtar] = ""
        sayisal_notlar_dict[anahtar] = 0
      else:
        ort = round(sum(sayisal) / len(sayisal))
        str_notlar[anahtar] = ort
        sayisal_notlar_dict[anahtar] = ort

  j_vals = [
      ("1", str_notlar["1_juri"]),
      ("2", str_notlar["2_juri"]),
      ("3", str_notlar["3_juri"]),
  ]
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

  final_ortalama = (
      (e1 * 0.08)
      + (e2 * 0.08)
      + (juri_1_etkin * 0.12)
      + (juri_2_etkin * 0.12)
      + (final_notu * 0.60)
  )
  final_ort_val = round(final_ortalama)

  if final_ort_val >= 60:
    str_notlar["butunleme"] = "Geçti"
    but_ort_val = "Geçti"
  else:
    but_val = str_notlar["butunleme"]
    if but_val != "" and but_val != "G" and but_val != "Geçti":
      but_notu = float(sayisal_notlar_dict["butunleme"])
      but_ortalama = (
          (e1 * 0.08)
          + (e2 * 0.08)
          + (juri_1_etkin * 0.12)
          + (juri_2_etkin * 0.12)
          + (but_notu * 0.60)
      )
      but_ort_val = round(but_ortalama)
    else:
      but_ort_val = "-"

  return str_notlar, final_ort_val, but_ort_val


def excel_olustur(df_ana, df_h1, df_h2, df_h3):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_ana.to_excel(writer, sheet_name="Genel Ortalama", index=False)
    df_h1.to_excel(writer, sheet_name="Beste AYTİN", index=False)
    df_h2.to_excel(writer, sheet_name="Duygu ÇAY", index=False)
    df_h3.to_excel(writer, sheet_name="Damla ATİK", index=False)
  processed_data = output.getvalue()
  return processed_data


# --- STREAMLIT AÇILIR BAREM MODAL PENCERESİ ---
@st.dialog("📋 Detaylı Barem ve Not Giriş Ekranı", width="large")
def barem_dialog_goster(hoca_kodu, hoca_adi, sinav_key):
  st.markdown(
      """
        <style>
        div[data-testid="stDialog"] button[kind="primary"] {
            background-color: #27ae60 !important;
            color: white !important;
            border-color: #27ae60 !important;
            padding: 6px 20px !important;
            font-weight: bold !important;
            font-size: 15px !important;
        }
        div[data-testid="stDialog"] button[kind="primary"]:hover {
            background-color: #219150 !important;
            border-color: #219150 !important;
        }
        </style>
    """,
      unsafe_allow_html=True,
  )

  sinav_adi = sinav_etiketleri[sinav_key]
  st.markdown(f"#### 👤 {hoca_adi} — 📝 **{sinav_adi}** Sınav Baremi")

  if sinav_key not in st.session_state.baremler:
    st.session_state.baremler[sinav_key] = []

  kriter_listesi = st.session_state.baremler[sinav_key]
  is_expanded = not bool(kriter_listesi)

  with st.expander(
      "⚙️ Barem Kriterlerini Tanımla / Düzenle (Tıklayarak Aç/Kapat)",
      expanded=is_expanded,
  ):
    st.caption(
        "Aşağıdaki tablodan mevcut kriterlerin adını ve max puanını"
        " değiştirebilir, en alt satırdan yeni kriter ekleyebilirsiniz:"
    )

    if kriter_listesi:
      df_kriter_init = pd.DataFrame(kriter_listesi).rename(
          columns={"ad": "Kriter Adı", "max": "Max Puan"}
      )
    else:
      df_kriter_init = pd.DataFrame(columns=["Kriter Adı", "Max Puan"])

    edited_kriter_df = st.data_editor(
        df_kriter_init,
        num_rows="dynamic",
        use_container_width=True,
        key=f"kriter_tablo_editor_{sinav_key}",
        column_config={
            "Kriter Adı": st.column_config.TextColumn(
                "Kriter Adı", required=True
            ),
            "Max Puan": st.column_config.NumberColumn(
                "Max Puan", min_value=1, max_value=100, step=1, required=True
            ),
        },
    )

    guncel_kriterler = []
    mevcut_toplam = 0
    for _, r in edited_kriter_df.iterrows():
      k_ad = str(r["Kriter Adı"]).strip() if pd.notna(r["Kriter Adı"]) else ""
      try:
        k_max = (
            int(round(float(r["Max Puan"]))) if pd.notna(r["Max Puan"]) else 0
        )
      except Exception:
        k_max = 0
      if k_ad and k_max > 0:
        guncel_kriterler.append({"ad": k_ad, "max": k_max})
        mevcut_toplam += k_max

    st.session_state.baremler[sinav_key] = guncel_kriterler

  guncel_kriterler = st.session_state.baremler[sinav_key]
  mevcut_toplam = sum(int(k["max"]) for k in guncel_kriterler)

  top_save_container = st.container()

  if mevcut_toplam > 100:
    st.error(
        f"⚠️ **Barem Toplamı 100'ü Aşıyor!** (Mevcut: `{mevcut_toplam}` / 100)."
        " Lütfen kriter puanlarını düzenleyin."
    )
  else:
    st.info(f"💡 **Mevcut Barem Toplamı:** `{mevcut_toplam} / 100` puan.")

  st.markdown("##### 📝 Öğrenci Barem Notları Girişi")

  barem_msg_container = st.container()

  arama_barem_raw = st.text_input(
      "🔍 Öğrenci Ara (İsim veya No):",
      key=f"arama_barem_{hoca_kodu}_{sinav_key}",
  )
  arama_barem_metni = tr_lower(arama_barem_raw)

  # Editor canlı yapılan son hücre değişikliklerini okur
  editor_key = f"editor_barem_notlar_{hoca_kodu}_{sinav_key}"
  edited_changes = {}
  if editor_key in st.session_state:
    edited_changes = st.session_state[editor_key].get("edited_rows", {})

  barem_rows = []
  for idx_row, (no, v) in enumerate(
      sorted(st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"])
  ):
    if (
        arama_barem_metni
        and (arama_barem_metni not in tr_lower(v["ad"]))
        and (arama_barem_metni not in str(no))
    ):
      continue

    b_detay = (
        v.get("barem_detaylari", {}).get(hoca_kodu, {}).get(sinav_key, {})
    )
    mevcut_sınav_notu = (
        str(v.get(hoca_kodu, {}).get(sinav_key, "")).strip().upper()
    )

    row_edits = edited_changes.get(idx_row, {})

    row = {
        "Sıra": v["sira"],
        "Ders Kodu": v["kod"],
        "Yürütücü": v["yurutucu"],
        "No": no,
        "Ad Soyad": v["ad"],
    }
    satir_toplam = 0
    has_g = (
        mevcut_sınav_notu == "G"
        or str(row_edits.get("TOPLAM", "")).strip().upper() == "G"
    )

    for k in guncel_kriterler:
      col_name = f"{k['ad']} ({k['max']}p)"
      b_val = row_edits.get(col_name, b_detay.get(k["ad"], "-"))
      s_bval = str(b_val).strip().upper() if b_val is not None else "-"

      if s_bval == "G":
        val_display = "G"
        has_g = True
      elif b_val is None or s_bval in ["", "-", "NONE", "NAN"]:
        val_display = "-"
      else:
        try:
          val_puan = int(round(float(str(b_val).replace(",", "."))))
          val_display = str(val_puan)
          satir_toplam += val_puan
        except Exception:
          val_display = "-"

      row[col_name] = val_display

    row["TOPLAM"] = "G" if has_g else (satir_toplam if satir_toplam > 0 else "-")
    barem_rows.append(row)

  if barem_rows and guncel_kriterler:
    df_barem = pd.DataFrame(barem_rows)
    disabled_cols = ["Sıra", "Ders Kodu", "Yürütücü", "No", "Ad Soyad"]

    column_config_barem = {
        "TOPLAM": st.column_config.TextColumn(
            label="TOPLAM",
            help=(
                "Toplam not. Buraya 'G' (Girmedi) veya toplam puan yazabilirsiniz."
            ),
        )
    }
    for k in guncel_kriterler:
      col_name = f"{k['ad']} ({k['max']}p)"
      column_config_barem[col_name] = st.column_config.TextColumn(
          label=col_name,
          help=(
              f"Bu kriter için maksimum limit: {k['max']} puan. Sayı, 'G' veya"
              " '-' girebilirsiniz."
          ),
      )

    # Gri Satır Vurgulama Fonksiyonu
    def highlight_g_rows(row):
      is_g = any(str(val).strip().upper() == "G" for val in row.values)
      if is_g:
        return [
            "background-color: #d3d3d3; color: #333333; font-weight: bold"
        ] * len(row)
      return [""] * len(row)

    try:
      styled_df = df_barem.style.apply(highlight_g_rows, axis=1)
      duzenlenen_barem_df = st.data_editor(
          styled_df,
          use_container_width=True,
          hide_index=True,
          disabled=disabled_cols,
          column_config=column_config_barem,
          key=editor_key,
          height=350,
      )
    except Exception:
      duzenlenen_barem_df = st.data_editor(
          df_barem,
          use_container_width=True,
          hide_index=True,
          disabled=disabled_cols,
          column_config=column_config_barem,
          key=editor_key,
          height=350,
      )

    # --- YEŞİL KAYDET BUTONU YERLEŞTİRME VE KAYDETME MANTIĞI ---
    with top_save_container:
      kaydet_tiklandi = st.button(
          "💾 Barem Notlarını Kaydet ve Hoca Sayfasına Aktar",
          type="primary",
          use_container_width=True,
          key=f"btn_barem_save_top_{sinav_key}",
      )

    if kaydet_tiklandi:
      if mevcut_toplam > 100:
        barem_msg_container.error(
            f"❌ Barem kriter toplamı ({mevcut_toplam}) 100 puanı aştığı için"
            " kaydedilemez!"
        )
      else:
        hatali_girisler = []

        # Kontrol: Limit aşımı var mı veya geçersiz bir metin girilmiş mi?
        for _, row in duzenlenen_barem_df.iterrows():
          ogr_ad = row["Ad Soyad"]

          toplam_val_str = (
              str(row.get("TOPLAM", "")).strip().upper()
              if pd.notna(row.get("TOPLAM"))
              else ""
          )
          if toplam_val_str and toplam_val_str not in ["G", "-", ""]:
            try:
              t_num = float(toplam_val_str.replace(",", "."))
              if t_num < 0 or t_num > 100:
                hatali_girisler.append(
                    f"• **{ogr_ad}** — **TOPLAM** notu `{toplam_val_str}` olamaz!"
                    " (0-100 veya 'G' girilebilir)"
                )
            except Exception:
              hatali_girisler.append(
                  f"• **{ogr_ad}** — **TOPLAM** sütununa girilen"
                  f" `{toplam_val_str}` değeri geçersizdir! (Sadece sayı, `G` veya"
                  " `-` girilebilir)"
              )

          for k in guncel_kriterler:
            col_name = f"{k['ad']} ({k['max']}p)"
            val = row.get(col_name, "-")
            s_val = str(val).strip().upper() if pd.notna(val) else "-"

            if s_val in ["", "-", "NONE", "NULL", "G"]:
              continue

            try:
              val_num = float(s_val.replace(",", "."))
              val_int = round(val_num)
              if val_int > k["max"]:
                hatali_girisler.append(
                    f"• **{ogr_ad}** — **{k['ad']}** kriterine `{val_int}` puan"
                    f" yazamazsınız! (Maksimum limit: **{k['max']}** puan)"
                )
              elif val_int < 0:
                hatali_girisler.append(
                    f"• **{ogr_ad}** — **{k['ad']}** kriteri: Negatif puan"
                    f" (`{val_int}`) girilemez!"
                )
            except Exception:
              hatali_girisler.append(
                  f"• **{ogr_ad}** — **{k['ad']}** kriterine girilen `{s_val}`"
                  " değeri geçersizdir! (Sadece sayı, `G` veya `-` girilebilir)"
              )

        if hatali_girisler:
          barem_msg_container.error(
              "⛔ **HATALI NOT GİRİŞİ! Kayıt işlemi yapılmadı:**\n\n"
              + "\n".join(hatali_girisler)
          )
        else:
          # Hata yoksa Hoca Sayfası ve Google Sheets'e kaydet
          for _, row in duzenlenen_barem_df.iterrows():
            ogr_no = str(row["No"])
            calc_toplam = 0
            is_g_student = False

            toplam_cell_val = (
                str(row.get("TOPLAM", "")).strip().upper()
                if pd.notna(row.get("TOPLAM"))
                else ""
            )
            if toplam_cell_val == "G":
              is_g_student = True

            if "barem_detaylari" not in st.session_state.ogrenciler[ogr_no]:
              st.session_state.ogrenciler[ogr_no]["barem_detaylari"] = {}
            if (
                hoca_kodu
                not in st.session_state.ogrenciler[ogr_no]["barem_detaylari"]
            ):
              st.session_state.ogrenciler[ogr_no]["barem_detaylari"][
                  hoca_kodu
              ] = {}
            if (
                sinav_key
                not in st.session_state.ogrenciler[ogr_no]["barem_detaylari"][
                    hoca_kodu
                ]
            ):
              st.session_state.ogrenciler[ogr_no]["barem_detaylari"][hoca_kodu][
                  sinav_key
              ] = {}

            for k in guncel_kriterler:
              col_name = f"{k['ad']} ({k['max']}p)"
              val = row.get(col_name, "-")
              s_val = str(val).strip() if pd.notna(val) else "-"
              s_val_upper = s_val.upper()

              if s_val_upper == "G":
                st.session_state.ogrenciler[ogr_no]["barem_detaylari"][
                    hoca_kodu
                ][sinav_key][k["ad"]] = "G"
                is_g_student = True
              elif s_val in ["", "-", "NONE", "NULL"]:
                st.session_state.ogrenciler[ogr_no]["barem_detaylari"][
                    hoca_kodu
                ][sinav_key][k["ad"]] = "-"
              else:
                val_int = round(float(s_val.replace(",", ".")))
                st.session_state.ogrenciler[ogr_no]["barem_detaylari"][
                    hoca_kodu
                ][sinav_key][k["ad"]] = val_int
                calc_toplam += val_int

            if is_g_student:
              final_sınav_notu = "G"
            elif (
                toplam_cell_val
                and toplam_cell_val != "-"
                and toplam_cell_val != "G"
            ):
              try:
                final_sınav_notu = round(
                    float(toplam_cell_val.replace(",", "."))
                )
              except Exception:
                final_sınav_notu = calc_toplam
            else:
              final_sınav_notu = calc_toplam

            st.session_state.ogrenciler[ogr_no][hoca_kodu][
                sinav_key
            ] = final_sınav_notu

          verileri_sheets_kaydet(
              st.session_state.ogrenciler, st.session_state.baremler
          )
          st.toast(
              f"✅ {sinav_adi} barem notları başarıyla hoca sayfasına aktarıldı!",
              icon="⚡",
          )
          st.session_state.aktif_barem = None
          st.rerun()

  elif not guncel_kriterler:
    st.warning(
        "Henüz herhangi bir barem kriteri tanımlanmadı. Yukarıdaki akordeon"
        " başlığına tıklayıp ilk kriterinizi ekleyin."
    )
  elif not barem_rows:
    st.info("Aramanıza uygun öğrenci bulunamadı.")


# --- ARAYÜZ TASARIMI ---
st.title("🎓 2026-2027 Güz Dönemi - Diploma Projesi Not Sistemi")

tab_ana, tab_hoca1, tab_hoca2, tab_hoca3 = st.tabs([
    "🏠 ANA SAYFA (Genel Sonuçlar)",
    "👤 Beste AYTİN",
    "👤 Duygu ÇAY",
    "👤 Damla ATİK",
])

ana_liste = []
h1_liste, h2_liste, h3_liste = [], [], []

for no, veri in sorted(
    st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]
):
  str_notlar, final_ort, but_ort = ana_sayfa_ortalama_hesapla(
      veri["hoca1"], veri["hoca2"], veri["hoca3"]
  )

  j_verileri = [
      ("1", str_notlar["1_juri"]),
      ("2", str_notlar["2_juri"]),
      ("3", str_notlar["3_juri"]),
  ]
  sayisal_j = [item for item in j_verileri if item[1] != "G" and item[1] != ""]

  en_dusuk_anahtar = None
  if sayisal_j:
    sayisal_j.sort(key=lambda x: float(x[1]))
    en_dusuk_anahtar = sayisal_j[0][0]

  j1_str = (
      f"[{str_notlar['1_juri']}]"
      if (en_dusuk_anahtar == "1" and str_notlar["1_juri"] != "G")
      else str(str_notlar["1_juri"])
  )
  j2_str = (
      f"[{str_notlar['2_juri']}]"
      if (en_dusuk_anahtar == "2" and str_notlar["2_juri"] != "G")
      else str(str_notlar["2_juri"])
  )
  j3_str = (
      f"[{str_notlar['3_juri']}]"
      if (en_dusuk_anahtar == "3" and str_notlar["3_juri"] != "G")
      else str(str_notlar["3_juri"])
  )

  but_hucre_degeri = "Geçti" if final_ort >= 60 else str_notlar["butunleme"]

  ana_liste.append({
      "Sıra": veri["sira"],
      "Ders Kodu": veri["kod"],
      "Yürütücü": veri["yurutucu"],
      "No": no,
      "Ad Soyad": veri["ad"],
      "1. Eskiz": str_notlar["1_eskiz"],
      "2. Eskiz": str_notlar["2_eskiz"],
      "1. jüri": j1_str,
      "2. jüri": j2_str,
      "3. jüri": j3_str,
      "Final": str_notlar["final"],
      "Final ORTALAMA": final_ort,
      "Bütünleme": but_hucre_degeri,
      "Büt ORTALAMA": but_ort,
  })

df_ana = pd.DataFrame(ana_liste)

with tab_ana:
  col1, col2 = st.columns([1, 4])
  with col1:
    st.write("")
  with col2:
    st.info("💡 Tablodaki başlıklara tıklayarak verileri sıralayabilirsiniz.")

  sabit_yukseklik = (len(df_ana) + 1) * 35 + 20
  st.dataframe(
      df_ana, use_container_width=True, hide_index=True, height=sabit_yukseklik
  )


# HOCA SEKMESİ OLUŞTURUCU
def hoca_sekmesi_olustur(hoca_kodu, hoca_adi, hedef_liste):
  st.markdown(f"### 🔍 {hoca_adi} Not Giriş Ekranı")

  st.write("📝 **Detaylı Barem Not Girişi Aç:**")
  b_cols = st.columns(6)
  for idx, skey in enumerate(
      ["1_eskiz", "2_eskiz", "1_juri", "2_juri", "3_juri", "final"]
  ):
    with b_cols[idx]:
      if st.button(
          f"📋 {sinav_etiketleri[skey]}",
          key=f"btn_barem_{hoca_kodu}_{skey}",
          use_container_width=True,
      ):
        st.session_state.aktif_barem = (hoca_kodu, hoca_adi, skey)

  st.caption(
      "⚡ Sadece **0-100** arası tam sayı notlar veya **'G'** harfi kabul edilir."
      " Notlar anında Google E-Tablonuza kaydedilir."
  )

  hoca_msg_container = st.container()

  arama_raw = st.text_input(
      "Öğrenci Ara (İsim veya No):", key=f"arama_{hoca_kodu}"
  )
  arama_metni = tr_lower(arama_raw)

  if arama_raw:
    st.session_state.aktif_barem = None

  gosterilecek_veriler = []
  for no, veri in sorted(
      st.session_state.ogrenciler.items(), key=lambda x: x[1]["sira"]
  ):
    notlar = veri[hoca_kodu]
    _, final_ort_kontrol, but_ort_kontrol = ana_sayfa_ortalama_hesapla(
        veri["hoca1"], veri["hoca2"], veri["hoca3"]
    )

    gosterilecek_but = (
        "Geçti"
        if (final_ort_kontrol >= 60 or but_ort_kontrol == "Geçti")
        else notlar["butunleme"]
    )

    satir = {
        "Sıra": veri["sira"],
        "Ders Kodu": veri["kod"],
        "Yürütücü": veri["yurutucu"],
        "No": no,
        "Ad Soyad": veri["ad"],
        "1. Eskiz": str(notlar["1_eskiz"]),
        "2. Eskiz": str(notlar["2_eskiz"]),
        "1. Jüri": str(notlar["1_juri"]),
        "2. Jüri": str(notlar["2_juri"]),
        "3. Jüri": str(notlar["3_juri"]),
        "Final": str(notlar["final"]),
        "Bütünleme": str(gosterilecek_but),
    }
    hedef_liste.append(satir)

    if (
        not arama_metni
        or arama_metni in tr_lower(veri["ad"])
        or arama_metni in str(no)
    ):
      gosterilecek_veriler.append(satir)

  sutunlar_listesi = [
      "Sıra",
      "Ders Kodu",
      "Yürütücü",
      "No",
      "Ad Soyad",
      "1. Eskiz",
      "2. Eskiz",
      "1. Jüri",
      "2. Jüri",
      "3. Jüri",
      "Final",
      "Bütünleme",
  ]
  if gosterilecek_veriler:
    df_hoca = pd.DataFrame(gosterilecek_veriler)
  else:
    df_hoca = pd.DataFrame(columns=sutunlar_listesi)

  kilitli_sutunlar = ["Sıra", "Ders Kodu", "Yürütücü", "No", "Ad Soyad"]
  tablo_yuksekligi = (len(df_hoca) + 1) * 35 + 20

  editor_key = f"editor_{hoca_kodu}"
  if editor_key in st.session_state and st.session_state[editor_key].get(
      "edited_rows"
  ):
    st.session_state.aktif_barem = None

  duzenlenen_df = st.data_editor(
      df_hoca,
      use_container_width=True,
      hide_index=True,
      disabled=kilitli_sutunlar,
      key=editor_key,
      height=tablo_yuksekligi,
  )

  sutun_haritasi = [
      ("1. Eskiz", "1_eskiz"),
      ("2. Eskiz", "2_eskiz"),
      ("1. Jüri", "1_juri"),
      ("2. Jüri", "2_juri"),
      ("3. Jüri", "3_juri"),
      ("Final", "final"),
      ("Bütünleme", "butunleme"),
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

      if islenmis_deger is None:
        hata_mesaji = (
            f"❌ **{row['Ad Soyad']}** öğrencisinin **{sutun_adi}** sütununa"
            f" girilen **'{ham_val}'** değeri geçersizdir! Lütfen sadece **0-100**"
            " arası bir not veya **'G'** harfi giriniz."
        )
        break

      eski_deger = st.session_state.ogrenciler[ogr_no][hoca_kodu][k]
      if islenmis_deger != eski_deger:
        st.session_state.ogrenciler[ogr_no][hoca_kodu][k] = islenmis_deger
        degisiklik_var_mi = True

    if hata_mesaji:
      break

  if hata_mesaji:
    hoca_msg_container.error(hata_mesaji)
  elif degisiklik_var_mi:
    verileri_sheets_kaydet(
        st.session_state.ogrenciler, st.session_state.baremler
    )
    st.toast("⚡ Değişiklikler Google Sheets'e anında kaydedildi!", icon="✅")


with tab_hoca1:
  hoca_sekmesi_olustur("hoca1", "Beste AYTİN", h1_liste)
with tab_hoca2:
  hoca_sekmesi_olustur("hoca2", "Duygu ÇAY", h2_liste)
with tab_hoca3:
  hoca_sekmesi_olustur("hoca3", "Damla ATİK", h3_liste)

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
      type="primary",
  )

# Aktif barem modal penceresini tetikleyici
if st.session_state.aktif_barem:
  h_kodu, h_adi, s_key = st.session_state.aktif_barem
  barem_dialog_goster(h_kodu, h_adi, s_key)
