# Kullanım Kılavuzu

## Temel kullanım

```bash
python3 urlcikar.py
```

İlk çalıştırmada `~/Desktop/urlcikar_config.json` oluşturulur. Config'i düzenledikten sonra tekrar çalıştırın.

## Config

| Anahtar | Varsayılan | Açıklama |
|---|---:|---|
| `dizin` | — | Taranacak kök dizin |
| `cikti` | — | Ham URL çıktısı |
| `durum_dosyasi` | — | Resume/checkpoint dosyası |
| `log_dosyasi` | — | Log dosyası |
| `ilerleme` | `true` | İlerleme göstergesi |
| `ilerleme_araligi` | `200` | Ekran güncelleme aralığı |
| `checkpoint_araligi` | `500` | State kaydetme aralığı |
| `uzantilar` | `[]` | Boşsa tüm uzantılar |
| `haric_dizinler` | `.git,...` | Atlanacak dizin adları |
| `maks_dosya_boyutu` | 500 MiB | Dosya üst limiti |
| `symlink_takip` | `false` | Symlink dizinlerini takip et |
| `binary_kontrol_byte` | `4096` | NUL-byte örnek boyutu |
| `maks_satir_uzunlugu` | 10 MiB | Patolojik satırları sınırla |
| `maks_url_uzunlugu` | 2048 | URL üst uzunluğu |
| `izinli_schemeler` | http/https | İzin verilen URL şemaları |
| `domain_blacklist` | `[]` | Domain veya alt domainleri engeller |
| `domain_whitelist` | `[]` | Sadece belirtilen domain ağacına izin verir |
| `ip_atla` | `false` | IP hostname'lerini atla |
| `localhost_atla` | `false` | localhost alanlarını atla |
| `query_temizle` | `false` | Query'yi kaldır |
| `fragment_temizle` | `false` | Fragment'i kaldır |
| `percent_decode` | `false` | Path/query percent decode |
| `dry_run` | `false` | Sadece uygun dosya say |
| `sessiz` | `false` | Terminal çıktısını azalt |
| `min_disk_alan` | 500 MiB | Başlangıç minimum boş alan |
| `cikti_rotate_boyut` | `0` | Gelecek sürümler için reserved |

## Domain filtreleme

Filtreler hostname sınırlarını gözetir:

```json
{
  "domain_whitelist": ["github.com"]
}
```

Bu, `github.com` ve `sub.github.com` ile eşleşir; `notgithub.com` ile eşleşmez.

## Büyük dosyalar

Tek bir dosyanın tamamı RAM'e alınmaz. Dosyalar streaming olarak okunur. Uzun satırlar da `maks_satir_uzunlugu` ile sınırlandırılır.

## Resume

Checkpoint'ler atomik olarak yazılır:

```bash
python3 urlcikar.py
# işlem kesilebilir
python3 urlcikar.py
```

Resume state; config fingerprint, kök dizin, çıktı ve son işlenen path ile ilişkilendirilir. Config veya çıktı değişirse eski state otomatik olarak geçersiz kabul edilir.

## Tekilleştirme

```bash
sort -u urls_raw.txt > urls.txt
```

Büyük veri:

```bash
sort -S 2G --parallel=4 -u urls_raw.txt > urls.txt
```

Geçici dizin:

```bash
TMPDIR=/mnt/1tb/tmp sort -S 2G -u urls_raw.txt > urls.txt
```

## Dry-run

```json
{
  "dizin": "/backup",
  "cikti": "/data/urls.raw",
  "dry_run": true
}
```

Çıktı üretmeden kaç dosyanın uygun olduğunu kontrol eder.

## Cron

```cron
0 3 * * * cd /opt/urlcikar && /usr/bin/python3 urlcikar.py >> /var/log/urlcikar-cron.log 2>&1
```

Cron için config'in mutlak yollar kullanması önerilir.

## Veri güvenliği

Araç taranan dosyaları değiştirmez. Çıktı, state ve log dosyalarının tarama kökü altında olmasına izin verilmez.

`percent_decode`, query temizleme ve fragment temizleme bilgi kaybı yaratabilir; bunları yalnızca bunun istendiği analizlerde kullanın.
