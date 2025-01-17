# partial-parsing

Demonstration of command-line chaining with argparse

```sh
echo 'Hello woooorld!!' | poetry run python3 src/partial_parse/main.py uniq
Helo world!
```

```sh
echo 'Hello woooorld!!' | poetry run python3 src/partial_parse/main.py uniq -c
H=1@e=1@l=2@o=1@ =1@w=1@o=4@r=1@l=1@d=1@!=2
```

```sh
echo 'Hello woooorld!!' | python3 src/partial_parse/main.py uniq -c tr "@" $'\n'
H=1
e=1
l=2
o=1
 =1
w=1
o=4
r=1
l=1
d=1
!=2
```


```sh
df | awk 'NR != 1{print}' | tr -s ' ' | python3 src/partial_parse/main2.py sort -t' ' -nrk1 | column -t 
/dev/sda1   47145992  37676136  9453472   80%  /
tmpfs       12277308  200       12277108  1%   /dev/shm
tmpfs       2455464   1820      2453644   1%   /run
tmpfs       2455460   632       2454828   1%   /run/user/1002
/dev/sda15  99800     6475      93326     7%   /boot/efi
tmpfs       5120      0         5120      0%   /run/lock
efivarfs    256       15        242       6%   /sys/firmware/efi/efivars
```
