package main

import (
    _ "github.com/lib/pq"
    "database/sql"
    "fmt"
    "bytes"
    "net/http"
    "log"
    "strings"
    "strconv"
    "time"
    "errors"
)

type Reader struct {
    db *sql.DB
    dp *Dispatcher
    tb string
    rs *sql.Rows
    nIn int
    nOut int
    empty bool
}

type Writer struct {
    db *sql.DB
    tb string
    nIn int
    nOut int
    nErr int
}

type Task struct {
    id string
    task string
}

type Result struct {
    id string
    res string
}

type Dispatcher struct {
    queue chan Task
    pends map[string]Task
    readers []*Reader
    nReading int
    writers map[string]*Writer
    nIn int
    nOut int
    bOut float64
}

type Record struct {
    t time.Time
    s int
}

type RecQueue struct {
    q []Record
    sp int
    tp int
}

type Client struct {
    ip string
    name string
    nIn int
    nOut int
    bOut float64
    nErr int
    fIn time.Time
    lOut time.Time
    qRec *RecQueue
}

type Moniter struct {
    clients map[string]*Client
    sTime time.Time
    qRec *RecQueue
}

var dispatcher Dispatcher
var mapData string
var moniter Moniter

func (rq *RecQueue) pushBack(rc Record) {
    rq.tp = (rq.tp + 1) % len(rq.q)
    if rq.tp == rq.sp {
        rq.sp = (rq.sp + 1) % len(rq.q)
    }
    rq.q[rq.tp] = rc
}

func (rq *RecQueue) back() Record {
    return rq.q[rq.tp]
}

func (rq *RecQueue) front() Record {
    return rq.q[rq.sp]
}

func (rq *RecQueue) size() int {
    if rq.sp < rq.tp {
        return rq.tp - rq.sp + 1
    }
    return len(rq.q) - rq.sp + rq.tp + 1
}

func (rq *RecQueue) speed() float64 {
    s := 0
    for _, v := range rq.q {
        s += v.s
    }
    return float64(s) / (rq.q[rq.tp].t.Sub(rq.q[rq.sp].t)).Seconds()
}

func bufMap() {
    db, err := sql.Open("postgres", "user=postgres dbname=beijing_map")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("map database connected")
    rs, err := db.Query("select id, source, target, km, kmh, reverse_cost, x1, y1, x2, y2, st_astext(geom_way) as geom from ways")
    if err != nil {
        log.Fatal(err)
    }
    var (
        id int
        source int
        target int
        km float64
        kmh int
        reverse_cost float64
        x1 float64
        y1 float64
        x2 float64
        y2 float64
        geom string
    )
    var buffer bytes.Buffer
    for rs.Next() {
        rs.Scan(&id, &source, &target, &km, &kmh, &reverse_cost, &x1, &y1, &x2, &y2, &geom)
        buffer.WriteString(fmt.Sprintf("%d, %d, %d, %f, %d, %d, %f, %f, %f, %f, %s\n", id, source, target, km, kmh, int(reverse_cost), x1, y1, x2, y2, geom))
    }
    mapData = buffer.String()
}

func (r *Reader) conn() (*Reader) {
    db, err := sql.Open("postgres", "user=postgres dbname=beijing_taxi_2012")
    if err != nil {
        log.Fatal(err)
    } else {
        fmt.Println(r.tb, "connected")
        r.db = db
    }
    return r
}

func (w *Writer) conn() (*Writer){
    db, err := sql.Open("postgres", "user=postgres dbname=beijing_taxi_2012")
    if err != nil {
        log.Fatal(err)
    } else {
        fmt.Println(w.tb, "connected")
        w.db = db
    }
    return w
}

func (r *Reader) query() {
    date := r.tb[len("taxi_tracks_occupied_cruising_"):]
    wtb := "taxi_paths_occupied_cruising_st_" + date
    rs, err := r.db.Query("select id, cuid_count, st_astext(track_geom), track_desc, oorc from " + r.tb + " where id not in (select tid from " + wtb + ")")
    if err != nil {
        log.Fatal(err)
    } else {
        fmt.Println(r.tb, "query succeed")
        r.rs = rs
    }
}

func (r *Reader) scan() {
    var (
        tid int
        cuid int
        geom string
        desc string
        oorc int
    )
    fmt.Println(r.tb, "scanning")
    r.dp.nReading++
    for r.rs.Next() {
        r.rs.Scan(&tid, &cuid, &geom, &desc, &oorc)
        r.nIn++
        id := r.tb[len("taxi_tracks_occupied_cruising_"):] + "_"  + fmt.Sprintf("%d", tid)
        s := fmt.Sprintf("%d\n%d\n%s\n%s\n%d", tid, cuid, geom, desc, oorc)
        r.dp.push(id, s)
        r.nOut++
    }
    r.empty = true
    r.dp.nReading--
}

func (r *Reader) run() {
    r.conn().query()
    r.scan()
}

func (w *Writer) store(s string) {
    w.nIn++
    if w.db == nil {
        w.conn()
    }
    ss := strings.Split(strings.TrimSpace(s), "\n")
    tid, _ := strconv.Atoi(ss[0])
    var err error
    if ss[1] == "error" {
        _, err = w.db.Exec("insert into " + w.tb + " values ($1);", tid)
        w.nErr++
    } else {
        _, err = w.db.Exec("insert into " + w.tb + " values ($1, $2, $3);", tid, ss[1], ss[2])
    }
    if err != nil {
        log.Fatal(err)
    } else {
        w.nOut++
    }
}

func (dp *Dispatcher) push (id string, s string) {
    dp.queue <- Task{id, s}
    // fmt.Println("push: task", id)
}

func (dp *Dispatcher) pop () (t Task, err error) {
    if dp.nReading <= 0 {
        err = errors.New("no reading")
        return
    }
    t = <-dp.queue
    dp.nIn++
    id := t.id
    dp.pends[id] = t
    // fmt.Println("pop: task", id)
    return
}

func (dp *Dispatcher) done (res Result) {
    dp.nOut++
    dp.bOut += float64(len(res.res))
    id := res.id
    w := dp.writers[id[:8]]
    w.store(res.res)
    delete(dp.pends, id)
    fmt.Println("done: task", id)
}

func (dp *Dispatcher) run(dates []int) {
    tbTrack := "taxi_tracks_occupied_cruising_201211%02d"
    tbPath := "taxi_paths_occupied_cruising_st_201211%02d"
    for i:=0; i<len(dp.readers); i++ {
        fmt.Print("creating reader", dates[i], "... ")
        dp.readers[i] = &Reader{nil, dp, fmt.Sprintf(tbTrack, dates[i]), nil, 0, 0, false}
        fmt.Print("writer", dates[i], "...\n")
        dp.writers[fmt.Sprintf("201211%02d", dates[i])] = &Writer{nil, fmt.Sprintf(tbPath, dates[i]), 0, 0, 0}
        go dp.readers[i].run()
    }
    fmt.Println("ok")
}

func (mn *Moniter) proc(ip string, name string, f string, bOut int) {
    id := ip + "-" + name
    c, ok := mn.clients[id]
    if !ok {
        c = &Client{ip, name, 0, 0, 0.0, 0, time.Now(), time.Now(), &RecQueue{make([]Record, 100, 100), 0, 1}}
        c.qRec.q[0] = Record{time.Now(), 0}
        c.qRec.q[1] = Record{time.Now(), 0}
        mn.clients[id] = c
    }
    now := time.Now()
    switch f {
    case "in":
        c.nIn++
    case "out": {
        c.nOut++
        c.bOut += float64(bOut)
        c.lOut = now
        c.qRec.pushBack(Record{now, bOut})
        mn.qRec.pushBack(Record{now, bOut})
    }
    case "err":
        c.nErr++
    }
}

func readTrack(w http.ResponseWriter, r *http.Request) {
    t, err := dispatcher.pop()
    if err != nil {
        fmt.Fprintf(w, "done")
        return
    }
    r.ParseForm()
    ns, ok := r.Form["name"]
    if !ok {
        ns = []string{""}
    }
    ip := strings.Split(r.RemoteAddr, ":")[0]
    go moniter.proc(ip, ns[0], "in", len(t.task))
    fmt.Fprintf(w, fmt.Sprintf("%s\n%s", t.id, t.task))
}

func writePath(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    ns, ok := r.Form["name"]
    if !ok {
        ns = []string{""}
    }
    ip := strings.Split(r.RemoteAddr, ":")[0]
    go moniter.proc(ip, ns[0], "out", len(r.Form["res"][0]))
    go dispatcher.done(Result{r.Form["id"][0], r.Form["res"][0]})

    t, err := dispatcher.pop()
    if err != nil {
        fmt.Fprintf(w, "done")
        return
    }
    go moniter.proc(ip, ns[0], "in", len(t.task))
    fmt.Fprintf(w, fmt.Sprintf("%s\n%s", t.id, t.task))
}

func readMap(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, mapData)
}

func stat(w http.ResponseWriter, r *http.Request) {
    d := time.Since(moniter.sTime)
    fmt.Fprintf(w, "\nServer:\n\n")
    fmt.Fprintf(w, fmt.Sprintf("Start Time: %s\nDuration: %s\nAvg Speed: %.3f task/sec, %.3f KB/sec\nSpeed: %.3f task/sec, %.3f KB/sec\n",
                                moniter.sTime.Format("2006-01-02 15:04:05"), d.String(),
                                float64(dispatcher.nOut) / d.Seconds(), dispatcher.bOut / d.Seconds() / 1000.0,
                                float64(moniter.qRec.size()) / (moniter.qRec.back().t.Sub(moniter.qRec.front().t)).Seconds(),
                                moniter.qRec.speed() / 1000.0))
    fmt.Fprintf(w, "\nReader Stat:\n\n")
    for _, v := range dispatcher.readers {
        fmt.Fprintf(w, fmt.Sprintf("table: %s, in: %9d, out: %9d", v.tb, v.nIn, v.nOut))
        if v.empty {
            fmt.Fprintf(w, ", done")
        }
        fmt.Fprintf(w, "\n")
    }

    fmt.Fprintf(w, "\nDispatcher Stat:\n\n")
    fmt.Fprintf(w, fmt.Sprintf("in: %9d, out: %9d, pending: %9d\n", dispatcher.nIn, dispatcher.nOut, len(dispatcher.pends)))

    fmt.Fprintf(w, "\nWriter Stat:\n\n")
    for _, v := range dispatcher.writers {
        fmt.Fprintf(w, fmt.Sprintf("table: %s, in: %9d, out: %9d, err: %9d\n", v.tb, v.nIn, v.nOut, v.nErr))
    }

    fmt.Fprintf(w, "\nClient Stat:\n\n")
    for _, v := range moniter.clients {
        d = v.qRec.back().t.Sub(v.qRec.front().t)
        fmt.Fprintf(w, fmt.Sprintf("%s, %s, in: %9d, out: %9d, err: %9d\nFirst Req: %s, Last Rep: %s",
                                    v.ip, v.name, v.nIn, v.nOut, v.nErr,
                                    v.fIn.Format("2006-01-02 15:04:05"), v.lOut.Format("2006-01-02 15:04:05")))
        if time.Since(v.lOut).Seconds() < 10*60 {
            fmt.Fprintf(w, ", online")
        }
        fmt.Fprintf(w, fmt.Sprintf("\nAvg Speed: %.3f task/sec, Speed: %.3f task/sec, %.3f KB/sec\n\n\n",
                                    float64(v.nOut) / (v.lOut.Sub(v.fIn)).Seconds(),
                                    float64(v.qRec.size()) / d.Seconds(),
                                    v.qRec.speed() / 1000.0))
    }
}

func printPends(w http.ResponseWriter, r *http.Request) {
    for k, _ := range dispatcher.pends {
        fmt.Fprintf(w, fmt.Sprintf("%s\n", k))
    }
}

func main() {
    fmt.Println("starting ...")

    bufMap()

    dates := []int{1,2,3,4,5}

    dispatcher = Dispatcher{make(chan Task, 100), make(map[string]Task), make([]*Reader, len(dates), len(dates)), 0, make(map[string]*Writer), 0, 0, 0.0}
    dispatcher.run(dates)

    moniter = Moniter{make(map[string]*Client), time.Now(), &RecQueue{make([]Record, 100, 100), 0, 1}}
    moniter.qRec.q[0] = Record{time.Now(), 0}
    moniter.qRec.q[1] = Record{time.Now(), 0}

    http.HandleFunc("/map", readMap)
    http.HandleFunc("/read", readTrack)
    http.HandleFunc("/write", writePath)
    http.HandleFunc("/pends", printPends)
    http.HandleFunc("/stat", stat)

    err := http.ListenAndServe(":9090", nil)
    if err != nil {
        log.Fatal("ListenAndServe: ", err)
    }
}

