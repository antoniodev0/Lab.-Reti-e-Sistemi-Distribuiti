import threading
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import Generator, PCG64
from time import perf_counter, sleep
import struct
import socket


from csv_writer import write_to_csv  # Importa la funzione per scrivere i dati nel file CSV

#Frequenze 
freq_inziale= 600 # 0.6 kHz
freq_desiderata= 200 # 0.2 kHz

#var Per l'edge server
Host="127.0.0.1" 
port=65435

#Var globali utili per il plot 
lista=[]
setPlot=False
index=0



def main():
    #variabili globali
    global lista
    global setPlot 
    
    i=0

    while  i<=10:
        
        #thread per generare valori
        t1 = threading.Thread(target=generate_and_subsample,args=(freq_inziale, freq_desiderata,))
        t1.start() 
        t1.join()
        
        #thread per scrivere su file csv
        t2 = threading.Thread(target=write_to_csv, args=(lista, "freq.csv",))
        t2.start()
        

        #thread per inviare i dati 
        t3 = threading.Thread(target=send_data, args=(Host,port,lista,))
        t3.start()
        

        #richiamo plot (non è consigliato non usare i thread)
        if(setPlot==False):
            fig, axs = plt.subplots(3, 1, figsize=(8, 12)) #creo finestra con i plot
            setPlot=True #imposto set a True così non verrà più creata alcuna finestra 
        myplot(lista,axs)   #ricniamo funzione per il plot

        i+=1

######################################################################################################################################################

def myplot(lista,axs):

    if lista is None:
        return
    
    #per avere indice condiviso ad ogni esecuzione 
    global index 
    #liste per conetere i dati da plottare 
    indexes=[]
    x_vals=[]
    y_vals=[]
    z_vals=[]


    for element in lista:
        #appendo i punti alla lista corrispondente
        indexes.append(index)
        x_vals.append(element[0])
        y_vals.append(element[1])
        z_vals.append(element[2])
        index+=1

        #faccio i 3 plot 
        axs[0].plot(indexes,x_vals,'b-')
        axs[1].plot(indexes,y_vals,'g-')
        axs[2].plot(indexes,z_vals,'r-')
        axs[0].set_xlabel('X')  # Etichetta per l'asse y del primo grafico
        axs[1].set_xlabel('Y')  # Etichetta per l'asse y del secondo grafico
        axs[2].set_xlabel('Z')  # Etichetta per l'asse y del terzo grafico
        
        #uso plt pause per rallentare la generazione del plt
        if index%10==0:
            plt.pause(0.1) 
        
        #rimuovo i dati precedenti ogni 200 valori
        if index %(freq_desiderata//2)==0:
            x_vals=x_vals[(freq_desiderata//2):]
            y_vals=y_vals[(freq_desiderata//2):]
            z_vals=z_vals[(freq_desiderata//2):]
            indexes=indexes[(freq_desiderata//2):]
            #mi assicuro che alla fine non venga pulito il plot 
            if index %freq_desiderata !=0:
                axs[0].cla()
                axs[1].cla()
                axs[2].cla()
                plt.cla()
    
    #comandi per pulire finestra prima dell'esecuzione successiva    
    plt.pause(0.1)
    axs[0].cla()
    axs[1].cla()
    axs[2].cla()
    plt.cla()

#######################################################################################################################################

def generate_and_subsample(frequenza_campionamento_originale, frequenza_campionamento_desiderata):

    start_time = perf_counter()
    rg = Generator(PCG64()) #classe per generare numeri casuali e pcg64 è l'algoritmo usato
    numero_campioni_originale = int(frequenza_campionamento_originale)

    # Generazione di segnali casuali (600 valori per ogni segnale) compresi tra -5 e 5
    segnale1 = rg.uniform(-5, 5, numero_campioni_originale)
    segnale2 = rg.uniform(-5, 5, numero_campioni_originale)
    segnale3 = rg.uniform(-5, 5, numero_campioni_originale)

    # Determinazione del fattore di downsampling 
    fattore_downsampling = int(frequenza_campionamento_originale / frequenza_campionamento_desiderata)

    
    segnale1 = np.float32(segnale1)
    segnale2 = np.float32(segnale2)
    segnale3 = np.float32(segnale3)

    #mean fa la media degli array prendendo in input l'output di reshape, lungo le colonne (axis=1)
    #reshape trasforma l'array in un array in cui i valori sono raggruppati in sottoarray di 3 elementi(x,y,z)
    segnale1_subsamp = np.mean(segnale1.reshape(-1, fattore_downsampling), axis=1)
    segnale2_subsamp = np.mean(segnale2.reshape(-1, fattore_downsampling), axis=1)
    segnale3_subsamp = np.mean(segnale3.reshape(-1, fattore_downsampling), axis=1)

    

    # Creazione della macrolista sottocampionata mantenendo la struttura di liste
    macrolista_subsamp = []

    for i in range(len(segnale1_subsamp)):
        sottolista = [segnale1_subsamp[i], segnale2_subsamp[i], segnale3_subsamp[i]]
        macrolista_subsamp.append(sottolista)

    end_time = perf_counter()

    generation_time = end_time - start_time

    sleep(1 - generation_time)
    print(macrolista_subsamp)
    
    global lista 
    lista = macrolista_subsamp

################################################################################################################################################################

def send_data(host,port,dati):
    #lista binaria per contenere i dati da inviare 
    binary_data=b""

    #recupero i 3 valori per ogni punto nella lista di dati     
    for f in dati:
        binary_data += struct.pack('f', f[0]) # asse x
        binary_data += struct.pack('f', f[1]) # asse y
        binary_data += struct.pack('f', f[2]) # asse z
    
    #Invio tramite TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(binary_data)
                #s.send(b"")
                s.close()


if __name__ == '__main__':
    main()
