# !/usr/bin/env bash

#
# Squash github commits starting from a point
#

point="0458ce54553349ec02da82252956982097cdf9fc"
message="Develop"

git reset --soft ${point}
git add --all
git commit --message=${message}
git push --force --follow-tags
