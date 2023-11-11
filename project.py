import sys
import argparse
import csv
import re
from resource import Resource
from datetime import datetime

# Define a list of CSV headers.
CSV_HEADERS = ["URL", "Domain", "Type", "Tag", "Error"]

# Define a parser for command-line arguments.
parser = argparse.ArgumentParser(
    description="Tool parses valid HTML resources, identifies links to internal or external resources, and captures response headers in a CSV file."
)


def main():
    """
    The main entry point of the program.
    This function parses command-line arguments, processes URLs, and generates a CSV file.
    """
    start_time = datetime.now()
    init_argv()
    urls = get_urls(parser.parse_args().resource)
    file = get_file_name(parser.parse_args().file_name)
    headers = allowed_headers(parser.parse_args().response_headers)
    tags = get_tags(parser.parse_args().tags)
    flag = get_flag(parser.parse_args().enable_external_link_processing)
    data = get_response_data(urls, headers, tags, flag)
    write_to_csv(data, file, headers)
    td = datetime.now() - start_time
    print(f"[INFO] Overall execution time [{get_readable_time(td)}]")


def get_response_data(urls, headers, tags, flag):
    """
    Retrieve response data for the provided URLs.
    This function processes each URL, extracts information, and updates the data list.

    Args:
    urls (list): A list of URLs to process.
    headers (list): A list of response headers to include in the CSV.
    tags (list): A list of HTML tags allowed for parsing.
    flag (bool): A flag to enable or disable external link processing.

    Returns:
    list: A list of dictionaries containing response data.
    """
    data = []
    for url in urls:
        start_time = datetime.now()
        print(f"***Processing [{url}] with args [{parser.parse_args()}]")
        r = Resource(
            path=url,
            allowed_headers=headers,
            enable_external_link_processing=flag,
            process_src=True,
            allowed_tags=tags,
        )
        if r.children:
            # Iterate through valid references and extract data
            print("***Update CSV with valid references")
            for nr in r.children:
                valid_link = Resource(
                    path=nr["link"],
                    allowed_headers=headers,
                    enable_external_link_processing=flag,
                    process_src=False,
                    allowed_tags=tags,
                )
                update_data(valid_link, tag="", data=data)
        if r.children_invalid:
            # Iterate through invalid references and extract data
            print("***Update CSV with invalid resources")
            for bnr in r.children_invalid:
                invalid_resource = Resource(
                    path=bnr["link"],
                    allowed_headers=headers,
                    enable_external_link_processing=flag,
                    process_src=False,
                    allowed_tags=tags,
                )
                # Add source tag information only if the links are invalid or not processed
                update_data(invalid_resource, bnr["tag"], data=data)
        if not r.children and not r.children_invalid:
            # Network resources are blank if the page doesn't exist or the domain is invalid
            update_data(resource=r, tag="", data=data)
        td = datetime.now() - start_time
        print(
            f"[INFO] Time to parse and generate CSV for [{url}] is [{get_readable_time(td)}]"
        )
    return data


def get_readable_time(delta):
    """
    Format a timedelta into a human-readable string.

    Args:
    delta (timedelta): A time duration.

    Returns:
    str: A human-readable time string.
    """
    return f"{delta.days} hr, {delta.seconds} sec, {delta.microseconds} µs"


def write_to_csv(data, file, headers):
    """
    Write data to a CSV file.

    Args:
    data (list): A list of dictionaries containing response data.
    file (str): The name of the CSV file to write.
    headers (list): A list of response headers to include in the CSV.
    """
    with open(file, "w", newline="", encoding="utf-8") as csvfile:
        csv_field_names = []
        csv_field_names.append(CSV_HEADERS[0])
        csv_field_names.append(CSV_HEADERS[1])
        csv_field_names.append(CSV_HEADERS[2])
        csv_field_names.extend(headers)
        csv_field_names.append(CSV_HEADERS[3])
        csv_field_names.append(CSV_HEADERS[4])
        writer = csv.DictWriter(csvfile, fieldnames=csv_field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def update_data(resource, tag, data):
    """
    Update the data list with resource information.

    Args:
    resource (Resource): The resource object containing information to be added to the data list.
    tag (str): The HTML tag associated with the resource.
    data (list): A list of dictionaries containing response data.
    """
    print(f"Updating the CSV with resource [{resource.path}]")
    entry = {}
    response_headers = resource.filtered_headers
    entry[CSV_HEADERS[0]] = resource.path
    entry[CSV_HEADERS[1]] = resource.domain
    entry[CSV_HEADERS[2]] = resource.type
    if response_headers:
        entry.update(response_headers)
    entry[CSV_HEADERS[3]] = tag
    entry[CSV_HEADERS[4]] = resource.error
    data.append(entry)


def get_file_name(name):
    """
    Get a valid CSV file name.

    Args:
    name (str): The provided file name.

    Returns:
    str: A valid CSV file name with a timestamp.
    """
    if matches := re.match(r"([\w-]{1,12})(.csv)", name):
        time = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{matches.group(1)}-{time}{matches.group(2)}"
    else:
        sys.exit(
            "Invalid CSV file name. Make sure the file name does not exceed 12 characters, excluding the extension."
        )


def get_urls(urls):
    """
    Get valid URLs from the provided list.

    Args:
    urls (list): A list of URLs.

    Returns:
    list: A list of valid URLs.
    """
    valid_urls = []
    if urls:
        for url in urls:
            if not Resource.is_valid_url(url):
                print(f"Invalid URL [{url}]")
            else:
                valid_urls.append(url)
    else:
        sys.exit(f"Invalid URL/s [{urls}]")
    return valid_urls


def get_tags(tags):
    """
    Get a list of HTML tags allowed for parsing.

    Args:
    tags (list): A list of HTML tags.

    Returns:
    list: A list of allowed HTML tags.
    """
    return tags


def get_flag(flag):
    """
    Get a boolean flag based on user input.

    Args:
    flag (str): The user input flag ('y' or 'n').

    Returns:
    bool: True if 'y', False if 'n'.
    """
    if flag == "y":
        return True
    else:
        return False


def allowed_headers(headers):
    """
    Get a list of allowed response headers.

    Args:
    headers (list): A list of response headers.

    Returns:
    list: A list of allowed response headers.
    """
    return headers


def init_argv():
    """
    Initialize command-line arguments and parse them.
    """
    parser.add_argument(
        "-r",
        "--resource",
        nargs="*",
        required=True,
        metavar="https://www.example.com, https://www.example1.com",
        help="Input URL/s to parse and generate a CSV with headers. Note: Values to be space-separated, if required values to be enclosed in quotes.",
    )
    parser.add_argument(
        "-rh",
        "--response_headers",
        nargs="*",
        metavar="Cache-Control, Pragma",
        help="Input response headers to include in the CSV.",
        default=["Cache-Control", "Pragma"],
    )
    parser.add_argument(
        "-fn",
        "--file_name",
        metavar="header.csv",
        help="CSV file name. Note: generated CSV file name will have a timestamp along with the provided file name.",
        default="headers.csv",
    )
    parser.add_argument(
        "-e",
        "--enable_external_link_processing",
        metavar="n",
        choices=["y", "n"],
        help="Enable/Disable external link processing, 'y' to enable and 'n' to disable. By default, external links will not be listed in the generated CSV.",
        default="n",
    )
    parser.add_argument(
        "-t",
        "--tags",
        metavar="img, source",
        nargs="*",
        choices=["a", "link", "script", "source", "img"],
        help="HTML tags allowed to parse in the HTML document. Note: Values to be space-separated, if required values to be enclosed in quotes.",
        default=["a", "link", "script", "source", "img"],
    )


if __name__ == "__main__":
    main()
