import json
from subprocess import call

import graphviz
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_graphviz

"""
Machine Learning
"""

"""
Load Data
"""
user_JSON = open("resources/json/users_IA_clases.json", "r")
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

print("Mean squared error: %.2f" % mean_squared_error(user_Y_test, user_Y_pred))

# Plot outputs

plt.scatter(user_X_test.values.ravel(), user_Y_test, color="black")
plt.plot(user_X_test.values.ravel(), user_Y_pred, color="blue", linewidth=3)
plt.xticks(())
plt.yticks(())
plt.show()

"""
Decision tree
"""

clf = tree.DecisionTreeClassifier()
clf = clf.fit(user_X_train, user_Y_train)

# Print plot
dot_data = tree.export_graphviz(clf, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("Usuarios Criticos")
dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=['email click'],
                                class_names=['No vulnerable', 'Vulnerable'],
                                filled=True, rounded=True,
                                special_characters=True)
graph = graphviz.Source(dot_data)
graph.render('test.gv', view=True).replace('\\', '/')

"""
Random forest
"""

clf = RandomForestClassifier(max_depth=5, random_state=0, n_estimators=10)
clf.fit(user_X_train.values.ravel().reshape(-1, 1), user_Y_train.values.ravel())
print(user_Y_train.values.ravel())
print(user_X_train.values.ravel().reshape(-1, 1))

for i in range(len(clf.estimators_)):
    print(i)
    estimator = clf.estimators_[i]
    export_graphviz(estimator,
                    out_file='./treeDir/tree.dot',
                    feature_names=['email click'],
                    class_names=['No vulnerable', 'Vulnerable'],
                    rounded=True, proportion=False,
                    precision=2, filled=True)
    call(['dot', '-Tpng', 'C:\\Users\\eilee\\Desktop\\pythonProject\\treeDir\\tree.dot', '-o', 'tree' + str(i) + '.png',
          '-Gdpi=600'], cwd='C:\\Users\\eilee\\Desktop\\pythonProject\\treeDir\\', shell=True)
"""
"""
