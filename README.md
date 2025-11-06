[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

![HA EnergyUA](https://raw.githubusercontent.com/kihoro2d/ha-energyua/main/icons/icon.png)

# ⚡️ HA EnergyUA

An integration for electricity outages based on data from [EnergyUA][energyua].

This integration for [Home Assistant][home-assistant] provides information about planned electricity outages.
It is based on messages posted by a community driven project [EnergyUA][energyua].

**💡 Note:** This project is not affiliated with [EnergyUA][energyua] in any way. This integration is developed by an individual.
Provided data may be incorrect or misleading, follow the official channels for reliable information.

> This integration is inspired by [ha-yasno-outages](https://github.com/denysdovhan/ha-yasno-outages) by [Denys Dovhan](https://github.com/denysdovhan) and [ha-lviv-poweroff](https://github.com/tsdaemon/ha-lviv-poweroff) by [Anatolii Stehnii](https://github.com/tsdaemon).

## Installation

The quickest way to install this integration is via [HACS][hacs-url] by clicking the button below:

[![Add to HACS via My Home Assistant][hacs-install-image]][hasc-install-url]

If it doesn't work, adding this repository to HACS manually by adding this URL:

1. Visit **HACS** → **Integrations** → **...** (in the top right) → **Custom repositories**
1. Click **Add**
1. Paste `https://github.com/kihoro2d/ha-energyua` into the **URL** field
1. Chose **Integration** as a **Category**
1. **EnergyUA** will appear in the list of available integrations. Install it normally.

## Usage

This integration is configurable via UI. On **Devices and Services** page, click **Add Integration** and search for **EnergyUA**.

1. Select your region
2. Select your group

Find your group by visiting [EnergyUA][energyua] website and typing your address in the search bar.

Then you can add the integration to your dashboard and see the information about the next planned outages.

![Sensors](https://raw.githubusercontent.com/kihoro2d/ha-energyua/main/media/example_sensors.png)

Integration also provides a calendar view of planned outages. You can add it to your dashboard as well via [Calendar card][calendar-card].

![Calendar](https://raw.githubusercontent.com/kihoro2d/ha-energyua/main/media/example_calendar.png)

<!-- References -->

[energyua]: https://energy-ua.info/
[home-assistant]: https://www.home-assistant.io/
[hacs-url]: https://github.com/hacs/integration
[hasc-install-url]: https://my.home-assistant.io/redirect/hacs_repository/?owner=kihoro2d&repository=ha-energyua&category=integration
[hacs-install-image]: https://my.home-assistant.io/badges/hacs_repository.svg
[calendar-card]: https://www.home-assistant.io/dashboards/calendar/
