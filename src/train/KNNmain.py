import sklearn
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import pickle

# opening csv with pandas
data = pd.read_csv("data.csv")
party_labels = data[["party"]]

# separating data into feature and results
X = data[data.columns[1:-1]].values
y = party_labels.values.ravel()

# will hold the model and accuracy for the best model
best = [0,0]

for i in range(1000):

    # separating data into random parts
    x_train,x_test,y_train,y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.20)

    # setup and train model
    model = KNeighborsClassifier(n_neighbors=11)
    model.fit(x_train,y_train)

    # predict results to tell accuracy
    y_pred = model.predict(x_test)
    acc = model.score(x_test, y_test)

    # checks if this instance of the model is better than the best
    if acc>best[1]:
        best[0] = model
        best[1] = acc

    print(acc,best)

# saves best model
model=best[0]
pickle.dump(model, open("modelKNN.pickle", 'wb'))
