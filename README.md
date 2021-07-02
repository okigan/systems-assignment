# Key-Value Server

Your job is to build a simple [key-value server](https://en.wikipedia.org/wiki/Key%E2%80%93value_database) for immutable data. 

To make the task easier, the server only serves read-only data that is provided in a separate file. The data doesn't need to be mutated in any way by the server. Clients need to be able to contact the server over network (you can choose the protocol), send a query containing a key, and the server will answer with the corresponding value from the dataset, if the given key exists.

The key-value data is provided in the following format:
```
3479d894-3271-4935-88cf-a06f3cbb80a5 this is a value
f8a24bb8-eff8-41dc-929b-10b4c3e49e05 1234
0cdfafb5-edb4-48a6-a7ec-5b1a75831f91 here is another value
```
The first column contains the key which is always a valid [UUID (version 4)](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)). A single space chacterter separates the key from the value that is the rest of the line until a newline (\n) character. You can use an example data file stored in this repository, `example.data`, for testing.

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
