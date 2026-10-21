#!/bin/fish

if set -q argv[1]
	cd $argv[1]
end

set yq /mnt/Games/SteamLibrary/steamapps/common/Mashinky/yq

for meta in */meta.xml
	set -l mod (basename (dirname $meta))
	# set -l resp (curl -s -o /dev/null -L -w "%{http_code}" 'https://steamcommunity.com/sharedfiles/filedetails/?id='"$mod")
	# if test $resp -eq 429
	# 	sleep 30
	# 	set resp (curl -s -o /dev/null -L -w "%{http_code}" 'https://steamcommunity.com/sharedfiles/filedetails/?id='"$mod")
	# end
	set -l name ($yq '.name.+@value' -oy $meta 2>&1)
	set -l name ($yq '.description.+@value' -oy $meta 2>&1)
	echo -e "$mod\t""[https://steamcommunity.com/sharedfiles/filedetails/?id=$mod""]\t$name\t$description"
	#sleep 1
end
