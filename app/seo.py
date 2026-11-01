"""Search engines and link previews (FEAT-034).

Only the logged-out pages below are public; everything else needs a login, so
it gets `noindex` and is disallowed in robots.txt. Team and player data is
never exposed. Absolute URLs use the public address from CALLBACK_URL, because
behind the HTTPS proxy Flask itself only sees http://localhost.
"""

from urllib.parse import urlsplit

from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    Response,
    send_from_directory,
)

seo_bp = Blueprint("seo", __name__)

DEFAULT_DESCRIPTION = (
    "Free planning tool for Hattrick managers: follow how your players develop, "
    "plan training, test line-ups and keep track of your matches and series."
)
# Public path -> (title, meta description)
PUBLIC_PAGES = {
    "/": (
        "HattrickPlanner - Team Management Tool for Hattrick Managers",
        DEFAULT_DESCRIPTION,
    ),
    "/changes": (
        "What's new in HattrickPlanner",
        "Every HattrickPlanner release and change: new features, fixes and "
        "improvements to the free team planning tool for Hattrick managers.",
    ),
    "/login": (
        "Log in to HattrickPlanner",
        "Log in or sign up with your Hattrick account (CHPP, Hattrick's own "
        "login) to use HattrickPlanner, the free tool for Hattrick managers.",
    ),
}
SHARE_IMAGE = "img/share.png"


def site_url():
    """Public base URL (scheme://host), taken from CALLBACK_URL."""
    parts = urlsplit(current_app.config.get("CALLBACK_URL") or request.url_root)
    return f"{parts.scheme}://{parts.netloc}"


def page_meta(title=None):
    """Title, description, canonical URL and indexing for the current page."""
    public = PUBLIC_PAGES.get(request.path)
    app_name = current_app.config.get("APP_NAME") or "HattrickPlanner"
    if public:
        page_title, description = public
    else:
        page_title = f"{title} · {app_name}" if title else app_name
        description = DEFAULT_DESCRIPTION
    base = site_url()
    return {
        "title": page_title,
        "description": description,
        "canonical": base + request.path,
        "index": public is not None,
        "is_home": request.path == "/",
        "site_url": base,
        "site_name": app_name,
        "image": base + "/static/" + SHARE_IMAGE,
    }


@seo_bp.route("/robots.txt")
def robots():
    lines = ["User-agent: *", "Allow: /$"]
    lines += [f"Allow: {path}" for path in PUBLIC_PAGES if path != "/"]
    lines += [
        "Allow: /static/",
        "Disallow: /",
        "",
        f"Sitemap: {site_url()}/sitemap.xml",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@seo_bp.route("/sitemap.xml")
def sitemap():
    xml = render_template(
        "sitemap.xml", base=site_url(), paths=[p for p in PUBLIC_PAGES if p != "/login"]
    )
    return Response(xml, mimetype="application/xml")


@seo_bp.route("/favicon.ico")
def favicon():
    """Browsers and crawlers ask for the icon at the site root."""
    return send_from_directory(
        current_app.static_folder, "favicon.ico", mimetype="image/x-icon"
    )


def init_app(app):
    """Make page_meta() available in all templates."""

    @app.context_processor
    def inject_seo():
        return {"page_meta": page_meta}
