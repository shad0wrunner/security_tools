import argparse
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests


def main():
    """
    The tool is intended to extract all links (complete and relative ones) from HTML tag attributes
    TODO: urljoin
    """
    links = []
    parser = argparse.ArgumentParser(description='Parser parser')
    parser.add_argument('-m', '--method', action='store', help='What method to use in request')
    parser.add_argument('-u', '--url', action='store', help='URL to call with the specified method')

    try:
        args = parser.parse_args()
        url = args.url
        scheme = urlparse(url).scheme
        method = args.method

        if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']:
            raise ValueError("Method %s is not supported." % method)

        response = requests.request(method, url, verify=False)  # get the response
        url = response.url.rstrip('/')  # if there was a redirect - acquire the URL from the response

        print('[+] Retrieving ' + url)
        raw_html = response.content

        soup = BeautifulSoup(raw_html, "html.parser")

        # neat print headers
        print("[+] Received the response HTTP %d" % response.status_code)
        for header in response.headers:
            print(header + ':', response.headers[header])

        # gathering a list of hrefs and srcs
        for script in soup.select('script'):
            links.append(script.get('src'))
        for anchor in soup.select('a'):
            links.append(anchor.get('href'))
        for link in soup.select('link'):
            links.append(link.get('href'))
        for form in soup.select('form'):
            links.append(form.get('action'))

        links = [link for link in links if
                 not link[0] == '#' and
                 not urlparse(link).scheme in ['mailto', 'skype'] and
                 not link == '/']  # removing bookmarks, emails and skype and '/'

        links = [scheme + '://' + link[2:] if link[0:2] == '//' else
                 link if urlparse(link).scheme in ['http', 'https'] else
                 url + link if link[0] == '/' else
                 url + '/' + link for link in links]  # appending URL value

    except Exception as e:
        print("[-] Something went wrong: %s" % e)

    except KeyboardInterrupt:
        print("[x] Exiting by user command")

    print("\n[+] %d Links extracted:" % len(links))
    for link in links:
        print(link)
    return links


if __name__ == "__main__":
    print('[*] Starting the main module')
    main()
