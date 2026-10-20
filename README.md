# Neakasa Integration for Home Assistant 🏠

[![GitHub Release](https://img.shields.io/github/v/release/bernysk/hass-neakasa?sort=semver&style=for-the-badge&color=green)](https://github.com/bernysk/hass-neakasa/releases/)
[![GitHub Release Date](https://img.shields.io/github/release-date/bernysk/hass-neakasa?style=for-the-badge&color=green)](https://github.com/bernysk/hass-neakasa/releases/)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/bernysk/hass-neakasa/latest/total?style=for-the-badge&label=Downloads%20latest%20Release)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/bernysk/hass-neakasa?style=for-the-badge)
[![hacs](https://img.shields.io/badge/HACS-Integration-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)

## Important note ##

This is a copy of the original Neakasa integration by @timniklas, whose repository is no longer available. This fork is kept for personal use and for experimenting with AI-assisted development. It is not actively maintained for others, so use it at your own risk.

## Overview

The Neakasa Home Assistant Custom Integration allows you to integrate your Neakasa devices with your Home Assistant setup.

### Currently supported devices
- Neakasa M1 (Cat Litter Box)

### Currently supported features
#### Sensors:
|Sensor|Unit|Example Value|Enabled by default|
|------|-------------|------|------|
|Cat litter level|percent|80 %|yes|
|WiFi RSS|dB|-60 dB|no (debug information)|
|Last stay time|seconds|45 s|no|
|Last usage|datetime|2024-12-07 14:52|yes|
|Device status|idle / cleaning / leveling / flipover / cat_present / paused / side_bin_locking_panels_missing / cleaning_interrupted|idle|yes|
|Cat litter state|insufficient / moderate / sufficient|sufficient|yes|
|Bin state|normal / full / missing|normal|yes|
|Cat {name}|kg|3.8|yes|

One "Cat {name}" sensor is created per cat on the account, including cats added later in the app. It shows the weight from the cat's most recent visit and is empty when there was no visit within the statistics lookback (see [Options](#options)).

#### Binary sensors:
|Binary Sensor|Example Value|Enabled by default|
|-------------|-------------|------------------|
|Garbage can full|off|yes|

#### Buttons:
|Button|Action|Enabled by default|
|------|------|------------------|
|Clean|Cleans the litter box|yes|
|Level|Initiates the leveling process|yes|

#### Switches:
|Switch|Enabled by default|
|------|------------------|
|Auto clean|yes|
|Kitten mode|no (rare edgecase)|
|Child lock|yes|
|Automatic cover|yes|
|Automatic leveling|yes|
|Silent mode|yes|
|Automatic recovery|no (potentialy dangerous!)|
|Unstoppable cycle|yes|

## Installation

### HACS (recommended)

This integration can be installed via HACS (Home Assistant Community Store) as a custom repository.

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant
3. Go to any of the sections (integrations, frontend, automation).
4. Click on the 3 dots in the top right corner.
5. Select "Custom repositories"
6. Add following URL to the repository `https://github.com/bernysk/hass-neakasa`.
7. Select Integration as category.
8. Click the "ADD" button
9. Search for "Neakasa"
10. Click the "Download" button

### Manual installation

#### from downloaded zip archive
To install this integration manually you have to download [_neakasa.zip_](https://github.com/bernysk/hass-neakasa/releases/latest/) and extract its contents to `config/custom_components/neakasa` directory:

```bash
mkdir -p custom_components/neakasa
cd custom_components/neakasa
wget https://github.com/bernysk/hass-neakasa/releases/latest/download/neakasa.zip
unzip neakasa.zip
rm neakasa.zip
```
restart Home Assistant.

#### Installation from git repository

with this variant, you can easily update the integration from the github repository.

##### First installation:

```bash
cd <to your Home Assistant config directory>
git clone https://github.com/bernysk/hass-neakasa
mkdir custom_components
cd custom_components
ln -s ../hass-neakasa/custom_components/neakasa/ .
```

restart Home Assistant.

##### update the existing installation:

```bash
cd <to your Home Assistant config directory>
cd hass-neakasa/
git pull
```

restart Home Assistant.


## Configuration

### Using UI

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=neakasa)

From the Home Assistant front page go to `Configuration` and then select `Devices & Services` from the list.
Use the `Add Integration` button in the bottom right to add a new integration called `Neakasa`.

Enter your Neakasa account credentials. One entry covers every litter box on the account.

### Options

Open the integration and choose `Configure` to change:

|Option|Default|Range|Description|
|------|-------|-----|-----------|
|Polling interval|60 s|30–300 s|How often the Neakasa cloud is polled.|
|Statistics lookback|7 days|1–30 days|How many days of visits are loaded for the cat weight sensors.|

### Changing credentials

- If your password changes, Home Assistant asks you to re-authenticate the integration.
- To switch the entry to another account, use `Reconfigure` on the integration.

Entries created by old versions (one per litter box) are merged automatically into a single entry per account; existing entities and their history are kept.

## Troubleshooting Tips / Known Issues

1. When you discover  that the mobile app is starting over and over, beginning again with the login steps, then you should use this HA integration with a different account than with the app. Create a second account and use the share function in the app - simply share the device with the second account
2. powercycle the litterbox
3. reset the litterbox and reintegrate it
4. open an issue

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Support and Contributions

This fork is maintained for personal use only, so there is no support and no promise of fixes or new features.
You are welcome to fork it and adapt it to your needs. Pull requests may be looked at occasionally, but may not be reviewed or merged.

## Disclaimer

This custom integration is not officially endorsed or supported by Neakasa.
Use it at your own risk and ensure that you comply with all relevant terms of service and privacy policies.
