.PHONY: clean

capp-installer: capp-installer-template src.tar.xz
	@(cat capp-installer-template; base64 src.tar.xz) > $@
	@chmod +x $@

proxy/nginx.tmpl: proxy/get-nginx-tmpl
	@./$<

src.tar.xz: proxy/nginx.tmpl proxy/.env proxy/docker-compose.yml dca/docker-compose.yml capp verify_dca.py
	@tar caf $@ proxy dca capp verify_dca.py

clean:
	@rm proxy/nginx.tmpl src.tar.xz capp-installer 2>/dev/null || true
