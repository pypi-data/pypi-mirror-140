import json
import threading
import time

from bottle import route, run, request
from pyngrok import ngrok

from sns import subscribe_to_sns, unsubscribe_from_sns, confirm_sns
from wsgi import ThreadedWSGIServer

subscription_arn = None


@route('/', method='POST')
def index():
    global subscription_arn
    body = json.loads(request.body.read())
    print(body)
    if body and body.get('Type') == 'SubscriptionConfirmation':
        subscription_arn = confirm_sns(body.get('SubscribeURL'))
        return "OK"

    return "Hello"


def main():
    global subscription_arn

    # Start web server to receive SNS messages
    threaded_wsgi = ThreadedWSGIServer(port=65500)
    http_server = threading.Thread(target=run, kwargs={'server': threaded_wsgi})
    http_server.start()

    # Start local tunnel to connect to SNS
    http_tunnel = ngrok.connect(addr=65500)

    # Subscribe to SNS via the tunnel
    url = http_tunnel.public_url.replace('http:', 'https:')
    print("URL is", url)
    subscribe_to_sns(url, 'ses_tbxofficial_inbound_email')

    # Wait
    try:
        while http_server.is_alive():
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Stop received! Stopping web server...")
        threaded_wsgi.stop()

    # After we're done, unsubscribe our subscription
    print("Unsubscribing from SNS topic...")
    unsubscribe_from_sns(subscription_arn)


# Start our web server on a background thread, then proceed.
if __name__ == "__main__":
    main()
