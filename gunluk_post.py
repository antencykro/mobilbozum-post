# -*- coding: utf-8 -*-
# MOBİL BOZUM kanalına GitHub Actions ile GÜNDE 2 KEZ otomatik tanıtım postu atar.
# Sabah (08:00 TR) ve öğleden sonra (16:00 TR) FARKLI içerik gider.
# PC'ye ihtiyaç YOK — GitHub'ın sunucusunda çalışır.
# Bot token GitHub Secret'tan (BOT_TOKEN) okunur, repoda DURMAZ.
# Hangi postun atılacağı tarih + slot'a göre belirlenir; sayaç dosyası gerekmez.
#   slot 0 = sabah, slot 1 = öğleden sonra (workflow SLOT env ile verir)
#   index = (gün_sırası * 2 + slot) % post_sayısı  -> her gün 2 ardışık (farklı) post
import os, json, urllib.request, urllib.parse, datetime

TOKEN = os.environ["BOT_TOKEN"].strip()
CHAT  = -1003978579531                 # @mobilbozumm (doğrulandı)
ADMIN = "@razergoldbozumcu"
KANAL = "t.me/mobilbozumm"
API   = f"https://api.telegram.org/bot{TOKEN}/"

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

    # --- Yeni eklenenler: daha çok çeşit, daha ilgi çekici ---
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
]

# --- Tarih + slot ile sıradaki postu seç ---
slot = int(os.environ.get("SLOT", "0"))            # 0 = sabah, 1 = öğleden sonra
idx = (datetime.date.today().toordinal() * 2 + slot) % len(POSTS)
metin = POSTS[idx]

# --- Gönder ---
data = urllib.parse.urlencode({"chat_id": CHAT, "text": metin}).encode()
with urllib.request.urlopen(API + "sendMessage", data=data) as r:
    res = json.load(r)

if res.get("ok"):
    print(f"OK: post #{idx} (slot {slot}) gönderildi.")
else:
    raise SystemExit("HATA: " + json.dumps(res, ensure_ascii=False))
