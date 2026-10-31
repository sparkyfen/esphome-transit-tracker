// Host-test stand-in for the ESPHome header that localization.h pulls in.
// Provides only what localization.cpp uses: str_sprintf and the uint alias.
#pragma once

#include <cstdarg>
#include <cstdio>
#include <string>
#include <sys/types.h>

namespace esphome {

inline std::string str_sprintf(const char *fmt, ...) {
  char buf[128];
  va_list args;
  va_start(args, fmt);
  vsnprintf(buf, sizeof(buf), fmt, args);
  va_end(args);
  return std::string(buf);
}

}  // namespace esphome
