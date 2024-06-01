#!/usr/bin/env python

import os
import time

import requests
import urllib3

import util
from influx_metric import InfluxMetric

_required_env_vars = ['PI_HOLE_API_TOKEN', 'INFLUX_ORG', 'INFLUX_BUCKET', 'INFLUX_TOKEN']
for var in _required_env_vars:
    util.ensure_var_set(var)

pi_hole_host = os.getenv("PI_HOLE_HOST", "http://pi.hole")
tag_pi_hole_host = urllib3.util.parse_url(pi_hole_host).host
auth_token = os.getenv("PI_HOLE_API_TOKEN", "")
influx_url = os.getenv("INFLUX_URL", "http://localhost:8086")
influx_org = os.getenv("INFLUX_ORG", "")
influx_bucket = os.getenv("INFLUX_BUCKET", "")
influx_token = os.getenv("INFLUX_TOKEN", "")


def get_pihole_data() -> dict:
    url = f'{pi_hole_host}/admin/api.php'
    query = {
        'auth': auth_token,
        'summaryRaw': '', 'overTimeData': '', 'topItems': '', 'recentItems': '',
        'getQueryTypes': '', 'getForwardDestinations': '', 'getQuerySources': '', 'jsonForceObject': ''
    }

    resp = requests.get(url, params=query)
    if resp.status_code != 200:
        print(f'pi-hole request to "{url}" failed with status: {resp.status_code} and body {resp.text}')
        return {}
    return resp.json()


def send_metrics(metrics: list[InfluxMetric]):
    url = influx_url + '/api/v2/write'
    headers = {'content-type': 'text/plain', 'Authorization': f'Token {influx_token}'}
    body = '\n'.join(str(mp) for mp in metrics)
    query = {'org': influx_org, 'bucket': influx_bucket, 'precision': 'ns'}
    resp = requests.post(url, headers=headers, data=body, params=query)
    if resp.status_code != 204:
        print(resp.status_code, resp, resp.text)


def main():
    # get pi-hole data, and setup timestamp for resulting metrics
    pihole_data = get_pihole_data()
    timestamp = time.time_ns()

    if not pihole_data:
        return

    metric_points = []

    # create the root pi_hole metric
    pi_hole_metric = InfluxMetric('pi_hole', timestamp) \
        .with_tag('pi_hole_host', tag_pi_hole_host) \
        .with_field('ads_blocked_today', int(pihole_data["ads_blocked_today"])) \
        .with_field('ads_percentage_today', float(pihole_data["ads_percentage_today"])) \
        .with_field('queries_cached', int(pihole_data["queries_cached"])) \
        .with_field('queries_forwarded', int(pihole_data["queries_forwarded"])) \
        .with_field('dns_queries_all_replies', int(pihole_data["dns_queries_all_replies"])) \
        .with_field('dns_queries_all_types', int(pihole_data["dns_queries_all_types"])) \
        .with_field('dns_queries_today', int(pihole_data["dns_queries_today"])) \
        .with_field('domains_being_blocked', int(pihole_data["domains_being_blocked"])) \
        .with_field('unique_clients', int(pihole_data["unique_clients"])) \
        .with_field('unique_domains', int(pihole_data["unique_domains"]))

    metric_points.append(pi_hole_metric)

    # create the 'pi_hole_top_sources' metrics
    for top_source, count in pihole_data.get("top_sources", {}).items():
        [hostname, ip_address] = top_source.split('|')
        top_source_metric = InfluxMetric('pi_hole_top_sources', timestamp) \
            .with_tag('pi_hole_host', tag_pi_hole_host) \
            .with_tag('host', hostname) \
            .with_tag('ip_address', ip_address) \
            .with_field('count', int(count))

        metric_points.append(top_source_metric)

    # create the 'pi_hole_query_types' metrics
    for query_type, percentage in pihole_data.get("querytypes", {}).items():
        query_type_metric = InfluxMetric('pi_hole_query_types', timestamp) \
            .with_tag('pi_hole_host', tag_pi_hole_host) \
            .with_tag('type', query_type) \
            .with_field('percentage', float(percentage))

        metric_points.append(query_type_metric)

    # create the 'pi_hole_forward_destinations' metrics
    for forward_destination, percentage in pihole_data.get("forward_destinations", {}).items():
        [hostname, ip_address] = forward_destination.split('|')
        top_source_metric = InfluxMetric('pi_hole_forward_destinations', timestamp) \
            .with_tag('pi_hole_host', tag_pi_hole_host) \
            .with_tag('host', hostname) \
            .with_tag('ip_address', ip_address) \
            .with_field('percentage', float(percentage))

        metric_points.append(top_source_metric)

    # create the 'pi_hole_top_ads' metrics
    for host, count in pihole_data.get("top_ads", {}).items():
        query_type_metric = InfluxMetric('pi_hole_top_ads', timestamp) \
            .with_tag('pi_hole_host', tag_pi_hole_host) \
            .with_tag('host', host) \
            .with_field('count', int(count))

        metric_points.append(query_type_metric)

    # create the 'pi_hole_top_queries' metrics
    for host, count in pihole_data.get("top_queries", {}).items():
        query_type_metric = InfluxMetric('pi_hole_top_queries', timestamp) \
            .with_tag('pi_hole_host', tag_pi_hole_host) \
            .with_tag('host', host) \
            .with_field('count', int(count))

        metric_points.append(query_type_metric)

    # create the 'pi_hole_gravity' metric
    gravity_metric = InfluxMetric('pi_hole_gravity', timestamp) \
        .with_tag('pi_hole_host', tag_pi_hole_host) \
        .with_field('updated', int(pihole_data["gravity_last_updated"]["absolute"]))

    metric_points.append(gravity_metric)

    # now that we've created all the points, ship-em-off
    send_metrics(metric_points)


if __name__ == '__main__':
    print(f'running against pi-hole host={pi_hole_host} and publishing to influx host={influx_url} org={influx_org} bucket={influx_bucket}')
    main()
