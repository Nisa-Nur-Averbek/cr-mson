import mysql.connector
import hashlib

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "",
    "database": "crimson",
    "charset": "utf8mb4",
}

class DatabaseManager:
    def get_conn(self):
        return mysql.connector.connect(**DB_CONFIG)

    @staticmethod
    def hash_password(p):
        return hashlib.sha256(p.encode()).hexdigest()

    def _fetchall(self, c):
        cols = [d[0] for d in c.description]
        rows = []
        for row in c.fetchall():
            d = dict(zip(cols, row))
            for k, v in d.items():
                if hasattr(v, 'isoformat'): d[k] = str(v)
            rows.append(d)
        return rows

    def _fetchone(self, c):
        row = c.fetchone()
        if not row: return None
        cols = [d[0] for d in c.description]
        d = dict(zip(cols, row))
        for k, v in d.items():
            if hasattr(v, 'isoformat'): d[k] = str(v)
        return d

class DatabaseSetup(DatabaseManager):
    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            sqls = [
                "CREATE TABLE IF NOT EXISTS Rol (rol_id INT AUTO_INCREMENT PRIMARY KEY, rol_adi VARCHAR(50) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS Kullanici (kullanici_id INT AUTO_INCREMENT PRIMARY KEY, ad VARCHAR(100) NOT NULL, soyad VARCHAR(100) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, sifre VARCHAR(255) NOT NULL, dogum_tarihi DATE, cinsiyet CHAR(1), ulke VARCHAR(100), rol_id INT NOT NULL DEFAULT 2, aktif TINYINT NOT NULL DEFAULT 1, kayit_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (rol_id) REFERENCES Rol(rol_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS Tur (tur_id INT AUTO_INCREMENT PRIMARY KEY, tur_adi VARCHAR(100) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS Program (program_id INT AUTO_INCREMENT PRIMARY KEY, program_adi VARCHAR(255) NOT NULL, program_tipi ENUM('Film','Dizi','Tv Show') NOT NULL, bolum_sayisi INT DEFAULT 1, bolum_uzunlugu INT DEFAULT 90, yayin_yili INT, aciklama TEXT, izlenme_sayisi INT DEFAULT 0) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS ProgramTur (program_id INT, tur_id INT, PRIMARY KEY (program_id, tur_id), FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE, FOREIGN KEY (tur_id) REFERENCES Tur(tur_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS KullaniciProgram (id INT AUTO_INCREMENT PRIMARY KEY, kullanici_id INT, program_id INT, puan INT CHECK(puan BETWEEN 1 AND 10), izleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id), FOREIGN KEY (program_id) REFERENCES Program(program_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS Favori (kullanici_id INT, program_id INT, eklenme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (kullanici_id, program_id), FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id), FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS KullaniciTur (kullanici_id INT, tur_id INT, PRIMARY KEY (kullanici_id, tur_id), FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id), FOREIGN KEY (tur_id) REFERENCES Tur(tur_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS Bolum (bolum_id INT AUTO_INCREMENT PRIMARY KEY, program_id INT, bolum_no INT, bolum_adi VARCHAR(255), sure INT DEFAULT 45, FOREIGN KEY (program_id) REFERENCES Program(program_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS IzlemeLog (log_id INT AUTO_INCREMENT PRIMARY KEY, kullanici_id INT, program_id INT, bolum_no INT DEFAULT 1, izleme_suresi INT DEFAULT 0, kalan_sure INT DEFAULT 0, tamamlandi TINYINT DEFAULT 0, izleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id), FOREIGN KEY (program_id) REFERENCES Program(program_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS OturumLog (log_id INT AUTO_INCREMENT PRIMARY KEY, kullanici_id INT, giris_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
            ]
            for sql in sqls:
                c.execute(sql)
            c.execute("INSERT IGNORE INTO Rol (rol_adi) VALUES ('Admin')")
            c.execute("INSERT IGNORE INTO Rol (rol_adi) VALUES ('Kullanici')")
            conn.commit()
        finally:
            c.close(); conn.close()

    def seed_data(self):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM Program")
            if c.fetchone()[0] > 0: return
            genres = ["Aksiyon ve Macera","Belgesel","Bilim Kurgu ve Fantastik Yapımlar","Çocuk ve Aile","Drama","Romantik","Korku","Gerilim","Komedi","Bilim ve Doğa","Reality Program","Anime","Aksiyon","Bilim Kurgu"]
            for g in genres:
                c.execute("INSERT IGNORE INTO Tur (tur_adi) VALUES (%s)", (g,))
            content = [
                ("Recep İvedik 6",["Aksiyon ve Macera"],"Film",1,110,2019),
                ("Assassin's Creed",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,116,2016),
                ("Alaca Karanlık",["Aksiyon ve Macera","Romantik"],"Film",1,122,2008),
                ("Yüzüklerin Efendisi İki Kule",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,179,2002),
                ("Maske",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,101,1994),
                ("Kara Şövalye",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,152,2008),
                ("Sherlock Holmes",["Aksiyon ve Macera"],"Film",1,128,2009),
                ("Yüzüklerin Efendisi Kralın Dönüşü",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,201,2003),
                ("Transformers Kayıp Çağ",["Aksiyon ve Macera"],"Film",1,165,2014),
                ("Başlangıç",["Aksiyon ve Macera"],"Film",1,148,2010),
                ("Interstellar",["Aksiyon ve Macera","Drama"],"Film",1,169,2014),
                ("Harry Potter Ölüm Yadigarları",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar","Çocuk ve Aile"],"Film",1,130,2010),
                ("Jurassic World",["Aksiyon ve Macera"],"Film",1,124,2015),
                ("Fantastik Canavarlar",["Aksiyon ve Macera","Çocuk ve Aile"],"Film",1,133,2016),
                ("Ninja Kaplumbağalar",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,101,2014),
                ("Kuşlarla Dans",["Belgesel"],"Film",1,81,2018),
                ("Mission Blue",["Belgesel"],"Film",1,95,2014),
                ("Mercan Peşinde",["Belgesel"],"Film",1,89,2019),
                ("Dream Big",["Belgesel"],"Film",1,42,2017),
                ("Ay'daki Son Adam",["Belgesel"],"Film",1,97,2020),
                ("Ben Efsaneyim",["Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,101,2007),
                ("Arif V 216",["Bilim Kurgu ve Fantastik Yapımlar","Komedi"],"Film",1,117,2018),
                ("PK",["Bilim Kurgu ve Fantastik Yapımlar","Romantik"],"Film",1,153,2014),
                ("Örümcek Adam",["Aksiyon ve Macera","Bilim Kurgu ve Fantastik Yapımlar"],"Film",1,121,2002),
                ("Jurassic Park",["Bilim Kurgu ve Fantastik Yapımlar","Aksiyon"],"Film",1,127,1993),
                ("Pokemon",["Çocuk ve Aile"],"Film",1,98,1999),
                ("Shrek",["Çocuk ve Aile","Komedi"],"Film",1,90,2001),
                ("Kung Fu Panda",["Çocuk ve Aile","Aksiyon ve Macera"],"Film",1,92,2008),
                ("Bizi Hatırla",["Drama"],"Film",1,105,2017),
                ("Dangal",["Drama"],"Film",1,161,2016),
                ("Delibal",["Drama","Romantik"],"Film",1,107,2015),
                ("Kardeşim Benim",["Drama","Komedi"],"Film",1,102,2014),
                ("Jaws",["Gerilim"],"Film",1,124,1975),
                ("Da Vinci Şifresi",["Gerilim"],"Film",1,149,2006),
                ("Marvel Iron Fist",["Aksiyon ve Macera"],"Dizi",13,55,2017),
                ("Diriliş Ertuğrul",["Aksiyon ve Macera"],"Dizi",150,120,2014),
                ("How I Met Your Mother",["Romantik"],"Dizi",208,22,2005),
                ("Leyla ile Mecnun",["Romantik"],"Dizi",77,45,2011),
                ("Beni Böyle Sev",["Drama","Romantik"],"Dizi",52,120,2019),
                ("Atiye",["Aksiyon ve Macera","Romantik"],"Dizi",24,45,2019),
                ("Maşa ve Koca Ayı",["Çocuk ve Aile"],"Dizi",52,7,2009),
                ("Sünger Bob",["Çocuk ve Aile","Komedi"],"Dizi",260,11,1999),
                ("Stranger Things",["Aksiyon ve Macera","Korku"],"Dizi",34,50,2016),
                ("The Originals",["Drama","Korku"],"Dizi",92,43,2013),
                ("Criminal",["Gerilim"],"Dizi",12,30,2019),
                ("Beyblade",["Anime","Çocuk ve Aile"],"Dizi",51,24,2001),
                ("The Blacklist",["Aksiyon ve Macera","Gerilim"],"Dizi",180,43,2013),
                ("Dünyanın En Sıra Dışı Evleri",["Reality Program"],"Tv Show",20,30,2018),
                ("Car Masters",["Reality Program"],"Tv Show",16,45,2018),
                ("Büyük Tasarımlar",["Reality Program"],"Tv Show",10,40,2020),
                ("Basketball or Nothing",["Reality Program"],"Tv Show",6,35,2019),
            ]
            for name, genre_list, ptype, episodes, duration, year in content:
                c.execute("INSERT INTO Program (program_adi,program_tipi,bolum_sayisi,bolum_uzunlugu,yayin_yili,aciklama,izlenme_sayisi) VALUES (%s,%s,%s,%s,%s,%s,0)",
                          (name, ptype, episodes, duration, year, f"{name} - {ptype}"))
                pid = c.lastrowid
                for g in genre_list:
                    c.execute("SELECT tur_id FROM Tur WHERE tur_adi=%s", (g,))
                    row = c.fetchone()
                    if row: c.execute("INSERT IGNORE INTO ProgramTur VALUES (%s,%s)", (pid, row[0]))
                if ptype in ("Dizi","Tv Show") and episodes > 1:
                    for ep in range(1, min(episodes+1, 6)):
                        c.execute("INSERT INTO Bolum (program_id,bolum_no,bolum_adi,sure) VALUES (%s,%s,%s,%s)", (pid, ep, f"Bölüm {ep}", duration))
            c.execute("SELECT rol_id FROM Rol WHERE rol_adi='Admin'")
            admin_rol = c.fetchone()[0]
            c.execute("INSERT IGNORE INTO Kullanici (ad,soyad,email,sifre,dogum_tarihi,cinsiyet,ulke,rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                      ("Admin","Admin","admin@netflix.com",self.hash_password("admin123"),"1990-01-01","E","Türkiye",admin_rol))
            conn.commit()
        finally:
            c.close(); conn.close()

class AuthManager(DatabaseManager):
    def login(self, email, password):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT k.*, r.rol_adi FROM Kullanici k JOIN Rol r ON k.rol_id=r.rol_id WHERE k.email=%s AND k.sifre=%s AND k.aktif=1",
                      (email, self.hash_password(password)))
            user = self._fetchone(c)
            if user:
                c.execute("INSERT INTO OturumLog (kullanici_id) VALUES (%s)", (user["kullanici_id"],))
                conn.commit()
            return user
        finally:
            c.close(); conn.close()

    def register(self, ad, soyad, email, sifre, dogum_tarihi, cinsiyet, ulke, tur_ids):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT kullanici_id FROM Kullanici WHERE email=%s", (email,))
            if c.fetchone(): return False, "Bu e-mail zaten kayıtlı."
            c.execute("SELECT rol_id FROM Rol WHERE rol_adi='Kullanici'")
            rol = c.fetchone(); rol_id = rol[0] if rol else 2
            c.execute("INSERT INTO Kullanici (ad,soyad,email,sifre,dogum_tarihi,cinsiyet,ulke,rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                      (ad, soyad, email, self.hash_password(sifre), dogum_tarihi, cinsiyet, ulke, rol_id))
            uid = c.lastrowid
            for tid in tur_ids:
                c.execute("INSERT IGNORE INTO KullaniciTur VALUES (%s,%s)", (uid, tid))
            conn.commit()
            return True, uid
        finally:
            c.close(); conn.close()

class ProgramManager(DatabaseManager):
    def get_programs(self, search="", tur_id=None, tip=None, min_puan=None, yayin_yili=None, sort="ad", sadece_favori_uid=None):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            sql = "SELECT p.*, GROUP_CONCAT(DISTINCT t.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p LEFT JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN Tur t ON pt.tur_id=t.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id WHERE 1=1"
            params = []
            if sadece_favori_uid:
                sql += " AND p.program_id IN (SELECT program_id FROM Favori WHERE kullanici_id=%s)"; params.append(sadece_favori_uid)
            if search:
                sql += " AND p.program_adi LIKE %s"; params.append(f"%{search}%")
            if tur_id:
                sql += " AND pt.tur_id=%s"; params.append(tur_id)
            if tip:
                sql += " AND p.program_tipi=%s"; params.append(tip)
            if yayin_yili:
                sql += " AND p.yayin_yili=%s"; params.append(yayin_yili)
            sql += " GROUP BY p.program_id"
            if min_puan: sql += f" HAVING ort_puan>={float(min_puan)}"
            order = {"ad":"p.program_adi","puan":"ort_puan DESC","izlenme":"p.izlenme_sayisi DESC","yil":"p.yayin_yili DESC"}.get(sort,"p.program_adi")
            sql += f" ORDER BY {order}"
            c.execute(sql, params)
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def get_program(self, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT p.*, GROUP_CONCAT(DISTINCT t.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p LEFT JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN Tur t ON pt.tur_id=t.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id WHERE p.program_id=%s GROUP BY p.program_id", (pid,))
            return self._fetchone(c)
        finally:
            c.close(); conn.close()

    def get_episodes(self, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM Bolum WHERE program_id=%s ORDER BY bolum_no", (pid,))
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def add_program(self, adi, tipi, bolum_sayisi, bolum_uzunlugu, yayin_yili, aciklama, tur_ids):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO Program (program_adi,program_tipi,bolum_sayisi,bolum_uzunlugu,yayin_yili,aciklama) VALUES (%s,%s,%s,%s,%s,%s)",
                      (adi, tipi, bolum_sayisi, bolum_uzunlugu, yayin_yili, aciklama))
            pid = c.lastrowid
            for tid in tur_ids:
                c.execute("INSERT IGNORE INTO ProgramTur VALUES (%s,%s)", (pid, tid))
            if tipi in ("Dizi","Tv Show") and bolum_sayisi > 0:
                for ep in range(1, bolum_sayisi+1):
                    c.execute("INSERT INTO Bolum (program_id,bolum_no,bolum_adi,sure) VALUES (%s,%s,%s,%s)", (pid, ep, f"Bölüm {ep}", bolum_uzunlugu))
            conn.commit(); return pid
        finally:
            c.close(); conn.close()

    def update_program(self, pid, adi, tipi, bolum_sayisi, bolum_uzunlugu, yayin_yili, aciklama, tur_ids):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("UPDATE Program SET program_adi=%s,program_tipi=%s,bolum_sayisi=%s,bolum_uzunlugu=%s,yayin_yili=%s,aciklama=%s WHERE program_id=%s",
                      (adi, tipi, bolum_sayisi, bolum_uzunlugu, yayin_yili, aciklama, pid))
            c.execute("DELETE FROM ProgramTur WHERE program_id=%s", (pid,))
            for tid in tur_ids:
                c.execute("INSERT IGNORE INTO ProgramTur VALUES (%s,%s)", (pid, tid))
            conn.commit()
        finally:
            c.close(); conn.close()

    def delete_program(self, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM Program WHERE program_id=%s", (pid,))
            conn.commit()
        finally:
            c.close(); conn.close()

class TurManager(DatabaseManager):
    def get_genres(self):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM Tur ORDER BY tur_adi")
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def add_genre(self, tur_adi):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM Tur WHERE tur_adi=%s", (tur_adi,))
            if c.fetchone()[0] > 0: return False, "Bu tür zaten mevcut."
            c.execute("INSERT INTO Tur (tur_adi) VALUES (%s)", (tur_adi,))
            conn.commit(); return True, "Tür eklendi."
        finally:
            c.close(); conn.close()

    def update_genre(self, tur_id, yeni_adi):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM Tur WHERE tur_adi=%s AND tur_id!=%s", (yeni_adi, tur_id))
            if c.fetchone()[0] > 0: return False, "Bu tür adı zaten mevcut."
            c.execute("UPDATE Tur SET tur_adi=%s WHERE tur_id=%s", (yeni_adi, tur_id))
            conn.commit(); return True, "Tür güncellendi."
        finally:
            c.close(); conn.close()

    def delete_genre(self, tur_id):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            # DÜZELTME 1: SELECT COUNT(*) kullan — SELECT 1 MySQL cursor sorununa yol açıyor
            c.execute("SELECT COUNT(*) FROM ProgramTur WHERE tur_id=%s", (tur_id,))
            if c.fetchone()[0] > 0: return False, "Bu türe bağlı içerik var, silinemez."
            c.execute("DELETE FROM Tur WHERE tur_id=%s", (tur_id,))
            conn.commit(); return True, "Tür silindi."
        finally:
            c.close(); conn.close()

class KullaniciManager(DatabaseManager):
    def add_to_favorites(self, uid, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("INSERT IGNORE INTO Favori (kullanici_id,program_id) VALUES (%s,%s)", (uid, pid))
            conn.commit()
        finally:
            c.close(); conn.close()

    def remove_from_favorites(self, uid, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM Favori WHERE kullanici_id=%s AND program_id=%s", (uid, pid))
            conn.commit()
        finally:
            c.close(); conn.close()

    def is_favorite(self, uid, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM Favori WHERE kullanici_id=%s AND program_id=%s", (uid, pid))
            return c.fetchone()[0] > 0
        finally:
            c.close(); conn.close()

    def get_favorites(self, uid, tur_id=None):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            sql = "SELECT p.*, GROUP_CONCAT(DISTINCT t.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan, f.eklenme_tarihi FROM Favori f JOIN Program p ON f.program_id=p.program_id LEFT JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN Tur t ON pt.tur_id=t.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id WHERE f.kullanici_id=%s"
            params = [uid]
            if tur_id:
                sql += " AND pt.tur_id=%s"; params.append(tur_id)
            sql += " GROUP BY p.program_id ORDER BY f.eklenme_tarihi DESC"
            c.execute(sql, params)
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def rate_content(self, uid, pid, puan):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT id FROM KullaniciProgram WHERE kullanici_id=%s AND program_id=%s", (uid, pid))
            ex = c.fetchone()
            if ex:
                c.execute("UPDATE KullaniciProgram SET puan=%s,izleme_tarihi=NOW() WHERE id=%s", (puan, ex[0]))
            else:
                c.execute("INSERT INTO KullaniciProgram (kullanici_id,program_id,puan) VALUES (%s,%s,%s)", (uid, pid, puan))
            conn.commit()
        finally:
            c.close(); conn.close()

    def get_user_rating(self, uid, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT puan FROM KullaniciProgram WHERE kullanici_id=%s AND program_id=%s", (uid, pid))
            r = c.fetchone(); return r[0] if r else None
        finally:
            c.close(); conn.close()

    def watch_content(self, uid, pid, bolum_no, sure, kalan_sure, tamamlandi):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT log_id FROM IzlemeLog WHERE kullanici_id=%s AND program_id=%s AND bolum_no=%s ORDER BY izleme_tarihi DESC LIMIT 1", (uid, pid, bolum_no))
            ex = c.fetchone()
            if ex:
                c.execute("UPDATE IzlemeLog SET izleme_suresi=%s,kalan_sure=%s,tamamlandi=%s,izleme_tarihi=NOW() WHERE log_id=%s", (sure, kalan_sure, tamamlandi, ex[0]))
            else:
                c.execute("INSERT INTO IzlemeLog (kullanici_id,program_id,bolum_no,izleme_suresi,kalan_sure,tamamlandi) VALUES (%s,%s,%s,%s,%s,%s)", (uid, pid, bolum_no, sure, kalan_sure, tamamlandi))
                c.execute("UPDATE Program SET izlenme_sayisi=izlenme_sayisi+1 WHERE program_id=%s", (pid,))
            conn.commit()
        finally:
            c.close(); conn.close()

    def get_watch_history(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT il.*, p.program_adi, p.program_tipi, kp.puan FROM IzlemeLog il JOIN Program p ON il.program_id=p.program_id LEFT JOIN KullaniciProgram kp ON kp.kullanici_id=il.kullanici_id AND kp.program_id=il.program_id WHERE il.kullanici_id=%s ORDER BY il.izleme_tarihi DESC", (uid,))
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def get_last_watch_position(self, uid, pid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT bolum_no, kalan_sure FROM IzlemeLog WHERE kullanici_id=%s AND program_id=%s AND tamamlandi=0 ORDER BY izleme_tarihi DESC LIMIT 1", (uid, pid))
            return self._fetchone(c)
        finally:
            c.close(); conn.close()

    def get_user_profile(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT k.*, r.rol_adi, (SELECT COUNT(DISTINCT program_id) FROM IzlemeLog WHERE kullanici_id=k.kullanici_id) as izlenen_sayi, (SELECT COALESCE(SUM(izleme_suresi),0) FROM IzlemeLog WHERE kullanici_id=k.kullanici_id) as toplam_sure, (SELECT COALESCE(AVG(puan),0) FROM KullaniciProgram WHERE kullanici_id=k.kullanici_id) as ort_puan FROM Kullanici k JOIN Rol r ON k.rol_id=r.rol_id WHERE k.kullanici_id=%s", (uid,))
            return self._fetchone(c)
        finally:
            c.close(); conn.close()

    def update_profile(self, uid, ad, soyad, email, ulke, sifre=None, dogum_tarihi=None, fav_tur_ids=None):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            if sifre:
                c.execute("UPDATE Kullanici SET ad=%s,soyad=%s,email=%s,ulke=%s,sifre=%s,dogum_tarihi=%s WHERE kullanici_id=%s",
                          (ad, soyad, email, ulke, self.hash_password(sifre), dogum_tarihi, uid))
            else:
                c.execute("UPDATE Kullanici SET ad=%s,soyad=%s,email=%s,ulke=%s,dogum_tarihi=%s WHERE kullanici_id=%s",
                          (ad, soyad, email, ulke, dogum_tarihi, uid))
            if fav_tur_ids is not None:
                c.execute("DELETE FROM KullaniciTur WHERE kullanici_id=%s", (uid,))
                for tid in fav_tur_ids:
                    c.execute("INSERT IGNORE INTO KullaniciTur (kullanici_id,tur_id) VALUES (%s,%s)", (uid, tid))
            conn.commit()
        finally:
            c.close(); conn.close()

    def get_user_fav_genres(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT t.tur_adi FROM KullaniciTur kt JOIN Tur t ON kt.tur_id=t.tur_id WHERE kt.kullanici_id=%s", (uid,))
            return [r[0] for r in c.fetchall()]
        finally:
            c.close(); conn.close()

class OneriManager(DatabaseManager):
    def get_recommendations(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT tur_id FROM KullaniciTur WHERE kullanici_id=%s", (uid,))
            fav_ids = [r[0] for r in c.fetchall()]
            if not fav_ids:
                c.execute("SELECT p.*, GROUP_CONCAT(DISTINCT t.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p LEFT JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN Tur t ON pt.tur_id=t.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id GROUP BY p.program_id ORDER BY ort_puan DESC LIMIT 6")
                return self._fetchall(c)
            result = []; seen = set()
            for tid in fav_ids:
                c.execute("SELECT p.*, GROUP_CONCAT(DISTINCT t2.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN ProgramTur pt2 ON p.program_id=pt2.program_id LEFT JOIN Tur t2 ON pt2.tur_id=t2.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id WHERE pt.tur_id=%s GROUP BY p.program_id ORDER BY ort_puan DESC LIMIT 5", (tid,))
                cnt = 0
                for row in self._fetchall(c):
                    if row["program_id"] not in seen and cnt < 2:
                        result.append(row); seen.add(row["program_id"]); cnt += 1
            return result[:6]
        finally:
            c.close(); conn.close()

    def get_advanced_recommendations(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT DISTINCT tur_id FROM KullaniciTur WHERE kullanici_id=%s UNION SELECT DISTINCT pt.tur_id FROM IzlemeLog il JOIN ProgramTur pt ON il.program_id=pt.program_id WHERE il.kullanici_id=%s UNION SELECT DISTINCT pt.tur_id FROM KullaniciProgram kp JOIN ProgramTur pt ON kp.program_id=pt.program_id WHERE kp.kullanici_id=%s AND kp.puan>=7", (uid,uid,uid))
            ids = [r[0] for r in c.fetchall()]
            if not ids:
                c.execute("SELECT p.*, GROUP_CONCAT(DISTINCT t.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p LEFT JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN Tur t ON pt.tur_id=t.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id GROUP BY p.program_id ORDER BY ort_puan DESC LIMIT 6")
            else:
                fmt = ",".join(["%s"]*len(ids))
                c.execute(f"SELECT p.*, GROUP_CONCAT(DISTINCT t2.tur_adi SEPARATOR ', ') as turler, COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p JOIN ProgramTur pt ON p.program_id=pt.program_id LEFT JOIN ProgramTur pt2 ON p.program_id=pt2.program_id LEFT JOIN Tur t2 ON pt2.tur_id=t2.tur_id LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id WHERE pt.tur_id IN ({fmt}) AND p.program_id NOT IN (SELECT DISTINCT program_id FROM IzlemeLog WHERE kullanici_id=%s) GROUP BY p.program_id ORDER BY ort_puan DESC LIMIT 6", ids+[uid])
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

class AdminManager(DatabaseManager):
    def get_all_users(self):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT k.*, r.rol_adi, (SELECT COUNT(DISTINCT program_id) FROM IzlemeLog WHERE kullanici_id=k.kullanici_id) as izlenen_sayi, (SELECT COALESCE(SUM(izleme_suresi),0) FROM IzlemeLog WHERE kullanici_id=k.kullanici_id) as toplam_sure FROM Kullanici k JOIN Rol r ON k.rol_id=r.rol_id ORDER BY k.kayit_tarihi DESC")
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def get_user_watch_history(self, uid):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT il.*, p.program_adi, p.program_tipi, kp.puan, CONCAT(k.ad,' ',k.soyad) as kullanici_adi FROM IzlemeLog il JOIN Program p ON il.program_id=p.program_id JOIN Kullanici k ON il.kullanici_id=k.kullanici_id LEFT JOIN KullaniciProgram kp ON kp.kullanici_id=il.kullanici_id AND kp.program_id=il.program_id WHERE il.kullanici_id=%s ORDER BY il.izleme_tarihi DESC", (uid,))
            return self._fetchall(c)
        finally:
            c.close(); conn.close()

    def toggle_user_active(self, uid, aktif):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute("UPDATE Kullanici SET aktif=%s WHERE kullanici_id=%s", (aktif, uid))
            conn.commit()
        finally:
            c.close(); conn.close()

    def get_reports(self):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            reports = {}
            c.execute("SELECT p.program_adi,p.program_tipi,p.izlenme_sayisi,COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p LEFT JOIN KullaniciProgram kp ON p.program_id=kp.program_id GROUP BY p.program_id ORDER BY p.izlenme_sayisi DESC LIMIT 10")
            reports["en_cok_izlenen"] = self._fetchall(c)
            c.execute("SELECT p.program_adi,p.program_tipi,COALESCE(AVG(kp.puan),0) as ort_puan FROM Program p JOIN KullaniciProgram kp ON p.program_id=kp.program_id GROUP BY p.program_id HAVING COUNT(kp.id)>0 ORDER BY ort_puan DESC LIMIT 10")
            reports["en_yuksek_puanli"] = self._fetchall(c)
            c.execute("SELECT t.tur_adi,SUM(p.izlenme_sayisi) as toplam_izlenme FROM Tur t JOIN ProgramTur pt ON t.tur_id=pt.tur_id JOIN Program p ON pt.program_id=p.program_id GROUP BY t.tur_id ORDER BY toplam_izlenme DESC LIMIT 10")
            reports["en_cok_izlenen_turler"] = self._fetchall(c)
            c.execute("SELECT CONCAT(k.ad,' ',k.soyad) as isim,COUNT(il.log_id) as izleme_sayisi,SUM(il.izleme_suresi) as toplam_sure FROM Kullanici k LEFT JOIN IzlemeLog il ON k.kullanici_id=il.kullanici_id GROUP BY k.kullanici_id ORDER BY izleme_sayisi DESC LIMIT 10")
            reports["en_aktif_kullanici"] = self._fetchall(c)
            c.execute("SELECT p.program_adi,COUNT(il.log_id) as izleme_sayisi FROM IzlemeLog il JOIN Program p ON il.program_id=p.program_id WHERE il.izleme_tarihi>=DATE_SUB(NOW(),INTERVAL 7 DAY) GROUP BY p.program_id ORDER BY izleme_sayisi DESC")
            reports["son_7_gun"] = self._fetchall(c)
            c.execute("SELECT COUNT(*) FROM Kullanici WHERE aktif=1"); reports["kullanici_sayisi"] = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(izlenme_sayisi),0) FROM Program"); reports["toplam_izlenme"] = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM KullaniciProgram WHERE puan IS NOT NULL"); reports["toplam_puan"] = c.fetchone()[0]
            return reports
        finally:
            c.close(); conn.close()

class NetflixDB:
    def __init__(self):
        self._setup=DatabaseSetup(); self._auth=AuthManager(); self._program=ProgramManager()
        self._tur=TurManager(); self._kullanici=KullaniciManager()
        self._oneri=OneriManager(); self._admin=AdminManager()
    def init_db(self): return self._setup.init_db()
    def seed_data(self): return self._setup.seed_data()
    def login(self,e,p): return self._auth.login(e,p)
    def register(self,*a,**kw): return self._auth.register(*a,**kw)
    def get_programs(self,*a,**kw): return self._program.get_programs(*a,**kw)
    def get_program(self,pid): return self._program.get_program(pid)
    def get_episodes(self,pid): return self._program.get_episodes(pid)
    def add_program(self,*a,**kw): return self._program.add_program(*a,**kw)
    def update_program(self,*a,**kw): return self._program.update_program(*a,**kw)
    def delete_program(self,pid): return self._program.delete_program(pid)
    def get_genres(self): return self._tur.get_genres()
    def add_genre(self,a): return self._tur.add_genre(a)
    def update_genre(self,t,y): return self._tur.update_genre(t,y)
    def delete_genre(self,t): return self._tur.delete_genre(t)
    def add_to_favorites(self,u,p): return self._kullanici.add_to_favorites(u,p)
    def remove_from_favorites(self,u,p): return self._kullanici.remove_from_favorites(u,p)
    def is_favorite(self,u,p): return self._kullanici.is_favorite(u,p)
    # DÜZELTME 2: tur_id keyword argümanı desteği eklendi
    def get_favorites(self,u,t=None,tur_id=None): return self._kullanici.get_favorites(u,t or tur_id)
    def rate_content(self,u,p,puan): return self._kullanici.rate_content(u,p,puan)
    def get_user_rating(self,u,p): return self._kullanici.get_user_rating(u,p)
    def watch_content(self,*a): return self._kullanici.watch_content(*a)
    def get_watch_history(self,uid): return self._kullanici.get_watch_history(uid)
    def get_last_watch_position(self,u,p): return self._kullanici.get_last_watch_position(u,p)
    def get_user_profile(self,uid): return self._kullanici.get_user_profile(uid)
    def update_profile(self,*a,**kw): return self._kullanici.update_profile(*a,**kw)
    def get_user_fav_genres(self,uid): return self._kullanici.get_user_fav_genres(uid)
    def get_recommendations(self,uid): return self._oneri.get_recommendations(uid)
    def get_advanced_recommendations(self,u): return self._oneri.get_advanced_recommendations(u)
    def get_all_users(self): return self._admin.get_all_users()
    def get_user_watch_history(self,uid): return self._admin.get_user_watch_history(uid)
    def toggle_user_active(self,u,a): return self._admin.toggle_user_active(u,a)
    def get_reports(self): return self._admin.get_reports()

_db = NetflixDB()
def init_db(): return _db.init_db()
def seed_data(): return _db.seed_data()
def login(e,p): return _db.login(e,p)
def register(*a,**kw): return _db.register(*a,**kw)
def get_programs(*a,**kw): return _db.get_programs(*a,**kw)
def get_program(pid): return _db.get_program(pid)
def get_episodes(pid): return _db.get_episodes(pid)
def add_program(*a,**kw): return _db.add_program(*a,**kw)
def update_program(*a,**kw): return _db.update_program(*a,**kw)
def delete_program(pid): return _db.delete_program(pid)
def get_genres(): return _db.get_genres()
def add_genre(a): return _db.add_genre(a)
def update_genre(t,y): return _db.update_genre(t,y)
def delete_genre(t): return _db.delete_genre(t)
def add_to_favorites(u,p): return _db.add_to_favorites(u,p)
def remove_from_favorites(u,p): return _db.remove_from_favorites(u,p)
def is_favorite(u,p): return _db.is_favorite(u,p)
# DÜZELTME 3: modül seviyesinde de tur_id desteği
def get_favorites(u,t=None,tur_id=None): return _db.get_favorites(u,t or tur_id)
def rate_content(u,p,puan): return _db.rate_content(u,p,puan)
def get_user_rating(u,p): return _db.get_user_rating(u,p)
def watch_content(*a): return _db.watch_content(*a)
def get_watch_history(uid): return _db.get_watch_history(uid)
def get_last_watch_position(u,p): return _db.get_last_watch_position(u,p)
def get_user_profile(uid): return _db.get_user_profile(uid)
def update_profile(*a,**kw): return _db.update_profile(*a,**kw)
def get_user_fav_genres(uid): return _db.get_user_fav_genres(uid)
def get_recommendations(uid): return _db.get_recommendations(uid)
def get_advanced_recommendations(uid): return _db.get_advanced_recommendations(uid)
def get_all_users(): return _db.get_all_users()
def get_user_watch_history(uid): return _db.get_user_watch_history(uid)
def toggle_user_active(u,a): return _db.toggle_user_active(u,a)
def get_reports(): return _db.get_reports()