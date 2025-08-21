from pathlib import Path

from bs4 import BeautifulSoup

from kextinfo import kext_stat

ROOT_PATH = Path(__file__).parent


def main():
    stats = kext_stat()
    stats_lookup = {}
    for stat in stats:
        stats_lookup[stat.index] = stat

    document = BeautifulSoup(
        """<!DOCTYPE html>
<html lang="en">
    <meta charset="UTF-8" />
    <title>kextstat :3</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <link rel="stylesheet" href="shiny.css" />
<head>
</head>
<body>
</body>""",
        "html.parser"
    )

    def new_el(name: str, contents=None, attrs=None):
        el = document.new_tag(name=name, attrs=attrs or {})
        if contents:
            el.string = str(contents)
        return el

    body = document.find("body")
    table = document.new_tag("table")

    thead = document.new_tag("thead")
    tr = document.new_tag("tr")
    for val in ["index", "version", "name", "refs", "address", "size", "wired", "uuid", "linked against", "linked by"]:
        tr.append(new_el("th", val))
    thead.append(tr)
    table.append(thead)

    tbody = document.new_tag("tbody")
    for stat_row in stats:
        tr = document.new_tag("tr", attrs={"id": f"stat-{stat_row.index}"})

        # index:
        tr.append(new_el("td", stat_row.index, attrs={"class": "cell-index"}))
        # version:
        tr.append(new_el("td", stat_row.version, attrs={"class": "cell-version"}))
        # name:
        tr.append(new_el("td", stat_row.name, attrs={"class": "cell-name"}))
        # refs:
        tr.append(new_el("td", stat_row.refs, attrs={"class": "cell-refs"}))
        # address:
        tr.append(new_el("td", f"0x{stat_row.address:016x}", attrs={"class": "cell-address"}))
        # size:
        tr.append(new_el("td", f"0x{stat_row.size:x}", attrs={"class": "cell-size"}))
        # wired:
        tr.append(new_el("td", f"0x{stat_row.wired:x}", attrs={"class": "cell-wired"}))
        # uuid:
        tr.append(new_el("td", f"{stat_row.uuid}", attrs={"class": "cell-uuid"}))
        # linked against:
        td = document.new_tag("td", attrs={"class": "cell-linked-against"})
        if len(stat_row.linked_against) > 0:
            details = new_el("details")
            details.append(new_el("summary", f"{len(stat_row.linked_against):,} items"))
            ul = new_el("ul")
            for i, linked_index in enumerate(stat_row.linked_against):
                linked_stat = stats_lookup[linked_index]
                li = new_el("li")
                li.append(new_el("a", f"{linked_index}: {linked_stat.name}", attrs={"href": f"#stat-{linked_index}"}))
                ul.append(li)
            details.append(ul)
            td.append(details)
        else:
            td.append("none")
        tr.append(td)

        # linked by:
        rows_linked_by = [new_stat_row for new_stat_row in stats if stat_row.index in new_stat_row.linked_against]
        td = document.new_tag("td", attrs={"class": "cell-linked-by"})
        if len(rows_linked_by) > 0:
            details = new_el("details")
            details.append(new_el("summary", f"{len(rows_linked_by):,} items"))
            ul = new_el("ul")
            for i, linked_stat in enumerate(rows_linked_by):
                li = new_el("li")
                li.append(new_el("a", f"{linked_stat.index}: {linked_stat.name}", attrs={"href": f"#stat-{linked_stat.index}"}))
                ul.append(li)
            details.append(ul)
            td.append(details)
        else:
            td.append("none")
        tr.append(td)

        tbody.append(tr)

    table.append(tbody)
    body.append(table)

    with open(ROOT_PATH / "output.html", "w", encoding="utf-8") as stream:
        stream.write(str(document))


if __name__ == '__main__':
    main()
