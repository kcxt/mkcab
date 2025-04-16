# mkcab

Build .cab archives for U-Boot releases for Qualcomm boards.

## Install

Simplest is to just do:

```sh
pipx install --editable .
```

Then you can hack on the script and not worry about anything.

## Usage

```txt
usage: mkcab [-h] uboot guid codename model version

Create a CAB file for U-Boot firmware with dynamic GUIDs.

positional arguments:
  uboot       Path to U-Boot binary
  guid        GUID for the firmware
  codename    Board codename (should match base compatible with the vendor prefix removed)
  model       Model name
  version     Release version

options:
  -h, --help  show this help message and exit
```

Compile U-Boot following the board specific instructions, and pack it
into whatever format is needed (e.g. signed MBN or Android boot image).

Determine the capsule UUID used for your board with:

```sh
$ .output/tools/mkeficapsule guidgen .output/dts/upstream/src/arm64/qcom/qcs6490-rb3gen2.dtb UBOOT_UEFI_PARTITION
Generating GUIDs for qcom,qcs6490-rb3gen2 with namespace 8c9f137e-91dc-427b-b2d6-b420faebaf2a:
UBOOT_UEFI_PARTITION: FDA31DED-6E9C-5C44-BE37-B46994BEB543
```

Update the path to be the DTB used by your board, the last parameter is
the fw_image identifier, it must be one of:

* `UBOOT_UEFI_PARTITION` - for rb3g2 and other boards which have U-Boot
  on the "uefi" partition
* `UBOOT_XBL_PARTITION` - for boards with U-Boot embedded into the XBL
  elf
* `UBOOT_BOOT_PARTITION` - for boards that chainload U-Boot via the
  Android bootloader

Then build the capsule using `mkeficapsule` again, for the rb3gen2 this
is:

```sh
$ .output/tools/mkeficapsule -g FDA31DED-6E9C-5C44-BE37-B46994BEB543 -i 1 u-boot.mbn rb3g2-uboot.capsule
```

Use the appropriate input file for your board (be it mbn, android boot
image, whatever) and the GUID you generated.

Finally, we can embed this all into a LVFS compatible .cab file with:

```sh
$ mkcab rb3g2-uboot.capsule FDA31DED-6E9C-5C44-BE37-B46994BEB543 qcs6490-rb3gen2 "RB3 Gen 2" 2025.04-1
Created u-boot-qcs6490-rb3gen2.cab
```

