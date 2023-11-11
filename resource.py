import urllib.request as request
import validators
from urllib.parse import urlparse
from bs4 import BeautifulSoup as BS
from resourcetype import ResourceType
from refprocessor import RefProcessor as RP


class Resource:
    """
    A class for processing and analyzing web resources.

    The Resource class is designed to represent web resources and perform various operations on them, such as fetching
    the resource content, processing links, and extracting headers.

    Args:
        path (str): The URL or path to the web resource.
        allowed_headers (list, optional): A list of allowed HTTP headers to extract. Default is ["Cache-Control", "Pragma"].
        enable_external_link_processing (bool, optional): A flag indicating whether to process external links. Default is False.
        process_src (bool, optional): A flag indicating whether to fetch the resource content. Default is True.
        allowed_tags (list, optional): A list of HTML tags to consider when processing network resources. Default is ["img", "source"].

    Attributes:
        path (str): The URL or path of the web resource.
        children (list): List of valid child resources found within the web resource.
        children_invalid (list): List of invalid or unsupported child resources.
        type (str): The type of the web resource (e.g., "Page", "Image").
        error (str): Any error messages related to the resource.
        src (bytes): The content of the web resource.
        url_root (str): The root URL of the web resource.
        domain (str): The domain of the web resource.
        allowed_headers (list): A list of allowed HTTP headers to extract.
        allowed_tags (list): A list of HTML tags considered when processing network resources.
        filtered_headers (dict): Filtered HTTP headers of the resource.
        enable_external_link_processing (bool): Flag indicating whether to process external links.
        process_src (bool): Flag indicating whether to fetch the resource content.

    Methods:
        __init__(self, path, allowed_headers, enable_external_link_processing, process_src, allowed_tags): Constructor for Resource class.
        _network_resources(self): Extract and process child resources within the web resource.
        _url_root(self): Extract the root URL of the web resource.
        _domain_name(self): Extract the domain name of the web resource.
        _filter_headers(self): Filter and extract allowed HTTP headers.
        is_valid_url(cls, url): Check if a URL is valid.
        is_external_link(cls, reference, url_root): Check if a reference is an external link.
        get_url_root(cls, url): Extract the root URL from a given URL.

    Examples:
        To process a web resource and extract child resources:
        >>> resource = Resource("https://example.com/page.html")
        >>> print(resource.path)
        "https://example.com/page.html"
    """

    def __init__(
        self,
        path,
        allowed_headers=["Cache-Control", "Pragma"],
        enable_external_link_processing=False,
        process_src=True,
        allowed_tags=["img", "source"],
    ):
        """
        Initialize a Resource object with the provided parameters.

        Args:
            path (str): The URL or path of the web resource.
            allowed_headers (list, optional): A list of allowed HTTP headers to extract. Default is ["Cache-Control", "Pragma"].
            enable_external_link_processing (bool, optional): A flag indicating whether to process external links. Default is False.
            process_src (bool, optional): A flag indicating whether to fetch the resource content. Default is True.
            allowed_tags (list, optional): A list of HTML tags to consider when processing network resources. Default is ["img", "source"].
        """
        self.path = path.strip()
        self.children = []
        self.children_invalid = []
        self.type = ResourceType.find(path).value
        self.error = ""
        self.src = ""
        self.url_root = ""
        self.domain = ""
        self.allowed_headers = allowed_headers
        self.allowed_tags = allowed_tags
        self.filtered_headers = {}
        self.enable_external_link_processing = enable_external_link_processing
        self.process_src = process_src
        # Save network resources by pre url pattern check
        if self.is_valid_url(path):
            self.url_root = self._url_root()
            self.domain = self._domain_name()
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
                    "sec-ch-ua": '"Google Chrome";v="112", " Not;A Brand";v="99", "Chromium";v="112"',
                    "referer": self.url_root,
                }
                r = request.Request(self.path, headers=headers)
                with request.urlopen(r) as response:
                    if response.status == 200:
                        self.headers = response.headers
                        self.filtered_headers = self._filter_headers()
                        if process_src:
                            self.src = response.read()
                            self._network_resources()
                    else:
                        raise Exception(f"HTTP status code is [{response.status}]")
            except Exception as e:
                # Catching exception is intentional; it is not to interrupt the resource processing for any reason
                self.error = e
                print(f"[ERROR] Invalid resource [{path}]", e)
                pass
        else:
            self.error = "Non-parsable URL"
            print(f"[ERROR] {self.error} [{path}]")

    def _network_resources(self):
        """
        Extract and process child resources within the web resource.

        This method extracts and processes child resources such as images, links, and other content
        within the web resource.
        """
        try:
            if self.type in [ResourceType.PAGE.value, ResourceType.NO_EXTENSION.value]:
                soup = BS(self.src, "html.parser")
                list = []
                bad_links = []
                for tag in soup.find_all(self.allowed_tags):
                    link = ""
                    match (tag.name):
                        case "a" | "link":
                            link = tag.get("href")
                        case "img" | "script":
                            link = tag.get("src")
                        case "source":
                            link = tag.get("srcset")
                        case _:
                            print(f"tag {tag.name} didn't match any case")
                    rp = RP(self, link)
                    if rp.link:
                        is_external_link = self.is_external_link(
                            reference=rp.link, url_root=self.url_root
                        )
                        if (
                            is_external_link
                            and not self.enable_external_link_processing
                        ):
                            # Handle external links according to your logic
                            ...
                        else:
                            list.append(
                                {
                                    "link": rp.link,
                                    "tag": str(tag),
                                    "is_external_link": is_external_link,
                                }
                            )
                    else:
                        is_external_link = self.is_external_link(
                            reference=rp.bad_link, url_root=self.url_root
                        )
                        if (
                            is_external_link
                            and not self.enable_external_link_processing
                        ):
                            # Handle external links according to your logic
                            ...
                        else:
                            bad_links.append(
                                {
                                    "link": rp.bad_link,
                                    "tag": str(tag),
                                    "is_external_link": is_external_link,
                                }
                            )
                self.children = list
                self.children_invalid = bad_links
            else:
                print(
                    f"[ERROR] Not parsing the resource. URL [{self.path}] is not a page."
                )
        except AssertionError as e:
            print(f"[ERROR] Processing the path [{self.path}] failed, [{e}]")

    def _url_root(self):
        """
        Extract the root URL of the web resource.

        Returns:
            str: The root URL of the web resource.
        """
        return self.get_url_root(self.path)

    def _domain_name(self):
        """
        Extract the domain name of the web resource.

        Returns:
            str: The domain name of the web resource.
        """
        url = urlparse(self.path)
        if url.netloc:
            return url.netloc.removeprefix("www.")

    def _filter_headers(self):
        """
        Filter and extract allowed HTTP headers.

        Returns:
            dict: Filtered HTTP headers of the resource.
        """
        if hasattr(self, "headers"):
            headers = self.headers
            return {key: headers[key] for key in self.allowed_headers if headers[key]}

    @classmethod
    def is_valid_url(cls, url):
        """
        Check if a URL is valid.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        return validators.url(url)

    @classmethod
    def is_external_link(cls, reference, url_root):
        """
        Check if a reference is an external link.

        Args:
            reference (str): The reference URL to check.
            url_root (str): The root URL of the web resource.

        Returns:
            bool: True if the reference is an external link, False otherwise.
        """
        if Resource.is_valid_url(reference):
            if not url_root == Resource.get_url_root(reference):
                return True
            else:
                return False

    @classmethod
    def get_url_root(cls, url):
        """
        Extract the root URL from a given URL.

        Args:
            url (str): The URL to extract the root URL from.

        Returns:
            str: The root URL of the provided URL.
        """
        url = urlparse(url)
        if url.netloc:
            return f"{url.scheme}://{url.netloc}"
