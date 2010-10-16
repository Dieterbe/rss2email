# packagers, set DESTDIR to your "package directory" and PREFIX to the prefix you want to have on the end-user system
# end-users who install directly, without packaging: don't care about DESTDIR, update PREFIX if you want to
PREFIX?=/usr/local
INSTALLDIR?=$(DESTDIR)$(PREFIX)
SHAREDIR?=$(INSTALLDIR)/share/rss2email

install:
	install -d $(INSTALLDIR)/bin
	install -d $(SHAREDIR)/docs
	install -d $(SHAREDIR)/examples
	install -D -m755 r2e               $(INSTALLDIR)/bin
	install -D -m755 rss2email.py      $(INSTALLDIR)/bin
	install -D -m644 README            $(SHAREDIR)/docs
	install -D -m644 CHANGELOG         $(SHAREDIR)/docs
	install -D -m644 config.py         $(SHAREDIR)/examples/

uninstall:
	rm -f $(INSTALLDIR)/bin/rss2email.py
	rm -f $(INSTALLDIR)/bin/r2e
	rm -rf $(SHAREDIR)

