# REFACTOR-103: Drop Flask-Bootstrap

Flask-Bootstrap ships Bootstrap 3, but `base.html` already loads Bootstrap 4 from a CDN, so we carry an unused dependency and mixed syntax.

**Good enough:**
- Remove `Bootstrap(app)` from `app/factory.py` and the package from `pyproject.toml`.
- Make `base.html` stand alone (no `bootstrap/base.html` inheritance).
- Click through the main pages; fix anything that looks broken.

No need to hunt down every Bootstrap 3 class in one go; fix them as you see them.
