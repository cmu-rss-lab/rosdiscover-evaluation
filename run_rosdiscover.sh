pushd ~/rosdiscover
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug.yml > ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug_out.yml
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug.yml > ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_out.yml
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix.yml > ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix_out.yml

pipenv run rosdiscover acme --acme ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug.acme --from-yml ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug_out.yml  ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug.yml
pipenv run rosdiscover acme --acme ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug.acme --from-yml ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_out.yml  ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug.yml
pipenv run rosdiscover acme --acme ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix.acme --from-yml ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix_out.yml  ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix.yml
