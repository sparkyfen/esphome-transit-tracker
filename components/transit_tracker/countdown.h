#pragma once

namespace esphome {
namespace transit_tracker {

// Decides whether a trip is drawn as the last-trip countdown.
//
// Only the GTFS-static tripsRemainingToday count is authoritative: a zero
// there means no later trip exists for the rest of the service day. The
// remainingTrips fallback (count within the API response window) is not
// enough; a zero there only means "last trip we were sent", so it is not
// consulted here. window_seconds <= 0 disables the feature.
inline bool last_trip_countdown_active(int trips_remaining_today, int seconds_until, int window_seconds) {
  return window_seconds > 0 && trips_remaining_today == 0 && seconds_until <= window_seconds;
}

}  // namespace transit_tracker
}  // namespace esphome
