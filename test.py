import pandas as pd

df = pd.read_csv('Arquivos_CSV/22.11.2022_18h26.csv')

df_tempo = df[df["tempo"].between(2682, 29110)]
acc_avg = round(df_tempo["ACC"].mean(), 2)
vel_avg = round(df_tempo["VEL_E"].mean(), 2)
distancia_lap = df_tempo["Distancia"].iloc[-1] - df_tempo["Distancia"].iloc[0]
tempo_percorrido = df_tempo["tempo"].iloc[-1] - df_tempo["tempo"].iloc[0]
print(df_tempo)
print(acc_avg, vel_avg, distancia_lap, tempo_percorrido)
