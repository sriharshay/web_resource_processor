import re
from urllib.parse import urlparse
from pathlib import PurePosixPath


class RefProcessor:
    """
    A utility class for processing and normalizing references within web resources.

    The RefProcessor class is designed to process various types of references found within web resources.
    It can normalize relative links, handle external links, and identify bad or unsupported links.

    Args:
        resource (Resource): The resource object representing the web page.
        reference (str): The reference to be processed.

    Attributes:
        link (str): The processed and normalized reference link.
        bad_link (str): A string for storing bad or unsupported links.
        enable_external_link_processing (bool): A flag indicating whether external link processing is enabled.

    Methods:
        __init__(self, resource, reference): Constructor for RefProcessor class.
        _relative_path(self, resource, reference, matches): Internal method to process relative paths.

    Examples:
        To process a reference within a web resource:
        >>> resource = Resource(...)
        >>> reference = "/path/to/some/resource"
        >>> processor = RefProcessor(resource, reference)
        >>> print(processor.link)
        "/path/to/some/resource"
    """

    def __init__(self, resource, reference):
        """
        Initialize the RefProcessor with a resource and a reference.

        Args:
            resource (Resource): The resource object representing the web page.
            reference (str): The reference to be processed.
        """
        self.link = ""
        self.bad_link = ""
        self.enable_external_link_processing = resource.enable_external_link_processing
        if reference:
            if resource.url_root == resource.get_url_root(reference):
                # Reference that has the same domain as the page
                self.link = reference
            elif self.enable_external_link_processing and re.match(
                r"(^//[.]*.+)", reference
            ):
                # Reference that starts with '//' - External link but within the same org. Ex://en.wikipedia.org/
                self.link = f"https:{reference}"
            elif re.match(r"(^/[^/][.]*.*)", reference):
                # Reference that starts with '/' but not '//'
                self.link = f"{resource.url_root}{reference}"
            elif matches := re.match(r"(^\.\./)\1*", reference):
                # Reference that starts with '../' pattern and/or repeats itself
                self.link = self._relative_path(resource, reference, matches)
            elif re.match(r"^(#|tel:|javascript:void)", reference):
                # Reference that starts with # or tel: or javascript:void
                self.link = reference
            elif (
                not reference.startswith("/")
                and "/" in reference
                and "://" not in reference
            ):
                # References that are relative from the current page and not an absolute URL
                self.link = f"{resource.path}{reference}"
            elif self.enable_external_link_processing:
                # If external link processing is enabled, treat them as valid links
                self.link = reference
            else:
                # All other reference patterns are invalid or bad links
                print(f"No parsing logic for [{reference}]")
                self.bad_link = reference

    def _relative_path(self, resource, reference, matches):
        """
        Process relative paths within the web resource.

        Args:
            resource (Resource): The resource object representing the web page.
            reference (str): The reference to be processed.
            matches (re.Match): A regular expression match object for '../' patterns.

        Returns:
            str: The processed relative reference.
        """
        dd_path = matches.group()
        relative_path = reference.replace(dd_path, "")
        prefix_path = urlparse(resource.path).path
        while True:
            if "../" in dd_path:
                dd_path = dd_path.removeprefix("../")
                prefix_path = PurePosixPath(prefix_path).parent
            else:
                break
        return f"{resource.url_root}{prefix_path.joinpath(relative_path)}"
