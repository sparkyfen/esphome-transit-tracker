# Testing Guide: Page Cycling & Remaining Trips Features

This guide covers testing the changes from PR #6 (page cycling) and the ESP-side support for PR #7 (remaining trips indicator).

## Prerequisites

### 1. Activate ESPHome Virtual Environment

```bash
source ~/.esphome-venv/bin/activate
```

### 2. Verify ESPHome is Working

```bash
esphome version
```

## Testing the Firmware

### Step 1: Configure WiFi

Edit `examples/matrix-portal-s3-cycling.yaml` and update lines 28-29 with your WiFi credentials:

```yaml
wifi:
  ssid: "YourActualSSID"
  password: "YourActualPassword!"
```

### Step 2: Compile and Flash

Connect your Matrix Portal S3 via USB, then:

```bash
cd /home/sparky/Documents/Code/workspaces/transit-tracker/esphome-transit-tracker

# Compile and flash in one step
esphome run examples/matrix-portal-s3-cycling.yaml
```

Or separate steps:

```bash
esphome compile examples/matrix-portal-s3-cycling.yaml
esphome upload examples/matrix-portal-s3-cycling.yaml
```

### Step 3: Monitor Logs

```bash
esphome logs examples/matrix-portal-s3-cycling.yaml
```

## What to Test

### Feature 1: Page Cycling (PR #6)

The `matrix-portal-s3-cycling.yaml` config has these settings enabled:

```yaml
trips_per_page: 1
page_cycle_duration: 5s
```

**Verify:**
- [ ] Display shows 1 trip at a time (not all trips stacked)
- [ ] Display cycles to next trip every 5 seconds
- [ ] Single trip is vertically centered on the matrix
- [ ] Transitions are smooth without display glitches
- [ ] After showing all trips, it loops back to the first

**Test variations:**
- Try `trips_per_page: 2` to show 2 trips per page
- Try `page_cycle_duration: 3s` for faster cycling

### Feature 2: Remaining Trips Indicator (PR #7 ESP support)

Edit `examples/matrix-portal-s3-cycling.yaml` and uncomment line 92:

```yaml
show_remaining_trips: true
```

Reflash and verify:
- [ ] Display shows `(-N)` next to arrival times
- [ ] `N` correctly indicates how many more trips follow
- [ ] Last trip of the day shows `(-0)` or no indicator

## Testing Against Local API (Optional)

To test with a local API instance instead of the production server:

### 1. Start the API

```bash
cd /home/sparky/Documents/Code/workspaces/transit-tracker/transit-tracker-api
pnpm install
docker compose -f docker-compose.dev.yml up -d
pnpm gtfs:db:migrate
pnpm start:dev
```

### 2. Update ESP Config

Change `base_url` in your YAML to point to your local machine's IP:

```yaml
transit_tracker:
  base_url: "ws://192.168.x.x:3000/"  # Replace with your LAN IP
```

### 3. Reflash and Test

The ESP should now connect to your local API instance.

## Troubleshooting

### ESPHome not found
```bash
source ~/.esphome-venv/bin/activate
```

### Device not detected
- Check USB cable (must be data-capable, not charge-only)
- Try `ls /dev/ttyUSB*` or `ls /dev/ttyACM*` to find the port
- You may need to add yourself to the `dialout` group: `sudo usermod -aG dialout $USER` (then log out/in)

### WiFi connection failures
- Check the serial logs for connection errors
- Verify SSID and password are correct
- The fallback hotspot "TransitTracker Fallback Hotspot" will appear if WiFi fails

### WebSocket connection issues
- Verify `base_url` starts with `ws://` or `wss://`
- Check that the API server is reachable from the device's network
