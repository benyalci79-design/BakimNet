# BakımNet

BakımNet, ekipmanların, iş emirlerinin, teknisyen atamalarının ve sorun bildirimlerinin takip edildiği bakım yönetim uygulamasıdır.

## Kullanılan teknolojiler

- FastAPI
- SQLAlchemy 2
- MariaDB / PyMySQL
- Alembic
- JWT ve Argon2 parola hashleme
- HTML, CSS ve JavaScript frontend
- Pytest

## Kurulum

Projeyi klonladıktan sonra sanal ortam oluşturun:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Bağımlılıkları yükleyin:

```powershell
python -m pip install fastapi uvicorn sqlalchemy pymysql alembic python-dotenv python-jose pwdlib[argon2] pytest httpx tzdata
```

## Ortam değişkenleri

Proje kökünde `.env` dosyası oluşturun:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=bakimnet
DB_USER=root
DB_PASSWORD=your_password
JWT_SECRET_KEY=change_this_secret
```

Gerçek parola ve secret değerlerini Git'e göndermeyin. Başlangıç şablonu için
`.env.example` dosyasını kopyalayıp `.env` olarak kullanabilirsiniz.

## Veritabanı ve migration

MariaDB'de `bakimnet` veritabanını oluşturduktan sonra:

```powershell
python -m alembic upgrade head
```

## Uygulamayı çalıştırma

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

- API: http://127.0.0.1:8001
- Swagger: http://127.0.0.1:8001/docs
- Sağlık kontrolü: http://127.0.0.1:8001/health

Frontend dosyaları `frontend/` klasöründedir. Frontend'i ayrı bir statik sunucuyla açın; API adresi `http://127.0.0.1:8001` olarak kullanılmalıdır.

## Docker ile çalıştırma

Docker Desktop açıkken proje kökünde çalıştırın:

```powershell
docker compose up --build -d
```

Frontend `http://127.0.0.1:5501`, API `http://127.0.0.1:8001`, Swagger ise
`http://127.0.0.1:8001/docs` adresinden açılır. Container'ları durdurmak için:

```powershell
docker compose down
```

MariaDB verileri `mariadb_data` Docker volume'unda saklanır.

## Veritabanı yedekleme

Çalışan Docker veritabanının SQL yedeğini almak için:

```powershell
.\scripts\backup-db.ps1
```

Belirli bir yedeği geri yüklemek için:

```powershell
.\scripts\restore-db.ps1 -BackupFile .\backups\bakimnet-YYYYMMDD-HHMMSS.sql
```

Sunum akışı için `docs/sunum-checklist.md` dosyasındaki kontrol listesini kullanın.
Tablo ilişkileri `docs/veritabani-iliski-diyagrami.md` dosyasında yer alır.

## Kullanıcı rolleri

- **Yönetici:** ekipman, iş emri, teknisyen ve sorun bildirimlerini yönetir.
- **Personel:** sorun bildirimi oluşturur.
- **Teknisyen:** kendisine atanan işleri görür, başlatır ve tamamlar.

## Testler

```powershell
python -m pytest
```

## Örnek veriler

Migration sonrasında örnek kullanıcı, ekipman ve parça eklemek için:

```powershell
python .\seed.py
```

Örnek kullanıcılar: `admin / Admin123!`, `personel / Personel123!`,
`teknisyen / Teknisyen123!`. Gerçek ortamda bu parolaları değiştirin.

Testler tamamlandığında tüm testlerin geçtiği ve yalnızca bilinen uyarıların bulunduğu çıktı kontrol edilmelidir.

## Önemli endpoint grupları

- `/equipment`
- `/work-orders`
- `/technicians`
- `/problem-reports`
- `/users`
- `/login`
- `/me`
- `/admin/dashboard`
- `/my-work-orders`
- `/spare-parts`
- `/work-orders/{id}/parts`
- `/work-orders/{id}/history`
- `/problem-reports/{id}/photo`
- `/notifications`

