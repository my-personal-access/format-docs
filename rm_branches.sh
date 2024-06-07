#!/bin/bash

echo "##########################################################################"
echo "######################## Removing remote Branches ########################"
echo "##########################################################################"

for project_id in $@
do
       BRANCHES=$(curl -s -k "https://$GITLAB_SERVER/api/v4/projects/$project_id/repository/branches" | jq -r '.[] | select(.name | startswith("Auto-Review/")) | .name')
       for branche in ${BRANCHES[@]}
       do
               # URL encoded
               ENCODED_BRANCH=$(echo $branche | sed 's/\//%2F/g' )
               curl -k -s --request DELETE --header "PRIVATE-TOKEN: $GITLAB_API_KEY" "https://$GITLAB_SERVER/api/v4/projects/$project_id/repository/branches/$ENCODED_BRANCH"
               echo "$project_id/$branche branch deleted"
       done
done

echo -e "-------------\n"
