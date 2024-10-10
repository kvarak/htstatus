// Core data types matching Flask models

export interface User {
  ht_id: number;
  ht_user: string;
  username: string;
  access_key?: string;
  access_secret?: string;
  c_login: number;
  c_team: number;
  c_player: number;
  c_matches: number;
  c_training: number;
  c_update: number;
  last_login?: Date;
  last_update?: Date;
  last_usage?: Date;
  created?: Date;
  role: string;
  player_columns?: string[];
}

export interface Player {
  ht_id: number;
  data_date: Date;
  first_name: string;
  nick_name?: string;
  last_name: string;
  number: number;
  category_id: number;
  owner_notes?: string;
  age_years: number;
  age_days: number;
  age: string;
  next_birthday: Date;
  arrival_date: Date;
  form: number;
  cards: number;
  injury_level: number;
  statement?: string;
  language?: string;
  language_id: number;
  agreeability: number;
  aggressiveness: number;
  honesty: number;
  experience: number;
  loyalty: number;
  specialty: number;
  native_country_id: number;
  native_league_id: number;
  native_league_name: string;
  tsi: number;
  salary: number;
  caps: number;
  caps_u20: number;
  career_goals: number;
  career_hattricks: number;
  league_goals: number;
  cup_goals: number;
  friendly_goals: number;
  current_team_matches: number;
  current_team_goals: number;
  national_team_id?: number;
  national_team_name?: string;
  is_transfer_listed: boolean;
  team_id: number;
  stamina: number;
  keeper: number;
  defender: number;
  playmaker: number;
  winger: number;
  passing: number;
  scorer: number;
  set_pieces: number;
  owner: number;
  old_owner: number;
  mother_club_bonus: boolean;
  leadership: number;
}

export interface Match {
  ht_id: number;
  home_team_id: number;
  home_team_name: string;
  away_team_id: number;
  away_team_name: string;
  datetime: Date;
  matchtype: number;
  context_id: number;
  rule_id: number;
  cup_level: number;
  cup_level_index: number;
  home_goals: number;
  away_goals: number;
}

export interface MatchPlay {
  id: number;
  match_id: number;
  player_id: number;
  datetime: Date;
  first_name: string;
  nick_name?: string;
  last_name: string;
  role_id: number;
  rating_stars: number;
  rating_stars_eom: number;
  behaviour: number;
}

export interface PlayerGroup {
  id: number;
  user_id: number;
  name: string;
  order: number;
  textcolor: string;
  bgcolor: string;
}

export interface PlayerSetting {
  id: number;
  user_id: number;
  group_id: number;
  player_id: number;
}

// UI Types
export interface StatCard {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon?: React.ComponentType;
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

// Match Types Constants
export const MATCH_TYPES = {
  1: "League match",
  2: "Qualification match", 
  3: "Cup match (standard league match)",
  4: "Friendly (normal rules)",
  5: "Friendly (cup rules)",
  7: "Hattrick Masters",
  8: "International friendly (normal rules)",
  9: "International friendly (cup rules)",
  10: "National teams competition match (normal rules)",
  11: "National teams competition match (cup rules)",
  12: "National teams friendly",
  50: "Tournament League match",
  51: "Tournament Playoff match",
  61: "Single match",
  62: "Ladder match",
  80: "Preparation match",
  100: "Youth league match",
  101: "Youth friendly match",
  103: "Youth friendly match (cup rules)",
  105: "Youth international friendly match",
  106: "Youth international friendly match (Cup rules)"
} as const;

// Position Types Constants  
export const POSITION_ROLES = {
  100: "Keeper",
  101: "Right back",
  102: "Right central defender", 
  103: "Middle central defender",
  104: "Left central defender",
  105: "Left back",
  106: "Right winger",
  107: "Right inner midfield",
  108: "Middle inner midfield", 
  109: "Left inner midfield",
  110: "Left winger",
  111: "Right forward",
  112: "Middle forward",
  113: "Left forward"
} as const;