import sys
import cctrack as ct
import ccdb as cdb

intervals = [2,4,6,8]

# result_fname = "sample_maxd.txt"
result_fname = "sample_avgd.txt"

tids = [28,69,96,97,451,464,476,477,479,481,483,501,505,548,550,658,662,691,724,727,735,768,891,940]

def main():
    trd = cdb.new_track_reader(offset = 0)

    with open(result_fname, 'w') as f:
        f.write(','.join(['tid'] + [str(x) for x in intervals]))
        f.write('\n')
        for tid in tids:
            print tid
            xs = [str(tid)]
            for interval in intervals:
                track = trd.fetch_by_id(tid)
                track.sample(interval)
                # xs.append(str(track.max_d()))
                xs.append(str(track.length()/len(track.rds)))
            f.write(','.join(xs))
            f.write('\n')

if __name__ == "__main__":
    main() 
