# SSS

## Neden `sort -u`?

Extractor'ın amacı URL bulmaktır; küresel deduplication state'i RAM'i büyütür. `sort -u` bu işi disk tabanlı harici sıralamayla yapabilir.

## Ne kadar sürer?

Sabit süre vermek doğru değildir. Toplam byte, dosya sayısı, depolama, filesystem, CPU ve URL yoğunluğu sonucu belirler.

## Çok RAM kullanır mı?

Program URL sayısıyla büyüyen bir `set()` tutmaz. Ancak Python, filesystem cache ve işletim sistemi normal bellek kullanır.

## Neden argparse yok?

Projenin basit tek-komut + JSON config yaklaşımı korunuyor.

## Neden tqdm yok?

Harici bağımlılık eklememek için standart terminal çıktısı kullanılır.

## Binary kontrolü kesin mi?

Hayır. NUL-byte heuristiğidir. UTF-16 gibi bazı metinler yanlışlıkla binary kabul edilebilir.

## Resume güvenli mi?

Checkpoint config fingerprint ve path bilgisiyle doğrulanır. Yine de dosyaların işlem sırasında değiştiği dinamik ağaçlarda tam transactional resume garanti edilmez.

## Config nerede?

Varsayılan olarak:

```text
~/Desktop/urlcikar_config.json
```

## Windows?

Kodun büyük bölümü platform bağımsızdır. `os.statvfs` bulunmayan sistemlerde minimum disk kontrolü atlanır.

## Birden fazla dizin?

Tek config tek root ile çalışır. Birden fazla root için işlemleri ayrı çalıştırıp raw çıktıları sonradan birleştirebilirsiniz.

## Çıktı neden `raw`?

Deduplication RAM'e bağlı olmaması için ham adaylar diske yazılır. Sonrasında:

```bash
sort -u urls_raw.txt > urls.txt
```

## Normalizasyon neden varsayılan değil?

`%2F`, query ve fragment gibi bileşenler URL semantiğinin parçası olabilir. Temizleme bilgi kaybına neden olabilir.
