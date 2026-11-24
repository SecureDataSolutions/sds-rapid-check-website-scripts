#!/usr/bin/env python3
# Secure Data Solutions (SDS), https://sdsitgroup.com. Read-only check. Questions about the output? Contact us at sdsitgroup.com.
# Eddie Espino, Secure Data Solutions. MIT License. No warranty; run only on systems you own or are authorized to check.
"""List third-party script hosts referenced in a web page's HTML.

Usage:
  python3 third_party_scripts.py https://www.example.com
  python3 third_party_scripts.py https://www.example.com https://shop.example.com
  python3 third_party_scripts.py --file saved-page.html --site https://www.example.com

Read-only. Use it on your own site. It fetches page HTML and follows HTTP(S) redirects on
the same host, including www aliases and standard HTTP-to-HTTPS upgrades. It never fetches
scripts or frames. With --file it reads only saved HTML and makes no network requests. The
--site address identifies your site for local files. It groups <script src> hosts using a
limited list of shared domain endings.

Limits: it sees scripts written in the page HTML only. It does not see scripts added later
by a tag manager or by other scripts, scripts inside frames, or other pages of the site.
For the full list, open the page in a browser, then DevTools > Network > filter "JS".
It lists who is loaded. It does not judge whether a script is safe.
Python 3 standard library only.
"""
import sys, urllib.request
from html.parser import HTMLParser
from ipaddress import ip_address
from urllib.parse import urljoin, urlparse

LAST_CHECKED = "2026-11-23"  # date the watch list below was last reviewed
WATCH = {  # script hosts worth a closer look
    "optimizely.com": "Optimizely: check Project JavaScript for code added on Nov 16, 2026",
    "googletagmanager.com": "Tag manager: it can load more scripts, so review its tags too",
}
# Common endings where the owner's name is the third label from the right (example.co.uk).
# Not a full list. For other country endings, check the result by eye.
TWO_PART = {"co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "co.nz", "co.za",
            "com.br", "com.mx", "com.ar", "com.co", "co.jp", "co.kr", "co.in", "com.sg", "com.hk",
            "com.tr", "com.cn", "com.tw", "co.il", "github.io", "pages.dev", "workers.dev", "vercel.app",
            "netlify.app", "cloudfront.net", "azurewebsites.net", "blogspot.com"}
MAX_BYTES = 5 * 1024 * 1024


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.srcs, self.inline, self.frames, self.base = [], 0, 0, None

    def handle_starttag(self, tag, attrs):
        a = dict(reversed(attrs))  # HTML uses the first value for duplicate attributes.
        if tag == "script":
            if "src" in a:
                src = (a["src"] or "").strip()
                if src:
                    self.srcs.append((src, bool((a.get("integrity") or "").strip())))
            else:
                self.inline += 1
        elif tag == "iframe":
            self.frames += 1
        elif tag == "base" and "href" in a and self.base is None:
            self.base = (a["href"] or "").strip()


def site(host):
    """Crude owner domain: last two labels, or three for the endings in TWO_PART."""
    try:
        return str(ip_address(host))
    except ValueError:
        pass
    labels = host.split(".")
    n = 3 if ".".join(labels[-2:]) in TWO_PART else 2
    return ".".join(labels[-n:])


def web_address(url):
    address = urlparse(url)
    if address.scheme not in ("http", "https") or not address.hostname:
        raise ValueError("expected an HTTP(S) address with a hostname")
    if address.username is not None or address.password is not None:
        raise ValueError("addresses with usernames or passwords are unsupported")
    host = address.hostname.rstrip(".")
    if not host or any(c.isspace() or ord(c) < 32 or c in "\\%" for c in host):
        raise ValueError("invalid hostname")
    port = address.port
    if port is None:
        port = 443 if address.scheme == "https" else 80
    return address.scheme, host.encode("idna").decode("ascii"), port


class PageRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old_scheme, old_host, old_port = web_address(req.full_url)
        scheme, host, port = web_address(newurl)
        old_host = old_host[4:] if old_host.startswith("www.") else old_host
        host = host[4:] if host.startswith("www.") else host
        same_service = (scheme, port) == (old_scheme, old_port)
        upgrade = (old_scheme, old_port, scheme, port) == ("http", 80, "https", 443)
        if host != old_host or not (same_service or upgrade):
            raise ValueError("redirect outside the supplied site; check the destination directly if authorized")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def report(final, page, own_host):
    p = Scripts()
    p.feed(page[:MAX_BYTES].decode("utf-8", "replace"))
    p.close()
    base = final
    if p.base:
        try:
            candidate = urljoin(final, p.base)
            web_address(candidate)
            base = candidate
        except ValueError:
            pass
    own = site(own_host)
    hosts = {}
    ignored = 0
    for src, has_integrity in p.srcs:
        try:
            _, h, _ = web_address(urljoin(base, src))
        except ValueError:
            ignored += 1
            continue
        if site(h) != own:
            hosts.setdefault(h, []).append(has_integrity)
    print(f"\n{final}\n  {len(p.srcs)} script references, {p.inline} inline script tags, "
          f"{p.frames} frames (not looked inside), {len(hosts)} third-party hosts")
    if len(page) > MAX_BYTES:
        print("  Partial result: checked only the first 5 MiB of the response.")
    if ignored:
        print(f"  Skipped {ignored} invalid or unsupported script URLs.")
    for h in sorted(hosts):
        note = next((n for k, n in WATCH.items() if h == k or h.endswith("." + k)), "")
        pinned = sum(hosts[h])
        lock = f", {pinned} with an integrity attribute" if pinned else ""
        print(f"  - {h} ({len(hosts[h])} file(s){lock})" + (f"  << {note}" if note else ""))


def check(url):
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    web_address(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 third-party-script-check/1.1"})
    opener = urllib.request.build_opener(PageRedirect())
    with opener.open(req, timeout=30) as r:
        page = r.read(MAX_BYTES + 1)
        final = r.geturl()
    report(final, page, web_address(final)[1])


def check_file(path, site_url):
    address = site_url.strip()
    if "://" not in address:
        address = "https://" + address
    _, host, _ = web_address(address)
    try:
        with open(path, "rb") as f:
            page = f.read(MAX_BYTES + 1)
    except OSError as e:
        raise ValueError(f"could not read saved page: {e}")
    report(address, page, host)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("addresses", nargs="*", help="site addresses to check online")
    parser.add_argument("--file", help="read saved page HTML locally (no network access)")
    parser.add_argument("--site", help="your site's HTTP(S) address, required with --file")
    args = parser.parse_args()
    if args.file is not None:
        if args.addresses:
            parser.error("positional addresses cannot be used with --file")
        if not args.site:
            parser.error("--site is required with --file")
    elif args.site:
        parser.error("--site can only be used with --file")
    elif not args.addresses:
        parser.print_help()
        sys.exit(2)
    failed = 0
    if args.file is not None:
        try:
            check_file(args.file, args.site)
        except Exception as e:
            failed = 1
            print(f"\nSaved page\n  error, nothing checked: {e}")
    else:
        for index, u in enumerate(args.addresses, 1):
            try:
                check(u)
            except Exception as e:
                failed += 1
                print(f"\nAddress {index}\n  error, nothing checked: {e}")
    print("\nNo finding is not proof of no compromise. This lists script hosts in the page HTML only.\n"
          "It does not see scripts added after the page loads, and it does not judge whether\n"
          "a listed script is safe. A short list is not a clean bill of health.")
    print(f"Watch list last checked: {LAST_CHECKED}.")
    sys.exit(1 if failed else 0)
