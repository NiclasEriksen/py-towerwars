#!/bin/zsh

git add ~/src/peace-tw/

echo "Commit message:"

read message

git commit -m "$message"

git push origin master