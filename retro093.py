#!/usr/bin/env python3
"""Prepare and serve a pinned Debian 0.93R6 paper experiment (Python stdlib only).

Host commands: prepare, init, serve, run, change, type, screenshot, status,
quit, export. Run --help and see REPRODUCE-093.md. No sudo is used by this script.
"""
import argparse
import concurrent.futures
import functools
import gzip
import hashlib
import http.server
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

PAPER_COMMIT = 'ee2486875ebf6074bc008e6b969a49136eb78f77'
RESOURCES = [{'path': 'media/1440_boot_floppy.gz',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/disks/1440_boot_floppy.gz',
  'sha256': 'd4cca01346fba41bbd5a3c5f949f75bbaaff0f5c8e207f408f6ea293f6878e67',
  'bytes': 683386,
  'kind': 'media'},
 {'path': 'media/1440_root_floppy.gz',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/disks/1440_root_floppy.gz',
  'sha256': 'd9ea1db9c67a971f5ff3a7c5c4850a783ad4949183474cbd90cdfb9aa128bab5',
  'bytes': 531757,
  'kind': 'media'},
 {'path': 'media/1440_base_floppy-1',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/disks/1440_base_floppy-1',
  'sha256': '5298becea08a85ffd39e1bb8b086a825ac185e8b29d027583173eb7905ecf642',
  'bytes': 1474560,
  'kind': 'media'},
 {'path': 'media/1440_base_floppy-2',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/disks/1440_base_floppy-2',
  'sha256': 'c6a9cc9e8b71031a35c5f313f45dd78ac86f96ce32cba92f236ba24e174d3aab',
  'bytes': 1474560,
  'kind': 'media'},
 {'path': 'media/1440_base_floppy-3',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/disks/1440_base_floppy-3',
  'sha256': '51e05a6824884c6f94e369eb398d08198734315c71ca66d489a49c2a6d22bb71',
  'bytes': 1119232,
  'kind': 'media'},
 {'path': 'packages/netbase-1.17-1.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/net/netbase-1.17-1.deb',
  'sha256': 'f6774bf15f7aa938852acea81d23fb91a1c49a8320759d859b8da7d6dec3eaea',
  'bytes': 167678,
  'kind': 'bootstrap'},
 {'path': 'packages/lynx-2.4.2-1.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/net/lynx-2.4.2-1.deb',
  'sha256': '57910b2fae21b1230c7c7a65024f0f0534ce25cbafff3fd034de1e71d306ca8c',
  'bytes': 189477,
  'kind': 'bootstrap'},
 {'path': 'packages/lilo-16-0.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/admin/lilo-16-0.deb',
  'sha256': '155b7f0de980701d4a8d288cf74b09a6332c07e941664ba4ca5de62f7a8ca352',
  'bytes': 105980,
  'kind': 'bootstrap'},
 {'path': 'packages/ncurses-runtime-1.9.4-0.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/misc/ncurses-runtime-1.9.4-0.deb',
  'sha256': 'c94c8bb8b56403a95629899c848d48d4ee8f667f1dbfc6a3ea59c1652e724cec',
  'bytes': 329082,
  'kind': 'package'},
 {'path': 'packages/dialog-0.6-1.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/misc/dialog-0.6-1.deb',
  'sha256': 'e5d2d57c203c6030f2995d2d4b0dd6cc7a7d3b1846ade272a07316bc839c6770',
  'bytes': 73052,
  'kind': 'package'},
 {'path': 'packages/xlib-3.1.2-2.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/x11/xlib-3.1.2-2.deb',
  'sha256': 'da7e4df67f4cb2a3e0241e44cf8338863fa2b1fc5d37d674d54e77b58594cca2',
  'bytes': 451223,
  'kind': 'package'},
 {'path': 'packages/kpathsea-2.6-1.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/kpathsea-2.6-1.deb',
  'sha256': '43166d0177a98b6460c05b2338a7dfa3944230e958993cf0989274acfbbfafcf',
  'bytes': 91242,
  'kind': 'package'},
 {'path': 'packages/mflib-1.0-4.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/mflib-1.0-4.deb',
  'sha256': '395677ebc5185103aafa93d5255faaeafe4e5838726c1d0a67fe36f37e4c9233',
  'bytes': 38939,
  'kind': 'package'},
 {'path': 'packages/mfbin-2.71-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/mfbin-2.71-3.deb',
  'sha256': '1cd33b9f215f1760b5fb523180af0a899792297d22e12d2a429afa0ae9980a5b',
  'bytes': 389642,
  'kind': 'package'},
 {'path': 'packages/texlib-1.0-4.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/texlib-1.0-4.deb',
  'sha256': '0a43c47f8681d352a099ac92e6e6b0dd4764b3000e5bdadec558f796f3928e65',
  'bytes': 278282,
  'kind': 'package'},
 {'path': 'packages/texbin-3.1415-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/texbin-3.1415-3.deb',
  'sha256': '0d3e95a5ca34f17d9de82e1e0e339e31f9878aea5b9ef5b5a0e30822a6553fbc',
  'bytes': 294072,
  'kind': 'package'},
 {'path': 'packages/mfbasfnt-1.0-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/mfbasfnt-1.0-3.deb',
  'sha256': '0c73d291d466498e2828c51e70db0f30df79f3063610582323ac3fa4e5efebc3',
  'bytes': 252589,
  'kind': 'package'},
 {'path': 'packages/textfm-1.0-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/textfm-1.0-3.deb',
  'sha256': '9a7d3991df32ec8cc4adfac7d79ec1864935a1370cbd26737adaa97c70448766',
  'bytes': 155168,
  'kind': 'package'},
 {'path': 'packages/latex-2e-4.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/latex-2e-4.deb',
  'sha256': 'fe378c1b0e0255d86ba8247b0a5d9daed17d8b579ea38bf1d57674575c30aea9',
  'bytes': 779683,
  'kind': 'package'},
 {'path': 'packages/bibtex-0.99c-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/bibtex-0.99c-3.deb',
  'sha256': '0842c667270f34034150ad80e1984c901184824d6ab1a826284a708caa62b980',
  'bytes': 43200,
  'kind': 'package'},
 {'path': 'packages/dvipsk-5.58f-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/tex/dvipsk-5.58f-3.deb',
  'sha256': '6011341993d7d91dffdd2248dcb18630d4706bfefe4f3897590a2443cbcf3300',
  'bytes': 180824,
  'kind': 'package'},
 {'path': 'packages/gnuplot-3.5-3.deb',
  'url': 'https://archive.debian.org/debian/dists/Debian-0.93R6/binary/math/gnuplot-3.5-3.deb',
  'sha256': 'e278356ff54799482e2700b367b962a306ac5d677d1342b33cf092db9202eeb1',
  'bytes': 246063,
  'kind': 'package'},
 {'path': 'paper/debian_intro.tex',
  'url': 'https://raw.githubusercontent.com/Mantains/debian-history-paper/ee2486875ebf6074bc008e6b969a49136eb78f77/debian_intro.tex',
  'sha256': '80143df3c3e3f317ab41be5de138d62b0790adc80431019fbb7d67958042b479',
  'bytes': 2523,
  'kind': 'paper'},
 {'path': 'paper/plot.gp',
  'url': 'https://raw.githubusercontent.com/Mantains/debian-history-paper/ee2486875ebf6074bc008e6b969a49136eb78f77/plot.gp',
  'sha256': '94f1e30e08d6d884a4d99234b75d2e271100b5c6f737f8af7086e33903befa2b',
  'bytes': 1135,
  'kind': 'paper'},
 {'path': 'paper/debian.dat',
  'url': 'https://raw.githubusercontent.com/Mantains/debian-history-paper/ee2486875ebf6074bc008e6b969a49136eb78f77/debian.dat',
  'sha256': '83c3cb63363960095be8380c081ed66465cd2a75e55e12227dbcd5e58006545d',
  'bytes': 270,
  'kind': 'paper'},
 {'path': 'paper/references.bib',
  'url': 'https://raw.githubusercontent.com/Mantains/debian-history-paper/ee2486875ebf6074bc008e6b969a49136eb78f77/references.bib',
  'sha256': 'd2c39b7e5bf9c191cfd98a4856ea2bec2685eaf1d913271e8e5b8e44898dd171',
  'bytes': 200,
  'kind': 'paper'}]


def checked(path, item):
    return path.is_file() and path.stat().st_size == item['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']


def fetch(work, item):
    path = work / 'www' / item['path']
    path.parent.mkdir(parents=True, exist_ok=True)
    if checked(path, item):
        return 'verified cache: ' + item['path']
    temporary = path.with_name(path.name + '.part')
    for attempt in range(3):
        try:
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'debian-history-paper/retro093'})
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open('wb') as out:
                shutil.copyfileobj(response, out)
            if not checked(temporary, item):
                raise ValueError('SHA-256 or size mismatch: ' + item['url'])
            temporary.replace(path)
            return 'downloaded: ' + item['path']
        except Exception:
            temporary.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def write_shell(path, content):
    path.write_text(content, encoding='ascii', newline='\n')


def prepare(args):
    work = args.work
    work.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(functools.partial(fetch, work), RESOURCES):
            print(result, flush=True)
    for name in ('1440_boot_floppy', '1440_root_floppy'):
        data = gzip.decompress((work / 'www/media' / (name + '.gz')).read_bytes())
        (work / 'www/media' / name).write_bytes(data)
    last = work/'www/media/1440_base_floppy-3'
    (last.with_name(last.name+'.img')).write_bytes(last.read_bytes().ljust(1474560, b'\0'))
    manifest = {'paper_commit': PAPER_COMMIT, 'resources': RESOURCES}
    (work / 'www/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    write_shell(work / 'www/install-paper.sh', install_script())
    write_shell(work / 'www/build-paper.sh', BUILD_SCRIPT)
    print('Prepared all installation media, original binary packages, and four pinned paper source files.')


def install_script():
    packages = [pathlib.PurePosixPath(row['path']).name for row in RESOURCES if row['kind'] == 'package']
    script = '''#!/bin/sh
set -e
base=${1:-http://10.0.2.2:8000}
mkdir -p /root/paper/packages /root/paper/logs
cd /root/paper/packages
'''
    for name in packages:
        script += 'echo "GET ' + name + '"\nlynx -source "$base/packages/' + name + '" >' + name + '\ntest -s ' + name + '\n'
    script += 'dpkg -i ' + ' '.join(packages) + '\n'
    script += 'dpkg -l > /root/paper/logs/dpkg-list.txt\n'
    script += 'cd /root/paper\n'
    for name in ('debian_intro.tex', 'plot.gp', 'debian.dat', 'references.bib'):
        script += 'lynx -source "$base/paper/' + name + '" >' + name + '\n'
    script += '''lynx -source "$base/build-paper.sh" >build-paper.sh
echo 'Packages and four source files are ready in /root/paper'
'''
    return script


BOOTSTRAP_SCRIPT = '''#!/bin/sh
set -e
base=${1:-http://10.0.2.2:8000}
dpkg -i /mnt/netbase-1.17-1.deb /mnt/lynx-2.4.2-1.deb
ifconfig lo 127.0.0.1 up
ifconfig eth0 10.0.2.15 netmask 255.255.255.0 broadcast 10.0.2.255 up
route add -net 10.0.2.0 netmask 255.255.255.0 dev eth0
route add default gw 10.0.2.2
echo 'HTTP smoke test:'
lynx -source "$base/manifest.json" > /root/resource-manifest.json
test -s /root/resource-manifest.json
echo 'HTTP bootstrap ready. See tutorial for LILO and paper installation.'
'''

BUILD_SCRIPT = r'''#!/bin/sh
set -e
cd /usr/lib/texmf/ini
if test ! -s latex.fmt; then
    initex '\nonstopmode\input latex.ltx' </dev/null >/root/paper/logs/initex.txt 2>&1 || echo 'Inspect initex warning; checking actual format below.'
fi
test -s latex.fmt
ls -l latex.fmt
cd /root/paper
gnuplot plot.gp </dev/null >logs/gnuplot.txt 2>&1
latex '\nonstopmode\input debian_intro.tex' </dev/null >logs/latex1.txt 2>&1
bibtex debian_intro </dev/null >logs/bibtex.txt 2>&1
latex '\nonstopmode\input debian_intro.tex' </dev/null >logs/latex2.txt 2>&1
latex '\nonstopmode\input debian_intro.tex' </dev/null >logs/latex3.txt 2>&1
dvips -t a4 debian_intro.dvi -o debian_intro.ps </dev/null >logs/dvips.txt 2>&1
if grep -i 'undefined' logs/latex3.txt; then exit 1; fi
if grep '^!' logs/latex3.txt; then exit 1; fi
ls -l debian_plot.eps debian_intro.dvi debian_intro.ps
cp debian_intro.ps /mnt/debian_intro.ps
tar czf /mnt/paper-results.tgz debian_intro.tex plot.gp debian.dat references.bib debian_plot.eps debian_intro.dvi debian_intro.ps debian_intro.log debian_intro.bbl logs
sync
echo 'PAPER-BUILD-PASS: PS and logs copied to mounted /dev/hdb at /mnt'
'''


def require(*names):
    for name in names:
        if shutil.which(name) is None:
            raise RuntimeError('Missing host command: ' + name)


def init(args):
    require('qemu-img', 'mke2fs')
    work = args.work
    for row in RESOURCES:
        if not checked(work / 'www' / row['path'], row):
            raise RuntimeError('Run prepare first; resource missing or changed: ' + row['path'])
    if (work / 'system.img').exists() or (work / 'bootstrap.img').exists():
        raise RuntimeError('Refusing to overwrite an existing disk. Choose a new --work directory.')
    staging = work / 'bootstrap-files'
    staging.mkdir(exist_ok=True)
    for item in RESOURCES:
        if item['kind'] == 'bootstrap':
            shutil.copyfile(work / 'www' / item['path'], staging / pathlib.PurePosixPath(item['path']).name)
    write_shell(staging / 'bootstrap.sh', BOOTSTRAP_SCRIPT)
    subprocess.run(['qemu-img', 'create', '-f', 'raw', str(work / 'system.img'), '512M'], check=True)
    with (work / 'bootstrap.img').open('xb') as disk:
        disk.truncate(16 * 1024 * 1024)
    command = ['mke2fs', '-q', '-t', 'ext2', '-I', '128', '-b', '1024', '-F', '-d', str(staging), str(work / 'bootstrap.img')]
    environment = dict(os.environ, MKE2FS_CONFIG='/dev/null')
    result = subprocess.run(command[:1]+['-r','0']+command[1:], capture_output=True, text=True, env=environment)
    if result.returncode and '-r option has been removed' in result.stderr:
        result = subprocess.run(command[:1]+['-E','revision=0']+command[1:], capture_output=True, text=True, env=environment)
    if result.returncode:
        raise RuntimeError(result.stderr)
    (work/'initialized.json').write_text(json.dumps({'blank_system_bytes': 512*1024*1024, 'bootstrap_ext2_revision': 0})+'\n')
    print('Created a BLANK system.img and whole-device ext2 bootstrap.img (no partition table).')


def alive(work):
    try:
        pid = int((work / 'qemu.pid').read_text())
        os.kill(pid, 0)
        # An exited daemon can briefly remain a zombie; it no longer holds disks.
        status = pathlib.Path('/proc') / str(pid) / 'stat'
        if status.exists() and status.read_text().split()[2] == 'Z':
            return False
        return True
    except (FileNotFoundError, ProcessLookupError):
        return False


def socket_path(work):
    # DrvFS (/mnt/c, /mnt/e, ...) cannot hold Unix sockets; use Linux /tmp.
    identity = hashlib.sha256(str(work).encode()).hexdigest()[:16]
    return pathlib.Path(tempfile.gettempdir()) / ('paper093-'+str(os.getuid())+'-'+identity+'.sock')


def run(args):
    require('qemu-system-i386')
    work = args.work
    if alive(work):
        raise RuntimeError('VM already running in this --work directory.')
    if not (work / 'initialized.json').exists() or not (work / 'system.img').exists() or not (work / 'bootstrap.img').exists():
        raise RuntimeError('Run init first.')
    (work / 'qemu.pid').unlink(missing_ok=True)
    socket_path(work).unlink(missing_ok=True)
    command = ['qemu-system-i386', '-name', 'debian-093-fresh', '-machine', 'pc-i440fx-9.2', '-accel', 'tcg', '-cpu', 'qemu32', '-m', '32',
               '-drive', 'file='+str(work/'system.img')+',format=raw,if=ide,index=0',
               '-drive', 'file='+str(work/'bootstrap.img')+',format=raw,if=ide,index=1',
               '-vga', 'cirrus', '-nic', 'none', '-netdev', 'user,id=n0,ipv6=off',
               '-device', 'ne2k_isa,netdev=n0,iobase=0x300,irq=9',
               '-qmp', 'unix:'+str(socket_path(work))+',server=on,wait=off', '-pidfile', str(work/'qemu.pid'),
               '-serial', 'file:'+str(work/'serial.log')]
    if args.boot != 'disk':
        command += ['-drive', 'file='+str(work/'www/media/1440_boot_floppy')+',format=raw,if=floppy', '-boot', 'a']
    else:
        command += ['-boot', 'c']
    command += ['-display', 'none' if args.headless else 'gtk']
    if args.headless:
        command.append('-daemonize')
    (work/'launch.json').write_text(json.dumps(command, indent=2)+'\n')
    subprocess.run(command, check=True)


def qmp(work, command, arguments=None):
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(15)
        connection.connect(str(socket_path(work)))
        stream = connection.makefile('rwb', buffering=0)
        json.loads(stream.readline())
        for name, values in [('qmp_capabilities', None), (command, arguments)]:
            request = {'execute': name}
            if values is not None:
                request['arguments'] = values
            stream.write((json.dumps(request)+'\n').encode())
            while True:
                result = json.loads(stream.readline())
                if 'error' in result:
                    raise RuntimeError(result['error'])
                if 'return' in result:
                    break
        return result['return']


def hmp(work, command):
    result = qmp(work, 'human-monitor-command', {'command-line': command})
    if result:
        print(result)


def type_text(args):
    plain = dict(zip(" -/.,;='[]\\`\n", ('spc','minus','slash','dot','comma','semicolon','equal','apostrophe','bracket_left','bracket_right','backslash','grave_accent','ret')))
    shifted = dict(zip('_?:+"{}|~<>!@#$%^&*()', ('minus','slash','semicolon','equal','apostrophe','bracket_left','bracket_right','backslash','grave_accent','comma','dot','1','2','3','4','5','6','7','8','9','0')))
    for character in args.text:
        if character.isascii() and character.isalnum():
            key = ('shift-' if character.isupper() else '') + character.lower()
        elif character in plain:
            key = plain[character]
        elif character in shifted:
            key = 'shift-' + shifted[character]
        else:
            raise ValueError('Unsupported key: '+repr(character))
        hmp(args.work, 'sendkey '+key+' 30')
        time.sleep(.065)


def export(args):
    require('debugfs', 'ps2pdf', 'pdfinfo')
    work = args.work
    if alive(work):
        raise RuntimeError('Shut down Linux, verify System halted, then quit QEMU before export.')
    out = work/'results'
    out.mkdir(exist_ok=True)
    for name in ('debian_intro.ps', 'paper-results.tgz'):
        target = out/name
        if target.exists():
            raise RuntimeError('Output exists; preserve or move it before export: '+str(target))
        subprocess.run(['debugfs', '-R', 'dump /'+name+' '+str(target), str(work/'bootstrap.img')], check=True)
        if not target.exists() or target.stat().st_size == 0:
            raise RuntimeError('Guest result missing: '+name)
    subprocess.run(['ps2pdf', str(out/'debian_intro.ps'), str(out/'debian_intro.pdf')], check=True)
    info = subprocess.run(['pdfinfo', str(out/'debian_intro.pdf')], check=True, capture_output=True, text=True)
    (out/'pdfinfo.txt').write_text(info.stdout)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'SHA256.json').write_text(json.dumps(hashes, indent=2)+'\n')
    print(info.stdout)
    print('HOST conversion complete. Open '+str(out/'debian_intro.pdf')+' and check both pages.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=pathlib.Path, default=pathlib.Path('retro093-work'))
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ('prepare','init','status','quit','export'):
        sub.add_parser(name)
    serving = sub.add_parser('serve')
    serving.add_argument('--port', type=int, default=8000)
    running = sub.add_parser('run')
    running.add_argument('--boot', choices=('install','rescue','disk'), default='install')
    running.add_argument('--headless', action='store_true')
    changing = sub.add_parser('change')
    changing.add_argument('image', choices=('1440_root_floppy','1440_base_floppy-1','1440_base_floppy-2','1440_base_floppy-3','1440_boot_floppy'))
    typing = sub.add_parser('type')
    typing.add_argument('text')
    screenshot = sub.add_parser('screenshot')
    screenshot.add_argument('file', type=pathlib.Path)
    args = parser.parse_args()
    args.work = args.work.resolve()
    if any(c in str(args.work) for c in (' ', ',', '"', '\n')):
        parser.error('Use a work directory without spaces, commas, quotes or newlines (QEMU/debugfs syntax).')
    if args.action in ('prepare','init','run','export'):
        globals()[args.action](args)
    elif args.action == 'serve':
        directory = args.work/'www'
        if not (directory/'manifest.json').exists():
            raise RuntimeError('Run prepare first.')
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
        # HTTP/1.0 + Content-Length are compatible with Lynx 2.4.2 binary -source.
        with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
            print('Serving pinned resources on http://127.0.0.1:'+str(args.port), flush=True)
            print('QEMU guest URL: http://10.0.2.2:'+str(args.port), flush=True)
            server.serve_forever()
    elif args.action == 'change':
        image = args.image+'.img' if args.image == '1440_base_floppy-3' else args.image
        hmp(args.work, 'change floppy0 '+str(args.work/'www/media'/image))
    elif args.action == 'type':
        type_text(args)
    elif args.action == 'screenshot':
        target = args.file.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        qmp(args.work, 'screendump', {'filename': str(target), 'format': 'png'})
        print(target)
    elif args.action == 'status':
        print(json.dumps(qmp(args.work, 'query-status')))
    elif args.action == 'quit':
        print('QEMU quit does not shut down Linux. Use only after System halted.', file=sys.stderr)
        qmp(args.work, 'quit')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
