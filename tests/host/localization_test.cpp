// Host-side checks for the duration formatters. Build and run with
// tests/host/run.sh; no ESPHome toolchain needed.
#include <cstdio>
#include <string>

#include "localization.h"

using esphome::transit_tracker::Localization;
using esphome::transit_tracker::UNIT_DISPLAY_SHORT;

static int failures = 0;

static void expect_eq(const std::string &got, const std::string &want, const char *what) {
  if (got != want) {
    std::printf("FAIL %s: got \"%s\", want \"%s\"\n", what, got.c_str(), want.c_str());
    failures++;
  } else {
    std::printf("ok   %s -> \"%s\"\n", what, got.c_str());
  }
}

int main() {
  Localization loc;
  loc.set_unit_display(UNIT_DISPLAY_SHORT);
  const uint now = 1'700'000'000;

  // Countdown shows minutes and zero-padded seconds.
  expect_eq(loc.fmt_countdown(now + 247, now), "4:07", "countdown 4m07s");
  expect_eq(loc.fmt_countdown(now + 600, now), "10:00", "countdown 10m00s");
  expect_eq(loc.fmt_countdown(now + 59, now), "0:59", "countdown under a minute");
  expect_eq(loc.fmt_countdown(now + 5, now), "0:05", "countdown single digit seconds");
  // Once the time has passed it reads like the normal formatter does.
  expect_eq(loc.fmt_countdown(now, now), "Now", "countdown at zero");
  expect_eq(loc.fmt_countdown(now - 3, now), "Now", "countdown past");

  // The normal formatter is unchanged.
  expect_eq(loc.fmt_duration_from_now(now + 247, now), "4m", "duration 4m");
  expect_eq(loc.fmt_duration_from_now(now + 10, now), "Now", "duration under 30s");
  expect_eq(loc.fmt_duration_from_now(now + 3900, now), "1h5m", "duration over an hour");

  if (failures) {
    std::printf("%d failure(s)\n", failures);
    return 1;
  }
  std::printf("all passed\n");
  return 0;
}
