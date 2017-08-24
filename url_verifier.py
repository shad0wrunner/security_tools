import argparse
import re

import requests
from urllib.parse import urlparse


def parse_parameters():
    # Retrieving parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', action='store', help='What method to use in requests', default='HEAD')
    parser.add_argument('-f', '--file', action='store', help='File for the links')
    parser.add_argument('-o', '--output', action='store', help='File for the verification results',
                        default='urls_verified_output.txt')
    args = parser.parse_args()
    parsed_args = (args.method, args.file, args.output)

    # checking for the supported methods
    if not args.method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE', 'HEAD']:
        raise ValueError("Method %s is not supported." % args.method)

    return parsed_args


def is_valid_hostname(hostname):
    """ Checks if the hostname is valid """
    if len(hostname) > 255:
        return False
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def file_to_list(input_file):
    """ Gets URLs from the input file, verifies and returns the list of the URLs which are alive """
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


def list_to_file(input_list, output_file):
    """ Gets a list and writes it to file """
    file = open(output_file, "w")
    print('[+] Writing checked links into the file')
    for link in input_list:
        file.write(','.join(map(str, link))+'\n')
    file.close()


def main(method, file, output_file):
    """ Quickly check if the URLs are alive """
    failed_urls, working_urls = [], []
    requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings
    url_list = file_to_list(file)  # getting a list of URLs from the file
    http_timeout = 60.06

    try:
        print('[+] Verifying URLs. %d in total' % len(url_list))
        for url in url_list:
            try:
                response = requests.request(method, url, verify=False, allow_redirects=False, timeout=http_timeout)
                print('Checking %s' % url)
                working_urls.append((url, response.status_code, response.headers.get('Location')))
            except requests.exceptions.ConnectionError:
                failed_urls.append(url)

        print('[+] Verification complete. %d URL(s) below seem operational:' % len(working_urls))
        print(working_urls)
        list_to_file(working_urls, output_file)
        print('[+] Non-responding links: %d' % len(failed_urls))

    except Exception as exception_message:
        print('[-] Something went wrong: %s' % exception_message)
    except KeyboardInterrupt:
        print("[x] Exiting by user command")

if __name__ == '__main__':
    print('[+] Starting main module')
    parsed_parameters = parse_parameters()
    main(*parsed_parameters)
