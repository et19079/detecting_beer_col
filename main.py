import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
from StateMachine import StateMachine
import time
import Identifier
from picamera import PiCamera
from RpiMotorLib import RpiMotorLib

# Setup LCD
lcd = CharLCD('PCF8574', 0x27)

# Setup Motor (Pin 21 -> not connected, Ganzschrittbetrieb (hardcoded))
motor = RpiMotorLib.A4988Nema(23, 24, (-1,-1,-1), "DRV8825") 

# Setup GPIO 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)  #reley 
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# Setup camera
camera = PiCamera()

# Erste Displayausgabe
lcd.clear()
lcd.write_string('Getraenkeautomat ES')
lcd.cursor_pos =(2,0)
lcd.write_string('Bereit zum scannen')


# Zustand 1
def idle():
    
    # Uebergangsbedingung
    if GPIO.input(4) == GPIO.HIGH:    # Tasterabfrage
        
        # Displayausgabe
        lcd.clear()
        lcd.write_string('Getraenkeautomat ES')
        lcd.cursor_pos =(2,0)
        lcd.write_string('Foto aufnehmen')
        
        # Motorbewegung
        motor.motor_go(False, "Full", 33, .0005, False, .05)
        
        # Nexter Zustand
        newState = "take_pic"
    
    # Keine Zustandsaenderung
    else:
        newState = "idle"
    return (newState)

# Zustand 2
def take_pic():
    
    # Reley anschalten
    GPIO.output(18,GPIO.HIGH)
    
    # Foto aufnehmen
    camera.capture('Bier.jpg')
    
    # warten
    time.sleep (1)
    
    # Reley ausschalten
    GPIO.output(18,GPIO.LOW)
    
    # Motor bewegen
    motor.motor_go(False, "Full", 33, .0005, False, .05) 
    
    # Display Ausgabe
    lcd.clear()
    lcd.write_string('Getraenkeautomat ES')
    lcd.cursor_pos =(2,0)
    lcd.write_string('Flasche scannen')
    
    # nachsten Zustand setzen
    newState = "identify"
    return (newState)

# Zustand 3
def identify():
    
    # Ettiket identifizieren
    beer = Identifier.identify()
    
    # Motor bewegen
    if (beer == "Augustiner"):
        motor.motor_go(False, "Full", 44, .0005, False, .05)
    if (beer == "Tegernseer"):
        motor.motor_go(False, "Full", 110, .0005, False, .05)
    
    # Display Ausgabe
    lcd.clear()
    lcd.write_string('Getraenkeautomat ES')  
    lcd.cursor_pos =(2,0)
    lcd.write_string(beer)
    
    # warten
    time.sleep(2)
    
    # Motor bewegen
    if (beer == "Augustiner"):
        motor.motor_go(False, "Full", 100, .0005, False, .05)
    if (beer == "Tegernseer"):
        motor.motor_go(False, "Full", 44, .0005, False, .05)
    
    # naechster Zustand
    newState = "show"
    return (newState)

# Zustand 4
def show():
    
    # Uebergangsbedingung
    if GPIO.input(4) == GPIO.HIGH: # Tasterabfrage
            
        # Taster entprellen
        time.sleep (0.5)  
        
        # Displayausgabe
        lcd.clear()
        lcd.write_string('Getraenkeautomat ES')
        lcd.cursor_pos =(2,0)
        lcd.write_string('Bereit zum scannen')
        
        # naechsten zustand setzen
        newState = "idle"
        
    # keine Uebergangsbedingung
    else:
        newState = "show"
    return (newState)

# error Zustand -> wird nie erreicht
def off():
    
    # Displayausgabe (error)
    lcd.clear()
    lcd.write_string('aus')  
    return ("aus","")

# Zustandsautomat initialisieren
stMa = StateMachine()

# Zustände hinzufügen
stMa.add_state("idle", idle)
stMa.add_state("take_pic", take_pic)
stMa.add_state("identify", identify)
stMa.add_state("show", show)
stMa.add_state("off", None, end_state=1)

# Startzustand setzen
stMa.set_start("idle")

# Zustandsmaschine starten
stMa.run()

        
    
    
        