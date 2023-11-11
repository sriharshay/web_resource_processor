# Web Resource Processing Tool
#### Video Demo:  https://www.youtube.com/watch?v=Kg82y4rxF-k
#### This Python script is a tool for parsing valid HTML resources, identifying links to internal or external resources, and capturing response headers in a CSV file.

## Command-Line Usage

To use this tool, you can provide the following command-line arguments:

- `-r, --resource`: Input URL/s to parse and generate a CSV with response headers.
- `-rh, --response_headers`: Input response headers to include in the CSV.
- `-fn, --file_name`: CSV file name. The generated CSV file name will have a timestamp along with the provided file name.
- `-e, --enable_external_link_processing`: Enable/Disable external link processing ('y' to enable, 'n' to disable). By default, external links are not listed in the generated CSV.
- `-t, --tags`: HTML tags allowed to parse in the HTML document. By default a, link, source, img, script tags are supported.

**Example**:

To generate a CSV file with response headers:

    python project.py -r https://www.example.com -rh "Cache-Control" "Content-Length" -fn output.csv -e y -t img script

## Web Resource Processor [Script 1: project.py](project.py)

The `main` function is the entry point of the script and is responsible for parsing command-line arguments, fetching resources, processing them, and generating a CSV file containing response headers.

## [Script 2: resource.py](resource.py)

The `Resource` class represents web resources and performs various operations on them. It has attributes and methods for processing, analyzing, and fetching web resources.

## [Script 3: refprocessor.py](refprocessor.py)

The `RefProcessor` class is a utility class for processing and normalizing references within web resources. It can normalize relative links, handle external links, and identify bad or unsupported links.

## [Script 4: resourcetype.py](resourcetype.py)

The `ResourceType` enum represents different types of web resources, such as web pages, images, stylesheets, and JavaScript files. It is used to classify resources based on their file extensions.

## [Script 5: test_project.py](test_project.py)

This make sure to perform basic CLI augument validation
