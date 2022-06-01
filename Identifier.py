import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie1976

# Referenzwert 1 (experimentell bestimmt)
Augustiner =   [[17.60841487, 84.28164275, 92.52894543],
                [ 3.78979366, 11.00008188, 4.14795709],
                [131.06409697,183.85235894,152.61541816],
                [ 78.4176127, 124.68525662,104.16051288],
                [28.56552742, 64.81091714, 29.78009999]]

# Referenzwert 2 (experimentell bestimmt)
Tegernseer =   [[73.67849283, 122.95838613, 113.81343781],
                [1.32453403, 9.77317357, 4.79412132],
                [16.64936551 ,56.41660776, 50.3517116 ],
                [107.44201984 ,159.5981064 , 145.61316501],
                [40.18330711 ,93.01901153, 87.48357365]]

# Funktion zum Bestimmen eines Wertes der die Differenz von zwei Bildern in einer Zahl ausdruekt
def findColor (color, temp):
    
    # für alle Vergleichswerte (5 Farben) den Farbraum aendern
    color1 = LabColor(temp[0][0],temp[0][1],temp[0][2])
    color2 = LabColor(temp[1][0],temp[1][1],temp[1][2])
    color3 = LabColor(temp[2][0],temp[2][1],temp[2][2])
    color4 = LabColor(temp[3][0],temp[3][1],temp[3][2])
    color5 = LabColor(temp[4][0],temp[4][1],temp[4][2])
    
    # Variablen anlegen
    j = 0
    x = np.array([0,0,0,0,0])
    
    # fuer alle Farben (5) vergleiche anstellen
    for i in color:
        # Farbraum ändern
        referenc = LabColor(i[0],i[1],i[2]) 
        
        # Differenz als Zahlenwert bestimmen
        delta_1 = delta_e_cie1976(color1, referenc)
        delta_2 = delta_e_cie1976(color2, referenc)
        delta_3 = delta_e_cie1976(color3, referenc)
        delta_4 = delta_e_cie1976(color4, referenc)
        delta_5 = delta_e_cie1976(color5, referenc)
        
        # geringsten Wert im Array speichern
        x [j]= min (delta_1, delta_2, delta_3, delta_4, delta_5)
        j = j+1
    
    # Durchschnittswert errechnen
    avg = sum(x)/len(x)
    
    # Ruekgabe des Durchschnittwertes
    return avg

# Funktion zum Vergleichen von einem Bild mit Referenzwerten
def identify ():

    # Einlesen
    img = cv.imread("Bier.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    #Groesse aendern
    img = cv.resize(img, (500, 300), interpolation = cv.INTER_AREA)
    
    #Clustern
    clt = KMeans(n_clusters=5)

    # Groesse des Arrays aendern
    clt_1 = clt.fit(img.reshape(-1, 3))
    
    # Gefundene Farben darstellen (optional)
    # show_img_compar(img, palette_perc(clt_1))

    # Array anlegen
    x = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])

    # Array mit Werten füllen
    for idx, centers in enumerate(clt_1.cluster_centers_): 
        x[idx] = centers
    
    # Vergleich welcher Zahlenwert größer ist -> Erkennung
    if (findColor(x,Augustiner) < findColor(x,Tegernseer)):
        return('Augustiner')
    else:
        return('Tegernseer')