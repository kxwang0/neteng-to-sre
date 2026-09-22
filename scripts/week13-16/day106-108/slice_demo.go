package main

import "fmt"

func main() {
    ips := []string{"192.168.30.252", "192.168.30.253"}
    for i, ip := range ips {
        fmt.Println(i, ip)
    }
    ips = append(ips, "192.168.30.134")
    fmt.Println(ips)
}