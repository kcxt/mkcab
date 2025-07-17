import jinja2
import cabarchive
import sys
import argparse
import time
from pathlib import Path

metainfo_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2024 Linaro Ltd.
     Author: Caleb Connolly <caleb.connolly@linaro.org> -->
<component type="firmware">
  <id>org.linaro.u-boot.qcom.{{ codename }}.firmware</id>
  <name>U-Boot {{ codename }}</name>
  <name_variant_suffix>U-Boot for {{ model }}</name_variant_suffix>
  <summary>Qualcomm {{ model }} U-Boot</summary>
  <description>
    <p>
    </p>
  </description>
  <provides>
    <firmware type="flashed">{{ guid }}</firmware>
  </provides>
  <url type="homepage">https://git.codelinaro.org/linaro/qcomlt/u-boot</url>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-2.0</project_license>
  <releases>
    <release urgency="medium" version="{{ version }}" date="{{ date }}" install_duration="120">
      <checksum filename="firmware.bin" target="content"/>
    </release>
  </releases>
  <custom>
    <value key="LVFS::VersionFormat">number</value>
    <value key="LVFS::UpdateProtocol">org.uefi.capsule</value>
  </custom>
  <keywords>
    <keyword>uefi</keyword>
    <keyword>u-boot</keyword>
    <keyword>bootloader</keyword>
  </keywords>
</component>
"""

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a CAB file for U-Boot firmware with dynamic GUIDs.")
    parser.add_argument("uboot", type=str, help="Path to U-Boot binary")
    parser.add_argument("guid", type=str, help="GUID for the firmware")
    parser.add_argument("codename", type=str, help="Board codename (should match base compatible with the vendor prefix removed)")
    parser.add_argument("model", type=str, help="Model name")
    parser.add_argument("version", type=str, help="Release version")
    return parser.parse_args()

def main():
    args = parse_args()
    guid = args.guid.lower()
    if len(guid) != 36:
        print(f"Invalid GUID: {guid}. Must be 36 characters long.")
        sys.exit(1)
    if not Path(args.uboot).is_file():
        print(f"U-Boot binary not found: {args.uboot}")
        sys.exit(1)

    # Create the metainfo.xml file
    template = jinja2.Template(metainfo_template)
    metainfo = template.render(
        codename=args.codename,
        model=args.model,
        guid=guid,
        version=args.version,
        date=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    )
    # print(metainfo)

    arc = cabarchive.CabArchive()
    arc[f"firmware.bin"] = cabarchive.CabFile(open(args.uboot, "rb").read())
    arc[f"firmware.metainfo.xml"] = cabarchive.CabFile(metainfo.encode())

    with open(f"u-boot-{args.codename}.cab", "wb") as f:
        f.write(arc.save())

    print(f"Created u-boot-{args.codename}.cab")
