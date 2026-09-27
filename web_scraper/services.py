import os
import re
import json

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient

from urllib.parse import (
    urljoin,
    urlparse,
    unquote,
)


load_dotenv()


# =========================================================
# REGEX
# =========================================================

EMAIL_REGEX = (
    r"[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

PHONE_REGEX = (
    r"(?:\+91[\s-]?)?"
    r"(?:[6-9]\d{9})"
)


# =========================================================
# SOCIAL DOMAINS
# =========================================================

SOCIAL_DOMAINS = {
    "instagram": "instagram.com",
    "facebook": "facebook.com",
    "linkedin": "linkedin.com",
}


SOCIAL_ONLY_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "linkedin.com",
]


# =========================================================
# THIRD PARTY / LISTING DOMAINS
# =========================================================

LISTING_DOMAINS = [
    "justdial.com",
    "sulekha.com",
    "indiamart.com",
    "tradeindia.com",
    "99businessmedia.com",
    "exportersindia.com",
    "yelp.com",
    "tripadvisor.com",
    "yellowpages.com",
    "foursquare.com",
    "clutch.co",
    "designrush.com",
    "crunchbase.com",
    "rocketreach.co",
    "quora.com",

    # Social
    "facebook.com",
    "instagram.com",
    "linkedin.com",

    # Google
    "google.com",
    "google.co.in",
    "google.co.uk",
    "maps.google.com",

    # Video
    "youtube.com",
    "youtu.be",

    # Reddit
    "reddit.com",
]


# =========================================================
# SOURCES THAT MUST NEVER BECOME A BUSINESS
# =========================================================

NON_BUSINESS_SOURCE_DOMAINS = [
    "reddit.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "youtu.be",
    "google.com",
    "google.co.in",
]


# =========================================================
# BAD BUSINESS NAME TERMS
# =========================================================

BAD_NAME_TERMS = [
    "home",
    "homepage",
    "home page",
    "about",
    "about us",
    "contact",
    "contact us",
    "login",
    "sign in",
    "sign up",

    "reddit",
    "facebook",
    "instagram",
    "linkedin",
    "youtube",
    "google",

    "justdial",
    "sulekha",
    "indiamart",
    "tradeindia",
    "exportersindia",

    "search results",
    "results",
    "directory",
    "directories",
    "business directory",
    "company list",
    "business list",
    "category",
    "categories",
    "service providers",
    "service provider",
    "official website",

    "logo",
    "buyer icon",
    "reel",
    "video",
    "watch",
    "this is why",
    "why noida",
    "premium crowd",

    "top salon services at home",
    "salon services at home",
    "salon services",
    "salons in noida",
    "salon in noida",
    "hair salons in noida",
    "beauty salons in noida",
]


# =========================================================
# BLOCKED ARTICLE / LISTICLE TERMS
# =========================================================

BLOCKED_RESULT_WORDS = [
    "directory",
    "ranking",
    "company list",
    "business list",
    "service providers",
    "semrush",
    "clutch",
]


# =========================================================
# HTTP
# =========================================================

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0 Safari/537.36"
    )
}


# =========================================================
# PROGRESS CALLBACK
# =========================================================

def report_progress(
    progress_callback,
    stage,
    current=0,
    total=0,
    message=""
):

    if not progress_callback:
        return

    try:

        progress_callback(
            stage=stage,
            current=current,
            total=total,
            message=message,
        )

    except Exception:

        # Progress must never break scraping.
        pass


# =========================================================
# TEXT
# =========================================================

def clean_text(text):

    if not text:
        return ""

    return " ".join(
        str(text).split()
    )


# =========================================================
# URL
# =========================================================

def normalize_url(url):

    if not url:
        return ""

    url = str(url).strip()

    if not url:
        return ""

    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    return url.rstrip("/")


def get_domain(url):

    if not url:
        return ""

    try:

        parsed = urlparse(
            url
        )

        domain = parsed.netloc.lower()

        domain = domain.replace(
            "www.",
            ""
        )

        domain = domain.split(
            ":",
            1
        )[0]

        return domain

    except Exception:

        return ""


def domain_matches(
    domain,
    target
):

    if not domain or not target:
        return False

    return (
        domain == target
        or domain.endswith(
            "." + target
        )
    )


# =========================================================
# URL TYPE
# =========================================================

def is_social_url(url):

    domain = get_domain(
        url
    )

    if not domain:
        return False

    return any(
        domain_matches(
            domain,
            social_domain
        )
        for social_domain in SOCIAL_ONLY_DOMAINS
    )


def is_third_party_url(url):

    domain = get_domain(
        url
    )

    if not domain:
        return True

    return any(
        domain_matches(
            domain,
            listing_domain
        )
        for listing_domain in LISTING_DOMAINS
    )


def is_non_business_source(url):

    domain = get_domain(
        url
    )

    if not domain:
        return True

    return any(
        domain_matches(
            domain,
            item
        )
        for item in NON_BUSINESS_SOURCE_DOMAINS
    )


# =========================================================
# SEARCH QUERY BUILDER
# =========================================================

def build_search_queries(
    context
):

    context = clean_text(
        context
    )

    if not context:
        return []

    queries = [
        context,
        f"{context} nearby",
        f"{context} local businesses",
    ]

    lower_context = context.lower()

    # -----------------------------------------------------
    # Noida / NCR coverage
    # -----------------------------------------------------

    if (
        "noida" in lower_context
        or "greater noida" in lower_context
    ):

        sectors = [
            "Sector 18",
            "Sector 27",
            "Sector 50",
            "Sector 62",
            "Sector 74",
            "Sector 76",
            "Sector 93",
            "Sector 104",
            "Sector 120",
            "Sector 137",
            "Sector 142",
            "Sector 150",
            "Sector 168",
        ]

        for sector in sectors:

            queries.append(
                f"{context} {sector}"
            )

    # -----------------------------------------------------
    # Salon-specific variations
    # -----------------------------------------------------

    if "salon" in lower_context:

        salon_variations = [
            f"hair salon {context}",
            f"beauty salon {context}",
            f"unisex salon {context}",
            f"ladies salon {context}",
            f"hair studio {context}",
            f"beauty studio {context}",
        ]

        queries.extend(
            salon_variations
        )

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    final_queries = []

    seen = set()

    for query in queries:

        query = clean_text(
            query
        )

        key = query.lower()

        if not query:
            continue

        if key in seen:
            continue

        seen.add(
            key
        )

        final_queries.append(
            query
        )

    return final_queries


# =========================================================
# GOOGLE PLACES SEARCH
# =========================================================

def search_businesses(
    context,
    max_results=20,
    exclude_place_ids=None,
    progress_callback=None,
):

    api_key = os.getenv(
        "GOOGLE_MAPS_API_KEY"
    )

    if not api_key:

        raise Exception(
            "GOOGLE_MAPS_API_KEY is missing in .env"
        )

    url = (
        "https://places.googleapis.com/v1/"
        "places:searchText"
    )

    headers = {
        "Content-Type": "application/json",

        "X-Goog-Api-Key": api_key,

        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.nationalPhoneNumber,"
            "places.websiteUri,"
            "places.googleMapsUri,"
            "nextPageToken"
        ),
    }

    wanted = max(
        1,
        int(max_results)
    )

    exclude_place_ids = set(
        exclude_place_ids or []
    )

    queries = build_search_queries(
        context
    )

    if not queries:
        return []

    all_places = []

    seen_place_ids = set()

    seen_fallback_keys = set()

    total_queries = len(
        queries
    )

    # =====================================================
    # MULTIPLE GOOGLE QUERIES
    # =====================================================

    for query_index, query in enumerate(
        queries,
        start=1
    ):

        if len(all_places) >= wanted:
            break

        report_progress(
            progress_callback,
            stage="🔎 Searching Google Places...",
            current=len(all_places),
            total=wanted,
            message=(
                f"Query {query_index}/{total_queries}: "
                f"{query}"
            ),
        )

        page_token = None

        # Google Text Search supports pagination.
        # We continue until this query is exhausted
        # or we have enough unique businesses.
        while len(all_places) < wanted:

            remaining = (
                wanted
                - len(all_places)
            )

            payload = {
                "textQuery": query,
                "pageSize": min(
                    20,
                    remaining
                ),
            }

            if page_token:

                payload[
                    "pageToken"
                ] = page_token

            try:

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                )

            except requests.RequestException as error:

                raise Exception(
                    "Google Places request failed: "
                    f"{error}"
                )

            if response.status_code != 200:

                raise Exception(
                    "Google Places API error "
                    f"{response.status_code}: "
                    f"{response.text[:1000]}"
                )

            data = response.json()

            current_places = data.get(
                "places",
                []
            )

            if not current_places:
                break

            for place in current_places:

                # -----------------------------------------
                # Place ID
                # -----------------------------------------

                place_id = clean_text(
                    place.get(
                        "id",
                        ""
                    )
                )

                # -----------------------------------------
                # Existing DB record
                # -----------------------------------------

                if (
                    place_id
                    and place_id in exclude_place_ids
                ):
                    continue

                # -----------------------------------------
                # Duplicate from another query
                # -----------------------------------------

                if place_id:

                    if place_id in seen_place_ids:
                        continue

                    seen_place_ids.add(
                        place_id
                    )

                else:

                    # Fallback for safety.
                    display_name = place.get(
                        "displayName",
                        {}
                    )

                    fallback_name = clean_text(
                        display_name.get(
                            "text",
                            ""
                        )
                    ).lower()

                    fallback_address = clean_text(
                        place.get(
                            "formattedAddress",
                            ""
                        )
                    ).lower()

                    fallback_key = (
                        fallback_name
                        + "|"
                        + fallback_address
                    )

                    if (
                        fallback_key
                        and fallback_key in seen_fallback_keys
                    ):
                        continue

                    if fallback_key:

                        seen_fallback_keys.add(
                            fallback_key
                        )

                all_places.append(
                    place
                )

                report_progress(
                    progress_callback,
                    stage="🔎 Searching Google Places...",
                    current=len(all_places),
                    total=wanted,
                    message=(
                        f"Found {len(all_places)} "
                        f"of {wanted} businesses"
                    ),
                )

                if len(all_places) >= wanted:
                    break

            page_token = data.get(
                "nextPageToken"
            )

            if not page_token:
                break

    return all_places[:wanted]


# =========================================================
# EMAIL VALIDATION
# =========================================================

def is_valid_email(
    email,
    allowed_domain=""
):

    if not email:
        return False

    email = email.strip(
        ".,;:()[]<> "
    ).lower()

    if not re.fullmatch(
        EMAIL_REGEX,
        email
    ):
        return False

    local_part, domain = (
        email.split(
            "@",
            1
        )
    )

    # -----------------------------------------------------
    # Obvious fake / placeholder domains
    # -----------------------------------------------------

    blocked_domains = {
        "example.com",
        "example.org",
        "example.net",
        "company.com",
        "domain.com",
        "email.com",
        "test.com",
        "sentry.io",
        "wixpress.com",
        "semrush.com",
        "wordpress.com",
        "leadiq.com",
    }

    if domain in blocked_domains:
        return False

    # -----------------------------------------------------
    # Obvious placeholder local names
    # -----------------------------------------------------

    blocked_local_parts = {
        "name",
        "firstname",
        "lastname",
        "fname",
        "lname",
        "flast",
        "firstlast",
        "yourname",
        "email",
        "test",
        "example",
        "user",
        "username",
        "admin",
    }

    if local_part in blocked_local_parts:
        return False

    # -----------------------------------------------------
    # Placeholder patterns
    # -----------------------------------------------------

    if (
        local_part.startswith(
            "firstname"
        )
        or local_part.startswith(
            "lastname"
        )
    ):
        return False

    # -----------------------------------------------------
    # If official website domain is known,
    # accept same-domain emails or common mailbox providers.
    # -----------------------------------------------------

    if allowed_domain:

        allowed_domain = (
            allowed_domain.lower()
            .replace("www.", "")
        )

        free_mail_domains = {
            "gmail.com",
            "outlook.com",
            "hotmail.com",
            "yahoo.com",
            "yahoo.co.in",
            "proton.me",
            "protonmail.com",
        }

        if (
            domain != allowed_domain
            and domain not in free_mail_domains
        ):
            return False

    return True


# =========================================================
# EMAIL EXTRACTION
# =========================================================

def extract_email(
    text,
    allowed_domain=""
):

    if not text:
        return ""

    matches = re.findall(
        EMAIL_REGEX,
        text
    )

    for email in matches:

        email = email.strip(
            ".,;:()[]<> "
        )

        if not is_valid_email(
            email,
            allowed_domain=allowed_domain
        ):
            continue

        return email

    return ""


# =========================================================
# PHONE
# =========================================================

def normalize_phone(
    phone
):

    if not phone:
        return ""

    digits = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if (
        len(digits) == 12
        and digits.startswith("91")
    ):

        digits = digits[2:]

    if (
        len(digits) == 10
        and digits[0] in "6789"
    ):
        return digits

    return ""


def extract_phone(
    text
):

    if not text:
        return ""

    matches = re.findall(
        PHONE_REGEX,
        text
    )

    for phone in matches:

        normalized = normalize_phone(
            phone
        )

        if normalized:
            return normalized

    return ""


# =========================================================
# SOCIAL PROFILE VALIDATION
# =========================================================

def is_valid_social_profile(
    platform,
    url
):

    url = normalize_url(
        url
    )

    if not url:
        return False

    if not is_social_url(
        url
    ):
        return False

    parsed = urlparse(
        url
    )

    path = parsed.path.lower().strip(
        "/"
    )

    if not path:
        return False

    # -----------------------------------------------------
    # Universal junk paths
    # -----------------------------------------------------

    blocked_exact = {
        "",
        "login",
        "signup",
        "signin",
        "register",
        "search",
        "explore",
        "watch",
        "share",
        "sharing",
        "sharer",
        "dialog",
        "feed",
        "notifications",
        "settings",
        "admin",
        "dashboard",
        "privacy",
        "terms",
        "help",
    }

    if path in blocked_exact:
        return False

    blocked_fragments = [
        "/share/",
        "/sharing/",
        "/sharer/",
        "/dialog/",
        "/login/",
        "/signup/",
        "/signin/",
        "/search/",
        "/explore/",
        "/watch/",
        "/reel/",
        "/reels/",
        "/video/",
        "/videos/",
        "/hashtag/",
        "/posts/",
        "/p/",
    ]

    for fragment in blocked_fragments:

        if fragment in (
            "/" + path + "/"
        ):

            return False

    # Simpler direct check too.
    for fragment in [
        "sharer",
        "sharing",
        "dialog",
        "login",
        "signup",
        "signin",
        "search",
        "explore",
        "watch",
        "reel",
        "video",
        "hashtag",
    ]:

        if fragment in path:
            return False

    # =====================================================
    # INSTAGRAM
    # =====================================================

    if platform == "instagram":

        reserved = {
            "accounts",
            "about",
            "directory",
            "direct",
            "emails",
            "explore",
            "legal",
            "press",
            "privacy",
            "reels",
            "stories",
            "web",
        }

        first_part = (
            path.split(
                "/",
                1
            )[0]
        )

        if first_part in reserved:
            return False

        # Instagram profile should normally be one segment.
        if "/" in path:
            return False

        return True

    # =====================================================
    # FACEBOOK
    # =====================================================

    if platform == "facebook":

        blocked_starts = (
            "groups/",
            "events/",
            "watch",
            "marketplace",
            "reel/",
            "reels/",
            "stories/",
            "plugins/",
            "hashtag/",
            "gaming/",
            "share/",
        )

        if path.startswith(
            blocked_starts
        ):
            return False

        return True

    # =====================================================
    # LINKEDIN
    # =====================================================

    if platform == "linkedin":

        # IMPORTANT:
        # /in/ = person profile.
        # We only want company/business pages.

        blocked_starts = (
            "in/",
            "pub/",
            "feed/",
            "posts/",
            "pulse/",
            "jobs/",
            "learning/",
            "messaging/",
            "notifications/",
            "admin/",
            "login/",
            "signup/",
            "search/",
            "share/",
            "cws/",
        )

        if path.startswith(
            blocked_starts
        ):
            return False

        # Accept:
        # /company/business-name
        # /showcase/business-name

        if not (
            path.startswith("company/")
            or path.startswith("showcase/")
        ):
            return False

        return True

    return False


# =========================================================
# SOCIAL LINKS
# =========================================================

def extract_social_links(
    soup
):

    socials = {
        "instagram": "",
        "facebook": "",
        "linkedin": "",
    }

    if not soup:
        return socials

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link.get(
            "href",
            ""
        ).strip()

        if not href:
            continue

        href = normalize_url(
            href
        )

        domain = get_domain(
            href
        )

        for platform, social_domain in SOCIAL_DOMAINS.items():

            if not domain_matches(
                domain,
                social_domain
            ):
                continue

            if socials[platform]:
                continue

            if not is_valid_social_profile(
                platform,
                href
            ):
                continue

            socials[platform] = href

    return socials


# =========================================================
# FETCH PAGE
# =========================================================

def get_page_content(
    url
):

    try:

        url = normalize_url(
            url
        )

        if not url:
            return None

        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=15,
            allow_redirects=True,
        )

        if response.status_code != 200:
            return None

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            ).lower()
        )

        if "text/html" not in content_type:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        return {
            "url": normalize_url(
                response.url
            ),
            "soup": soup,
            "text": clean_text(
                soup.get_text(" ")
            ),
        }

    except Exception:

        return None


# =========================================================
# CONTACT PAGES
# =========================================================

def find_contact_pages(
    soup,
    base_url
):

    pages = []

    if not soup:
        return pages

    keywords = [
        "contact",
        "contact us",
        "about",
        "about us",
        "reach us",
        "reach",
        "connect",
        "get in touch",
    ]

    base_domain = get_domain(
        base_url
    )

    for link in soup.find_all(
        "a",
        href=True
    ):

        text = clean_text(
            link.get_text(" ")
        ).lower()

        href = link.get(
            "href",
            ""
        ).strip()

        if not href:
            continue

        combined = (
            text
            + " "
            + href.lower()
        )

        if not any(
            keyword in combined
            for keyword in keywords
        ):
            continue

        full_url = normalize_url(
            urljoin(
                base_url,
                href
            )
        )

        if not full_url:
            continue

        if is_social_url(
            full_url
        ):
            continue

        if get_domain(
            full_url
        ) != base_domain:
            continue

        if full_url not in pages:

            pages.append(
                full_url
            )

    return pages[:3]


# =========================================================
# JSON-LD
# =========================================================

def get_jsonld_objects(
    soup
):

    objects = []

    if not soup:
        return objects

    scripts = soup.find_all(
        "script",
        type="application/ld+json"
    )

    for script in scripts:

        try:

            raw = (
                script.string
                or script.get_text()
            )

            if not raw:
                continue

            data = json.loads(
                raw
            )

            if isinstance(
                data,
                list
            ):

                objects.extend(
                    data
                )

            elif isinstance(
                data,
                dict
            ):

                objects.append(
                    data
                )

                graph = data.get(
                    "@graph"
                )

                if isinstance(
                    graph,
                    list
                ):

                    objects.extend(
                        graph
                    )

        except Exception:

            continue

    return objects


# =========================================================
# BUSINESS NAME VALIDATION
# =========================================================

def looks_like_real_business_name(
    name,
    context=""
):

    name = clean_text(
        name
    )

    if not name:
        return False

    if len(name) < 2:
        return False

    if len(name) > 100:
        return False

    lower = name.lower()

    # -----------------------------------------------------
    # Exact junk
    # -----------------------------------------------------

    bad_exact = {
        "home",
        "homepage",
        "home page",
        "about",
        "about us",
        "contact",
        "contact us",
        "login",
        "sign in",
        "sign up",
        "buyer icon",

        "youtube",
        "facebook",
        "instagram",
        "linkedin",
        "google",
        "reddit",

        "logo",

        "justdial",
        "tradeindia",
        "indiamart",
        "sulekha",

        "top salon services at home",
        "salon services at home",
        "salon services",
        "salon services in noida",
        "salons in noida",
        "salon in noida",
        "hair salons in noida",
        "beauty salons in noida",
    }

    if lower in bad_exact:
        return False

    # -----------------------------------------------------
    # Generic bad terms
    # -----------------------------------------------------

    if lower in BAD_NAME_TERMS:
        return False

    # -----------------------------------------------------
    # URL-like
    # -----------------------------------------------------

    if (
        "http://" in lower
        or "https://" in lower
        or "www." in lower
    ):
        return False

    # -----------------------------------------------------
    # Article / list patterns
    # -----------------------------------------------------

    bad_patterns = [

        r"^this is why",

        r"^why .* chooses",

        r"^why .* choose",

        r"^top\s+\d+",

        r"^best .* in ",

        r"^salons? in ",

        r"^hair salons? in ",

        r"^beauty salons? in ",

        r"^salon services",

        r"^services at home",

        r"^find .* salons?",

        r"^list of .* salons?",

        r"^.*\bcategory\b$",

        r"^.*\bdirectory\b$",

        r"^.*\bsearch results\b$",
    ]

    for pattern in bad_patterns:

        if re.search(
            pattern,
            lower,
            flags=re.I
        ):
            return False

    words = name.split()

    if len(words) > 9:
        return False

    # -----------------------------------------------------
    # Sentence-like names
    # -----------------------------------------------------

    sentence_words = [
        "this",
        "why",
        "where",
        "what",
        "how",
        "which",
        "choose",
        "chooses",
        "crowd",
        "watch",
        "video",
    ]

    sentence_count = sum(
        1
        for word in words
        if word.lower().strip(
            ".,!?"
        ) in sentence_words
    )

    if sentence_count >= 2:
        return False

    return True


# =========================================================
# BUSINESS NAME FROM JSON-LD / PAGE
# =========================================================

def extract_company_name_from_page(
    soup,
    page_url
):

    if not soup:
        return ""

    # -----------------------------------------------------
    # JSON-LD
    # -----------------------------------------------------

    for obj in get_jsonld_objects(
        soup
    ):

        if not isinstance(
            obj,
            dict
        ):
            continue

        obj_type = obj.get(
            "@type",
            ""
        )

        if isinstance(
            obj_type,
            list
        ):

            obj_type = " ".join(
                map(
                    str,
                    obj_type
                )
            )

        obj_type = str(
            obj_type
        ).lower()

        valid_types = [
            "organization",
            "localbusiness",
            "corporation",
            "store",
            "professionalservice",
            "salon",
            "healthandbeautybusiness",
            "manufacturer",
        ]

        if any(
            value in obj_type
            for value in valid_types
        ):

            name = clean_text(
                obj.get(
                    "name",
                    ""
                )
            )

            if looks_like_real_business_name(
                name
            ):
                return name

    # -----------------------------------------------------
    # OG site name
    # -----------------------------------------------------

    tag = soup.find(
        "meta",
        property="og:site_name"
    )

    if tag:

        name = clean_text(
            tag.get(
                "content",
                ""
            )
        )

        if looks_like_real_business_name(
            name
        ):
            return name

    # -----------------------------------------------------
    # Header logo alt
    # -----------------------------------------------------

    for selector in [
        "header",
        "nav",
    ]:

        element = soup.find(
            selector
        )

        if not element:
            continue

        for logo in element.find_all(
            "img",
            alt=True
        ):

            name = clean_text(
                logo.get(
                    "alt",
                    ""
                )
            )

            if name.lower().endswith(
                " logo"
            ):
                continue

            if looks_like_real_business_name(
                name
            ):
                return name

    # -----------------------------------------------------
    # H1
    # -----------------------------------------------------

    for h1 in soup.find_all(
        "h1"
    )[:3]:

        name = clean_text(
            h1.get_text(" ")
        )

        if looks_like_real_business_name(
            name
        ):
            return name

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    title_tag = soup.find(
        "title"
    )

    if title_tag:

        title = clean_text(
            title_tag.get_text()
        )

        parts = re.split(
            r"\s*(?:\||\-|–|—|::)\s*",
            title
        )

        for candidate in parts:

            candidate = clean_text(
                candidate
            )

            if looks_like_real_business_name(
                candidate
            ):
                return candidate

    return ""


# =========================================================
# EXTRACT BUSINESS NAME FROM CONTENT
# =========================================================

def extract_business_name_from_content(
    content
):

    if not content:
        return ""

    text = clean_text(
        content
    )

    patterns = [

        r"\b(?:business|company|salon|shop|store)"
        r"\s*[:\-]\s*"
        r"([A-Z][A-Za-z0-9&'.\-\s]{2,70})",

        r"\b([A-Z][A-Za-z0-9&'.\-]{2,50}"
        r"\s+(?:Salon|Studio|Spa|Parlour|Parlor|"
        r"Services|Enterprises|Industries|"
        r"Technologies|Solutions|Pvt Ltd|"
        r"Private Limited|LLP))",

        r"\b(?:at|visit|from)\s+"
        r"([A-Z][A-Za-z0-9&'.\-]{2,50}"
        r"\s+(?:Salon|Studio|Spa|Parlour|Parlor))",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.I
        )

        for match in matches:

            name = clean_text(
                match
            )

            if looks_like_real_business_name(
                name
            ):
                return name

    return ""


# =========================================================
# TITLE CANDIDATE
# =========================================================

def extract_business_name_from_title(
    title
):

    if not title:
        return ""

    title = clean_text(
        title
    )

    parts = re.split(
        r"\s*(?:\||\-|–|—|::)\s*",
        title
    )

    for part in parts:

        name = clean_text(
            part
        )

        name = re.sub(
            r"\b(official website|official|website)\b",
            "",
            name,
            flags=re.I
        )

        name = clean_text(
            name
        ).strip(
            " -|–—:,. "
        )

        if looks_like_real_business_name(
            name
        ):
            return name

    return ""


# =========================================================
# BUSINESS NAME FROM URL SLUG
# =========================================================

def extract_business_name_from_url(
    url
):

    if not url:
        return ""

    try:

        parsed = urlparse(
            url
        )

        path = unquote(
            parsed.path
        )

        parts = [
            p
            for p in path.split("/")
            if p
        ]

        if not parts:
            return ""

        bad_parts = {
            "contact",
            "about",
            "services",
            "service",
            "home",
            "index",
            "salon",
            "noida",
            "india",
        }

        candidates = []

        for part in reversed(
            parts
        ):

            candidate = re.sub(
                r"[-_]+",
                " ",
                part
            )

            candidate = clean_text(
                candidate
            )

            if candidate.lower() in bad_parts:
                continue

            if len(candidate) < 3:
                continue

            candidates.append(
                candidate
            )

        for candidate in candidates:

            pretty = " ".join(
                word.capitalize()
                for word in candidate.split()
            )

            if looks_like_real_business_name(
                pretty
            ):
                return pretty

    except Exception:

        pass

    return ""


# =========================================================
# SCRAPE OFFICIAL WEBSITE
# =========================================================

def scrape_website(
    url
):

    result = {
        "website": "",
        "business_name": "",
        "email": "",
        "phone": "",
        "instagram": "",
        "facebook": "",
        "linkedin": "",
    }

    url = normalize_url(
        url
    )

    if not url:
        return result

    if is_social_url(
        url
    ):
        return result

    page = get_page_content(
        url
    )

    if not page:
        return result

    result["website"] = page[
        "url"
    ]

    soup = page[
        "soup"
    ]

    text = page[
        "text"
    ]

    official_domain = get_domain(
        page["url"]
    )

    result["business_name"] = (
        extract_company_name_from_page(
            soup,
            page["url"]
        )
    )

    result["email"] = extract_email(
        text,
        allowed_domain=official_domain
    )

    result["phone"] = extract_phone(
        text
    )

    result.update(
        extract_social_links(
            soup
        )
    )

    # -----------------------------------------------------
    # Contact pages
    # -----------------------------------------------------

    if (
        not result["email"]
        or not result["phone"]
        or not result["instagram"]
        or not result["facebook"]
        or not result["linkedin"]
    ):

        contact_pages = (
            find_contact_pages(
                soup,
                page["url"]
            )
        )

        for contact_url in contact_pages:

            contact_page = (
                get_page_content(
                    contact_url
                )
            )

            if not contact_page:
                continue

            contact_text = (
                contact_page["text"]
            )

            if not result["email"]:

                result["email"] = (
                    extract_email(
                        contact_text,
                        allowed_domain=official_domain
                    )
                )

            if not result["phone"]:

                result["phone"] = (
                    extract_phone(
                        contact_text
                    )
                )

            socials = (
                extract_social_links(
                    contact_page["soup"]
                )
            )

            for key in socials:

                if (
                    not result[key]
                    and socials[key]
                ):

                    result[key] = (
                        socials[key]
                    )

    return result


# =========================================================
# NORMALIZE BUSINESS NAME
# =========================================================

def normalize_business_name(
    name
):

    if not name:
        return ""

    name = clean_text(
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip(
        " -|–—:,."
    )


# =========================================================
# BUSINESS NAME KEY
# =========================================================

def business_name_key(
    name
):

    if not name:
        return ""

    value = normalize_business_name(
        name
    ).lower()

    value = re.sub(
        r"\b(private limited|pvt ltd|pvt\. ltd\.|"
        r"limited|ltd|llp|incorporated|inc)\b",
        "",
        value
    )

    value = re.sub(
        r"[^a-z0-9]",
        "",
        value
    )

    return value


# =========================================================
# BUSINESS NAME MATCHING
# =========================================================

def business_names_match(
    name1,
    name2
):

    key1 = business_name_key(
        name1
    )

    key2 = business_name_key(
        name2
    )

    if not key1 or not key2:
        return False

    if key1 == key2:
        return True

    if (
        len(key1) >= 5
        and key1 in key2
    ):
        return True

    if (
        len(key2) >= 5
        and key2 in key1
    ):
        return True

    return False


# =========================================================
# FIND OFFICIAL WEBSITE
# =========================================================

def find_company_website(
    business_name,
    context="",
    original_url=""
):

    if not business_name:
        return ""

    api_key = os.getenv(
        "TAVILY_API_KEY"
    )

    if not api_key:
        return ""

    try:

        client = TavilyClient(
            api_key=api_key
        )

        queries = [
            f'"{business_name}" official website',
            f'"{business_name}" website',
        ]

        original_domain = get_domain(
            original_url
        )

        for query in queries:

            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=8,
                include_answer=False,
            )

            results = response.get(
                "results",
                []
            )

            for item in results:

                candidate_url = normalize_url(
                    item.get(
                        "url",
                        ""
                    )
                )

                if not candidate_url:
                    continue

                if is_third_party_url(
                    candidate_url
                ):
                    continue

                if is_social_url(
                    candidate_url
                ):
                    continue

                candidate_domain = get_domain(
                    candidate_url
                )

                if not candidate_domain:
                    continue

                if (
                    original_domain
                    and candidate_domain == original_domain
                ):
                    continue

                page = get_page_content(
                    candidate_url
                )

                if not page:
                    continue

                page_name = (
                    extract_company_name_from_page(
                        page["soup"],
                        page["url"]
                    )
                )

                if not page_name:
                    continue

                if business_names_match(
                    business_name,
                    page_name
                ):
                    return page["url"]

    except Exception:

        return ""

    return ""


# =========================================================
# TAVILY PHONE ENRICHMENT
# =========================================================

def extract_phone_from_tavily_results(
    results,
    business_name
):

    if not results:
        return ""

    business_key = business_name_key(
        business_name
    )

    if not business_key:
        return ""

    for item in results:

        title = clean_text(
            item.get(
                "title",
                ""
            )
        )

        content = clean_text(
            item.get(
                "content",
                ""
            )
        )

        result_url = normalize_url(
            item.get(
                "url",
                ""
            )
        )

        # Never trust social/video/google pages
        # for phone enrichment.
        if (
            is_non_business_source(
                result_url
            )
        ):
            continue

        if is_probably_article(
            title,
            result_url
        ):
            continue

        combined = (
            title
            + " "
            + content
        )

        combined_key = business_name_key(
            combined
        )

        # Search result should actually contain
        # the business name.
        if business_key not in combined_key:
            continue

        phone = extract_phone(
            combined
        )

        if phone:
            return phone

    return ""


# =========================================================
# TAVILY EMAIL ENRICHMENT
# =========================================================

def extract_email_from_tavily_results(
    results,
    business_name
):

    if not results:
        return ""

    business_key = business_name_key(
        business_name
    )

    if not business_key:
        return ""

    for item in results:

        title = clean_text(
            item.get(
                "title",
                ""
            )
        )

        content = clean_text(
            item.get(
                "content",
                ""
            )
        )

        result_url = normalize_url(
            item.get(
                "url",
                ""
            )
        )

        # Don't trust social / Google / video sources.
        if (
            is_non_business_source(
                result_url
            )
        ):
            continue

        if is_probably_article(
            title,
            result_url
        ):
            continue

        combined = (
            title
            + " "
            + content
        )

        combined_key = business_name_key(
            combined
        )

        if business_key not in combined_key:
            continue

        source_domain = get_domain(
            result_url
        )

        # If source is a third-party listing,
        # only accept email if it belongs to that
        # source's domain or is a common free mailbox.
        email = extract_email(
            combined
        )

        if not email:
            continue

        email_domain = (
            email.lower()
            .split("@")[-1]
        )

        free_mail_domains = {
            "gmail.com",
            "outlook.com",
            "hotmail.com",
            "yahoo.com",
            "yahoo.co.in",
            "proton.me",
            "protonmail.com",
        }

        if (
            source_domain
            and email_domain != source_domain
            and email_domain not in free_mail_domains
        ):
            continue

        return email

    return ""


# =========================================================
# MERGE
# =========================================================

def merge_value(
    old,
    new
):

    if old:
        return old

    return new or ""


def merge_leads(
    old,
    new
):

    old["business_name"] = merge_value(
        old.get(
            "business_name"
        ),
        new.get(
            "business_name"
        )
    )

    if (
        not old.get("website")
        or old.get("website") == "X"
    ):

        old["website"] = new.get(
            "website",
            "X"
        )

    for key in [
        "email",
        "phone",
        "instagram",
        "facebook",
        "linkedin",
        "source_url",
    ]:

        old[key] = merge_value(
            old.get(key),
            new.get(key)
        )

    old["has_website"] = (
        old.get("website")
        not in (
            "",
            "X",
            None
        )
    )

    return old


# =========================================================
# EXISTING DATABASE PLACE IDS
# =========================================================

def get_existing_place_ids():

    try:

        # Local import avoids unnecessary import-time
        # Django model loading issues.
        from .models import Lead

        values = (
            Lead.objects
            .exclude(
                place_id__isnull=True
            )
            .exclude(
                place_id=""
            )
            .values_list(
                "place_id",
                flat=True
            )
        )

        return set(
            values
        )

    except Exception:

        return set()


# =========================================================
# DISCOVER LEADS
# =========================================================

def discover_leads(
    context,
    max_results=20,
    exclude_place_ids=None,
    progress_callback=None,
):

    wanted = max(
        1,
        int(max_results)
    )

    # =====================================================
    # EXISTING DATABASE RECORDS
    # =====================================================

    existing_place_ids = (
        get_existing_place_ids()
    )

    if exclude_place_ids:

        existing_place_ids.update(
            exclude_place_ids
        )

    # =====================================================
    # GOOGLE PLACES = PRIMARY DISCOVERY
    # =====================================================

    report_progress(
        progress_callback,
        stage="🔎 Starting Google Places search...",
        current=0,
        total=wanted,
        message=(
            f"Looking for up to {wanted} "
            "new businesses"
        ),
    )

    places = search_businesses(
        context=context,
        max_results=wanted,
        exclude_place_ids=existing_place_ids,
        progress_callback=progress_callback,
    )

    report_progress(
        progress_callback,
        stage="🔍 Processing businesses...",
        current=0,
        total=len(places),
        message=(
            f"Google returned {len(places)} "
            "candidate businesses"
        ),
    )

    leads = []

    seen_place_ids = set()

    seen_name_keys = set()

    seen_domains = set()

    seen_phones = set()

    # =====================================================
    # PROCESS GOOGLE RESULTS
    # =====================================================

    total_places = len(
        places
    )

    for index, place in enumerate(
        places,
        start=1
    ):

        report_progress(
            progress_callback,
            stage="🔍 Processing businesses...",
            current=index - 1,
            total=total_places,
            message=(
                f"Processing "
                f"{index}/{total_places}"
            ),
        )

        # -------------------------------------------------
        # GOOGLE BUSINESS NAME
        # -------------------------------------------------

        display_name = place.get(
            "displayName",
            {}
        )

        business_name = clean_text(
            display_name.get(
                "text",
                ""
            )
        )

        # -------------------------------------------------
        # PLACE ID
        # -------------------------------------------------

        place_id = clean_text(
            place.get(
                "id",
                ""
            )
        )

        if not business_name:
            continue

        if not looks_like_real_business_name(
            business_name,
            context
        ):
            continue

        # Existing DB check again for safety.
        if (
            place_id
            and place_id in existing_place_ids
        ):
            continue

        if (
            place_id
            and place_id in seen_place_ids
        ):
            continue

        if place_id:

            seen_place_ids.add(
                place_id
            )

        # -------------------------------------------------
        # GOOGLE DATA
        # -------------------------------------------------

        phone = normalize_phone(
            place.get(
                "nationalPhoneNumber",
                ""
            )
        )

        website = normalize_url(
            place.get(
                "websiteUri",
                ""
            )
        )

        maps_url = normalize_url(
            place.get(
                "googleMapsUri",
                ""
            )
        )

        # Google Maps URL is always the source.
        source_url = maps_url

        # -------------------------------------------------
        # CONTACT DATA
        # -------------------------------------------------

        email = ""

        instagram = ""

        facebook = ""

        linkedin = ""

        # =================================================
        # OFFICIAL WEBSITE
        # =================================================

        if website:

            report_progress(
                progress_callback,
                stage="🌐 Checking official website...",
                current=index - 1,
                total=total_places,
                message=business_name,
            )

            official_data = scrape_website(
                website
            )

            # ---------------------------------------------
            # Email
            # ---------------------------------------------

            official_email = (
                official_data.get(
                    "email",
                    ""
                )
            )

            if official_email:

                email = official_email

            # ---------------------------------------------
            # Phone
            # ---------------------------------------------

            official_phone = normalize_phone(
                official_data.get(
                    "phone",
                    ""
                )
            )

            # Google phone ALWAYS wins.
            if not phone and official_phone:

                phone = official_phone

            # ---------------------------------------------
            # Social
            # ---------------------------------------------

            instagram = (
                official_data.get(
                    "instagram",
                    ""
                )
            )

            facebook = (
                official_data.get(
                    "facebook",
                    ""
                )
            )

            linkedin = (
                official_data.get(
                    "linkedin",
                    ""
                )
            )

        # =================================================
        # TAVILY ENRICHMENT
        #
        # IMPORTANT:
        # Tavily does NOT create a business.
        # It only fills missing contact data.
        # =================================================

        try:

            tavily_key = os.getenv(
                "TAVILY_API_KEY"
            )

            if tavily_key:

                report_progress(
                    progress_callback,
                    stage="🔎 Enriching contact data...",
                    current=index - 1,
                    total=total_places,
                    message=business_name,
                )

                client = TavilyClient(
                    api_key=tavily_key
                )

                enrichment_query = (
                    f'"{business_name}" '
                    f'"{context}" '
                    f'contact phone email '
                    f'Instagram Facebook LinkedIn'
                )

                response = client.search(
                    query=enrichment_query,
                    search_depth="basic",
                    max_results=5,
                    include_answer=False,
                )

                tavily_results = response.get(
                    "results",
                    []
                )

                # -----------------------------------------
                # SOCIAL URLs
                #
                # IMPORTANT:
                # Only use the result URL itself.
                # Never scan combined text and assume
                # every URL belongs to every platform.
                # -----------------------------------------

                for item in tavily_results:

                    result_url = normalize_url(
                        item.get(
                            "url",
                            ""
                        )
                    )

                    if not result_url:
                        continue

                    if (
                        not instagram
                        and is_valid_social_profile(
                            "instagram",
                            result_url
                        )
                    ):

                        instagram = result_url

                    if (
                        not facebook
                        and is_valid_social_profile(
                            "facebook",
                            result_url
                        )
                    ):

                        facebook = result_url

                    if (
                        not linkedin
                        and is_valid_social_profile(
                            "linkedin",
                            result_url
                        )
                    ):

                        linkedin = result_url

                # -----------------------------------------
                # Missing phone
                # -----------------------------------------

                if not phone:

                    phone = (
                        extract_phone_from_tavily_results(
                            tavily_results,
                            business_name
                        )
                    )

                # -----------------------------------------
                # Missing email
                #
                # Only accept when the result strongly
                # appears to belong to this business.
                # -----------------------------------------

                if not email:

                    email = (
                        extract_email_from_tavily_results(
                            tavily_results,
                            business_name
                        )
                    )

        except Exception:

            # Tavily must never destroy the Google lead.
            pass

        # =================================================
        # FINAL PHONE NORMALIZATION
        # =================================================

        phone = normalize_phone(
            phone
        )

        # =================================================
        # FINAL EMAIL VALIDATION
        # =================================================

        if email:

            if not is_valid_email(
                email
            ):

                email = ""

        # =================================================
        # FINAL SOCIAL VALIDATION
        # =================================================

        if instagram:

            if not is_valid_social_profile(
                "instagram",
                instagram
            ):

                instagram = ""

        if facebook:

            if not is_valid_social_profile(
                "facebook",
                facebook
            ):

                facebook = ""

        if linkedin:

            if not is_valid_social_profile(
                "linkedin",
                linkedin
            ):

                linkedin = ""

        # =================================================
        # WEBSITE
        # =================================================

        if not website:

            website_value = "X"

        else:

            website_value = website

        # =================================================
        # BUILD LEAD
        # =================================================

        lead = {
            "business_name": business_name,
            "place_id": place_id,
            "website": website_value,
            "email": email,
            "phone": phone,
            "instagram": instagram,
            "facebook": facebook,
            "linkedin": linkedin,
            "source_url": source_url,
            "has_website": bool(website),
        }

        # =================================================
        # LOCAL DEDUPLICATION
        # =================================================

        name_key = business_name_key(
            business_name
        )

        website_domain = ""

        if website:

            website_domain = get_domain(
                website
            )

        phone_key = re.sub(
            r"\D",
            "",
            phone or ""
        )

        # -------------------------------------------------
        # Same place ID
        # -------------------------------------------------

        if (
            place_id
            and place_id in existing_place_ids
        ):
            continue

        # -------------------------------------------------
        # Same name
        # -------------------------------------------------

        if (
            name_key
            and name_key in seen_name_keys
        ):
            continue

        # -------------------------------------------------
        # Same website
        # -------------------------------------------------

        if (
            website_domain
            and website_domain in seen_domains
        ):
            continue

        # -------------------------------------------------
        # Same phone
        # -------------------------------------------------

        if (
            phone_key
            and phone_key in seen_phones
        ):
            continue

        # =================================================
        # ADD LEAD
        # =================================================

        leads.append(
            lead
        )

        if name_key:

            seen_name_keys.add(
                name_key
            )

        if website_domain:

            seen_domains.add(
                website_domain
            )

        if phone_key:

            seen_phones.add(
                phone_key
            )

        # =================================================
        # STOP EXACTLY AT USER LIMIT
        # =================================================

        if len(leads) >= wanted:

            break

        report_progress(
            progress_callback,
            stage="✅ Business processed",
            current=index,
            total=total_places,
            message=(
                f"{len(leads)} new leads ready"
            ),
        )

    # =====================================================
    # FINAL PROGRESS
    # =====================================================

    report_progress(
        progress_callback,
        stage="✅ Search completed",
        current=len(leads),
        total=wanted,
        message=(
            f"{len(leads)} new unique businesses "
            "ready to save"
        ),
    )

    return leads[:wanted]


# =========================================================
# ARTICLE CHECK
# =========================================================

def is_probably_article(
    title,
    url
):

    title_text = (
        title or ""
    ).lower()

    url_text = (
        url or ""
    ).lower()

    # -----------------------------------------------------
    # Strong article indicators
    # -----------------------------------------------------

    strong_words = [
        "directory",
        "ranking",
        "company list",
        "business list",
        "service providers",
        "semrush",
        "clutch",
    ]

    for word in strong_words:

        if word in title_text:

            return True

    # -----------------------------------------------------
    # Generic category URLs
    # -----------------------------------------------------

    category_url_words = [
        "/category/",
        "/categories/",
        "/directory/",
        "/search/",
        "/list/",
        "/top-",
        "/best-",
    ]

    for word in category_url_words:

        if word in url_text:

            return True

    return False