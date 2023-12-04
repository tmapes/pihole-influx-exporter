# pihole-influx-exporter

Allows visualising many of the graphs seen on the Pi-Hole dashboard, in Grafana for an expanded historical view of your DNS metrics. 

### Configuration

A few environment variables are required to get this up and running.

| Name | Default | Required | Description |
| ---- | ------- | -------- | ----------- |
| PI_HOLE_HOST | `localhost:8081` | Yes | Hostname & Port of your PiHole|
| PI_HOLE_API_TOKEN | `<no default>` | Yes | API Token for accessing PiHole |
| PI_HOLE_USE_HTTP | `false` | No | Set to true to connect to your PiHole over HTTP |
| INFLUX_URL | `http://localhost:8086` | Yes | Schema, Hostname, & Port of your Influx Instance |
| INFLUX_DATABASE | `metrics` | No | What Influx database to write into |

### Metrics

Below are the metrics that are created from this repository.

All metrics are tagged as `pi_hole_host` with the `PI_HOLE_HOST` value.

`pi_hole`

  - No Tags
  - Fields:
    - `ads_blocked_today` - int - Incrementing counter of # of ads blocked today
    - `ads_percentage_today` - float - (0.0 - 100.0) % of how many DNS requests were blocked due to being on an ad list
    - `queries_cached` - int - How many queries were served from the cache
    - `queries_forwarded` - int - How many queries were forwarded to the configured upstream DNS servers
    - `dns_queries_all_replies` - int - Incrementing count of total amount of replies
    - `dns_queries_all_types` - int - Incrementing count of all DNS query types
    - `dns_queries_today` - int - How many queries were served today
    - `domains_being_blocked` - int - Counter of all domains blocked by ad lists
    - `unique_clients` - int - How many distinct clients have been served by Pi Hole
    - `unique_domains` - int - How many distinct domains have been served by PI Hole

`pi_hole_top_sources`

  - Tags:
    - `host` - string - Hostname of the client
    - `ip_address` - string - IP addres of the client
  - Fields:
    - `count` - int - Incrementing count of DNS requests from this client

---

`pi_hole_query_types`

  - Tags:
    - `type` - string - Type of DNS request (A, AAAA, etc...)
  - Fields:
    - `percentage` - float (0.0 -100.00) - Percent of total DNS requests are of this type

---

`pi_hole_forward_destinations`

  - Tags:
    - `host` - string - Hostname of the upstream dns server
    - `ip_address` - string - IP addres of the upstream dns server
  - Fields:
    - `percentage` - float (0.0 -100.00) - Percent of upstream DNS requests sent to this server 

---

`pi_hole_top_ads`

  - Tags:
    - `host` - string - Hostname of the blocked ad
  - Fields:
    - `count` - int - Incrementing count of DNS requests for this blocked ad

---

`pi_hole_top_queries`

  - Tags:
    - `host` - string - Hostname of the client
  - Fields:
    - `count` - int - Incrementing count of DNS requests for this client

---

`pi_hole_gravity`

  - No Tags
  - Fields:
    - `updated` - int - Millisecond Epoch timestamp when the gravity file was last updated
