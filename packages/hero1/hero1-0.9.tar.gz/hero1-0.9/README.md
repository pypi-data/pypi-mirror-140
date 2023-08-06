# Hero1

```
import hero1

s = hero1.setup("test")
hero1.init(10,10,0,0)
c = hero1.Cmd()
c.cmd = hero1.CmdType.MAP
c.strings.append('coin')
c.ints.append(3)
c.ints.append(1)
c.ints.append(2)
c.ints.append(2)
s.sendall(c.SerializeToString())
s.recv(1024)
hero1.render()

hero1.scan()
while hero1.canMoveDown():
  hero1.moveDown()
hero1.moveRight()
hero1.moveUp()
```



