pushd ~/rosdiscover
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug.yml >& ~/rosdiscover-evaluation/bugs/$1/rd_$1_pre_bug_out.log
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug.yml >& ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_out.log
pipenv run rosdiscover launch ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix.yml >& ~/rosdiscover-evaluation/bugs/$1/rd_$1_bug_fix_out.log