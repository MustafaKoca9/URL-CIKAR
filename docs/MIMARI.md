# Mimari

## 1. Streaming output

Problem: URL'leri `set()` içinde tutmak benzersiz URL sayısı büyüdükçe RAM'i büyütür.

Karar: Her URL doğrudan raw output'a yazılır.

Avantaj: Bellek tüketimi URL sayısıyla doğrusal büyümez.

Dezavantaj: Raw çıktı tekilleştirilmiş çıktından çok daha büyük olabilir.

## 2. `sort -u`

Tekilleştirme extractor'ın işi değildir. Unix ortamında `sort -u`, harici sıralama kullanarak büyük datasetleri yönetebilir.

Avantaj: Python heap'inde milyonlarca string tutulmaz.

Dezavantaj: Geçici disk ve RAM gerekir.

## 3. Deterministik traversal

Resume için dosya sırası önemlidir. `os.scandir()` sonuçları doğal olarak garanti edilmiş sıralı bir liste değildir.

Karar: Dizin stack'i kontrollü ve isim sırasına göre oluşturulur.

## 4. URL regex + parser

Regex yalnızca aday bulur. `urllib.parse.urlsplit()` scheme, netloc ve hostname gibi yapısal kontrolleri yapar.

Bu ayrım regex'in tam bir URL parser'a dönüşmesini engeller.

## 5. Checkpoint

State JSON'unda config fingerprint, root, output, son path ve işlenen dosya sayısı tutulur.

Config değişirse eski checkpoint kullanılmaz.

## 6. Atomik state

State önce `.tmp` dosyasına yazılır, `fsync()` uygulanır ve `os.replace()` ile yer değiştirilir.

Bu, yarım JSON state bırakma riskini azaltır. Mutlak elektrik kesintisi dayanıklılığı filesystem ve donanım davranışına bağlıdır.

## 7. Binary heuristiği

İlk N byte içinde NUL bulunması hızlı bir filtre olarak kullanılır. Bu kesin MIME/file-type tespiti değildir.

## 8. Self-scan koruması

Output/state/log dosyalarının taranan kökün altında bulunmasına izin verilmez. Böylece program kendi çıktısını tarama riskini engeller.

## 9. Normalizasyon

Query, fragment ve percent decoding ayrı seçeneklerdir. Bunlar URL kimliğini değiştirebilir ve varsayılan olarak kapalıdır.

## 10. Bellek modeli

Büyük global URL set'i yoktur. Temel akış:

Filesystem → eligibility → binary check → streaming reader → candidate regex → URL parser → filters → normalization → output.

Büyük input dosyasının tamamı RAM'e yüklenmez.
