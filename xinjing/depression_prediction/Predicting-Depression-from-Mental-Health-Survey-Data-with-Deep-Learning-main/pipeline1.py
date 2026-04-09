# Import necessary libraries
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTENC
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from scikeras.wrappers import KerasClassifier


# --- Custom Transformers ---
# Handles missing values by filling them using related columns
class NullSatisfactionFiller(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        df = X.copy()
        df['Study/job Satisfaction'] = df['Study Satisfaction'].fillna(df['Job Satisfaction'])
        df['Academic/work Pressure'] = df['Academic Pressure'].fillna(df['Work Pressure'])
        return df

# Drops unnecessary columns like IDs, names, and unrelated attributes
class ColumnDropper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        df = X.copy()
        cols_to_drop = ['CGPA','Name','Gender','id','City','Profession',
                        'Academic Pressure','Work Pressure','Degree',
                        'Study Satisfaction','Job Satisfaction']
        return df.drop(columns=cols_to_drop)

# Corrects categorical feature formats and converts categorical values
class FormatCorrector(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        # Dietary Habits
        correct_dh = ['Moderate', 'Unhealthy', 'Healthy']
        df['Dietary Habits'] = df['Dietary Habits'].apply(lambda x: x if x in correct_dh else None)
        
        # Sleep Duration
        correct_SD = ['Less than 5 hours', '1-2 hours', '2-3 hours', '3-4 hours', '4-5 hours',
                      '5-6 hours', '6-7 hours', '7-8 hours', '8-9 hours', '9-11 hours', 
                      '10-11 hours', 'More than 8 hours']
        sleep_map = {
            'Less than 5 hours': 4, '1-2 hours': 1.5, '2-3 hours': 2.5,
            '3-4 hours': 3.5, '4-5 hours': 4.5, '5-6 hours': 5.5, '6-7 hours': 6.5,
            '7-8 hours': 7.5, '8-9 hours': 8.5, '9-11 hours': 10,
            '10-11 hours': 10.5, 'More than 8 hours': 9
        }
        df['Sleep Duration'] = df['Sleep Duration'].apply(lambda x: x if x in correct_SD else np.nan)
        df['Sleep Duration'] = df['Sleep Duration'].map(sleep_map)
        return df

# Drops rows with missing values
class NullDropper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.dropna().copy()

# Handles class imbalance by applying SMOTENC (Synthetic Minority Oversampling)
class SMOTENCTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, target='Depression'):
        self.target = target

    def fit(self, X, y=None):
        return self

    def transform(self, df):
        # Skip if target not present (i.e., in test data)
        if self.target not in df.columns:
            return df

        X_ = df.drop(columns=self.target)
        y_ = df[self.target]

        categorical_cols = [
            'Working Professional or Student',
            'Dietary Habits',
            'Have you ever had suicidal thoughts ?',
            'Financial Stress',
            'Family History of Mental Illness',
            'Academic/work Pressure',
            'Study/job Satisfaction'
        ]
        cat_idx = [X_.columns.get_loc(col) for col in categorical_cols if col in X_.columns]

        smote = SMOTENC(categorical_features=cat_idx, random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_, y_)

        # Create DataFrame with resampled data
        df_res = pd.DataFrame(X_resampled, columns=X_.columns)
        df_res[self.target] = y_resampled

        # Post-processing numeric columns
        for col in ['Age', 'Work/Study Hours', 'Study/job Satisfaction', 'Academic/work Pressure', 'Financial Stress']:
            if col in df_res.columns:
                df_res[col] = df_res[col].round().astype(int)

        # Apply valid range filters and ensure target is filtered too
        mask = (
            df_res['Age'].between(15, 60) &
            df_res['Work/Study Hours'].between(0, 12) &
            df_res['Study/job Satisfaction'].between(1, 5) &
            df_res['Academic/work Pressure'].between(1, 5) &
            df_res['Financial Stress'].between(1, 5)
        )
        df_res = df_res[mask].copy()
        y_resampled = y_resampled[mask]  # Filter target to match

        # Reattach filtered target to DataFrame
        df_res[self.target] = y_resampled

        return df_res

# Removes outliers in the Age column based on interquartile range (IQR)
class OutlierClipper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, df):
        if 'Depression' not in df.columns:
            return df

        g1 = df[df['Depression'] == 1].copy()
        g0 = df[df['Depression'] == 0].copy()

        Q1 = g1['Age'].quantile(0.25)
        Q3 = g1['Age'].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        g1['Age'] = g1['Age'].clip(lower=lower, upper=upper)
        df_out = pd.concat([g0, g1]).reset_index(drop=True)
        
        # Verify sample count
        if len(df_out) != len(df):
            print(f"Warning: Sample count changed from {len(df)} to {len(df_out)} in OutlierClipper")
        
        return df_out
# Converts categorical variables into one-hot encoded format
class OneHotEncoderWrapper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.categorical_cols = X.select_dtypes(include='object').columns.tolist()
        self.encoder = OneHotEncoder(drop='first', handle_unknown='ignore')
        self.encoder.fit(X[self.categorical_cols])
        return self

    def transform(self, X):
        df = X.copy()
        encoded = self.encoder.transform(df[self.categorical_cols]).toarray()
        encoded_df = pd.DataFrame(encoded, columns=self.encoder.get_feature_names_out(self.categorical_cols), index=df.index)
        df = pd.concat([df.drop(columns=self.categorical_cols), encoded_df], axis=1)
        return df

# Cleans column names by replacing spaces with underscores
class ColumnNameCleaner(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        df.columns = df.columns.str.replace(" ", "_")
        return df
    
# class ScalerWrapperm(BaseEstimator, TransformerMixin):
#     def fit(self, X, y=None):
#         self.scaler = StandardScaler()
#         self.scaler.fit(X)
#         return self
    
#     def transform(seelf, X):
#         return pd.DataFrame(self.scaler.transforum(X), columns=X.columns)