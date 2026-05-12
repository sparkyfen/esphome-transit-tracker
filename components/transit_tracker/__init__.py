import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components.http_request import CONF_HTTP_REQUEST_ID, HttpRequestComponent
from esphome.components.display import Display
from esphome.components.font import Font
from esphome.components.time import RealTimeClock
from esphome.components import color
from esphome.const import CONF_ID, CONF_DISPLAY_ID, CONF_TIME_ID, CONF_SHOW_UNITS, __version__ as ESPHOME_VERSION

_MINIMUM_ESPHOME_VERSION = "2025.7.0"

DEPENDENCIES = ["network"]
AUTO_LOAD = ["json", "watchdog"]

transit_tracker_ns = cg.esphome_ns.namespace("transit_tracker")
TransitTracker = transit_tracker_ns.class_("TransitTracker", cg.Component)

UnitDisplay = transit_tracker_ns.enum("UnitDisplay")
UNIT_DISPLAY_VALUES = {
    "long": UnitDisplay.UNIT_DISPLAY_LONG,
    "short": UnitDisplay.UNIT_DISPLAY_SHORT,
    "none": UnitDisplay.UNIT_DISPLAY_NONE,
}

CONF_ROUTES = "routes"
CONF_STOPS = "stops"
CONF_BASE_URL = "base_url"
CONF_FONT_ID = "font_id"
CONF_LIMIT = "limit"
CONF_ABBREVIATIONS = "abbreviations"
CONF_STYLES = "styles"
CONF_FEED_CODE = "feed_code"
CONF_DEFAULT_ROUTE_COLOR = "default_route_color"
CONF_TIME_DISPLAY = "time_display"
CONF_LIST_MODE = "list_mode"
CONF_SCROLL_HEADSIGNS = "scroll_headsigns"
CONF_TRIPS_PER_PAGE = "trips_per_page"
CONF_PAGE_CYCLE_DURATION = "page_cycle_duration"
CONF_SHOW_REMAINING_TRIPS = "show_remaining_trips"
CONF_REMAINING_TRIPS_THRESHOLD = "remaining_trips_threshold"
CONF_PRESETS = "presets"
CONF_DEFAULT_PRESET = "default_preset"
CONF_SIGN_LOCATION = "sign_location"
CONF_WALK_SPEED_MS = "walk_speed_ms"


def validate_ws_url(value):
    url = cv.url(value)
    if not value.startswith("ws://") and not value.startswith("wss://"):
        raise cv.Invalid("URL must start with 'ws://' or 'wss://")

    return url


def validate_esphome_version(obj):
    if cv.Version.parse(ESPHOME_VERSION) < cv.Version.parse(_MINIMUM_ESPHOME_VERSION):
        raise cv.Invalid(
            "The transit_tracker component requires ESPHome version " +
            f"{_MINIMUM_ESPHOME_VERSION} or later."
        )
    return obj


CONFIG_SCHEMA = cv.All(
    validate_esphome_version,
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(TransitTracker),
            cv.GenerateID(CONF_DISPLAY_ID): cv.use_id(Display),
            cv.GenerateID(CONF_FONT_ID): cv.use_id(Font),
            cv.GenerateID(CONF_TIME_ID): cv.use_id(RealTimeClock),
            cv.Optional(CONF_BASE_URL): validate_ws_url,
            cv.Optional(CONF_LIMIT, default=3): cv.positive_int,
            cv.Optional(CONF_FEED_CODE, default=""): cv.string,
            cv.Optional(CONF_TIME_DISPLAY, default="departure"): cv.one_of(
                "departure", "arrival"
            ),
            cv.Optional(CONF_LIST_MODE, default="sequential"): cv.one_of(
                "sequential", "nextPerRoute"
            ),
            cv.Optional(CONF_SCROLL_HEADSIGNS, default=False) : cv.boolean,
            cv.Optional(CONF_TRIPS_PER_PAGE): cv.positive_int,
            cv.Optional(CONF_PAGE_CYCLE_DURATION, default="5s"): cv.time_period,
            cv.Optional(CONF_SHOW_REMAINING_TRIPS, default=False): cv.boolean,
            cv.Optional(CONF_REMAINING_TRIPS_THRESHOLD, default=-1): cv.int_,
            cv.Optional(CONF_STOPS, default=[]): cv.ensure_list(
                cv.Schema(
                    {
                        cv.Required("stop_id"): cv.string,
                        cv.Optional("time_offset", default="0s"): cv.time_period,
                        cv.Required(CONF_ROUTES): cv.ensure_list(cv.string),
                    }
                )
            ),
            cv.Optional(CONF_SHOW_UNITS, default="long"): cv.enum(UNIT_DISPLAY_VALUES),
            cv.Optional(CONF_DEFAULT_ROUTE_COLOR): cv.use_id(color.ColorStruct),
            cv.Optional(CONF_STYLES): cv.ensure_list(
                cv.Schema(
                    {
                        cv.Required("route_id"): cv.string,
                        cv.Required("name"): cv.string,
                        cv.Required("color"): cv.use_id(color.ColorStruct),
                    }
                )
            ),
            cv.Optional(CONF_ABBREVIATIONS): cv.ensure_list(
                cv.Schema(
                    {
                        cv.Required("from"): cv.string,
                        cv.Required("to"): cv.string,
                    }
                )
            ),
            # Optional preset definitions. When provided, each preset has its
            # own set of stops/routes; the active preset can be switched at
            # runtime via set_active_preset() (typically driven from a HA
            # select entity). When omitted, the top-level `stops` list is
            # used as a single implicit "default" preset.
            cv.Optional(CONF_PRESETS): cv.ensure_list(
                cv.Schema(
                    {
                        cv.Required("name"): cv.string,
                        cv.Required(CONF_STOPS): cv.ensure_list(
                            cv.Schema(
                                {
                                    cv.Required("stop_id"): cv.string,
                                    cv.Optional(
                                        "time_offset", default="0s"
                                    ): cv.time_period,
                                    cv.Required(CONF_ROUTES): cv.ensure_list(
                                        cv.string
                                    ),
                                }
                            )
                        ),
                    }
                )
            ),
            cv.Optional(CONF_DEFAULT_PRESET): cv.string,
            cv.Optional(CONF_SIGN_LOCATION): cv.Schema(
                {
                    cv.Required("lat"): cv.float_,
                    cv.Required("lon"): cv.float_,
                }
            ),
            cv.Optional(CONF_WALK_SPEED_MS, default=1.4): cv.float_range(
                min=0.1, max=10
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
)


def _generate_schedule_string(stops):
    return ";".join(
        [
            f"{route},{stop['stop_id']},{stop['time_offset'].total_seconds}"
            for stop in stops
            for route in stop[CONF_ROUTES]
        ]
    )


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])

    drawing_display = await cg.get_variable(config[CONF_DISPLAY_ID])
    cg.add(var.set_display(drawing_display))

    font = await cg.get_variable(config[CONF_FONT_ID])
    cg.add(var.set_font(font))

    time = await cg.get_variable(config[CONF_TIME_ID])
    cg.add(var.set_rtc(time))

    if CONF_BASE_URL in config:
        cg.add(var.set_base_url(config[CONF_BASE_URL]))

    cg.add(var.set_feed_code(config[CONF_FEED_CODE]))

    # Build the preset map. If `presets:` is provided, register each one and
    # mark the default. Otherwise fall back to a single implicit "default"
    # preset from the top-level `stops:` for backwards compatibility.
    if CONF_PRESETS in config:
        preset_names = [p["name"] for p in config[CONF_PRESETS]]
        for preset in config[CONF_PRESETS]:
            cg.add(
                var.add_preset(
                    preset["name"],
                    _generate_schedule_string(preset[CONF_STOPS]),
                )
            )
        default_preset = config.get(CONF_DEFAULT_PRESET, preset_names[0])
        if default_preset not in preset_names:
            raise cv.Invalid(
                f"default_preset '{default_preset}' is not in the presets list"
            )
        cg.add(var.set_default_preset(default_preset))
    else:
        cg.add(
            var.add_preset(
                "default", _generate_schedule_string(config[CONF_STOPS])
            )
        )
        cg.add(var.set_default_preset("default"))

    if CONF_SIGN_LOCATION in config:
        cg.add(
            var.set_sign_location(
                config[CONF_SIGN_LOCATION]["lat"],
                config[CONF_SIGN_LOCATION]["lon"],
            )
        )

    cg.add(var.set_walk_speed_ms(config[CONF_WALK_SPEED_MS]))

    display_departure_times = config[CONF_TIME_DISPLAY] == "departure"
    cg.add(var.set_display_departure_times(display_departure_times))

    cg.add(var.set_list_mode(config[CONF_LIST_MODE]))
    cg.add(var.set_scroll_headsigns(config[CONF_SCROLL_HEADSIGNS]))
    cg.add(var.set_show_remaining_trips(config[CONF_SHOW_REMAINING_TRIPS]))
    cg.add(var.set_remaining_trips_threshold(config[CONF_REMAINING_TRIPS_THRESHOLD]))

    if CONF_TRIPS_PER_PAGE in config:
        cg.add(var.set_trips_per_page(config[CONF_TRIPS_PER_PAGE]))

    page_cycle_duration_ms = int(config[CONF_PAGE_CYCLE_DURATION].total_seconds * 1000)
    cg.add(var.set_page_cycle_duration(page_cycle_duration_ms))

    cg.add(var.set_limit(config[CONF_LIMIT]))

    cg.add(var.set_unit_display(config[CONF_SHOW_UNITS]))

    if CONF_ABBREVIATIONS in config:
        for abbreviation in config[CONF_ABBREVIATIONS]:
            cg.add(var.add_abbreviation(abbreviation["from"], abbreviation["to"]))

    if CONF_DEFAULT_ROUTE_COLOR in config:
        cg.add(
            var.set_default_route_color(
                await cg.get_variable(config[CONF_DEFAULT_ROUTE_COLOR])
            )
        )

    if CONF_STYLES in config:
        for style in config[CONF_STYLES]:
            color_struct = await cg.get_variable(style["color"])
            cg.add(var.add_route_style(style["route_id"], style["name"], color_struct))

    await cg.register_component(var, config)

    cg.add_library("NetworkClientSecure", None)
    cg.add_library("HTTPClient", None)

    # Fork contains patch for TLS issue - https://github.com/gilmaimon/ArduinoWebsockets/pull/142
    cg.add_library(
        "ArduinoWebsockets", None, "https://github.com/tjhorner/ArduinoWebsockets"
    )
