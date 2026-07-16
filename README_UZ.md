# Oylik ish haqi hisoblash tizimi (veb-ilova)

Oliy ta'lim muassasasi uchun login/parol bilan kiradigan, rol bo'yicha dostup beriladigan
onlayn ilova. Ma'lumotlar serverdagi bazada saqlanadi — barcha foydalanuvchilar bir xil
ma'lumotni ko'radi.

## Imkoniyatlari

- **Login / parol** bilan kirish (parollar shifrlangan holda saqlanadi).
- **3 xil rol (dostup darajasi):**
  - **Admin** — hamma narsa: xodimlarni tahrirlash, soliq stavkalarini o'zgartirish, foydalanuvchilarni boshqarish.
  - **Muharrir** — xodim ma'lumotlarini kiritadi/tahrirlaydi (sozlama va foydalanuvchilarga tegmaydi).
  - **Ko'ruvchi** — faqat ko'radi va eksport qiladi, o'zgartira olmaydi.
- **3 ta bo'lim:** Professor-o'qituvchilar, Ma'muriyat, Texnik xodimlar (har biriga mos ustunlar).
- Avtomatik hisoblash: asosiy maosh, soatbay, ustamalar, mukofot, daromad solig'i (12%), INPS (0,1%), kasaba (1%), avans → **qo'lga tegadigan** summa.
- Boshqaruv paneli (jami ko'rsatkichlar), xodim hisob varaqasi (raschyot listok), Excel/CSV eksport-import.
- O'zgarishlar **avtomatik saqlanadi**.

---

## 1-usul (tavsiya etiladi): Render.com da bepul joylashtirish

Bunda ilova internetда ishlaydi va odamlaringiz istalgan joydan kiradi.

**a) Fayllarni GitHub'ga joylash**
1. https://github.com da bepul hisob oching.
2. "New repository" → nom bering (masalan `ish-haqi`) → Create.
3. Ushbu papkadagi **barcha fayllarni** repositoryga yuklang (Add file → Upload files → hammasini tashlang → Commit).

**b) Render'da ishga tushirish**
1. https://render.com da hisob oching ("Sign in with GitHub" bilan kiring).
2. **New +** → **Blueprint** → yuqoridagi repositoryni tanlang → **Apply**.
   - `render.yaml` fayli hammasini avtomatik sozlaydi: server, ma'lumotlar bazasi diski va maxfiy kalit.
3. Deploy tugagach, Render sizga manzil beradi (masalan `https://ish-haqi.onrender.com`).
4. Shu manzilni odamlaringizga bering — ular login/parol bilan kiradi.

> Bepul tarifda ilova bir muddat ishlatilmasa "uxlaydi", keyingi kirishda 30–50 soniya sekin ochiladi. Doimiy tez ishlashi uchun Render'da arzon tarifga o'tish mumkin.

**Muqobil:** xuddi shu tarzda https://railway.app yoki https://fly.io da ham joylashtirса bo'ladi.

---

## 2-usul: O'z kompyuteringiz yoki serveringizda

```bash
pip install -r requirements.txt
# Ma'lumotlar shu papkadagi ish_haqi.db fayliga saqlanadi
python app.py
```
Brauzerda `http://localhost:5000` manzilini oching. Ichki tarmoqda ishlatish uchun serverning
IP manzilidan foydalaning (masalan `http://192.168.1.50:5000`).

Ishlab chiqarish (production) uchun:
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

---

## Birinchi kirish (MUHIM)

- **Login:** `admin`
- **Parol:** `admin123`

⚠️ **Birinchi kirishdayoq parolni o'zgartiring:** yuqoridagi **"Foydalanuvchilar"** bo'limi →
"O'z parolimni o'zgartirish".

Keyin shu bo'limdan xodimlaringizga **login/parol yarating** va har biriga rol (Admin / Muharrir /
Ko'ruvchi) bering. Kimga qaysi huquq berishni o'zingiz belgilaysiz.

---

## Xavfsizlik

- Barcha parollar shifrlangan (hash) holda saqlanadi — bazada ochiq parol yo'q.
- Render/Railway avtomatik **HTTPS** (xavfsiz ulanish) beradi.
- Har bir foydalanuvchiga kuchli parol qo'ying va rolni ehtiyotkorlik bilan bering.
- Yagona adminni tasodifan o'chirib/pasaytirib bo'lmaydi (tizim himoyalaydi).

## Sozlamalarni o'zgartirish

Soliq va ushlanma stavkalari (12% / 0,1% / 1% / BHM) admin uchun **Sozlamalar** bo'limida — bir joyda
o'zgartiriladi va barcha hisob-kitoblarga qo'llaniladi.
