#!/bin/bash
# Run every 30 min for fresh data:   */30 * * * * cd /path/to/market_intel && ./run_daily.sh data
# Run once each morning for a brief:  0 7 * * *   cd /path/to/market_intel && ./run_daily.sh brief
cd "$(dirname "$0")"
case "$1" in
  data)  python ingest.py news; python ingest.py prices ;;
  brief) python ingest.py all; python brief.py ;;
  *) echo "usage: ./run_daily.sh data|brief" ;;
esac
