"""Rebuild the synthetic demonstration models.
Run from the repository root: python models/train_model.py
The checked-in model artifacts were trained only on synthetic data.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.inspection import permutation_importance

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'synthetic_patients.csv'
OUT=ROOT/'models'
FEATURES=['age','sex','primary_condition','chronic_conditions','prior_admissions_12m','prior_ed_visits_12m','length_of_stay','medication_count','followup_scheduled','transportation_barrier','lives_alone','rural_distance_miles','home_health_referral']
NUM=['age','chronic_conditions','prior_admissions_12m','prior_ed_visits_12m','length_of_stay','medication_count','rural_distance_miles']
CAT=[c for c in FEATURES if c not in NUM]

def main():
    df=pd.read_csv(DATA)
    X,y=df[FEATURES],df['readmitted_30d']
    pre=ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUM),('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]),CAT)])
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.30,random_state=42,stratify=y)
    candidates={'Logistic Regression':LogisticRegression(max_iter=2000,class_weight='balanced',random_state=42),'Random Forest':RandomForestClassifier(n_estimators=450,max_depth=7,min_samples_leaf=3,class_weight='balanced',random_state=42)}
    results={}; fitted={}
    for name,est in candidates.items():
        pipe=Pipeline([('preprocessor',pre),('classifier',est)]).fit(Xtr,ytr)
        p=pipe.predict_proba(Xte)[:,1]; pred=(p>=.5).astype(int)
        results[name]={'roc_auc':round(float(roc_auc_score(yte,p)),3),'accuracy':round(float(accuracy_score(yte,pred)),3),'precision':round(float(precision_score(yte,pred,zero_division=0)),3),'recall':round(float(recall_score(yte,pred,zero_division=0)),3),'f1':round(float(f1_score(yte,pred,zero_division=0)),3),'confusion_matrix':confusion_matrix(yte,pred).tolist()}
        fitted[name]=pipe
    best=max(results,key=lambda k:results[k]['roc_auc'])
    joblib.dump(fitted[best],OUT/'care_transition_model.pkl')
    joblib.dump(fitted['Logistic Regression'],OUT/'logistic_baseline.pkl')
    joblib.dump(fitted['Random Forest'],OUT/'random_forest_model.pkl')
    meta={'best_model':best,'training_rows':len(Xtr),'test_rows':len(Xte),'outcome_rate':round(float(y.mean()),3),'threshold':.5,'metrics':results,'synthetic_data':True,'model_version':'1.0.0'}
    (OUT/'model_metrics.json').write_text(json.dumps(meta,indent=2))
    pi=permutation_importance(fitted[best],Xte,yte,n_repeats=15,random_state=42,scoring='roc_auc')
    pd.DataFrame({'feature':FEATURES,'importance':pi.importances_mean,'std':pi.importances_std}).sort_values('importance',ascending=False).to_csv(OUT/'feature_importance.csv',index=False)
    print(json.dumps(meta,indent=2))
if __name__=='__main__': main()
