# -*- coding: utf-8 -*-
# MOBİL BOZUM kanalına GitHub Actions ile GÜNDE 2 KEZ otomatik tanıtım postu atar.
# Sabah (08:xx TR) ve öğleden sonra (16:xx TR) FARKLI içerik gider.
# PC'ye ihtiyaç YOK — GitHub'ın sunucusunda çalışır. Token GitHub Secret'tan (BOT_TOKEN) okunur.
#
# *** KENDİNİ ONARAN / ÇİFT-ATMA KORUMALI ***
# GitHub tam saat başı cron'ları bazen düşürür. Bu yüzden her pencerede BİRDEN FAZLA
# yedek saat çalışır (workflow'a bak). Hangi postun atıldığı `gonderilenler.txt`
# durum dosyasına yazılır ve repoya commit'lenir:
#   - Bugün bu slot zaten atıldıysa  -> sessizce ATLANIR (çift post olmaz).
#   - Atılmadıysa -> gönderilir, durum dosyası güncellenir + push'lanır.
# Böylece bir çalışma düşse bile sonraki yedek saat postu garanti gönderir; tekrar olmaz.
#
# Slot, ÇALIŞMA ANININ UTC SAATİNE göre belirlenir:
#   UTC saat < 12  -> sabah (slot 0)
#   UTC saat >= 12 -> öğleden sonra (slot 1)
# Post seçimi: idx = (gün_sırası * 2 + slot) % post_sayısı  -> her gün 2 ardışık FARKLI post.
import os, sys, json, urllib.request, urllib.parse, datetime, subprocess

TOKEN = os.environ["BOT_TOKEN"].strip()
CHAT  = -1003978579531                 # @mobilbozumm (doğrulandı)
ADMIN = "@razergoldbozumcu"
KANAL = "t.me/mobilbozumm"
API   = f"https://api.telegram.org/bot{TOKEN}/"
STATE = "gonderilenler.txt"            # her satır: YYYY-MM-DD-slot

# --- Dürüst, ilgi çekici, her zaman geçerli tanıtım postları (uydurma rakam/yorum YOK) ---
POSTS = [
    (f"📊 GÜNCEL ORANLAR AKTİF\n\niTunes · Razer Gold · PUBG UC · Gift Card ve daha fazlası "
     f"için bugünkü oranlar hazır.\n\n💬 Net oran için yaz 👉 {ADMIN}\n⚡ İşlem dakikalar içinde."),

    (f"⚙️ 3 ADIMDA NAKİT\n\n1️⃣ {ADMIN} adresine yaz\n2️⃣ Kart/bakiyeni ve tutarı söyle\n"
     f"3️⃣ Oranı onayla, paranı al\n\nBu kadar basit. 🟢"),

    (f"🔒 GÜVENLE İŞLEM\n\n✅ Oran işlem ÖNCESİ net söylenir, sürpriz yok\n"
     f"✅ Adım adım açık iletişim\n✅ Anında ödeme: Faster / Havale / Kripto\n\n"
     f"Sorularını çekinmeden sor 👉 {ADMIN}"),

    (f"💰 NELERİ BOZUYORUZ?\n\n🍎 iTunes  🟢 Razer Gold  🎮 PUBG UC  🎁 Gift Card\n"
     f"📱 Mobil Ödeme  💬 SMS  🟦 Paycell  🔴 Moneypay  🕹️ Steam\n\nElinde varsa yaz 👉 {ADMIN}"),

    (f"🕐 7/24 AKTİFİZ\n\nHafta sonu, gece, tatil fark etmez — bozum işlemlerin için "
     f"her an buradayız.\n\n👉 {ADMIN}"),

    (f"🍎 iTunes BAKİYEN Mİ VAR?\n\nKullanmadığın iTunes kodunu/bakiyeni yüksek oranla "
     f"anında nakde çevir.\n\n💬 {ADMIN}"),

    (f"🟢 RAZER GOLD BOZUM\n\nTL veya USD Razer Gold bakiyeni güvenle ve hızlıca boz.\n"
     f"Güncel oran için yaz 👉 {ADMIN}"),

    (f"🎮 OYUNCULAR İÇİN\n\nPUBG UC, Steam, Valorant, COD Mobile ve oyun kodlarını "
     f"nakde çeviriyoruz.\n\n👉 {ADMIN}"),

    (f"🏦 ÖDEME YÖNTEMLERİ\n\n⚡ Faster (anında)\n🏦 Havale / EFT\n₿ Kripto\n\n"
     f"Sana uygun olanı seç, işleme başlayalım 👉 {ADMIN}"),

    (f"⚡ ANINDA ÖDEME\n\nİşlem onaylanır onaylanmaz ödemen yapılır — bekletme yok.\n\n"
     f"Hemen yaz 👉 {ADMIN}"),

    (f"🎁 GIFT CARD BOZUM\n\nElindeki hediye kartı / dijital kodu değerlendirelim.\n"
     f"Hangi kart olduğunu yaz, oranı söyleyelim 👉 {ADMIN}"),

    (f"📢 Kanalı arkadaşlarınla paylaş!\n\nGüncel oranlar ve fırsatlar önce burada: {KANAL}\n"
     f"İşlem için 👉 {ADMIN}"),

    # --- Daha çok çeşit, daha ilgi çekici ---
    (f"🤔 ELİNDE ATIL KOD MU VAR?\n\nÇekmecede unuttuğun, kullanmadığın bir kart kodu / bakiye "
     f"boş yere durmasın. Nakde çevirelim.\n\n👉 {ADMIN}"),

    (f"❓ NEDEN BİZ?\n\n✅ Oran baştan net — pazarlık derdi yok\n✅ Hızlı dönüş, hızlı ödeme\n"
     f"✅ Açık ve dürüst iletişim\n\nFarkı gör 👉 {ADMIN}"),

    (f"📱 MOBİL ÖDEME & SMS BOZUM\n\nTurkcell · Vodafone · Türk Telekom faturana yansıyan "
     f"mobil ödeme bakiyeni nakde çevir.\n\nDetay için yaz 👉 {ADMIN}"),

    (f"🕹️ STEAM CÜZDAN BOZUM\n\nSteam bakiyeni / cüzdan kodunu güvenle nakde çeviriyoruz.\n"
     f"Güncel oran için 👉 {ADMIN}"),

    (f"💵 YÜKSEK TUTAR? SORUN DEĞİL\n\nKüçük ya da büyük — her tutarda işlem yapıyoruz, "
     f"aynı güven ve hızla.\n\nKonuşalım 👉 {ADMIN}"),

    (f"🙋 İLK DEFA MI BOZDURACAKSIN?\n\nMerak etme — her adımı tek tek anlatırız, "
     f"oranı önceden söyleriz, sonra işleme geçeriz.\n\nÇekinmeden yaz 👉 {ADMIN}"),

    (f"🆓 ORAN SORMAK ÜCRETSİZ\n\nFiyat sormak seni bağlamaz. Önce oranı öğren, "
     f"beğenirsen işleme geçeriz.\n\nHemen sor 👉 {ADMIN}"),

    (f"₿ KRİPTO İLE AL\n\nİstersen ödemeni kripto olarak da alabilirsin — hızlı ve pratik.\n"
     f"Detaylar için 👉 {ADMIN}"),

    (f"🟦 PAYCELL & 🔴 MONEYPAY BOZUM\n\nPaycell ve Moneypay bakiyeni de nakde çeviriyoruz.\n"
     f"Tutarı yaz, oranı söyleyelim 👉 {ADMIN}"),

    (f"💬 AKLINDA SORU MU VAR?\n\nNasıl çalışıyor, oran ne, ödeme ne kadar sürer... "
     f"ne merak ediyorsan sor. Cevaplamaktan memnuniyet duyarız.\n\n👉 {ADMIN}"),

    # --- Ek çeşitlilik: farklı kartlar, platformlar ve açılar ---
    (f"🛒 GOOGLE PLAY & AMAZON\n\nGoogle Play ve Amazon hediye kodlarını da nakde çeviriyoruz.\n"
     f"Kodun türünü ve tutarını yaz, oranı söyleyelim 👉 {ADMIN}"),

    (f"🎮 KONSOL OYUNCULARI\n\nPlayStation, Xbox ve Nintendo bakiye/kodlarını güvenle boz.\n"
     f"Hangisi elindeyse yaz 👉 {ADMIN}"),

    (f"₿ USDT / KRİPTO İLE ÖDEME\n\nİstersen ödemeni USDT (Tether) veya tercih ettiğin kripto "
     f"olarak al — hızlı ve pratik.\n\nDetaylar için 👉 {ADMIN}"),

    (f"📸 KODU GÖNDER, GERİSİ BİZDE\n\nKartının/bakiyenin bilgisini paylaş, oranı söyleyelim, "
     f"onaylarsan işlemi biz hallederiz.\n\nBaşlayalım 👉 {ADMIN}"),

    (f"🔎 ORANLARI KARŞILAŞTIR\n\nAcele etme — başka yerlere de bak, sonra bize sor. "
     f"Net oranımızı duyunca karar ver.\n\nOran için 👉 {ADMIN}"),

    (f"💎 KÜÇÜK TUTAR DA OLUR\n\nElindeki bakiye küçük diye çekinme — düşük tutarlı işlemleri de "
     f"aynı ciddiyetle yapıyoruz.\n\nYaz yeter 👉 {ADMIN}"),

    (f"🎉 TATİL & BAYRAMDA DA AÇIĞIZ\n\nResmi tatil, bayram, hafta sonu... fark etmez. "
     f"Bozum işlemlerin için her gün buradayız.\n\n👉 {ADMIN}"),

    (f"❓ SSS: NE KADAR SÜRER?\n\nOranı onayladıktan sonra ödeme genelde kısa sürede yapılır — "
     f"bekletme sevmeyiz.\n\nDetay için yaz 👉 {ADMIN}"),

    (f"🎵 DİJİTAL KOD & ABONELİK\n\nElindeki dijital hediye kodlarını değerlendirelim. "
     f"Hangi koda sahipsen yaz, uygun mu bakalım 👉 {ADMIN}"),

    (f"🤝 ŞEFFAF İLETİŞİM\n\nGizli kapaklı iş yok: oranı baştan söyleriz, adımları açıklarız, "
     f"sonra işleme geçeriz.\n\nSorununu çekinmeden ilet 👉 {ADMIN}"),

    (f"🌙 GECE GEÇ Mİ OLDU?\n\nGeç saatte de mesaj at — uygun olunca en kısa sürede döneriz.\n"
     f"Yaz 👉 {ADMIN}"),

    (f"📌 NASIL BAŞLARIM?\n\nTek yapman gereken {ADMIN} adresine \"merhaba\" yazıp elindeki "
     f"kartı/bakiyeyi söylemek. Gerisini birlikte hallederiz.\n\n👉 {ADMIN}"),

    (f"💼 DÜZENLİ İŞLEM Mİ YAPIYORSUN?\n\nSık sık bozum yapıyorsan bize yaz — işini hızlandıralım, "
     f"sürecini kolaylaştıralım.\n\n👉 {ADMIN}"),

    (f"📲 EN GÜNCEL FIRSATLAR BURADA\n\nYeni oranlar ve duyurular önce kanalda paylaşılır. "
     f"Takipte kal: {KANAL}\n\nİşlem için 👉 {ADMIN}"),
]

# --- Slot + bugünün anahtarı ---
now   = datetime.datetime.utcnow()
slot  = 0 if now.hour < 12 else 1                  # UTC<12 sabah, >=12 öğleden sonra
today = datetime.date.today()
key   = f"{today.isoformat()}-{slot}"

# --- Bugün bu slot zaten atıldı mı? ---
sent = []
if os.path.exists(STATE):
    with open(STATE, encoding="utf-8") as f:
        sent = [l.strip() for l in f if l.strip()]

if key in sent:
    print(f"ATLANDI: {key} -> bu slot bugün zaten gönderilmiş, çift post yok.")
    sys.exit(0)

# --- Postu seç ve gönder ---
idx   = (today.toordinal() * 2 + slot) % len(POSTS)
metin = POSTS[idx]
data  = urllib.parse.urlencode({"chat_id": CHAT, "text": metin}).encode()
with urllib.request.urlopen(API + "sendMessage", data=data) as r:
    res = json.load(r)
if not res.get("ok"):
    raise SystemExit("HATA: " + json.dumps(res, ensure_ascii=False))
print(f"OK: post #{idx} (slot {slot}, {key}) gönderildi.")

# --- Durumu kaydet (son 60 kayıt yeter) + repoya commit/push ---
sent.append(key)
sent = sent[-60:]
with open(STATE, "w", encoding="utf-8") as f:
    f.write("\n".join(sent) + "\n")

def git(*a):
    subprocess.run(["git", *a], check=True)

try:
    git("config", "user.name", "mobilbozum-bot")
    git("config", "user.email", "actions@github.com")
    git("add", STATE)
    git("commit", "-m", f"durum: {key} gonderildi")
    try:
        git("push")
    except subprocess.CalledProcessError:
        git("pull", "--rebase")
        git("push")
    print("Durum dosyası güncellendi.")
except subprocess.CalledProcessError as e:
    # Post zaten GİTTİ; sadece durum kaydı başarısız oldu. Çalışmayı patlatma.
    print(f"UYARI: durum push edilemedi ({e}). Post gönderildi ama kayıt yapılamadı.")
