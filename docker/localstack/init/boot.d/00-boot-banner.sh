#!/usr/bin/env bash
set -euo pipefail

readonly CYAN="\033[1;36m"
readonly YELLOW="\033[1;33m"
readonly RESET="\033[0m"

printf "\n${CYAN}"
cat <<'BANNER'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          EVENT RELAY · LOCALSTACK DEVELOPMENT 🐈‍⬛             ║
║                                                              ║
║              Boot sequence has started                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
BANNER
printf "${RESET}"

printf "${YELLOW}→ Waiting for AWS services to become ready...${RESET}\n"
printf "${YELLOW}→ SQS resources will be created in READY phase.${RESET}\n\n"