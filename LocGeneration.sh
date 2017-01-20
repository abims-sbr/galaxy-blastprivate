
DIR="/db/blast/all"
KEYWORD=$1
OUT=$2

ls $DIR | grep '.nhr' | grep $KEYWORD | sed -r 's/^(.*)\.nhr$/\1/g' > Liste_db

awk -v dr=$DIR 'BEGIN {print "#<unique_id>\t<database_caption>\t<base_name_path>"}
	{print $0"\t"$0"\t"dr"/"$0}' Liste_db > "tool-data/"$OUT

