from spika import driven
import time

if __name__ == '__main__':

    #
    # - spawn the 'snippet' go executable (make sure you built it first)
    # - it supports 2 commands: "uptime" and "shutdown"
    #
    with driven('snippet') as p:

        for _ in range(10):
            
            #
            # - use the "uptime" command which replies with a small json
            #   payload
            #
            reply = p.ask('uptime')
            print reply['ms']
            time.sleep(0.1)

        #
        # - gracefully request the subprocess to go down via the "shutdown"
        #   command (which will effectively exit(0) the go code)
        #
        p.ask('shutdown')