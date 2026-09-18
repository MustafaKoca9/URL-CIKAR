# Changelog

Bu proje Semantic Versioning kullanır.

## [Unreleased]

## [2.1.0] - 2026-09-18

### Eklendi
- URL candidate regex + `urllib.parse.urlsplit()` doğrulama katmanı
- Domain boundary-aware allowlist/denylist
- Deterministik directory traversal
- Self-scan koruması
- Daha güvenli checkpoint modeli ve config fingerprint
- Dry-run ve kapsamlı filtreler
- Benchmark dokümantasyonu

### Düzeltildi
- Performans ve RAM konusunda garanti niteliğindeki ifadeler kaldırıldı
- Binary tespitinin heuristik olduğu açıkça belirtildi
- Normalizasyon seçeneklerinin bilgi kaybı riski belgelendi

## [2.0.0] - 2025-01-15

### Eklendi
- Resume desteği
- Gömülü test
- JSON config
- Sinyal yakalama
- Binary tespiti
- Disk alanı kontrolü
- Atomik durum kaydı
- İlerleme göstergesi
- Domain ve uzantı filtreleri

### Değişti
- RAM tabanlı URL `set()` yaklaşımı kaldırıldı
- Satır/stream tabanlı okuma
- Tek output handle

## [1.0.0] - 2024-12-01

### Eklendi
- İlk sürüm
- Regex ile URL çıkarma
- Set ile tekilleştirme
