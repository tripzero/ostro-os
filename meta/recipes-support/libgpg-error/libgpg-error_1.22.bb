SUMMARY = "Small library that defines common error values for all GnuPG components"
HOMEPAGE = "http://www.gnupg.org/related_software/libgpg-error/"
BUGTRACKER = "https://bugs.g10code.com/gnupg/index"

LICENSE = "GPLv2+ & LGPLv2.1+"
LIC_FILES_CHKSUM = "file://COPYING;md5=59530bdf33659b29e73d4adb9f9f6552 \
                    file://COPYING.LIB;md5=2d5025d4aa3495befef8f17206a5b0a1 \
                    file://src/gpg-error.h.in;endline=23;md5=cf562f60b9dba7df20d6ee3f97ea1d5a \
                    file://src/init.c;endline=20;md5=872b2389fe9bae7ffb80d2b91225afbc"


SECTION = "libs"

UPSTREAM_CHECK_URI = "https://gnupg.org/download/index.html"
SRC_URI = "${GNUPG_MIRROR}/libgpg-error/libgpg-error-${PV}.tar.bz2 \
           file://pkgconfig.patch \
	  "
SRC_URI[md5sum] = "83c686abe3fa223ec89f3b51da830770"
SRC_URI[sha256sum] = "f2a04ee6317bdb41a625bea23fdc7f0b5a63fb677f02447c647ed61fb9e69d7b"

BINCONFIG = "${bindir}/gpg-error-config"

inherit autotools binconfig-disabled pkgconfig gettext
CPPFLAGS += "-P"
do_compile_prepend() {
	TARGET_FILE=linux-gnu
	if [ ${TARGET_OS} != "linux" ]; then
		TARGET_FILE=${TARGET_OS}
	fi

	case ${TARGET_ARCH} in
	  aarch64_be) TUPLE=aarch64-unknown-linux-gnu ;;
	  arm)	      TUPLE=arm-unknown-linux-gnueabi ;;
	  armeb)      TUPLE=arm-unknown-linux-gnueabi ;;
	  i586|i686)  TUPLE=i686-pc-linux-gnu ;;
	  mips64el)   TUPLE=mipsel-unknown-linux-gnu ;;
	  mips64)     TUPLE=mips-unknown-linux-gnu ;;
	  x86_64)     TUPLE=x86_64-pc-linux-gnu ;;
	  *)          TUPLE=${TARGET_ARCH}-unknown-linux-gnu ;; 
	esac

	cp ${S}/src/syscfg/lock-obj-pub.$TUPLE.h \
	  ${S}/src/syscfg/lock-obj-pub.$TARGET_FILE.h
}

do_install_append() {
	# we don't have common lisp in OE
	rm -rf "${D}${datadir}/common-lisp/"
}

FILES_${PN}-dev += "${bindir}/gpg-error"

BBCLASSEXTEND = "native"
