# bash request-script.sh
# param:
#-c, --concurrent=NUM      CONCURRENT users, default is 10
#-r, --reps=NUM            REPS, number of times to run the test.
TIMES=10
for i in $(eval echo "{1..$TIMES}")
do
    siege -c 10 -r 1 http://192.168.49.2:31000/
    siege -c 30 -r 5 http://192.168.49.2:31000/getBookByAuthor
    siege -c 20 -r 10 http://192.168.49.2:31000/getBooksByCategory/5
    siege -c 50 -r 3 http://192.168.49.2:31000/getBooksByCategory/1
    siege -c 20 -r 10 http://192.168.49.2:31000/getBookByAuthor/p
    siege -c 20 -r 3 http://192.168.49.2:31000/getBooksByAuthor/h
    siege -c 15 -r 5 http://192.168.49.2:31000/getBooksByTitle/h
    siege -c 10 -r 2 http://192.168.49.2:31000/getAllBooks
    siege -c 100 -r 1 http://192.168.49.2:31000/getAllBooks
    sleep 5
done
