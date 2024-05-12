# aws-update-navigator-slack-app
A Slack app that provides explanations and summaries of AWS updates in your preferred language, using Amazon Bedrock. The Agent Instruction is optimized for Japanese, but you can choose your preferred language.

## Ovewview
![](https://raw.githubusercontent.com/hayao-k/aws-update-navigator/main/images/architecture.png)

## Example of use
![](https://raw.githubusercontent.com/hayao-k/aws-update-navigator/main/images/example.png)

## Prerequisites

Before deploying this application, ensure you have the following:

- AWS CLI installed and configured.
- SAM CLI installed.
- A Slack account and a Slack app created for integration.

## Deployment

To deploy this application:

1. Run the following command:

   ```bash
   git clone https://github.com/hayao-k/aws-update-navigator
   cd aws-update-navigator
   sam build -u 
   sam deploy
   ```

   Follow the prompts in the deployment process to set up the application.

2. Update the `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` environment variables of the Lambda function with their actual values.

## Parameters

The template accepts the following parameters:

- `pModelId`: The Model ID of the Bedrock Agent. Supported values are:
  - `anthropic.claude-3-opus-20240229-v1:0`
  - `anthropic.claude-3-sonnet-20240229-v1:0`
  - `anthropic.claude-3-haiku-20240307-v1:0`
  - `anthropic.claude-v2:1`
  - `anthropic.claude-v2`
  - `anthropic.claude-instant-v1`
  - `amazon.titan-text-premier-v1:0`

## Resources

The following resources are created by this template:

- **SlackAppFunction**: A Lambda function that handles interactions with the Slack application.
- **BedrockAgentFunction**: A Lambda function that the Bedrock agent invokes to process and summarize AWS service updates.
- **BedrockAgent**: An Amazon Bedrock agent configured to summarize AWS service updates.
- **SlackAppLayer** and **BedrockAgentFunctionLayer**: Lambda layers for dependencies.

## Outputs

- **SlackAppFunctionUrl**: The Function URL endpoint for the Slack application.

## Cleanup

To delete the application and its resources:

1. Run the following command:

   ```bash
   sam delete
   ```

2. Follow the prompts to confirm deletion.
