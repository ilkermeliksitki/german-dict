# german-dict cli

## Introduction
The german-dict cli is a command-line interface designed to help users easily find the conjugation or declension of a German word. The cli is written in Python, and it uses the popular requests library to fetch data from external sources.

## Installation
Before installing the CLI, make sure you have Python 3 installed on your system. To install the CLI, run the following command:

```bash
$ pip install -r requirements.txt
```

## Usage
To use the `german-dict` cli, open up a terminal and type in german-dict, followed by the word you want to look up. You can also add any of the optional arguments `-h`, `-p`, `-d`, and `-c`. The following command will show the usage of it.

```
$ german-dict -h
usage: german-dict [-h] [-p] (-d | -c) word

positional arguments:
  word                 the word that you want to look for.

options:
  -h, --help           show this help message and exit
  -p, --pronunciation  gives the link for the pronunciation of the word.
  -d, --declension     prints the declension of the word.
  -c, --conjugation    prints the conjugation of the word.
```

## Examples

Here is one example for the declension of a word.
<pre>
$ german-dict -d musik
<span><b>die Musik</b></span>
<span><b>music</b></span>

           Singular     Plural
Fälle
akkusativ  die Musik    die Musiken
dativ      der Musik    den Musiken
genitiv    der Musik    der Musiken
nominativ  die Musik    die Musiken
</pre>

Here is one example of the conjugaison of a verb.
<pre>
$ german-dict -c spielen
<span><b>spielen</b></span>
play, play (against), have a tinge (of), play (with), play opposite, fiddle about (with), fiddle around (with), toy with, be set, enact

<span><b>präsens</b></span>
pronoun   conjugaiton
ich         spiel(e)⁵
du          spielst  
er          spielt   
wir         spielen  
ihr         spielt   
sie         spielen  

<span><b>präteritum</b></span>
pronoun   conjugaiton
ich         spielte  
du          spieltest
er          spielte  
wir         spielten 
ihr         spieltet 
sie         spielten 

<span><b>imperativ</b></span>
pronoun      conjugaiton 
-                     NaN
spiel(e)⁵    (du)        
-                     NaN
spielen      wir         
spielt       (ihr)       
spielen      Sie         

<span><b>konjunktiv i</b></span>
pronoun  conjugaiton
ich         spiele  
du          spielest
er          spiele  
wir         spielen 
ihr         spielet 
sie         spielen 

<span><b>konjunktiv ii</b></span>
pronoun   conjugaiton
ich         spielte  
du          spieltest
er          spielte  
wir         spielten 
ihr         spieltet 
sie         spielten 
</pre>

## Contributing
This is just a fun project and it's been tested only on Debian 12 (linux). 

Contributions are always welcomed at any time.
