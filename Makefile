VERSION=$(shell python -c 'from inputdeviceindicator.info import VERSION; print(VERSION)' )

install_local: bdist_deb
	sudo dpkg -i deb_dist/input-device-indicator*.deb
sdist_dsc:
	python setup.py --command-packages=stdeb.command sdist_dsc
bdist_deb:
	python setup.py --command-packages=stdeb.command bdist_deb
clean:
	-rm input-device-indicator*.deb input-device-indicator*.tar.gz
	-rm -r dist deb_dist tmp *.egg-info
publish: clean sdist_dsc
	mkdir -p tmp
	cd tmp ; \
	ls ../deb_dist/input-device-indicator_${VERSION}-1.dsc ; \
	dpkg-source -x ../deb_dist/input-device-indicator_${VERSION}-1.dsc ; \
	cd input-device-indicator-${VERSION} ; \
	debuild -S -sa ; \
	dput ppa:brandizzi/ppa ../input-device-indicator_${VERSION}-1_source.changes
