'''
StratzToGo Point Allocation
'''

# TODO: Core/Support point differential, using core for all temporarily
# Point total is out of 100

point_dict = {}

# Points assigned (Core/Support):
# Laning Advantage (25/25)
point_dict['laning_gold_5'] = 3
point_dict['laning_xp_5'] = 3
point_dict['laning_lh_5'] = 1
point_dict['laning_dn_5'] = 1
point_dict['laning_gold_10'] = 7
point_dict['laning_xp_10'] = 5
point_dict['laning_lh_10'] = 3
point_dict['laning_dn_10'] = 2

# Combat Advantage (25/25)
# KDA to hero/lane average (15/12)
# Actual KDA ratio vs expected (5/5)
# Kills and assists vs team median (5/8)
point_dict['kda_hero_lane_average'] = 15
point_dict['kda_ratio_vs_expected'] = 5
point_dict['kill_assist_participation'] = 5

# Hero Damage Advantage (20/15)
# Hero damage per Minute percentile (15/10)
# Hero damage per Minute percentile ratio (5/5)
point_dict['hd_percentile'] = 15
point_dict['hd_percentile_mean'] = 5

# Farm Advantage (20/15)
# Last Hits per Minute percentile (4/4)
# Last Hits per Minute percentile mean (1/1)
# GPM to hero/lane average (8/4)
# Actual GPM ratio vs expected (2/1)
# XPM to hero/lane average (4/4)
# Actual XPM ratio vs expected (1/1)
point_dict['lh_percentile'] = 4
point_dict['lh_percentile_mean'] = 1
point_dict['gpm_vs_average'] = 8
point_dict['gpm_vs_expected_ratio'] = 2
point_dict['xpm_vs_average'] = 4
point_dict['xpm_vs_expected_ratio'] = 1

# Tower Damage Advantage (5/5)
# Tower Damage per Minute percentile (4/4)
# Tower Damage per Minute percentile mean (1/1)
point_dict['td_percentile'] = 4
point_dict['td_percentile_mean'] = 1

# Utility Advantage (5/15)
# Hero healing per Minute percentile (1/4)
# Hero healing per Minute percentile mean (1/1)
# Stuns per Minute percentile (2/8)
# Stuns per Minute percentile mean (1/2)
point_dict['hh_percentile'] = 1
point_dict['hh_percentile_mean'] = 1
point_dict['stun_percentile'] = 2
point_dict['stun_percentile_mean'] = 1