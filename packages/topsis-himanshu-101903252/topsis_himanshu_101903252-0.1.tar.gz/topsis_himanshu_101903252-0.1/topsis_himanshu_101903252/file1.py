import pandas as pd
import numpy as np

class topsis():
    def __init__(self,data,weights,impacts):
        self.data=data
        self.w=weights
        self.i=impacts

    def gettopsisResult(self):

        new_data = self.data.values[:,1:]

        rofsquares = [np.sqrt(sum(np.square(arr))) for arr in new_data.transpose()]
        rofsquares=np.array(rofsquares)

        normalizesd_data = np.array([new_data.transpose()[i]/rofsquares[i] for i in range(len(rofsquares))] ).transpose()

        weighted_normalizesd_data = np.array([normalizesd_data.transpose()[i]*self.w[i] for i in range(len(self.w))] ).transpose()

        y=0
        ideal_best= []
        ideal_worst=[]
        for x in self.i:
            if x=='+':
                ideal_best.append(max(weighted_normalizesd_data.transpose()[y]))
                ideal_worst.append(min(weighted_normalizesd_data.transpose()[y]))
            if x=='-':
                ideal_worst.append(max(weighted_normalizesd_data.transpose()[y]))
                ideal_best.append(min(weighted_normalizesd_data.transpose()[y]))
            y=y+1

        ideal_best,ideal_worst

        Splus = np.array([np.sqrt(np.sum(np.square(weighted_normalizesd_data[i]-np.array(ideal_best)))) for i in range(len(weighted_normalizesd_data))])
        Splus

        Sminus = np.array([np.sqrt(np.sum(np.square(weighted_normalizesd_data[i]-np.array(ideal_worst)))) for i in range(len(weighted_normalizesd_data))])
        Splus,Sminus

        Pscore = Sminus/(Splus+Sminus)
        Pscore

        temp = Pscore.argsort()[::-1]
        ranks = np.empty_like(temp)
        ranks[temp] = np.arange(len(Pscore))
        ranks=ranks+1
        ranks

        self.data['Topsis Score']=Pscore
        self.data['Rank'] = ranks
        return self.data

