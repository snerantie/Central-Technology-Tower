# Phase 1 — Step 2: Connect to AWS

Goal: run the **same** agent against your real AWS account instead of mock mode.
Outputs land in S3, actions land in DynamoDB, extraction & summarisation use
**Amazon Bedrock**.

You'll do this **once**, then everything afterwards is a one-line command.

## Pre-flight checks (2 minutes)

In your AWS console, confirm:

| Check | How |
|-------|-----|
| You're in the **right region** | Top-right of the console (e.g. `eu-west-1` Ireland) |
| **Bedrock model access** is enabled | `Amazon Bedrock` → `Model access` → confirm **Anthropic Claude 3.5 Sonnet** is "Access granted" |
| You can create resources | If you can deploy CloudFormation in the console, you're good |

## Step 2.1 — Deploy the AWS resources (5 minutes)

This creates the DynamoDB table, two S3 buckets, and an IAM policy.

### Console path (recommended for first time)

1. Open `CloudFormation` → **Create stack** → **With new resources**.
2. Choose **Upload a template file** → upload `cloudformation.yaml` from this folder.
3. **Stack name:** `ctt-admin-agent`. Leave everything else as-is. Next, Next, **Submit**.
4. Wait ~2 minutes for `CREATE_COMPLETE`. Open the **Outputs** tab — you'll see:
   - `ActionRegisterTableName` → `ctt-action-register`
   - `TranscriptsBucketName` → `ctt-admin-agent-transcripts-...`
   - `OutputsBucketName` → `ctt-admin-agent-outputs-...`
   - `AgentPolicyArn`

### CLI path (if you prefer)

```bash
aws cloudformation deploy \
  --stack-name ctt-admin-agent \
  --template-file cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-1
```

## Step 2.2 — Run the agent against real AWS (3 minutes)

From the `phase1_admin_agent/` folder:

```bash
# 1. Tell the agent to use real AWS (no more mock mode)
export ADMIN_AGENT_MOCK=0
export AWS_REGION=eu-west-1                                  # your Bedrock region
export ACTION_REGISTRY_BACKEND=dynamodb
export ACTION_REGISTRY_TABLE=ctt-action-register
export ADMIN_AGENT_OUTPUT=s3://ctt-admin-agent-outputs-<youraccount>-eu-west-1

# 2. Make sure boto3 is installed
pip install -r requirements.txt

# 3. Run it on a real transcript
python -m admin_agent.cli process samples/sample_meeting.vtt \
  --title "Cloud Migration SteerCo" \
  --date 2026-06-17 \
  --attendees "Priya,David,Sarah,Marcus"
```

You should see *much* better output than mock mode:
- A real summary (not just the first sentences),
- Owners correctly identified even when phrasing is awkward,
- "Unassigned" only when there genuinely is no owner.

## Step 2.3 — Verify it landed in AWS

| Where to look | What you should see |
|---------------|---------------------|
| `DynamoDB` → `ctt-action-register` → **Explore items** | A row per action, with `owner`, `due_date`, `status=Open`, `priority` |
| `S3` → `ctt-admin-agent-outputs-...` | `MTG-XXXX_minutes.md`, `MTG-XXXX_summary.txt`, `MTG-XXXX_actions.json` |
| Console → **Bedrock** → `Model invocation logs` (if enabled) | One invocation per `process` call |

## Common gotchas

- **`AccessDeniedException` calling `bedrock:Converse`** — you've not enabled
  model access for Anthropic Claude 3.5 Sonnet in this region. Fix in
  `Amazon Bedrock` → `Model access`.
- **`ResourceNotFoundException` on the table** — wrong region. The table is in
  the region you deployed CloudFormation to; `AWS_REGION` must match.
- **Region doesn't have Claude 3.5 Sonnet** — try `us-east-1` or `us-west-2`,
  or switch `BEDROCK_MODEL_ID` to a region-appropriate inference profile
  (e.g. `eu.anthropic.claude-3-5-sonnet-20240620-v1:0`).

## Tear-down

If you want to remove everything:
```bash
# Empty the buckets first (CloudFormation can't delete non-empty buckets)
aws s3 rm s3://ctt-admin-agent-transcripts-<acct>-<region> --recursive
aws s3 rm s3://ctt-admin-agent-outputs-<acct>-<region> --recursive
aws cloudformation delete-stack --stack-name ctt-admin-agent --region eu-west-1
```
