Just run preProcessing.py then you will probably get a temp.pkl file(preProcessing the data).

Then just run trainLGBM.py. You will probably get a model file and submission.csv that can calculate score on Kaggle. The score is about 0.85991.

And for more works I did, can take a look at the below link in Kaggle.
Train a simple LGBM:
(https://www.kaggle.com/tylerchenchen/predict-sales-problem-step-by-step-part1)

After training a LGBM, I dicide to use Optuna to tune the parameter of model.
So, below is I use Optuna to tune some parameters and retrain the model.
(https://www.kaggle.com/tylerchenchen/predict-sales-problem-step-by-step-part2)

What's more, for improving score, I even use the stacking model and combine to LGBM model.
Here is a small stacking model that I train.
(https://www.kaggle.com/tylerchenchen/predict-sales-problem-step-by-step-part3)

google slide:
https://docs.google.com/presentation/d/1uNSS7Uk7MnEztnnaMrTdJ4usUMtU6tqI5vRyYlI5mCo/edit?usp=sharing
