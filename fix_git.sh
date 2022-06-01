# Sooo... If you want to git checkout different branches, you need to update the git repo to fetch ALL sources
git config --local --add remote.origin.fetch +refs/heads/*:refs/remotes/origin/*
