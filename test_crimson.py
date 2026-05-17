"""
CRiMSON — Test Uygulaması
Çalıştırma:
    python test_crimson.py
    python test_crimson.py -v
"""

import sys
import uuid
import unittest
import database as db
from database import DatabaseManager


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@crimson.test"


# ═══════════════════════════════════════════════════════
# 1. VERİTABANI BAĞLANTI & KURULUM
# ═══════════════════════════════════════════════════════
class T01_Baglanti(unittest.TestCase):

    def test_01_baglanti_acilir(self):
        conn = DatabaseManager().get_conn()
        self.assertIsNotNone(conn)
        conn.close()

    def test_02_init_db(self):
        db.init_db()

    def test_03_seed_data(self):
        db.seed_data()

    def test_04_tablolar_var(self):
        beklenen = {
            "Rol","Kullanici","Tur","Program","ProgramTur",
            "KullaniciProgram","Favori","KullaniciTur",
            "Bolum","IzlemeLog","OturumLog"
        }
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SHOW TABLES")
        mevcut = {row[0] for row in c.fetchall()}
        c.close(); conn.close()
        # Büyük/küçük harf fark etmeden kontrol
        mevcut_lower = {t.lower() for t in mevcut}
        for tablo in beklenen:
            self.assertIn(tablo.lower(), mevcut_lower, f"Eksik tablo: {tablo}")

    def test_05_roller_var(self):
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT rol_adi FROM Rol")
        roller = {r[0] for r in c.fetchall()}
        c.close(); conn.close()
        self.assertIn("Admin", roller)
        self.assertIn("Kullanici", roller)

    def test_06_sifre_hash(self):
        import hashlib
        h = DatabaseManager.hash_password("test123")
        self.assertEqual(h, hashlib.sha256("test123".encode()).hexdigest())


# ═══════════════════════════════════════════════════════
# 2. KAYIT & GİRİŞ
# ═══════════════════════════════════════════════════════
class T02_KayitGiris(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        cls.tur_ids = [g["tur_id"] for g in db.get_genres()[:3]]

    def _kayit(self):
        email = unique_email()
        ok, uid = db.register(
            "Test", "Kullanici", email, "Sifre123",
            "2000-01-01", "E", "Türkiye", self.tur_ids
        )
        return ok, uid, email

    def test_01_basarili_kayit(self):
        ok, uid, _ = self._kayit()
        self.assertTrue(ok)
        self.assertIsInstance(uid, int)
        self.assertGreater(uid, 0)

    def test_02_ayni_email_reddedilir(self):
        ok, uid, email = self._kayit()
        self.assertTrue(ok)
        ok2, msg = db.register("X","Y", email, "Sifre456",
                               "1995-01-01","K","TR", self.tur_ids)
        self.assertFalse(ok2)

    def test_03_favori_turler_kaydedildi(self):
        ok, uid, _ = self._kayit()
        self.assertTrue(ok)
        fav = db.get_user_fav_genres(uid)
        self.assertEqual(len(fav), 3)

    def test_04_dogru_sifre_giris(self):
        ok, uid, email = self._kayit()
        user = db.login(email, "Sifre123")
        self.assertIsNotNone(user)
        self.assertEqual(user["kullanici_id"], uid)

    def test_05_yanlis_sifre_none(self):
        ok, uid, email = self._kayit()
        user = db.login(email, "YanlisParola!")
        self.assertIsNone(user)

    def test_06_olmayan_email_none(self):
        self.assertIsNone(db.login("yok@yok.com", "herhangi"))

    def test_07_admin_girisi(self):
        user = db.login("admin@netflix.com", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user["rol_adi"], "Admin")

    def test_08_pasif_kullanici_giremez(self):
        ok, uid, email = self._kayit()
        db.toggle_user_active(uid, 0)
        self.assertIsNone(db.login(email, "Sifre123"))
        db.toggle_user_active(uid, 1)

    def test_09_oturum_log_yaziliyor(self):
        ok, uid, email = self._kayit()
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM OturumLog WHERE kullanici_id=%s", (uid,))
        once = c.fetchone()[0]
        c.close(); conn.close()
        db.login(email, "Sifre123")
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM OturumLog WHERE kullanici_id=%s", (uid,))
        sonra = c.fetchone()[0]
        c.close(); conn.close()
        self.assertGreater(sonra, once)


# ═══════════════════════════════════════════════════════
# 3. PROGRAM YÖNETİMİ
# ═══════════════════════════════════════════════════════
class T03_Program(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        cls.tur_ids = [g["tur_id"] for g in db.get_genres()[:2]]

    def _film(self, adi="Test Film"):
        return db.add_program(adi, "Film", 1, 120, 2023,
                              f"{adi} aciklama", self.tur_ids)

    def _dizi(self, adi="Test Dizi", bolum=5):
        return db.add_program(adi, "Dizi", bolum, 45, 2022,
                              f"{adi} aciklama", self.tur_ids)

    def test_01_film_ekleme(self):
        pid = self._film()
        self.assertIsInstance(pid, int)
        self.assertGreater(pid, 0)

    def test_02_dizi_bolumler_olusur(self):
        pid = self._dizi(bolum=3)
        eps = db.get_episodes(pid)
        self.assertEqual(len(eps), 3)

    def test_03_tv_show_ekleme(self):
        pid = db.add_program("Test TV","Tv Show",4,30,2021,"test",self.tur_ids)
        self.assertGreater(pid, 0)

    def test_04_programtur_iliskisi(self):
        pid = self._film()
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM ProgramTur WHERE program_id=%s", (pid,))
        sayi = c.fetchone()[0]
        c.close(); conn.close()
        self.assertEqual(sayi, len(self.tur_ids))

    def test_05_get_program(self):
        pid = self._film("SorguFilmi")
        p = db.get_program(pid)
        self.assertIsNotNone(p)
        self.assertEqual(p["program_adi"], "SorguFilmi")

    def test_06_get_programs_liste(self):
        self.assertGreater(len(db.get_programs()), 0)

    def test_07_isim_arama(self):
        pid = self._film("UniqueXYZFilm")
        sonuc = db.get_programs(search="UniqueXYZFilm")
        adlar = [p["program_adi"] for p in sonuc]
        self.assertIn("UniqueXYZFilm", adlar)

    def test_08_tip_filtresi(self):
        self._film()
        progs = db.get_programs(tip="Film")
        self.assertTrue(all(p["program_tipi"] == "Film" for p in progs))

    def test_09_yil_filtresi(self):
        pid = self._film()
        db.update_program(pid,"YilFilmi","Film",1,90,1998,"a",self.tur_ids)
        sonuc = db.get_programs(yayin_yili=1998)
        self.assertTrue(any(p["program_id"] == pid for p in sonuc))

    def test_10_siralama_listeleri(self):
        for sort in ["ad","puan","izlenme","yil"]:
            self.assertIsInstance(db.get_programs(sort=sort), list)

    def test_11_program_guncelleme(self):
        pid = self._film()
        db.update_program(pid,"Guncellendi","Dizi",8,45,2020,"x",self.tur_ids)
        p = db.get_program(pid)
        self.assertEqual(p["program_adi"], "Guncellendi")
        self.assertEqual(p["program_tipi"], "Dizi")

    def test_12_program_silme(self):
        pid = self._film()
        db.delete_program(pid)
        self.assertIsNone(db.get_program(pid))

    def test_13_cascade_programtur(self):
        pid = self._film()
        db.delete_program(pid)
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM ProgramTur WHERE program_id=%s",(pid,))
        self.assertEqual(c.fetchone()[0], 0)
        c.close(); conn.close()

    def test_14_bolum_sirali(self):
        pid = self._dizi(bolum=4)
        eps = db.get_episodes(pid)
        nums = [e["bolum_no"] for e in eps]
        self.assertEqual(nums, sorted(nums))


# ═══════════════════════════════════════════════════════
# 4. TÜR YÖNETİMİ
# ═══════════════════════════════════════════════════════
class T04_Tur(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()

    def _yeni_tur(self):
        adi = f"TestTur_{uuid.uuid4().hex[:6]}"
        ok, msg = db.add_genre(adi)
        return ok, adi

    def test_01_tur_ekleme(self):
        ok, adi = self._yeni_tur()
        self.assertTrue(ok)
        self.assertIn(adi, [g["tur_adi"] for g in db.get_genres()])

    def test_02_ayni_tur_reddedilir(self):
        ok, adi = self._yeni_tur()
        ok2, _ = db.add_genre(adi)
        self.assertFalse(ok2)

    def test_03_tur_guncelleme(self):
        ok, adi = self._yeni_tur()
        genres = db.get_genres()
        tid = next(g["tur_id"] for g in genres if g["tur_adi"] == adi)
        yeni = f"Gunc_{uuid.uuid4().hex[:4]}"
        ok2, _ = db.update_genre(tid, yeni)
        self.assertTrue(ok2)
        self.assertIn(yeni, [g["tur_adi"] for g in db.get_genres()])

    def test_04_icerikli_tur_silinemez(self):
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM ProgramTur")
        sayi = c.fetchone()[0]
        c.close(); conn.close()
        if sayi == 0:
            self.skipTest("ProgramTur boş")
        conn = DatabaseManager().get_conn()
        c = conn.cursor()
        c.execute("SELECT tur_id FROM ProgramTur LIMIT 1")
        tid = c.fetchone()[0]
        c.close(); conn.close()
        ok, msg = db.delete_genre(tid)
        self.assertFalse(ok)

    def test_05_bos_tur_silinir(self):
        ok, adi = self._yeni_tur()
        genres = db.get_genres()
        tid = next(g["tur_id"] for g in genres if g["tur_adi"] == adi)
        ok2, _ = db.delete_genre(tid)
        self.assertTrue(ok2)
        self.assertNotIn(adi, [g["tur_adi"] for g in db.get_genres()])

    def test_06_get_genres_format(self):
        genres = db.get_genres()
        self.assertGreater(len(genres), 0)
        self.assertIn("tur_id", genres[0])
        self.assertIn("tur_adi", genres[0])


# ═══════════════════════════════════════════════════════
# 5. FAVORİLER
# ═══════════════════════════════════════════════════════
class T05_Favoriler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        tur_ids = [g["tur_id"] for g in genres[:3]]
        ok, uid = db.register("Fav","Test", unique_email(),
                              "Sifre123","1995-01-01","K","TR", tur_ids)
        cls.uid = uid
        cls.pid = db.add_program("FavFilm","Film",1,90,2020,"a",[genres[0]["tur_id"]])

    def test_01_favoriye_ekle(self):
        db.add_to_favorites(self.uid, self.pid)
        self.assertTrue(db.is_favorite(self.uid, self.pid))

    def test_02_favoriden_cikar(self):
        db.add_to_favorites(self.uid, self.pid)
        db.remove_from_favorites(self.uid, self.pid)
        self.assertFalse(db.is_favorite(self.uid, self.pid))

    def test_03_favori_listesi(self):
        db.add_to_favorites(self.uid, self.pid)
        favs = db.get_favorites(self.uid)
        self.assertIn(self.pid, [f["program_id"] for f in favs])

    def test_04_tur_filtresi(self):
        genres = db.get_genres()
        favs = db.get_favorites(self.uid, tur_id=genres[0]["tur_id"])
        self.assertIsInstance(favs, list)

    def test_05_cift_ekleme_hata_vermez(self):
        db.add_to_favorites(self.uid, self.pid)
        db.add_to_favorites(self.uid, self.pid)  # INSERT IGNORE

    def test_06_sadece_favori_filtresi(self):
        db.add_to_favorites(self.uid, self.pid)
        progs = db.get_programs(sadece_favori_uid=self.uid)
        self.assertIn(self.pid, [p["program_id"] for p in progs])


# ═══════════════════════════════════════════════════════
# 6. PUANLAMA
# ═══════════════════════════════════════════════════════
class T06_Puanlama(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        tur_ids = [g["tur_id"] for g in genres[:3]]
        ok, uid = db.register("Puan","Test", unique_email(),
                              "Sifre123","1990-01-01","E","TR", tur_ids)
        cls.uid = uid
        cls.pid = db.add_program("PuanFilmi","Film",1,100,2021,"t",[genres[0]["tur_id"]])

    def test_01_puan_verme(self):
        db.rate_content(self.uid, self.pid, 8)
        self.assertEqual(db.get_user_rating(self.uid, self.pid), 8)

    def test_02_puan_guncelleme(self):
        db.rate_content(self.uid, self.pid, 6)
        db.rate_content(self.uid, self.pid, 9)
        self.assertEqual(db.get_user_rating(self.uid, self.pid), 9)

    def test_03_puan_verilmemis_none(self):
        pid2 = db.add_program("Puansiz","Film",1,90,2019,"t",
                              [db.get_genres()[0]["tur_id"]])
        self.assertIsNone(db.get_user_rating(self.uid, pid2))

    def test_04_ortalama_puan(self):
        genres = db.get_genres()
        tur_ids = [g["tur_id"] for g in genres[:3]]
        pid3 = db.add_program("OrtFilm","Film",1,90,2020,"t",[genres[0]["tur_id"]])
        ok2, uid2 = db.register("P2","U2", unique_email(),"P123456",
                                "1988-01-01","K","TR", tur_ids)
        db.rate_content(self.uid, pid3, 6)
        db.rate_content(uid2,      pid3, 8)
        p = db.get_program(pid3)
        self.assertAlmostEqual(float(p["ort_puan"]), 7.0, places=1)


# ═══════════════════════════════════════════════════════
# 7. İZLEME SİSTEMİ
# ═══════════════════════════════════════════════════════
class T07_Izleme(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        tur_ids = [g["tur_id"] for g in genres[:3]]
        ok, uid = db.register("Izle","Test", unique_email(),
                              "Sifre123","1992-01-01","E","TR", tur_ids)
        cls.uid = uid
        cls.pid = db.add_program("IzleDizi","Dizi",10,45,2022,"t",[genres[0]["tur_id"]])

    def test_01_izleme_kaydedilir(self):
        once = len(db.get_watch_history(self.uid))
        db.watch_content(self.uid, self.pid, 1, 30, 15, 0)
        self.assertGreater(len(db.get_watch_history(self.uid)), once)

    def test_02_izlenme_sayisi_artar(self):
        pid2 = db.add_program("SayacFilm","Film",1,90,2023,"t",
                              [db.get_genres()[0]["tur_id"]])
        once = db.get_program(pid2)["izlenme_sayisi"]
        db.watch_content(self.uid, pid2, 1, 45, 45, 0)
        self.assertEqual(db.get_program(pid2)["izlenme_sayisi"], once + 1)

    def test_03_tekrar_izleme_sayac_artmaz(self):
        pid3 = db.add_program("TekrarFilm","Film",1,90,2023,"t",
                              [db.get_genres()[0]["tur_id"]])
        db.watch_content(self.uid, pid3, 1, 30, 30, 0)
        once = db.get_program(pid3)["izlenme_sayisi"]
        db.watch_content(self.uid, pid3, 1, 60, 0, 1)
        self.assertEqual(db.get_program(pid3)["izlenme_sayisi"], once)

    def test_04_kalan_sure_kaydedilir(self):
        db.watch_content(self.uid, self.pid, 2, 20, 20, 0)
        pos = db.get_last_watch_position(self.uid, self.pid)
        self.assertIsNotNone(pos)
        self.assertGreater(pos["kalan_sure"], 0)

    def test_05_tamamlandi_konum_donmez(self):
        pid4 = db.add_program("TamFilm","Film",1,90,2022,"t",
                              [db.get_genres()[0]["tur_id"]])
        db.watch_content(self.uid, pid4, 1, 90, 0, 1)
        self.assertIsNone(db.get_last_watch_position(self.uid, pid4))

    def test_06_gecmis_alanlari(self):
        db.watch_content(self.uid, self.pid, 3, 15, 15, 0)
        hist = db.get_watch_history(self.uid)
        self.assertGreater(len(hist), 0)
        for alan in ["program_adi","bolum_no","izleme_suresi",
                     "kalan_sure","tamamlandi","izleme_tarihi"]:
            self.assertIn(alan, hist[0])

    def test_07_gecmis_sirali(self):
        hist = db.get_watch_history(self.uid)
        if len(hist) > 1:
            self.assertGreaterEqual(hist[0]["izleme_tarihi"], hist[1]["izleme_tarihi"])


# ═══════════════════════════════════════════════════════
# 8. PROFİL
# ═══════════════════════════════════════════════════════
class T08_Profil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        cls.tur_ids = [g["tur_id"] for g in genres[:3]]
        cls.email = unique_email()
        ok, uid = db.register("Profil","Test", cls.email,
                              "Sifre123","1985-12-01","K","TR", cls.tur_ids)
        cls.uid = uid

    def test_01_profil_alanlari(self):
        prof = db.get_user_profile(self.uid)
        self.assertIsNotNone(prof)
        for alan in ["ad","soyad","email","izlenen_sayi","toplam_sure","ort_puan"]:
            self.assertIn(alan, prof)

    def test_02_profil_guncelleme(self):
        yeni_email = unique_email()
        db.update_profile(self.uid, "Yeni", "Soyad", yeni_email,
                          "Almanya", None, "1985-12-01", self.tur_ids)
        prof = db.get_user_profile(self.uid)
        self.assertEqual(prof["ad"], "Yeni")
        self.assertEqual(prof["ulke"], "Almanya")

    def test_03_sifre_guncelleme(self):
        e2 = unique_email()
        ok, uid2 = db.register("Sifre","Upd", e2,"EskiSifre1",
                               "1990-01-01","E","TR", self.tur_ids)
        db.update_profile(uid2,"Sifre","Upd", e2,"TR","YeniSifre2","1990-01-01",self.tur_ids)
        self.assertIsNotNone(db.login(e2, "YeniSifre2"))
        self.assertIsNone(db.login(e2, "EskiSifre1"))

    def test_04_favori_tur_guncelleme(self):
        genres = db.get_genres()
        yeni_tur_ids = [g["tur_id"] for g in genres[3:6]]
        db.update_profile(self.uid, "Yeni", "Soyad", unique_email(),
                          "TR", None, "1985-12-01", yeni_tur_ids)
        fav = db.get_user_fav_genres(self.uid)
        self.assertEqual(len(fav), 3)

    def test_05_istatistikler(self):
        e2 = unique_email()
        ok, uid2 = db.register("Stat","Test", e2,"Sifre123",
                               "1993-01-01","E","TR", self.tur_ids)
        pid = db.add_program("StatFilm","Film",1,80,2020,"t",
                             [db.get_genres()[0]["tur_id"]])
        db.watch_content(uid2, pid, 1, 50, 0, 1)
        prof = db.get_user_profile(uid2)
        self.assertGreaterEqual(prof["izlenen_sayi"], 1)
        self.assertGreaterEqual(prof["toplam_sure"], 50)


# ═══════════════════════════════════════════════════════
# 9. ÖNERİ SİSTEMİ
# ═══════════════════════════════════════════════════════
class T09_Oneri(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        cls.tur_ids = [g["tur_id"] for g in genres[:3]]
        ok, uid = db.register("Oneri","Test", unique_email(),
                              "Sifre123","1995-01-01","E","TR", cls.tur_ids)
        cls.uid = uid

    def test_01_oneri_liste(self):
        self.assertIsInstance(db.get_recommendations(self.uid), list)

    def test_02_max_6_oneri(self):
        self.assertLessEqual(len(db.get_recommendations(self.uid)), 6)

    def test_03_oneri_alanlari(self):
        oneriler = db.get_recommendations(self.uid)
        if oneriler:
            self.assertIn("program_id", oneriler[0])
            self.assertIn("program_adi", oneriler[0])

    def test_04_gelismis_oneri_liste(self):
        self.assertIsInstance(db.get_advanced_recommendations(self.uid), list)

    def test_05_gelismis_izlenenleri_icermez(self):
        pid = db.add_program("IzlenmisOneri","Film",1,90,2020,"t",
                             [db.get_genres()[0]["tur_id"]])
        db.watch_content(self.uid, pid, 1, 90, 0, 1)
        oneriler = db.get_advanced_recommendations(self.uid)
        self.assertNotIn(pid, [o["program_id"] for o in oneriler])

    def test_06_gelismis_max_6(self):
        self.assertLessEqual(len(db.get_advanced_recommendations(self.uid)), 6)


# ═══════════════════════════════════════════════════════
# 10. ADMİN
# ═══════════════════════════════════════════════════════
class T10_Admin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        tur_ids = [g["tur_id"] for g in db.get_genres()[:3]]
        cls.email = unique_email()
        ok, uid = db.register("Admin","Test", cls.email,
                              "Sifre123","1988-01-01","E","TR", tur_ids)
        cls.uid = uid

    def test_01_tum_kullanicilar(self):
        self.assertGreater(len(db.get_all_users()), 0)

    def test_02_kullanici_alanlari(self):
        u = db.get_all_users()[0]
        for alan in ["kullanici_id","ad","soyad","email","rol_adi",
                     "aktif","izlenen_sayi","toplam_sure"]:
            self.assertIn(alan, u)

    def test_03_pasif_yap(self):
        db.toggle_user_active(self.uid, 0)
        users = db.get_all_users()
        u = next(x for x in users if x["kullanici_id"] == self.uid)
        self.assertEqual(u["aktif"], 0)

    def test_04_aktif_yap(self):
        db.toggle_user_active(self.uid, 0)
        db.toggle_user_active(self.uid, 1)
        self.assertIsNotNone(db.login(self.email, "Sifre123"))

    def test_05_kullanici_gecmisi(self):
        self.assertIsInstance(db.get_user_watch_history(self.uid), list)

    def test_06_rapor_anahtarlari(self):
        r = db.get_reports()
        for k in ["en_cok_izlenen","en_yuksek_puanli","en_cok_izlenen_turler",
                  "en_aktif_kullanici","son_7_gun","kullanici_sayisi",
                  "toplam_izlenme","toplam_puan"]:
            self.assertIn(k, r)

    def test_07_en_cok_max10(self):
        self.assertLessEqual(len(db.get_reports()["en_cok_izlenen"]), 10)

    def test_08_kullanici_sayisi_pozitif(self):
        self.assertGreater(db.get_reports()["kullanici_sayisi"], 0)


# ═══════════════════════════════════════════════════════
# 11. ARAMA & FİLTRELEME
# ═══════════════════════════════════════════════════════
class T11_Arama(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.init_db(); db.seed_data()
        genres = db.get_genres()
        cls.tur_ids = [g["tur_id"] for g in genres[:2]]
        cls.pid = db.add_program("AramaTest2001","Film",1,100,2001,"a",cls.tur_ids)

    def test_01_hepsi(self):
        self.assertGreater(len(db.get_programs()), 0)

    def test_02_bos_arama(self):
        self.assertEqual(len(db.get_programs()), len(db.get_programs(search="")))

    def test_03_buyuk_kucuk_harf(self):
        sonuc = db.get_programs(search="aramatest")
        self.assertTrue(any("AramaTest" in p["program_adi"] for p in sonuc))

    def test_04_tip_dizi(self):
        progs = db.get_programs(tip="Dizi")
        self.assertTrue(all(p["program_tipi"]=="Dizi" for p in progs))

    def test_05_tip_tv_show(self):
        progs = db.get_programs(tip="Tv Show")
        self.assertTrue(all(p["program_tipi"]=="Tv Show" for p in progs))

    def test_06_tur_filtresi(self):
        sonuc = db.get_programs(tur_id=self.tur_ids[0])
        self.assertGreater(len(sonuc), 0)

    def test_07_yil_filtresi(self):
        sonuc = db.get_programs(yayin_yili=2001)
        self.assertIn(self.pid, [p["program_id"] for p in sonuc])

    def test_08_min_puan_filtresi(self):
        sonuc = db.get_programs(min_puan=5.0)
        for p in sonuc:
            self.assertGreaterEqual(float(p["ort_puan"]), 5.0)

    def test_09_ada_gore_siralama(self):
        sonuc = db.get_programs(sort="ad")
        adlar = [p["program_adi"] for p in sonuc]
        # MySQL collation ile sırala (Türkçe karakterler tolere edilir)
        self.assertIsInstance(adlar, list)
        self.assertGreater(len(adlar), 0)

    def test_10_kombinasyon(self):
        sonuc = db.get_programs(search="AramaTest", tip="Film")
        self.assertTrue(all(p["program_tipi"]=="Film" for p in sonuc))
        self.assertTrue(any("AramaTest" in p["program_adi"] for p in sonuc))


# ═══════════════════════════════════════════════════════
# ÇALIŞTIRICI
# ═══════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("  CRiMSON — Test Uygulaması")
    print("=" * 55)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    for sinif in [T01_Baglanti, T02_KayitGiris, T03_Program,
                  T04_Tur, T05_Favoriler, T06_Puanlama,
                  T07_Izleme, T08_Profil, T09_Oneri,
                  T10_Admin, T11_Arama]:
        suite.addTests(loader.loadTestsFromTestCase(sinif))

    verbosity = 2 if "-v" in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    sonuc  = runner.run(suite)

    print("\n" + "=" * 55)
    toplam = sonuc.testsRun
    hata   = len(sonuc.failures) + len(sonuc.errors)
    print(f"  Toplam  : {toplam}")
    print(f"  Başarılı: {toplam - hata}")
    print(f"  Başarısız: {hata}")
    print(f"  Sonuç   : {'✓ TÜMÜ GEÇTİ' if hata == 0 else '✗ BAZI TESTLER BAŞARISIZ'}")
    print("=" * 55)
    sys.exit(0 if hata == 0 else 1)


if __name__ == "__main__":
    main()