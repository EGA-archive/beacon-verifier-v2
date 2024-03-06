import subprocess

bash_string = ('python3 analyses.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 biosamples.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 cohorts.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 datasets.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 genomicVariations.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 individuals.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
bash_string = ('python3 runs.py')
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    replaced_stringed_bash=replaced_stringed_bash.replace("\n","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)