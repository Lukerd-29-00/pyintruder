# Pyintruder
This is a command-line tool I built for myself as a substitute for Portswigger's intruder tool, which I didn't want to pay for. The tool itself is my own code and is open source.

## Installation
this can be installed via pip. 
```bash
pip3 install git+https://github.com/Lukerd-29-00/pyintruder
```
The package is not on PyPi, thus the git+ prefix is necessary. Once you have installed it, you may access the command line tool with the command 
```bash
python3 -m pyintruder
```
You can also import pyintruder into a python script the same way you would import any other module.
## Usage
This tool is designed to be used along side Portswigger's <a href="https://portswigger.net/burp/communitydownload">Burp Suite</a> tool for web vulnerability testing. If you're familiar with the intruder tool, this tool's usage is very similar. It takes a file containing the full text of an HTTP request, with a few variables that are substituted from keywords in a dictionary file. By default, it will print out the substiuted values at the end along with the status code from the server when the request was sent.

### getting more response information
If you need more information than the status code, you will need to write your own python program and import pyintruder as a module instead of using the command line. you can supply a callback to the IntruderSession.intrude_pitchfork method that processes the response from the server, which will supply the output of the function.

### Positional Parameters
This tool takes two positional arguments; the template file followed by the host being contacted.

#### Template-file
This file should contain the raw text of an HTTP request. You can obtain this easily by examining the request in burp suite, and then copying it into a text file. The tool will interpret this as a python format string. This means you can substitute values by putting them in curly braces ('{' and '}'). If you need to use literal curly braces, you simply type double brackets '{{' and '}}'. Make sure you don't leave curly brackets that need to be escaped this way accidentally. 

##### Sample template file
here's the original request to the server:

```
GET / HTTP/1.1
Host: www.test.com
Sec-Ch-Ua: "Chromium";v="123", "Not:A-Brand";v="8"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: close


```
Now let's replace the method with a variable that we can substitute:

```
{verb} / HTTP/1.1
Host: www.test.com
Sec-Ch-Ua: "Chromium";v="123", "Not:A-Brand";v="8"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: close


```

This allows you to substitute the variable 'verb' for HTTP verbs. See the dictionaries option to map these variables to a list of values to substitute them for.

#### host
This is the server you are targeting. This should just be the <i>server</i>. There should be no path or query parameters. If the page you want is www.foo.com/page.html, you should <i>not</i> enter https://www.foo.com/page.html, but <i>only</i> https://www.foo.com. The path is included in the HTTP template file so that you can add parameters like anywhere else in the request.

### Options:
This tool has several switches and options. All of these are optional except the dictionaries argument.

#### dictionaries
This option (indicated by -d or --dictionaries) maps variables in the template file (see above) to dictionary files. It uses the format variable,file. The file can be either a relative or absolute path to a file. The file should be a list of strings that are substituted into the request, one per line. 

##### default dictionaries
This tool comes with a few default wordlists. You can list these dictionaries with the -l or --ls switch (see below). To use these, you can simply type the file name of one of the dictionaries instead of a path to a file. You can use a file that has the same name as one of the default dictionaries by starting the file name with './' (or .\\ on windows).

##### multipile occurrences
The dictionaries option can occur several times, to allow you to substitute multipile variables with different wordlists. This will behave like Burp Suite's pitchfork attack; it will move through the lists in lockstep. Here's an example. Suppose you have two dictionary files, list_1.txt and list_2.txt.

list_1.txt
```
a
b
```
list_2.txt
```
b
a
```

and the following template:
```
GET /{value_1}/{value_2} HTTP/1.1
Host: www.google.com
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
X-Client-Data: COHrygE=
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Chromium";v="123", "Not:A-Brand";v="8"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Full-Version: ""
Sec-Ch-Ua-Arch: ""
Sec-Ch-Ua-Platform: "Windows"
Sec-Ch-Ua-Platform-Version: ""
Sec-Ch-Ua-Model: ""
Sec-Ch-Ua-Bitness: ""
Sec-Ch-Ua-Wow64: ?0
Sec-Ch-Ua-Full-Version-List: 
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: close


```

now if we run the following command:
```bash
python3 -m pyintruder template.txt https://www.google.com -d value_1,list_1.txt -d value_2,list_2.txt --verbose
```
the tool makes these two requests:
```
GET /b/a: 404
GET /a/b: 404
```


#### help
The -h or --help switch will display a brief summary of the usage as a reminder if you forget the syntax.

#### ls
The -l or --ls switch will display the files included in the pyintruder library itself (see default dictionaries above). No other parameters should be listed if this switch is used.

#### verbose
The -v or --verbose switch tells the tool to log requests as they happen, allowing you to see that the tool is making progress. It also displays the URL, which can be useful for debugging.

#### no-ssl
The -s or --no-ssl switch indicates that the library should continue if the certificate is invalid (e.g. a self-signed certificate)

#### batch size
the -b or --batch-size switch is the number of requests that are sent out at once (the requests are handled asynchronously). The default value is 10. The higher the number, the faster the attack completes. However, too high a batch size may trigger rate limiting issues or overwhelm the server if you aren't careful. The default value is 10, so if this parameter isn't specified, the tool won't send more than 10 requests at a time.

### Example usage
Here is a sample of using the tool. First, we copy the raw text of a request from burp into a file.

<img src="burp_request.png">
template.txt:

```
GET / HTTP/1.1
Host: www.test.com
Sec-Ch-Ua: "Chromium";v="123", "Not:A-Brand";v="8"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: close


```

Then we replace some part of the request (in this case the method) with a template string:

```
{verb} / HTTP/1.1
Host: www.test.com
Sec-Ch-Ua: "Chromium";v="123", "Not:A-Brand";v="8"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: close


```

Now we enter the command:
```bash
python3 -m pyintruder -d verb,HTTP_verbs.txt template.txt https://www.google.com
```

and get this output:
```
-----RESULTS-----
verb=DELETE: 405
verb=GET: 200
verb=HEAD: 200
verb=OPTIONS: 405
verb=PATCH: 405
verb=POST: 405
verb=PUT: 405
-----------------
```

And now we can see that https://www.google.com/ only accepts the GET and HEAD methods.
