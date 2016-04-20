#include<map>

enum stats_t{
  ENQ_STEAL_SUCC,
  ENQ_STEAL_FAIL,
  ENQ_SUCC,
  ENQ_FAIL,
  DEQ_STEAL_SUCC,
  DEQ_STEAL_FAIL,
  DEQ_PHY_SUCC,
  DEQ_PHY_FAIL,
  DEQ_LOG_SUCC,
  DEQ_LOG_FAIL,
  NUM_STATS
};

std::map<int, std::string> stat_map {
  std::make_pair (0, "ENQ_STEAL_SUCC"),
  std::make_pair (1, "ENQ_STEAL_FAIL"),
  std::make_pair (2, "ENQ_SUCC      "),
  std::make_pair (3, "ENQ_FAIL      "),
  std::make_pair (4, "DEQ_STEAL_SUCC"),
  std::make_pair (5, "DEQ_STEAL_FAIL"),
  std::make_pair (6, "DEQ_PHY_SUCC  "),
  std::make_pair (7, "DEQ_PHY_FAIL  "),
  std::make_pair (8, "DEQ_LOG_SUCC  "),
  std::make_pair (9, "DEQ_LOG_FAIL  "),
};
