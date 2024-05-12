# aws-update-navigator-slack-app
Amazon Bedrockを使用して、任意の言語で AWS アップデートの説明と要約を提供する Slack アプリです。エージェントの指示は日本語に最適化されていますが、好みの言語を指示することで他の言語でも使用することができるでしょう。

## 概要
![](https://raw.githubusercontent.com/hayao-k/aws-update-navigator/main/images/architecture.png)

## 使用例
![](https://raw.githubusercontent.com/hayao-k/aws-update-navigator/main/images/example.png)

## 前提条件

このアプリケーションをデプロイに必要な前提条件は以下の通りです。

- AWS CLIがインストールされ、設定されていること
- SAM CLIがインストールされていること
- Slack アカウントと Slack アプリが作成済みであること

## デプロイ

1. 次のコマンドを実行します:

   ```bash
   git clone https://github.com/hayao-k/aws-update-navigator
   cd aws-update-navigator
   sam build -u 
   sam deploy
   ```

   プロンプトに従って設定値を入力し、デプロイします。

2. Bedrock Agent Function の `SLACK_BOT_TOKEN` と `SLACK_SIGNING_SECRET` 環境変数を実際の値に更新します。

## Parameters

CloudFormation テンプレートでは以下のパラメータを受け入れます。

- `pModelId`: BedrockエージェントのモデルID。サポートされる値:
  - `anthropic.claude-3-opus-20240229-v1:0`
  - `anthropic.claude-3-sonnet-20240229-v1:0`
  - `anthropic.claude-3-haiku-20240307-v1:0`
  - `anthropic.claude-v2:1`
  - `anthropic.claude-v2`
  - `anthropic.claude-instant-v1`
  - `amazon.titan-text-premier-v1:0`

## Resources

CloudFormation テンプレートによって作成される主なリソースは以下の通りです：

- **SlackAppFunction**: Slackアプリケーションとのやり取りを処理するLambda関数
- **BedrockAgentFunction**: AWSサービスのアップデートを処理し要約するためにBedrockエージェントが呼び出すLambda関数
- **BedrockAgent**: AWS サービスのアップデートを要約するように設定されたAmazon Bedrockエージェント
- **SlackAppLayer** and **BedrockAgentFunctionLayer**: 依存関係のための Lambda Layers

## Outputs

- **SlackAppFunctionUrl**: SlackアプリケーションのFunction URLエンドポイント。

## アプリケーションの削除

1. 次のコマンドを実行します:

   ```bash
   sam delete
   ```

2. 削除を確認するプロンプトに従います
