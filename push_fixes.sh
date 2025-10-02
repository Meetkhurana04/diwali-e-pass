#!/bin/bash
cd "$(dirname "$0")"
git add .
git commit -m "Fix PostgreSQL compatibility - use %s placeholders instead of ?"
git push origin main
