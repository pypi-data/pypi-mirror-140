from sklearn.preprocessing import StandardScaler
class df_ops:
    def __init__(self, df):
        try:
            self.df = df
        except Exception as e:
            raise Exception(f'Something went wrong to initialize the process:{str(e)}')

    def removeNull(self):
        '''It removes null values of a column in dataframe with its mean'''
        try:
            col_names = self.df.columns
            null_col = self.df.isnull().sum()
            for idx, val in enumerate(null_col):
                if val != 0:
                    self.df[col_names[idx]] = self.df[col_names[idx]].fillna(self.df[col_names[idx]].mean())
        except Exception as e:
            raise Exception(f'(removeNull)-Something went wrong:{str(e)}')

    def getStandardScaler(self):
        '''It return the standard normal distribution of the data'''
        try:
            scaler = StandardScaler()
            self.df = scaler.fit_transform(self.df)
            return self.df
        except Exception as e:
            raise Exception('(getStandardScaler)-Something went wrong:{str(e)}')