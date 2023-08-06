import pandas as pd
import numpy as np

class chiragtopsis():
    def __init__(self,data,weight,impact):
        self.data = data
        self.w = weight
        self.i = impact
    def getResult(self):
        new_data = self.data.values[:, 1:]

        rofsquares = [np.sqrt(sum(np.square(arr))) for arr in new_data.transpose()]
        rofsquares = np.array(rofsquares)
     
        normalizesd_data = np.array([new_data.transpose()[i]/rofsquares[i]
                                    for i in range(len(rofsquares))]).transpose()
        

        weighted_normalizesd_data = np.array(
            [normalizesd_data.transpose()[i]*self.w[i] for i in range(len(self.w))]).transpose()

        y = 0
        ideal_best = []
        ideal_worst = []
        for x in self.i:
            if x == '+':
                ideal_best.append(max(weighted_normalizesd_data.transpose()[y]))
                ideal_worst.append(min(weighted_normalizesd_data.transpose()[y]))
            if x == '-':
                ideal_worst.append(max(weighted_normalizesd_data.transpose()[y]))
                ideal_best.append(min(weighted_normalizesd_data.transpose()[y]))
            y = y+1


        Splus = np.array([np.sqrt(np.sum(np.square(weighted_normalizesd_data[i]-np.array(ideal_best))))
                        for i in range(len(weighted_normalizesd_data))])

        Sminus = np.array([np.sqrt(np.sum(np.square(weighted_normalizesd_data[i]-np.array(ideal_worst))))
                        for i in range(len(weighted_normalizesd_data))])

        Pscore = Sminus/(Splus+Sminus)

        temp = Pscore.argsort()[::-1]
        ranks = np.empty_like(temp)
        ranks[temp] = np.arange(len(Pscore))
        ranks = ranks+1

        self.data['Topsis Score'] = Pscore
        self.data['Rank'] = ranks
        return self.data



        