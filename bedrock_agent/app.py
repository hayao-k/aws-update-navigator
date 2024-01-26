"""
Lambda function to extract text content from URL and respond to Agents for Amazon Bedrock.
"""

import json
from logging import getLogger
from typing import Optional
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

logger = getLogger()

def extract_text_from_url(url: str, target_tag: str = 'p',
                          text_limit: Optional[int] = 5000) -> str:
    """
    Extracts text content from the given URL and returns the concatenated text.

    Args:
        url (str): The URL to extract text from.
        target_tag (str, optional): The HTML tag to extract text from. Defaults to 'p'.
        text_limit (Optional[int], optional): The maximum number of characters to return. 
                                              Defaults to 5000.

    Returns:
        str: The extracted and concatenated text, limited to the specified number of characters.
    """
    try:
        with urlopen(url) as response:
            html_body = response.read().decode('utf-8')

        soup = BeautifulSoup(html_body, 'html.parser')
        extracted_texts = [content.get_text() for content in soup.find_all(target_tag)]
        concatenated_texts = '\n\n'.join(extracted_texts)

        return (concatenated_texts[:text_limit] if text_limit else concatenated_texts)
    except HTTPError as e:
        logger.error('HTTP request failed: %s, %s', e.code, e.reason)
        return ''
    except URLError as e:
        logger.error('URL error occured: %s', e.reason)
        return ''

def lambda_handler(event, context):
    """
    AWS Lambda function handler that processes the given event and returns a response.

    Args:
        event (dict): The event data containing the API path, request body, and other information.
        context (object): The AWS Lambda context object.

    Returns:
        dict: A dictionary containing the message version and the response data.
    """
    logger.debug(event)
    api_path = event['apiPath']
    url = ''
    body = {}
    http_status_code = 200

    if api_path == '/summarize_article':
        properties = event['requestBody']['content']['application/json']['properties']
        url = next((item['value'] for item in properties if item['name'] == 'url'), '')
        body = {'body': extract_text_from_url(url)}
    else:
        body = {'error': 'Invalid API path'}
        logger.error('Invalid API path: %s', api_path)
        http_status_code = 400

    response_body = {
        'application/json': {
            'body': json.dumps(body, ensure_ascii=False)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': api_path,
        'httpMethod': event['httpMethod'],
        'httpStatusCode': http_status_code,
        'responseBody': response_body,
    }

    return {
        'messageVersion': '1.0',
        'response': action_response
    }
    