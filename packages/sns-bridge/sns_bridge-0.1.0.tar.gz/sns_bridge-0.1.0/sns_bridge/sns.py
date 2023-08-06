import boto3
import xml.etree.ElementTree as ET

import requests

client = boto3.client('sns', region_name='us-west-2')


def subscribe_to_sns(url, sns_endpoint_name):
    """
    Subscribe a given URL to an SNS endpoint
    :param url: URL to subscribe
    :param sns_endpoint_name: Endpoint name to subscribe to
    :return:
    """
    # TODO: properly handle pagination

    topics = client.list_topics()['Topics']
    topic_arn = None

    for topic in topics:
        if sns_endpoint_name in topic['TopicArn']:
            topic_arn = topic['TopicArn']
            break

    results = client.subscribe(TopicArn=topic_arn, Protocol='https', Endpoint=url)
    print(results)

    return results['SubscriptionArn']


def unsubscribe_from_sns(subscription_arn):
    client.unsubscribe(SubscriptionArn=subscription_arn)


def confirm_sns(confirmation_url):
    confirmation = requests.get(confirmation_url)
    node = ET.fromstring(confirmation.content)
    return node[0][0].text
