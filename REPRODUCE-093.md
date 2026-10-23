# Debian 0.93R6：从空白磁盘到 PDF

本流程只编译本仓库为旧工具链准备的示例文章。老 Debian 负责生成 EPS、DVI 和 PostScript；现代宿主负责把 PS 转成 PDF。不需要给客体移植 SSH，也不需要安装 X、邮件服务器或完整开发环境。

配套的 `retro093.py` 仅使用 Python 3 标准库；它会下载五份安装介质、必要的原版 `.deb` 和固定提交的四个源码文件，并逐个核对内嵌的 SHA-256 和字节数。没有借用预装系统盘。软件以原版二进制包安装，因此不需要额外下载并编译 Gnuplot、TeX 或 Dropbear 源码；文章源码固定于 `ee2486875ebf6074bc008e6b969a49136eb78f77`。

## 1. 现代宿主的准备

以下命令在现代 Debian/Ubuntu 的 **Linux shell** 中执行。Windows 用户应在 WSL2 的 Debian 中执行，QEMU 窗口通过 WSLg 显示。Python 工具的下载/HTTP 部分不依赖 pip；磁盘及模拟器操作使用系统命令。

```bash
sudo apt update
sudo apt install python3 git qemu-system-x86 qemu-system-gui qemu-utils e2fsprogs ghostscript poppler-utils
git clone https://github.com/Mantains/debian-history-paper.git
cd debian-history-paper
LAB="$HOME/debian093-lab"
python3 retro093.py --work "$LAB" prepare
python3 retro093.py --work "$LAB" init
```

测试宿主为 Debian trixie，QEMU 10.0.13，Python 3.13，e2fsprogs 1.47.2。启动命令固定使用 `pc-i440fx-9.2`，需要提供该机型的 QEMU（9.2 或更新版本）。`qemu-system-i386 -machine help` 可以查看可用机型。较旧发行版需要先升级 QEMU。

`init` 只创建两块新盘：

| 文件 | 容量 | 内容及客体位置 |
| --- | --- | --- |
| `system.img` | 512 MiB | 空白系统盘，客体 `/dev/hda`；安装时创建 `/dev/hda1` |
| `bootstrap.img` | 16 MiB | ext2 revision 0，无分区表，客体整个 `/dev/hdb`；只预置 netbase、Lynx、LILO 和 bootstrap.sh，之后也用于导出结果 |

工具拒绝覆盖已有盘。要重新安装，请选择一个新的 `--work` 路径。不要用 `/dev/hdb1` 挂载辅助盘；它没有分区。

`prepare` 可重复运行，已有文件仍会校验；下载失败或校验不符会停止。所有输入的 URL、版本及校验值另写入 `$LAB/www/manifest.json`。

## 2. 启动宿主 HTTP 服务和虚拟机

终端 A 留在仓库根目录，执行：

```bash
LAB="$HOME/debian093-lab"
python3 retro093.py --work "$LAB" serve
```

服务只监听 `127.0.0.1:8000`，只提供 `$LAB/www`。QEMU 的 user 网络允许客体通过 `10.0.2.2:8000` 访问同一 Linux 宿主；服务和 QEMU 应在同一个 WSL 发行版中运行。这里不使用旧测试脚本里的 `restrict=on`，也不向局域网转发客体服务。

终端 B 也进入仓库根目录，执行：

```bash
LAB="$HOME/debian093-lab"
python3 retro093.py --work "$LAB" run --boot install
```

QEMU 窗口会显示软盘引导提示。终端 B 在窗口关闭前保持占用。后续宿主换盘命令在终端 C 执行，同样先进入仓库根目录并设置 `LAB`。这些操作不会自动选择其他已有的测试盘。

## 3. 从软盘安装基础系统

以下按屏幕提示操作。键盘被 QEMU 捕获时，按 Ctrl+Alt 可释放。不要把现代宿主的真实磁盘路径传给虚拟机。

1. 在 `boot:` 提示符按 Enter。等待 `Insert Debian GNU/Linux Root Disk and press <ENTER>`。
2. 在宿主终端 C 执行：

   ```bash
   python3 retro093.py --work "$LAB" change 1440_root_floppy
   ```

   回到 QEMU 按 Enter，等待读盘结束。
3. 欢迎页选 OK，显示设置选 Continue，安装模式选 **Expert**。
4. 选 **1 Partition A Hard Disk**，磁盘选 **/dev/hda**。在 cfdisk 中依次选择 New → Primary，大小用默认值占满磁盘；设置 Bootable。选择 Write（快捷键是大写 W），输入 `yes`，等待写入完成，再 Quit。
5. 选 **3 Prepare A Linux Partition**，输入框已有 `/dev/`，在后面补 `hda1`。等待格式化和坏块检查完成；512 MiB 在模拟环境中也可能需要几分钟。
6. 选 **4 Mount/Unmount Partitions**，按其命令提示把 hda1 挂到根目录：输入 `m`，设备框已有 `/dev/`，补 `hda1`；目录框已有 `/`，直接 Enter；最后输入 `c` 继续。不是把它挂到宿主目录。
7. 选 **5 Install Debian GNU/Linux**，确认根分区 `/dev/hda1`，来源选 `/dev/fd0`。按提示依次换入三个分卷：

   ```bash
   python3 retro093.py --work "$LAB" change 1440_base_floppy-1
   python3 retro093.py --work "$LAB" change 1440_base_floppy-2
   python3 retro093.py --work "$LAB" change 1440_base_floppy-3
   ```

   **每次只执行当前所需的一条**，回到 QEMU 按 Enter，等下一张盘的提示再换。第三张官方下载只有 1,119,232 字节，这是完整分卷；但 QEMU 软驱需要标准容量。工具保留原件与校验值，另生成补零到 1,474,560 字节的 `.img` 副本，`change` 命令自动选择该副本。直接插入未补齐的第三张会出现 `/dev/fd0: No such device or address`。
8. 选 **6 Configure Debian GNU/Linux**，确认根分区，选择键盘；本次使用 `en.us`。各模块选择页保持默认，不额外加载模块。主机名用 `debian`，域名留空，时区按实际所在地选择。
9. 在重启之前，把软盘换回引导盘：

   ```bash
   python3 retro093.py --work "$LAB" change 1440_boot_floppy
   ```

   再选 **9 Reboot The System**。在新的 `boot:` 提示符输入：

   ```text
   linux root=/dev/hda1
   ```

10. 以 root 登录，按首次启动提示设置自己的密码，然后创建一个普通账户（例如 `paper`）并设置密码。姓名、办公室等四项可留空，最后的确认要明确输入 `y`。首次配置接着启动 dselect，选择 **6 [Q]uit** 退出，不在这里选择其他软件。回到 login 提示后，再以 root 和刚设置的密码登录。此时先借软盘内核启动硬盘上的系统；安装 LILO 后才改成直接硬盘引导。

## 4. 用辅助盘引导 HTTP 下载

以下命令全部在 **Debian 0.93R6 客体内**执行：

```sh
mount -t ext2 /dev/hdb /mnt
ls /mnt
sh /mnt/bootstrap.sh
```

脚本从辅助盘安装 `netbase-1.17-1.deb` 和 `lynx-2.4.2-1.deb`。netbase 会询问 `/etc/init.d/netbase`、gateways、hosts.allow、hosts.deny、rpc 等配置文件差异，均选默认 **N**（Enter），保留安装器生成的版本；Lynx 询问默认主页时也可 Enter。然后脚本设置 ISA NE2000 网络，并通过 HTTP GET 把宿主清单下载到 `/root/resource-manifest.json`。它在本次新安装中运行一次即可；重复执行 `route add` 可能报告路由已存在。

网络配置等价于：

```sh
ifconfig lo 127.0.0.1 up
ifconfig eth0 10.0.2.15 netmask 255.255.255.0 broadcast 10.0.2.255 up
route add -net 10.0.2.0 netmask 255.255.255.0 dev eth0
route add default gw 10.0.2.2
```

`dmesg` 应显示 NE2000 位于 0x300、IRQ 9。若 HTTP 失败，先确认终端 A 仍在运行服务、地址和端口是 `10.0.2.2:8000`，再检查 `ifconfig` 和 `route -n`。客体不需要支持 HTTPS：下载归档和 GitHub HTTPS 的工作由宿主 Python 完成。

接着安装 LILO：

```sh
dpkg -i /mnt/lilo-16-0.deb
```

根据安装脚本提示确认安装引导器。本教程的根分区是 `/dev/hda1`，引导盘是 `/dev/hda`。不要照抄旧源盘中并不存在的 `/mnt/lilo*.deb` 路径。

## 5. 最小排版软件和四个源码文件

客体执行：

```sh
cd /root
lynx -source http://10.0.2.2:8000/install-paper.sh >install-paper.sh
test -s install-paper.sh
sh install-paper.sh
echo $?
```

退出状态应为 0。texlib 配置期间会出现 **Hyphenation** 语言选择框，保留包含 english 的默认选择，确认 OK；不要将整个安装命令的输出重定向到文件，否则可能看不到这个界面。安装脚本以 HTTP GET 获取以下包，按表中顺序交给原装 dpkg；不使用 `--force-depends`。同一次 dpkg 调用会先解包，再按依赖配置，最后保存已安装包清单。

| 软件包文件 | 在此流程中的用途 |
| --- | --- |
| `ncurses-runtime-1.9.4-0.deb` | dialog 所需的 ncurses 运行环境 |
| `dialog-0.6-1.deb` | texlib 的配置工具 |
| `xlib-3.1.2-2.deb` | 提供 mfbin 声明依赖的 `xlibraries`；不安装 X server |
| `kpathsea-2.6-1.deb` | TeX 系列的文件及字体搜索 |
| `mflib-1.0-4.deb` | Metafont 辅助文件及字体生成脚本 |
| `mfbin-2.71-3.deb` | 提供 `metafont`，供 TeX/dvips 的字体生成使用 |
| `texlib-1.0-4.deb` | TeX 宏、断词和标准参考文献样式等辅助文件 |
| `texbin-3.1415-3.deb` | TeX、initex，提供虚拟包 `tex` |
| `mfbasfnt-1.0-3.deb` | 基础字体源文件 |
| `textfm-1.0-3.deb` | 字体度量文件 |
| `latex-2e-4.deb` | LaTeX 格式和宏 |
| `bibtex-0.99c-3.deb` | 参考文献处理 |
| `dvipsk-5.58f-3.deb` | DVI 转 PostScript，及相应 EPS 宏 |
| `gnuplot-3.5-3.deb` | 从数据生成 EPS |

基础系统提供已有 libc 和 shell 等运行条件；这不是供任意裸根目录使用的通用依赖求解器。本集合针对上述软盘安装出的 0.93R6。

脚本也把固定版本的 `debian_intro.tex`、`plot.gp`、`debian.dat`、`references.bib` 放到 `/root/paper/`，把构建脚本放到 `/root/paper/build-paper.sh`。不用在客体里安装 Git。

```sh
cd /root/paper
ls -l debian_intro.tex plot.gp debian.dat references.bib
```

四个文件长度分别应为 2523、1135、270、200 字节。最终结果包也包含这四个输入，宿主可以再次与下载清单核对。

## 6. 格式文件、绘图与排版

一键运行已经下载的构建脚本：

```sh
sh /root/paper/build-paper.sh
```

它先进入 `/usr/lib/texmf/ini`。仅当 `latex.fmt` 不存在或为空时，执行：

```sh
cd /usr/lib/texmf/ini
initex '\nonstopmode\input latex.ltx' </dev/null >/root/paper/logs/initex.txt 2>&1
ls -l latex.fmt
test -s latex.fmt
```

旧 LaTeX 会检查源文件年龄。日期警告可能使 initex 退出非零，因此必须同时检查实际生成的格式和随后的文章编译；不能只忽略错误码。不要修改时钟或宏源码来隐藏检查。脚本保留初始化日志，并在没有非空格式文件时停止。

随后回到 `/root/paper`，执行六个阶段：

```sh
cd /root/paper
gnuplot plot.gp
latex '\nonstopmode\input debian_intro.tex'
bibtex debian_intro
latex '\nonstopmode\input debian_intro.tex'
latex '\nonstopmode\input debian_intro.tex'
dvips -t a4 debian_intro.dvi -o debian_intro.ps
```

脚本实际为每一步保存独立日志、遇到失败就停止，并检查最终日志中没有 `!` 错误和未定义引用。首次 dvips 可能调用 Metafont 生成 PK 字体，耗时会比后续运行长。

最后应有 `debian_plot.eps`、`debian_intro.dvi`、`debian_intro.ps`。脚本会把 PS 和包含源码、日志的 `paper-results.tgz` 复制到已挂载的 `/mnt` 辅助盘。看见 `PAPER-BUILD-PASS` 后再进入下一步。

## 7. 导出 PS，在现代宿主生成 PDF

客体内执行：

```sh
sync
umount /mnt
shutdown -h now
```

等屏幕真正显示 `System halted`。然后在宿主终端 C 退出模拟器并导出：

```bash
python3 retro093.py --work "$LAB" quit
python3 retro093.py --work "$LAB" export
```

`quit` 只退出模拟器，不能代替 Linux 的正常关机。`export` 拒绝在 QEMU 仍运行时读取辅助盘。它使用宿主 debugfs 只读导出两个文件，再运行：

```bash
ps2pdf "$LAB/results/debian_intro.ps" "$LAB/results/debian_intro.pdf"
pdfinfo "$LAB/results/debian_intro.pdf"
```

最终 PDF 位于 `$LAB/results/debian_intro.pdf`；PS、原始结果包、pdfinfo 输出和 SHA-256 记录在同一目录。用宿主 PDF 阅读器打开，检查两页：第一页正文和参考文献，第二页图表及图注。还可以渲染图片检查：

```bash
pdftoppm -png -r 120 "$LAB/results/debian_intro.pdf" "$LAB/results/page"
```

老式 Type3 字体可能使现代渲染器输出 bounding box 警告，仍需检查实际页面。本文不证明客体直接生成 PDF，也不保证任意现代 LaTeX 项目可以在旧宏包上编译。

## 8. 再次启动

LILO 安装成功并正常关机后，宿主运行：

```bash
python3 retro093.py --work "$LAB" run --boot disk
```

此时不挂引导软盘。如果要重新下载东西，仍需启动宿主 HTTP 服务并在客体设置网络；首次安装时的手工路由不会自动永久保存。已有软件和 `/root/paper` 文件保存在系统盘。

## 扩展与原始来源

X 桌面、额外 SSH、本地邮件和网页浏览属于另外的实验，不是生成 PDF 的前置条件。旧测试盘的 xdm Oops 和 gpm 关机问题也不应直接套用到未安装这些组件的最小系统。

- 原始介质与软件包：[Debian Archive](https://archive.debian.org/debian/dists/Debian-0.93R6/)。
- QEMU 网络结构：[官方 user 网络说明](https://www.qemu.org/docs/master/system/devices/net.html)。
- e2fsprogs 参数变化：[上游 1.47.2 发行记录](https://github.com/tytso/e2fsprogs/blob/master/doc/RelNotes/v1.47.2.txt)。工具自动兼容旧 `-r 0` 和新 `-E revision=0`。
