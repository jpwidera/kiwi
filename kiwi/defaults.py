# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import os
import glob
from collections import namedtuple
import platform
from pkg_resources import resource_filename

# project
from .path import Path
from .version import (
    __githash__,
    __version__
)

from .exceptions import KiwiBootLoaderGrubDataError


class Defaults:
    """
    **Implements default values**

    Provides static methods for default values and state information
    """
    def __init__(self):
        self.defaults = {
            # alignment in bytes
            'kiwi_align': 1048576,
            # start sector number
            'kiwi_startsector': 2048,
            # sectorsize in bytes
            'kiwi_sectorsize': 512,
            # inode size in bytes for inode based filesystems
            'kiwi_inode_size': 256,
            # inode ratio for inode based filesystems
            'kiwi_inode_ratio': 16384,
            # minimum inode number for inode based filesystems
            'kiwi_min_inodes': 20000,
            # kiwi git revision
            'kiwi_revision': __githash__
        }
        self.profile_key_list = [
            'kiwi_align',
            'kiwi_startsector',
            'kiwi_sectorsize',
            'kiwi_revision'
        ]

    @staticmethod
    def get_luks_key_length():
        """
        Provides key length to use for random luks keys
        """
        return 256

    @staticmethod
    def get_xz_compression_options():
        """
        Provides compression options for the xz compressor

        :return:
            Contains list of options

            .. code:: python

                ['--option=value']

        :rtype: list
        """
        return [
            '--threads=0'
        ]

    @staticmethod
    def is_x86_arch(arch):
        """
        Checks if machine architecture is x86 based

        Any arch that matches 32bit and 64bit x86 architecture
        causes the method to return True. Anything else will
        cause the method to return False

        :rtype: bool
        """
        if arch == 'x86_64' or arch == 'i686' or arch == 'i586':
            return True
        return False

    @staticmethod
    def is_buildservice_worker():
        """
        Checks if build host is an open buildservice machine

        The presence of /.buildenv on the build host indicates
        we are building inside of the open buildservice

        :return: True if obs worker, else False

        :rtype: bool
        """
        return os.path.exists(
            os.sep + Defaults.get_buildservice_env_name()
        )

    @staticmethod
    def get_buildservice_env_name():
        """
        Provides the base name of the environment file in a
        buildservice worker

        :return: file basename

        :rtype: str
        """
        return '.buildenv'

    @staticmethod
    def get_obs_download_server_url():
        """
        Provides the default download server url hosting the public open
        buildservice repositories

        :return: url path

        :rtype: str
        """
        return 'http://download.opensuse.org/repositories'

    @staticmethod
    def get_s390_disk_block_size():
        """
        Provides the default block size for s390 storage disks

        :return: blocksize value

        :rtype: int
        """
        return '4096'

    @staticmethod
    def get_s390_disk_type():
        """
        Provides the default disk type for s390 storage disks

        :return: type name

        :rtype: str
        """
        return 'CDL'

    @staticmethod
    def get_solvable_location():
        """
        Provides the directory to store SAT solvables for repositories.
        The solvable files are used to perform package
        dependency and metadata resolution

        :return: directory path

        :rtype: str
        """
        return '/var/tmp/kiwi/satsolver'

    @staticmethod
    def get_shared_cache_location():
        """
        Provides the shared cache location

        This is a directory which shares data from the image buildsystem
        host with the image root system. The location is returned as an
        absolute path stripped off by the leading '/'. This is because
        the path is transparently used on the host /<cache-dir> and
        inside of the image imageroot/<cache-dir>

        :return: directory path

        :rtype: str
        """
        from .cli import Cli
        return os.path.abspath(os.path.normpath(
            Cli().get_global_args().get('--shared-cache-dir')
        )).lstrip(os.sep)

    @staticmethod
    def get_exclude_list_for_root_data_sync():
        """
        Provides the list of files or folders that are created
        by KIWI for its own purposes. Those files should be not
        be included in the resulting image.

        :return: list of file and directory names

        :rtype: list
        """
        exclude_list = [
            'image', '.profile', '.kconfig',
            Defaults.get_buildservice_env_name(),
            Defaults.get_shared_cache_location()
        ]
        return exclude_list

    @staticmethod
    def get_failsafe_kernel_options():
        """
        Provides failsafe boot kernel options

        :return:
            list of kernel options

            .. code:: python

                ['option=value', 'option']

        :rtype: list
        """
        return ' '.join(
            [
                'ide=nodma',
                'apm=off',
                'noresume',
                'edd=off',
                'nomodeset',
                '3'
            ]
        )

    @staticmethod
    def get_video_mode_map():
        """
        Provides video mode map

        Assign a tuple to each kernel vesa hex id for each of the
        supported bootloaders

        :return:
            video type map

            .. code:: python

                {'kernel_hex_mode': video_type(grub2='mode', isolinux='mode')}

        :rtype: dict
        """
        video_type = namedtuple(
            'video_type', ['grub2', 'isolinux']
        )
        return {
            '0x301': video_type(grub2='640x480', isolinux='640 480'),
            '0x310': video_type(grub2='640x480', isolinux='640 480'),
            '0x311': video_type(grub2='640x480', isolinux='640 480'),
            '0x312': video_type(grub2='640x480', isolinux='640 480'),
            '0x303': video_type(grub2='800x600', isolinux='800 600'),
            '0x313': video_type(grub2='800x600', isolinux='800 600'),
            '0x314': video_type(grub2='800x600', isolinux='800 600'),
            '0x315': video_type(grub2='800x600', isolinux='800 600'),
            '0x305': video_type(grub2='1024x768', isolinux='1024 768'),
            '0x316': video_type(grub2='1024x768', isolinux='1024 768'),
            '0x317': video_type(grub2='1024x768', isolinux='1024 768'),
            '0x318': video_type(grub2='1024x768', isolinux='1024 768'),
            '0x307': video_type(grub2='1280x1024', isolinux='1280 1024'),
            '0x319': video_type(grub2='1280x1024', isolinux='1280 1024'),
            '0x31a': video_type(grub2='1280x1024', isolinux='1280 1024'),
            '0x31b': video_type(grub2='1280x1024', isolinux='1280 1024'),
        }

    @staticmethod
    def get_volume_id():
        """
        Provides default value for ISO volume ID

        :return: name

        :rtype: str
        """
        return 'CDROM'

    @staticmethod
    def get_install_volume_id():
        """
        Provides default value for ISO volume ID for install media

        :return: name

        :rtype: str
        """
        return 'INSTALL'

    @staticmethod
    def get_snapper_config_template_file():
        """
        Provides the default configuration template file for snapper

        :return: file

        :rtype: str
        """
        return '/etc/snapper/config-templates/default'

    @staticmethod
    def get_default_video_mode():
        """
        Provides 800x600 default video mode as hex value for the kernel

        :return: vesa video kernel hex value

        :rtype: str
        """
        return '0x303'

    @staticmethod
    def get_grub_boot_directory_name(lookup_path):
        """
        Provides grub2 data directory name in boot/ directory

        Depending on the distribution the grub2 boot path could be
        either boot/grub2 or boot/grub. The method will decide for
        the correct base directory name according to the name pattern
        of the installed grub2 tools

        :return: directory basename

        :rtype: str
        """
        chroot_env = {
            'PATH': os.sep.join([lookup_path, 'usr', 'sbin'])
        }
        if Path.which(filename='grub2-install', custom_env=chroot_env):
            # the presence of grub2-install is an indicator to put all
            # grub2 data below boot/grub2
            return 'grub2'
        else:
            # in any other case the assumption is made that all grub
            # boot data should live below boot/grub
            return 'grub'

    @staticmethod
    def get_grub_basic_modules(multiboot):
        """
        Provides list of basic grub modules

        :param bool multiboot: grub multiboot mode

        :return: list of module names

        :rtype: list
        """
        modules = [
            'ext2',
            'iso9660',
            'linux',
            'echo',
            'configfile',
            'search_label',
            'search_fs_file',
            'search',
            'search_fs_uuid',
            'ls',
            'normal',
            'gzio',
            'png',
            'fat',
            'gettext',
            'font',
            'minicmd',
            'gfxterm',
            'gfxmenu',
            'all_video',
            'xfs',
            'btrfs',
            'lvm',
            'luks',
            'gcry_rijndael',
            'gcry_sha256',
            'gcry_sha512',
            'crypto',
            'cryptodisk',
            'test',
            'true'
        ]
        if multiboot:
            modules.append('multiboot')
        return modules

    @staticmethod
    def get_grub_efi_modules(multiboot=False):
        """
        Provides list of grub efi modules

        :param bool multiboot: grub multiboot mode

        :return: list of module names

        :rtype: list
        """
        host_architecture = platform.machine()
        modules = Defaults.get_grub_basic_modules(multiboot) + [
            'part_gpt',
            'part_msdos',
            'efi_gop'
        ]
        if host_architecture == 'x86_64':
            modules += [
                'efi_uga',
                'linuxefi'
            ]
        return modules

    @staticmethod
    def get_grub_bios_modules(multiboot=False):
        """
        Provides list of grub bios modules

        :param bool multiboot: grub multiboot mode

        :return: list of module names

        :rtype: list
        """
        modules = Defaults.get_grub_basic_modules(multiboot) + [
            'part_gpt',
            'part_msdos',
            'biosdisk',
            'vga',
            'vbe',
            'chain',
            'boot'
        ]
        return modules

    @staticmethod
    def get_grub_ofw_modules():
        """
        Provides list of grub ofw modules (ppc)

        :return: list of module names

        :rtype: list
        """
        modules = Defaults.get_grub_basic_modules(multiboot=False) + [
            'part_gpt',
            'part_msdos',
            'boot'
        ]
        return modules

    @staticmethod
    def get_grub_path(root_path, filename, raise_on_error=True):
        """
        Provides grub path to given search file

        Depending on the distribution grub could be installed below
        a grub2 or grub directory. grub could also reside in /usr/lib
        as well as in /usr/share. Therefore this information needs
        to be dynamically looked up

        :param string root_path: root path to start the lookup from
        :param string filename: filename to search
        :param bool raise_on_error: raise on not found, defaults to True

        The method returns the path to the given grub search file.
        By default it raises a KiwiBootLoaderGrubDataError exception
        if the file could not be found in any of the search locations.
        If raise_on_error is set to False and no file could be found
        the function returns None

        :return: filepath

        :rtype: str
        """
        install_dirs = [
            'usr/share', 'usr/lib'
        ]
        lookup_list = []
        for grub_name in ['grub2', 'grub']:
            for install_dir in install_dirs:
                grub_path = os.sep.join(
                    [root_path, install_dir, grub_name, filename]
                )
                if os.path.exists(grub_path):
                    return grub_path
                lookup_list.append(grub_path)
        if raise_on_error:
            raise KiwiBootLoaderGrubDataError(
                'grub path {0} not found in {1}'.format(filename, lookup_list)
            )

    @staticmethod
    def get_preparer():
        """
        Provides ISO preparer name

        :return: name

        :rtype: str
        """
        return 'KIWI - https://github.com/OSInside/kiwi'

    @staticmethod
    def get_publisher():
        """
        Provides ISO publisher name

        :return: name

        :rtype: str
        """
        return 'SUSE LINUX GmbH'

    @staticmethod
    def get_shim_loader(root_path):
        """
        Provides shim loader file path

        Searches distribution specific locations to find shim.efi
        below the given root path

        :param string root_path: image root path

        :return: file path or None

        :rtype: str
        """
        shim_file_patterns = [
            '/usr/share/efi/*/shim.efi',
            '/usr/lib64/efi/shim.efi',
            '/boot/efi/EFI/*/shim.efi'
        ]
        for shim_file_pattern in shim_file_patterns:
            for shim_file in glob.iglob(root_path + shim_file_pattern):
                return shim_file

    @staticmethod
    def get_unsigned_grub_loader(root_path):
        """
        Provides unsigned grub efi loader file path

        Searches distribution specific locations to find grub.efi
        below the given root path

        :param string root_path: image root path

        :return: file path or None

        :rtype: str
        """
        unsigned_grub_file_patterns = [
            '/usr/share/grub*/*-efi/grub.efi',
            '/usr/lib/grub*/*-efi/grub.efi'
        ]
        for unsigned_grub_file_pattern in unsigned_grub_file_patterns:
            for unsigned_grub_file in glob.iglob(
                root_path + unsigned_grub_file_pattern
            ):
                return unsigned_grub_file

    @staticmethod
    def get_grub_bios_core_loader(root_path):
        """
        Provides grub bios image

        Searches distribution specific locations to find the
        core bios image below the given root path

        :param string root_path: image root path

        :return: file path or None

        :rtype: str
        """
        bios_grub_core_patterns = [
            '/usr/share/grub*/i386-pc/{0}'.format(
                Defaults.get_bios_image_name()
            ),
            '/usr/lib/grub*/i386-pc/{0}'.format(
                Defaults.get_bios_image_name()
            )
        ]
        for bios_grub_core_pattern in bios_grub_core_patterns:
            for bios_grub_core in glob.iglob(
                root_path + bios_grub_core_pattern
            ):
                return bios_grub_core

    @staticmethod
    def get_syslinux_modules():
        """
        Returns list of syslinux modules to include on ISO
        images that boots via isolinux

        :return: base file names

        :rtype: list
        """
        return [
            'isolinux.bin',
            'ldlinux.c32',
            'libcom32.c32',
            'libutil.c32',
            'gfxboot.c32',
            'gfxboot.com',
            'menu.c32',
            'chain.c32',
            'mboot.c32'
        ]

    @staticmethod
    def get_syslinux_search_paths():
        """
        syslinux is packaged differently between distributions.
        This method returns a list of directories to search for
        syslinux data

        :return: directory names

        :rtype: list
        """
        return [
            '/usr/share/syslinux',
            '/usr/lib/syslinux/modules/bios',
            '/usr/lib/ISOLINUX'
        ]

    @staticmethod
    def get_isolinux_bios_grub_loader():
        """
        Return name of eltorito grub image used as isolinux loader
        in BIOS mode if isolinux.bin should not be used

        :return: file base name

        :rtype: str
        """
        return 'eltorito.img'

    @staticmethod
    def get_signed_grub_loader(root_path):
        """
        Provides shim signed grub loader file path

        Searches distribution specific locations to find grub.efi
        below the given root path

        :param string root_path: image root path

        :return: file path or None

        :rtype: str
        """
        signed_grub_file_patterns = [
            '/usr/share/efi/*/grub.efi',
            '/usr/lib64/efi/grub.efi',
            '/boot/efi/EFI/*/grub*.efi',
            '/usr/share/grub*/*-efi/grub.efi'
        ]
        for signed_grub_pattern in signed_grub_file_patterns:
            for signed_grub in glob.iglob(root_path + signed_grub_pattern):
                return signed_grub

    @staticmethod
    def get_shim_vendor_directory(root_path):
        """
        Provides shim vendor directory

        Searches distribution specific locations to find shim.efi
        below the given root path and return the directory name
        to the file found

        :param string root_path: image root path

        :return: directory path or None

        :rtype: str
        """
        shim_vendor_patterns = [
            '/boot/efi/EFI/*/shim.efi',
            '/EFI/*/shim.efi'
        ]
        for shim_vendor_pattern in shim_vendor_patterns:
            for shim_file in glob.iglob(root_path + shim_vendor_pattern):
                return os.path.dirname(shim_file)

    @staticmethod
    def get_default_volume_group_name():
        """
        Provides default LVM volume group name

        :return: name

        :rtype: str
        """
        return 'systemVG'

    @staticmethod
    def get_min_partition_mbytes():
        """
        Provides default minimum partition size in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 10

    @staticmethod
    def get_min_volume_mbytes():
        """
        Provides default minimum LVM volume size in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 30

    @staticmethod
    def get_lvm_overhead_mbytes():
        """
        Provides empiric LVM overhead size in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 80

    @staticmethod
    def get_default_boot_mbytes():
        """
        Provides default boot partition size in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 300

    @staticmethod
    def get_default_efi_boot_mbytes():
        """
        Provides default EFI partition size in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 20

    @staticmethod
    def get_recovery_spare_mbytes():
        """
        Provides spare size of recovery partition in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 300

    @staticmethod
    def get_default_legacy_bios_mbytes():
        """
        Provides default size of bios_grub partition in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 2

    @staticmethod
    def get_default_prep_mbytes():
        """
        Provides default size of prep partition in mbytes

        :return: mbsize value

        :rtype: int
        """
        return 8

    @staticmethod
    def get_disk_format_types():
        """
        Provides supported disk format types

        :return: disk types

        :rtype: list
        """
        return [
            'gce', 'qcow2', 'vmdk', 'ova', 'vmx', 'vhd', 'vhdx',
            'vhdfixed', 'vdi', 'vagrant.libvirt.box', 'vagrant.virtualbox.box'
        ]

    @staticmethod
    def get_vagrant_config_virtualbox_guest_additions():
        """
        Provides the default value for
        ``vagrantconfig.virtualbox_guest_additions_present``

        :return: whether guest additions are expected to be present in the
            vagrant box

        :rtype: bool
        """
        return False

    @staticmethod
    def get_firmware_types():
        """
        Provides supported architecture specific firmware types

        :return: firmware types per architecture

        :rtype: dict
        """
        return {
            'x86_64': ['efi', 'uefi', 'bios', 'ec2hvm', 'ec2'],
            'i586': ['bios'],
            'i686': ['bios'],
            'aarch64': ['efi', 'uefi'],
            'arm64': ['efi', 'uefi'],
            'armv5el': ['efi', 'uefi'],
            'armv5tel': ['efi', 'uefi'],
            'armv6hl': ['efi', 'uefi'],
            'armv6l': ['efi', 'uefi'],
            'armv7hl': ['efi', 'uefi'],
            'armv7l': ['efi', 'uefi'],
            'ppc': ['ofw'],
            'ppc64': ['ofw', 'opal'],
            'ppc64le': ['ofw', 'opal'],
            's390': [],
            's390x': []
        }

    @staticmethod
    def get_default_firmware(arch):
        """
        Provides default firmware for specified architecture

        :param string arch: platform.machine

        :return: firmware name

        :rtype: str
        """
        default_firmware = {
            'x86_64': 'bios',
            'i586': 'bios',
            'i686': 'bios',
            'ppc': 'ofw',
            'ppc64': 'ofw',
            'ppc64le': 'ofw',
            'arm64': 'efi',
            'armv5el': 'efi',
            'armv5tel': 'efi',
            'armv6hl': 'efi',
            'armv6l': 'efi',
            'armv7hl': 'efi',
            'armv7l': 'efi'
        }
        if arch in default_firmware:
            return default_firmware[arch]

    @staticmethod
    def get_efi_capable_firmware_names():
        """
        Provides list of EFI capable firmware names. These are
        those for which kiwi supports the creation of an EFI
        bootable disk image

        :return: firmware names

        :rtype: list
        """
        return ['efi', 'uefi']

    @staticmethod
    def get_ec2_capable_firmware_names():
        """
        Provides list of EC2 capable firmware names. These are
        those for which kiwi supports the creation of disk images
        bootable within the Amazon EC2 public cloud

        :return: firmware names

        :rtype: list
        """
        return ['ec2']

    @staticmethod
    def get_efi_module_directory_name(arch):
        """
        Provides architecture specific EFI directory name which
        stores the EFI binaries for the desired architecture.

        :param string arch: platform.machine

        :return: directory name

        :rtype: str
        """
        default_module_directory_names = {
            'x86_64': 'x86_64-efi',

            # There is no dedicated xen architecture but there are
            # modules provided for xen. Thus we treat it as an
            # architecture
            'x86_64_xen': 'x86_64-xen',

            'aarch64': 'arm64-efi',
            'arm64': 'arm64-efi',
            'armv5el': 'arm-efi',
            'armv5tel': 'arm-efi',
            'armv6l': 'arm-efi',
            'armv7l': 'arm-efi'
        }
        if arch in default_module_directory_names:
            return default_module_directory_names[arch]

    @staticmethod
    def get_bios_module_directory_name():
        """
        Provides x86 BIOS directory name which stores the pc binaries

        :return: directory name

        :rtype: str
        """
        return 'i386-pc'

    @staticmethod
    def get_efi_image_name(arch):
        """
        Provides architecture specific EFI boot binary name

        :param string arch: platform.machine

        :return: name

        :rtype: str
        """
        default_efi_image_names = {
            'x86_64': 'bootx64.efi',
            'aarch64': 'bootaa64.efi',
            'arm64': 'bootaa64.efi',
            'armv5el': 'bootarm.efi',
            'armv5tel': 'bootarm.efi',
            'armv6l': 'bootarm.efi',
            'armv7l': 'bootarm.efi'
        }
        if arch in default_efi_image_names:
            return default_efi_image_names[arch]

    @staticmethod
    def get_bios_image_name():
        """
        Provides bios core boot binary name

        :return: name

        :rtype: str
        """
        return 'core.img'

    @staticmethod
    def get_default_boot_timeout_seconds():
        """
        Provides default boot timeout in seconds

        :return: seconds

        :rtype: int
        """
        return 10

    @staticmethod
    def get_default_disk_start_sector():
        """
        Provides the default initial disk sector for the first disk
        partition.

        :return: sector value

        :rtype: int
        """
        return Defaults().defaults['kiwi_startsector']

    @staticmethod
    def get_default_efi_partition_table_type():
        """
        Provides the default partition table type for efi firmwares.

        :return: partition table type name

        :rtype: str
        """
        return 'gpt'

    @staticmethod
    def get_default_inode_size():
        """
        Provides default size of inodes in bytes. This is only
        relevant for inode based filesystems

        :return: bytesize value

        :rtype: int
        """
        return Defaults().defaults['kiwi_inode_size']

    @staticmethod
    def get_archive_image_types():
        """
        Provides list of supported archive image types

        :return: archive names

        :rtype: list
        """
        return ['tbz']

    @staticmethod
    def get_container_image_types():
        """
        Provides list of supported container image types

        :return: container names

        :rtype: list
        """
        return ['docker', 'oci']

    @staticmethod
    def get_filesystem_image_types():
        """
        Provides list of supported filesystem image types

        :return: filesystem names

        :rtype: list
        """
        return [
            'ext2', 'ext3', 'ext4', 'btrfs', 'squashfs',
            'xfs', 'fat16', 'fat32'
        ]

    @staticmethod
    def get_default_live_iso_type():
        """
        Provides default live iso union type

        :return: live iso type

        :rtype: str
        """
        return 'overlay'

    @staticmethod
    def get_default_uri_type():
        """
        Provides default URI type

        Absolute path specifications used in the context of an URI
        will apply the specified default mime type

        :return: URI mime type

        :rtype: str
        """
        return 'dir:/'

    @staticmethod
    def get_dracut_conf_name():
        """
        Provides file path of dracut config file to be used with KIWI

        :return: file path name

        :rtype: str
        """
        return '/etc/dracut.conf.d/02-kiwi.conf'

    @staticmethod
    def get_live_dracut_module_from_flag(flag_name):
        """
        Provides flag_name to dracut module name map

        Depending on the value of the flag attribute in the KIWI image
        description a specific dracut module needs to be selected

        :return: dracut module name

        :rtype: str
        """
        live_modules = {
            'overlay': 'kiwi-live',
            'dmsquash': 'dmsquash-live livenet'
        }
        if flag_name in live_modules:
            return live_modules[flag_name]
        else:
            return 'kiwi-live'

    @staticmethod
    def get_default_live_iso_root_filesystem():
        """
        Provides default live iso root filesystem type

        :return: filesystem name

        :rtype: str
        """
        return 'ext4'

    @staticmethod
    def get_live_iso_persistent_boot_options(persistent_filesystem=None):
        """
        Provides list of boot options passed to the dracut
        kiwi-live module to setup persistent writing

        :return: list of boot options

        :rtype: list
        """
        live_iso_persistent_boot_options = [
            'rd.live.overlay.persistent'
        ]
        if persistent_filesystem:
            live_iso_persistent_boot_options.append(
                'rd.live.overlay.cowfs={0}'.format(persistent_filesystem)
            )
        return live_iso_persistent_boot_options

    @staticmethod
    def get_disk_image_types():
        """
        Provides supported disk image types

        :return: disk image type names

        :rtype: list
        """
        return ['oem', 'vmx']

    @staticmethod
    def get_live_image_types():
        """
        Provides supported live image types

        :return: live image type names

        :rtype: list
        """
        return ['iso']

    @staticmethod
    def get_network_image_types():
        """
        Provides supported pxe image types

        :return: pxe image type names

        :rtype: list
        """
        return ['pxe']

    @staticmethod
    def get_boot_image_description_path():
        """
        Provides the path to find custom kiwi boot descriptions

        :return: directory path

        :rtype: str
        """
        return '/usr/share/kiwi/custom_boot'

    @staticmethod
    def get_boot_image_strip_file():
        """
        Provides the file path to bootloader strip metadata.
        This file contains information about the files and directories
        automatically striped out from the kiwi initrd

        :return: file path

        :rtype: str
        """
        return Defaults.project_file('config/strip.xml')

    @staticmethod
    def get_schema_file():
        """
        Provides file path to kiwi RelaxNG schema

        :return: file path

        :rtype: str
        """
        return Defaults.project_file('schema/kiwi.rng')

    @staticmethod
    def get_common_functions_file():
        """
        Provides the file path to config functions metadata.

        This file contains bash functions used for system
        configuration or in the boot code from the kiwi initrd

        :return: file path

        :rtype: str
        """
        return Defaults.project_file('config/functions.sh')

    @staticmethod
    def get_xsl_stylesheet_file():
        """
        Provides the file path to the KIWI XSLT style sheets

        :return: file path

        :rtype: str
        """
        return Defaults.project_file('xsl/master.xsl')

    @staticmethod
    def project_file(filename):
        """
        Provides the python module base directory search path

        The method uses the resource_filename method to identify
        files and directories from the application

        :param string filename: relative project file

        :return: absolute file path name

        :rtype: str
        """
        return resource_filename('kiwi', filename)

    @staticmethod
    def get_imported_root_image(root_dir):
        """
        Provides the path to an imported root system image

        If the image description specified a derived_from attribute
        the file from this attribute is copied into the root_dir
        using the name as provided by this method

        :param string root_dir: image root directory

        :return: file path name

        :rtype: str
        """
        return os.sep.join([root_dir, 'image', 'imported_root'])

    @staticmethod
    def get_iso_boot_path():
        """
        Provides arch specific relative path to boot files
        on kiwi iso filesystems

        :return: relative path name

        :rtype: str
        """
        arch = platform.machine()
        if arch == 'i686' or arch == 'i586':
            arch = 'ix86'
        return os.sep.join(['boot', arch])

    @staticmethod
    def get_iso_tool_category():
        """
        Provides default iso tool category

        :return: name

        :rtype: str
        """
        return 'xorriso'

    @staticmethod
    def get_container_compression():
        """
        Provides default container compression algorithm

        :return: name

        :rtype: str
        """
        return 'xz'

    @staticmethod
    def get_default_container_name():
        """
        Provides the default container name.

        :return: name

        :rtype: str
        """
        return 'kiwi-container'

    @staticmethod
    def get_container_base_image_tag():
        """
        Provides the tag used to identify base layers during the build
        of derived images.

        :return: tag

        :rtype: str
        """
        return 'base_layer'

    @staticmethod
    def get_oci_archive_tool():
        """
        Provides the default OCI archive tool name.

        :return: name

        :rtype: str
        """
        return 'umoci'

    @staticmethod
    def get_default_container_tag():
        """
        Provides the default container tag.

        :return: tag

        :rtype: str
        """
        return 'latest'

    @staticmethod
    def get_default_container_subcommand():
        """
        Provides the default container subcommand.

        :return: command as a list of arguments

        :rtype: list
        """
        return ['/bin/bash']

    @staticmethod
    def get_default_container_created_by():
        """
        Provides the default 'created by' history entry for containers.

        :return: the specific kiwi version used for the build

        :rtype: str
        """
        return 'KIWI {0}'.format(__version__)

    @staticmethod
    def get_custom_rpm_macros_path():
        """
        Returns the custom macros directory for the rpm database.

        :return: path name

        :rtype: str
        """
        return 'usr/lib/rpm/macros.d'

    @staticmethod
    def get_custom_rpm_bootstrap_macro_name():
        """
        Returns the rpm bootstrap macro file name created
        in the custom rpm macros path

        :return: filename

        :rtype: str
        """
        return 'macros.kiwi-bootstrap-config'

    @staticmethod
    def get_custom_rpm_image_macro_name():
        """
        Returns the rpm image macro file name created
        in the custom rpm macros path

        :return: filename

        :rtype: str
        """
        return 'macros.kiwi-image-config'

    @staticmethod
    def get_default_packager_tool(package_manager):
        """
        Provides the packager tool according to the package manager

        :param string package_manager: package manger name

        :return: packager tool binary name

        :rtype: str
        """
        rpm_based = ['zypper', 'yum', 'dnf']
        deb_based = ['apt-get']
        if package_manager in rpm_based:
            return 'rpm'
        elif package_manager in deb_based:
            return 'dpkg'

    def get(self, key):
        """
        Implements get method for profile elements

        :param string key: profile keyname

        :return: key value

        :rtype: str
        """
        if key in self.defaults:
            return self.defaults[key]

    def to_profile(self, profile):
        """
        Implements method to add list of profile keys and their values
        to the specified instance of a Profile class

        :param object profile: Profile instance
        """
        for key in sorted(self.profile_key_list):
            # Do not apply default values to any variable that was
            # already defined in the profile instance.
            cur_profile = profile.dot_profile
            if key not in cur_profile or cur_profile[key] is None:
                profile.add(key, self.get(key))
