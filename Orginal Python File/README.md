# Orginal Python File

এই ফোল্ডারে Python-এর কিছু শেখার/পরীক্ষামূলক প্রোগ্রাম আছে—ক্যালকুলেটর, DNS lookup, UDP server ও client, multiprocessing উদাহরণ এবং PostgreSQL সংযোগ। UDP-সংক্রান্ত কিছু ফাইল নিজের কম্পিউটার বা অনুমতিপ্রাপ্ত পরীক্ষার পরিবেশে চালানোর জন্য; অন্যের সার্ভার বা নেটওয়ার্কে পরীক্ষা করবেন না।

## ফাইলগুলোর কাজ

| ফাইল | কী করে |
|---|---|
| `Calculator.py` | টার্মিনালে যোগ, বিয়োগ, গুণ, ভাগ, ভাগশেষ ও ঘাতের হিসাব করে; চলতি সেশনের হিসাবের ইতিহাস দেখায়। |
| `dns_lookup.py` | `dnspython` ব্যবহার করে ডোমেইনের DNS রেকর্ড (যেমন A, AAAA, MX, NS, TXT) দেখে; PTR reverse lookup-ও সমর্থন করে। |
| `client.py` | HTTP-ভিত্তিক টার্মিনাল chat client: সার্ভার থেকে বার্তা নেয় এবং ব্যবহারকারীর বার্তা পাঠায়। `requests` প্যাকেজ লাগে। |
| `database.py` | UDP সার্ভারের জন্য asynchronous PostgreSQL connection pool তৈরি করে এবং UDP packet-এর তথ্য সংরক্ষণের সহায়তা দেয়। |
| `High-performance asyncio udp v1.0` | asyncio-ভিত্তিক UDP server উদাহরণ; queue ও worker দিয়ে datagram প্রক্রিয়া, পরিসংখ্যান এবং PostgreSQL সংযোগের কাঠামো দেখায়। |
| `asyncio_udp_v2.0_optimized` | asyncio UDP server-এর batch/thread pool-ভিত্তিক পরীক্ষামূলক সংস্করণ; queue, পরিসংখ্যান ও shutdown পরিচালনা করে। |
| `Multiprocess Engine v2.0` | multiprocessing queue ও worker process ব্যবহার করে UDP datagram প্রক্রিয়াকরণের উদাহরণ। |
| `server_async_mp.py` | asyncio-তে UDP datagram গ্রহণ করে multiprocessing worker-এ পাঠায়; worker উত্তর পাঠায়। |
| `multiprocessing supervisor + worker pool.py` | worker process পরিচালনা, task queue, heartbeat, worker restart এবং graceful shutdown-এর reusable উদাহরণ। |
| `asyncio request sender v1.0` | asyncio দিয়ে UDP datagram পাঠানোর পরীক্ষামূলক client; কেবল নিজের বা স্পষ্ট অনুমতিপ্রাপ্ত test server-এ ব্যবহার করুন। |
| `Multiprocess Request Sender v2.0` | multiprocessing ও thread দিয়ে UDP traffic তৈরি করে নিজের server-এর নিয়ন্ত্রিত load/performance test করার script। অন্য কোনো target-এ চালাবেন না। |
| `Docker-compose.yml` | Docker image/container চালানোর configuration-এর খসড়া। এতে `7.py`-এর উল্লেখ আছে, যা এই তালিকায় নেই; চালানোর আগে configuration মিলিয়ে নিন। |
| `requirements.txt` | PostgreSQL driver/pool এবং Windows ছাড়া `uvloop`-এর dependency তালিকা। সব script-এর dependency এতে অন্তর্ভুক্ত নাও থাকতে পারে। |

## `Server/` সাবফোল্ডার

| ফাইল | কী করে |
|---|---|
| `Server/udp server.py` | asyncio UDP server; worker-ներով packet process করে, PostgreSQL-এ batch-ээр সংরক্ষণ করে এবং ঐচ্ছিক reply সমর্থন করে। |
| `Server/database.py` | `asyncpg` দিয়ে PostgreSQL connection pool, `packets` table এবং batch insert পরিচালনা করে। |
| `Server/sender.py` | localhost-এর UDP port `9999`-এ test datagram পাঠানোর ছোট উদাহরণ। কেবল নিজের স্থানীয় test server-এ ব্যবহার করুন। |
| `Server/Redme .md` | Server চালানো ও PostgreSQL নিয়ে আগের নোট। এটি পুরোনো/অসম্পূর্ণ হতে পারে; বর্তমান code ও dependency আগে যাচাই করুন। |

## চালানোর আগে

- Python 3 ব্যবহার করুন।
- `dns_lookup.py` চালাতে `dnspython` এবং `client.py` চালাতে `requests` ইনস্টল করতে হবে।
- PostgreSQL-নির্ভর server-এর জন্য PostgreSQL চালু ও সঠিক connection URL প্রয়োজন; dependency-র জন্য `requirements.txt` দেখুন। `Server/`-এর code `asyncpg` ব্যবহার করে, যা ওই `requirements.txt`-এ নেই।
- সব script একই dependency চায় না; সংশ্লিষ্ট ফাইলের import ও argument দেখে প্রয়োজনীয় package যাচাই করুন।
- UDP server-এ `0.0.0.0` bind করলে তা একাধিক network interface-এ শুনতে পারে। শেখা/পরীক্ষার সময় localhost বা বিচ্ছিন্ন test environment ব্যবহার করুন এবং অননুমোদিত traffic তৈরি করবেন না।

## নিরাপদ ব্যবহার

এগুলো শিক্ষামূলক ও পরীক্ষামূলক উদাহরণ। UDP sender/load-test script কেবল নিজের নিয়ন্ত্রণাধীন বা লিখিত অনুমতি থাকা server-এ, সীমিত ও নিয়ন্ত্রিত পরীক্ষায় ব্যবহার করুন। কোনো public service বা তৃতীয় পক্ষের network-এ traffic পাঠাবেন না।
