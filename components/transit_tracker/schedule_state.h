#pragma once

#include <climits>
#include <vector>
#include <mutex>

#include "esphome/components/display/display.h"

namespace esphome {
namespace transit_tracker {

class Trip {
  public:
    std::string route_id;
    std::string route_name;
    Color route_color;
    std::string headsign;
    time_t arrival_time;
    time_t departure_time;
    bool is_realtime;
    // Number of trips remaining after this one for the same route/stop today.
    // -1 if not available from API
    int remaining_trips;
    // Trips remaining for the rest of the GTFS service day for the same
    // route/stop. Set by GTFS-static providers; -1 when unavailable
    // (OBA-backed feeds), in which case consumers should fall back to
    // remaining_trips.
    int trips_remaining_today;
    // Realtime prediction delay vs static schedule, in seconds. Positive =
    // late, negative = early. INT_MIN when no realtime data is available
    // (use is_realtime to gate display).
    int delay_seconds;
};

class ScheduleState {
  public:
    std::mutex mutex;
    std::vector<Trip> trips;
};

} // namespace transit_tracker
} // namespace esphome