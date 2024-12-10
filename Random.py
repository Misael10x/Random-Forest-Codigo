#!/usr/bin/env python
# coding: utf-8

# # Caso practico: Ramdom Forest
# 
# En este caso practico se pretende resolver un problema de deteccion de Malware en dispositivos Android mediante el analisis del trafico de red qe genra el dispositivo mediante el uso de subconjuntos de arboles de decision.
# 
# ### DataSet: Deteccion de Malware en Android
# 
# #### Descripcion
# Android adware and general malware dataset (CIC-AAGM2017)
# The sophisticated and advanced Android malware is able to identify the presence of the emulator used by the malware analyst and in response, alter its behaviour to evade detection. To overcome this issue, we installed the Android applications on the real device and captured its network traffic. 
# 
# CICAAGM dataset is captured by installing the Android apps on the real smartphones semi-automated. The dataset is generated from 1,900 applications with the following three categories:
# 
# 1. Adware (250 apps)
# Airpush: Designed to deliver unsolicited advertisements to the user’s systems for information stealing.
# 
# Dowgin: Designed as an advertisement library that can also steal the user’s information.
# 
# Kemoge: Designed to take over a user’s Android device. This adware is a hybrid of botnet and disguises itself as popular apps via repackaging.
# 
# Mobidash: Designed to display ads and to compromise user’s personal information.
# 
# Shuanet: Similar to Kemoge, Shuanet is also designed to take over a user’s device.
# 
# 2. General Malware (150 apps)
# AVpass: Designed to be distributed in the guise of a Clock app.
# 
# FakeAV: Designed as a scam that tricks user to purchase a full version of the software in order to re-mediate non-existing infections.
# 
# FakeFlash/FakePlayer: Designed as a fake Flash app in order to direct users to a website (after successfully installed).
# 
# GGtracker: Designed for SMS fraud (sends SMS messages to a premium-rate number) and information stealing.
# 
# Penetho: Designed as a fake service (hacktool for Android devices that can be used to crack the WiFi password). The malware is also able to infect the user’s computer via infected email attachment, fake updates, external media and infected documents.
# 
# 3. Benign (1,500 apps)
# 2015 GooglePlay market (top free popular and top free new)
# 
# 2016 GooglePlay market (top free popular and top free new)
# 
# License
# The CICAAGM dataset consists of the following items is publicly available for researchers.
# 
# .pcap files – the network traffic of both the malware and benign (20% malware and 80% benign)
# 
# .csv files - the list of extracted network traffic features generated by the CIC-flowmeter
# 
# If you are using our dataset, you should cite our related paper that outlines the details of the dataset and its underlying principles:
# 
# Arash Habibi Lashkari, Andi Fitriah A. Kadir, Hugo Gonzalez, Kenneth Fon Mbah and Ali A. Ghorbani, “Towards a Network-Based Framework for Android Malware Detection and Characterization”, In the proceeding of the 15th International Conference on Privacy, Security and Trust, PST, Calgary, Canada, 2017.
# 

# ### Imports

# In[1]:


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import f1_score


# ### Funciones Auxiliares

# In[2]:


# Construcción de una función que realize el particionado completo.
def train_val_test_split(df, rstate=42, shuffle=True, stratify=None):
    strat = df[stratify] if stratify else None 
    train_set, test_set = train_test_split(
        df, test_size = 0.4, random_state = rstate, shuffle = shuffle, stratify = strat)
    strat = train_test[stratify] if stratify else None
    val_set, test_set = train_test_split(
        test_set, test_size=0.5, random_state = rstate, shuffle=shuffle, stratify = strat)
    return (train_set, val_set, test_set)


# In[3]:


def remove_labels(df, label_name):
    X = df.drop(label_name, axis=1)
    y = df[label_name].copy()
    return (X,y)


# In[4]:


def evaluate_result(y_pred, y, y_prep_pred, y_prep, metric):
    print(metric.__name__, "WITHOUT preparation", metric(y_pred, y, average="weighted"))
    print(metric.__name__, "WITH preparation", metric(y_prep_pred, y_prep, average="weighted"))


# ## 2.- Visualizacion del DataSet

# In[5]:


df = pd.read_csv('AndroiDataSet/AndroidAdware2017/TotalFeatures-ISCXFlowMeter.csv')


# In[6]:


df


# In[7]:


df.head(10)


# In[8]:


print("Longitud del Dataset:", len(df))
print("Numero de caracteristicas")


# In[9]:


# Transformamos las variable de salida a numerica para calcualar coorelaciones
X = df.copy()
X['calss'] = X['calss'].factorize()[0] 


# In[10]:


# Calcular correlaciones
corr_matrix = X.corr()
corr_matrix["calss"].sort_values(ascending = False)


# In[11]:


X.corr()


# In[12]:


# Se puede llegar y valorar y quedarnos con aquellos que tengan 
# mayor correlacion
corr_matrix[corr_matrix['calss'] > 0.05]


# ## 3.- Division de DataSet

# In[13]:


# Dividir del DataSet 
train_set, val_set, test_set = train_val_test_split(df)


# In[14]:


X_train, y_train = remove_labels(train_set, 'calss')
X_val, y_val = remove_labels(val_set, 'calss')
X_test, y_test = remove_labels(test_set, 'calss')


# ### **4.- Escalado del DataSet**
# 
# Es importante comprender que los arboles de desicion son algoritmos que **no requieren demasioanda preparacion de los datos** correctamente, no rquieren la realizacion o escalado o normalizacion.
# En este ejercicio se va a relizar escalado al DataSet y se van a comparar los resultados con el DataSet sin esclar.
# De esta manera se demuestra como aplicar preprocesamientos como el escalado puede llegar a fectar el rendimiento del modelo

# In[15]:


scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)


# In[16]:


scaler = RobustScaler()
X_test_scaled = scaler.fit_transform(X_test)


# In[17]:


scaler = RobustScaler()
X_val_scaled = scaler.fit_transform(X_val)


# In[18]:


from pandas import DataFrame


# In[19]:


# Realizar la transformación a un DataFrame de pandas
X_train_scaled = DataFrame(X_train_scaled, columns = X_train.columns, index=X_train.index)
X_train_scaled.head(10)


# In[20]:


X_train_scaled.describe()


# ## Decision Forrest

# In[21]:


# Modelo entrenado con el DataSet sin escalar
from sklearn.tree import DecisionTreeClassifier

clf_tree = DecisionTreeClassifier(random_state = 42)
clf_tree.fit(X_train, y_train)


# In[22]:


# Predecir con el DataSet de entrenamiento
y_train_pred = clf_tree.predict(X_train)


# In[23]:


print


# In[24]:


# Predecir con el dataset de validacion
y_val_pred = clf_tree.predict(X_val)


# In[25]:


# comparar resultados entre el escalado y sin escalar 
print("F1 Score Validation Set:", f1_score(y_val_pred, y_val, average='weighted'))


# ## 6.- Random Forest

# In[26]:


from sklearn.ensemble import RandomForestClassifier

# Modelo  entrenado con el DataSet sin escalar
clf_rnd = RandomForestClassifier(n_estimators=100, random_state = 42, n_jobs = -1)
clf_rnd.fit(X_train, y_train)


# In[27]:


# Modelo de entrenamiento con el DataSet escalodo
clf_rnd_scaled = RandomForestClassifier(n_estimators=100, random_state = 42, n_jobs = -1)
clf_rnd_scaled.fit(X_train_scaled, y_train)


# In[28]:


# Predecir con el DataSet de entrenamiento
y_train_pred = clf_rnd.predict(X_train)
y_train_prep_pred = clf_rnd_scaled.predict(X_train_scaled)


# In[29]:


# Comparar resultados entre el escalado y sin escalar
evaluate_result(y_train_pred, y_train, y_train_prep_pred, y_train, f1_score)


# ## 7.- Regresion Forest

# In[30]:


from sklearn.ensemble import RandomForestRegressor


# In[31]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as pltweb: gunicorn app:app
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Paso 1: Transformar la variable de salida a valores numéricos (si es categórica)
X = df.copy()
X['calss'] = X['calss'].factorize()[0]

# Paso 2: Separar las variables predictoras y la variable de salida
X_features = X.drop('calss', axis=1)  # Las características (sin la variable de salida)
y_target = X['calss']  # La variable de salida

