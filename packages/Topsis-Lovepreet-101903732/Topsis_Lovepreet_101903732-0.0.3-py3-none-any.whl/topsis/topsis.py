import pandas as pd
import math
import sys

log=open('101903732-log.txt','w')


def f_topsis(df, w, i):
    data=df.copy(deep=True)
    log.write(f'-> Performing topsis \n')
    no_feature = len(data.columns) - 1
    no_val = len(data.index);

    ideal_best = []
    ideal_worst = []
    for i in range(1, no_feature + 1):
        k = math.sqrt(sum(data.iloc[:, i] * data.iloc[:, i]))
        max_val = 0;
        min_val = 1;
        for j in range(0, no_val):
            data.iloc[j, i] = (data.iloc[j, i] / k) * int(w[i - 1])
            max_val = max(max_val, data.iloc[j, i])
            min_val = min(min_val, data.iloc[j, i])
        if impact[i - 1] == '+':
            ideal_best.append(max_val)
            ideal_worst.append(min_val)
        else:
            ideal_best.append(min_val)
            ideal_worst.append(max_val)

    r = []
    for i in range(no_val):
        db = math.sqrt(sum((data.iloc[i, 1:] - ideal_best) ** 2))
        dw = math.sqrt(sum((data.iloc[i, 1:] - ideal_worst) ** 2))
        score = dw / (dw + db)
        r.append([i, score])
    r.sort(key=lambda x: x[1])
    for rank in range(1, len(r) + 1):
        r[rank - 1].append(rank)
    r.sort(key=lambda x: x[0])
    x = pd.DataFrame(r)
    df['Topsis Score'] = x.iloc[:, 1]
    df['Rank'] = x.iloc[:, 2]
    # print(df.head())
    return df


if __name__ == '__main__':

    lst = sys.argv

    if len(lst) != 5:
        log.write('-> wrong arguments Try "file.py weights impacts input.csv"\n ')
        # print('wrong arguments Try "file.py weights impacts input.csv"')

    else:
        try:
            log.write(f'-> Reading file {lst[1]}')
            data = pd.read_csv(lst[1]);
            if data.shape[1]<3:
                log.write('-> Input file must contain three or more columns.')
            else:

                weight = lst[2]
                w = weight.split(',')
                impact = lst[3]
                imp = impact.split(',')

                if len(w) == len(data.columns)-1 and len(imp) == len(data.columns)-1:
                    if all(p == '+' or p == '-' for p in imp):
                        ans = f_topsis(data, w, imp)
                        ans.to_csv(lst[4],index=False)
                        # print(ans)
                        log.write(f'-> Done Successfully !! \n-> Output in {lst[4]}')
                    else:
                        log.write('-> weights must be either "+" or "-"\n')
                else:
                    log.write('-> The no. of weights and impact does not match with no.of feature columns\n ')
        except OSError as e:
            log.write(f'-> {str(e)}')
    log.close()
# python 101903732.py 101903732-data.csv 1,1,1,2,1 +,+,-,+,+ 101903732-result.csv
