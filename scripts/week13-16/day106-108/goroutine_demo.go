package main

import (
    "fmt"
    "time"
)

func say(id int) {
    fmt.Printf("worker %d\n", id)
    time.Sleep(100 * time.Millisecond)
}

func main() {
    for i := 1; i <= 5; i++ {
        go say(i) // 前面加 go = 并发开跑
    }
    time.Sleep(time.Second) // 主程序不能立刻退出，否则 goroutine 来不及打印
}