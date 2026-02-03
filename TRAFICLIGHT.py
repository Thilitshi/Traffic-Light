from gpiozero import LED 
import time 
import tkinter as tk 
from threading import Thread 
import socket 
 
# LED setup 
red = LED(16) 
yellow = LED(18) 
green = LED(17) 
 
# TCP Server setup 
HOST = '0.0.0.0'  # Listen on all network interfaces 
PORT = 65432      # Port to listen on 
 
# Global flag for pedestrian request 
pedestrian_request = False 
 
def handle_client(conn, addr): 
    global pedestrian_request 
    print(f"Connected by {addr}") 
    try: 
        while True:
             data = conn.recv(1024) 
            if not data: 
                break 
            if data.decode().strip().lower() == 'pedestrian': 
                pedestrian_request = True 
                print("Pedestrian request received via TCP") 
    finally: 
        conn.close() 
 
def start_tcp_server(): 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
        s.bind((HOST, PORT)) 
        s.listen() 
        print(f"TCP server listening on {HOST}:{PORT}") 
        while True: 
            conn, addr = s.accept() 
            Thread(target=handle_client, args=(conn, addr)).start() 
 
def pedestrian_callback(): 
    global pedestrian_request 
    pedestrian_request = True 
    print("Pedestrian button pressed") 
 
def traffic_light_loop(): 
    global pedestrian_request 
    while True: 
 # Normal operation sequence 
        if not pedestrian_request: 
            red.on() 
            time.sleep(5) 
            red.off() 
             
            green.on() 
            time.sleep(5) 
            green.off() 
             
            yellow.on() 
            time.sleep(2) 
            yellow.off() 
        else: 
            # Handle pedestrian request 
            print("Pedestrian crossing activated") 
             
            # If green or yellow is on, transition to red 
            if green.is_lit or yellow.is_lit: 
                green.off() 
                yellow.on() 
                time.sleep(2) 
                yellow.off() 
          
            red.on() 
            time.sleep(7)  # Longer red light for pedestrian crossing  red.off() 
             
            pedestrian_request = False 
            print("Resuming normal operation") 
 
# Create GUI 
root = tk.Tk() 
root.title("Traffic Light Controller") 
 
pedestrian_button = tk.Button(root, text="Pedestrian Crossing",     
command=pedestrian_callback, height=3, width=20) 
pedestrian_button.pack(padx=20, pady=20) 
 
# Start TCP server in a separate thread 
tcp_thread = Thread(target=start_tcp_server) 
tcp_thread.daemon = True 
tcp_thread.start() 
 
# Start traffic light loop in a separate thread 
traffic_thread = Thread(target=traffic_light_loop) 
traffic_thread.daemon = True 
traffic_thread.start() 
 
 
# Start GUI main loop 
root.mainloop()