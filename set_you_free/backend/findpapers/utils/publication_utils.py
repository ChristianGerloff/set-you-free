from urllib.parse import urlparse

from set_you_free.backend.findpapers.data.predatory_data import (
    POTENTIAL_PREDATORY_JOURNALS,
    POTENTIAL_PREDATORY_PUBLISHERS,
)

POTENTIAL_PREDATORY_PUBLISHERS_HOSTS: set[str] = {
    urlparse(x.get("url")).netloc.replace("www.", "") for x in POTENTIAL_PREDATORY_PUBLISHERS
}
POTENTIAL_PREDATORY_PUBLISHERS_NAMES: set[str] = {x.get("name").lower() for x in POTENTIAL_PREDATORY_PUBLISHERS}
POTENTIAL_PREDATORY_JOURNALS_URLS: set[str] = {x.get("url") for x in POTENTIAL_PREDATORY_JOURNALS}
POTENTIAL_PREDATORY_JOURNALS_NAMES: set[str] = {x.get("name").lower() for x in POTENTIAL_PREDATORY_JOURNALS}
