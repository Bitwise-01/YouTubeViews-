#!/bin/bash
script=("python youtube.py  2 youtubeLinks.txt 50 184") #Make changes you wish to do here.
counter=1
echo $script
while [ $counter -le 10 ] # replace 10 with number of times you want to run the script
do
	 $script
	((counter++))
done
echo "Done" # you will see Done when script has run 10 times
