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

# --- GÜVENLİ VE YEDEKLEMELİ KAYIT SİSTEMİ ---
def verileri_kaydet():
    try:
        # 1. Önce ana dosyayı güvenli şekilde kaydet (.tmp kullanarak)
        temp_dosya = DOSYA_ADI + ".tmp"
        with open(temp_dosya, "w", encoding="utf-8") as dosya:
            json.dump(ogrenciler, dosya, ensure_ascii=False, indent=4)
        
        if os.path.exists(DOSYA_ADI):
            os.replace(temp_dosya, DOSYA_ADI)
        else:
            os.rename(temp_dosya, DOSYA_ADI)

        # 2. Her kayıtta otomatik olarak 'yedekler' klasörüne zaman damgalı kopya al
        if not os.path.exists(YEDEK_KLASOR):
            os.makedirs(YEDEK_KLASOR, exist_ok=True)
            
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        yedek_adi = os.path.join(YEDEK_KLASOR, f"notlar_yedek_{zaman_damgasi}.json")
        shutil.copy2(DOSYA_ADI, yedek_adi)
        
        # Klasörde 40'tan fazla yedek birikirse en eskisini siler
        yedekler = sorted([os.path.join(YEDEK_KLASOR, f) for f in os.listdir(YEDEK_KLASOR)])
        if len(yedekler) > 40:
            os.remove(yedekler[0])
            
    except Exception as e:
        print(f"Kayıt veya yedekleme hatası: {e}")

def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
                kayitli_veri = json.load(dosya)
                for no in kayitli_veri:
                    if no in ogrenciler:
                        ogrenciler[no].update(kayitli_veri[no])
                        for hoca in ["hoca1", "hoca2", "hoca3"]:
                            if hoca in kayitli_veri[no] and "butunleme" not in kayitli_veri[no][hoca]:
                                ogrenciler[no][hoca]["butunleme"] = 0
        except Exception:
            pass

verileri_yukle()

# --- HESAPLAMA MANTIĞI ---
def ana_sayfa_ortalama_hesapla(h1_notlari, h2_notlari, h3_notlari):
    def not_kontrol_ve_hesapla(anahtar):
        notlar = [h1_notlari[anahtar], h2_notlari[anahtar], h3_notlari[anahtar]]
        for n in notlar:
            if str(n).upper() == "G":
                return "G", "G"
        sayisal_notlar = [float(n) for n in notlar if n != ""]
        if not sayisal_notlar:
            return 0, "G"
        return round(sum(sayisal_notlar) / len(sayisal_notlar)), "NUM"

    str_notlar = {}
    sayisal_notlar_dict = {}
    
    for anahtar in not_anahtarlari:
        val, tip = not_kontrol_ve_hesapla(anahtar)
        str_notlar[anahtar] = val 
        sayisal_notlar_dict[anahtar] = 0 if tip == "G" else val

    j_vals = [("1", str_notlar["1_juri"]), ("2", str_notlar["2_juri"]), ("3", str_notlar["3_juri"])]
    sayisal_juriler = [j for j in j_vals if j[1] != "G"]
    
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
    
    # 1. Normal Final Ortalaması
    final_ortalama = (e1 * 0.08) + (e2 * 0.08) + (juri_1_etkin * 0.12) + (juri_2_etkin * 0.12) + (final_notu * 0.60)
    final_ort_val = round(final_ortalama)
    
    # 2. Bütünleme ve Büt Ortalama Mantığı
    if final_ort_val >= 60:
        str_notlar["butunleme"] = "Geçti"
        but_ort_val = "Geçti"
    else:
        but_val = str_notlar["butunleme"]
        if but_val != 0 and but_val != "G" and str(but_val) != "" and str(but_val) != "Geçti":
            but_notu = float(sayisal_notlar_dict["butunleme"])
            but_ortalama = (e1 * 0.08) + (e2 * 0.08) + (juri_1_etkin * 0.12) + (juri_2_etkin * 0.12) + (but_notu * 0.60)
            but_ort_val = round(but_ortalama)
        else:
            but_ort_val = "-"

    return str_notlar, final_ort_val, but_ort_val

# --- ARAYÜZ (GUI) KURULUMU ---
root = tk.Tk()
root.title("Trakya Üniversitesi - Proje Değerlendirme Sistemi")
root.geometry("1450x750")
root.configure(bg=BG_COLOR)
root.eval('tk::PlaceWindow . center')

# --- MODERN STYLING ---
style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
style.configure("TNotebook.Tab", font=(FONT_FAMILY, 11, "bold"), padding=[25, 10], 
                background="#dcdde1", foreground="#2f3640", borderwidth=0)
style.map("TNotebook.Tab", background=[("selected", HEADER_BG)], foreground=[("selected", "white")])

style.configure("Treeview", font=(FONT_FAMILY, 10), rowheight=35, background="white", fieldbackground="white", borderwidth=0)
style.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"), background=HEADER_BG, foreground=HEADER_FG, borderwidth=0, padding=8)
style.map("Treeview.Heading", background=[("active", "#34495e")])
style.map("Treeview", background=[("selected", SELECTED_BG)], foreground=[("selected", "white")])

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=20)

tab_ana = tk.Frame(notebook, bg=BG_COLOR)
tab_hoca1 = tk.Frame(notebook, bg=BG_COLOR)
tab_hoca2 = tk.Frame(notebook, bg=BG_COLOR)
tab_hoca3 = tk.Frame(notebook, bg=BG_COLOR)

notebook.add(tab_ana, text="🏠 ANA SAYFA (Genel Sonuçlar)")
notebook.add(tab_hoca1, text="👤 Beste AYTİN")
notebook.add(tab_hoca2, text="👤 Duygu ÇAY")
notebook.add(tab_hoca3, text="👤 Damla ATİK")

# --- TABLO SIRALAMA FONKSİYONU ---
def tabloyu_sirala(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    
    def veri_anahtari(item):
        val = str(item[0]).replace("[", "").replace("]", "").strip()
        if val.replace('.', '', 1).isdigit():
            return float(val)
        return val.lower()

    try:
        l.sort(key=veri_anahtari, reverse=reverse)
    except Exception:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
        
    tree.heading(col, command=lambda: tabloyu_sirala(tree, col, not reverse))

# --- EXCEL AKTARIMI ---
def excele_tumunu_aktar():
    dosya_yolu = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Dosyası", "*.xlsx")],
        title="Tüm Listeleri Excel Olarak Kaydet"
    )
    if not dosya_yolu: return
        
    try:
        wb = openpyxl.Workbook()
        ws_ana = wb.active
        ws_ana.title = "Genel Ortalama"
        ws_ana.append(sutunlar_ana)
        for row_id in tablo_ana.get_children():
            ws_ana.append(tablo_ana.item(row_id)["values"])
            
        hocalar_sheet = [("Beste AYTİN", "hoca1"), ("Duygu ÇAY", "hoca2"), ("Damla ATİK", "hoca3")]
        for isim, kod in hocalar_sheet:
            ws = wb.create_sheet(title=isim)
            ws.append(sutunlar_hoca)
            for row_id in hoca_tablolari[kod].get_children():
                ws.append(hoca_tablolari[kod].item(row_id)["values"])
                
        wb.save(dosya_yolu)
        messagebox.showinfo("Başarılı", f"Dosya başarıyla kaydedildi:\n{dosya_yolu}")
    except Exception as e:
        messagebox.showerror("Hata", f"Excel kaydedilirken bir hata oluştu:\n{e}")

# --- ANA SAYFA TASARIMI ---
ust_frame_ana = tk.Frame(tab_ana, bg=BG_COLOR)
ust_frame_ana.pack(fill="x", padx=10, pady=10)

btn_excel = tk.Button(ust_frame_ana, text="📥 Tabloları Excel'e Aktar", command=excele_tumunu_aktar, 
                      bg=BTN_COLOR, fg="white", font=(FONT_FAMILY, 10, "bold"), relief="flat", padx=15, pady=8, cursor="hand2")
btn_excel.pack(side="left")

tk.Label(ust_frame_ana, text="💡 Sütun başlıklarına tıklayarak sıralama yapabilirsiniz.", 
         bg=BG_COLOR, fg="#7f8c8d", font=(FONT_FAMILY, 9, "italic")).pack(side="right", pady=10)

sutunlar_ana = ("Sıra", "Ders Kodu", "Yürütücü", "No", "Ad Soyad", "Eskiz 1", "Eskiz 2", "1. jüri", "2. jüri", "3. jüri", "Final", "Final ORTALAMA", "Bütünleme", "Büt ORTALAMA")
tablo_ana = ttk.Treeview(tab_ana, columns=sutunlar_ana, show="headings")

genislikler_ana = [45, 80, 105, 90, 170, 80, 80, 75, 75, 75, 75, 115, 85, 110]
for col, w in zip(sutunlar_ana, genislikler_ana):
    tablo_ana.heading(col, text=col, command=lambda c=col: tabloyu_sirala(tablo_ana, c, False))
    tablo_ana.column(col, width=w, anchor="center")

tablo_ana.column("Ad Soyad", anchor="w")
tablo_ana.pack(fill="both", expand=True, padx=10, pady=5)

tablo_ana.tag_configure("evenrow", background=ROW_EVEN, font=(FONT_FAMILY, 10, "bold"))
tablo_ana.tag_configure("oddrow", background=ROW_ODD, font=(FONT_FAMILY, 10, "bold"))

def ana_sayfayi_guncelle():
    for row in tablo_ana.get_children():
        tablo_ana.delete(row)
        
    sayac = 0
    for no, veri in sorted(ogrenciler.items(), key=lambda x: x[1]["sira"]):
        str_notlar, final_ort, but_ort = ana_sayfa_ortalama_hesapla(veri["hoca1"], veri["hoca2"], veri["hoca3"])
        
        j_verileri = [("1", str_notlar['1_juri']), ("2", str_notlar['2_juri']), ("3", str_notlar['3_juri'])]
        sayisal_j = [item for item in j_verileri if item[1] != "G"]
        
        en_dusuk_anahtar = None
        if sayisal_j:
            sayisal_j.sort(key=lambda x: float(x[1]))
            en_dusuk_anahtar = sayisal_j[0][0]
            
        j1_str = f"[{str_notlar['1_juri']}]" if (en_dusuk_anahtar == "1" and str_notlar['1_juri'] != "G") else str(str_notlar['1_juri'])
        j2_str = f"[{str_notlar['2_juri']}]" if (en_dusuk_anahtar == "2" and str_notlar['2_juri'] != "G") else str(str_notlar['2_juri'])
        j3_str = f"[{str_notlar['3_juri']}]" if (en_dusuk_anahtar == "3" and str_notlar['3_juri'] != "G") else str(str_notlar['3_juri'])
        
        but_hucre_degeri = "Geçti" if final_ort >= 60 else str_notlar['butunleme']
        
        tag = "evenrow" if sayac % 2 == 0 else "oddrow"
        tablo_ana.insert("", tk.END, values=(
            veri["sira"], veri["kod"], veri["yurutucu"], no, veri["ad"], 
            str_notlar['1_eskiz'], str_notlar['2_eskiz'], j1_str, j2_str, j3_str, 
            str_notlar['final'], final_ort, but_hucre_degeri, but_ort
        ), tags=(tag,))
        sayac += 1
        
    verileri_kaydet()

hoca_tablolari = {}
sutunlar_hoca = ("Sıra", "Ders Kodu", "Yürütücü", "No", "Ad Soyad", "Eskiz 1", "Eskiz 2", "Jüri 1", "Jüri 2", "Jüri 3", "Final", "Bütünleme")

# --- HOCA SEKMELERİ ---
def hoca_sekmesi_hazirla(sekme, hoca_kodu):
    ust_frame = tk.Frame(sekme, bg=BG_COLOR)
    ust_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(ust_frame, text="🔍 Öğrenci Ara:", font=(FONT_FAMILY, 10, "bold"), bg=BG_COLOR, fg="#2c3e50").pack(side="left", padx=5)
    
    arama_var = tk.StringVar()
    arama_entry = tk.Entry(ust_frame, textvariable=arama_var, width=30, font=(FONT_FAMILY, 10), relief="flat")
    arama_entry.pack(side="left", padx=5, ipady=4)

    tk.Label(ust_frame, text="💡 Sütun başlığına tıklayarak sıralayabilirsiniz. Girmedi için 'G' yazın.", 
             bg=BG_COLOR, fg="#7f8c8d", font=(FONT_FAMILY, 9, "italic")).pack(side="right", padx=5)

    hoca_tablo = ttk.Treeview(sekme, columns=sutunlar_hoca, show="headings")
    hoca_tablolari[hoca_kodu] = hoca_tablo
    
    hoca_tablo.tag_configure("evenrow", background=ROW_EVEN)
    hoca_tablo.tag_configure("oddrow", background=ROW_ODD)
    
    genislikler_hoca = [45, 80, 105, 90, 170, 75, 75, 75, 75, 75, 75, 85]
    for col, w in zip(sutunlar_hoca, genislikler_hoca):
        hoca_tablo.heading(col, text=col, command=lambda c=col: tabloyu_sirala(hoca_tablo, c, False))
        hoca_tablo.column(col, width=w, anchor="center")
        
    hoca_tablo.column("Ad Soyad", anchor="w")
    hoca_tablo.pack(fill="both", expand=True, padx=10, pady=5)

    def tabloyu_doldur(filtre=""):
        for row in hoca_tablo.get_children():
            hoca_tablo.delete(row)
            
        filtre = filtre.lower()
        sayac = 0
        for no, veri in sorted(ogrenciler.items(), key=lambda x: x[1]["sira"]):
            if filtre in veri["ad"].lower() or filtre in str(no).lower():
                notlar = veri[hoca_kodu]
                
                _, final_ort_kontrol, but_ort_kontrol = ana_sayfa_ortalama_hesapla(veri["hoca1"], veri["hoca2"], veri["hoca3"])
                
                if final_ort_kontrol >= 60 or but_ort_kontrol == "Geçti":
                    gosterilecek_but = "Geçti"
                else:
                    gosterilecek_but = notlar["butunleme"]
                
                tag = "evenrow" if sayac % 2 == 0 else "oddrow"
                hoca_tablo.insert("", tk.END, iid=no, values=(
                    veri["sira"], veri["kod"], veri["yurutucu"], no, veri["ad"], 
                    notlar["1_eskiz"], notlar["2_eskiz"], notlar["1_juri"], notlar["2_juri"], notlar["3_juri"], notlar["final"], gosterilecek_but
                ), tags=(tag,))
                sayac += 1

    arama_var.trace_add("write", lambda *args: tabloyu_doldur(arama_var.get()))
    tabloyu_doldur()

    def hucreyi_duzenle(row_id, column_id):
        col_idx = int(column_id.replace('#', '')) - 1 
        if col_idx < 5: return 
            
        x, y, width, height = hoca_tablo.bbox(row_id, column_id)
        if not x: return
            
        mevcut_deger = str(hoca_tablo.set(row_id, column_id)).replace("[", "").replace("]", "")
        if mevcut_deger == "Geçti": mevcut_deger = ""

        entry = tk.Entry(hoca_tablo, justify="center", font=(FONT_FAMILY, 10, "bold"), fg=SELECTED_BG, relief="flat")
        entry.place(x=x+2, y=y+2, width=width-4, height=height-4)
        entry.insert(0, mevcut_deger)
        entry.select_range(0, tk.END)
        entry.focus()

        def notu_kaydet_ve_cikis():
            yeni_deger_str = entry.get().strip().upper()
            if yeni_deger_str == "G": yeni_deger = "G"
            elif yeni_deger_str == "" or yeni_deger_str == "-": yeni_deger = 0
            else:
                yeni_deger = round(float(yeni_deger_str))
                if not (0 <= yeni_deger <= 100): raise ValueError()
            
            hoca_tablo.set(row_id, column_id, yeni_deger)
            ogrenciler[row_id][hoca_kodu][not_anahtarlari[col_idx - 5]] = yeni_deger
            ana_sayfayi_guncelle()
            tabloyu_doldur(arama_var.get())
            return True

        def enter_basildi(event):
            try:
                notu_kaydet_ve_cikis()
                tum = hoca_tablo.get_children()
                if row_id in tum and tum.index(row_id) + 1 < len(tum):
                    hucreyi_duzenle(tum[tum.index(row_id) + 1], column_id)
                entry.destroy()
            except ValueError:
                messagebox.showerror("Hata", "0-100 arası sayı veya 'G' giriniz!")
                entry.destroy()
            return "break"

        def tab_basildi(event):
            try:
                notu_kaydet_ve_cikis()
                tum = hoca_tablo.get_children()
                if row_id in tum:
                    if col_idx + 1 < len(sutunlar_hoca):
                        hucreyi_duzenle(row_id, f"#{col_idx + 2}")
                    elif tum.index(row_id) + 1 < len(tum):
                        hucreyi_duzenle(tum[tum.index(row_id) + 1], "#6")
                entry.destroy()
            except ValueError:
                messagebox.showerror("Hata", "0-100 arası sayı veya 'G' giriniz!")
                entry.destroy()
            return "break"

        entry.bind("<Return>", enter_basildi)
        entry.bind("<Tab>", tab_basildi)
        entry.bind("<FocusOut>", lambda e: (notu_kaydet_ve_cikis() if (entry.get().strip().upper() == "G" or entry.get().strip().isdigit() or entry.get().strip() == "") else None, entry.destroy()))

    hoca_tablo.bind("<Double-1>", lambda e: hucreyi_duzenle(hoca_tablo.identify_row(e.y), hoca_tablo.identify_column(e.x)) if hoca_tablo.identify_row(e.y) else None)

hoca_sekmesi_hazirla(tab_hoca1, "hoca1")
hoca_sekmesi_hazirla(tab_hoca2, "hoca2")
hoca_sekmesi_hazirla(tab_hoca3, "hoca3")

ana_sayfayi_guncelle()
root.mainloop()

