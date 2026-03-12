package main

import (
	"bufio"
	"net"
	"os"
	"strings"
	"time"

	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		panic("Error loading .env file")
	}

	flag := os.Getenv("FLAG")
	if flag == "" {
		panic("FLAG not set")
	}
	Flag := strings.TrimSpace(flag)

	password := os.Getenv("PASSWORD")
	if password == "" {
		panic("PASSWORD not set")
	}
	Password := strings.TrimSpace(password)

	ln, err := net.Listen("tcp", ":9001")
	if err != nil {
		panic(err)
	}
	defer ln.Close()

	for {
		conn, err := ln.Accept()
		if err != nil {
			continue
		}
		go handleconn(conn, Flag, Password)
	}
}

func check(input, password string) bool {
	for i := 0; i < len(password); i++ {
		if i >= len(input) {
			return false
		}
		if input[i] != password[i] {
			return false
		}
		time.Sleep(1000 * time.Millisecond)
	}
	return len(input) == len(password)
}

func handleconn(conn net.Conn, Flag string, Password string) {
	const maxInputLen = 40
	defer conn.Close()

	conn.SetDeadline(time.Now().Add(15 * time.Minute))

	reader := bufio.NewReader(conn)

	conn.Write([]byte("Welcome to the password checker!\n"))

	for {
		conn.Write([]byte("Please enter the password: "))

		inputBytes, err := reader.ReadBytes('\n')
		if err != nil {
			return
		}

		input := strings.TrimSpace(string(inputBytes))

		if len(input) > maxInputLen {
			conn.Write([]byte("Input too long. Maximum 40 characters allowed.\n"))
			continue
		}

		if check(input, Password) {
			conn.Write([]byte("Correct! " + Flag + "\n"))
			return
		} else {
			conn.Write([]byte("Incorrect password.\n"))
		}
	}
}
