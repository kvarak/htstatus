TEAM = 12345
PAGES = {
    "player": f"/player?id={TEAM}",
    "stats": f"/stats?id={TEAM}",
    "training": f"/training?id={TEAM}",
    "formations": f"/formations?id={TEAM}",
    "compare": f"/player/compare?team_id={TEAM}&player_ids=601&player_ids=602",
    "settings": "/settings",
    "matches": f"/matches?id={TEAM}",
    "debug": "/debug",
    "feedback": "/feedback/",
}


def test_render_previews(authenticated_client, db_session):
    from datetime import datetime, timedelta

    from models import Group, PlayerSetting, User
    from tests.factories import make_player_record

    admin = User(TEAM, "kvarak", "kvarak", "x", "k", "s")
    admin.setRole("Admin")
    db_session.add(admin)
    for ht_id, first, last, skill in [(601, "Michal", "Keeper", 7), (602, "Yngve", "Winger", 6), (603, "Anna", "Scorer", 8)]:
        for days, bump in ((20, 0), (2, 1)):
            r = make_player_record(ht_id, TEAM, first, last)
            r.data_date = datetime.now() - timedelta(days=days)
            r.number = ht_id - 600
            r.keeper = skill + bump
            r.scorer = skill
            db_session.add(r)
    db_session.flush()
    g = Group(TEAM, "Main Squad", 1, "#ffffff", "#2e7d32")
    db_session.add(g)
    db_session.flush()
    db_session.add(PlayerSetting(601, TEAM, g.id))
    db_session.commit()
    with authenticated_client.session_transaction() as s:
        s["current_user"] = "kvarak"
    for name, url in PAGES.items():
        r = authenticated_client.get(url)
        open(f"app/static/zz-preview-{name}.html", "w").write(r.get_data(as_text=True))
