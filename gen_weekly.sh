d=`date +"%Y-%m-%d%H-%M-%S"`
cp -r weekly weekly.$d

rm weekly/*
d=`date +"%Y-%m-%d"`

python 2md.py Go > weekly/go_weekly.$d.md
python 2md.py C++ > weekly/cplusplus_weekly.$d.md
python 2md.py C > weekly/c_weekly.$d.md

python 2md.py Python > weekly/python_weekly.$d.md
python 2md.py Perl > weekly/perl_weekly.$d.md
python 2md.py PHP > weekly/php_weekly.$d.md

python 2md.py JavaScript > weekly/javascript_weekly.$d.md
python 2md.py Vue > weekly/vue_weekly.$d.md
python 2md.py HTML > weekly/html_weekly.$d.md

python 2md.py Java > weekly/java_weekly.$d.md
python 2md.py Scala > weekly/scala_weekly.$d.md
python 2md.py Kotlin > weekly/kotlin_weekly.$d.md

python 2md.py TECHBLOG > weekly/techblog_weekly.$d.md
