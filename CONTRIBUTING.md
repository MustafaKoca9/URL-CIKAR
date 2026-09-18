# Katkı Rehberi

Katkıda bulunmak için teşekkürler.

## Felsefe

- Standart kütüphane öncelikli
- Okunabilirlik > kısalık
- Yorumlar "neden"i açıklar
- Büyük veri kullanımında bellek davranışı korunur
- Tarama yapılan dosyalar değiştirilmez

## Pull Request

1. Fork oluşturun.
2. Yeni dal açın.
3. Değişikliği yapın.
4. `python3 urlcikar.py test` çalıştırın.
5. `python3 -m py_compile urlcikar.py` çalıştırın.
6. Dokümantasyonu gerekiyorsa güncelleyin.
7. PR açın.

## Kod stili

- PEP 8
- 4 boşluk
- `snake_case`
- Sabitler `UPPER_CASE`
- Yeni bağımlılık eklemek için gerekçe gerekir.

## Test

Yeni davranış ekliyorsanız `urlcikar.py` içindeki gömülü testlere uygun bir test ekleyin.
