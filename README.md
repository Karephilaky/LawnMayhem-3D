
# LawnMayhem 3D

**LawnMayhem 3D** es un juego 3D en tercera persona desarrollado con **Pygame** y **OpenGL**, donde controlarás una podadora futurista a través de un jardín lleno de peligros... y conejos.

## 🌱 Lore

En un futuro no muy lejano, los jardines inteligentes se han salido de control. Los **conejos biónicos**, creados originalmente para mantener la biodiversidad, se han multiplicado sin control y están consumiendo toda la energía solar de la superficie.

La única esperanza: tú. Un jardinero solitario, equipado con la **LawnMower X9000**, debes recorrer kilómetros de césped digitalizado y **eliminar a los conejos** antes de que absorban el ecosistema entero.

Pero no estás solo:
- 🧱 **Las piedras** son obstáculos antiguos del viejo jardín: al golpearlas, pierdes salud.
- 🧌 **Los gnomos** son reliquias encantadas que te hacen perder puntos si los dañas. ¡Evítalos!

## 🎮 Controles

| Tecla       | Acción                            |
|-------------|-----------------------------------|
| ← / →       | Mover la podadora a izquierda/derecha |
| Enter       | Iniciar partida desde el menú     |
| R           | Reiniciar después de un Game Over |
| ESC         | Salir del juego                   |
| M           | Pausar / Reanudar música          |

## 🕹️ Gameplay

- El césped se desplaza hacia ti automáticamente.
- Puedes cambiar de carril entre tres posiciones: izquierda, centro, y derecha.
- Ganas puntos por cada **conejo eliminado**.
- Pierdes puntos por golpear **gnomos**.
- Pierdes salud al chocar con **piedras**.
- El juego termina si tu salud llega a cero.

Además, verás **efectos de partículas**:
- 🔴 Rojas al eliminar conejos
- 🟡 Amarillas al golpear piedras
- 🌸 Rosadas al tocar gnomos

## 📁 Estructura del proyecto

```
LawnMayhem 3D/
│
├── main.py                     # Código principal
├── README.md                   # Este archivo
├── models/                     # Modelos 3D (.obj)
│   ├── lawnmower.obj
│   ├── Bunny_lowpoly.obj
│   ├── cube.obj
│   └── ...
├── sound/
│   └── C418 - Haggstrom - Minecraft Volume Alpha.mp3
├── game/
│   ├── __init__.py
│   ├── utils.py                # Carga de modelos
│   ├── conejo.py
│   ├── gnomo.py
│   └── piedra.py
```

## 🛠️ Tecnologías

- Python 3.12+
- Pygame 2.6+
- PyOpenGL
- Modelos .obj low poly
- Música: **C418 - Haggstrom** (Minecraft Volume Alpha)

## ✨ Créditos

Desarrollado por Johannes Carofilis Veliz

Inspirado en la estética low-poly y los minijuegos arcade, con un toque de humor absurdo y caos de jardín.

---

¡Diviértete podando!
