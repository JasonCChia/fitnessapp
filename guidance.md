# FitDiscipline
## AI-Powered Workout & Nutrition Coach
App Ideation Document v1.3

> **Changelog v1.3:** 6 inkonsistensi kritis diperbaiki — prinsip produk, DDL schema, arsitektur AI call, signature service, jumlah step onboarding, dan tipe UUID. Lihat Bagian 14 untuk daftar lengkap perubahan.

---

## Architecture Contract (Backend)

Struktur backend wajib mengikuti modular monolith:

```txt
Blueprint -> Schema Validation -> Service -> Repository -> Database
```

### Folder Responsibility
- `blueprints/`: route layer only (request parsing, auth checks, response shaping).
- `schemas/`: request/response shape dan reusable validators.
- `services/`: business orchestration dan domain rules.
- `repositories/`: seluruh SQL/query data access.
- `db/`: connection/bootstrap/schema/migrations.
- `core/`: middleware, exception, response contract, security, utils.

### Project Structure (Current Target)
```txt
project/
├── app.py
├── config.py
├── guidance.md
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── wsgi.py
├── asgi.py
├── assets/
├── templates/
├── blueprints/
├── core/
├── db/
├── models/
├── repositories/
├── services/
├── schemas/
├── tasks/
├── tests/
├── docs/
└── storage/
```

### Hard Rules
- Dilarang menaruh SQL langsung di blueprint.
- Dilarang menaruh business logic berat di template atau route.
- Dilarang hardcode secret di source code.
- Dilarang bypass repository dari route.
- Semua response API harus konsisten lewat helper response standard.

### Feature Expansion Rule
Saat menambah fitur baru, wajib tambah minimal:
- `blueprints/<feature>/`
- `schemas/request|response|validators`
- `services/<feature>/`
- `repositories/<feature>_repository.py`
- `tests/` (unit + api minimal)
- `docs/` update

---

## 1. Vision & Goals
FitDiscipline adalah personal coach berbasis AI yang membantu pengguna mencapai target badan ideal melalui program workout dan nutrisi yang dipersonalisasi, dengan sistem discipline scoring yang adaptif.

### Core Principles
- AI sebagai coach, bukan sekadar tracker: AI analisa, propose, lalu user konfirmasi.
- Data tersimpan di server (MySQL), diakses via backend REST API yang dikelola sendiri. Tidak ada third-party yang menyimpan data user selain AI provider yang dipilih user secara eksplisit.
- Service abstraction: semua integrasi eksternal (AI, storage, backend) bisa diganti tanpa ubah UI.
- Konfirmasi sebelum apply: AI tidak pernah auto-apply perubahan program tanpa persetujuan user.

---

## 2. App Flow - Awal Sampai Akhir

### FASE 1 - Onboarding & Setup Profil
| Step | Action | Detail |
| --- | --- | --- |
| 1.1 | Input profil dasar | Nama, usia, jenis kelamin, berat badan saat ini, tinggi badan |
| 1.2 | Input gaya hidup | Rata-rata jam tidur/hari (disimpan sebagai `sleep_target_hours`), level aktivitas (sedentary, light, moderate, active) — disimpan ke `user_preferences` |
| 1.3 | Set target | Target berat badan, deadline target opsional (disimpan sebagai `goal_deadline_date` di `user_preferences`), tipe tujuan: cut, bulk, maintain |
| 1.4 | Input preferensi makan | Pantangan makanan, alergi, preferensi (vegetarian, halal, dll) |
| 1.5 | Input preferensi workout | Lokasi (gym/rumah), alat yang tersedia, hari tersedia per minggu, durasi per sesi |
| 1.6 | Minta izin notifikasi | Request notification permission (iOS/Android) — harus dilakukan di onboarding, bukan saat pertama kali schedule notif |
| 1.7 | Input API Key (opsional) | User bisa pasang API key sendiri (Anthropic/OpenAI/Gemini). Disimpan via platform keychain (expo-secure-store), bukan ke storage biasa. Tanpa key, AI pakai mode terbatas |

### FASE 2 - AI Analisa & Proposal Program
| Step | Action | Detail |
| --- | --- | --- |
| 2.1 | Hitung BMI & TDEE | App hitung otomatis: BMI, BMR (Mifflin-St Jeor), TDEE berdasarkan `activity_level` dari `user_preferences` |
| 2.2 | AI analisa profil | `AIService.analyzeProfile(userProfile)` -> hasilkan ringkasan kondisi fisik saat ini |
| 2.3 | AI propose program workout | `AIService.generateWorkoutPlan(profile, preferences)` -> draft program mingguan |
| 2.4 | AI propose menu makan | `AIService.generateMealPlan(profile, preferences, calories)` -> draft menu 7 hari |
| 2.5 | Tampilkan proposal ke user | User melihat ringkasan: target kalori/hari, program workout, contoh menu |
| 2.6 | User review & konfirmasi | User bisa edit, reject bagian tertentu, atau minta AI revisi sebelum confirm |
| 2.7 | Program aktif | Setelah confirm, program tersimpan dan mulai berjalan dari hari ini |

### FASE 3 - Daily Tracking (Loop Harian)
| Step | Action | Detail |
| --- | --- | --- |
| 3.1 | Buka app pagi | Dashboard tampil: task hari ini (workout + target makan), sisa kalori, discipline score |
| 3.2 | Log sarapan | User ketik nama makanan -> `CalorieService.estimate("nasi goreng")` yang secara internal memanggil `AIService.estimateCalories` jika online, atau fallback ke manual input / local database jika offline |
| 3.3 | Log workout | Centang sesi workout selesai, bisa tambah catatan (berat angkat, reps, dll) |
| 3.4 | Log makan siang & malam | Sama seperti sarapan, running total kalori terupdate real-time |
| 3.5 | Log tidur | Input jam tidur kemarin malam (atau auto dari jam buka app pertama kali) |
| 3.6 | Discipline score update | Score terhitung otomatis dari semua log hari ini (lihat sistem scoring di Bagian 5) |
| 3.7 | Malam: recap harian | Notifikasi/reminder ringkasan: kalori, workout, tidur, score hari ini |

### FASE 4 - Weekly AI Review
| Step | Action | Detail |
| --- | --- | --- |
| 4.1 | Trigger review | Otomatis 7 hari kalender setelah program aktif dimulai (rolling window dari `confirmed_at` workout plan), atau user minta manual kapan saja |
| 4.2 | AI analisa minggu lalu | `AIService.weeklyReview(weekLogs)` -> evaluasi progress, identifikasi pola |
| 4.3 | AI propose adjustment | Jika progress lambat/cepat, AI propose: ubah kalori target, intensitas workout, atau menu |
| 4.4 | User konfirmasi adjustment | Sama seperti Fase 2.6, user review dulu, baru apply |
| 4.5 | Update program | Program minggu depan tersimpan dengan penyesuaian baru |

### FASE 5 - Monthly Fitness Level Review
| Step | Action | Detail |
| --- | --- | --- |
| 5.1 | Trigger review | Dijalankan saat app dibuka (on-open check), bukan cron — cek apakah sudah >= 28 hari dari `last_monthly_review_at` di `user_preferences`. Jika ya, jalankan review |
| 5.2 | AI analisa bulan lalu | Kumpulkan data `fitness_capabilities` + `day_scores` + `workout_sessions` 30 hari terakhir |
| 5.3 | Propose level change | AI propose naik/turun/pertahankan level sesuai logika di Bagian 12 |
| 5.4 | User konfirmasi | Wajib konfirmasi user sebelum level berubah |
| 5.5 | Simpan snapshot baru | INSERT row baru ke `fitness_capabilities` (append-only), update `last_monthly_review_at` |

---

## 3. Daftar Screen & Komponen
| Screen | Components | AI Actions |
| --- | --- | --- |
| Onboarding | Form step-by-step (7 langkah termasuk notif permission & API key), progress bar, validasi tiap step | Tidak ada (pure input) |
| AI Setup | Loading state, preview proposal (workout + menu), tombol Edit/Revisi/Confirm | `analyzeProfile`, `generateWorkoutPlan`, `generateMealPlan` |
| Dashboard Utama | Discipline score ring, task hari ini (checklist), kalori ring, streak counter | Tidak ada (tampilkan data lokal) |
| Log Makanan | Search makanan, card estimasi kalori + macro, riwayat makanan hari ini, toggle manual input (offline fallback) | `estimateCalories(foodName)` via `CalorieService` |
| Log Workout | Checklist sesi dari program aktif, input sets/reps/weight per exercise | Tidak ada (pure input) |
| Program Workout | Tampilkan program mingguan aktif, bisa edit manual, tombol "Minta AI Revisi" | `reviseWorkoutPlan` (on-demand) |
| Menu Makan | Tampilkan menu 7 hari aktif, bisa swap satu item, tombol "Minta AI Ganti" | `swapMealItem`, `reviseMealPlan` |
| Progress & Stats | Grafik berat badan (dari `weight_logs`), grafik kalori 7/30 hari, grafik discipline score, milestone | Tidak ada (pure visualisasi) |
| Weekly Review | Card ringkasan minggu, proposal AI (highlight perubahan), tombol Setuju/Edit/Tolak | `weeklyReview`, `adjustProgram` |
| Settings | Profil, API Key input via secure keychain (+ test koneksi), pilih provider AI, export data (JSON), reset data | `testConnection(apiKey)` |

---

## 4. Service Architecture
Semua service di-inject sebagai dependency, bukan di-import langsung di UI.

### Prinsip Service Abstraction
- Setiap service punya interface (kontrak) yang fixed.
- Implementasi bisa berganti (misal: `RESTStorageService` -> `GraphQLStorageService`) tanpa ubah UI.
- AI provider bisa diganti (`Anthropic` -> `OpenAI` -> `Gemini`) hanya dengan swap implementasi `AIService`.
- Testing mudah karena setiap service bisa di-mock secara independen.

### Keputusan Arsitektur: AI Call dari Client, Bukan Backend
AI call (ke Anthropic/OpenAI/Gemini) dilakukan **langsung dari client app**, bukan via backend. Keputusan ini bersifat final untuk v1:
- API key user disimpan di device keychain (`expo-secure-store`) dan digunakan langsung dari client untuk hit AI provider.
- API key **tidak pernah dikirim ke backend** milik kita. Backend hanya menangani data (MySQL), bukan AI proxy.
- Konsekuensi: backend tidak perlu menyimpan atau mengelola AI credentials. Jika user tidak pasang API key, AI features dinonaktifkan (mode terbatas).
- Auth user ke backend menggunakan mekanisme terpisah (JWT / session token), bukan API key AI.

### Daftar Service & Interface
| Service | Interface | Input | Output |
| --- | --- | --- | --- |
| AIService | `analyzeProfile(profile: UserProfile)`, `generateWorkoutPlan(profile: UserProfile, preferences: WorkoutPreferences)`, `generateMealPlan(profile: UserProfile, preferences: FoodPreferences, targetCalories: number)`, `estimateCalories(foodName: string)`, `weeklyReview(logs: WeekLog)`, `reviseWorkoutPlan(plan: WorkoutPlan, feedback: string)`, `swapMealItem(plan: MealPlan, day: number, meal: string, feedback: string)` | Sesuai signature | Structured JSON `{ status, data, error, tokensUsed }` |
| StorageService | `get(key)`, `set(key, value)`, `delete(key)`, `listKeys(prefix)` | Key string + value | Value/null |
| CalorieService | `estimate(foodName)`, `getMacros(food)`, `searchFood(query)` | Food name/query | Kalori + macro breakdown. Secara internal memanggil `AIService.estimateCalories` jika online; fallback ke local database jika offline. `AIService` tidak dipanggil langsung dari UI untuk fitur ini. |
| WorkoutService | `getActivePlan()`, `savePlan(plan)`, `logSession(session)`, `getHistory(range)` | Plan/Session object | Plan atau history array |
| MealService | `getActivePlan()`, `savePlan(plan)`, `logMeal(entry)`, `swapItem(day, meal, newItem)` | Plan/Meal entry | Plan atau log array |
| WeightService | `logWeight(entry)`, `getHistory(range)`, `getLatest()` | `WeightEntry` object | Entry atau history array |
| ScoringService | `calculate(dayLog)`, `getStreak()`, `getWeeklyScore()` | `DayLog` object | Score number (0-100) |
| NotificationService | `schedule(time, msg)`, `cancel(id)`, `requestPermission()` | Time + message | Notification ID / permission status |

### CalorieService — Strategi Fallback
```
CalorieService.estimate(foodName)
  ├── Online?
  │   └── AIService.estimateCalories(foodName) → return result
  └── Offline?
      ├── searchLocalDB(foodName) → jika ada, return result
      └── tidak ada di local DB → prompt user input manual (calories, protein, carbs, fat)
```
Local database minimal: top ~500 makanan umum Indonesia (nasi putih, nasi goreng, ayam goreng, tempe, tahu, dll) disimpan sebagai JSON bundle di app assets.

### AI Provider Abstraction
`AIService` adalah interface. Implementasinya bisa:
- `AnthropicAIService`: pakai claude-sonnet-4 via Anthropic API.
- `OpenAIService`: pakai gpt-4o via OpenAI API.
- `GeminiAIService`: pakai gemini-pro via Google AI.
- `MockAIService`: untuk testing, return data dummy tanpa API call.

Semua implementasi return format yang sama: `{ status, data, error, tokensUsed }`

### API Key Security
API key user digunakan **langsung dari client** untuk memanggil AI provider. Tidak pernah melewati backend kita.
- Disimpan via `expo-secure-store` (iOS Keychain + Android Keystore) — tidak pernah di AsyncStorage atau database.
- Kolom `api_key_ref` di tabel `users` hanya menyimpan referensi string (e.g. `"keychain:fitdiscipline_apikey"`), bukan nilai key-nya.
- Backend auth user menggunakan JWT yang terpisah dari API key AI — keduanya tidak boleh dicampur.

### Rate Limit Handling
- `AIService` punya built-in retry dengan exponential backoff.
- Jika kena limit: queue request, tampilkan estimasi waktu tunggu ke user.
- Partial response disimpan, jika interrupted lanjut dari checkpoint.
- `AIService.getStatus()` return: `ready | rate_limited | waiting | error`.

---

## 5. Sistem Discipline Scoring
Score harian dihitung tiap malam (atau saat user tutup app). Range 0-100.

| Activity | Points | Conditions |
| --- | --- | --- |
| Selesaikan semua sesi workout | +35 pts | Berdasarkan program aktif hari itu. Tidak berlaku pada hari yang ditandai `is_rest_day: true` |
| Partial workout (>50% selesai) | +15 pts | Minimal setengah sesi selesai |
| Kalori dalam target +/-100 kkal | +25 pts | Target dari program aktif |
| Kalori dalam target +/-200 kkal | +12 pts | Toleransi lebih longgar (tidak kumulatif dengan poin di atas) |
| Log makanan lengkap (3x) | +10 pts | Sarapan, makan siang, makan malam semua di-log |
| Tidur >= target jam tidur | +15 pts | Target tidur dari `user_preferences.sleep_target_hours` |
| Tidur 1 jam kurang dari target | +8 pts | Toleransi ringan (tidak kumulatif dengan poin di atas) |
| Log berat badan minggu ini | +5 pts | Minimal sekali per 7 hari (dari tabel `weight_logs`) |
| Streak bonus (7 hari berturut) | +5 pts | Bonus flat per minggu streak aktif |
| Melewatkan workout tanpa alasan | -10 pts | Tidak berlaku jika `is_rest_day: true` di schedule hari itu |
| Kalori melebihi target >300 kkal | -10 pts | Overeating signifikan |

**Catatan:** Total maksimum yang bisa dicapai adalah **95 pts** (35+25+10+15+5+5). Range "0-100" dibulatkan untuk komunikasi ke user; perfect score = 95 pts. Atau dapat ditambahkan 5 pts bonus kategori baru jika ingin score bisa menyentuh 100.

Discipline score mingguan = rata-rata score harian × faktor konsistensi (0.8–1.2).

### Definisi Rest Day
Rest day adalah hari di mana `weeks_data` di `workout_plans` tidak memiliki session apapun untuk hari tersebut, **atau** session memiliki field `is_rest_day: true`. `ScoringService` wajib cek kondisi ini sebelum apply penalti workout.

---

## 6. Data Model
| Entity | Key Fields | Type | Notes |
| --- | --- | --- | --- |
| UserProfile | id, name, age, gender, bodyWeight, height | Object (JSON) | Data statis. Setting seperti sleep target & activity level ada di `UserPreferences` |
| UserPreferences | userId, sleepTargetHours, activityLevel, goalType, goalWeightKg, goalDeadlineDate, lastMonthlyReviewAt | Object (JSON) | Setting user yang bisa berubah. Bukan data statis identity |
| WorkoutPlan | id, createdAt, confirmedAt, weeks[{ day, isRestDay, sessions[] }] | Object (JSON) | Program aktif. `isRestDay` wajib ada di setiap day object |
| WorkoutSession | date, planSessionId, exercises[{ name, sets, reps, weight }], completed, duration | Object (JSON) | Log per sesi |
| MealPlan | id, createdAt, confirmedAt, days[{ breakfast, lunch, dinner, snacks }] | Object (JSON) | Program aktif |
| MealLog | date, meal, foodName, calories, protein, carbs, fat, isManualInput | Object (JSON) | `isManualInput: true` jika user input manual (offline/tidak pakai AI) |
| WeightLog | date, weightKg, notes | Object (JSON) | Log berat badan harian/mingguan. Terpisah dari `fitness_capabilities` |
| DayLog | date, workoutDone, totalCalories, targetCalories, sleepHours, targetSleep, disciplineScore | Object (JSON) | Computed dari WorkoutSession + MealLog. Tidak disimpan terpisah — gunakan `day_scores` sebagai persistent store |
| AIPromptConfig | systemPrompt, userPromptTemplate, temperature, maxTokens, provider, model | Object (JSON) | Per-method config, editable user |

---

## 7. AI Prompt System
Semua prompt disimpan sebagai konfigurasi yang bisa diedit user, bukan hardcode di kode.

### Struktur Prompt Config
- `systemPrompt`: konteks AI (role, rules, format output yang diharapkan).
- `userPromptTemplate`: template dengan placeholder `{{weight}}`, `{{goal}}`, `{{preferences}}`, dll.
- `outputSchema`: JSON schema yang diharapkan (AI harus return JSON sesuai skema ini).
- `fallbackBehavior`: apa yang dilakukan jika AI return format yang salah.

### Method -> Prompt Mapping
- `analyzeProfile`: "Kamu adalah dokter olahraga. Analisa profil berikut dan berikan ringkasan kondisi fisik..."
- `generateWorkoutPlan`: "Buat program workout `{{weeksCount}}` minggu untuk `{{goalType}}`. Format JSON: `{ weeks: [...] }`"
- `generateMealPlan`: "Buat menu makan 7 hari dengan target `{{calories}}` kkal/hari. Preferensi: `{{preferences}}`..."
- `estimateCalories`: "Estimasi kalori dan makro untuk: `{{foodName}}`. Return JSON: `{ calories, protein, carbs, fat }`"
- `weeklyReview`: "Analisa progress minggu ini berdasarkan log berikut. Propose adjustment jika perlu..."

### Konfirmasi Sebelum Apply
Setiap AI response yang mengubah program melewati `ConfirmationFlow`:
- AI propose -> app parse JSON response -> tampilkan diff (sebelum vs sesudah).
- User bisa: Setuju, Edit manual, Minta revisi (dengan catatan), Tolak.
- Jika "Minta revisi": feedback user dimasukkan ke prompt berikutnya sebagai additional context.
- Baru setelah user tap "Setuju" -> program tersimpan via `StorageService`.

---

## 8. Tech Stack Rekomendasi

### Frontend
- React Native (Expo): bisa build iOS + Android dari satu codebase.
- Alternatif: React (web) + PWA, lebih cepat develop dan bisa install di HP.
- Alternatif: Flutter, performa native tetapi beda bahasa (Dart).

### Storage — MySQL
Database utama menggunakan **MySQL**. Schema di Bagian 13 ditulis dalam MySQL DDL syntax.

- **Server:** MySQL 8.0+ — self-hosted atau managed (PlanetScale, AWS RDS, Railway, Supabase MySQL-compatible).
- **Mobile / client:** Tidak connect langsung ke MySQL dari device. Semua akses data lewat **REST API / backend layer** (Express, Fastify, atau framework sejenis) yang berjalan di server.
- **Konsekuensi arsitektur:** App tidak lagi pure local-only untuk data relasional. Backend layer wajib ada sebagai perantara antara app dan MySQL.
- **Offline handling:** Karena data ada di server, fitur offline terbatas pada cache lokal ringan (AsyncStorage/IndexedDB) untuk data yang terakhir di-fetch. Fitur yang butuh write (log makanan, log workout) memerlukan koneksi internet atau implementasi queue + sync.
- Semua akses database tetap dibungkus `StorageService`. UI tidak tahu implementasinya — swap implementasi cukup di layer service.

> **Catatan:** Dengan MySQL sebagai backend, fitur "privacy-first: semua data lokal" di Bagian 1 perlu direvisi. Data user kini tersimpan di server. Pastikan kebijakan privasi dan enkripsi data at-rest dikomunikasikan ke user.

### Secure Storage (untuk API Key)
- `expo-secure-store` (React Native/Expo) — wajib untuk menyimpan API key user.
- Web: Web Crypto API + sessionStorage (key di-derive dari password, tidak persisten).

### AI API (Free Tier Options)
- Anthropic: `claude-haiku-4` paling murah, `claude-sonnet-4` untuk analisa kompleks.
- Google Gemini: `gemini-1.5-flash` gratis dengan rate limit.
- OpenAI: `gpt-4o-mini` relatif murah.
- Groq: `llama3` gratis, sangat cepat, cocok untuk `estimateCalories`.

### Charting
- Victory Native (React Native) atau Recharts (React web).
- Untuk grafik: berat badan trend (dari `weight_logs`), kalori 7/30 hari, discipline score history.

---

## 9. Urutan Implementasi (untuk AI Agent)

### Sprint 1 - Foundation
| Step | Action | Detail |
| --- | --- | --- |
| S1.1 | Setup project & folder structure | Buat struktur: `/screens`, `/services`, `/services/impl`, `/hooks`, `/store`, `/types`, `/assets/data` |
| S1.2 | Definisikan semua TypeScript interfaces | `UserProfile`, `UserPreferences`, `WorkoutPlan`, `MealPlan`, `WeightLog`, `DayLog`, `AIServiceInterface`, `StorageServiceInterface` |
| S1.3 | Setup MySQL schema & backend layer | Buat migration file untuk semua tabel di Bagian 13 (MySQL DDL). Setup backend API (Express/Fastify). Test CRUD endpoint untuk setiap tabel |
| S1.4 | Implement `StorageService` | HTTP client wrapper yang hit backend API. Test `get/set/delete/list` via REST endpoint |
| S1.5 | Implement `WorkoutService` & `MealService` | `getActivePlan`, `savePlan`, `logSession`, `logMeal` — dibutuhkan Sprint 3 |
| S1.6 | Implement `WeightService` | `logWeight`, `getHistory`, `getLatest` |
| S1.7 | Implement `ScoringService` | Logic scoring dari Bagian 5 termasuk logika rest day. Unit test dengan berbagai skenario |
| S1.8 | Bundle local calorie database | Buat JSON asset ~500 makanan umum Indonesia untuk offline fallback |
| S1.9 | Onboarding screens | Form 7 langkah (termasuk notif permission + API key setup), validasi, simpan ke `StorageService` |

### Sprint 2 - AI Integration
| Step | Action | Detail |
| --- | --- | --- |
| S2.1 | Implement `AIServiceInterface` | Buat abstract class/interface dengan semua method signature |
| S2.2 | Implement `AnthropicAIService` | Wrap Anthropic API. Handle auth, rate limit, retry, parse JSON response |
| S2.3 | Implement `MockAIService` | Return dummy data untuk development tanpa buang token API |
| S2.4 | Implement `CalorieService` | Facade dengan online (AIService) + offline (local DB + manual) fallback strategy |
| S2.5 | Prompt config system | Load prompt dari config file, support template placeholder |
| S2.6 | Confirmation flow UI | Komponen reusable: tampilkan proposal AI, tombol Setuju/Edit/Revisi |
| S2.7 | AI Setup screen (Fase 2) | Onboarding AI: analisa profil -> propose program -> user confirm |

### Sprint 3 - Daily Tracking
| Step | Action | Detail |
| --- | --- | --- |
| S3.1 | Dashboard screen | Score ring, task hari ini, kalori ring, streak |
| S3.2 | Log makanan + `CalorieService` | Search field, estimasi kalori, running total, fallback manual input |
| S3.3 | Log workout screen | Checklist dari program aktif (dengan indikator rest day), input sets/reps |
| S3.4 | Log tidur | Simple input, masuk ke `DayLog` |
| S3.5 | Log berat badan | Input berat via `WeightService.logWeight` |
| S3.6 | Daily score calculation | `ScoringService.calculate(dayLog)` dipanggil otomatis |

### Sprint 4 - Review & Polish
| Step | Action | Detail |
| --- | --- | --- |
| S4.1 | Weekly review flow | Trigger (7 hari dari `confirmed_at`), AI analisa, proposal adjustment, konfirmasi |
| S4.2 | Monthly review flow | On-open trigger check, AI analisa, propose level change, konfirmasi |
| S4.3 | Progress & stats screen | Grafik berat badan (`weight_logs`), kalori, discipline score |
| S4.4 | Program & menu editor | Tampilkan program aktif, edit manual, minta AI revisi |
| S4.5 | Settings screen | API key (via secure keychain), pilih provider, test koneksi, export JSON, reset data |
| S4.6 | Rate limit UX | Tampilkan status AI, estimasi waktu tunggu, queue antrian |

---

## 10. Catatan Penting untuk AI Agent

### Yang wajib diikuti
- Jangan hardcode logika AI di screen/component, selalu lewat `AIService`.
- Jangan hardcode storage key di screen, selalu lewat `StorageService` dengan konstanta.
- Setiap method `AIService` harus return `{ status, data, error }`, jangan throw exception langsung ke UI.
- Prompt template harus bisa diedit tanpa rebuild app, simpan di storage, bukan di kode.
- AI tidak pernah auto-apply perubahan program, selalu lewat `ConfirmationFlow`.
- API key **selalu** lewat `expo-secure-store`, tidak pernah AsyncStorage atau SQLite.
- `CalorieService` adalah satu-satunya pintu masuk estimasi kalori dari UI — tidak boleh panggil `AIService.estimateCalories` langsung dari screen.

### Edge cases yang harus dihandle
- User tidak pasang API key: tampilkan mode terbatas, fitur non-AI tetap berjalan.
- User offline saat log makanan: `CalorieService` auto-fallback ke local DB, lalu ke manual input. Tampilkan indikator "estimasi offline".
- AI return JSON malformed: parse dengan try/catch, tampilkan error jelas, retry otomatis.
- Rate limit kena: queue request, estimasi waktu, notif ke user.
- User edit manual program hasil AI: tandai sebagai "manually edited", weekly review tetap jalan.
- Rest day: `ScoringService` tidak apply penalti workout jika `is_rest_day: true`.
- Monthly review: jalankan hanya via on-open check, bukan background cron. Cek `last_monthly_review_at` di `user_preferences`.
- Notification permission ditolak: semua fitur tetap berjalan, hanya reminder notif yang dinonaktifkan. Jangan block onboarding.

### Yang boleh dikembangkan nanti (out of scope v1)
- Sync ke cloud/multi-device.
- Foto makanan -> estimasi kalori (butuh vision model).
- Integrasi wearable (Apple Watch, Fitbit).
- Social features/sharing progress.

---

## 11. AI Restrictions & User Preference Context
AI harus selalu memuat preference context sebelum generate apa pun. Tidak boleh propose makanan atau latihan yang bertentangan dengan restriction user.

Food preferences (per user, persisten) disimpan di tabel terpisah `food_preferences`. AI wajib load ini sebagai system context sebelum `generateMealPlan` atau `estimateCalories`.

| Field | Type | Contoh Nilai | Keterangan |
| --- | --- | --- | --- |
| preference_id | UUID | uuid-xxx | Primary key |
| user_id | FK -> users | uuid-yyy | Relasi ke tabel user |
| category | ENUM | liked/disliked/allergy/intolerance/religious | Tipe restriction. `allergy` = hard block, lainnya soft restriction |
| food_name | VARCHAR(100) | tempe, udang | Nama makanan spesifik |
| food_group | VARCHAR(100) | seafood, dairy | Opsional. Jika diisi, restriction berlaku untuk seluruh grup |
| severity | ENUM | hard/soft | `hard` = AI tidak boleh propose sama sekali, `soft` = boleh dengan catatan/alternatif |
| note | TEXT | alergi kulit parah | Catatan user, dimasukkan ke AI context sebagai kalimat natural |
| created_at | TIMESTAMP | 2025-01-15 08:00 | Kapan preference ini ditambahkan |
| deleted_at | TIMESTAMP | NULL | Soft-delete. Tidak pernah hard-delete agar history terjaga |

### Bagaimana AI menggunakan Food Preferences
- Sebelum `generateMealPlan`: load semua `food_preferences` user (where `deleted_at IS NULL`) lalu inject ke system prompt sebagai blok `RESTRICTIONS`.
- Hard restrictions: "NEVER include these foods or food groups: ..."
- Soft restrictions: "Avoid if possible, if included add alternatives: ..."
- Liked foods: "Prioritize these when nutritionally appropriate: ..."
- `estimateCalories` / `CalorieService.estimate`: jika makanan yang di-log masuk daftar hard allergy, tampilkan warning ke user.

---

## 12. Fitness Leveling System & Capabilities

### Konsep
Setiap user punya `fitness_level` yang menentukan seberapa berat program yang AI boleh generate. Level naik/turun berdasarkan evaluasi bulanan yang di-trigger saat app dibuka (bukan cron server). AI tidak boleh assign latihan di luar capability range level saat ini tanpa konfirmasi eksplisit user.

### Fitness Level Enum
| Level | Label | Kriteria Umum | Contoh Kemampuan |
| --- | --- | --- | --- |
| 1 | Absolute Beginner | Baru mulai, belum rutin olahraga | Jalan kaki 20 menit, push-up lutut, squat tanpa beban |
| 2 | Beginner | Rutin 1-2x/minggu, form masih belajar | Push-up 10 reps, bodyweight squat 15 reps, plank 30 detik |
| 3 | Intermediate | Rutin 3x/minggu, form sudah bagus | Push-up 25 reps, dumbbell curl, lari 5 km non-stop |
| 4 | Advanced | Rutin 4-5x/minggu, latihan terstruktur | Pull-up 10 reps, bench press BW, lari 10 km < 60 menit |
| 5 | Athletic | Kompetitif/atlet, program periodisasi | Deadlift 1.5x BW, strict muscle-up, lari half-marathon |

Tabel `fitness_capabilities` bersifat append-only per user dan punya log historis.

| Field | Type | Contoh | Keterangan |
| --- | --- | --- | --- |
| capability_id | UUID | uuid-xxx | Primary key |
| user_id | FK -> users | uuid-yyy | Relasi ke tabel users |
| recorded_at | TIMESTAMP | 2025-01-01 | Kapan snapshot ini dibuat |
| source | ENUM | onboarding/monthly_review/manual | `monthly_cron` diganti `monthly_review` (on-open check) |
| fitness_level | INT (1-5) | 2 | Level saat ini |
| body_weight_kg | DECIMAL(5,2) | 72.50 | Berat badan saat snapshot |
| body_fat_pct | DECIMAL(4,1) | 18.5 | Opsional |
| resting_hr_bpm | INT | 68 | Opsional |
| vo2max_estimate | DECIMAL(4,1) | 42.5 | Opsional |
| pushup_max_reps | INT | 20 | Test capability |
| pullup_max_reps | INT | 5 | Test capability |
| squat_1rm_kg | DECIMAL(5,2) | 60.00 | Opsional |
| deadlift_1rm_kg | DECIMAL(5,2) | 80.00 | Opsional |
| run_5k_minutes | DECIMAL(5,1) | 32.0 | NULL jika belum pernah tes |
| weekly_active_days | INT | 3 | Rata-rata hari aktif |
| avg_session_min | INT | 45 | Rata-rata durasi sesi |
| monthly_task_done | INT | 18 | Jumlah task workout selesai bulan ini |
| monthly_task_total | INT | 24 | Total task workout bulan ini |
| completion_rate_pct | DECIMAL(4,1) | 75.0 | `monthly_task_done / monthly_task_total x 100` |
| ai_notes | TEXT | User lapor lutut sakit | Catatan AI untuk review berikutnya |

### Monthly Review - Logic Level Naik / Turun
Review di-trigger saat app dibuka, cek apakah `last_monthly_review_at` >= 28 hari yang lalu. AI yang decide, tetapi user harus konfirmasi sebelum level berubah.

| Kondisi | Keputusan AI | Catatan |
| --- | --- | --- |
| completion_rate >= 85% selama 2 bulan berturut | Propose LEVEL UP (+1) | AI cek capability test mendukung |
| completion_rate 60-84% | Pertahankan level | Intensitas bisa disesuaikan dalam level yang sama |
| completion_rate 40-59% | AI review alasan | AI tanya cedera/faktor eksternal sebelum putuskan level turun |
| completion_rate < 40% selama 2 bulan berturut | Propose LEVEL DOWN (-1) | Wajib ada penjelasan + konfirmasi user, level minimum 1 |
| Ada laporan cedera/sakit di ai_notes | Hold | Tidak propose perubahan level jika injury flag aktif |

### AI Restriction dari Fitness Level
- `generateWorkoutPlan` hanya boleh propose exercise di library capability level saat ini dan satu level di atas (stretch goal).
- Jika user minta exercise di luar range: AI jelaskan kenapa belum waktunya, lalu tawarkan progression path.
- Level bisa naik manual jika user bisa buktikan capability (upload test result atau konfirmasi manual).
- `ai_notes` dari bulan lalu selalu dimasukkan ke context bulan berikutnya.

---

## 13. Database Schema Lengkap

Storage: **MySQL 8.0+** diakses via backend REST API. App tidak connect langsung ke MySQL dari device.

**Konvensi UUID:** Semua primary key bertipe `CHAR(36)` dengan default `(UUID())` — human-readable, mudah di-debug. Untuk volume tinggi di masa depan bisa dimigrasikan ke `BINARY(16)` dengan fungsi konversi. Semua tabel menggunakan `ENGINE=InnoDB` dan `DEFAULT CHARSET=utf8mb4`.

```sql
-- ============================================================
-- TABEL: users
-- ============================================================
CREATE TABLE users (
  user_id         CHAR(36)     NOT NULL DEFAULT (UUID()),
  name            VARCHAR(100) NOT NULL,
  email           VARCHAR(255) NULL,
  gender          ENUM('male','female','other') NOT NULL,
  birth_date      DATE         NOT NULL,
  height_cm       DECIMAL(4,1) NOT NULL,
  ai_provider     VARCHAR(50)  NOT NULL DEFAULT 'anthropic',
  api_key_ref     TEXT         NULL COMMENT 'Keychain reference string only — never the key value itself',
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  onboarding_done BOOLEAN      NOT NULL DEFAULT FALSE,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: user_preferences
-- Satu row per user (UNIQUE user_id). Gunakan UPSERT, bukan INSERT.
-- ============================================================
CREATE TABLE user_preferences (
  pref_id                CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id                CHAR(36)     NOT NULL,
  sleep_target_hours     DECIMAL(3,1) NOT NULL DEFAULT 8.0,
  activity_level         ENUM('sedentary','light','moderate','active') NOT NULL,
  goal_type              ENUM('cut','bulk','maintain') NOT NULL,
  goal_weight_kg         DECIMAL(5,2) NOT NULL,
  goal_deadline_date     DATE         NULL,
  last_monthly_review_at TIMESTAMP    NULL,
  updated_at             TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (pref_id),
  UNIQUE KEY uq_user_preferences_user (user_id),
  CONSTRAINT fk_prefs_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: weight_logs
-- Log berat badan harian/mingguan. Beda dari fitness_capabilities (monthly snapshot).
-- ============================================================
CREATE TABLE weight_logs (
  log_id     CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id    CHAR(36)     NOT NULL,
  log_date   DATE         NOT NULL,
  weight_kg  DECIMAL(5,2) NOT NULL,
  notes      TEXT         NULL,
  created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_weight_logs_user_date (user_id, log_date),
  CONSTRAINT fk_wl_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: fitness_capabilities
-- APPEND-ONLY. Tidak pernah UPDATE. Selalu INSERT row baru.
-- Current = row dengan MAX(recorded_at) per user_id.
-- ============================================================
CREATE TABLE fitness_capabilities (
  capability_id       CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id             CHAR(36)     NOT NULL,
  recorded_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  source              ENUM('onboarding','monthly_review','manual') NOT NULL,
  fitness_level       TINYINT      NOT NULL,
  body_weight_kg      DECIMAL(5,2) NOT NULL,
  body_fat_pct        DECIMAL(4,1) NULL,
  resting_hr_bpm      SMALLINT     NULL,
  vo2max_estimate     DECIMAL(4,1) NULL,
  pushup_max_reps     SMALLINT     NULL,
  pullup_max_reps     SMALLINT     NULL,
  squat_1rm_kg        DECIMAL(5,2) NULL,
  deadlift_1rm_kg     DECIMAL(5,2) NULL,
  run_5k_minutes      DECIMAL(5,1) NULL,
  weekly_active_days  TINYINT      NULL,
  avg_session_min     SMALLINT     NULL,
  monthly_task_done   SMALLINT     NULL,
  monthly_task_total  SMALLINT     NULL,
  completion_rate_pct DECIMAL(4,1) NULL,
  ai_notes            TEXT         NULL,
  PRIMARY KEY (capability_id),
  KEY idx_fc_user_recorded (user_id, recorded_at),
  CONSTRAINT chk_fc_level CHECK (fitness_level BETWEEN 1 AND 5),
  CONSTRAINT fk_fc_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: food_preferences
-- Soft-delete via deleted_at. Tidak pernah hard-delete.
-- ============================================================
CREATE TABLE food_preferences (
  preference_id CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id       CHAR(36)     NOT NULL,
  category      ENUM('liked','disliked','allergy','intolerance','religious') NOT NULL,
  food_name     VARCHAR(100) NULL,
  food_group    VARCHAR(100) NULL,
  severity      ENUM('hard','soft') NOT NULL DEFAULT 'soft',
  note          TEXT         NULL,
  created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at    TIMESTAMP    NULL,
  PRIMARY KEY (preference_id),
  KEY idx_fp_user_active (user_id, deleted_at),
  CONSTRAINT fk_fp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: workout_plans
-- Hanya 1 row status='active' per user. Saat plan baru dikonfirmasi,
-- set archived_at pada plan lama terlebih dahulu.
-- ============================================================
CREATE TABLE workout_plans (
  plan_id          CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id          CHAR(36)     NOT NULL,
  fitness_level_at TINYINT      NOT NULL,
  status           ENUM('active','archived','draft') NOT NULL DEFAULT 'draft',
  goal_type        ENUM('cut','bulk','maintain') NOT NULL,
  target_weight_kg DECIMAL(5,2) NOT NULL,
  weeks_data       JSON         NOT NULL COMMENT 'Structure: { weeks: [{ day, isRestDay, sessions: [...] }] }',
  ai_generated     BOOLEAN      NOT NULL DEFAULT FALSE,
  confirmed_at     TIMESTAMP    NULL COMMENT 'Weekly review trigger dihitung dari kolom ini',
  created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  archived_at      TIMESTAMP    NULL,
  PRIMARY KEY (plan_id),
  KEY idx_wp_user_status (user_id, status),
  CONSTRAINT fk_wp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: workout_sessions
-- ============================================================
CREATE TABLE workout_sessions (
  session_id     CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id        CHAR(36)     NOT NULL,
  plan_id        CHAR(36)     NULL COMMENT 'NULL jika sesi bebas (tidak dari plan aktif)',
  session_date   DATE         NOT NULL,
  completed      BOOLEAN      NOT NULL DEFAULT FALSE,
  completion_pct DECIMAL(4,1) NOT NULL DEFAULT 0.0,
  duration_min   SMALLINT     NULL,
  exercises_log  JSON         NOT NULL COMMENT 'Array: [{name, sets, reps, weight_kg, notes}]',
  user_notes     TEXT         NULL,
  created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (session_id),
  KEY idx_ws_user_date (user_id, session_date),
  CONSTRAINT fk_ws_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_ws_plan
    FOREIGN KEY (plan_id) REFERENCES workout_plans(plan_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: meal_plans
-- Hanya 1 row status='active' per user.
-- ============================================================
CREATE TABLE meal_plans (
  plan_id             CHAR(36)  NOT NULL DEFAULT (UUID()),
  user_id             CHAR(36)  NOT NULL,
  status              ENUM('active','archived','draft') NOT NULL DEFAULT 'draft',
  target_calories     SMALLINT  NOT NULL,
  target_protein_g    SMALLINT  NOT NULL,
  target_carbs_g      SMALLINT  NOT NULL,
  target_fat_g        SMALLINT  NOT NULL,
  days_data           JSON      NOT NULL COMMENT 'Structure: { days: [...] }',
  preference_snapshot JSON      NULL COMMENT 'Snapshot food_preferences saat plan dibuat',
  ai_generated        BOOLEAN   NOT NULL DEFAULT FALSE,
  confirmed_at        TIMESTAMP NULL,
  created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (plan_id),
  KEY idx_mp_user_status (user_id, status),
  CONSTRAINT fk_mp_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: meal_logs
-- ============================================================
CREATE TABLE meal_logs (
  log_id          CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id         CHAR(36)     NOT NULL,
  log_date        DATE         NOT NULL,
  meal_type       ENUM('breakfast','lunch','dinner','snack') NOT NULL,
  food_name       VARCHAR(200) NOT NULL,
  portion_desc    VARCHAR(100) NULL,
  calories        SMALLINT     NOT NULL,
  protein_g       DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  carbs_g         DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  fat_g           DECIMAL(5,1) NOT NULL DEFAULT 0.0,
  ai_estimated    BOOLEAN      NOT NULL DEFAULT FALSE,
  is_manual_input BOOLEAN      NOT NULL DEFAULT FALSE,
  allergy_flag    BOOLEAN      NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_ml_user_date (user_id, log_date),
  CONSTRAINT fk_ml_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: day_scores
-- UNIQUE (user_id, score_date). Recalculate jika user edit log hari yang sama.
-- ============================================================
CREATE TABLE day_scores (
  score_id           CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id            CHAR(36)     NOT NULL,
  score_date         DATE         NOT NULL,
  total_score        TINYINT      NOT NULL,
  workout_pts        TINYINT      NOT NULL DEFAULT 0,
  nutrition_pts      TINYINT      NOT NULL DEFAULT 0,
  sleep_pts          TINYINT      NOT NULL DEFAULT 0,
  logging_pts        TINYINT      NOT NULL DEFAULT 0,
  bonus_pts          TINYINT      NOT NULL DEFAULT 0,
  penalty_pts        TINYINT      NOT NULL DEFAULT 0 COMMENT 'Nilai negatif, e.g. -10',
  workout_done       BOOLEAN      NOT NULL DEFAULT FALSE,
  is_rest_day        BOOLEAN      NOT NULL DEFAULT FALSE COMMENT 'Diisi dari workout_plans.weeks_data, bukan input user',
  calories_actual    SMALLINT     NOT NULL DEFAULT 0,
  calories_target    SMALLINT     NOT NULL DEFAULT 0,
  sleep_hours_actual DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  sleep_hours_target DECIMAL(3,1) NOT NULL DEFAULT 0.0 COMMENT 'Snapshot dari user_preferences.sleep_target_hours',
  calculated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (score_id),
  UNIQUE KEY uq_day_scores_user_date (user_id, score_date),
  CONSTRAINT fk_ds_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABEL: ai_prompt_configs
-- user_id NULL = global default. Load order: user config -> global default.
-- ============================================================
CREATE TABLE ai_prompt_configs (
  config_id     CHAR(36)     NOT NULL DEFAULT (UUID()),
  user_id       CHAR(36)     NULL COMMENT 'NULL = global default config',
  method_name   VARCHAR(100) NOT NULL,
  system_prompt TEXT         NOT NULL,
  user_template TEXT         NOT NULL,
  output_schema JSON         NULL,
  temperature   DECIMAL(3,2) NOT NULL DEFAULT 0.70,
  max_tokens    SMALLINT     NOT NULL DEFAULT 2000,
  is_default    BOOLEAN      NOT NULL DEFAULT FALSE,
  updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id),
  KEY idx_apc_user_method (user_id, method_name),
  CONSTRAINT fk_apc_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Relasi Antar Tabel
- `users (1) -> (1) user_preferences` (UNIQUE user_id)
- `users (1) -> (N) weight_logs` (log berat badan harian/mingguan)
- `users (1) -> (N) fitness_capabilities` (append-only; current = MAX(recorded_at))
- `users (1) -> (N) food_preferences` (soft-delete via `deleted_at`)
- `users (1) -> (N) workout_plans` (hanya 1 active, sisanya archived)
- `users (1) -> (N) meal_plans` (hanya 1 active, sisanya archived)
- `users (1) -> (N) workout_sessions` (FK ke `plan_id` nullable → SET NULL jika plan dihapus)
- `users (1) -> (N) meal_logs`
- `users (1) -> (N) day_scores` (UNIQUE per user per tanggal)
- `users (1) -> (N) ai_prompt_configs` (`user_id` NULL = global default)

### Catatan Penting untuk Implementasi
- `fitness_capabilities` append-only: tidak pernah UPDATE, selalu INSERT row baru.
- `workout_plans` dan `meal_plans`: set `archived_at` plan lama sebelum INSERT plan baru yang active.
- `food_preferences`: soft-delete (`deleted_at`), query aktif selalu tambahkan `WHERE deleted_at IS NULL`.
- `day_scores`: recalculate (bukan append baru) jika user edit log di hari yang sama — manfaatkan `UNIQUE(user_id, score_date)` dengan `INSERT ... ON DUPLICATE KEY UPDATE`.
- `user_preferences`: satu row per user — gunakan `INSERT ... ON DUPLICATE KEY UPDATE`, bukan plain INSERT.
- `ai_prompt_configs`: load dengan `ORDER BY (user_id IS NULL) ASC` agar user config prioritas di atas global default.

---

## 14. Changelog

### v1.2 — Storage migration ke MySQL
| # | Issue | Perubahan |
| --- | --- | --- |
| V2.1 | SQLite diganti MySQL | Bagian 8 storage section ditulis ulang. MySQL 8.0+ sebagai database utama via backend layer |
| V2.2 | Arsitektur berubah jadi client-server | App tidak lagi connect langsung ke database. Wajib ada backend layer (REST API). Bagian 8 mencantumkan opsi hosting (PlanetScale, RDS, Railway) |
| V2.3 | JSONB diganti JSON | Semua kolom bertipe `JSONB` di schema Bagian 13 diubah ke `JSON` (MySQL syntax) |
| V2.4 | StorageService implementation berubah | Sprint 1 S1.3–S1.4 diupdate: setup MySQL + backend API, StorageService jadi HTTP client wrapper |
| V2.5 | Privacy-first note | Ditambahkan catatan di Bagian 8: dengan MySQL server, data tidak lagi pure lokal — perlu komunikasi kebijakan privasi ke user |
| V2.6 | Offline handling diclarify | Bagian 8 mencantumkan konsekuensi offline: cache lokal untuk read, queue+sync untuk write |

### v1.1 — Audit fixes
#### Critical fixes
| # | Issue | Perubahan |
| --- | --- | --- |
| C1 | Tech stack vs schema tidak cocok | Bagian 8 diupdate: SQLite sebagai rekomendasi utama. AsyncStorage/IndexedDB tidak direkomendasikan untuk schema relasional |
| C2 | weight_logs tidak ada | Tabel `weight_logs` ditambahkan ke Bagian 13. `WeightService` ditambahkan ke Bagian 4 dan Sprint 1 |
| C3 | sleep_target tidak punya kolom | Tabel `user_preferences` dibuat baru, menampung `sleep_target_hours`, `activity_level`, `goal_deadline_date`, `last_monthly_review_at` |
| C4 | activity_level tidak ada di schema | Dipindahkan ke `user_preferences`. Dihapus dari `users` (bukan data statis) |
| C5 | Monthly cron tidak bisa di mobile | Seluruh framing "cron" diganti "on-open check". Logika trigger didokumentasikan via `last_monthly_review_at`. Fase 5 ditambahkan ke App Flow |

#### Warning fixes
| # | Issue | Perubahan |
| --- | --- | --- |
| W1 | Score max 95 bukan 100 | Catatan eksplisit ditambahkan di Bagian 5: "maksimum aktual 95 pts" |
| W2 | Rest day tidak terdefinisi | `isRestDay` field ditambahkan ke `weeks_data` schema. Definisi rest day ditambahkan di Bagian 5. `is_rest_day` ditambahkan ke `day_scores` |
| W3 | CalorieService vs AIService overlap | `CalorieService` dijadikan facade dengan strategi fallback eksplisit. Bagian 4 diupdate dengan diagram alur online/offline |
| W4 | food_preferences tidak ada deleted_at | Field `deleted_at` ditambahkan ke tabel di Bagian 11 |
| W5 | Food log offline tidak ada fallback | Fallback strategy didokumentasikan di Bagian 4 (CalorieService) dan Bagian 3 (Log Makanan screen). Local calorie database bundle ditambahkan ke Sprint 1 |
| W6 | Weekly review trigger ambigu | Diklarifikasi: "7 hari kalender dari `confirmed_at` workout plan, rolling window" |
| W7 | MealService & WorkoutService tidak ada di sprint | Kedua service dipindahkan ke Sprint 1 (S1.5) |

#### Security fix
| # | Issue | Perubahan |
| --- | --- | --- |
| S1 | Enkripsi API key tidak aman | Bagian 8 ditambahkan seksi "Secure Storage". `api_key_enc` di tabel `users` diganti `api_key_ref` (referensi ke keychain). Bagian 10 ditambahkan rule wajib `expo-secure-store` |

#### Minor fixes
| # | Issue | Perubahan |
| --- | --- | --- |
| M1 | DayLog vs day_scores tidak direkonsiliasi | Bagian 6 diklarifikasi: DayLog adalah computed type in-memory, `day_scores` adalah persistent store |
| M2 | Tidak ada data export | Settings screen diupdate dengan fitur "export data (JSON)" |
| M3 | Notifikasi permission tidak dibahas | Step 1.6 ditambahkan ke Fase 1 onboarding |
| M4 | goal_deadline tidak ada di schema | Field `goal_deadline_date` ditambahkan ke `user_preferences` |
