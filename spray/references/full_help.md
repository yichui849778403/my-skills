# spray — Full Help & Built-in Resources Reference

## Tool Location

```
C:\HACK\1漏洞扫描工具\spray\spray_windows_amd64.exe
```

Project: ChainReactors / Wiki: https://chainreactors.github.io/wiki/spray

## Full CLI Help

```
Usage:
  spray_windows_amd64.exe   WIKI: https://chainreactors.github.io/wiki/spray

  QUICKSTART:
    basic:  spray -u http://example.com
    cidr and port:  spray -i example -p top2,top3
    simple brute:
      spray -u http://example.com -d wordlist1.txt -d wordlist2.txt
    mask-base brute with wordlist:
      spray -u http://example.com -w "/aaa/bbb{?l#4}/ccc"
    rule-base brute with wordlist:
      spray -u http://example.com -r rule.txt -d 1.txt
    list input spray:
      spray -l url.txt -r rule.txt -d 1.txt
    resume:
      spray --resume stat.json

Input Options:
      --resume=                     File, resume filename
  -c, --config=                     File, config filename
  -u, --url=                        Strings, input baseurl, e.g.: http://google.com
  -l, --list=                       File, input filename
  -p, --port=                       String, input port range, e.g.: 80,8080-8090,db
  -i, --cidr=                       String, input cidr, e.g.: 1.1.1.1/24
      --raw=                        File, input raw request filename
  -d, --dict=                       Files, Multi,dict files, e.g.: -d 1.txt -d 2.txt
  -D, --default                     Bool, use default dictionary
  -w, --word=                       String, word generate dsl, e.g.: -w test{?ld#4}
  -r, --rules=                      Files, rule files, e.g.: -r rule1.txt -r rule2.txt
  -R, --append-rule=                Files, when found valid path, use append rule generator
      --filter-rule=                String, filter rule, e.g.: --rule-filter '>8 <4'
      --append=                     Files, append file
      --offset=                     Int, wordlist offset
      --limit=                      Int, wordlist limit

Function Options:
  -e, --extension=                  String, add extensions, e.g.: -e jsp,jspx
      --force-extension             Bool, force add extensions
      --exclude-extension=          String, exclude extensions
      --remove-extension=           String, remove extensions
  -U, --uppercase                   Bool, upper wordlist
  -L, --lowercase                   Bool, lower wordlist
      --prefix=                     Strings, add prefix
      --suffix=                     Strings, add suffix
      --replace=                    Strings, replace string, e.g.: --replace aaa:bbb
      --skip=                       String, skip word when generate

Output Options:
      --match=                      String, custom match function
      --filter=                     String, custom filter function
      --fuzzy                       String, open fuzzy output
  -f, --file=                       String, output filename
      --dump-file=                  String, dump all request to file
      --dump                        Bool, dump all request
      --auto-file                   Bool, auto generator output filename
  -F, --format=                     String, output format
  -j, --json                        Bool, output json
  -O, --file-output=                Bool, file output format (default: json)
  -o, --probe=                      String, output mode: tree/full/probe (default: tree)
  -q, --quiet                       Bool, Quiet
      --no-color                    Bool, no color
      --no-bar                      Bool, No progress bar
      --no-stat                     Bool, No stat file output

Plugin Options:
  -a, --advance                     Bool, enable all plugin
      --extract=                    Strings, extract response
      --extract-config=             String, extract config filename
      --active                      Bool, enable active finger path
      --recon                       Bool, enable recon
      --bak                         Bool, enable bak found
      --fuzzuli                     Bool, enable fuzzuli plugin
      --common                      Bool, enable common file found
      --crawl                       Bool, enable crawl
      --crawl-depth=                Int, crawl depth (default: 3)
      --append-depth=               Int, append depth (default: 2)
      --finger                      Bool, enable active finger detect
      --finger-engine=              String, custom finger engine (default: all)

Request Options:
  -X, --method=                     String, request method (default: GET)
  -H, --header=                     Strings, custom headers
      --host=                       String, custom host header
      --path=                       String, custom request path
      --user-agent=                 String, custom user-agent
      --random-agent                Bool, use random user-agent
      --cookie=                     Strings, custom cookie
      --read-all                    Bool, read all response body
      --max-length=                 Int, max response body length kb (default: 100)

Modify Options:
      --rate-limit=                 Int, request rate limit (rate/s)
      --force                       Bool, skip error break
      --no-scope                    Bool, no scope
      --scope=                      String, custom scope
      --recursive=                  String, custom recursive rule
      --depth=                      Int, recursive depth (default: 0)
      --index=                      String, custom index path (default: /)
      --random=                     String, custom random path
      --check-period=               Int, check period when request (default: 200)
      --error-period=               Int, check period when error (default: 10)
      --error-threshold=            Int, break when error exceeds threshold (default: 20)
  -B, --black-status=               Strings, custom black status (default: 400,410)
  -W, --white-status=               Strings, custom white status (default: 200)
      --fuzzy-status=               Strings, custom fuzzy status
      --unique-status=              Strings, custom unique status
      --unique                      Bool, unique response
      --retry=                      Int, retry count (default: 0)

Miscellaneous Options:
  -m, --mod=[path|host]             String, path/host spray (default: path)
  -C, --client=[fast|standard|auto] String, Client type (default: auto)
      --deadline=                   Int, deadline seconds (default: 999999)
  -T, --timeout=                    Int, timeout seconds (default: 5)
  -P, --pool=                       Int, Pool size (default: 5)
  -t, --thread=                     Int, threads per pool (default: 20)
      --debug                       Bool, output debug info
      --version                     Bool, show version
  -v                                Bool, log verbose level
      --proxy=                      String, proxy address
      --init                        Bool, init config file
      --print                       Bool, print all preset config
      --finger-file=                Strings, custom finger YAML file path or URL
```

## Built-in Dictionaries

| Dict Name | Entries | Purpose |
|-----------|---------|---------|
| `default` | 9646 | 通用目录爆破 (综合字典) |
| `dir`     | 5152  | 目录字典 |
| `admin`   | 1002  | 后台管理路径 |
| `editor`  | 95    | 编辑器路径 |
| `cgi`     | 639   | CGI 路径 |
| `debug`   | 19    | 调试路径 |
| `springboot` | 306 | Spring Boot 路径 |
| `weblogic` | 312  | WebLogic 路径 |
| `k8s`     | 57    | Kubernetes 路径 |
| `log`     | 208   | 日志文件路径 |
| `js`      | 153   | JS 文件路径 |
| `common`  | 115   | 通用文件 |
| `swagger` | 54    | Swagger 文档路径 |
| `java`    | 1665  | Java Web 路径 |
| `iis`     | 79    | IIS 相关路径 |

## Built-in Rules

| Rule Name      | Count | Purpose |
|----------------|-------|---------|
| `extbypass`    | 12    | 扩展名绕过 |
| `filebak`      | 13    | 备份文件 |
| `authbypass`   | 56    | 认证绕过 |

## Built-in Extractor (--extract)

mail, inter-ip, wecom-key, pentest, windows-file, username, url, phone, ip, aws-ak, jwt, info, idcard, oss, s3, rsa-key, password, jdbc, js, github-token

## Built-in Finger Engines (--finger-engine)

goby, nmap, favicon, fingers, fingerprinthub, wappalyzer, ehole (all loaded by default with 14388 fingerprints)
