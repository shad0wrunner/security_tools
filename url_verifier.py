import argparse
import re

import requests
from urllib.parse import urlparse


def is_valid_hostname(hostname):
    """ Checks if the hostname is valid """
    if len(hostname) > 255:
        return False
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def file_to_list(input_file):
    """ Gets URLs from the input file, verifies and returns the list """
    url_list = []

    if input_file is not None:
        print('[+] Reading an input file')
        file = open(input_file)
        for line in file:
            parsed_url = urlparse(line)
            hostname = parsed_url.netloc
            if (parsed_url.scheme in ['http', 'https']) and (is_valid_hostname(hostname) and (hostname != '')):
                url_list.append(line.rstrip())
        file.close()

    return url_list


def main(method, url_list):
    """ Quickly check if the URLs are alive """
    failed_urls, working_urls = [], []
    requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings

    # checking for the supported methods
    if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE', 'HEAD']:
        raise ValueError("Method %s is not supported." % method)

    try:
        print('[+] Verifying URLs. %d in total' % len(url_list))
        for url in url_list:
            try:
                response = requests.request(method, url, verify=False, allow_redirects=False)
                working_urls.append((url, response.status_code))
            except requests.exceptions.ConnectionError:
                failed_urls.append(url)

        print('[+] Verification complete. %d URL(s) below seem operational:' % len(working_urls))
        print(working_urls)
        print('Non-responding links: %d' % len(failed_urls))

    except Exception as exception_message:
        print('[-] Something went wrong: %s' % exception_message)
    except KeyboardInterrupt:
        print("[x] Exiting by user command")

if __name__ == '__main__':
    print('[+] Starting main module')

    # Retrieving parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', action='store', help='What method to use in requests', default='HEAD')
    parser.add_argument('-f', '--file', action='store', help='File for the links')
    args = parser.parse_args()

    file = args.file
    url_list = file_to_list(file)

    main(args.method, url_list)
