"""Minutes per player and field position in one match (FEAT-036).

Follows Hattrick Organizer (MatchLineupTeam.initMinutesOfPlayersInSectors): start
from the starting lineup, apply the orders by minute, end a player's time at a
red card or injury, and count the rest until the end of the match.
"""

from app.training_rules import ROLE_SECTORS

SUBSTITUTION = 1  # also a behaviour/position change when subject == object
POSITION_SWAP = 3
MAN_MARKING = 4  # changes no position
MATCH_END = 90
RED_CARD = 2  # booking_type
INJURY = 2  # injury_type (1 = bruise: he plays on)


def position_minutes(lineup, bookings=(), injuries=()):
    """``{player_id: {role_id: minutes}}`` for the lineup's team.

    ``bookings``/``injuries`` are the match details lists (any team; filtered by
    player). Extra time beyond 90 only counts up to the last known event.
    """
    on_field = {}  # role -> (player, minute he took it)
    for player, role in lineup.starting_roles.items():
        if role in ROLE_SECTORS:
            on_field[role] = (player, 0)
    minutes = {}

    def leave(player, minute):
        """Close the player's current position; return the role he left."""
        for role, (who, since) in list(on_field.items()):
            if who == player:
                del on_field[role]
                if minute > since:
                    per_role = minutes.setdefault(player, {})
                    per_role[role] = per_role.get(role, 0) + minute - since
                return role
        return None

    def enter(player, role, minute):
        if role in ROLE_SECTORS and player:
            on_field[role] = (player, minute)

    end = MATCH_END
    for order in lineup.substitutions:
        minute = order["minute"] or 0
        end = max(end, minute)
        subject, obj = order["subject"], order["object"]
        if order["order_type"] == SUBSTITUTION:
            old_role = leave(subject, minute)
            new_role = (
                order["new_role"] if order["new_role"] in ROLE_SECTORS else old_role
            )
            enter(obj or subject, new_role, minute)
        elif order["order_type"] == POSITION_SWAP:
            subject_role = leave(subject, minute)
            object_role = leave(obj, minute)
            enter(subject, object_role, minute)
            enter(obj, subject_role, minute)

    players_on_field = {who for who, _ in on_field.values()}
    endings = [
        (b["player_id"], b["minute"])
        for b in bookings
        if b.get("booking_type") == RED_CARD
    ] + [
        (i["player_id"], i["minute"])
        for i in injuries
        if i.get("injury_type") == INJURY
    ]
    for player, minute in sorted(endings, key=lambda e: e[1] or 0):
        if player in players_on_field and minute is not None:
            leave(player, minute)
            players_on_field.discard(player)

    for player, _ in list(on_field.values()):
        leave(player, end)
    return minutes
