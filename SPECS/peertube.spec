%define debug_package %{nil}
%define repo github.com/Chocobozzz/PeerTube
%define _version 1.0.0-beta.3

Name:           peertube
Version:        1.0.0beta3
Release:        1%{?dist}
Summary:        Federated (ActivityPub) video streaming platform using P2P (BitTorrent) directly in the web browser with WebTorrent and Angular

License:        AGPLv3
URL:            https://%{repo}
Source0:        https://%{repo}/releases/download/v%{_version}/%{name}-v%{_version}.zip

Requires:       openssl nodejs >= 8 redis ffmpeg >= 3
BuildRequires:  npm python2 yarn systemd git

AutoReq:        no 
AutoReqProv:    no

%description
Federated (ActivityPub) video streaming platform using P2P (BitTorrent) directly in the web browser with WebTorrent and Angular

%prep
%setup -q -c -n %{name}-v%{_version}

%build
cd %{name}-v%{_version}
yarn install --production --pure-lockfile

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
fi

%files
%{_datadir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}/production.yaml
%license %{name}-v%{_version}/LICENSE
%doc %{name}-v%{_version}/support/doc

%changelog
* Thu Apr 12 2018 Pierre-Alain TORET <pierre-alain.toret@protonmail.com> 1.0.0-beta3-1
- Initial rpm : version 1.0.0-beta3