.PHONY: help test run readme clean lint

help:
	@echo "urlcikar — komutlar:"
	@echo "  make run       Taramayı başlat"
	@echo "  make test      Testleri çalıştır"
	@echo "  make readme    README'yi göster"
	@echo "  make clean     Geçici dosyaları temizle"
	@echo "  make lint      Sözdizimi kontrolü"

run:
	python3 urlcikar.py

test:
	python3 urlcikar.py test

readme:
	python3 urlcikar.py readme

clean:
	rm -f urlcikar_durum.json.tmp
	rm -f *.state.json
	rm -rf __pycache__/
	find . -name "*.pyc" -delete

lint:
	python3 -m py_compile urlcikar.py
	@echo "Sözdizimi OK"
