import argparse

import dns.resolver
import itertools
import requests
import string
import timeit


def progress(current_position, total, percentage):
    divisor = total // percentage
    if current_position % divisor == 0:
        print('%d percent complete (%d out of %d)' % ((current_position * 100 / total),
                                                      current_position,
                                                      total))


def main():
    """
    brute-forces subdomains
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', action='store', help='What method to use in request', default='GET')
    parser.add_argument('-d', '--domain', action='store', help='Domain against which brute-force subdomains')
    parser.add_argument('-o', '--outfile', action='store', help='Output file for the working links')
    parser.add_argument('-l', '--length', action='store', type=int, help='Length of the subdomains names')
    parser.add_argument('-s', '--schema', action='store', help='Schema - http, https, etc.', default='http')
    try:
        args = parser.parse_args()
        method = args.method
        schema, domain = args.schema, args.domain
        subdomain_length = args.length
        suspicious_urls, working_urls = [], []
        failed_urls_count = 0
        requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings

        dns_resolver = dns.resolver.Resolver()

        # specifies how often should the progress be updated [1-100]. 20 - around each 5% of requests.
        progress_freq = 50

        char_set = string.ascii_lowercase + string.digits + '-' + '_'

        # checking for the supported methods
        if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']:
            raise ValueError("Method %s is not supported." % method)

        print('[+] Starting a generator of possible subdomains')
        start_time = timeit.default_timer()
        host_generator = (''.join(permutation)+'.'+domain for permutation in
                          itertools.product(char_set, repeat=subdomain_length))
        total_hosts = len(char_set)**subdomain_length

        print('[+] Brute-forcing subdomains. %d URLs in total' % total_hosts)
        for index, host in enumerate(host_generator):
            try:
                progress(index, total_hosts, progress_freq)
                dns_response = (dns_resolver.query(host, 'A', raise_on_no_answer=False))
                resolved_host = dns_response.qname.to_text(omit_final_dot=True)

                url = schema+'://'+resolved_host
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
    main()
