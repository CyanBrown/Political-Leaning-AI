import pickle

# loads model
with open("../train/modelKNN.pickle", 'rb') as f:
    model = pickle.load(f)

# function to call from respond
def guess(l):
    # predicts party
    party = model.predict([l])

    return party[0]


