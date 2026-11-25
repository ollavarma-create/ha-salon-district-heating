# Salon District Heating for Home Assistant

[![Status: Planning](https://img.shields.io/badge/status-planning-blue)](#project-status)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An **unofficial, open-source Home Assistant integration** for the **Salon Kaukolämpö LämpöVahti API**, intended to help district-heating customers monitor their energy use and understand their heating system.

> **Project status: planning / initial development.** No installable integration is available yet. This project is independent of Salon Kaukolämpö and is not endorsed or supported by the utility.

## Goals

- Authenticate using a user-provided LämpöVahti API key.
- Discover the locations available to that key.
- Retrieve hourly district-heating energy consumption and available meter measurements.
- Expose suitable Home Assistant entities and support long-term energy analysis.
- Handle historical readings, API pagination, missing measurements and subsequently revised data responsibly.
- Eventually provide a straightforward installation path, potentially through HACS.

## Available API data

The published OpenAPI 3.0.3 specification describes the following fields:

| Field | Meaning | Unit |
| --- | --- | --- |
| `consumption` | Energy consumed in the measurement interval (hourly readings) | Wh |
| `reading_total` | Cumulative energy meter reading; nullable | Wh |
| `flow_temperature` | District-heating supply temperature; nullable | °C |
| `return_temperature` | District-heating return temperature; nullable | °C |
| `flow` | Flow rate; nullable | m³/h |
| `date` | Measurement timestamp | UTC ISO 8601 |
| `status` | `read` (actual) or `estimated` (gap-filled) | — |
| `modified_at` | Timestamp of last modification; nullable | UTC ISO 8601 |
| `location_id` | Location identifier | — |
| `serial_number` | Meter serial number, if available | — |

See [API data reference](docs/API_DATA.md) for the exact endpoint and pagination details, and [architecture](docs/ARCHITECTURE.md) for design decisions still to be validated.

## API documentation

Official Swagger documentation: https://api-lampovahti.salonkaukolampo.fi/external/api/docs/

The OpenAPI specification defines a server base path of `/external/api` and these routes:

- `GET /external/api/v1/locations/` — accessible locations
- `GET /external/api/v1/consumptions/` — hourly consumption records

Authentication: `X-API-Key` HTTP request header. API keys are created in the LämpöVahti account. Published limits: **60 requests/minute and 10,000 requests/day per API key** (HTTP 429 when exceeded).

**Never commit API keys, customer addresses, meter serial numbers, raw account responses or other personal information.**

## Installation

**Not available yet.** The repository currently contains planning and API documentation only. Please do not attempt to add it as a Home Assistant custom integration until code and installation instructions are published.

## Roadmap

- [x] Establish repository and license
- [x] Document API response models and integration design
- [ ] Implement an API client with authentication, pagination, errors and tests
- [ ] Add Home Assistant config flow and per-location devices/entities
- [ ] Validate sensor units, availability, statistics and Energy Dashboard compatibility
- [ ] Test initial history import and handling of revised readings
- [ ] Test on a real Home Assistant installation
- [ ] Publish an initial pre-release and installation instructions
- [ ] Evaluate HACS support

## Development and contributions

Feedback, reproducible bug reports and pull requests are welcome as development progresses. Please remove credentials and identifying meter/location information from logs and screenshots before sharing them.

## License

MIT — see [LICENSE](LICENSE). API documentation and the LämpöVahti service belong to their respective owners.

### Hourly data quality (alpha.4)
Hourly energy and average power retain the last verified API value for up to two hours from its measurement time. See **Consumption measurement time** and **Data quality** for freshness. No interpolation is used. Do not use hourly values as the sole input for real-time heating control or safety functions. See [measurement limitations](docs/CONSUMPTION_INTEGRITY.md).
