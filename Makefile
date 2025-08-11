TMPL = install/capp-installer
ARCHIVE = src.tar.xz
INSTALLER = capp-installer
SOURCES = \
  confs/compose.sudoers \
  confs/compose@.service \
  confs/deploy.sudoers \
  confs/sshd-deploy.conf \
  scripts/capp \
  scripts/compose-systemd \
  scripts/deploy-capp \
  scripts/get_deploy_keys \
  scripts/wait-for-cpu-idle
DIRS = \
  proxy \
  dca
DOCKER_GEN_FILES = \
  docker-gen/docker-gen \
  docker-gen/LICENSE
GEN_FILES = \
  proxy/gen/docker-gen \
  proxy/gen/LICENSE \
  proxy/le/docker-gen
ALL_SOURCES = $(shell for dir in $(DIRS); do find $$dir -type f -not -name '.*'; done) $(SOURCES) $(GEN_FILES)

# Show all available targets
help:
	@for target in $$(grep '^\.PHONY:' Makefile|cut -d: -f2); do \
		msg=$$(grep -B1 "^$$target:" Makefile|grep '^#'|cut -c3-); \
		echo "$$target:$$msg"; \
	done | column -s: -t

# Create the installer
installer: $(INSTALLER)
$(INSTALLER): $(TMPL) $(ARCHIVE)
	@CAPP_VER=$$(./project_version get); \
	(sed -r "s/^CAPP_VER=.*/CAPP_VER=$$CAPP_VER/" $(TMPL); base64 $(ARCHIVE)) > $@
	@chmod +x $@

docker-gen/docker-gen: docker-gen/version docker-gen/build docker-gen/security-updates
	@./docker-gen/build
docker-gen/LICENSE: docker-gen/docker-gen

proxy/gen/docker-gen: docker-gen/docker-gen
	@cp $< $@
proxy/gen/LICENSE: docker-gen/LICENSE
	@cp $< $@
proxy/gen/nginx.tmpl: proxy/gen/get-nginx-tmpl
	@./$<
proxy/le/docker-gen: docker-gen/docker-gen
	@cp $< $@

# Make the install source archive
archive: $(ARCHIVE)
$(ARCHIVE): $(ALL_SOURCES)
	@tar caf $@ $(DIRS) $(SOURCES)

# Remove generated files
clean:
	@rm $(DOCKER_GEN_FILES) $(GEN_FILES) $(ARCHIVE) 2>/dev/null || true
	@rm -r __pycache__ 2>/dev/null || true

# Remove all created files
dist-clean: clean
	@rm $(INSTALLER) 2>/dev/null || true

.PHONY: help installer archive clean dist-clean
