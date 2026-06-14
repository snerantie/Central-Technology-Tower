# Deployment Screenshots — Phase 1

A place to keep evidence of the AWS deployment for audit / handover / demos.
Drop screenshots here using a clear filename so anyone can find them later.

## Suggested filename pattern

```
YYYY-MM-DD_<what>_<status>.png
```

Examples:

| Filename | What it captures |
|----------|------------------|
| `2026-06-17_cloudformation_create-complete.png` | Stack reaches `CREATE_COMPLETE` |
| `2026-06-17_cloudformation_outputs.png` | The four Outputs values from the stack |
| `2026-06-17_dynamodb_action-register.png` | First actions appearing in the table |
| `2026-06-17_s3_outputs-bucket.png` | Generated minutes/summary/actions in the bucket |
| `2026-06-17_bedrock_first-invocation.png` | First successful Bedrock model invocation |

## How to add one

If you're working in Kiro Web:

1. Take the screenshot.
2. Drop the image into the chat with a quick "save under `phase1_admin_agent/aws/screenshots/`" — the agent will commit and push it for you.

Or via GitHub directly:

1. Open the repo → navigate to this folder → **Add file** → **Upload files**.
2. Drag the screenshot in, give it a meaningful name, commit straight to `main`.

## Deployment milestones to capture

Tick these off as you go — useful for showing management later:

- [ ] CloudFormation stack `ctt-admin-agent` reaches `CREATE_COMPLETE`
- [ ] CloudFormation **Outputs** tab showing the four resource names/ARNs
- [ ] Bedrock **Model access** screen showing Claude 3.5 Sonnet "Access granted"
- [ ] First successful end-to-end run (CLI output)
- [ ] Action register in DynamoDB with first real actions
- [ ] Outputs S3 bucket containing first minutes/summary files
