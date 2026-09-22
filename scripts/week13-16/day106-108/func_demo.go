package main

import (
    "fmt"
    "strconv"
)

func double(a int) int { return a * 2 }

func main() {
    fmt.Println(double(3))
    _, err := strconv.Atoi("abc")
    if err != nil {
        fmt.Println("出错:", err)
        return
    }
}