#!/usr/bin/python
import re
import argparse
import pathlib as pt
import fontforge as ff

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--dry-run", action="store_true", help="don't generate new files"
)
parser.add_argument(
    "-g", "--glob", default="*.ttf", help="glob string to search for font files"
)
parser.add_argument("-f", "--family", default=None, help="specify custom family name")
parser.add_argument(
    "-r",
    "--replace",
    action="extend",
    nargs=2,
    default=[r"\.bak|-[oO][lL][dD]", ""],
    help="regex for matching parts of the original filename and a replacement",
)

args = parser.parse_args()
fonts = []
outfile_search = args.replace[0] if len(args.replace) < 3 else args.replace[2]
outfile_replace = args.replace[1] if len(args.replace) < 3 else args.replace[3]
re_file = re.compile(outfile_search)
re_clear = re.compile(r"\s?(NFP|Nerd Font ((Complete )?Mono|Propo)|NerdFontComplete)")
re_family = re.compile(
    r"\s*(-|Semi|Thin|Bold|Italic|Regular|Normal|Light|Extra|Medium)\s*"
)

for path in pt.Path(".").glob(args.glob):
    file = str(path)
    fonts.append((file, ff.open(file)))

print("\n" * 100)


def clear(value: str, family: bool = False) -> str:
    if family:
        return re_family.sub("", re_clear.sub("", value))
    else:
        return re_clear.sub("", value)


for file, font in fonts:
    output = re_file.sub(outfile_replace, file)
    print(f'\nfile: "{file}" -> "{output}"')

    _family = f'"{font.familyname}"'
    _font = f'"{font.fontname}"'
    _full = f'"{font.fullname}"'

    if args.family is None:
        font.familyname = clear(font.familyname, True)
        font.fontname = clear(font.fontname)
        font.fullname = clear(font.fullname)

    else:
        source_family = font.familyname
        font.familyname = args.family
        font.fontname = clear(font.fontname).replace(source_family, font.familyname)
        font.fullname = clear(font.fullname).replace(source_family, font.familyname)

    font.comment = ""

    _names_bef = [
        (k.lower().replace(" ", "_") + ":", f'"{v}"')
        for (_, k, v) in font.sfnt_names
        if k in ("Preferred Family", "Compatible Full")
    ]
    font.appendSFNTName("English (US)", "Preferred Family", font.familyname)
    font.appendSFNTName("English (US)", "Compatible Full", font.fullname)
    _names_aft = [
        f'"{v}"'
        for (_, k, v) in font.sfnt_names
        if k in ("Preferred Family", "Compatible Full")
    ]

    print(f'    {"family:": <18} {_family: >65} -> "{font.familyname}"')
    print(f'    {"font:": <18} {_font: >65} -> "{font.fontname}"')
    print(f'    {"full:": <18} {_full: >65} -> "{font.fullname}"')

    for idx in range(len(_names_bef)):
        print(
            f"    {_names_bef[idx][0]: <18} {_names_bef[idx][1]: >65} -> {_names_aft[idx]}"
        )

    if not args.dry_run:
        font.generate(output)
