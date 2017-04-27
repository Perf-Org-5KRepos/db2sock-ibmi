#------IMPORTANT WARNING -------
This project is under construction. APIs are changing daily, therefore, you should not use for ANY production purpose. 
When this warning disappears, APIs will be considered stable.


#Notes
Clarification to avoid conspiracy theory.

To be clear, **new libdb400.a synchronous driver CLI APIs are the same (today APIs).**
That is, new libdb400.a under most PASE languages will run exactly same code path. In fact, at present new libdb400.a 
will run 'original APIs' by calling old driver (/QOpenSys/QIBM/ProdData/OS400/PASE/lib/libdb400.a).
You really should be able to slip this driver under your current PASE favorite script language and keep running (i am).

Specifically 'new' changes to old driver, **original UTF-8 (1208) and new UTF-16 (1200 - wide) APIs take 
alternate short path directly call ILE API database (no PASE iconv).** 
Current technical theory is all UTF-8/16 DB2 CLI APIs should work without old PASE libdb400.a iconv 'assistance'.
In unlikely event UTF-8/16 fast path proves untrue (not work), 
some new CLI APIs may return back to PASE iconv like current libdb400.a (old driver). 

All asynchronous APIs with suffix **'Async/Thread'** are new. 
Also, all aggregate APIs with prefix **'SQL400'** are new (mutiple call task APIs).  

**Current node.js issues are old driver.** The current async DB2 interfaces for Node.js on 
IBM i do NOT use this new driver. Specifically, any current issues or performance problems with 
node db2a having NOTHING to do with this new project (see future). 

**The goal is new APIs for any language.** To be clear, 'async' APIs are NOT just for 'async' Node.js, 
but can instead be applied to all PASE langs (PHP, Ruby, Python, etc).
Some languages will use 'async' poll/reap (php), others use async 'callback' (nodejs).

**Most of this code is generated by python gen.py.** This is not frivolous programmer play time. 
Script generation allows for very rapid enhancement or change of underlying technology. 
All but ends programmer finger checks present in repeated monotony of code duplication (bored programmer asleep at desk). 
The basic calls through CLI are trivial (as intended), therefore very well suited to script generation. 
Due simple CLI interfaces we can add extended calls like 'Async' with high level of confidence in quality. 
Basically, have a thought, day later have a new API.

**The driver has thread mutex locking at the connection level for most CLI APIs.** 
DB2 is not completely thread safe. Simply stated, client PASE language side, do not share DB2 resources 
across threads (connections/statements). To this end, new libdb400.a driver uses a connection/thread-mutex. 
This means only one operation/statement will be running against a given QSQSRVR job at a time. Also, 
any single connection will not be used across multiple threads at the same time 
(mutex at connection level). However, any given client may have many threads each with a connection, 
running many QSQSRVR jobs executing same relative time profile indifferent.
(If you have difficulty understanding threads and mutexes, ignore, mutex will only confuse you. 
New libdb400.a just works fast enough 'async'.).

**On demand dynamic symbol resolution** is used for both up calls to ILE DB2 and old calls to PASE libdb400.a. 
A good thing! This will work fine without performance impact, because only APIs 'used' will be 'resolved' on first touch API. 
To wit, consider 98% of PASE applications are running as demons (php, node, ruby, etc.), and, use task repeatable CLI APIs 
(aka, connect, prepare/execute or query, fetch, related APIs), wherein, technically, repeatable tasks will 
'dynamic resolve' to ILE/PASE API 'first touch API' and re-use forever subsequent calls to API (once and done).  

**Open Source libdb400.a driver** does not mean poor quality. In fact, experts (me) are working on the new driver. 
This project is open because we want complete transparency on how your PASE new scripting language DB2 driver works. 
No more mystery, look at the source (and help). When available for production (notice removed top project), 
we will try to be very careful not to damage anything currently running. However, new people can have new ideas, 
so the new exotic 'non-architecture' APIs like 'Async' or 'SQL400' may change over time. 
Also, any new driver may introduce some behavior issues. If you have a recommendation, problem, so on, 
please feel free to use issues on git project (click 'Issues' left panel).

