#pragma once

#include <map>
#include <ArduinoWebsockets.h>

#include "esphome/core/component.h"
#include "esphome/components/display/display.h"
#include "esphome/components/font/font.h"
#include "esphome/components/time/real_time_clock.h"

#include "schedule_state.h"
#include "localization.h"

namespace esphome {
namespace transit_tracker {

struct RouteStyle {
  std::string name;
  Color color;
};

class TransitTracker : public Component {
  public:
    void setup() override;
    void loop() override;
    void dump_config() override;
    void on_shutdown() override;

    float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }

    void reconnect();
    void close(bool fully = false);

    void draw_schedule();

    Localization* get_localization() { return &this->localization_; }

    void set_display(display::Display *display) { display_ = display; }
    void set_font(font::Font *font) { font_ = font; }
    void set_rtc(time::RealTimeClock *rtc) { rtc_ = rtc; }

    void set_base_url(const std::string &base_url) { base_url_ = base_url; }
    void set_feed_code(const std::string &feed_code) { feed_code_ = feed_code; }
    void set_display_departure_times(bool display_departure_times) { display_departure_times_ = display_departure_times; }
    void set_list_mode(const std::string &list_mode) { list_mode_ = list_mode; }

    // Preset configuration. add_preset() registers a (name -> schedule string)
    // mapping at codegen time. set_default_preset() picks which preset is
    // active before any user selection / NVS-restored value is applied.
    // set_active_preset() switches the active preset at runtime, persists it,
    // and triggers a WS reconnect so the new schedule subscription takes
    // effect immediately.
    void add_preset(const std::string &name, const std::string &schedule_string) {
      presets_[name] = schedule_string;
    }
    void set_default_preset(const std::string &name) {
      default_preset_ = name;
      if (active_preset_.empty()) {
        active_preset_ = name;
      }
    }
    void set_active_preset(const std::string &name);
    const std::string &get_active_preset() const { return active_preset_; }

    // Optional walking-time configuration. When sign_location is set, the
    // firmware sends walkingFrom + walkSpeedMs in the WS subscription so the
    // server applies per-stop walking-time offsets. When unset, behavior is
    // unchanged.
    void set_sign_location(float lat, float lon) {
      sign_lat_ = lat;
      sign_lon_ = lon;
      has_sign_location_ = true;
    }
    void set_walk_speed_ms(float speed) { walk_speed_ms_ = speed; }
    void set_limit(int limit) { limit_ = limit; }
    void set_scroll_headsigns(bool scroll_headsigns) { scroll_headsigns_ = scroll_headsigns; }
    void set_trips_per_page(int trips_per_page) { trips_per_page_ = trips_per_page; }
    void set_page_cycle_duration(int page_cycle_duration) { page_cycle_duration_ = page_cycle_duration; }
    void set_show_remaining_trips(bool show_remaining_trips) { show_remaining_trips_ = show_remaining_trips; }
    void set_remaining_trips_threshold(int threshold) { remaining_trips_threshold_ = threshold; }

    void set_unit_display(UnitDisplay unit_display) { this->localization_.set_unit_display(unit_display); }
    void add_abbreviation(const std::string &from, const std::string &to) { abbreviations_[from] = to; }
    void set_default_route_color(const Color &color) { default_route_color_ = color; }
    void add_route_style(const std::string &route_id, const std::string &name, const Color &color) { route_styles_[route_id] = RouteStyle{name, color}; }

    void set_abbreviations_from_text(const std::string &text);
    void set_route_styles_from_text(const std::string &text);

  protected:
    static constexpr int scroll_speed = 10; // pixels/second
    static constexpr int idle_time_left = 5000;
    static constexpr int idle_time_right = 1000;

    std::string from_now_(time_t unix_timestamp, uint rtc_now) const;
    void draw_text_centered_(const char *text, Color color);
    void draw_realtime_icon_(int bottom_right_x, int bottom_right_y, unsigned long now);

    void draw_trip(
      const Trip &trip, int y_offset, int font_height, unsigned long uptime, uint rtc_now,
      bool no_draw = false, int *headsign_overflow_out = nullptr, int scroll_cycle_duration = 0
    );

    Localization localization_{};
    ScheduleState schedule_state_;

    display::Display *display_;
    font::Font *font_;
    time::RealTimeClock *rtc_;

    websockets::WebsocketsClient ws_client_{};

    void on_ws_message_(websockets::WebsocketsMessage message);
    void on_ws_event_(websockets::WebsocketsEvent event, String data);
    void connect_ws_();
    int connection_attempts_ = 0;
    unsigned long last_heartbeat_ = 0;
    bool has_ever_connected_ = false;
    bool fully_closed_ = false;

    std::string base_url_;
    std::string feed_code_;
    std::string list_mode_;
    bool display_departure_times_ = true;
    int limit_;

    // Preset state. Populated at codegen via add_preset().
    // Persistence across reboots is handled by the user's select entity
    // (restore_value: true), not this component.
    std::map<std::string, std::string> presets_;
    std::string default_preset_;
    std::string active_preset_;

    // Walking-time origin (only sent when has_sign_location_).
    bool has_sign_location_ = false;
    float sign_lat_ = 0;
    float sign_lon_ = 0;
    float walk_speed_ms_ = 1.4f;

    // Page cycling configuration
    // trips_per_page_ = -1 means show all trips (uses limit_ value for backward compatibility)
    // When set to a positive value, display will cycle through pages of trips
    int trips_per_page_ = -1;
    int page_cycle_duration_ = 5000;  // milliseconds per page

    std::map<std::string, std::string> abbreviations_;
    Color default_route_color_ = Color(0x028e51);
    std::map<std::string, RouteStyle> route_styles_;
    bool scroll_headsigns_ = false;
    bool show_remaining_trips_ = false;  // Display "(-N)" indicator for remaining trips
    // Suppress (-N) when the count is greater than this value, so the indicator
    // only appears as service is running thin. -1 means always show.
    int remaining_trips_threshold_ = -1;
};


}  // namespace transit_tracker
}  // namespace esphome