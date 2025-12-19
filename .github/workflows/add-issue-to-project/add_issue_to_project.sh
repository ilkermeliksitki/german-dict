#!/bin/bash

set -euo pipefail # exit on error, undefined variable, or error in pipeline

OWNER="ilkermeliksitki"
REPO="german-dict"
PROJECT=5

echo "Syncing issues from $OWNER/$REPO into project #$PROJECT..."

# get all issues in the repo
ISSUES=$(gh issue list --repo "$OWNER/$REPO" --limit 10000 --state open --json number,url -q '.[] | {number, url}')

# get all issues already in the project
EXISTING=$(gh project item-list "$PROJECT" --owner "$OWNER" --limit 10000 --format json | jq '.items[].content.url')

echo "$ISSUES" | jq -c '.' | while read -r issue; do
  URL=$(echo "$issue" | jq -r '.url')
  NUM=$(echo "$issue" | jq -r '.number')

  if echo "$EXISTING" | grep -q "$URL"; then
    echo "✅ Issue $URL, #$NUM already in project"
  else
    echo "➕ Adding issue $URL to project"
    gh project item-add "$PROJECT" --owner "$OWNER" --url "$URL"
  fi
done


