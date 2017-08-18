import argparse

import itertools
import string
import requests


def get_all_subdomains():
    pass


def progress(current_element, elements_list, percentage):
    """ calculates percentage of completion based on the index of the element in the list """
    try:
        divisor = len(elements_list) // percentage
        current_position = elements_list.index(current_element)
        if current_position % divisor == 0:
            print('%d percent complete (%d out of %d)' % ((current_position * 100 / len(elements_list)),
                                                          current_position,
                                                          len(elements_list)))

    except Exception as exception_message:
        print('[-] Something went wrong in the progress meter: %s' % exception_message)


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
        failed_urls, working_urls = [], []

        # specifies how often should the progress be updated [1-100]. 20 - around each 5% of requests.
        progress_freq = 20

        char_set = string.ascii_lowercase + string.digits + '-' + '_'

        # checking for the supported methods
        if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']:
            raise ValueError("Method %s is not supported." % method)

        requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings

        print('[+] Generating a list of possible subdomains')
        url_list = [schema+'://'+''.join(permutation)+'.'+domain for permutation in
                    list(itertools.product(char_set, repeat=subdomain_length))]

        print('[+] Brute-forcing subdomains. %d URLs in total' % len(url_list))
        for url in url_list:
            try:
                progress(url, url_list, progress_freq)
                response = requests.request(method, url, verify=False, timeout=(3.05, 27.10))  # get the response
                print(url,'looks alive')
                working_urls.append((url, response.status_code))
            except requests.exceptions.ConnectionError:
                failed_urls.append(url)

        print('[+] Brute-forcing complete. %d host(s) below seem operational:' % len(working_urls))
        print(working_urls)
        print('Non-responding hosts: %d' % len(failed_urls))

    except Exception as exception_message:
        print('[-] Something went wrong: %s' % exception_message)

    except KeyboardInterrupt:
        print("[x] Exiting by user command")

if __name__ == '__main__':
    print('[+] Starting the main module')
    main()
