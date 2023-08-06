from collections import namedtuple


CalcContribMetric = namedtuple("CalcContribMetric", ["cc_name", "cc_func"])


# 2019 Events
# EVENT = "2019flwp"  # South Florida Regional
# EVENT = "2019orwil"  # Wilsonville PNW
#
# 2020 Events
# EVENT = "2020orore"  # Clackamas Academy PNW
#
# 2022 Events
# EVENT = "2022orore"  # Clackamas Academy PNW
# EVENT = "2022flwp"  # South Florida Regional


def cc_metric_my_opr(*, match_data, alliance):
    """Find the total score earned during the match"""
    return int(match_data["score_breakdown"][alliance]["totalPoints"])


def cc_metric_fouls(*, match_data, alliance):
    """Find the total score earned during the match"""
    alliance = "red" if alliance == "blue" else "blue"
    if match_data and match_data["score_breakdown"] and match_data["score_breakdown"][alliance] and match_data["score_breakdown"][alliance]["foulPoints"]:
        result = -1 * int(match_data["score_breakdown"][alliance]["foulPoints"])
    else:
        result = 0
    return result


def cc_metric_2020_power_cell(*, match_data, alliance):
    """Find the total cell points earned during the auto and teleop periods"""
    if int(match_data["score_breakdown"][alliance]["teleopCellPoints"]) and int(match_data["score_breakdown"][alliance]["autoCellPoints"]):
        t_cells = int(match_data["score_breakdown"][alliance]["teleopCellPoints"])
        a_cells = int(match_data["score_breakdown"][alliance]["autoCellPoints"])
        result = t_cells + a_cells
    else:
        result = 0
    return result


CC_METRICS = {
    "2022": [
        CalcContribMetric("FOUL", cc_metric_fouls),
        CalcContribMetric("MY_OPR", cc_metric_my_opr),
    ],
    "2020": [
        CalcContribMetric("PC", cc_metric_2020_power_cell),
        CalcContribMetric("FOUL", cc_metric_fouls),
        CalcContribMetric("MY_OPR", cc_metric_my_opr),
    ],
    "2019": [
        CalcContribMetric("FOUL", cc_metric_fouls),
        CalcContribMetric("MY_OPR", cc_metric_my_opr),
    ],
}

SORT_BY_COLUMNS = {
    "2022": ["FOUL", "MY_OPR"],
    "2020": ["PC", "FOUL", "MY_OPR"],
    "2019": ["FOUL", "MY_OPR"],
}
