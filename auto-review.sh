#!/bin/bash

PROJECT_SSH_URL="git@$GITLAB_SERVER:sdoppe/deploiements/docs-projets"
PROJECT_PATH=$( dirname -- "$( readlink -f -- "$0"; )"; )

function fetch_project_name() {
    NAME=$(curl -s -k --request GET --header "PRIVATE-TOKEN: $GITLAB_API_KEY" "https://$GITLAB_SERVER/api/v4/projects/$1" | jq -r '.|.name')
}

cd $PROJECT_PATH

echo "#############################################################"
echo "######################## Auto-Review ########################"
echo "#############################################################"

for ID in $@
do

    fetch_project_name $ID

    BRANCH=Auto-Review/$(date +'%Y%m%d_%H%M%S')
    GIT_URL=$PROJECT_SSH_URL/$NAME\.git

    # IF sudo is used, then ROOT SSH Key is used /#/ but not set in Gitlab account
    res_clone=$(git clone $GIT_URL 2>&1)
    if [[ $res_clone == *'fatal'* ]]
    then
        echo "ERROR: $GIT_URL not cloned ! KO"
        echo $res_clone
        continue
    fi

    sudo chown -R $(whoami): $NAME

    cd $NAME
    git checkout -q -b $BRANCH
    cd ..
    
    # Run main for each project name.
    .venv/bin/python main.py $NAME

    # Move log file to project folder
    mv Auto-Review-$(date +'%Y%m%d')_*.log $NAME

    cd $NAME
    
    git add .
    git commit --quiet -m "Review - Rundeck - $(date +'%Y%m%d_%H%M%S')"

    res=$(git push -u origin $BRANCH 2>&1)
    if [[ $res == *'fatal'* ]]
    then
        echo "ERROR: $NAME not pushed ! KO"
    else
        echo "INFO: $NAME pushed ! OK"
    fi

    cd ..
    
    sudo rm -Rf $NAME
done

echo -e "-------------\n"

exit 0
