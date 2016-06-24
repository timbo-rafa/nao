## Setup

- Download [v-rep]
- Download [Project-NAO-Control]
- Download Choreographe suite e Python NAOqi SDK da [Aldebaran],
que abstrai uns movimentos pro robo

Coloquei todos esses programas em /opt/vrep/
```sh
/opt/vrep$ ls
choregraphe-suite-2.4.3.28-linux64         pynaoqi-python2.7-2.1.4.13-linux64.tar.gz
choregraphe-suite-2.4.3.28-linux64.tar.gz  V-REP_PRO_EDU_V3_3_1_64_Linux
pynaoqi-python2.7-2.1.4.13-linux64
```

set_py_env.sh: exporta pynaoqi para o path do python
maioria dos scripts da pasta Scripts estao originalmente na pasta do pynaoqi em
```
/path/to/V-REP_PRO_EDU_V3_3_1_64_Linux/programming/remoteApiBindings/python/python
```

- Scripts/simpleTest.py: funcionou aqui mas so fez o nao cair
- Scripts/almotion_wbKick.2.1.py: [script] que teoricamente era pra fazer o nao andar


[v-rep]:www.coppeliarobotics.com/downloads.html
[Project-NAO-Control]:https://github.com/PierreJac/Project-NAO-Control
[Aldebaran]:https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb
[script]:http://doc.aldebaran.com/2-1/dev/python/examples/motion/whole_body.html
