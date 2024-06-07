#!/bin/bash

PROJECT_PATH=$( dirname -- "$( readlink -f -- "$0"; )"; )

function get_branch() {
        if [[ $PROJECT_PATH == *'/dev/'* ]]
        then
                BRANCH=dev
        elif [[ $PROJECT_PATH == *'/master/'* ]]
        then
                BRANCH=master
        else
                echo "Wrong folder: run.sh must be located in /home/master/* or /home/dev/*"
                exit 1
        fi
} 


function fetch_repos_ids() {
        # If any arg is passed to the main ; then occur on all projects
        if [ $# -eq 0 ]
        then
                for i in $(seq 1 2)
                do
                        # Fetch each page result (page limit is 100)
                        PAGE_IDS=$(curl -s -k "https://$GITLAB_SERVER/api/v4/groups/885/projects?per_page=100&page=$i" | jq '.[]|select(.name|startswith("hwi6_"))|.id')
                        # Concat pages results
                        IDS=( "${IDS[@]}" "${PAGE_IDS[@]}" )
                done
        else
                for i in $@
                do
                        RESPONSE=$(curl -s --request GET --header "PRIVATE-TOKEN: $GITLAB_API_KEY" "https://$GITLAB_SERVER/api/v4/groups/885/search?scope=projects&search=$i" | jq -r .)
                        if [ $(echo $RESPONSE | jq -r '.|length') -gt 0 ]
                        then
                                if [[ ! -z $(echo $RESPONSE | jq -r '.[]|select(.name=="'$i'")|.name') ]]
                                then
                                        IDS=( "${IDS[@]}" "$(echo $RESPONSE | jq -r '.[]|select(.name=="'$i'")|.id')" )
                                else
                                        echo "Elément $i non trouvé sur Gitlab"
                                fi
                        else
                                echo "Elément '$i' non trouvé sur Gitlab"
                        fi
                done
        fi
}

get_branch

IDS=()
if [[ $BRANCH == "master" ]]
then
        fetch_repos_ids $@
else
        if [ $# -gt 0 ]
        then
                fetch_repos_ids $@
        else
                IDS=( 1914 ) # ODSMSG GITLAB PROJECT ID
        fi
fi

cd $PROJECT_PATH

./rm_branches.sh ${IDS[@]}

./auto-review.sh ${IDS[@]}
