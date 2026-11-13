# Kunlik yordamchi — Telegram bot

O'zbekiston foydalanuvchilari uchun ko'p funksiyali Telegram bot. Barcha muloqot **o'zbek tilida (lotin yozuvida)**, vaqt esa **Asia/Tashkent** mintaqasi bo'yicha.

> Bu loyiha boshqa loyihalardan (jumladan Nexio CRM'dan) mustaqil: o'z kodi va o'z bazasiga ega.

## Imkoniyatlar

| Xizmat | Tavsif | Ma'lumot manbasi |
|---|---|---|
| 🌤 Ob-havo | Tanlangan shahar uchun hozirgi holat va 4 kunlik prognoz | Open-Meteo |
| 💱 Valyuta | Markaziy bank rasmiy kurslari, summani so'mga hisoblash | cbu.uz |
| 🧮 Kalkulyator | `+ - * / ^ % //`, qavslar, `sqrt()`, `abs()`, `pi` (xavfsiz, `eval()`siz) | — |
| 📐 Birliklar | Uzunlik, vazn, harorat | — |
| 🌐 Tarjima | 10 ta tilga, asl til avtomatik aniqlanadi | MyMemory |
| ⏰ Eslatmalar | Yaratish, ko'rish, o'chirish | Bot bazasi |
| 📝 Vazifalar | Qo'shish, bajarildi deb belgilash, o'chirish | Bot bazasi |
| ❓ Savol-javob | Bot haqida tasdiqlangan javoblar; bilmasa, ochiq aytadi | — |

Har bir xizmatda **🔙 Orqaga** (asosiy menyu) va **❌ Bekor qilish** tugmalari bor. Tashqi xizmat ishlamasa, bot buni o'zbekcha tushuntiradi va hech qachon taxminiy ma'lumot ko'rsatmaydi.

## Loyiha tuzilishi

```text
daily_helper_bot/
├── app/
│   ├── main.py              # ishga tushirish (polling / webhook)
│   ├── config.py            # .env sozlamalari
│   ├── logging_config.py    # loglar (token avtomatik yashiriladi)
│   ├── handlers/            # har bir xizmat uchun alohida modul + router
│   ├── keyboards/           # menyu va umumiy tugmalar
│   ├── services/            # tashqi API'lar, kalkulyator, aylantirgich, eslatma yuboruvchi
│   ├── database/            # ulanish, modellar, repozitoriylar
│   └── utils/               # tekshirish va formatlash
├── tests/test_core.py
├── .env.example · .gitignore · requirements.txt · Dockerfile
```

## Ishga tushirish (lokal)

Python 3.11 yoki yangiroq kerak.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
# .env ichiga TELEGRAM_BOT_TOKEN ni kiriting (@BotFather dan)
python -m app.main
```

Birinchi ishga tushirishda jadvallar avtomatik yaratiladi (`data/bot.db`).

## Muhit o'zgaruvchilari (`.env`)

| O'zgaruvchi | Majburiy | Izoh |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ha | @BotFather bergan token |
| `DATABASE_URL` | yo'q | Standart: SQLite. PostgreSQL: `postgresql://user:parol@host:5432/db` |
| `LOG_LEVEL` | yo'q | `INFO` (standart) |
| `HTTP_TIMEOUT` | yo'q | Tashqi so'rovlar timeouti, soniya (standart 10) |
| `MYMEMORY_EMAIL` | yo'q | Tarjima kunlik limitini oshirish uchun |
| `WEBHOOK_URL` | yo'q | Bo'sh bo'lsa polling; to'ldirilsa webhook rejimi |
| `WEBHOOK_SECRET` | yo'q | Webhook so'rovlarini tasdiqlash uchun maxfiy matn (tavsiya etiladi) |
| `PORT` | yo'q | Webhook porti (standart 8080) |

`.env` fayli `.gitignore` ga qo'shilgan — uni hech qachon omborga yuklamang.

## Eslatmalar qanday yuboriladi

Eslatmalar bazada saqlanadi (vaqti UTC ko'rinishida). Bot ichidagi `JobQueue` har **30 soniyada** muddati kelgan eslatmalarni topib, foydalanuvchiga yuboradi va «yuborildi» deb belgilaydi.

- Bot o'chib yonsa ham eslatmalar yo'qolmaydi: qayta ishga tushganda muddati o'tganlari kechikish belgisi bilan yuboriladi.
- Aniqlik taxminan ±30 soniya.
- Buning uchun jarayon **doimiy ishlab turishi** shart.

## Deployment

⚠️ **Serverless funksiyalarda (Vercel, AWS Lambda, Cloud Functions va h.k.) ishlatmang.** Ular doimiy jarayonni ushlab turmaydi: polling to'xtaydi va eslatma yuboruvchi ishlamaydi.

Mos variantlar: VPS, Docker konteyner, Render / Railway / Fly.io kabi doimiy ishlaydigan xizmatlar.

**1) Doimiy server + polling (eng sodda).** `WEBHOOK_URL` ni bo'sh qoldiring, `python -m app.main` ni `systemd`/Docker bilan doimiy ishga tushiring.

**2) Webhook (hosting HTTPS manzil bersa).**
```env
WEBHOOK_URL=https://mening-botim.example.com
WEBHOOK_SECRET=uzun_tasodifiy_matn
PORT=8080
```
Bot `<WEBHOOK_URL>/webhook` manziliga webhook o'rnatadi. Eslatmalar uchun jarayon baribir doimiy ishlashi kerak (uxlab qoladigan bepul tariflarda eslatmalar kechikadi).

**3) Docker.**
```bash
docker build -t daily-helper-bot .
docker run -d --name helper --env-file .env -v helper_data:/srv/data daily-helper-bot
```
SQLite fayli `/srv/data` ichida — shu papkani volume qiling. Ko'p foydalanuvchi yoki hosting uchun **PostgreSQL** (`DATABASE_URL`) tavsiya etiladi, chunki ba'zi hostinglarda fayl tizimi qayta ishga tushganda tozalanadi.

## Testlar

```bash
pip install pytest
pytest
```
Testlar tarmoq va Telegram'siz ishlaydi (kalkulyator, aylantirgich, eslatma vaqtini tahlil qilish, log yashirish va h.k.).

## Xavfsizlik

- Token va kalitlar kodda yo'q, faqat `.env` dan o'qiladi.
- Loglarda token va maxfiy qiymatlar `[YASHIRILGAN]` bilan almashtiriladi; `httpx` so'rov manzillari loglanmaydi.
- Kalkulyator `eval()` ishlatmaydi: faqat ruxsat etilgan amallar bajariladi, daraja va natija hajmi cheklangan.
- Foydalanuvchi matni Telegram'ga HTML-xavfsiz (escape qilingan) holda yuboriladi.

## Ma'lumotlar va cheklovlar

- Tarjima — mashina tarjimasi (MyMemory), bepul limiti bor.
- Markaziy bank kursi rasmiy kurs; bank/almashtirish shoxobchalari kursidan farq qilishi mumkin.
- Bot faqat shaxsiy (private) chatlarda ishlaydi.
