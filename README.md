# german-dict cli

## Introduction
The german-dict cli is a command-line interface designed to help users easily find the conjugation or declension of a German word. The cli is written in Python, and it uses the popular requests library to fetch data from external sources.
<br><br>
It is also using OPENAI API for creating sentences and the fetched definitions, sentences, conjugations etc are saved locally to SQLite3 database.

## Installation
Before installing the CLI, make sure you have Python 3 installed on your system. To install the CLI, run the following command:

```bash
$ pip install -r requirements.txt
```

## Usage
To use the `german-dict` cli, open up a terminal and type in german-dict, followed by the word you want to look up. You can also add any of the optional arguments `-h`, `-p`, `-s`, and `-c`. The following command will show the usage of it. `-d` flag have not been implemented yet.
<br><br>
Note that you have to use <b>OPENAI API key</b>, and have to save it to environmental variable called `OPENAI_API_KEY`. Secondly, you have to create an environmental variable called `GERMAN_DICT_DIR`, which should be the path of the project folder.
```
$ german-dict -h
usage: german-dict [-h] [-p] [-d | -c | -s] [-r] word

positional arguments:
  word                 the word that you want to look for.

options:
  -h, --help           show this help message and exit
  -p, --pronunciation  gives the link for the pronunciation of the word.
  -d, --declension     prints the declension of the word.
  -c, --conjugation    prints the conjugation of the word.
  -s, --sentence       prints example sentences.
  -r, --replace        replaces the example sentences.
```

## Examples

Here is one example for the declension of a noun.
<pre>$ german-dict laufen
<span style="color:#12488B"><b>laufen</b></span>
<span style="color:#C01C28"><b>run, walk, race, be in process, function, pass, go, flow, move, be in progress</b></span>
</pre>

<pre>$ german-dict laufen --conjugation
1 = present
2 = imperfect
3 = imperative
4 = present subj.
5 = imperf. subj.
6 = infinitive
7 = participle
Enter the desired id: 1
<span style="color:#C01C28"><b>present</b></span>
<span style="color:#12488B"><b>ich</b></span>       <span style="color:#26A269"><b>lauf(e)</b></span>
<span style="color:#12488B"><b>du</b></span>        <span style="color:#26A269"><b>läufst</b></span>
<span style="color:#12488B"><b>er</b></span>        <span style="color:#26A269"><b>läuft</b></span>
<span style="color:#12488B"><b>wir</b></span>       <span style="color:#26A269"><b>laufen</b></span>
<span style="color:#12488B"><b>ihr</b></span>       <span style="color:#26A269"><b>lauft</b></span>
<span style="color:#12488B"><b>sie</b></span>       <span style="color:#26A269"><b>laufen</b></span>
</pre>

You  can see the sentences created by the API of OPENAI.
<pre>$ german-dict laufen --sentence

<span style="color:#12488B">Ich laufe ins Geschäft.</span>            <span style="color:#A2734C"><i>I am running to the store.</i></span>

<span style="color:#12488B">Der Mann läuft langsam.</span>            <span style="color:#A2734C"><i>The man is running slowly.</i></span>

<span style="color:#12488B">Wir laufen nicht schnell.</span>          <span style="color:#A2734C"><i>We are not running quickly.</i></span>

<span style="color:#12488B">Du kannst nicht laufen.</span>            <span style="color:#A2734C"><i>You can&apos;t run.</i></span>

<span style="color:#12488B">Sie laufen zu Fuß.</span>                 <span style="color:#A2734C"><i>They are running on foot.</i></span>
</pre>

`--replace` flag updates the sentences in database.

<pre>$ german-dict laufen --sentence --replace

<span style="color:#12488B">Ich laufe nach Hause.</span>              <span style="color:#A2734C"><i>I am running home.</i></span>

<span style="color:#12488B">Wann läufst du?</span>                    <span style="color:#A2734C"><i>When are you running?</i></span>

<span style="color:#12488B">Er lief zur Bahnstation.</span>           <span style="color:#A2734C"><i>He ran to the train station.</i></span>

<span style="color:#12488B">Laufen Sie heute?</span>                  <span style="color:#A2734C"><i>Are you running today?</i></span>

<span style="color:#12488B">Sie laufen zusammen.</span>               <span style="color:#A2734C"><i>They are running together.</i></span>
</pre>
## Contributing
This is just a fun project and it's been tested only on Debian 12 (linux). 

Contributions are always welcomed at any time.
