"""
AWS Lambda function to run a Slack app that processes What's New URLs.
A summary of the URLs is provided by Agents for Amazon Bedrock and posted to Slack.
"""
import json
from logging import getLogger
import os
import re
from uuid import uuid4
import boto3
from botocore.config import Config
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from slack_bolt import App, Ack
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
logger = getLogger()

URL_PATTERN = re.compile(
    r'https://aws\.amazon\.com/about-aws/whats-new/(?:\d{4})/(?:\d{2})/(?:[\w-]+)/'
)

app = App(
    token=os.environ['SLACK_BOT_TOKEN'],
    signing_secret=os.environ['SLACK_SIGNING_SECRET'],
    process_before_response=True,
)

def just_ack(ack: Ack):
    """Notify Slack that the app has received a request by executing the ack function."""
    logger.info('Just ACK')
    ack()

def create_bedrock_agent_client() -> BaseClient:
    """Create a Bedrock agent client with custom configuration."""
    config = Config(
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        },
        read_timeout=120
    )
    return boto3.client('bedrock-agent-runtime', config=config)

def create_slack_message(data):
    """
    Create a Slack message with the given data in a predefined format.
    
    Args:
        data (dict): A dictionary containing summary, advantages, and technical issues addressed.
        
    Returns:
        dict: A dictionary containing a list of Slack message blocks.
    """
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*記事の要約*"}},
		{"type": "divider"},
		{"type": "section", "text": {"type": "plain_text", "text": data['summary']}},
		{"type": "section", "text": {"type": "mrkdwn", "text": "*このアップデートの利点*"}},
        {"type": "divider"},
		{"type": "section", "text": {"type": "plain_text", "text": data['advantages']}},
		{"type": "section", "text": {"type": "mrkdwn", "text": "*このアップデートが解決する技術的な課題*"}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "plain_text", "text": data['addresses']}},
		{"type": "context", "elements": [{"type": "plain_text", "text": "Powered by Amazon Bedrock"}]}
	]
    return {"blocks": blocks, "text": data['summary']}

def process_whats_new_url(body, say):
    """
    Process the given event body and post the response from Agents for Amazon Bedrock to Slack.

    Args:
        body (dict): The event body containing the message text.
        say (function): A function to send a message to the Slack channel.
    """
    text = body.get('event', {}).get('text', {})
    thread_ts = body['event']['ts']
    url = URL_PATTERN.search(text)

    if url:
        try:
            client = create_bedrock_agent_client()

            response = client.invoke_agent(
                agentId=os.environ['BEDROCK_AGENT_ID'],
                agentAliasId=os.environ['BEDROCK_AGENT_ALIAS_ID'],
                sessionId=str(uuid4()),
                enableTrace=True,
                inputText=url.group()
            )

            event_stream = response['completion']
            data = ''
            trace = ''
            for event in event_stream:
                if 'chunk' in event:
                    data = event['chunk']['bytes'].decode('utf-8')
                    logger.info(data)
                trace = event.get('trace', {}).get('trace', {}).get('preProcessingTrace', {}) \
        				.get('modelInvocationOutput', {}).get('parsedResponse')
                if trace:
                    if trace['isValid'] is False:
                        logger.info(trace)
                        say(text=trace['rationale'], thread_ts=thread_ts)
            if data:
                message = create_slack_message(json.loads(data))
                say(blocks=message['blocks'], text=message['text'], thread_ts=thread_ts)
        except ClientError as e:
            error_message = e.response['Error']['Message']
            logger.error(error_message)
            say(text=error_message, thread_ts=thread_ts)
    else:
        logger.info('nothing to do')

app.event('message')(
    ack=just_ack,
    lazy=[process_whats_new_url],
)

def lambda_handler(event, context):
    """
    AWS Lambda handler for processing Slack events.
    
    Args:
        event (dict): The AWS Lambda event object.
        context (object): The AWS Lambda context object.
        
    Returns:
        object: The response from the SlackRequestHandler.
    """
    logger.debug(event)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
