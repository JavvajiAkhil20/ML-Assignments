# -*- coding: utf-8 -*-
"""akhil_ml_lab_8

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g_9AeyzZqn3t-PxzCHCbdRQ2Vpr20dui
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import pylab as pl
from sklearn.metrics import roc_curve, auc
from sklearn import metrics    
from sklearn import feature_selection
import itertools
from sklearn.model_selection import cross_val_score
import warnings
import seaborn as sns
warnings.filterwarnings("ignore")

df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')
df.head()

df.isnull().sum() #To check whether there are any missing values

df.hist(edgecolor='black', linewidth=1.2, figsize=(20, 20));

"""As we see that standard deviation for EmployeeCount, StandardHours, Over18 is near zero so we can remove them. EmployeeNumber is an Indentification number which won't be helpful in prediction so we will also drop it."""

df.drop(['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours'], axis="columns", inplace=True)

categorical_col = []
for column in df.columns:
    if df[column].dtype == object and len(df[column].unique()) <= 50:
        categorical_col.append(column)
        print(f"{column} : {df[column].unique()}")
        print("====================================")

df['Attrition'] = df.Attrition.astype("category").cat.codes

def plot_cat(attr,labels=None):
    if(attr=='JobRole'):
        sns.factorplot(data=df,kind='count',size=5,aspect=3,x=attr)
        return
    
    sns.factorplot(data=df,kind='count',size=5,aspect=1.5,x=attr)

plot_cat('Attrition')

# Plotting how every feature correlate with the "target"
sns.set(font_scale=1.2)
plt.figure(figsize=(30, 30))

for i, column in enumerate(categorical_col, 1):
    plt.subplot(3, 3, i)
    g = sns.barplot(x=f"{column}", y='Attrition', data=df)
    g.set_xticklabels(g.get_xticklabels(), rotation=90)
    plt.ylabel('Attrition Count')
    plt.xlabel(f'{column}')

"""##Conclusions

**BusinessTravel** : The workers who travel alot are more likely to quit then other employees.

**Department** : The worker in Research & Development are more likely to stay then the workers on other departement.

**EducationField** : The workers with Human Resources and Technical Degree are more likely to quit then employees from other fields of educations.

**Gender** : The Male are more likely to quit.

**JobRole** : The workers in Laboratory Technician, Sales Representative, and Human Resources are more likely to quit the workers in other positions.

**MaritalStatus** : The workers who have Single marital status are more likely to quit the Married, and Divorced.

**OverTime** : The workers who work more hours are likely to quit then others.
"""

plt.figure(figsize=(30, 30))
sns.heatmap(df.corr(), annot=True, cmap="RdYlGn", annot_kws={"size":15})

categorical_col.remove('Attrition')

# Transform categorical data into dummies
# categorical_col.remove("Attrition")
# data = pd.get_dummies(df, columns=categorical_col)
# data.info()
from sklearn.preprocessing import LabelEncoder

label = LabelEncoder()
for column in categorical_col:
    df[column] = label.fit_transform(df[column])

X = df.drop('Attrition', axis=1)
y = df.Attrition

from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score

def print_score(clf, X, y, X_train, y_train, X_test, y_test, train=True):
    if train:
        pred = clf.predict(X_train)
        print("\nTrain Result:\n===========================================")
        print(f"accuracy score: {accuracy_score(y_train, pred):.4f}\n")
        train_accuracy.append(accuracy_score(y_train, pred))
        print(f"Classification Report: \n \tPrecision: {precision_score(y_train, pred)}\n\tRecall Score: {recall_score(y_train, pred)}\n\tF1 score: {f1_score(y_train, pred)}\n")
        print(f"Confusion Matrix: \n {confusion_matrix(y_train, clf.predict(X_train))}\n")
        
    elif train==False:
        pred = clf.predict(X_test)
        print("\nTest Result:\n===========================================")   
        test_accuracy.append(accuracy_score(y_test, pred))     
        print(f"accuracy score: {accuracy_score(y_test, pred)}\n")
        print(f"Classification Report: \n \tPrecision: {precision_score(y_test, pred)}\n\tRecall Score: {recall_score(y_test, pred)}\n\tF1 score: {f1_score(y_test, pred)}\n")
        print(f"Confusion Matrix: \n {confusion_matrix(y_test, pred)}\n")
        scores = cross_val_score(clf, X, y, cv=10)
        cv_accuracy.append(scores.mean())
        cv_devia.append(scores.std()*2)
        print(f"10-fold Cross Validation Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def plot_ROC(model, X_test, y_test):  
  probs = model.predict_proba(X_test)
  preds = probs[:,1]
  fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
  roc_auc = metrics.auc(fpr, tpr)
  roc_accuracy.append(roc_auc)
  # method I: plt
  plt.title('Receiver Operating Characteristic')
  plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
  plt.legend(loc = 'lower right')
  plt.plot([0, 1], [0, 1],'r--')
  plt.xlim([0, 1])
  plt.ylim([0, 1])
  plt.ylabel('True Positive Rate')
  plt.xlabel('False Positive Rate')
  plt.show()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

train_accuracy = []
test_accuracy = []
cv_accuracy = []
cv_devia = []
roc_accuracy = []

"""##Decision Tree"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV

params = {
    "criterion":("gini", "entropy"), 
    "splitter":("best", "random"), 
    "max_depth":(list(range(1, 20))), 
    "min_samples_split":[2, 3, 4], 
    "min_samples_leaf":list(range(1, 20)), 
}


model = DecisionTreeClassifier(random_state=42)
grid_search_cv = GridSearchCV(model, params, scoring="accuracy", n_jobs=-1, verbose=1, cv=3)

tree = DecisionTreeClassifier(ccp_alpha=0.0, class_weight=None, criterion='entropy',
                       max_depth=6, max_features=None, max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=10, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, presort='deprecated',
                       random_state=42, splitter='best')

tree.fit(X_train, y_train)

print_score(tree, X, y, X_train, y_train, X_test, y_test, train=True)
print_score(tree, X, y, X_train, y_train, X_test, y_test, train=False)

plot_ROC(tree,X_test,y_test)

"""##Random Forest

###GridSearchCV for random forest hyperparameter tuning
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV


param_grid = {'max_depth':[50, 60, 75], 
              'n_estimators':[1400, 1425, 1450],
              'max_features':['sqrt'],
              'min_samples_split':[4, 5, 6], 
              'min_samples_leaf':[1], 
              'bootstrap':[ False], 
              'criterion':["gini"]}

rand_frst_clf = RandomForestClassifier(random_state=42, n_estimators=1000)

grid_rand_forest = GridSearchCV(rand_frst_clf, param_grid, scoring="accuracy", 
                                n_jobs=-1, verbose=1, cv=3)

rand_forest = RandomForestClassifier(bootstrap=False, ccp_alpha=0.0, class_weight=None,
                       criterion='gini', max_depth=50, max_features='sqrt',
                       max_leaf_nodes=None, max_samples=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=4,
                       min_weight_fraction_leaf=0.0, n_estimators=1400,
                       n_jobs=None, oob_score=False, random_state=42, verbose=1,
                       warm_start=False)
log_reg.fit(X_train,y_train)
rand_forest.fit(X_train, y_train)

print_score(rand_forest, X, y, X_train, y_train, X_test, y_test, train=True)
print_score(rand_forest, X, y, X_train, y_train, X_test, y_test, train=False)

"""###Importance of features in random forest"""

feat_importances = pd.Series(rand_forest.feature_importances_, index=X.columns)
feat_importances = feat_importances.nlargest(20)
feat_importances.plot(kind='barh')

plot_ROC(rand_forest,X_test,y_test)

"""##Logistic Regression"""

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
clf = LogisticRegression()
grid_values = {'penalty': ['l1', 'l2'],'C':[0.001,.009,0.01,.09,1,5,10,25]}
log_reg = GridSearchCV(clf, param_grid = grid_values, scoring="accuracy", refit=True, cv=3, verbose=1)
log_reg.fit(X_train, y_train)
print(log_reg.best_estimator_)

log_reg = LogisticRegression(C=1, class_weight=None, dual=False, fit_intercept=True,
                   intercept_scaling=1, l1_ratio=None, max_iter=100,
                   multi_class='auto', n_jobs=None, penalty='l2',
                   random_state=None, solver='lbfgs', tol=0.0001, verbose=0,
                   warm_start=False)

log_reg.fit(X_train,y_train)
print_score(log_reg, X, y, X_train, y_train, X_test, y_test, train=True)
print_score(log_reg, X, y, X_train, y_train, X_test, y_test, train=False)

plot_ROC(log_reg,X_test,y_test)

"""##SVM"""

from sklearn import svm
from sklearn.model_selection import GridSearchCV 

param_grid = {'C': [0.1, 1, 10, 100, 1000], 
			'gamma': [1, 0.1, 0.01, 0.001, 0.0001], 
			'kernel': ['rbf']} 

SVM = GridSearchCV(svm.SVC(), param_grid, scoring="accuracy", refit = True, cv=3, verbose = 1) 
SVM.fit(X_train,y_train)

print(SVM.best_estimator_)
best = SVM.best_estimator_

SVM=svm.SVC(C=10, break_ties=False, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma=0.0001, kernel='rbf',
    max_iter=-1, probability=True, random_state=None, shrinking=True,
    tol=0.001, verbose=False)
SVM.fit(X_train,y_train)
print_score(SVM, X, y, X_train, y_train, X_test, y_test, train=True)
print_score(SVM, X, y, X_train, y_train, X_test, y_test, train=False)

plot_ROC(SVM,X_test,y_test)

models = ['Decision Tree', 'Random Forest', 'Logistic Regression' , 'SVM' ]

results = pd.DataFrame({"10-fold Cross Validation":cv_accuracy[0:4], "Std Deviation(+/-)":cv_devia[0:4], "Roc score" : roc_accuracy[0:4], "Test Accuracy" : test_accuracy[0:4] , "Train Accuracy" : train_accuracy[0:4]} , index = models)
results

"""Above we can compare all four models and by looking at Cross Validation scores along with standard deviation we can conclude that Random Forest is the best model.
Also the ROC Score of Random Forest is highest.
"""