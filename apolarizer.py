from autopolarizer import AutoPolarizer

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("degree", type=int, help="polarizer angle [deg]")
    parser.add_argument("-p", "--port", type=str, default="/dev/tty.usbserial-FTRWB1RN", help="srial port name")
    parser.add_argument("-r", "--reset", action="store_true", help="determines whether to perform a reset")
    args = parser.parse_args()
    
    #command line arguments
    port = args.port
    deg = args.degree
    is_reset = args.reset

    #connect to the polarizer
    polarizer = AutoPolarizer(port=port)
    
    #set speed as default
    polarizer.set_speed()
    
    #reset (if required)
    if is_reset:
        polarizer.reset()
    
    #rotate the polarizer
    polarizer.degree = deg
    
    #explicit disconnect request
    del polarizer
    
if __name__=="__main__":
    main()
