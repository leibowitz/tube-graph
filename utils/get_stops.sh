cat $1 | jq '.[] | {(.from): (.to)}' | sort -u | ghead -n -2 | tr -d '"' | tr -s " " | sed 's/^ *//' | sed 's/: /:/' | gcut -d':' -f1,2 --output-delimiter=','
