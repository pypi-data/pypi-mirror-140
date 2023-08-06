import pandas as pd;
import numpy as np;
import copy;
import math;
import sys;

def main():
    class Error_wrong_inputs(Exception):
        pass
    class Input_file_name(Exception):
        pass
    class Result_file_name(Exception):
        pass
    class wghts_exception(Exception):
        pass
    class impcts_exception(Exception):
        pass
    class Col_Num_exception(Exception):
        pass
    class Not_Numeric_exception(Exception):
        pass
    class Postive_negative_exception(Exception):
        pass

    try:
        if len(sys.argv)<5 or len(sys.argv)>5:
            raise Error_wrong_inputs(len(sys.argv))
        file_name = sys.argv[1];
        df = pd.read_csv(file_name);
        if(len(df.columns)<3):
            raise Col_Num_exception(len(df.columns))
        for i in df.iloc[:-1,1:]:
            if not pd.to_numeric(df[i], errors='coerce').notnull().all():
                raise Not_Numeric_exception(i)
    except Error_wrong_inputs as err:
        print(f'Wrong number of inputs - {err}. Required 5')
    except FileNotFoundError:
        print(f'File with name {file_name} does not exist');
    except Col_Num_exception:
        print(f'The input file must contain 3 or more cols');
    except Not_Numeric_exception:
        print(f'All the values must be numeric');
    else:
        try:
            temp = file_name.split('.');
            wghts =  sys.argv[2].split(",");
            impcts = sys.argv[3].split(",");
            result_file_name = sys.argv[4];
            temp2 = result_file_name.split('.');

            if not 'csv' in temp:
                raise Input_file_name(file_name)
            if not 'csv' in temp2:
                raise Result_file_name(result_file_name)
            if len(wghts)!=len(df.columns)-1:
                raise wghts_exception(wghts)
            if len(impcts)!=len(df.columns)-1:
                raise impcts_exception(impcts)
            for i in impcts:    
                if i != "+" and i!= "-":
                    raise Postive_negative_exception(i)
        except Input_file_name as err:
            print(f'Err:Input data file must be csv file')
        except Result_file_name as err:
            print(f'Err:Result data file name must be csv file')
        except wghts_exception as err:
            print(f'Err: wghts should be equal to number of numeric cols and should be separated by commas')
        except impcts_exception as err:
            print(f'Err: impcts should be equal to number of numeric cols and should be separated by commas')
        except Postive_negative_exception:
            print(f'All the values in impcts must be +ve or -ve');
        else:
            new_df = copy.copy(df);
            print(new_df);
            print(new_df.columns);
            #Normalization
            norm = []
            for i in new_df.iloc[:-1,1:]:
                sum=0
                for j in new_df.loc[:,i]:
                    j = float(j)
                    sum += j**2
                norm.append(math.sqrt(sum))
            print(f'Normalization Vector - {norm}')
            index=0
            for i in new_df.iloc[:-1,1:]:
                new_df[i] = new_df[i].div(norm[index])
                index = index+1
            print(f'Normalized Data Frame - {new_df}')

            index=0
            print(f'wghts are - {wghts}')
            for i in new_df.iloc[:-1,1:]:
                new_df[i] = new_df[i] * float(wghts[index])
                index = index+1

            print(f'Data Frame after assinging wghts - {new_df}')

            index=0
            print(f'impcts - {impcts}')
            ideal_best = []
            ideal_worst = []
            for i in new_df.iloc[:-1,1:]:
                if impcts[index]=='+':
                    ideal_best.append(new_df[i].max())
                    ideal_worst.append(new_df[i].min())
                else:
                    ideal_best.append(new_df[i].min())
                    ideal_worst.append(new_df[i].max())
                index = index+1

            print(f'Ideal Best - {ideal_best}')
            print(f'Ideal Worst - {ideal_worst}')

            EucBest = []
            EucWorst = []

            for i in range(0,len(new_df.iloc[:,:1])):
                best = 0
                worst = 0
                for index,j in enumerate(new_df.iloc[i,1:]):
                    best += (j-ideal_best[index])**2
                    worst += (j-ideal_worst[index])**2
                EucBest.append(math.sqrt(best))
                EucWorst.append(math.sqrt(worst))

            print(f'Euc Best - {EucBest}')
            print(f'Euc Worst - {EucWorst}')

            performance = []
            for i in range(0,len(EucBest)):
                performance.append(EucWorst[i]/(EucBest[i]+EucWorst[i]))

            print(f'Performance - {performance}')

            new_df['Topsis Score'] = performance

            new_df['Rank'] = new_df['Topsis Score'].rank(ascending=0)

            print(f'Data Frame with Topsis Score & rank - {new_df}')

            new_df.to_csv(result_file_name,index=False);