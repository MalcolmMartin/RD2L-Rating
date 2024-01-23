'''
StratzToGo Point Allocation
'''

# Stuns removed from opendota api, temporarily reallocating stun points
# into damage/gpm/healing, weights in comments are intended, in code are temp

# Point total is out of 100
# Points assigned (1/2/3/4/5):
point_dict = {}

# TODO: Maybe use role weighting
# Laning Advantage (25/25/25/25/25)
# Gold at 5 (3/3/3/3/3)
# XP at 5 (3/3/3/3/3)
# LH at 5 (1/1/1/1/1)
# DN at 5 (1/1/1/1/1)
# Gold at 10 (7/7/7/7/7)
# XP at 10 (5/5/5/5/5)
# LH at 10 (3/3/3/3/3)
# DN at 10 (2/2/2/2/2)
point_dict['laning_gold_5'] = 3
point_dict['laning_xp_5'] = 3
point_dict['laning_lh_5'] = 1
point_dict['laning_dn_5'] = 1
point_dict['laning_gold_10'] = 7
point_dict['laning_xp_10'] = 5
point_dict['laning_lh_10'] = 3
point_dict['laning_dn_10'] = 2

# Combat Advantage (25/25/25/25/25)
# KDA to hero/lane average (15/15/15/10/10)
# Actual KDA ratio vs expected (5/5/5/6/6)
# Kills and assists vs team median (5/5/5/9/9)
point_dict['kda_hero_lane_average_1'] = 15
point_dict['kda_ratio_vs_expected_1'] = 5
point_dict['kill_assist_participation_1'] = 5
point_dict['kda_hero_lane_average_2'] = 15
point_dict['kda_ratio_vs_expected_2'] = 5
point_dict['kill_assist_participation_2'] = 5
point_dict['kda_hero_lane_average_3'] = 15
point_dict['kda_ratio_vs_expected_3'] = 5
point_dict['kill_assist_participation_3'] = 5
point_dict['kda_hero_lane_average_4'] = 12
point_dict['kda_ratio_vs_expected_4'] = 5
point_dict['kill_assist_participation_4'] = 8
point_dict['kda_hero_lane_average_5'] = 12
point_dict['kda_ratio_vs_expected_5'] = 5
point_dict['kill_assist_participation_5'] = 8

# Hero Damage Advantage (20/20/15/15/15)
# Hero damage per Minute percentile (15/15/10/10/10)
# Hero damage per Minute percentile ratio (5/5/5/5/5)
point_dict['hd_percentile_1'] = 15
point_dict['hd_percentile_mean_1'] = 5
point_dict['hd_percentile_2'] = 15
point_dict['hd_percentile_mean_2'] = 5
point_dict['hd_percentile_3'] = 15
point_dict['hd_percentile_mean_3'] = 5
point_dict['hd_percentile_4'] = 15
point_dict['hd_percentile_mean_4'] = 5
point_dict['hd_percentile_5'] = 15
point_dict['hd_percentile_mean_5'] = 5

# Farm Advantage (20/20/15/15/15)
# Last Hits per Minute percentile (4/4/4/4/4)
# Last Hits per Minute percentile mean (1/1/1/1/1)
# GPM to hero/lane average (8/8/4/4/4)
# Actual GPM ratio vs expected (2/2/1/1/1)
# XPM to hero/lane average (4/4/4/4/4)
# Actual XPM ratio vs expected (1/1/1/1/1)
point_dict['lh_percentile_1'] = 4
point_dict['lh_percentile_mean_1'] = 1
point_dict['gpm_vs_average_1'] = 8
point_dict['gpm_vs_expected_ratio_1'] = 2
point_dict['xpm_vs_average_1'] = 4
point_dict['xpm_vs_expected_ratio_1'] = 1
point_dict['lh_percentile_2'] = 4
point_dict['lh_percentile_mean_2'] = 1
point_dict['gpm_vs_average_2'] = 8
point_dict['gpm_vs_expected_ratio_2'] = 2
point_dict['xpm_vs_average_2'] = 4
point_dict['xpm_vs_expected_ratio_2'] = 1
point_dict['lh_percentile_3'] = 4
point_dict['lh_percentile_mean_3'] = 1
point_dict['gpm_vs_average_3'] = 8
point_dict['gpm_vs_expected_ratio_3'] = 2
point_dict['xpm_vs_average_3'] = 4
point_dict['xpm_vs_expected_ratio_3'] = 1
point_dict['lh_percentile_4'] = 4
point_dict['lh_percentile_mean_4'] = 1
point_dict['gpm_vs_average_4'] = 8
point_dict['gpm_vs_expected_ratio_4'] = 2
point_dict['xpm_vs_average_4'] = 4
point_dict['xpm_vs_expected_ratio_4'] = 1
point_dict['lh_percentile_5'] = 4
point_dict['lh_percentile_mean_5'] = 1
point_dict['gpm_vs_average_5'] = 8
point_dict['gpm_vs_expected_ratio_5'] = 2
point_dict['xpm_vs_average_5'] = 4
point_dict['xpm_vs_expected_ratio_5'] = 1

# Tower Damage Advantage (5/5/5/5/5)
# Tower Damage per Minute percentile (4/4/4/4/4)
# Tower Damage per Minute percentile mean (1/1/1/1/1)
point_dict['td_percentile_1'] = 4
point_dict['td_percentile_mean_1'] = 1
point_dict['td_percentile_2'] = 4
point_dict['td_percentile_mean_2'] = 1
point_dict['td_percentile_3'] = 4
point_dict['td_percentile_mean_3'] = 1
point_dict['td_percentile_4'] = 4
point_dict['td_percentile_mean_4'] = 1
point_dict['td_percentile_5'] = 4
point_dict['td_percentile_mean_5'] = 1

# Utility Advantage (5/5/15/15/15)
# Hero healing per Minute percentile (1/1/4/4/4)
# Hero healing per Minute percentile mean (1/1/1/1/1)
# Stuns per Minute percentile (2/2/8/8/8)
# Stuns per Minute percentile mean (1/1/2/2/2)
point_dict['hh_percentile_1'] = 3
point_dict['hh_percentile_mean_1'] = 2
#point_dict['stun_percentile_1'] = 2
#point_dict['stun_percentile_mean_1'] = 1
point_dict['hh_percentile_2'] = 3
point_dict['hh_percentile_mean_2'] = 2
#point_dict['stun_percentile_2'] = 2
#point_dict['stun_percentile_mean_2'] = 1
point_dict['hh_percentile_3'] = 3
point_dict['hh_percentile_mean_3'] = 2
#point_dict['stun_percentile_3'] = 8
#point_dict['stun_percentile_mean_3'] = 2
point_dict['hh_percentile_4'] = 3
point_dict['hh_percentile_mean_4'] = 2
#point_dict['stun_percentile_4'] = 8
#point_dict['stun_percentile_mean_4'] = 2
point_dict['hh_percentile_5'] = 3
point_dict['hh_percentile_mean_5'] = 2
#point_dict['stun_percentile_5'] = 8
#point_dict['stun_percentile_mean_5'] = 2