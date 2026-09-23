package main

import (
    "fmt"
    "net"
    "sync"
    "time"
)

func check(ip string, results chan<- string, wg *sync.WaitGroup) {
    defer wg.Done()
    conn, err := net.DialTimeout("tcp", ip+":22", 500*time.Millisecond)
    if err == nil {
        conn.Close()
        results <- ip
    }
}

func main() {
    var wg sync.WaitGroup
    results := make(chan string, 256)
    for i := 1; i < 255; i++ {
        wg.Add(1)
        go check(fmt.Sprintf("192.168.30.%d", i), results, &wg) // 换成你的网段
    }
    wg.Wait()
    close(results)
    for ip := range results {
        fmt.Println(ip, "SSH 开放")
    }
}