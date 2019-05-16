/*
xrit-decrypt.go
https://github.com/sam210723/COMS-1

Decrypts xRIT file into a plain-text xRIT file using single layer DES
*/

package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	args := os.Args[1:]
	key := args[0]
	keyhex, err := strconv.ParseInt(key, 16, 64)
	path := args[1]

	if err != nil {
		fmt.Println("Error parsing key argument")
		os.Exit(1)
	}

	fmt.Println("Key:", key)
	fmt.Println("Path:", path)
	fmt.Sprintf("%X", keyhex)
}
