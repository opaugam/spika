package main

import (
	"bufio"
	"encoding/json"
	"time"
	"os"
)

type Payload map[string]interface{}

type command struct {
	Tag int64 `json:"tag"`
	Cmd string  `json:"cmd"`
	Ext Payload `json:"ext"`
}

func pipe(supported map[string]func(Payload) Payload) {
	scanner := bufio.NewScanner(os.Stdin)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		in := command{}
		if err := json.Unmarshal([]byte(scanner.Text()), &in); err == nil {
			if f, ok := supported[in.Cmd]; ok {
				go func(f func(Payload) Payload, cmd command) {
					if out := f(cmd.Ext); out == nil {
						cmd.Ext = Payload{}
					} else {
						cmd.Ext = out
					}
					encoder.Encode(cmd)
				}(f, in)
			}
		}
	}
	if err := scanner.Err(); err != nil {
		panic("unable to read from stdin")
	}
}

func EnableCommands(supported map[string]func(Payload) Payload) {
	go pipe(supported)
}

func main() {
	started := time.Now()
	done := make(chan bool, 1)
	supported := map[string]func(Payload) Payload {

		"uptime": func(in Payload) Payload {
			lapse := time.Now().Sub(started)
			return Payload{"ms": 1000 * lapse.Seconds()}
		},

		"shutdown": func(in Payload) Payload {
			done <- true
			return nil
		},
	}
	EnableCommands(supported)
	<-done
	os.Exit(0)
}