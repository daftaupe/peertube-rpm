%define debug_package %{nil}
%define repo github.com/Chocobozzz/PeerTube
%define _version 1.0.0-beta.8

Name:           peertube
Version:	1.0.0beta8
Release:        1%{?dist}
Summary:        Federated (ActivityPub) video streaming platform using P2P (BitTorrent) directly in the web browser with WebTorrent and Angular

License:        AGPLv3
URL:            https://%{repo}
Source0:        https://%{repo}/releases/download/v%{_version}/%{name}-v%{_version}.zip

Requires:       openssl nodejs >= 8 redis ffmpeg >= 3
BuildRequires:  nodejs >= 8 python2 yarn systemd git

AutoReq:        no 
AutoReqProv:    no

%description
Federated (ActivityPub) video streaming platform using P2P (BitTorrent) directly in the web browser with WebTorrent and Angular

%prep
%setup -q -c -n %{name}-v%{_version}

%build
cd %{name}-v%{_version}
if [ %{?dist} == ".el7" ];
then
    . /opt/rh/devtoolset-7/enable
    CC=/opt/rh/devtoolset-7/root/usr/bin/gcc CXX=/opt/rh/devtoolset-7/root/usr/bin/g++ yarn install --production --pure-lockfile
else
    yarn install --production --pure-lockfile
fi

%install
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datadir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}

cp %{name}-v%{_version}/support/systemd/%{name}.service %{buildroot}%{_unitdir}
sed -i  "s@/var/www/%{name}/config@/etc/%{name}@;s@/var/www/%{name}/%{name}-latest@/usr/share/%{name}@g" "%{buildroot}%{_unitdir}/%{name}.service"
cp %{name}-v%{_version}/config/production.yaml.example %{buildroot}%{_sysconfdir}/%{name}/production.yaml
sed -i "s@/var/www/%{name}@/var/lib/%{name}@g" "%{buildroot}%{_sysconfdir}/%{name}/production.yaml"

cp -a %{name}-v%{_version} %{buildroot}%{_datadir}/%{name}
rm -rf %{buildroot}%{_datadir}/%{name}/{config,*.md,LICENSE}

%post
if [ "$1" = 1 ]; then
    groupadd --system peertube
    useradd --system --gid peertube -d /var/lib/peertube -s /usr/bin/nologin peertube
    mkdir /var/lib/peertube
    chown -R peertube:peertube /var/lib/peertube 
fi

if [ "$1" = 2 ]; then
    systemctl daemon-reload
    if systemctl is-enabled peertube &>/dev/null || systemctl is-active peertube &>/dev/null ; then
        systemctl restart peertube
    fi
fi

%preun
if [ "$1" = 0 ]; then
    if systemctl is-enabled peertube &>/dev/null || systemctl is-active peertube &>/dev/null ; then
        systemctl stop peertube
        systemctl disable peertube
    fi
fi

%postun
if [ "$1" = 0 ]; then
    userdel -f peertube
    systemctl daemon-reload
	mv /var/lib/peertube /var/lib/peertube.bkp
fi

%files
%{_datadir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}/production.yaml
%license %{name}-v%{_version}/LICENSE
%doc %{name}-v%{_version}/support/doc

%changelog
* Tue Jun 12 2018 Rigel KENT <sendmemail@rigelk.eu> 1.0.0-beta8-1
- Update to version 1.0.0-beta8

* Tue May 29 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta7-1
- Update to version 1.0.0-beta7

* Wed May 23 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta6-1
- Update to version 1.0.0-beta6

* Mon May 07 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta4-1
- Update to version 1.0.0-beta4

* Sat Apr 14 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta3-2
- Inclusion of CentOS7 specific part

* Thu Apr 12 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta3-1
- Initial rpm : version 1.0.0-beta3
