import argparse

import dns.resolver
import itertools
import requests
import string
import timeit


def parse_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', action='store', help='What method to use in request', default='GET')
    parser.add_argument('-s', '--schema', action='store', help='Schema - http, https, etc.', default='http')
    parser.add_argument('-d', '--domain', action='store', help='Domain against which brute-force subdomains')
    parser.add_argument('-l', '--length', action='store', type=int, help='Length of the subdomains names')
    parser.add_argument('-o', '--outfile', action='store', help='Output file for the working links')
    args = parser.parse_args()
    parsed_args = (args.method, args.schema, args.domain, args.length)
    return parsed_args


def progress(current_position, total, resolution):
    part = total*resolution // 100
    if current_position % part == 0:
        print('%d percent complete (%d out of %d)' % ((current_position * 100 / total),
                                                      current_position,
                                                      total))


def main(method, schema, domain, subdomain_length):
    """
    brute-forces subdomains
    """
    try:
        suspicious_urls, working_urls = [], []
        failed_urls_count = 0
        requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings

        dns_resolver = dns.resolver.Resolver()

        # specifies how often (in percent) should the progress be updated.
        progress_resolution = 0.5

        char_set = string.ascii_lowercase + string.digits + '-' + '_'

        # checking for the supported methods
        if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE', 'HEAD']:
            raise ValueError("Method %s is not supported." % method)

        print('[+] Starting a generator of possible subdomains')
        start_time = timeit.default_timer()
        host_generator = (''.join(permutation)+'.'+domain for permutation in
                          itertools.product(char_set, repeat=subdomain_length))
        total_hosts = len(char_set)**subdomain_length

        print('[+] Brute-forcing subdomains. %d URLs in total' % total_hosts)
        for index, host in enumerate(host_generator):
            try:
                progress(index, total_hosts, progress_resolution)
                dns_response = (dns_resolver.query(host, 'A'))

                url = schema+'://'+dns_response.qname.to_text(omit_final_dot=True)
                http_response = requests.request(method, url, verify=False, timeout=(3, 3))  # get the response
                print('%s answers HTTP %d' % (url, http_response.status_code))
                working_urls.append((url, http_response.status_code))

            except requests.exceptions.ConnectionError:
                print('%s has been resolved but provided no HTTP response. Try HTTPS or assume it is firewalled' % url)
                suspicious_urls.append(url)

            except dns.resolver.NXDOMAIN:
                failed_urls_count += 1

            except Exception as exception_message:
                print('[-] Something went wrong while brute-forcing hosts: %s while trying %s' %
                      (exception_message, host))

        stop_time = timeit.default_timer()
        print('[+] Brute-forcing complete in %d sec. %d host(s) below seem operational:' %
              (stop_time-start_time, len(working_urls)))
        print(working_urls)
        print('[?] %d host(s) below might require additional inspection:' % len(suspicious_urls))
        print(suspicious_urls)
        print('[+] Not resolved hosts: %d' % failed_urls_count)

    except Exception as exception_message:
        print('[-] Something went wrong: %s' % exception_message)

    except KeyboardInterrupt:
        print("[x] Exiting by user command")

if __name__ == '__main__':
    print('[+] Starting the main module')
    parsed_parameters = parse_parameters()
    main(*parsed_parameters)
