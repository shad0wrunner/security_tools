import argparse

import itertools
import string
import requests


def get_all_subdomains():
    pass


def check_url():
    pass


def progress(current_element, elements_list, percentage):
    """ calculates percentage of completion based on the index of the element in the list """
    try:
        divisor = len(elements_list) // percentage
        current_position = elements_list.index(current_element)
        if current_position % divisor == 0:
            print('%d percent complete' % (current_position * 100 / len(elements_list)))
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
    # parser.add_argument('-i', '--infile', action='store', help='Input subdomains list')
    try:
        args = parser.parse_args()
        method = args.method
        schema, domain = args.schema, args.domain
        subdomain_length = args.length
        working_urls = []
        failed_urls = []

        char_set = string.ascii_lowercase + string.digits + '-' + '_'
        url_list = [schema+'://'+''.join(permutation)+'.'+domain for permutation in
                    list(itertools.product(char_set, repeat=subdomain_length))]

        for url in url_list:
            try:
                progress(url, url_list, 5)
                print('Trying %s' % url)
                response = requests.request(method, url, verify=False)  # get the response
                working_urls.append((url, response.status_code))
            except requests.exceptions.ConnectionError:
                failed_urls.append(url)

        print(working_urls)
        print('Failed URLs: %d' % len(failed_urls))

    except Exception as exception_message:
        print('[-] Oops %s' % exception_message)


if __name__ == '__main__':
    print('[+] Starting main module')
    main()
