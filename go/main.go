package main

import (
	"fmt"
	"github.com/dwash/py-cymbal/pycymbal"
)

func main() {
	c := pycymbal.NewCymbal()
	fmt.Println("Cymbal wrapper created successfully")
	fmt.Printf("DB Path: %s\n", c.GetDBPath())
}
