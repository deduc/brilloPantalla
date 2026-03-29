# 🖥️ 1. Ver pantallas conectadas

El comando más común:
```
xrandr --listmonitors
```


Te mostrará salidas como HDMI-1, eDP-1, DP-1, etc.  
👉 Esos nombres los usarás en los siguientes comandos.

---

# 💡 2. Brillo

## 🔍 Ver brillo actual (por pantalla)
```
xrandr --verbose | grep -i brightness
```

⚠️ Nota: xrandr usa valores tipo:

- 1.0 = normal  
- 0.5 = más oscuro  
- 1.5 = más brillante  

---

## ⬆️ Subir brillo

```
xrandr --output eDP-1 --brightness 1.2
```

## ⬇️ Bajar brillo
```
xrandr --output eDP-1 --brightness 0.7
```

(Reemplaza eDP-1 por tu pantalla)

---

## 🔎 Método alternativo (hardware real, mejor en laptops)

```
ls /sys/class/backlight/
```

Luego:

```
cat /sys/class/backlight/intel_backlight/brightness  
cat /sys/class/backlight/intel_backlight/max_brightness  
```

👉 Aquí sí tienes:

- nivel actual  
- nivel máximo  

### Subir/bajar:

```
echo 500 | sudo tee /sys/class/backlight/intel_backlight/brightness
```

---

# 🎨 3. Contraste

Linux no tiene “contraste real” estándar, pero puedes simularlo con gamma:

## 🔍 Ver valores actuales

```
xrandr --verbose | grep -i gamma
```

---

## Ajustar contraste (simulado)

### ⬆️ Más contraste

```
xrandr --output eDP-1 --gamma 1.2:1.2:1.2
```

### ⬇️ Menos contraste

```
xrandr --output eDP-1 --gamma 0.8:0.8:0.8
```

---

# 🔵 4. Luz azul (filtro)

Esto se controla modificando los canales RGB.

## 🔍 Ver valores actuales

```
xrandr --verbose | grep -i gamma
```

---

## ⬇️ Reducir luz azul (modo noche)

```
xrandr --output eDP-1 --gamma 1:1:0.7
```

👉 Reduce el canal azul

---

## ⬆️ Restaurar luz azul normal

```
xrandr --output eDP-1 --gamma 1:1:1
```

---

# 🧠 Alternativa mejor para luz azul (recomendada)

Instala:

```
sudo apt install redshift
```

### Ejecutar:

```
redshift -O 4500
```

### Restaurar:

```
redshift -x
```