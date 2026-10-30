import json

def write_json_report(page_data, filename="report.json"):
    # Sort the pages
    pages = sorted(page_data.values(), key=lambda p: p["url"])
    print(f"pages: {pages}\n")

    # Open the output file and write json
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(pages, file, indent=2)

    return