SHELL = /bin/bash
INSTALL_PATH = /opt/dewey
VERSION ?= $(shell cat VERSION)
PLOP_BRANCH ?= development

install: FINAL_PATH = $(DESTDIR)$(INSTALL_PATH)

all:

install:
	[ -f .gitmodules ] || git submodule init
	git submodule update --init
	cd lib && git fetch && git pull origin master && git lfs pull && cd ..
	mkdir -p $(FINAL_PATH) $(DESTDIR)/usr/bin $(DESTDIR)/etc/init $(DESTDIR)/etc/default
	virtualenv -p python3 $(FINAL_PATH)
	. $(FINAL_PATH)/bin/activate && pip --version | grep 9.0.1 || pip install --no-index --find-links lib/python --upgrade pip
	. $(FINAL_PATH)/bin/activate && pip install --no-index --find-links lib/python -r requirements/production.txt
	. $(FINAL_PATH)/bin/activate && python setup.py install
	rsync -rl bin/ $(DESTDIR)/usr/bin/
	cp debian/dewey-scheduler.upstart $(DESTDIR)/etc/init/dewey-scheduler.conf
	cp debian/dewey-worker.upstart $(DESTDIR)/etc/init/dewey-worker.conf
	cp debian/dewey-flower.upstart $(DESTDIR)/etc/init/dewey-flower.conf
	for file in `ls lib/misc/*.tar.gz`; do tar xzf $$file -C $(DESTDIR); done
	virtualenv -p python3 --relocatable $(FINAL_PATH)
	echo '[ -f /etc/default/dewey ] && . /etc/default/dewey' >> $(FINAL_PATH)/bin/activate
	sed -i 's/^VIRTUAL_ENV.*$$/VIRTUAL_ENV="\/opt\/dewey"/' $(FINAL_PATH)/bin/activate

.PHONY: docker
docker:
	mkdir -p tmp/
	-git clone git@github.com:PLOS/plop.git tmp/plop
	pushd tmp/plop && git pull && git checkout $(PLOP_BRANCH) && popd
	docker build -t plos/dewey:v$(VERSION) .
