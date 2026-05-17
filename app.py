import customtkinter as ctk
from tkinter import messagebox, StringVar
import tkinter as tk
from datetime import datetime
import database as db

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

# ── Palet (Krem / Lacivert Tema) ───────────────────────
BG       = "#F5F0E8"   # krem arka plan
SURFACE  = "#EDE8DC"   # hafif koyu krem yüzey
CARD     = "#FAF7F2"   # kart arka planı
CARD2    = "#EDE8DC"   # ikincil kart
RED      = "#1B2A4A"   # lacivert (vurgu)
RED2     = "#2E4A7A"   # açık lacivert (hover)
RED_DIM  = "#C8D4E8"   # soluk lacivert arka plan
RED_DARK = "#D4DDF0"   # çok soluk lacivert
WHITE    = "#1A1A2E"   # koyu lacivert — metin rengi
BTN_TXT  = "#F0EAD6"   # krem — buton üzeri metin rengi
MUTED    = "#6B6B7A"   # gri-mor ton (yardımcı metin)
MUTED2   = "#8A8A99"   # daha açık yardımcı
BORDER   = "#D8D0C0"   # krem sınır
BORDER2  = "#C8C0B0"   # koyu krem sınır
SIDEBAR  = "#EDE8DC"   # sidebar krem
SIDEBAR_W = 180

# ── Tipografi ──────────────────────────────────────────
FH = ("Helvetica", 12, "bold")
FB = ("Helvetica", 11)
FS = ("Helvetica", 9)
FL = ("Helvetica", 10, "bold")
FT = ("Helvetica", 14, "bold")
FN = ("Helvetica", 16, "bold")


# ── Yardımcılar ────────────────────────────────────────
def clear(f):
    for w in f.winfo_children():
        w.destroy()

def rbtn(parent, text, cmd, bg=RED, fg=None, w=120, h=32, f=FL, r=6):
    hov = RED2 if bg == RED else BORDER2
    # Lacivert/koyu butonlarda otomatik krem yazı; açık butonlarda belirtilen renk
    if fg is None:
        fg = BTN_TXT if bg in (RED, RED2) else WHITE
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color=bg, hover_color=hov, text_color=fg,
        font=f, width=w, height=h, corner_radius=r)

def rentry(parent, ph="", show="", w=280, h=34):
    return ctk.CTkEntry(
        parent, placeholder_text=ph, show=show,
        width=w, height=h, fg_color=CARD2,
        border_color=BORDER2, text_color=WHITE,
        placeholder_text_color=MUTED, font=FB, corner_radius=6)

def rlabel(parent, text, f=FB, c=WHITE, anchor="w"):
    return ctk.CTkLabel(parent, text=text, font=f, text_color=c, anchor=anchor)

def red_accent(parent):
    ctk.CTkFrame(parent, fg_color=RED, height=2, corner_radius=0).pack(fill="x")

def page_title(parent, title, sub=None):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=20, pady=(16, 10))
    rlabel(f, title, FT, WHITE).pack(anchor="w")
    ctk.CTkFrame(f, fg_color=RED, height=2, width=32, corner_radius=0).pack(anchor="w", pady=(4, 0))
    if sub:
        rlabel(f, sub, FS, MUTED).pack(anchor="w", pady=(4, 0))

def roption(parent, values, variable, w=150, h=32):
    return ctk.CTkOptionMenu(
        parent, values=values, variable=variable,
        width=w, height=h, fg_color=CARD2,
        button_color=RED_DIM, button_hover_color=RED,
        text_color=WHITE, dropdown_fg_color=CARD2,
        dropdown_text_color=WHITE, font=FS,
        dropdown_font=FS, corner_radius=6)


# ── Film Kartı (katalog) ────────────────────────────────
def film_card(parent, p, on_detail, on_fav, uid, row, col):
    c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=8,
                     border_width=1, border_color=BORDER2, width=200)
    c.grid(row=row, column=col, padx=5, pady=5, sticky="n")

    ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")

    br = ctk.CTkFrame(c, fg_color="transparent")
    br.pack(fill="x", padx=8, pady=(6, 0))
    tip_bg = {"Film": CARD2, "Dizi": RED_DARK, "Tv Show": "#D0E0F0"}
    tip_fg = {"Film": MUTED, "Dizi": "#1B3A6B", "Tv Show": "#1A4477"}
    ctk.CTkLabel(br, text=p["program_tipi"].upper(),
                 font=("Helvetica", 8, "bold"),
                 text_color=tip_fg.get(p["program_tipi"], MUTED),
                 fg_color=tip_bg.get(p["program_tipi"], CARD2),
                 corner_radius=3, height=16, width=44).pack(side="left")
    rlabel(br, str(p["yayin_yili"] or ""), FS, MUTED).pack(side="right")

    nf = ctk.CTkFrame(c, fg_color="transparent", height=40)
    nf.pack(fill="x", padx=10, pady=(6,0))
    nf.pack_propagate(False)
    ctk.CTkLabel(nf, text=p["program_adi"], font=FH, text_color=WHITE,
                 wraplength=185, justify="left", anchor="nw").pack(fill="both")

    turler = (p["turler"] or "").split(",")
    tf = ctk.CTkFrame(c, fg_color="transparent", height=18)
    tf.pack(fill="x", padx=10, pady=(2,0))
    tf.pack_propagate(False)
    ctk.CTkLabel(tf, text=" · ".join(t.strip() for t in turler[:2]),
                 font=FS, text_color=MUTED, anchor="w").pack(fill="both")

    puan = round(p["ort_puan"] or 0, 1)
    bar = ctk.CTkFrame(c, fg_color=BORDER2, height=2, corner_radius=1)
    bar.pack(fill="x", padx=10, pady=(6, 0))
    pct = max(0.0, min(1.0, puan / 10))
    if pct > 0:
        ctk.CTkFrame(bar, fg_color=RED, height=2, corner_radius=1,
                     width=int(180 * pct)).place(x=0, y=0)

    meta = ctk.CTkFrame(c, fg_color="transparent")
    meta.pack(padx=10, pady=(5, 4), fill="x")
    filled = round(puan / 2)
    for i in range(5):
        ctk.CTkFrame(meta, fg_color=RED if i < filled else BORDER2,
                     width=7, height=7, corner_radius=4).pack(side="left", padx=1)
    rlabel(meta, f"  {puan}", ("Helvetica", 10, "bold"), WHITE).pack(side="left")
    rlabel(meta, f"{p['izlenme_sayisi']}", FS, MUTED).pack(side="right")

    ctk.CTkFrame(c, fg_color=BORDER, height=1).pack(fill="x")
    btns = ctk.CTkFrame(c, fg_color=CARD2, corner_radius=0)
    btns.pack(fill="x")
    rbtn(btns, "▶  İzle", lambda pid=p["program_id"]: on_detail(pid),
         w=136, h=32, f=FS).pack(side="left")
    is_fav = db.is_favorite(uid, p["program_id"])
    rbtn(btns, "♥" if is_fav else "♡",
         lambda pid=p["program_id"]: on_fav(pid),
         bg=RED_DIM if is_fav else CARD2, fg=RED, w=36, h=32, f=FB).pack(side="left")


# ── İçerik Yönetim Kartı (admin) ───────────────────────
def admin_content_card(parent, p, on_edit, on_del, row, col):
    c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=8,
                     border_width=1, border_color=BORDER2, width=200)
    c.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")

    # Tip badge + yıl — sabit yükseklik
    br = ctk.CTkFrame(c, fg_color="transparent", height=26)
    br.pack(fill="x", padx=10, pady=(8,0))
    br.pack_propagate(False)
    tip_bg = {"Film": CARD2, "Dizi": RED_DARK, "Tv Show": "#D0E0F0"}
    tip_fg = {"Film": MUTED, "Dizi": "#1B3A6B", "Tv Show": "#1A4477"}
    ctk.CTkLabel(br, text=p["program_tipi"].upper(),
                 font=("Helvetica", 8, "bold"),
                 text_color=tip_fg.get(p["program_tipi"], MUTED),
                 fg_color=tip_bg.get(p["program_tipi"], CARD2),
                 corner_radius=3, height=16, width=44).pack(side="left")
    rlabel(br, str(p["yayin_yili"] or ""), FS, MUTED).pack(side="right")

    # İsim — sabit 40px yükseklik, 2 satır max
    name_frame = ctk.CTkFrame(c, fg_color="transparent", height=40)
    name_frame.pack(fill="x", padx=10, pady=(4,0))
    name_frame.pack_propagate(False)
    ctk.CTkLabel(name_frame, text=p["program_adi"], font=FH, text_color=WHITE,
                 wraplength=180, justify="left", anchor="nw").pack(fill="both")

    # Tür — sabit 18px, tek satır
    turler = (p["turler"] or "").split(",")
    tur_text = " · ".join(t.strip() for t in turler[:2])
    tur_frame = ctk.CTkFrame(c, fg_color="transparent", height=18)
    tur_frame.pack(fill="x", padx=10, pady=(2,0))
    tur_frame.pack_propagate(False)
    ctk.CTkLabel(tur_frame, text=tur_text, font=FS, text_color=MUTED2,
                 anchor="w").pack(fill="both")

    # Meta — sabit 18px
    meta = ctk.CTkFrame(c, fg_color="transparent", height=18)
    meta.pack(fill="x", padx=10, pady=(6,8))
    meta.pack_propagate(False)
    ctk.CTkLabel(meta, text=f"▸ {p['izlenme_sayisi']} izlenme",
                 font=FS, text_color=MUTED2, anchor="w").pack(side="left")
    ctk.CTkLabel(meta, text=f"{p['bolum_sayisi']} bölüm",
                 font=FS, text_color=MUTED2, anchor="e").pack(side="right")

    ctk.CTkFrame(c, fg_color=BORDER, height=1).pack(fill="x")
    btns = ctk.CTkFrame(c, fg_color=CARD2, corner_radius=0, height=32)
    btns.pack(fill="x")
    btns.pack_propagate(False)
    rbtn(btns, "Düzenle", lambda pid=p["program_id"]: on_edit(pid),
         bg=CARD2, fg=MUTED, w=100, h=32, f=FS).pack(side="left")
    rbtn(btns, "Sil", lambda pid=p["program_id"]: on_del(pid),
         bg=RED_DIM, fg=RED, w=72, h=32, f=FS).pack(side="left")


# ── Grid Render ────────────────────────────────────────
def render_catalog_grid(parent, programs, on_detail, on_fav, uid):
    clear(parent)
    if not programs:
        rlabel(parent, "İçerik bulunamadı.", FB, MUTED, "center").pack(pady=60)
        return
    rlabel(parent, f"  {len(programs)} sonuç", FS, MUTED2).pack(
        anchor="w", padx=4, pady=(4, 2))
    grid = ctk.CTkFrame(parent, fg_color="transparent")
    grid.pack(fill="x", padx=4)
    COLS = 5
    for i, p in enumerate(programs):
        film_card(grid, p, on_detail, on_fav, uid, i // COLS, i % COLS)

def render_admin_grid(parent, programs, on_edit, on_del):
    clear(parent)
    if not programs:
        rlabel(parent, "İçerik yok.", FB, MUTED).pack(pady=40)
        return
    rlabel(parent, f"  {len(programs)} kayıt", FS, MUTED2).pack(
        anchor="w", padx=4, pady=(4, 2))
    grid = ctk.CTkFrame(parent, fg_color="transparent")
    grid.pack(fill="x", padx=4)
    COLS = 5
    for i, p in enumerate(programs):
        admin_content_card(grid, p, on_edit, on_del, i // COLS, i % COLS)


# ── Filtre Şeridi ──────────────────────────────────────
def build_filter_bar(parent, genres, on_search, uid):
    fbar = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=0)
    fbar.pack(fill="x")
    ctk.CTkFrame(fbar, fg_color=BORDER, height=1).pack(fill="x")

    r1 = ctk.CTkFrame(fbar, fg_color="transparent")
    r1.pack(padx=16, pady=(8, 4), fill="x")

    search_var = StringVar()
    se = ctk.CTkEntry(r1, textvariable=search_var, placeholder_text="İçerik ara...",
                      width=190, height=30, fg_color=CARD2, border_color=BORDER2,
                      text_color=WHITE, placeholder_text_color=MUTED, font=FS, corner_radius=6)
    se.pack(side="left", padx=(0, 6))

    tur_list = ["Tüm Türler"] + [g["tur_adi"] for g in genres]
    tur_var = StringVar(value="Tüm Türler")
    roption(r1, tur_list, tur_var, w=160, h=30).pack(side="left", padx=3)

    tip_var = StringVar(value="Tümü")
    roption(r1, ["Tümü", "Film", "Dizi", "Tv Show"], tip_var, w=96, h=30).pack(side="left", padx=3)

    sort_map = {"Ada Göre": "ad", "En Çok İzlenen": "izlenme",
                "En Yüksek Puan": "puan", "Yıla Göre": "yil"}
    sort_var = StringVar(value="Ada Göre")
    roption(r1, list(sort_map.keys()), sort_var, w=145, h=30).pack(side="left", padx=3)

    def _do():
        sq  = search_var.get().strip()
        tv  = tur_var.get()
        tid = next((g["tur_id"] for g in genres if g["tur_adi"] == tv), None)
        tip = None if tip_var.get() == "Tümü" else tip_var.get()
        srt = sort_map.get(sort_var.get(), "ad")
        yil_s = yil_var.get().strip()
        yayin_yili = int(yil_s) if yil_s.isdigit() else None
        mp_s = mp_var.get().strip()
        min_puan = float(mp_s) if mp_s else None
        fav_uid  = uid if fav_var.get() else None
        on_search(sq, tid, tip, srt, yayin_yili, min_puan, fav_uid)

    rbtn(r1, "Ara", _do, w=68, h=30, f=FS).pack(side="left", padx=6)
    rbtn(r1, "Öneriler",
         lambda: on_search(None, None, None, None, None, None, None, oneri=True),
         bg=CARD2, fg=RED, w=86, h=30, f=FS).pack(side="left", padx=2)

    r2 = ctk.CTkFrame(fbar, fg_color="transparent")
    r2.pack(padx=16, pady=(0, 8), fill="x")

    rlabel(r2, "Yıl:", FS, MUTED).pack(side="left")
    yil_var = StringVar()
    ctk.CTkEntry(r2, textvariable=yil_var, placeholder_text="2019",
                 width=68, height=26, fg_color=CARD2, border_color=BORDER2,
                 text_color=WHITE, font=FS, corner_radius=6).pack(side="left", padx=4)
    rlabel(r2, "Min Puan:", FS, MUTED).pack(side="left", padx=(8, 0))
    mp_var = StringVar()
    ctk.CTkEntry(r2, textvariable=mp_var, placeholder_text="1-10",
                 width=55, height=26, fg_color=CARD2, border_color=BORDER2,
                 text_color=WHITE, font=FS, corner_radius=6).pack(side="left", padx=4)
    fav_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(r2, text="Sadece Favorilerim", variable=fav_var,
                    text_color=MUTED, font=FS, fg_color=RED,
                    hover_color=RED2, checkmark_color=BG,
                    corner_radius=3).pack(side="left", padx=10)
    return _do


# ══════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CRiMSON")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG)
        self.current_user = None
        self.root = ctk.CTkFrame(self, fg_color=BG)
        self.root.pack(fill="both", expand=True)
        db.init_db()
        db.seed_data()
        self.show_login()

    # ── Navbar ───────────────────────────────────────
    def _navbar(self, tabs, is_admin=False):
        nav = ctk.CTkFrame(self.root, fg_color=SURFACE, corner_radius=0, height=50)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        ctk.CTkLabel(nav, text="CRi", font=("Helvetica", 16, "bold"),
                     text_color=RED).pack(side="left", padx=(16, 0))
        ctk.CTkLabel(nav, text="MSON", font=("Helvetica", 16, "bold"),
                     text_color=WHITE).pack(side="left", padx=(0, 4))
        if is_admin:
            rlabel(nav, "YÖNETİCİ", ("Helvetica", 9, "bold"), RED_DIM).pack(side="left", padx=4)
        ctk.CTkFrame(nav, fg_color=BORDER2, width=1, height=22).pack(side="left", padx=8)
        for txt, cmd in tabs:
            ctk.CTkButton(nav, text=txt, command=cmd,
                          fg_color="transparent", hover_color=CARD2,
                          text_color=MUTED, font=FL, width=96, height=50,
                          corner_radius=0).pack(side="left")
        rbtn(nav, "Çıkış", self.show_login, bg=CARD2, fg=MUTED,
             w=66, h=30, f=FS).pack(side="right", padx=12)
        ctk.CTkFrame(nav, fg_color=RED, width=6, height=6,
                     corner_radius=3).pack(side="right", padx=(0, 4))
        rlabel(nav, self.current_user["ad"] if self.current_user else "",
               FS, MUTED).pack(side="right")
        ctk.CTkFrame(self.root, fg_color=RED, height=2, corner_radius=0).pack(fill="x")

    # ── Sidebar + İçerik Alanı ───────────────────────
    def _sidebar_layout(self, items, active_idx=0):
        wrap = ctk.CTkFrame(self.root, fg_color=BG)
        wrap.pack(fill="both", expand=True)

        # Sidebar
        sb = ctk.CTkFrame(wrap, fg_color=SIDEBAR, corner_radius=0,
                          width=SIDEBAR_W, border_width=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkFrame(sb, fg_color=BORDER, width=1).pack(side="right", fill="y")

        rlabel(sb, "MENÜ", ("Helvetica", 8, "bold"), MUTED2).pack(
            anchor="w", padx=14, pady=(14, 6))

        for i, (ico, lbl, cmd) in enumerate(items):
            is_active = (i == active_idx)
            btn_bg    = CARD if is_active else "transparent"
            btn_fg    = WHITE if is_active else MUTED
            border_c  = RED if is_active else "transparent"
            f = ctk.CTkFrame(sb, fg_color=btn_bg, corner_radius=0,
                             border_width=0, height=38)
            f.pack(fill="x")
            f.pack_propagate(False)
            accent = ctk.CTkFrame(f, fg_color=border_c, width=3, corner_radius=0)
            accent.pack(side="left", fill="y")
            ctk.CTkButton(f, text=f"{ico}  {lbl}", command=cmd,
                          fg_color="transparent", hover_color=CARD,
                          text_color=btn_fg, font=FS,
                          anchor="w", width=SIDEBAR_W - 3, height=38,
                          corner_radius=0).pack(fill="both")

        # İçerik alanı
        content = ctk.CTkScrollableFrame(wrap, fg_color=BG, corner_radius=0)
        content.pack(side="left", fill="both", expand=True)
        return content

    # ── GİRİŞ ────────────────────────────────────────
    def show_login(self):
        clear(self.root)
        left = ctk.CTkFrame(self.root, fg_color=RED, corner_radius=0, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        inner = ctk.CTkFrame(left, fg_color="transparent")
        inner.place(relx=0.5, rely=0.42, anchor="center")
        ctk.CTkLabel(inner, text="CRi", font=("Helvetica", 52, "bold"),
                     text_color=BG).pack(anchor="w")
        ctk.CTkLabel(inner, text="MSON", font=("Helvetica", 52, "bold"),
                     text_color=RED_DIM).pack(anchor="w")
        ctk.CTkFrame(inner, fg_color=BG, height=2, width=130,
                     corner_radius=0).pack(anchor="w", pady=10)
        ctk.CTkLabel(inner, text="Tüm içerikler\nbir arada.",
                     font=("Helvetica", 12), text_color=BG,
                     justify="left").pack(anchor="w")
        dot_row = ctk.CTkFrame(inner, fg_color="transparent")
        dot_row.pack(anchor="w", pady=(18, 0))
        for _ in range(5):
            ctk.CTkFrame(dot_row, fg_color=WHITE, width=7, height=7,
                         corner_radius=4).pack(side="left", padx=3)

        right = ctk.CTkFrame(self.root, fg_color=BG)
        right.pack(side="left", fill="both", expand=True)
        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        rlabel(form, "Giriş Yap", FT, WHITE).pack(anchor="w")
        ctk.CTkFrame(form, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4, 16))

        rlabel(form, "E-posta", FL, MUTED).pack(anchor="w")
        email_e = rentry(form, "kullanici@ornek.com", w=300)
        email_e.pack(pady=(3, 10))
        rlabel(form, "Şifre", FL, MUTED).pack(anchor="w")
        pass_e  = rentry(form, "••••••••", show="•", w=300)
        pass_e.pack(pady=(3, 6))

        err = rlabel(form, "", FS, "#cc4444")
        err.pack(pady=4)

        def do_login():
            e, p = email_e.get().strip(), pass_e.get().strip()
            if not e or not p:
                err.configure(text="Tüm alanları doldurunuz.")
                return
            if "@" not in e:
                err.configure(text="Geçersiz e-posta.")
                return
            user = db.login(e, p)
            if user:
                self.current_user = user
                self.show_admin() if user["rol_adi"] == "Admin" else self.show_home()
            else:
                err.configure(text="Hatalı e-posta veya şifre.")

        rbtn(form, "▶  Giriş Yap", do_login, w=300, h=38).pack(pady=(4, 6))
        rbtn(form, "Kayıt Ol", self.show_register,
             bg=CARD2, fg=WHITE, w=300, h=34).pack()
        ctk.CTkFrame(form, fg_color=BORDER2, height=1, width=300).pack(pady=10)
        rlabel(form, "Demo: admin@netflix.com / admin123", FS, MUTED, "center").pack()

    # ── KAYIT ────────────────────────────────────────
    def show_register(self):
        clear(self.root)
        wrap = ctk.CTkScrollableFrame(self.root, fg_color=BG)
        wrap.pack(fill="both", expand=True)
        box = ctk.CTkFrame(wrap, fg_color=CARD, corner_radius=10,
                           border_width=1, border_color=BORDER2, width=580)
        box.pack(pady=20, padx=40)
        ctk.CTkFrame(box, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(padx=28, pady=18, fill="x")
        rlabel(inner, "Yeni Hesap", FT, WHITE).pack(anchor="w")
        ctk.CTkFrame(inner, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4, 12))

        gg = ctk.CTkFrame(inner, fg_color="transparent")
        gg.pack(fill="x")
        fields = {}
        defs = [("Ad","ad"),("Soyad","soyad"),("E-posta","email"),
                ("Şifre","sifre"),("Şifre Tekrar","sifre2"),
                ("Doğum (YYYY-MM-DD)","dogum"),("Ülke","ulke")]
        for i, (lbl, key) in enumerate(defs):
            cf = ctk.CTkFrame(gg, fg_color="transparent")
            cf.grid(row=i//2, column=i%2, padx=6, pady=3, sticky="w")
            rlabel(cf, lbl, FS, MUTED).pack(anchor="w")
            e = rentry(cf, lbl.lower(), show="•" if "ifre" in lbl else "", w=230, h=32)
            e.pack()
            fields[key] = e

        rlabel(inner, "Cinsiyet", FS, MUTED).pack(anchor="w", pady=(10,4))
        cin_var = StringVar(value="E")
        cr = ctk.CTkFrame(inner, fg_color="transparent")
        cr.pack(anchor="w")
        for txt, val in [("Erkek","E"),("Kadın","K")]:
            ctk.CTkRadioButton(cr, text=txt, variable=cin_var, value=val,
                               text_color=WHITE, font=FS,
                               fg_color=RED, hover_color=RED2).pack(side="left", padx=(0,14))

        rlabel(inner, "Favori Türler — 3 seçiniz", FS, MUTED).pack(anchor="w", pady=(10,4))
        genres = db.get_genres()
        tur_vars = {}
        gf = ctk.CTkFrame(inner, fg_color=CARD2, corner_radius=6)
        gf.pack(fill="x")
        for i, g in enumerate(genres):
            v = tk.BooleanVar()
            tur_vars[g["tur_id"]] = v
            ctk.CTkCheckBox(gf, text=g["tur_adi"], variable=v,
                            text_color=MUTED, font=FS, fg_color=RED,
                            hover_color=RED2, checkmark_color=BG,
                            corner_radius=3).grid(row=i//3, column=i%3,
                                                  sticky="w", padx=10, pady=4)
        err = rlabel(inner, "", FS, "#cc4444")
        err.pack(anchor="w", pady=6)

        def do_reg():
            vals = {k: fields[k].get().strip() for k in fields}
            if not all(vals.values()):
                err.configure(text="Tüm alanları doldurunuz."); return
            if "@" not in vals["email"]:
                err.configure(text="Geçersiz e-posta."); return
            if vals["sifre"] != vals["sifre2"]:
                err.configure(text="Şifreler eşleşmiyor."); return
            if len(vals["sifre"]) < 6:
                err.configure(text="Şifre en az 6 karakter."); return
            sel = [tid for tid, v in tur_vars.items() if v.get()]
            if len(sel) != 3:
                err.configure(text="Tam olarak 3 tür seçiniz."); return
            try:
                dt = datetime.strptime(vals["dogum"], "%Y-%m-%d")
                if dt > datetime.now():
                    err.configure(text="Geçersiz doğum tarihi."); return
            except ValueError:
                err.configure(text="Tarih: YYYY-MM-DD"); return
            ok, result = db.register(vals["ad"], vals["soyad"], vals["email"],
                                     vals["sifre"], vals["dogum"], cin_var.get(),
                                     vals["ulke"], sel)
            if ok:
                self._reg_success(db.get_recommendations(result))
            else:
                err.configure(text=str(result))

        br = ctk.CTkFrame(inner, fg_color="transparent")
        br.pack(fill="x", pady=(6,0))
        rbtn(br, "▶  Kayıt Ol", do_reg, w=200, h=36).pack(side="left")
        rbtn(br, "← Geri", self.show_login,
             bg=CARD2, fg=WHITE, w=100, h=36).pack(side="left", padx=8)

    def _reg_success(self, recs):
        clear(self.root)
        wrap = ctk.CTkScrollableFrame(self.root, fg_color=BG)
        wrap.pack(fill="both", expand=True)
        ctk.CTkFrame(wrap, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        rlabel(wrap, "Kayıt Başarılı!", ("Helvetica", 22, "bold"), WHITE, "center").pack(pady=(20,4))
        rlabel(wrap, "Beğenebileceğin içerikler:", FB, MUTED, "center").pack()
        grid = ctk.CTkFrame(wrap, fg_color="transparent")
        grid.pack(pady=14, padx=28)
        for i, r in enumerate(recs[:6]):
            c = ctk.CTkFrame(grid, fg_color=CARD, corner_radius=8,
                             border_width=1, border_color=BORDER2, width=185)
            c.grid(row=i//3, column=i%3, padx=5, pady=5)
            ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
            rlabel(c, r["program_adi"], FH, WHITE).pack(padx=10, pady=(8,2), anchor="w")
            rlabel(c, r["program_tipi"], FS, MUTED).pack(padx=10, anchor="w", pady=(0,8))
        rbtn(wrap, "▶  Giriş Yap", self.show_login, w=180, h=36).pack(pady=14)

    # ── KULLANICI LAYOUT ─────────────────────────────
    def show_home(self):
        clear(self.root)
        tabs = [("Katalog", self.show_content_page),
                ("Favoriler", self.show_favorites_page),
                ("Geçmiş", self.show_history_page),
                ("Profil", self.show_profile_page)]
        self._navbar(tabs)
        self._setup_user_sidebar(0)

    def _setup_user_sidebar(self, active):
        if hasattr(self, "_wrap") and self._wrap.winfo_exists():
            self._wrap.destroy()
        self._wrap = ctk.CTkFrame(self.root, fg_color=BG)
        self._wrap.pack(fill="both", expand=True)

        items = [("▶", "Katalog",   self.show_content_page),
                 ("♥", "Favoriler", self.show_favorites_page),
                 ("◎", "Geçmiş",    self.show_history_page),
                 ("◈", "Profil",    self.show_profile_page)]

        sb = ctk.CTkFrame(self._wrap, fg_color=SIDEBAR, corner_radius=0, width=SIDEBAR_W)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkFrame(sb, fg_color=BORDER, width=1).pack(side="right", fill="y")
        rlabel(sb, "MENÜ", ("Helvetica", 8, "bold"), MUTED2).pack(anchor="w", padx=14, pady=(14,6))
        for i, (ico, lbl, cmd) in enumerate(items):
            is_a = (i == active)
            fr = ctk.CTkFrame(sb, fg_color=CARD if is_a else "transparent",
                              corner_radius=0, height=38)
            fr.pack(fill="x")
            fr.pack_propagate(False)
            ctk.CTkFrame(fr, fg_color=RED if is_a else "transparent",
                         width=3, corner_radius=0).pack(side="left", fill="y")
            ctk.CTkButton(fr, text=f"{ico}  {lbl}", command=cmd,
                          fg_color="transparent", hover_color=CARD,
                          text_color=WHITE if is_a else MUTED,
                          font=FS, anchor="w",
                          width=SIDEBAR_W-3, height=38, corner_radius=0).pack(fill="both")

        self.content_area = ctk.CTkScrollableFrame(self._wrap, fg_color=BG, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

    def _home_content(self, active_idx):
        clear(self.root)
        tabs = [("Katalog", self.show_content_page),
                ("Favoriler", self.show_favorites_page),
                ("Geçmiş", self.show_history_page),
                ("Profil", self.show_profile_page)]
        self._navbar(tabs)
        self._setup_user_sidebar(active_idx)

    # ── KATALOG ──────────────────────────────────────
    def show_content_page(self):
        self._home_content(0)
        uid = self.current_user["kullanici_id"]
        genres = db.get_genres()

        # Filtre cubuğu ONCE ekleniyor (sayfanın en başı)
        res = ctk.CTkFrame(self.content_area, fg_color="transparent")

        def on_search(sq, tid, tip, srt, yil, mp, fav_uid, oneri=False):
            if oneri:
                progs = db.get_recommendations(uid)
            else:
                progs = db.get_programs(sq or "", tid, tip,
                                        min_puan=mp, yayin_yili=yil,
                                        sort=srt or "ad",
                                        sadece_favori_uid=fav_uid)
            render_catalog_grid(res, progs,
                                self.show_detail, self._toggle_fav, uid)

        build_filter_bar(self.content_area, genres, on_search, uid)
        # Icerik grid'i filtre cubugundan SONRA pack ediliyor
        res.pack(fill="both", expand=True)
        render_catalog_grid(res, db.get_programs(),
                            self.show_detail, self._toggle_fav, uid)

    def _toggle_fav(self, pid):
        uid = self.current_user["kullanici_id"]
        if db.is_favorite(uid, pid):
            db.remove_from_favorites(uid, pid)
        else:
            db.add_to_favorites(uid, pid)
        self.show_content_page()

    # ── DETAY ────────────────────────────────────────
    def show_detail(self, pid):
        self._home_content(0)
        uid = self.current_user["kullanici_id"]
        p   = db.get_program(pid)
        pos = db.get_last_watch_position(uid, pid)

        rbtn(self.content_area, "← Geri", self.show_content_page,
             bg=CARD2, fg=MUTED, w=78, h=26, f=FS).pack(anchor="w", padx=16, pady=8)

        hbox = ctk.CTkFrame(self.content_area, fg_color=SURFACE,
                            corner_radius=8, border_width=1, border_color=BORDER)
        hbox.pack(fill="x", padx=16, pady=4)
        ctk.CTkFrame(hbox, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        hi = ctk.CTkFrame(hbox, fg_color="transparent")
        hi.pack(padx=18, pady=12, fill="x")

        tr = ctk.CTkFrame(hi, fg_color="transparent")
        tr.pack(fill="x")
        rlabel(tr, p["program_adi"], ("Helvetica", 18, "bold"), WHITE).pack(side="left")
        tip_bg = {"Film": CARD2, "Dizi": RED_DARK, "Tv Show": "#D0E0F0"}
        tip_fg = {"Film": MUTED, "Dizi": "#1B3A6B", "Tv Show": "#1A4477"}
        ctk.CTkLabel(tr, text=p["program_tipi"].upper(),
                     font=("Helvetica", 9, "bold"),
                     text_color=tip_fg.get(p["program_tipi"], MUTED),
                     fg_color=tip_bg.get(p["program_tipi"], CARD2),
                     corner_radius=4, height=20, width=46).pack(side="left", padx=10)

        # Kullanıcının izleyip izlemediği
        hist = db.get_watch_history(uid)
        izledi = any(h["program_id"] == pid for h in hist)
        izleme_etiketi = "● Daha önce izlendi" if izledi else "◌ Henüz izlenmedi"
        izleme_renk = RED if izledi else MUTED
        ctk.CTkLabel(tr, text=izleme_etiketi, font=FS,
                     text_color=izleme_renk).pack(side="right", padx=8)

        mg = ctk.CTkFrame(hi, fg_color="transparent")
        mg.pack(fill="x", pady=8)
        for i, (k, v) in enumerate([
            ("Türler", p["turler"] or "—"), ("Yıl", str(p["yayin_yili"] or "—")),
            ("Bölüm Sayısı", str(p["bolum_sayisi"])), ("Bölüm Süresi", f"{p['bolum_uzunlugu']} dk"),
            ("Ort. Puan", f"★ {round(p['ort_puan'] or 0,1)}/10"), ("İzlenme", f"▸{p['izlenme_sayisi']}")
        ]):
            mf = ctk.CTkFrame(mg, fg_color="transparent")
            mf.grid(row=i//3, column=i%3, sticky="w", padx=14, pady=2)
            rlabel(mf, k+": ", FS, MUTED).pack(side="left")
            rlabel(mf, v, FS, RED).pack(side="left")
        rlabel(hi, p["aciklama"] or "", FS, MUTED).pack(anchor="w", pady=(4,0))

        # Kaldığı yerden devam — Film ve Dizi her ikisi için (docx gereksinimi)
        if pos and pos.get("kalan_sure", 0) > 0:
            pos_box = ctk.CTkFrame(self.content_area, fg_color=RED_DARK,
                                   corner_radius=6, border_width=1, border_color=RED_DIM)
            pos_box.pack(fill="x", padx=16, pady=6)
            pi = ctk.CTkFrame(pos_box, fg_color="transparent")
            pi.pack(padx=14, pady=8, fill="x")
            kaldin_sur = pos["kalan_sure"]
            kaldin_bol = pos.get("bolum_no", 1)
            if p["program_tipi"] == "Dizi":
                devam_msg = f"{kaldin_bol}. bölüm {kaldin_sur}. dakikadan devam etmek ister misiniz?"
            else:
                devam_msg = f"Filmi {kaldin_sur}. dakikadan devam etmek ister misiniz?"
            rlabel(pi, f"⏸  {devam_msg}", FL, RED).pack(side="left")
            def ask_resume(b=kaldin_bol, t=kaldin_sur):
                self.show_watch(pid, b, t)
            def start_over():
                self.show_watch(pid, 1, 0)
            rbtn(pi, "▶ Devam Et", ask_resume,
                 bg=RED, fg=BTN_TXT, w=110, h=28, f=FS).pack(side="right", padx=(4,0))
            rbtn(pi, "Baştan Başla", start_over,
                 bg=CARD2, fg=MUTED, w=110, h=28, f=FS).pack(side="right")

        act = ctk.CTkFrame(self.content_area, fg_color="transparent")
        act.pack(padx=16, pady=6, fill="x")
        ep_var = StringVar()
        if p["program_tipi"] == "Dizi":
            # Bölüm listesini bolum_sayisi'na göre oluştur (tabloya bağımlı değil)
            eps = db.get_episodes(pid)
            if eps:
                epc = [f"Bölüm {e['bolum_no']}" for e in eps]
            else:
                epc = [f"Bölüm {i}" for i in range(1, p["bolum_sayisi"]+1)]
            roption(act, epc, ep_var, w=126, h=32).pack(side="left", padx=(0,6))
            ep_var.set(epc[0])

        def get_ep():
            try: return int(ep_var.get().split()[-1])
            except: return 1

        rbtn(act, "▶  İzle", lambda: self.show_watch(pid, get_ep()),
             w=108, h=34).pack(side="left", padx=(0,6))
        is_fav = db.is_favorite(uid, pid)
        def tf():
            if db.is_favorite(uid, pid): db.remove_from_favorites(uid, pid)
            else: db.add_to_favorites(uid, pid)
            self.show_detail(pid)
        rbtn(act, "♥ Favoriden Çıkar" if is_fav else "♡ Favoriye Ekle", tf,
             bg=RED_DIM if is_fav else CARD2, fg=RED, w=150, h=34).pack(side="left")

        # Kullanıcının verdiği puan
        ur = db.get_user_rating(uid, pid)
        rbox = ctk.CTkFrame(self.content_area, fg_color=SURFACE,
                            corner_radius=6, border_width=1, border_color=BORDER)
        rbox.pack(fill="x", padx=16, pady=4)
        ri2 = ctk.CTkFrame(rbox, fg_color="transparent")
        ri2.pack(padx=14, pady=8, fill="x")
        if ur:
            rlabel(ri2, f"Verdiğiniz puan: ★ {ur}/10", FL, RED).pack(side="left")
        else:
            rlabel(ri2, "Henüz puan vermediniz.", FS, MUTED).pack(side="left")
        rlabel(ri2, "Puan (1–10):", FL, MUTED).pack(side="left", padx=(20,0))
        rv  = StringVar(value=str(ur) if ur else "")
        ctk.CTkEntry(ri2, textvariable=rv, width=56, height=30,
                     fg_color=CARD2, border_color=BORDER2,
                     text_color=RED, font=("Helvetica",13,"bold"),
                     corner_radius=6).pack(side="left", padx=8)
        rm = rlabel(ri2, "", FS, MUTED)
        rm.pack(side="left", padx=6)
        def do_rate():
            if not izledi:
                rm.configure(text="Önce izlemeniz gerekiyor!", text_color="#cc4444"); return
            try:
                puan = int(rv.get()); assert 1<=puan<=10
                db.rate_content(uid, pid, puan)
                rm.configure(text="● Kaydedildi!", text_color=RED)
                self.show_detail(pid)
            except: rm.configure(text="1-10 arası değer.", text_color="#cc4444")
        rbtn(ri2, "Puanla", do_rate, w=80, h=30, f=FS).pack(side="left")

    # ── İZLEME ───────────────────────────────────────
    def show_watch(self, pid, bolum_no=1, start_time=0):
        self._home_content(0)
        p   = db.get_program(pid)
        uid = self.current_user["kullanici_id"]

        rbtn(self.content_area, "← Geri", lambda: self.show_detail(pid),
             bg=CARD2, fg=MUTED, w=78, h=26, f=FS).pack(anchor="w", padx=16, pady=8)

        box = ctk.CTkFrame(self.content_area, fg_color=SURFACE,
                           corner_radius=8, border_width=1, border_color=BORDER)
        box.pack(padx=16, pady=4, fill="x")
        ctk.CTkFrame(box, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(padx=22, pady=14, fill="x")
        rlabel(inner, "▶  İzleme Ekranı", FT, WHITE).pack(anchor="w")
        ctk.CTkFrame(inner, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4,10))
        rlabel(inner, p["program_adi"], FH, WHITE).pack(anchor="w")

        player = ctk.CTkFrame(inner, fg_color=CARD2,
                              width=600, height=170, corner_radius=8,
                              border_width=1, border_color=BORDER2)
        player.pack(pady=10)
        player.pack_propagate(False)
        ctk.CTkLabel(player, text="▶", font=("Helvetica",52), text_color=RED_DIM
                     ).place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(player, text=p["program_adi"].upper(),
                     font=("Helvetica",9), text_color=MUTED
                     ).place(relx=0.5, rely=0.78, anchor="center")

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(fill="x", pady=4)
        for txt in [f"Bölüm {bolum_no}/{p['bolum_sayisi']}", f"Süre {p['bolum_uzunlugu']} dk"]:
            rlabel(info, txt, FL, MUTED).pack(side="left", padx=14)

        # Kaldıgı yerden devam ediyorsa bilgi banner
        if start_time and start_time > 0:
            sb = ctk.CTkFrame(inner, fg_color=RED_DIM, corner_radius=6)
            sb.pack(fill="x", pady=(0,6))
            rlabel(sb, f"  ▶  {bolum_no}. bölüm {start_time}. dakikadan devam ediliyor",
                   FS, RED).pack(padx=10, pady=6, anchor="w")

        df = ctk.CTkFrame(inner, fg_color="transparent")
        df.pack(fill="x", pady=6)
        rlabel(df, "İzleme Süresi (dk):", FL, MUTED).pack(side="left")
        # Kaldığı yerden devam ediyorsa mevcut dakikayı göster
        dur_var = StringVar(value=str(start_time) if start_time and start_time > 0 else "")
        ctk.CTkEntry(df, textvariable=dur_var, width=68, height=30,
                     fg_color=CARD2, border_color=BORDER2, text_color=RED,
                     font=("Helvetica",12,"bold"), corner_radius=6).pack(side="left", padx=8)
        rlabel(df, f"/ {p['bolum_uzunlugu']} dk", FS, MUTED).pack(side="left")

        msg = rlabel(inner, "", FS, MUTED)
        msg.pack()

        def do_save(tam=False):
            try:
                sure = int(dur_var.get()) if dur_var.get() else 0
                if tam:
                    # Tamamlandı: tam süre kaydet, kalan_sure=0 (devam gerekmez)
                    sure = p["bolum_uzunlugu"]
                    kalan = 0
                else:
                    # Yarıda bıraktı: girilen dakikayı kalan_sure olarak kaydet
                    kalan = sure
                db.watch_content(uid, pid, bolum_no, sure, kalan, int(tam))
                msg.configure(text="● "+("Tamamlandı!" if tam else "Kaydedildi!"), text_color=RED)
            except:
                msg.configure(text="Geçerli süre giriniz.", text_color="#cc4444")

        bf = ctk.CTkFrame(inner, fg_color="transparent")
        bf.pack(pady=8)
        rbtn(bf, "● Tamamladım", lambda: do_save(True),
             bg=RED_DIM, fg=RED, w=140, h=34).pack(side="left", padx=6)
        rbtn(bf, "Kaydet", lambda: do_save(False),
             bg=CARD2, fg=MUTED, w=100, h=34).pack(side="left")

        rf = ctk.CTkFrame(inner, fg_color="transparent")
        rf.pack(pady=4)
        rlabel(rf, "Puan (1–10):", FL, MUTED).pack(side="left")
        ur  = db.get_user_rating(uid, pid)
        rv  = StringVar(value=str(ur) if ur else "")
        ctk.CTkEntry(rf, textvariable=rv, width=54, height=28,
                     fg_color=CARD2, border_color=BORDER2, text_color=RED,
                     font=("Helvetica",12,"bold"), corner_radius=6).pack(side="left", padx=8)
        def do_rate():
            try:
                puan=int(rv.get()); assert 1<=puan<=10
                db.rate_content(uid,pid,puan); msg.configure(text="● Puan verildi!", text_color=RED)
            except: msg.configure(text="1-10 arası.", text_color="#cc4444")
        rbtn(rf, "Puanla", do_rate, w=78, h=28, f=FS).pack(side="left")

    # ── FAVORİLER ────────────────────────────────────
    def show_favorites_page(self):
        self._home_content(1)
        uid    = self.current_user["kullanici_id"]
        genres = db.get_genres()
        page_title(self.content_area, "Favoriler", "Kaydettiğiniz içerikler")

        fb = ctk.CTkFrame(self.content_area, fg_color="transparent")
        fb.pack(padx=16, pady=4, anchor="w")
        rlabel(fb, "Türe Göre:", FS, MUTED).pack(side="left")
        tur_list = ["Tümü"] + [g["tur_adi"] for g in genres]
        tur_var  = StringVar(value="Tümü")
        roption(fb, tur_list, tur_var, w=180, h=30).pack(side="left", padx=6)

        res = ctk.CTkFrame(self.content_area, fg_color="transparent")
        res.pack(fill="both", expand=True)

        def refresh():
            tv  = tur_var.get()
            orig = next((g for g in genres if g["tur_adi"]==tv), None)
            tid  = orig["tur_id"] if orig else None
            render_catalog_grid(res, db.get_favorites(uid, tid),
                                self.show_detail, self._toggle_fav, uid)

        rbtn(fb, "Filtrele", refresh, w=86, h=30, f=FS).pack(side="left")
        render_catalog_grid(res, db.get_favorites(uid),
                            self.show_detail, self._toggle_fav, uid)

    # ── GEÇMİŞ ───────────────────────────────────────
    def show_history_page(self):
        self._home_content(2)
        uid  = self.current_user["kullanici_id"]
        hist = db.get_watch_history(uid)
        page_title(self.content_area, "İzleme Geçmişi", "Tüm izleme kayıtlarınız")

        if not hist:
            rlabel(self.content_area, "Henüz izleme kaydı yok.",
                   FB, MUTED, "center").pack(pady=60)
            return

        tbl = ctk.CTkScrollableFrame(self.content_area, fg_color=SURFACE, corner_radius=8)
        tbl.pack(padx=16, pady=6, fill="both", expand=True)

        headers = ["İçerik Adı","Tür","Bölüm","Süre","Puan","Tamamlandı","Tarih"]
        widths   = [210,75,55,65,55,90,145]
        hrow = ctk.CTkFrame(tbl, fg_color=RED_DIM, corner_radius=6)
        hrow.pack(fill="x", padx=4, pady=(4,2))
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hrow, text=h, font=FL, text_color=RED,
                         width=w, anchor="w").pack(side="left", padx=8, pady=6)

        for i, h in enumerate(hist):
            bg  = CARD if i%2==0 else CARD2
            row = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=0, height=30)
            row.pack(fill="x", padx=4, pady=1)
            row.pack_propagate(False)
            # İçerik adı tıklanabilir — detay sayfasına gider
            ctk.CTkButton(row, text=h["program_adi"], font=FS, text_color=RED,
                          fg_color="transparent", hover_color=BORDER,
                          width=210, height=30, anchor="w", corner_radius=0,
                          command=lambda pid=h["program_id"]: self.show_detail(pid)
                          ).pack(side="left", padx=8)
            vals = [h["program_tipi"], str(h["bolum_no"]),
                    f"{h['izleme_suresi']} dk", str(h["puan"] or "—"),
                    "● Evet" if h["tamamlandi"] else "◌ Hayır",
                    h["izleme_tarihi"][:16]]
            tcs = [MUTED,MUTED,MUTED,
                   RED if h["puan"] else MUTED,
                   RED if h["tamamlandi"] else MUTED, MUTED]
            for v, w, tc in zip(vals, widths[1:], tcs):
                ctk.CTkLabel(row, text=v, font=FS, text_color=tc,
                             width=w, anchor="w").pack(side="left", padx=8)

    # ── PROFİL ───────────────────────────────────────
    def show_profile_page(self):
        self._home_content(3)
        uid     = self.current_user["kullanici_id"]
        prof    = db.get_user_profile(uid)
        fav_tur = db.get_user_fav_genres(uid)
        page_title(self.content_area, "Profil", "Hesap bilgileriniz")

        # Kullanıcı bilgi özeti
        info_bar = ctk.CTkFrame(self.content_area, fg_color=SURFACE,
                                corner_radius=8, border_width=1, border_color=BORDER)
        info_bar.pack(fill="x", padx=16, pady=(0,8))
        ctk.CTkFrame(info_bar, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        ib = ctk.CTkFrame(info_bar, fg_color="transparent")
        ib.pack(padx=16, pady=10, fill="x")
        dogum_str = prof.get("dogum_tarihi") or "—"
        for lbl, val in [("Ad Soyad", f"{prof['ad']} {prof['soyad']}"),
                         ("E-posta", prof["email"]),
                         ("Doğum Tarihi", dogum_str),
                         ("Ülke", prof.get("ulke") or "—"),
                         ("Favori Türler", ", ".join(fav_tur) if fav_tur else "—")]:
            rf = ctk.CTkFrame(ib, fg_color="transparent")
            rf.pack(anchor="w", pady=1)
            rlabel(rf, f"{lbl}: ", FS, MUTED).pack(side="left")
            rlabel(rf, val, FS, WHITE).pack(side="left")

        sr = ctk.CTkFrame(self.content_area, fg_color="transparent")
        sr.pack(padx=16, fill="x", pady=(0,12))
        for ico, lbl, val in [
            ("▶","İzlenen", str(prof["izlenen_sayi"])),
            ("◎","Süre", f"{prof['toplam_sure']} dk"),
            ("★","Puan", f"{round(prof['ort_puan'] or 0,1)}/10")
        ]:
            c = ctk.CTkFrame(sr, fg_color=CARD, corner_radius=8,
                             border_width=1, border_color=BORDER2, width=180)
            c.pack(side="left", padx=6)
            ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
            ctk.CTkLabel(c, text=ico, font=("Helvetica",24), text_color=RED).pack(pady=(10,2))
            ctk.CTkLabel(c, text=val, font=("Helvetica",16,"bold"), text_color=WHITE).pack()
            rlabel(c, lbl, FS, MUTED, "center").pack(pady=(0,10))

        fb = ctk.CTkFrame(self.content_area, fg_color=SURFACE,
                          corner_radius=8, border_width=1, border_color=BORDER)
        fb.pack(fill="x", padx=16, pady=6)
        ctk.CTkFrame(fb, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        fi = ctk.CTkFrame(fb, fg_color="transparent")
        fi.pack(padx=18, pady=14, fill="x")
        rlabel(fi, "Profil Güncelle", FH, WHITE).pack(anchor="w")
        ctk.CTkFrame(fi, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4,12))

        fields = {}
        eg = ctk.CTkFrame(fi, fg_color="transparent")
        eg.pack(fill="x")
        for i, (lbl, key, val) in enumerate([
            ("Ad","ad",prof["ad"]), ("Soyad","soyad",prof["soyad"]),
            ("E-posta","email",prof["email"]), ("Ülke","ulke",prof["ulke"] or "")
        ]):
            cf = ctk.CTkFrame(eg, fg_color="transparent")
            cf.grid(row=i//2, column=i%2, padx=6, pady=3, sticky="w")
            rlabel(cf, lbl, FS, MUTED).pack(anchor="w")
            e = rentry(cf, lbl.lower(), w=240, h=32)
            e.insert(0, val); e.pack()
            fields[key] = e

        # Doğum tarihi alanı
        rlabel(fi, "Doğum Tarihi (YYYY-MM-DD)", FS, MUTED).pack(anchor="w", pady=(8,2))
        dogum_e = rentry(fi, "YYYY-MM-DD", w=240, h=32)
        dogum_e.insert(0, prof.get("dogum_tarihi") or "")
        dogum_e.pack(anchor="w")

        rlabel(fi, "Yeni Şifre (boş = değişmez)", FS, MUTED).pack(anchor="w", pady=(8,2))
        sifre_e = rentry(fi, "yeni şifre...", show="•", w=240, h=32)
        sifre_e.pack(anchor="w")

        # Favori türler — güncellenebilir checkbox listesi
        rlabel(fi, "Favori Türler (3 seçiniz)", FS, MUTED).pack(anchor="w", pady=(10,4))
        all_genres = db.get_genres()
        tur_vars = {}
        gf = ctk.CTkFrame(fi, fg_color=CARD2, corner_radius=6)
        gf.pack(fill="x", pady=(0,6))
        for i, g in enumerate(all_genres):
            v = tk.BooleanVar(value=(g["tur_adi"] in fav_tur))
            tur_vars[g["tur_id"]] = v
            ctk.CTkCheckBox(gf, text=g["tur_adi"], variable=v,
                            text_color=WHITE, font=FS, fg_color=RED,
                            hover_color=RED2, checkmark_color=BG,
                            corner_radius=3).grid(row=i//3, column=i%3,
                                                  sticky="w", padx=10, pady=4)

        msg = rlabel(fi, "", FS, RED)
        msg.pack(anchor="w", pady=2)

        def do_upd():
            ad=fields["ad"].get().strip(); soyad=fields["soyad"].get().strip()
            email=fields["email"].get().strip(); ulke=fields["ulke"].get().strip()
            sifre=sifre_e.get().strip()
            dogum=dogum_e.get().strip()
            if not all([ad,soyad,email]):
                msg.configure(text="Ad, soyad ve e-posta zorunludur.", text_color="#cc4444"); return
            # Doğum tarihi kontrolü
            if dogum:
                try:
                    dt = datetime.strptime(dogum, "%Y-%m-%d")
                    if dt > datetime.now():
                        msg.configure(text="Doğum tarihi bugünden büyük olamaz.", text_color="#cc4444"); return
                except ValueError:
                    msg.configure(text="Tarih formatı: YYYY-MM-DD", text_color="#cc4444"); return
            # Favori tür kontrolü
            sel = [tid for tid, v in tur_vars.items() if v.get()]
            if len(sel) != 3:
                msg.configure(text="Tam olarak 3 favori tür seçiniz.", text_color="#cc4444"); return
            db.update_profile(uid, ad, soyad, email, ulke, sifre or None, dogum or None, sel)
            self.current_user["ad"] = ad
            msg.configure(text="● Güncellendi!", text_color=RED)

        rbtn(fi, "● Güncelle", do_upd, w=130, h=34).pack(anchor="w", pady=8)

    # ══ ADMİN ════════════════════════════════════════
    def show_admin(self):
        clear(self.root)
        self._setup_admin_sidebar(0)

    def _setup_admin_sidebar(self, active):
        if hasattr(self, "_wrap") and self._wrap.winfo_exists():
            self._wrap.destroy()
        self._wrap = ctk.CTkFrame(self.root, fg_color=BG)
        self._wrap.pack(fill="both", expand=True)

        items = [("▶","İçerikler",self.admin_content),
                 ("◈","Türler",   self.admin_genres),
                 ("◎","Kullanıcılar",self.admin_users),
                 ("★","Raporlar", self.admin_reports)]

        sb = ctk.CTkFrame(self._wrap, fg_color=SIDEBAR, corner_radius=0, width=SIDEBAR_W)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkFrame(sb, fg_color=BORDER, width=1).pack(side="right", fill="y")
        # Brand + Çıkış
        top = ctk.CTkFrame(sb, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(12,4))
        ctk.CTkLabel(top, text="CRi", font=("Helvetica",14,"bold"),
                     text_color=RED).pack(side="left")
        ctk.CTkLabel(top, text="MSON", font=("Helvetica",14,"bold"),
                     text_color=WHITE).pack(side="left")
        ctk.CTkFrame(sb, fg_color=BORDER, height=1).pack(fill="x", padx=10)
        ctk.CTkLabel(sb, text="YÖNETİM", font=("Helvetica",8,"bold"),
                     text_color=MUTED2).pack(anchor="w", padx=14, pady=(10,6))
        for i, (ico, lbl, cmd) in enumerate(items):
            is_a = (i == active)
            fr = ctk.CTkFrame(sb, fg_color=CARD if is_a else "transparent",
                              corner_radius=0, height=38)
            fr.pack(fill="x")
            fr.pack_propagate(False)
            ctk.CTkFrame(fr, fg_color=RED if is_a else "transparent",
                         width=3, corner_radius=0).pack(side="left", fill="y")
            ctk.CTkButton(fr, text=f"{ico}  {lbl}", command=cmd,
                          fg_color="transparent", hover_color=CARD,
                          text_color=WHITE if is_a else MUTED,
                          font=FS, anchor="w",
                          width=SIDEBAR_W-3, height=38, corner_radius=0).pack(fill="both")

        # Alt: çıkış butonu
        rbtn(sb, "Çıkış", self.show_login, bg=CARD2, fg=MUTED,
             w=SIDEBAR_W-20, h=28, f=FS).pack(side="bottom", padx=10, pady=8)
        if self.current_user:
            rlabel(sb, self.current_user["ad"], FS, MUTED).pack(
                side="bottom", padx=14, pady=(0,2))

        self.admin_area = ctk.CTkScrollableFrame(self._wrap, fg_color=BG, corner_radius=0)
        self.admin_area.pack(side="left", fill="both", expand=True)

    def _admin_nav(self, active):
        clear(self.root)
        self._setup_admin_sidebar(active)

    # ── ADMİN İÇERİK ─────────────────────────────────
    def admin_content(self):
        self._admin_nav(0)

        # Başlık + Yeni Ekle butonu yan yana
        hrow = ctk.CTkFrame(self.admin_area, fg_color="transparent")
        hrow.pack(fill="x", padx=16, pady=(16, 4))
        fl = ctk.CTkFrame(hrow, fg_color="transparent")
        fl.pack(side="left")
        rlabel(fl, "İçerik Yönetimi", FT, WHITE).pack(anchor="w")
        ctk.CTkFrame(fl, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4, 0))
        rbtn(hrow, "+ Yeni İçerik", self._admin_add_program_popup,
             w=130, h=34, f=FS).pack(side="right")

        # Arama/filtreleme çubuğu
        fbar = ctk.CTkFrame(self.admin_area, fg_color=SURFACE, corner_radius=6)
        fbar.pack(fill="x", padx=16, pady=4)
        fb_inner = ctk.CTkFrame(fbar, fg_color="transparent")
        fb_inner.pack(padx=12, pady=8, fill="x")
        rlabel(fb_inner, "Ara:", FS, MUTED).pack(side="left")
        admin_search_var = StringVar()
        ctk.CTkEntry(fb_inner, textvariable=admin_search_var,
                     placeholder_text="program adı...", width=200, height=28,
                     fg_color=CARD2, border_color=BORDER2, text_color=WHITE,
                     font=FS, corner_radius=6).pack(side="left", padx=6)
        admin_tip_var = StringVar(value="Tümü")
        roption(fb_inner, ["Tümü","Film","Dizi","Tv Show"], admin_tip_var, w=96, h=28).pack(side="left", padx=4)

        grid_frame = ctk.CTkFrame(self.admin_area, fg_color="transparent")

        def do_admin_search():
            for w in grid_frame.winfo_children():
                w.destroy()
            sq  = admin_search_var.get().strip()
            tip = None if admin_tip_var.get() == "Tümü" else admin_tip_var.get()
            progs = db.get_programs(sq, tip=tip)
            rlabel(grid_frame, f"  {len(progs)} kayıt", FS, MUTED2).pack(
                anchor="w", padx=4, pady=(4, 2))
            g = ctk.CTkFrame(grid_frame, fg_color="transparent")
            g.pack(fill="x", padx=4)
            COLS = 5
            for i, p in enumerate(progs):
                admin_content_card(g, p, self._admin_edit_program,
                                   self._admin_delete, i//COLS, i%COLS)

        rbtn(fb_inner, "Ara", do_admin_search, w=68, h=28, f=FS).pack(side="left", padx=6)
        rbtn(fb_inner, "Tümü Göster",
             lambda: (admin_search_var.set(""), admin_tip_var.set("Tümü"), do_admin_search()),
             bg=CARD2, fg=MUTED, w=100, h=28, f=FS).pack(side="left", padx=2)

        grid_frame.pack(fill="x", padx=12, pady=4)
        do_admin_search()


    def _admin_add_program_popup(self):
        win = ctk.CTkToplevel(self)
        win.title("Yeni İçerik Ekle")
        win.geometry("600x500")
        win.configure(fg_color=BG)
        ctk.CTkFrame(win, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        inner = ctk.CTkScrollableFrame(win, fg_color=BG)
        inner.pack(fill="both", expand=True, padx=20, pady=16)
        rlabel(inner, "Yeni İçerik Ekle", FH, WHITE).pack(anchor="w")
        ctk.CTkFrame(inner, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4, 10))

        fr = ctk.CTkFrame(inner, fg_color="transparent")
        fr.pack(fill="x")
        fields = {}
        for lbl, key, w in [("Program Adı","adi",190),("Yayın Yılı","yil",78),
                             ("Bölüm Sayısı","bolum",78),("Süre (dk)","sure",78)]:
            cf = ctk.CTkFrame(fr, fg_color="transparent")
            cf.pack(side="left", padx=5)
            rlabel(cf, lbl, FS, MUTED).pack(anchor="w")
            e = rentry(cf, lbl.lower(), w=w, h=32)
            e.pack(); fields[key] = e

        f2 = ctk.CTkFrame(inner, fg_color="transparent")
        f2.pack(fill="x", pady=6)
        rlabel(f2, "Tip:", FS, MUTED).pack(side="left")
        tip_var = StringVar(value="Film")
        roption(f2, ["Film","Dizi","Tv Show"], tip_var, w=100, h=30).pack(side="left", padx=6)

        genres = db.get_genres()
        tur_vars = {}
        gf = ctk.CTkFrame(inner, fg_color=CARD2, corner_radius=6)
        gf.pack(fill="x", pady=4)
        rlabel(gf, "Türler:", FS, MUTED).pack(anchor="w", padx=10, pady=(6,0))
        gg = ctk.CTkFrame(gf, fg_color="transparent")
        gg.pack(anchor="w", padx=10, pady=6)
        for i, g in enumerate(genres):
            v = tk.BooleanVar()
            tur_vars[g["tur_id"]] = v
            ctk.CTkCheckBox(gg, text=g["tur_adi"], variable=v,
                            text_color=MUTED, font=FS, fg_color=RED,
                            hover_color=RED2, checkmark_color=BG,
                            corner_radius=3).grid(row=i//4, column=i%4,
                                                  sticky="w", padx=8, pady=2)

        rlabel(inner, "Açıklama:", FS, MUTED).pack(anchor="w", pady=(6,2))
        desc_e = ctk.CTkTextbox(inner, width=520, height=50,
                                fg_color=CARD2, border_color=BORDER2,
                                text_color=WHITE, font=FS, corner_radius=6)
        desc_e.pack(anchor="w")
        msg = rlabel(inner, "", FS, RED)
        msg.pack(anchor="w", pady=4)

        def do_add():
            adi = fields["adi"].get().strip()
            if not adi:
                msg.configure(text="Program adı zorunludur.", text_color="#cc4444"); return
            try:
                yil  = int(fields["yil"].get())  if fields["yil"].get()  else None
                bol  = int(fields["bolum"].get()) if fields["bolum"].get() else 1
                sure = int(fields["sure"].get())  if fields["sure"].get() else 90
            except:
                msg.configure(text="Sayısal alanlara sayı girin.", text_color="#cc4444"); return
            sel = [tid for tid, v in tur_vars.items() if v.get()]
            db.add_program(adi, tip_var.get(), bol, sure, yil,
                           desc_e.get("1.0","end").strip(), sel)
            msg.configure(text="● Eklendi!", text_color=RED)
            self.admin_content()
            win.after(900, win.destroy)

        rbtn(inner, "● Ekle", do_add, w=110, h=34).pack(pady=8)

    def _admin_edit_program(self, pid):
        p   = db.get_program(pid)
        win = ctk.CTkToplevel(self)
        win.title("Düzenle")
        win.geometry("580x480")
        win.configure(fg_color=BG)
        ctk.CTkFrame(win, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        inner = ctk.CTkScrollableFrame(win, fg_color=BG)
        inner.pack(fill="both", expand=True, padx=18, pady=14)
        rlabel(inner, "İçerik Düzenle", FH, WHITE).pack(anchor="w")
        ctk.CTkFrame(inner, fg_color=RED, height=2, width=32,
                     corner_radius=0).pack(anchor="w", pady=(4,10))
        fields = {}
        for lbl, key, val in [("Program Adı","adi",p["program_adi"]),
                               ("Yayın Yılı","yil",str(p["yayin_yili"] or "")),
                               ("Bölüm Sayısı","bolum",str(p["bolum_sayisi"])),
                               ("Süre (dk)","sure",str(p["bolum_uzunlugu"]))]:
            rlabel(inner, lbl, FS, MUTED).pack(anchor="w")
            e = rentry(inner, lbl.lower(), w=420, h=32)
            e.insert(0, val); e.pack(anchor="w", pady=(2,8)); fields[key] = e

        tip_var = StringVar(value=p["program_tipi"])
        roption(inner, ["Film","Dizi","Tv Show"], tip_var, w=120, h=30).pack(anchor="w", pady=4)

        genres     = db.get_genres()
        cur_turler = (p["turler"] or "").split(",")
        tur_vars   = {}
        gf = ctk.CTkFrame(inner, fg_color=CARD2, corner_radius=6)
        gf.pack(fill="x", pady=4)
        gg = ctk.CTkFrame(gf, fg_color="transparent")
        gg.pack(anchor="w", padx=10, pady=6)
        for i, g in enumerate(genres):
            v = tk.BooleanVar(value=g["tur_adi"].strip() in [t.strip() for t in cur_turler])
            tur_vars[g["tur_id"]] = v
            ctk.CTkCheckBox(gg, text=g["tur_adi"], variable=v,
                            text_color=MUTED, font=FS, fg_color=RED,
                            hover_color=RED2, checkmark_color=BG,
                            corner_radius=3).grid(row=i//3, column=i%3,
                                                  sticky="w", padx=6, pady=2)
        rlabel(inner, "Açıklama:", FS, MUTED).pack(anchor="w", pady=(6,2))
        desc_e = ctk.CTkTextbox(inner, width=480, height=50,
                                fg_color=CARD2, border_color=BORDER2,
                                text_color=WHITE, font=FS, corner_radius=6)
        desc_e.insert("1.0", p["aciklama"] or "")
        desc_e.pack(anchor="w")
        msg = rlabel(inner, "", FS, RED)
        msg.pack(anchor="w", pady=4)

        def do_upd():
            try:
                yil  = int(fields["yil"].get())  if fields["yil"].get()  else None
                bol  = int(fields["bolum"].get()) if fields["bolum"].get() else 1
                sure = int(fields["sure"].get())  if fields["sure"].get() else 90
            except:
                msg.configure(text="Sayısal alanlara sayı girin.", text_color="#cc4444"); return
            db.update_program(pid, fields["adi"].get().strip(), tip_var.get(),
                              bol, sure, yil, desc_e.get("1.0","end").strip(),
                              [tid for tid,v in tur_vars.items() if v.get()])
            msg.configure(text="● Güncellendi!", text_color=RED)
            self.admin_content(); win.after(800, win.destroy)

        rbtn(inner, "● Güncelle", do_upd, w=130, h=32).pack(pady=8)

    def _admin_delete(self, pid):
        if messagebox.askyesno("Sil", "Bu içeriği silmek istiyor musunuz?"):
            db.delete_program(pid)
            self.admin_content()

    # ── ADMİN TÜRLER ─────────────────────────────────
    def admin_genres(self):
        self._admin_nav(1)
        page_title(self.admin_area, "Tür Yönetimi", "Tür ekle, güncelle veya sil")

        abox = ctk.CTkFrame(self.admin_area, fg_color=SURFACE,
                            corner_radius=8, border_width=1, border_color=BORDER)
        abox.pack(fill="x", padx=16, pady=6)
        ctk.CTkFrame(abox, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        af = ctk.CTkFrame(abox, fg_color="transparent")
        af.pack(padx=18, pady=12, fill="x")
        rlabel(af, "Yeni Tür:", FS, MUTED).pack(side="left", padx=(0,6))
        tur_e = rentry(af, "tür adı...", w=240, h=30)
        tur_e.pack(side="left")
        add_msg = rlabel(af, "", FS, RED)

        def do_add():
            ok, txt = db.add_genre(tur_e.get().strip())
            add_msg.configure(text=txt, text_color=RED if ok else "#cc4444")
            if ok: tur_e.delete(0,"end"); self.admin_genres()

        rbtn(af, "Ekle", do_add, w=76, h=30, f=FS).pack(side="left", padx=6)
        add_msg.pack(side="left", padx=6)

        rlabel(self.admin_area, "Mevcut Türler", FL, MUTED2).pack(
            anchor="w", padx=20, pady=(12,4))
        grid = ctk.CTkFrame(self.admin_area, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=4)
        genres = db.get_genres()
        COLS = 5
        for i, g in enumerate(genres):
            c = ctk.CTkFrame(grid, fg_color=CARD, corner_radius=8,
                             border_width=1, border_color=BORDER2, width=200)
            c.grid(row=i//COLS, column=i%COLS, padx=5, pady=5, sticky="n")
            ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
            rlabel(c, g["tur_adi"], FH, WHITE).pack(padx=10, pady=(10,6), anchor="w")
            ctk.CTkFrame(c, fg_color=BORDER, height=1).pack(fill="x")
            btns = ctk.CTkFrame(c, fg_color=CARD2, corner_radius=0)
            btns.pack(fill="x")
            def do_del(tid=g["tur_id"]):
                ok, txt = db.delete_genre(tid)
                if not ok: messagebox.showerror("Hata", txt)
                else: self.admin_genres()
            def do_edit(tid=g["tur_id"], eski=g["tur_adi"]):
                self._admin_edit_genre(tid, eski)
            rbtn(btns, "Düzenle", do_edit, bg=CARD2, fg=MUTED, w=100, h=28, f=FS).pack(side="left")
            rbtn(btns, "Sil", do_del, bg=RED_DIM, fg=RED, w=72, h=28, f=FS).pack(side="left")

    def _admin_edit_genre(self, tur_id, eski_adi):
        win = ctk.CTkToplevel(self)
        win.title("Tür Düzenle")
        win.geometry("360x170")
        win.configure(fg_color=BG)
        ctk.CTkFrame(win, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        inner = ctk.CTkFrame(win, fg_color=BG)
        inner.pack(fill="both", expand=True, padx=18, pady=14)
        rlabel(inner, f"Mevcut: {eski_adi}", FS, MUTED).pack(anchor="w")
        tur_e = rentry(inner, "yeni ad...", w=300, h=32)
        tur_e.insert(0, eski_adi); tur_e.pack(pady=6)
        msg = rlabel(inner, "", FS, RED); msg.pack()
        def do_upd():
            ok, txt = db.update_genre(tur_id, tur_e.get().strip())
            msg.configure(text=txt, text_color=RED if ok else "#cc4444")
            if ok: self.admin_genres(); win.after(800, win.destroy)
        rbtn(inner, "● Güncelle", do_upd, w=120, h=30).pack(pady=4)

    # ── ADMİN KULLANICILAR ───────────────────────────
    def admin_users(self):
        self._admin_nav(2)
        page_title(self.admin_area, "Kullanıcı Yönetimi", "Kullanıcıları görüntüle ve yönet")
        users = db.get_all_users()

        tbl = ctk.CTkScrollableFrame(self.admin_area, fg_color=SURFACE, corner_radius=8)
        tbl.pack(padx=16, pady=6, fill="both", expand=True)
        headers = ["Ad Soyad","E-posta","Rol","Kayıt","İzlenen","Süre","Durum","İşlem"]
        widths   = [140,185,75,95,55,75,75,175]
        hrow = ctk.CTkFrame(tbl, fg_color=RED_DIM, corner_radius=6)
        hrow.pack(fill="x", padx=4, pady=(4,2))
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hrow, text=h, font=FL, text_color=RED,
                         width=w, anchor="w").pack(side="left", padx=8, pady=6)

        for i, u in enumerate(users):
            bg  = CARD if i%2==0 else CARD2
            row = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=0, height=32)
            row.pack(fill="x", padx=4, pady=1)
            row.pack_propagate(False)
            for v, w in zip([u["ad"]+" "+u["soyad"], u["email"], u["rol_adi"],
                             (u["kayit_tarihi"] or "")[:10],
                             str(u["izlenen_sayi"]), str(u["toplam_sure"])+" dk"],
                            widths[:6]):
                ctk.CTkLabel(row, text=v, font=FS, text_color=WHITE,
                             width=w, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(row, text="● Aktif" if u["aktif"] else "◌ Pasif",
                         font=FS, text_color=RED if u["aktif"] else MUTED,
                         width=75).pack(side="left", padx=8)
            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.pack(side="left")
            def do_tog(uid=u["kullanici_id"], cur=u["aktif"]):
                db.toggle_user_active(uid, 0 if cur else 1); self.admin_users()
            isim = u["ad"]+" "+u["soyad"]
            rbtn(bf, "Pasif" if u["aktif"] else "Aktif", do_tog,
                 bg=RED_DIM if u["aktif"] else CARD2,
                 fg=RED if u["aktif"] else MUTED, w=58, h=22, f=FS).pack(side="left", padx=2)
            rbtn(bf, "Geçmiş",
                 lambda uid=u["kullanici_id"], isim=isim: self._admin_user_history(uid, isim),
                 bg=CARD2, fg=MUTED, w=58, h=22, f=FS).pack(side="left", padx=2)

    def _admin_user_history(self, uid, isim):
        win = ctk.CTkToplevel(self)
        win.title(f"Kullanıcı Detayı — {isim}")
        win.geometry("820x540")
        win.configure(fg_color=BG)
        ctk.CTkFrame(win, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
        rlabel(win, f"  {isim} — Detay & İzleme Geçmişi", FH, WHITE).pack(padx=18, pady=10, anchor="w")

        # Kullanıcı detay bilgileri
        prof = db.get_user_profile(uid)
        fav_tur = db.get_user_fav_genres(uid)
        if prof:
            info = ctk.CTkFrame(win, fg_color=SURFACE, corner_radius=6)
            info.pack(fill="x", padx=18, pady=(0,8))
            ir = ctk.CTkFrame(info, fg_color="transparent")
            ir.pack(padx=14, pady=8, fill="x")
            for lbl, val in [
                ("E-posta", prof.get("email","—")),
                ("Doğum Tarihi", prof.get("dogum_tarihi") or "—"),
                ("Ülke", prof.get("ulke") or "—"),
                ("Cinsiyet", prof.get("cinsiyet") or "—"),
                ("Kayıt Tarihi", (prof.get("kayit_tarihi") or "")[:10]),
                ("Favori Türler", ", ".join(fav_tur) if fav_tur else "—"),
                ("İzlenen İçerik", str(prof.get("izlenen_sayi", 0))),
                ("Toplam İzleme Süresi", f"{prof.get('toplam_sure', 0)} dk"),
                ("Ort. Puan", f"{round(prof.get('ort_puan') or 0, 1)}/10"),
            ]:
                rf = ctk.CTkFrame(ir, fg_color="transparent")
                rf.pack(side="left", padx=10)
                rlabel(rf, lbl+":", FS, MUTED).pack(anchor="w")
                rlabel(rf, val, FS, WHITE).pack(anchor="w")

        hist = db.get_user_watch_history(uid)
        if not hist:
            rlabel(win, "İzleme kaydı yok.", FB, MUTED).pack(pady=20); return
        tbl = ctk.CTkScrollableFrame(win, fg_color=SURFACE, corner_radius=8)
        tbl.pack(padx=18, pady=8, fill="both", expand=True)
        headers = ["İçerik","Tür","Bölüm","Süre","Puan","Tamamlandı","Tarih"]
        widths   = [210,68,55,65,55,88,145]
        hrow = ctk.CTkFrame(tbl, fg_color=RED_DIM, corner_radius=4)
        hrow.pack(fill="x", padx=4, pady=(4,2))
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hrow, text=h, font=FL, text_color=RED,
                         width=w, anchor="w").pack(side="left", padx=8, pady=5)
        for i, h in enumerate(hist):
            bg  = CARD if i%2==0 else CARD2
            row = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=0, height=28)
            row.pack(fill="x", padx=4, pady=1)
            row.pack_propagate(False)
            for v, w in zip([h["program_adi"], h["program_tipi"], str(h["bolum_no"]),
                             f"{h['izleme_suresi']} dk", str(h["puan"] or "—"),
                             "● Evet" if h["tamamlandi"] else "◌ Hayır",
                             h["izleme_tarihi"][:16]], widths):
                ctk.CTkLabel(row, text=v, font=FS, text_color=WHITE,
                             width=w, anchor="w").pack(side="left", padx=8)

    # ── ADMİN RAPORLAR ───────────────────────────────
    def admin_reports(self):
        self._admin_nav(3)
        page_title(self.admin_area, "Raporlar", "Platform istatistikleri")
        reports = db.get_reports()

        sr = ctk.CTkFrame(self.admin_area, fg_color="transparent")
        sr.pack(padx=16, pady=6, fill="x")
        for ico, lbl, val in [("◎","Aktif Kullanıcı",reports["kullanici_sayisi"]),
                              ("▶","Toplam İzlenme", reports["toplam_izlenme"]),
                              ("★","Toplam Puan",    reports["toplam_puan"])]:
            c = ctk.CTkFrame(sr, fg_color=CARD, corner_radius=8,
                             border_width=1, border_color=BORDER2, width=180)
            c.pack(side="left", padx=6)
            ctk.CTkFrame(c, fg_color=RED, height=2, corner_radius=0).pack(fill="x")
            ctk.CTkLabel(c, text=ico, font=("Helvetica",22), text_color=RED).pack(pady=(10,2))
            ctk.CTkLabel(c, text=str(val), font=("Helvetica",18,"bold"), text_color=WHITE).pack()
            rlabel(c, lbl, FS, MUTED, "center").pack(pady=(0,10))

        def rtable(title, data, cols):
            rlabel(self.admin_area, title, FL, MUTED2).pack(
                anchor="w", padx=20, pady=(12,4))
            if not data:
                rlabel(self.admin_area, "Veri yok", FS, MUTED).pack(anchor="w", padx=24); return
            box = ctk.CTkFrame(self.admin_area, fg_color=SURFACE, corner_radius=8)
            box.pack(padx=16, pady=4, fill="x")
            for i, rd in enumerate(data):
                bg  = CARD if i%2==0 else CARD2
                row = ctk.CTkFrame(box, fg_color=bg, corner_radius=0, height=28)
                row.pack(fill="x", padx=6, pady=1)
                row.pack_propagate(False)
                ctk.CTkLabel(row, text=f"{i+1:02d}", font=FS,
                             text_color=MUTED2, width=26).pack(side="left", padx=6)
                for col, w in cols:
                    val = str(rd.get(col,""))
                    if col=="ort_puan": val=f"★ {round(float(val),1)}"
                    elif col in ("izlenme_sayisi","toplam_izlenme"): val=f"▸ {val}"
                    ctk.CTkLabel(row, text=val, font=FS, text_color=WHITE,
                                 width=w, anchor="w").pack(side="left", padx=6)

        rtable("En Çok İzlenen 10 İçerik", reports["en_cok_izlenen"],
               [("program_adi",280),("program_tipi",70),("izlenme_sayisi",90),("ort_puan",90)])
        rtable("En Yüksek Puanlı 10 İçerik", reports["en_yuksek_puanli"],
               [("program_adi",280),("program_tipi",70),("ort_puan",90)])
        rtable("En Çok İzlenen Türler", reports["en_cok_izlenen_turler"],
               [("tur_adi",260),("toplam_izlenme",110)])
        rtable("En Aktif Kullanıcılar", reports["en_aktif_kullanici"],
               [("isim",200),("izleme_sayisi",110),("toplam_sure",110)])
        rtable("Son 7 Gün", reports["son_7_gun"],
               [("program_adi",280),("izleme_sayisi",110)])


if __name__ == "__main__":
    app = App()
    app.mainloop()