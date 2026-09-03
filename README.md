# Digital Store Bot (Phase 1 MVP)

Telegram-এ ফাইল/ভিডিও/ডকুমেন্ট বিক্রির বট। আসল ফাইল কখনো সার্ভার/ফোনে জমা থাকে
না — সব থাকে একটা প্রাইভেট **Storage Channel**-এ। ডাটাবেজও নিয়মিত অটোমেটিক
একটা প্রাইভেট **Backup Channel**-এ ব্যাকআপ হয়, তাই Termux বন্ধ হলে বা নতুন
হোস্টে (Railway/VPS) সরিয়ে নিলেও ডেটা হারায় না।

## ফিচার (Phase 1 — সম্পূর্ণ)
- Welcome message + welcome image (`assets/welcome.jpg` বসিয়ে দিন)
- ক্যাটাগরি + প্রোডাক্ট ব্রাউজিং, প্রতিটি প্রোডাক্টে ঐচ্ছিক 🔍 Preview/Sample ফাইল
- 🪙 Coin Wallet (ম্যানুয়াল bKash/Nagad টপ-আপ, অ্যাডমিন অ্যাপ্রুভ)
- ⭐ Telegram Stars-এ সরাসরি পেমেন্ট (auto verify + auto delivery)
- 🎟️ Coupon system (percent / fixed-coin discount)
- 🎁 Referral system (unique link, প্রথম কেনাকাটায় রেফারারকে কয়েন রিওয়ার্ড)
- 📚 Purchased Library / re-download
- 👑 Admin panel: প্রোডাক্ট অ্যাড (+ Preview আপলোড), প্রোডাক্ট লিস্ট/Enable-Disable,
  ক্যাটাগরি অ্যাড, কয়েন ম্যানেজ, কুপন তৈরি, ব্যান/আনব্যান, সেলস স্ট্যাটস, ম্যানুয়াল ব্যাকআপ
- `/cancel` — যেকোনো মাল্টি-স্টেপ ফ্লো (যেমন প্রোডাক্ট অ্যাড করার মাঝপথে) থেকে বের হওয়ার কমান্ড
- 💾 Auto DB backup (pinned message) + auto restore on boot
- 🛡️ গ্লোবাল এরর হ্যান্ডলার — কোনো একটা মেসেজে বাগ থাকলেও পুরো বট ক্র্যাশ করবে না
- 🔄 Watchdog script (Termux ক্র্যাশ রিকভারি)

## সেটআপ (Termux / VPS / যেকোনো জায়গায় একই ধাপ)

1. **দুটো প্রাইভেট Telegram চ্যানেল বানান:**
   - একটা Storage Channel (আসল ফাইল থাকবে)
   - একটা Backup Channel (DB ব্যাকআপ থাকবে)
   - দুটো চ্যানেলেই বটকে **Admin** বানান (Post + Pin permission সহ)
   - চ্যানেলের numeric ID বের করতে চ্যানেলে যেকোনো মেসেজ ফরওয়ার্ড করুন
     [@userinfobot](https://t.me/userinfobot)-এ, অথবা @RawDataBot ব্যবহার করুন

2. **রিপো ক্লোন করুন:**
   ```bash
   git clone <your-private-repo-url>
   cd bot-project
   pip install -r requirements.txt
   ```

3. **`.env` বানান:**
   ```bash
   cp .env.example .env
   nano .env   # BOT_TOKEN, ADMIN_IDS, STORAGE_CHANNEL_ID, BACKUP_CHANNEL_ID বসান
   ```

4. **চালান:**
   ```bash
   python main.py
   ```
   প্রথমবার চালু হলে এটি:
   - Backup channel-এ পিন করা ব্যাকআপ থাকলে সেটা restore করবে
   - না থাকলে fresh ডাটাবেজ বানাবে (টেবিল অটো তৈরি)

## Termux-এ ২৪/৭ চালানো

```bash
termux-wake-lock
chmod +x run.sh
tmux new -s bot
./run.sh
```

`run.sh` একটা watchdog — বট ক্র্যাশ করলে ৫ সেকেন্ড পর নিজে থেকেই আবার চালু হয়ে
যাবে। `tmux` সেশনে রাখলে Termux অ্যাপ বন্ধ করলেও বট চলতে থাকবে (`tmux detach` =
Ctrl+B তারপর D)। এছাড়া Android Settings থেকে Termux-কে Battery Optimization
থেকে বাদ দিন, নাহলে ফোন নিজেই প্রসেস মেরে ফেলতে পারে।

## Railway-তে migrate করলে
- একই কোডবেস, শুধু Railway-তে Environment Variables ট্যাবে `.env`-এর ভ্যালুগুলো বসান
- `Procfile` আগে থেকেই আছে (`worker: python main.py`)
- Railway-এর ডিস্ক ephemeral — কিন্তু backup/restore সিস্টেম থাকায় প্রতিবার
  redeploy-তে backup channel থেকে ডেটা ফিরে আসবে, তাই আলাদা Volume লাগবে না

## অ্যাডমিন কমান্ড
- `/admin` — অ্যাডমিন প্যানেল খুলুন (প্রোডাক্ট/ক্যাটাগরি/কয়েন/কুপন/ব্যান/স্ট্যাটস/ম্যানুয়াল ব্যাকআপ)

## গুরুত্বপূর্ণ নিরাপত্তা নোট
- `.env` কখনো git push করবেন না (এমনকি প্রাইভেট রিপো হলেও) — `.gitignore`-এ আগে থেকেই বাদ দেওয়া আছে
- শুধু `ADMIN_IDS`-এ থাকা Telegram ID-গুলোই admin ফিচার ব্যবহার করতে পারবে

## পরে (Phase 2) যোগ হবে
Daily check-in, VIP tiers, Wishlist, Rating/Review, Leaderboard, Support
ticket, Multi-admin roles, Analytics dashboard, Multi-language।
