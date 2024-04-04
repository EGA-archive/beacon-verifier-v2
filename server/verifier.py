import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

string='python3 analyses.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 biosamples.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 cohorts.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 datasets.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 filtering_terms.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 genomicVariations.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 individuals.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 runs.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)