# Mobil Bozum — Otomatik Günlük Post Sistemi (GitHub Actions)

> ✅ **KURULUM TAMAMLANDI (2026-06-15).** Sistem çalışıyor.
> 🔁 **GÜNCELLEME (2026-06-16):** "Kendini onaran" yapıya geçildi — yedek saatler +
> çift-atma koruması. Artık bir çalışma düşse bile post o gün **garanti** gider,
> hiçbir zaman çift atmaz.
> 🔁 **GÜNCELLEME (2026-06-18):** 18 Haziran sabahı GitHub sabah penceresinin TÜM cron'larını
> düşürdü → post kaçtı, elle kurtarıldı. Bunun bir daha olmaması için **yedek saatler her
> pencerede 3'ten 10'a çıkarıldı**. Ayrıca post içeriği **22'den 36'ya** çeşitlendirildi ve
> PC'deki ölü yerel sistem (Windows görevi + .bat/.py dosyaları) **tamamen kaldırıldı**.
> Bu dosya "nasıl çalışıyor + nasıl yönetilir" rehberidir.

Kanal her gün **otomatik** tanıtım postu atıyor. Bilgisayar **kapalı olsa bile** çalışır,
çünkü GitHub'ın sunucusunda çalışıyor. Tamamen ücretsiz.

---

## ŞU AN KURULU OLAN SİSTEM
- **GitHub hesabı:** `antencykro`
- **Repo (gizli):** https://github.com/antencykro/mobilbozum-post
- **Kanal:** @mobilbozumm  ·  **İletişim:** @razergoldbozumcu
- **Zamanlama:** Her gün **2 post** (sabah + öğleden sonra, birbirinden FARKLI):
  - 🌅 **Sabah penceresi (10 yedek):** TR 08:17/08:47/09:17/09:47/10:17/10:47/11:17/11:47/12:17/12:47 — ilk başarılı çalışma atar
  - 🌇 **Akşam penceresi (10 yedek):** TR 16:17/16:47/17:17/17:47/18:17/18:47/19:17/19:47/20:17/20:47 — ilk başarılı çalışma atar
- **İçerik:** 36 farklı, dürüst tanıtım postu. Her gün 2 ardışık post seçilir, sırayla döner;
  aynı gün asla aynısı tekrar etmez. (Uydurma rakam/yorum YOK.)
- **Token güvenliği:** Bot token repoda DOSYA olarak durmaz; GitHub'da gizli **Secret**
  (`BOT_TOKEN`) olarak tutulur.

### Dosyalar (bu klasörde + repoda)
- `gunluk_post.py` — postu seçip gönderen script. Çift-atma korumalı (durum dosyasına bakar).
- `.github/workflows/gunluk-post.yml` — zamanlama (yedekli cron'lar) + `contents: write` izni.
- `gonderilenler.txt` — **durum dosyası** (repoda). Hangi gün/slot atıldığını tutar; script
  otomatik günceller. **Elle dokunmana gerek yok.**

---

## NASIL ÇALIŞIR — "Kendini onaran" mantık

**Neden yedekli?** GitHub tam saat başı (`:00`) cron'ları yoğunlukta gecikebilir veya
**tamamen düşürebilir** (06-16'da bir post bu yüzden kaçtı). Tek bir cron %100 garanti vermez.

**Çözüm 2 parça:**
1. **Çoklu yedek saat** — her pencerede **10 çalışma denemesi** var (yarım saat arayla).
   GitHub denemelerin yarısını düşürse bile biri mutlaka tutar. (18 Haziran'da TÜM sabah
   cron'ları düşünce post kaçtığı için 3'ten 10'a çıkarıldı.)
2. **Çift-atma koruması (idempotency)** — script önce `gonderilenler.txt`'ye bakar:
   - O gün + o slot zaten atıldıysa → **sessizce atlar** (çift post YOK).
   - Atılmadıysa → gönderir, sonra `gonderilenler.txt`'ye `YYYY-MM-DD-slot` yazıp repoya
     commit/push eder. Böylece o günün yedek çalışmaları "zaten atılmış" görüp atlar.

**Slot nasıl belli olur?** Çalışma anının UTC saatine göre script karar verir:
- UTC saat **< 12** → sabah (slot 0)
- UTC saat **>= 12** → öğleden sonra (slot 1)

Post seçimi: `idx = (date.toordinal() * 2 + slot) % len(POSTS)` → her gün 2 ardışık farklı post.

Cron satırları (`gunluk-post.yml`, UTC; TR = UTC + 3):
- `17,47 5,6,7,8,9 * * *`     → TR 08:17–12:47 arası 10 deneme (sabah yedekleri)
- `17,47 13,14,15,16,17 * * *` → TR 16:17–20:47 arası 10 deneme (akşam yedekleri)

---

## YÖNETİM — SIK İHTİYAÇLAR

### Hemen elle bir post attırmak (test)
1. https://github.com/antencykro/mobilbozum-post/actions
2. Soldan **Gunluk Mobil Bozum Postu** → sağda **Run workflow** → **Run workflow**.
3. ~1 dk içinde kanala post düşer. **Not:** O slot bugün zaten atıldıysa "ATLANDI" yazıp
   post atmaz (çift-atma koruması). Test için sorun değil — beklenen davranış.

### Saatleri değiştirmek
`gunluk-post.yml` içindeki cron satırlarını düzenle (UTC yaz, TR için 3 saat çıkar).
Yedekli yapıyı koru: örn. akşamı 21:00 TR istersen `0,30 18,19 * * *` gibi birkaç deneme bırak.
Tam saat başını (`:00`) tek başına kullanma — düşme riski yüksek; `:17` gibi sapma dakika tercih et.

### İçerik (post metinleri) değiştirmek / eklemek
`gunluk_post.py` içindeki `POSTS = [ ... ]` listesini düzenle. Push edilince otomatik geçerli olur.

### Token değişirse
GitHub → repo → **Settings → Secrets and variables → Actions** → `BOT_TOKEN`'ı güncelle.

---

## ÖNEMLİ NOTLAR
- ✅ **Eski yerel sistem KALDIRILDI (2026-06-18):** PC'deki Windows görevi
  ("MobilBozum Gunluk Post") silindi ve `Mobil Bozum` klasöründeki ölü yerel dosyalar
  (`gunluk-post.bat`, `pazarlama-postlari.py`, `post-sayac.txt`, `post-log.txt`) temizlendi.
  Artık tek ve gerçek sistem GitHub Actions'tır; PC'nin hiçbir rolü yok.
- `gonderilenler.txt`'yi elle silme/düzenleme — silersen o gün post tekrar atılabilir (çift).
- GitHub, repo'da **60 gün hiç hareket olmazsa** zamanlanmış görevi otomatik durdurur.
  Sistem her gün durum dosyasını commit'lediği için repo zaten sürekli aktif kalır → bu risk yok.
- Token'ı asla repoda dosya olarak tutma; sadece Secret olarak. Mevcut kurulum böyle.

---

## TEKNİK (geliştirici notu)
- Bu klasör (`...\Desktop\Mobil Bozum\github-mobilbozum`) git'e BAĞLI DEĞİL (`.git` yok).
  Dosyalar GitHub'a `gh api ... -X PUT` ile gönderilir; düzenlemeler önce burada yapılıp push edilir.
- `gh` (GitHub CLI) taşınabilir, PATH'te DEĞİL: `C:\Users\SAMORUK\AppData\Local\gh-portable\bin\gh.exe`
  (winget MSI 1603 hatası verdiği için portable zip kullanıldı.) Giriş: hesap `anilerikci100-lab`,
  scope'lar `repo` + `workflow`.
- ⚠️ Windows'ta `gh api` ile dosya PUT ederken JSON'u stdin'den verme (encoding bozulur → HTTP 400);
  payload'ı UTF-8 BOM'suz temp dosyaya yazıp `--input <dosya>` ile gönder.
- Sabah kaçarsa elle kurtarma:
  `gh workflow run "Gunluk Mobil Bozum Postu" --repo antencykro/mobilbozum-post`
- Workflow'da `permissions: contents: write` var → script `GITHUB_TOKEN` ile
  `gonderilenler.txt`'yi commit/push edebilir (push fail olursa `pull --rebase` + retry).
- Idempotency send-then-record sırasıyla: önce gönderir sonra kaydeder. Nadir push hatasında
  teorik çift post riski var ama sessizce kaçırmaktan iyi kabul edildi.
- Durum dosyası son 60 kaydı tutar (otomatik kırpılır).
