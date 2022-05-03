import json
import os
from subprocess import call

import graphviz
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.tree import export_graphviz
import numpy as np

"""
Machine Learning
"""

"""
Load Data
"""
user_JSON = open(os.getcwd()+"/resources/json/users_IA_clases.json".replace('/', '\\'), "r")
user_info = json.load(user_JSON)

usuario = []
emails_phishing_recibidos = []
emails_phishing_clicados = []
emails = []
vulnerable = []

for line in user_info['usuarios']:
    usuario.append(line['usuario'].replace(".", " "))
    emails_phishing_recibidos.append(line['emails_phishing_recibidos'])
    emails_phishing_clicados.append(line['emails_phishing_clicados'])
    if line['emails_phishing_recibidos'] != 0:
        emails.append(line['emails_phishing_clicados'] / line['emails_phishing_recibidos'])
    else:
        emails.append(0)

    vulnerable.append(line['vulnerable'])

user_X = pd.DataFrame({'phishing': emails})
user_Y = pd.DataFrame({'vulnerable': vulnerable})

"""
Regresion lineal
"""

user_X_train = user_X[:-20]
user_X_test = user_X[-20:]

user_Y_train = user_Y[:-20]
user_Y_test = user_Y[-20:]

reg = LinearRegression()
reg.fit(user_X_train, user_Y_train)
print(reg.coef_)
user_Y_pred = reg.predict(user_X_test)
user_pred = []

for valor in user_Y_pred:
    if valor < 0.5:
        user_pred.append(0)
    else:
        user_pred.append(1)

#print("Mean squared error: %.2f" % accuran (user_Y_test, user_pred))
# The coefficient of determination: 1 is perfect prediction
print("Coefficient of determination: %.2f" % r2_score(user_Y_test, user_pred))


# Plot outputs

plt.scatter(user_X_test.values.ravel(), user_Y_test, color="black")
print("X", user_Y_test)
print("score", r2_score(user_Y_test, user_pred))
print("intercept", reg.intercept_)
plt.plot(reg.coef_[0]*np.array(user_X_test.values.ravel())+reg.intercept_, user_pred, color="blue", linewidth=3)
plt.xticks()
plt.yticks()
plt.xlabel("Prob_click")
plt.ylabel("Vulnerable")
plt.show()

"""
Decision tree
"""

clf = tree.DecisionTreeClassifier()
clf = clf.fit(user_X_train, user_Y_train)

# Print plot
dot_data = tree.export_graphviz(clf)
graph = graphviz.Source(dot_data)
graph.render("machine_learning/tree_graph_render")
dot_data = tree.export_graphviz(clf,
                                feature_names=['email click'],
                                class_names=['No vulnerable', 'Vulnerable'],
                                filled=True, rounded=True,
                                special_characters=True)
graph = graphviz.Source(dot_data)
graph.render('machine_learning/tree.gv', view=True).replace('\\', '/')

"""
Random forest
"""

clf = RandomForestClassifier(max_depth=5, random_state=0, n_estimators=10)
clf.fit(user_X_train.values.ravel().reshape(-1, 1), user_Y_train.values.ravel())

for i in range(len(clf.estimators_)):
    print(i)
    estimator = clf.estimators_[i]
    export_graphviz(estimator,
                    out_file='machine_learning/random_forest/random_forest.dot',
                    feature_names=['email click'],
                    class_names=['No vulnerable', 'Vulnerable'],
                    rounded=True, proportion=False,
                    precision=2, filled=True)
    call(['dot', '-Tpng', os.getcwd()+'/machine_learning/random_forest/random_forest.dot'.replace('/', '\\'), '-o', os.getcwd()+'/machine_learning/random_forest/random_forest_tree_'.replace('/', '\\') + str(i) + '.png',
          '-Gdpi=600'], cwd='machine_learning', shell=True)
