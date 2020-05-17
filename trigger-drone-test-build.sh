#!/usr/bin/env bash

set -eo pipefail

{
    if [[ $1 = "--with-local-changes" || $1 = "-l" ]]; then
        git ci -a -m 'Trigger test build with local changes'
        git push --force-with-lease origin HEAD:test
        git reset HEAD~1
    else
        openssl rand -hex 10 > triggerbit.txt
        git add triggerbit.txt
        git ci -m 'Change trigger bit'
        git push --force-with-lease origin HEAD:test
        git reset --hard HEAD~1
    fi
} &> /dev/null

echo -e "\e[32mSuccessfully pushed dummy commit to trigger pipeline.\e[0m"

