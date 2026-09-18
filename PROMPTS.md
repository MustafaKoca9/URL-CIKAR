# AI Promptları

Bu dosya proje bakımında kullanılabilecek üretim prompt'larını içerir.

## Kod inceleme promptu

```text
urlcikar.py dosyasını güvenlik, correctness, filesystem edge-case,
resume doğruluğu, Unicode, URL parsing, büyük dosya performansı ve
RAM davranışı açısından incele. Varsayımları açıkça belirt.
Harici bağımlılık ekleme. Değişiklikleri gerekçelendir ve regression
testleri öner.
```

## Benchmark promptu

```text
urlcikar için tekrarlanabilir benchmark planı hazırla. Dosya sayısı,
toplam byte, URL yoğunluğu, disk tipi, filesystem, Python sürümü,
elapsed time, files/s, MB/s ve peak RSS ölçümlerini raporla.
Sonuçlardan genellenemeyecek iddiaları ayır.
```

## Dokümantasyon promptu

```text
urlcikar'ın davranışını kaynak koddan doğrula. Dokümantasyonda kaynak
kodun garanti etmediği RAM, süre, doğruluk veya platform iddialarını
kullanma. Türkçe ve teknik olarak ölçülü yaz.
```
