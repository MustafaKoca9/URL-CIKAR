# urlcikar

Büyük dizin ve disk yedeklerinde HTTP/HTTPS URL'lerini **streaming** olarak çıkaran, Python standart kütüphanesiyle çalışan tek dosyalık araç.

> Tasarım hedefi: milyonlarca dosya ve URL tararken URL'leri RAM'de `set()` içinde biriktirmemek. Ham sonuç diske yazılır; tekilleştirme gerektiğinde harici `sort -u` kullanılır.

## Özellikler

- Python standart kütüphanesi — harici paket yok
- Streaming dosya okuma ve streaming çıktı
- Deterministik filesystem traversal
- Resume/checkpoint desteği
- Atomik checkpoint yazımı
- Ctrl+C / SIGTERM ile temiz çıkış
- Binary dosya için hızlı NUL-byte heuristiği
- Dosya boyutu ve uzantı filtreleri
- Hariç dizinler ve symlink kontrolü
- URL parser tabanlı doğrulama
- Domain allowlist/denylist
- localhost/IP filtreleri
- İsteğe bağlı query/fragment/percent normalizasyonu
- Dry-run
- Gömülü testler
- Sıfır bağımlılık

## Kurulum

```bash
git clone https://github.com/KULLANICI/urlcikar.git
cd urlcikar
python3 urlcikar.py
```

İlk çalıştırmada config oluşturulur. Config'i düzenledikten sonra tekrar çalıştırın.

## Hızlı başlangıç

```bash
python3 urlcikar.py
nano ~/Desktop/urlcikar_config.json
python3 urlcikar.py
sort -u ~/Desktop/urls_raw.txt > ~/Desktop/urls.txt
```

## Komutlar

| Komut | Açıklama |
|---|---|
| `python3 urlcikar.py` | Taramayı başlat/devam ettir |
| `python3 urlcikar.py test` | Gömülü testleri çalıştır |
| `python3 urlcikar.py readme` | README'yi terminalde göster |
| `python3 urlcikar.py versiyon` | Sürüm bilgisi |
| `python3 urlcikar.py config` | Config'i göster/oluştur |
| `python3 urlcikar.py config-yenile` | Config'i varsayılanlarla yenile |
| `python3 urlcikar.py sifirla` | Resume durumunu kaldır |

## Büyük veri için

`urlcikar` benzersiz URL'leri RAM'de tutmaz. Bunun yerine ham çıktıyı diske yazar:

```bash
sort -S 2G -u urls_raw.txt > urls.txt
```

Geçici disk alanını ayrı bir filesystem'de tutabilirsiniz:

```bash
TMPDIR=/mnt/1tb/tmp sort --parallel=4 -S 2G -u urls_raw.txt > urls.txt
```

`sort` büyük datasetlerde yine RAM ve geçici disk alanı kullanabilir. `-S` RAM üst sınırını ayarlamak için kullanılabilir.

## Performans

Sabit bir RAM veya süre garantisi verilmez. Gerçek performans; toplam veri boyutu, dosya sayısı, dosya sistemi, depolama aygıtı, CPU, encoding ve URL yoğunluğuna bağlıdır.

Ölçümlerin tekrarlanabilir şekilde tutulması için [`docs/BENCHMARK.md`](docs/BENCHMARK.md) kullanın.

## Güvenlik ve veri bütünlüğü

Araç taranan dosyaları değiştirmez. Çıktı, state ve log dosyalarının taranan kök dizinin içinde olmasına izin verilmez; böylece aracın kendi çıktısını tekrar taraması engellenir.

`percent_decode`, `query_temizle` ve `fragment_temizle` bilgi kaybına yol açabilecek normalizasyon seçenekleridir ve varsayılan olarak kapalıdır.

Binary kontrolü kesin dosya tipi tespiti değildir; hızlı bir heuristiktir. Örneğin bazı UTF-16 dosyaları NUL byte içerdiğinden atlanabilir.

## Dokümantasyon

- [Kullanım Kılavuzu](docs/KULLANIM.md)
- [Mimari](docs/MIMARI.md)
- [SSS](docs/SSS.md)
- [Benchmark](docs/BENCHMARK.md)

## Lisans

MIT — [LICENSE](LICENSE)
