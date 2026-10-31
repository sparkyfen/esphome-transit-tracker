#!/usr/bin/env sh
# Builds and runs the host-side formatter test with the system C++ compiler.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
comp="$here/../../components/transit_tracker"
out="${TMPDIR:-/tmp}/transit_tracker_localization_test"
c++ -std=c++17 -Wall -I "$here/stubs" -I "$comp" \
  "$here/localization_test.cpp" "$comp/localization.cpp" -o "$out"
"$out"
