1. Data collection & cleaning (stats-examination.ipynb, stats-processing.ipynb)
   1. Script to crawl & scrape profootballarchives
   2. Collect: team name, date of games, opponents, wlt, h/a, overtime, location, team/opponent scores, attendance, notes
   3. Derive: score sum/difference, class for wlt, percent score for team/opponent
   4. Drop: overtime, attendance, notes, date
   5. Generate: extra columns based on last-n-games (5 used), for score & location
2. Modelling
   1. All models try to predict the odds of a team winning the game. This means that the team & opponent can be evaluated separately for the same game, and their outputs compared to give the odds of a tie.
   2. Start with SVC (last-n-games-scores-only cell 20)
   3. Grid search over linear, poly, rbf, sigmoid and different Cs (all other params default)
      1. Linear performs consistently well, doesn't overfit
      2. Poly overfits
      3. rbf overfits
      4. sigmoid overfits
   4. Performance is ok overall, trends up with more columns generally
   5. Bagging tree ensemble
      1. Grid search cell 22
      2. Capable of overfitting, but also outperforms svms
      3. Explored in more thorough grid search cell 23 & 24 (f'kin long)
   6. Single deep tree
      1. Overfits, but gets similar performance to bagged ensemble
   7. LinearSVC
      1. Faster than generalized SVC
      2. Deeper grid search performed, take best c's and perturb them slightly to try some hill climbing
      3. Doesn't actually beat tree ensembles
   8. XGBoost, CatBoost
      1. Fancy state-of-the-art tree ensembles
      2. Mostly out-of-the-box training
      3. Outperforms manual grid search over bagged ensembles, and runs much faster
3. Evaluating models
   1. All promising models 5-fold cross-validated
   2. Test set witheld entirely
   3. Accuracy of predictions _isn't_ the target predictor, though it is what these models explored
   4. Payout is optimistically explored
      1. results pending