# Assignment notes

## Notes:
* not much know about the call pattern from the client(s), assuming mostly random access and that clients use correct keys
* setup with basic Python environment and tooling (just pyenv, no poetry, no docker, no k8s, or other fancy stuff) everything invoked from Makefile

## class KVServiceBisect:
    Assumptions: 
    - we want very low memory footprint, after index construction
    - we want a fast restart
    - we can use more than 1 cpu(s)
    Behavior: 
    - very low memory footprint
    - working set independent of the size of the data in the data file (tested with 100M)
    - minimal working set also independent of the number of time items the data file
    - index can be re-used by multiple processes
    - uses single core, an additional process(es) can be started
    Limitations:
    - currently configured to handle ~1TB (~200M kv items) of data file, easily extended to more with a slight increase of index file


## class KVServiceDict:
    Assumptions: 
    - we want fast lookup, ok to use more memory
    - ok to take time on startup
    Behavior: 
    - very fast lookup
    - takes time to start
    - memory footprint independent of the size of the data in the data file (tested with 100M)
    - memory footprint depends on number of items in the data file (tested with 100M ~ 15 GB)
    - index is not shared between processes
    - uses single core, additional processes can be started, mind the memory footprint

## class KVServiceMock:
    Mock implementation for performance baseline testing

## Usage:
- program support command line help, see Makefile for example usage
- program performs mini benchmark on startup (excluding http/fastapi overhead)
- API documentation is available at http://localhost:5000/docs

### to start bisect based server:
```make run-bisect```

with 10M entries on a single core of 

    model name      : Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz
    bogomips        : 5187.54

    KVServiceBisect index built: 10,000,000 entries in 0.00014066696166992188s
    Test pass execution time: 9.677794218063354 s
    Average time per query: 9.677697441088944e-05s
    RPS: 10,332.93307821658

### to start dictionary based server:
```make run-dict```

with 10M entries on a single core of 

    model name      : Intel(R) Core(TM) i7-5600U CPU @ 2.60GHz
    bogomips        : 5187.54

    KVServiceDict index built: 10,000,000 entries in 41.469183921813965s
    Test pass execution time: 0.4095578193664551 s
    Average time per query: 4.095537238292168e-06s
    RPS: 244,165.76920614036 (RAM usage ~ 1.2GB)


### Client
- there is no separate client implementation, use :
    * curl or browser to test the service
    * use the swagger UI at: http://localhost:5000/docs
    * stress test with httperf/ab/siege: `make run-http-bench`

### Http performance testing
Even with mock implementation, the RPS maxes out at ~ 1700 RPS which is a bottleneck for either of the above implementations, I assume that is caused by the client re-createing connection for each request. I've tried some options for keep-alive, but did not investigate further.

# Key-Value Server

Your job is to build a simple [key-value server](https://en.wikipedia.org/wiki/Key%E2%80%93value_database) for immutable data. 

To make the task easier, the server only serves read-only data that is provided in a separate file. The data doesn't need to be mutated in any way by the server. Clients need to be able to contact the server over network (you can choose the protocol), send a query containing a key, and the server will answer with the corresponding value from the dataset, if the given key exists.

The key-value data is provided in the following format:
```
3479d894-3271-4935-88cf-a06f3cbb80a5 this is a value
f8a24bb8-eff8-41dc-929b-10b4c3e49e05 1234
0cdfafb5-edb4-48a6-a7ec-5b1a75831f91 here is another value
```
The first column contains the key which is always a valid [UUID (version 4)](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)). A single space character separates the key from the value that is the rest of the line until a newline (\n) character. You can use an example data file stored in this repository, `example.data`, for testing.

You are free to use any common programming language for your implementation. You can choose to use either HTTP or TCP for communication with the server. You can decide the details of the protocol. Your server should accept a single command line argument during startup that defines a path to the data file.

In addition to implementing the server, provide an example how a client can request data from the server. The client will provide only a key, e.g. `f8a24bb8-eff8-41dc-929b-10b4c3e49e05`, and the server needs to provide the corresponding value in the response, in this case, `1234`.

You can implement the server and the example client as you see fit. Your implementation should be able to handle files that contain up to a million key-value pairs.

**Important**: You should be able to explain how your system works in detail and answer follow up questions like these:

- How much data can your server handle? How could you improve it so it can handle even larger datasets?
- How many milliseconds it takes for the client to get a response on average? How could you improve the latency?
- What are some failure patterns that you can anticipate?

While you are allowed to use external libraries as a part of your solution, you should be prepared to explain in detail how these libraries work internally. If you are unsure about their internals, it is better to avoid using them and go with a simpler, more understandable approach instead.

The point of this exercise is not so much the code itself. Please don't spend more than 1-2 hours solving this problem. If you have ideas about how to improve your solution if more time was available, save them for the follow-up discussion about possible improvements and their relative pros and cons. For this reason, the question is deliberately open-ended - there is not a single right answer or any tricks or gotchas. 

You can use any language to provide a solution. It is ok to implement your solution in a high-level language such as Python. We evaluate speed and scalability in terms of data structures and algorithms you chose rather than overhead caused by the language. 

You can share your solution (which can be just one file or more, if needed) either as a private repo or as an email attachment at [workwithus@outerbounds.co](mailto:workwithus@outerbounds.co). Naturally feel free to [ask me](mailto:savin@outerbounds.co) if anything seems unclear!
