ARCHIVE = src.tar.xz
TMPL = capp-installer-template
INSTALLER = $(patsubst %-template,%,$(TMPL))
SOURCES = capp verify_dca.py get_deploy_keys
DIRS = proxy dca
ALL_SOURCES = $(wildcard $(addsuffix *,$(DIRS))) $(OCAL_SOURCES)

$(INSTALLER): $(TMPL) $(ARCHIVE)
	@CAPP_VER=$$(sed -rn '/^__version__ =/{s/.*\((.+), (.+), (.+)\)/\1.\2.\3/;p}' capp); \
	(sed -r "s/^CAPP_VER=.*/CAPP_VER=$$CAPP_VER/" $(TMPL); base64 $(ARCHIVE)) > $@
	@chmod +x $@

proxy/nginx.tmpl: proxy/get-nginx-tmpl
	@./$<

$(ARCHIVE): $(ALL_SOURCES)
	@tar caf $@ $(DIRS) $(SOURCES)

clean:
	@rm proxy/nginx.tmpl $(ARCHIVE) $(INSTALLER) 2>/dev/null || true

.PHONY: clean $(ARCHIVE)
