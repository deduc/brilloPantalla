Ver pantallas conectadas
xrandr --listmonitors

Ver brillo actual (por pantalla)
xrandr --verbose | grep -i brightness

Subir brillo
xrandr --output eDP-1 --brightness 1.2

Bajar brillo
xrandr --output eDP-1 --brightness 0.7

Ver método hardware de brillo
ls /sys/class/backlight/

Ver brillo actual hardware
cat /sys/class/backlight/intel_backlight/brightness

Ver brillo máximo hardware
cat /sys/class/backlight/intel_backlight/max_brightness

Ajustar brillo hardware
echo 500 | sudo tee /sys/class/backlight/intel_backlight/brightness

Ver valores de contraste actuales
xrandr --verbose | grep -i gamma

Aumentar contraste
xrandr --output eDP-1 --gamma 1.2:1.2:1.2

Reducir contraste
xrandr --output eDP-1 --gamma 0.8:0.8:0.8

Ver valores de gamma actuales
xrandr --verbose | grep -i gamma

Reducir luz azul (modo noche)
xrandr --output eDP-1 --gamma 1:1:0.7

Restaurar luz azul normal
xrandr --output eDP-1 --gamma 1:1:1

Instalar redshift
sudo apt install redshift

Ejecutar redshift
redshift -O 4500

Restaurar redshift
redshift -x
