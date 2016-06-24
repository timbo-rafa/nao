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
Conferir se o script da scene do V-REP tem nas ultimas duas linhas (uso a porta 25000 pro V-REP
e a porta 26000 pro Choreographe Suite)
```
newPortNb=25000
simExtRemoteApiStart(newPortNb, 250, true)
```

- set_py_env.sh: exporta pynaoqi para o path do python
maioria dos scripts da pasta Scripts estao originalmente na pasta do pynaoqi em
```
/path/to/V-REP_PRO_EDU_V3_3_1_64_Linux/programming/remoteApiBindings/python/python
```
- Scripts/simpleTest.py: funcionou aqui mas so fez o nao cair
- Scripts/almotion_wbKick.2.1.py: [script] que teoricamente era pra fazer o nao andar

### Execucao

- Roda servidor no choreographe:
```
/opt/vrep/choregraphe-suite-2.4.3.28-linux64/bin$ ./naoqi-bin -p 26000 &
```
- Liga o V-REP importa a scene e da play
- Roda o script cliente teste(NAO cai):
```
/path/to/Project-NAO-Control/Scripts$ python single_nao_control.py
```
- Roda o script cliente(nao faz o NAO chutar ainda, mas acredito que esse
[script] almotion_wbkick seja um bom comeco):
```
Project-NAO-Control/Scripts$ python almotion_wbKick.2.1.py
```

[v-rep]:www.coppeliarobotics.com/downloads.html
[Project-NAO-Control]:https://github.com/PierreJac/Project-NAO-Control
[Aldebaran]:https://community.ald.softbankrobotics.com/en/resources/software/language/en-gb
[script]:http://doc.aldebaran.com/2-1/dev/python/examples/motion/whole_body.html
