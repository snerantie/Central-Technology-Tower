#!/usr/bin/env bash
# Convenience wrapper for running the Phase 1 Administrative AI Agent
# against the deployed AWS resources (Bedrock + DynamoDB + S3).
#
# Usage:
#   ./run.sh process path/to/transcript.vtt \
#       --title   "Meeting title"          \
#       --date    "YYYY-MM-DD"             \
#       --attendees "Alice,Bob,Charlie"
#
#   ./run.sh list                  # show all actions in the register
#   ./run.sh list --status Open    # show only open actions
#
# Override any setting via env var, e.g.:
#   AWS_REGION=us-east-1 ./run.sh process samples/sample_meeting.vtt
#   ADMIN_AGENT_OUTPUT=output ./run.sh process my.vtt   # write locally

set -euo pipefail

export AWS_REGION="${AWS_REGION:-eu-west-1}"
export ADMIN_AGENT_MOCK="${ADMIN_AGENT_MOCK:-0}"
export ACTION_REGISTRY_BACKEND="${ACTION_REGISTRY_BACKEND:-dynamodb}"
export ACTION_REGISTRY_TABLE="${ACTION_REGISTRY_TABLE:-ctt-action-register}"
export BEDROCK_MODEL_ID="${BEDROCK_MODEL_ID:-eu.amazon.nova-2-lite-v1:0}"
export PYTHONPATH="${PYTHONPATH:-src}"

if [ -z "${ADMIN_AGENT_OUTPUT:-}" ]; then
  ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")"
  if [ -n "$ACCOUNT_ID" ]; then
    export ADMIN_AGENT_OUTPUT="s3://ctt-admin-agent-outputs-${ACCOUNT_ID}-${AWS_REGION}"
  else
    export ADMIN_AGENT_OUTPUT="output"
    echo "WARN: Could not detect AWS account ID; writing to local 'output/' folder." >&2
  fi
fi

echo "==> Running admin agent with:"
echo "    AWS_REGION:          $AWS_REGION"
echo "    Action register:     $ACTION_REGISTRY_BACKEND ($ACTION_REGISTRY_TABLE)"
echo "    Output destination:  $ADMIN_AGENT_OUTPUT"
echo "    Bedrock model:       $BEDROCK_MODEL_ID"
echo

exec python3 -m admin_agent.cli "$@"
