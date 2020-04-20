%define api %(echo %{version} |cut -d. -f1)
%define major %api

%define qtminor %(echo %{version} |cut -d. -f2)
%define qtsubminor %(echo %{version} |cut -d. -f3)
%define beta beta4

%define major_private 1
%define qtversion %{api}.%{qtminor}.%{qtsubminor}

%define qtx11extras %mklibname qt%{api}x11extras %{major}
%define qtx11extrasd %mklibname qt%{api}x11extras -d
%define qtx11extras_p_d %mklibname qt%{api}x11extras-private -d

%define _qt5_prefix %{_libdir}/qt%{api}

Name:		qt5-qtx11extras
Version:	5.15.0
%if "%{beta}" != ""
Release:	0.%{beta}.1
%define qttarballdir qtx11extras-everywhere-src-%{version}-%{beta}
Source0:	http://download.qt.io/development_releases/qt/%(echo %{version}|cut -d. -f1-2)/%{version}-%{beta}/submodules/%{qttarballdir}.tar.xz
%else
Release:	1
%define qttarballdir qtx11extras-everywhere-src-%{version}
Source0:	http://download.qt.io/official_releases/qt/%(echo %{version}|cut -d. -f1-2)/%{version}/submodules/%{qttarballdir}.tar.xz
%endif
Summary:	Qt GUI toolkit
Group:		Development/KDE and Qt
License:	LGPLv2 with exceptions or GPLv3 with exceptions and GFDL
URL:		http://www.qt.io
BuildRequires:	qmake5 >= %version
BuildRequires:	pkgconfig(Qt5Gui) >= %version
BuildRequires:	pkgconfig(Qt5Widgets) >= %version
# For the Provides: generator
BuildRequires:	cmake >= 3.11.0-1

%description
Provides specific APIs for X11.

#------------------------------------------------------------------------------

%package -n %{qtx11extras}
Summary: Qt%{api} Component Library
Group: System/Libraries

%description -n %{qtx11extras}
Qt%{api} Component Library.


%files -n %{qtx11extras}
%{_qt5_libdir}/libQt5X11Extras.so.%{api}*

#------------------------------------------------------------------------------

%package -n %{qtx11extrasd}
Summary: Devel files needed to build apps based on QtX11Extras
Group:    Development/KDE and Qt
Requires: %{qtx11extras} = %version

%description -n %{qtx11extrasd}
Devel files needed to build apps based on QtX11Extras.

%files -n %{qtx11extrasd}
%{_qt5_includedir}/QtX11Extras
%{_qt5_libdir}/cmake/Qt5X11Extras
%{_qt5_libdir}/libQt5X11Extras.prl
%{_qt5_libdir}/libQt5X11Extras.so
%{_qt5_libdir}/pkgconfig/Qt5X11Extras.pc
%{_qt5_prefix}/mkspecs/modules/qt_lib_x11extras.pri
%{_qt5_prefix}/mkspecs/modules/qt_lib_x11extras_private.pri

#------------------------------------------------------------------------------

%prep
%autosetup -n %qttarballdir -p1

%build
%qmake_qt5

%make_build
#------------------------------------------------------------------------------

%install
%make_install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


# Don't reference builddir neither /usr(/X11R6)?/ in .pc files.
perl -pi -e '\
s@-L/usr/X11R6/%{_lib} @@g;\
s@-I/usr/X11R6/include @@g;\
s@-L/%{_builddir}\S+@@g'\
    `find . -name \*.pc`

# .la and .a files, die, die, die.
rm -f %{buildroot}%{_qt5_libdir}/lib*.la
rm -f %{buildroot}%{_qt5_libdir}/lib*.a
