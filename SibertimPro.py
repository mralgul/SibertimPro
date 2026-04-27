import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import random
import os
import subprocess
import zipfile
import hashlib
import zlib

# ==========================
#  Yardımcılar
# ==========================

def open_path_crossplatform(path: str):
    try:
        os.startfile(path)  # Windows
    except AttributeError:
        try:
            subprocess.call(["open", path])  # macOS
        except Exception:
            subprocess.call(["xdg-open", path])  # Linux

def unique(seq):
    return list(dict.fromkeys(seq))

# === BANNER ===

def banner():
    print(r"""
       🔥  SİBER TİM İŞTEE !
        (\_/)        
       ( •_•)   ← Tavşan ama root yetkili...
       />🍪   ⌐■_■   "TAVŞANI DEĞİL SİBERTİMİ TAKİP ET !"
    ╔════════════════════════════════════════════════════╗
    ║         ☠ YA BENİMSİN YA HURDACININ ☠              ║
    ╚════════════════════════════════════════════════════╝
    """)

# === LEETSPEAK & VARYASYONLAR ===
def leetspeak(word):
    leet_dict = {'a': '@', 'e': '3', 'i': '1', 's': '$', 'o': '0', 'b': '8'}
    return ''.join(leet_dict.get(c.lower(), c) for c in word)

def generate_smart_variations(keyword, numbers, symbols, extra_words):
    variations = set()
    base = [keyword, keyword.lower(), keyword.upper(), keyword.capitalize(),
            leetspeak(keyword), keyword[::-1]]

    numbers = [n.strip() for n in numbers.split(',') if n.strip()]
    symbols = list(symbols)
    extras  = [e.strip() for e in extra_words.split(',') if e.strip()]

    for b in base:
        variations.add(b)

        for num in numbers:
            variations.update([f"{b}{num}", f"{num}{b}"])

        for sym in symbols:
            variations.update([f"{b}{sym}", f"{sym}{b}"])

        for ext in extras:
            variations.update([f"{b}{ext}", f"{ext}{b}"])

    return variations

# === HASHLEME ===
def hash_text(text: str, algo: str) -> str:
    data = text.encode("utf-8", errors="replace")
    algo = algo.lower()
    if algo == "crc32":
        return f"{zlib.crc32(data) & 0xffffffff:08x}"
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()

def run_hash(algo: str):
    txt = hash_entry.get()
    if not txt:
        messagebox.showwarning("Uyarı", "Lütfen hashlemek için bir metin/şifre girin.")
        return
    try:
        digest = hash_text(txt, algo)
    except ValueError:
        messagebox.showerror("Hata", f"Bilinmeyen algoritma: {algo}")
        return

    hash_output.configure(state="normal")
    hash_output.delete("1.0", "end")
    hash_output.insert("1.0", f"{algo.upper()}: {digest}\n")
    hash_output.configure(state="disabled")

def copy_hash_result():
    result = hash_output.get("1.0", "end").strip()
    if not result:
        return
    root.clipboard_clear()
    root.clipboard_append(result)
    messagebox.showinfo("Kopyalandı", "Hash sonucu panoya kopyalandı.")

def save_hash_to_txt():
    content = hash_output.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Uyarı", "Kaydedilecek hash sonucu yok.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile="HashSonucu.txt",
        filetypes=[("Metin Dosyası", "*.txt")]
    )
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            messagebox.showinfo("Kaydedildi", f"Hash sonucu kaydedildi:\n{path}")
            try:
                open_path_crossplatform(path)
            except Exception:
                pass
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Bu dizine dosya kaydetme izniniz yok. Lütfen başka bir konum seçin.")
        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"Dosya kaydedilirken bir sorun oluştu:\n{e}")

def toggle_show_secret():
    current = hash_entry.cget("show")
    hash_entry.config(show="" if current == "•" else "•")

# === TXT KAYDET (Wordlist) ===
def save_to_file():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile="Wordlist.txt",
        filetypes=[("Metin Dosyası", "*.txt")]
    )
    if filepath:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output.get(1.0, tk.END))
            messagebox.showinfo("Kaydedildi", f"Wordlist kaydedildi:\n{filepath}")
            try:
                open_path_crossplatform(filepath)
            except Exception:
                pass
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Bu dizine dosya kaydetme izniniz yok. Lütfen başka bir konum seçin.")
        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"Dosya kaydedilirken bir sorun oluştu:\n{e}")

# === ZIP KAYDET (Wordlist) ===
def save_to_zip():
    content = output.get(1.0, tk.END).strip()
    if not content:
        messagebox.showerror("Hata", "Kaydedilecek içerik yok.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".zip",
        initialfile="Wordlist.zip",
        filetypes=[("ZIP Dosyası", "*.zip")]
    )
    
    if filepath:
        temp_txt_name = "temp_wordlist_export.txt"
        try:
            # 1. Önce geçici txt dosyasını oluştur
            with open(temp_txt_name, "w", encoding="utf-8") as f:
                f.write(content)
                
            # 2. Sonra bu dosyayı zip'e ekle (Zip içindeki adı wordlist.txt olacak şekilde)
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_txt_name, "wordlist.txt")
                
            messagebox.showinfo("Kaydedildi", f"ZIP dosyası oluşturuldu:\n{filepath}")
            try:
                open_path_crossplatform(filepath)
            except Exception:
                pass
                
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Bu konuma dosya kaydetme veya geçici dosya oluşturma izniniz yok.")
        except Exception as e:
            messagebox.showerror("Hata", f"Zip kaydı sırasında hata:\n{e}")
        finally:
            # 3. İşlem başarılı da olsa, hata da verse bu kod çalışır ve çöp bırakmaz
            if os.path.exists(temp_txt_name):
                try:
                    os.remove(temp_txt_name)
                except:
                    pass

def generate_wordlist():
    output.delete(1.0, tk.END)
    kw = keyword_entry.get().strip()
    nums = number_entry.get()
    syms = symbol_entry.get()
    extras = extra_entry.get()
    
    min_len = None
    max_len = None
    minv = min_entry.get().strip()
    maxv = max_entry.get().strip()

    if minv:
        try:
            min_len = int(minv)
            if min_len < 0: raise ValueError()
        except Exception:
            messagebox.showerror("Hata", "Min karakter pozitif bir tamsayı olmalıdır.")
            return
    if maxv:
        try:
            max_len = int(maxv)
            if max_len < 0: raise ValueError()
        except Exception:
            messagebox.showerror("Hata", "Maks karakter pozitif bir tamsayı olmalıdır.")
            return
    if min_len is not None and max_len is not None and min_len > max_len:
        messagebox.showerror("Hata", "Minimum karakter, maksimumdan büyük olamaz.")
        return

    if not kw:
        messagebox.showerror("Hata", "Anahtar kelime boş olamaz.")
        return

    result = generate_smart_variations(kw, nums, syms, extras)

    # Filtre uygula (min/max)
    if min_len is not None or max_len is not None:
        filtered = []
        for w in result:
            L = len(w)
            if (min_len is None or L >= min_len) and (max_len is None or L <= max_len):
                filtered.append(w)
        result_list = sorted(filtered)
    else:
        result_list = sorted(result)

    if not result_list:
        messagebox.showinfo("Bilgi", "Hiç varyasyon üretilmedi veya filtre sonucu boş.")
        return

    for word in result_list:
        output.insert(tk.END, word + "\n")
    messagebox.showinfo("Tamamlandı", f"{len(result_list)} şifre oluşturuldu.")

# ==========================
#  Hash Çözme (Wordlist / Varyasyonlardan)
# ==========================
class CrackState:
    def __init__(self):
        self.lines = []
        self.iter = None
        self.running = False
        self.target = ""
        self.algo = "md5"
        self.batch = 2000

state = CrackState()

def load_wordlist_for_crack():
    path = filedialog.askopenfilename(
        filetypes=[("Metin Dosyası", ".txt"), ("Tümü", ".*")]
    )
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            state.lines = [ln.strip() for ln in f if ln.strip()]
        crack_status.configure(text=f"Wordlist yüklendi: {len(state.lines)} satır")
    except Exception as e:
        messagebox.showerror("Hata", f"Wordlist okunamadı:\n{e}")

def build_candidates_from_ui(mode: str):
    vars_text = output.get("1.0", "end").strip()
    vars_list = vars_text.splitlines() if vars_text else []
    wlist = state.lines

    if mode == "vars":
        return (vars_list, "Varyasyon listesi") if vars_list else ([], "")
    if mode == "wordlist":
        return (wlist, "Yüklü wordlist") if wlist else ([], "")
    if mode == "both":
        combined = unique((vars_list or []) + (wlist or []))
        return (combined, "Varyasyon + Wordlist") if combined else ([], "")

    if vars_list:
        return vars_list, "Varyasyon listesi"
    if wlist:
        return wlist, "Yüklü wordlist"

    candidates = []
    right_plain = hash_entry.get().strip()
    if right_plain:
        candidates.append(right_plain)

    kw = (keyword_entry.get() or "").strip()
    nums = (number_entry.get() or "").strip()
    syms = (symbol_entry.get() or "").strip()
    extras = (extra_entry.get() or "").strip()
    
    if kw or nums or syms or extras:
        try:
            auto_vars = generate_smart_variations(kw, nums, syms, extras)
            candidates.extend(list(auto_vars))
        except Exception:
            pass

    return (unique(candidates), "Otomatik (alanlardan)") if candidates else ([], "")

def start_crack_from_ui():
    """Sol paneldeki 'Çöz' butonu."""
    state.target = crack_hash_entry.get().strip().lower()
    if not state.target:
        messagebox.showwarning("Uyarı", "Lütfen çözümlenecek hash değerini girin.")
        return

    state.algo = algo_var.get()
    mode = source_var.get()

    candidates, src = build_candidates_from_ui(mode)

    if not candidates:
        if mode in ("wordlist", "both"):
            load_wordlist_for_crack()
            if not state.lines and mode != "both":
                messagebox.showwarning("Uyarı", "Wordlist seçilmedi.")
                return
            candidates, src = build_candidates_from_ui(mode)
        if not candidates:
            messagebox.showwarning("Uyarı", "Kullanılacak aday bulunamadı.")
            return

    crack_output.configure(state="normal")
    crack_output.delete("1.0", "end")
    crack_output.insert("1.0", f"Kaynak: {src}\nAlgoritma: {state.algo.upper()}\nAranıyor...\n")
    crack_output.configure(state="disabled")

    crack_status.configure(text=f"Başladı ({src}) — Aday sayısı: {len(candidates)}")
    state.iter = iter(candidates)
    run_crack_loop()

def run_crack_loop():
    state.running = True
    process_crack_batch()

def process_crack_batch():
    if not state.running:
        return
    tried = 0
    found = None
    try:
        while tried < state.batch:
            candidate = next(state.iter)
            if hash_text(candidate, state.algo) == state.target:
                found = candidate
                break
            tried += 1
    except StopIteration:
        state.running = False
        crack_status.configure(text="Bitti: eşleşme bulunamadı.")
        return

    if found is not None:
        state.running = False
        crack_output.configure(state="normal")
        crack_output.delete("1.0", "end")
        crack_output.insert("1.0", f"EŞLEŞME BULUNDU ✅\n"
                                   f"Plain: {found}\n"
                                   f"Hash : {state.target}\n"
                                   f"Algo : {state.algo.upper()}\n")
        crack_output.configure(state="disabled")
        crack_status.configure(text="Tamamlandı (eşleşme bulundu).")
        return

    crack_status.configure(text="Çalışıyor...")
    root.after(1, process_crack_batch)

def cancel_crack():
    state.running = False
    crack_status.configure(text="İptal edildi.")

def save_crack_result():
    content = crack_output.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Uyarı", "Kaydedilecek sonuç yok.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile="HashCozum.txt",
        filetypes=[("Metin Dosyası", "*.txt")]
    )
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            messagebox.showinfo("Kaydedildi", f"Çözüm çıktısı kaydedildi:\n{path}")
            try:
                open_path_crossplatform(path)
            except Exception:
                pass
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Bu dizine dosya kaydetme izniniz yok.")
        except Exception as e:
            messagebox.showerror("Beklenmeyen Hata", f"Dosya kaydedilirken bir sorun oluştu:\n{e}")

# ==========================
#  GUI DÜZENİ
# ==========================
root = tk.Tk()
root.title("SİBERTİM PRO - Akıllı Wordlist + Hash Aracı")
root.geometry("1200x900")
root.configure(bg="#0f0f0f")

# CANVAS (tam pencerelik, responsive)
canvas = tk.Canvas(root, bg="#0f0f0f", highlightthickness=0)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# === MATRIX (responsive) ===
class MatrixRain:
    def __init__(self, canvas, font_size=16):
        self.canvas = canvas
        self.font_size = font_size

        self.width = max(1, self.canvas.winfo_width() or 800)
        self.height = max(1, self.canvas.winfo_height() or 600)
        self.columns = max(1, int(self.width / self.font_size))
        self.drops = [random.randint(0, int(self.height/self.font_size) or 1) for _ in range(self.columns)]

    def update_dimensions(self):
        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())
        if w != self.width or h != self.height:
            self.width = w
            self.height = h
            new_columns = max(1, int(self.width / self.font_size))
            if new_columns != self.columns:
                self.columns = new_columns
                self.drops = [random.randint(0, int(self.height/self.font_size) or 1) for _ in range(self.columns)]

    def draw(self):
        self.update_dimensions()
        self.canvas.delete("matrix")
        for i in range(self.columns):
            char = random.choice(['0', '1'])
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            self.canvas.create_text(x, y, text=char, fill='#00FF00',
                                    font=('Courier', self.font_size, 'bold'),
                                    tags='matrix', anchor='nw')
            if y > self.height and random.random() > 0.9:
                self.drops[i] = 0
            else:
                self.drops[i] += 1
        self.canvas.after(30, self.draw)

# MatrixRain örneğini oluştur ve başlat
rain = MatrixRain(canvas, font_size=16)
rain.draw()

# LOGO
try:
    if "_file_" in globals():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logo_img = Image.open("SiberTim.png").resize((180, 180))
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo, bg="#0f0f0f")
    logo_label.image = logo_photo
    logo_label.place(relx=0.5, rely=0.00009, anchor='n')

except Exception as e:
    print("Logo yüklenemedi:", e)

# FORM (orta)
form = tk.Frame(root, bg="#0f0f0f")
form.place(relx=0.5, rely=0.22, anchor='n')
def field(label_text):
    
    tk.Label(form, text=label_text, fg="#00FF00", bg="#0f0f0f", font=("Courier", 12)).pack()
    e = tk.Entry(form, width=50, bg="#1a1a1a", fg="#00FF00",
                 insertbackground="#00FF00", font=("Courier", 11))
    e.pack(pady=6)
    return e
keyword_entry = field("Anahtar Kelime:")

number_entry  = field("Sayılar (virgülle):")
symbol_entry  = field("Semboller (örn: !@.+):")
extra_entry   = field("Ekstra Kelimeler (örn: admin,test):")

# ---------- Min / Max Karakter ----------
minmax_frame = tk.Frame(form, bg="#0f0f0f")
minmax_frame.pack(pady=4)

tk.Label(minmax_frame, text="Min Karakter (opsiyonel):", fg="#00FF00", bg="#0f0f0f", font=("Courier", 10)).grid(row=0, column=0, sticky="w")
min_entry = tk.Entry(minmax_frame, width=18, bg="#1a1a1a", fg="#00FF00", font=("Courier", 11))
min_entry.grid(row=1, column=0, padx=(0,10))

tk.Label(minmax_frame, text="Maks Karakter (opsiyonel):", fg="#00FF00", bg="#0f0f0f", font=("Courier", 10)).grid(row=0, column=1, sticky="w")
max_entry = tk.Entry(minmax_frame, width=18, bg="#1a1a1a", fg="#00FF00", font=("Courier", 11))
max_entry.grid(row=1, column=1)

tk.Button(form, text="Varyasyonları Oluştur", command=generate_wordlist,
          bg="#00FF00", fg="black", font=("Courier", 12, "bold")).pack(pady=12)
save_frame = tk.Frame(form, bg="#0f0f0f")
save_frame.pack(pady=6)

tk.Button(save_frame, text="TXT Olarak Kaydet", command=save_to_file,
          bg="#1aff66", fg="black", font=("Courier", 12, "bold"),
          width=18).pack(side="left", padx=6)

tk.Button(save_frame, text="ZIP Olarak Kaydet", command=save_to_zip,
          bg="#ffaa00", fg="black", font=("Courier", 12, "bold"),
          width=18).pack(side="left", padx=6)

# VARYASYON ÇIKTISI
output_frame = tk.Frame(root, bg="#0a0a0a", bd=2, relief="groove", highlightthickness=0)
output_frame.place(relx=0.20, rely=0.75, relwidth=0.60, relheight=0.225, anchor='nw')
tk.Label(output_frame, text="Üretilen Varyasyonlar", fg="#00FF00", bg="#0a0a0a",
         font=("Courier", 12, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
output = scrolledtext.ScrolledText(output_frame, width=140, height=14, bg="black",
                                   fg="#00FF00", insertbackground="green", font=("Courier", 11))
output.pack(fill="both", expand=True, padx=8, pady=8)

# HASHLEME (SAĞ)
hash_frame = tk.LabelFrame(root, text=" Hashleme ", fg="#00FF00", bg="#0f0f0f",
                           font=("Courier", 12, "bold"), bd=2, labelanchor="n")
hash_frame.place(relx=0.85, rely=0.23, width=340, height=320, anchor='n')
for i in range(3):
    hash_frame.columnconfigure(i, weight=1)
tk.Label(hash_frame, text="Şifre/Metin:", fg="#00FF00", bg="#0f0f0f",
         font=("Courier", 11)).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2), columnspan=2)
hash_entry = tk.Entry(hash_frame, width=24, bg="#1a1a1a", fg="#00FF00",
                      insertbackground="#00FF00", font=("Courier", 11), show="•")
hash_entry.grid(row=1, column=0, padx=8, pady=2, sticky="we", columnspan=2)
tk.Button(hash_frame, text="Göster/Gizle", command=toggle_show_secret,
          bg="#2e2e2e", fg="#00FF00", font=("Courier", 9, "bold")).grid(row=1, column=2, padx=6, pady=2)
algos = ["MD5", "SHA1", "SHA256", "SHA384", "SHA512", "CRC32"]
for idx, name in enumerate(algos):
    r = 2 + idx // 3
    c = idx % 3
    tk.Button(hash_frame, text=name, command=lambda n=name: run_hash(n),
              bg="#00FF00", fg="black", font=("Courier", 10, "bold")).grid(row=r, column=c, padx=6, pady=8, sticky="we")
hash_output = scrolledtext.ScrolledText(hash_frame, width=34, height=5, bg="black",
                                        fg="#00FF00", insertbackground="green",
                                        font=("Courier", 10), state="disabled")
hash_output.grid(row=4, column=0, columnspan=3, padx=8, pady=(4, 6), sticky="nsew")
btn_row = tk.Frame(hash_frame, bg="#0f0f0f")
btn_row.grid(row=5, column=0, columnspan=3, pady=(2, 10))
tk.Button(btn_row, text="Kopyala", command=copy_hash_result,
          bg="#1aff66", fg="black", font=("Courier", 10, "bold"), width=10).pack(side="left", padx=6)
tk.Button(btn_row, text="TXT Kaydet", command=save_hash_to_txt,
          bg="#00ccff", fg="black", font=("Courier", 10, "bold"), width=12).pack(side="left", padx=6)

# HASH ÇÖZME (SOL)
left_crack = tk.LabelFrame(root, text=" Hash Çözme ", fg="#00FF00", bg="#0f0f0f",
                           font=("Courier", 12, "bold"), bd=2, labelanchor="n")
left_crack.place(relx=0.03, rely=0.23, width=340, height=320, anchor='nw')
for i in range(3):
    left_crack.columnconfigure(i, weight=1)
tk.Label(left_crack, text="Hash:", fg="#00FF00", bg="#0f0f0f",
         font=("Courier", 11)).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2), columnspan=3)
crack_hash_entry = tk.Entry(left_crack, width=30, bg="#1a1a1a", fg="#00FF00",
                            insertbackground="#00FF00", font=("Courier", 10))
crack_hash_entry.grid(row=1, column=0, columnspan=3, padx=8, pady=2, sticky="we")
tk.Label(left_crack, text="Algoritma:", fg="#00FF00", bg="#0f0f0f",
         font=("Courier", 10)).grid(row=2, column=0, sticky="w", padx=8, pady=(8, 2))
algo_var = tk.StringVar(value="md5")
algo_menu = tk.OptionMenu(left_crack, algo_var, "md5", "sha1", "sha256", "sha384", "sha512", "crc32")
algo_menu.config(bg="#1a1a1a", fg="#00FF00", activebackground="#2a2a2a", activeforeground="#00FF00")
algo_menu.grid(row=2, column=1, sticky="we", padx=8, pady=(6, 2))

# Kaynak seçimi (yeni)
tk.Label(left_crack, text="Kaynak:", fg="#00FF00", bg="#0f0f0f",
         font=("Courier", 10)).grid(row=2, column=2, sticky="e", padx=6, pady=(8, 2))
source_var = tk.StringVar(value="auto")
src_menu = tk.OptionMenu(left_crack, source_var, "auto", "vars", "wordlist", "both")
src_menu.config(bg="#1a1a1a", fg="#00FF00", activebackground="#2a2a2a", activeforeground="#00FF00")
src_menu.grid(row=2, column=2, sticky="we", padx=(70, 8), pady=(6, 2))

crack_status = tk.Label(left_crack, text="Varyasyonları oluştur veya wordlist yükle.", fg="#00FF00", bg="#0f0f0f",
                        font=("Courier", 9))
crack_status.grid(row=3, column=0, columnspan=3, padx=8, pady=2, sticky="w")

tk.Button(left_crack, text="Wordlist Yükle", command=load_wordlist_for_crack,
          bg="#00ccff", fg="black", font=("Courier", 10, "bold")).grid(row=4, column=0, padx=6, pady=6, sticky="we")
tk.Button(left_crack, text="Çöz", command=start_crack_from_ui,
          bg="#00FF00", fg="black", font=("Courier", 10, "bold")).grid(row=4, column=1, padx=6, pady=6, sticky="we")
tk.Button(left_crack, text="İptal", command=cancel_crack,
          bg="#ffaa00", fg="black", font=("Courier", 10, "bold")).grid(row=4, column=2, padx=6, pady=6, sticky="we")

crack_output = scrolledtext.ScrolledText(left_crack, width=34, height=5, bg="black",
                                         fg="#00FF00", insertbackground="green",
                                         font=("Courier", 10), state="normal")
crack_output.grid(row=5, column=0, columnspan=3, padx=8, pady=6, sticky="nsew")
tk.Button(left_crack, text="TXT Kaydet", command=save_crack_result,
          bg="#1aff66", fg="black", font=("Courier", 10, "bold")).grid(row=6, column=0, columnspan=3, padx=8, pady=(2, 10), sticky="we")

# Enter => SHA256 kısa yolu (hashleme tarafı)
root.bind("<Return>", lambda e: run_hash("SHA256"))

# pencere için minimum boyut (butonların kaybolmaması için)
root.minsize(900, 700)

# pencere yeniden boyutlandığında matrix güncelle
def on_resize(event):
    try:
        rain.update_dimensions()
    except Exception:
        pass

root.bind("<Configure>", on_resize)

# === BAŞLAT ===
if __name__ == "__main__":
    banner()
    root.mainloop()