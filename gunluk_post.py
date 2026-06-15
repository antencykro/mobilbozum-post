# -*- coding: utf-8 -*-
# MOBİL BOZUM kanalına GitHub Actions ile her gün otomatik tanıtım postu atar.
# PC'ye ihtiyaç YOK — GitHub'ın sunucusunda çalışır.
# Bot token'ı GitHub Secret'tan (BOT_TOKEN) okunur, repoda DURMAZ.
# Hangi postun atılacağı tarihe göre belirlenir (her gün 1 ilerler), sayaç dosyası gerekmez.
import os, json, urllib.request, urllib.parse, datetime

TOKEN = os.environ["BOT_TOKEN"].strip()
CHAT  = -1003978579531                 # @mobilbozumm (doğrulandı)
ADMIN = "@razergoldbozumcu"
KANAL = "t.me/mobilbozumm"
API   = f"https://api.telegram.org/bot{TOKEN}/"

# --- Dürüst, her zaman geçerli tanıtım postları (uydurma rakam/yorum YOK) ---
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
]

# --- Tarihe göre sıradaki postu seç (her gün 1 ilerler, liste bitince başa döner) ---
idx = datetime.date.today().toordinal() % len(POSTS)
metin = POSTS[idx]

# --- Gönder ---
data = urllib.parse.urlencode({"chat_id": CHAT, "text": metin}).encode()
with urllib.request.urlopen(API + "sendMessage", data=data) as r:
    res = json.load(r)

if res.get("ok"):
    print(f"OK: post #{idx} gönderildi.")
else:
    raise SystemExit("HATA: " + json.dumps(res, ensure_ascii=False))
