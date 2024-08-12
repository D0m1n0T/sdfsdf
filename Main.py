# ============================================================
#  🖱️  PYTHON AUTOCLICKER  –  tanulási célra
#  Szükséges könyvtárak:  pip install pynput
# ============================================================

# --- IMPORT BLOKK ---
# 'pynput' egy külső könyvtár (library), amit előbb telepíteni kell.
# Alternatíva: pyautogui (más szintaxis, de hasonló), xdotool (Linux), pywin32 (Windows-only)
import time                          # Beépített modul: időzítéshez, várakozáshoz
import threading                     # Beépített modul: párhuzamos futtatáshoz (hogy a klikk NE blokkolja a billentyűfigyelést)

from pynput.mouse import Button, Controller as MouseController
# Button      → egy Enum (felsorolás): Button.left, Button.right, Button.middle
# Controller  → az objektum, amellyel ténylegesen mozgatjuk/kattintjuk az egeret
# Alternatíva: pyautogui.click() – de az nem tud háttérben futni billentyűfigyeléssel együtt

from pynput.keyboard import Key, Listener as KeyboardListener
# Key      → speciális billentyűk Enum-ja: Key.f8, Key.esc, Key.ctrl_l, stb.
# Listener → háttérben figyeli a billentyűzetnyomásokat (nem blokkolja a programot)
# Alternatíva: keyboard könyvtár (keyboard.on_press), de az root jogot kér Linuxon


# ============================================================
#  BEÁLLÍTÁSOK  –  ezeket szabadon változtathatod
# ============================================================

CLICK_INTERVAL  = 0.05   # Másodpercek két kattintás között  (0.05 = 20 katt/mp)
                          # Minél kisebb a szám, annál gyorsabb. 0.001 ≈ 1000 katt/mp
TOGGLE_KEY      = Key.f8  # Ezzel kapcsolható be/ki az autoclicker  →  F8
                          # Alternatíva: Key.f6, Key.insert, Key.scroll_lock  stb.
CLICK_BUTTON    = Button.left  # Melyik egérgombot nyomja: .left / .right / .middle


# ============================================================
#  GLOBÁLIS ÁLLAPOTVÁLTOZÓK
# ============================================================

# 'mouse' az egér vezérlő-objektuma – ezen keresztül küldünk kattintást
mouse = MouseController()
# Alternatíva helyett: pyautogui.click() – de az nem tud háttérben futni

# Ez a változó tárolja, hogy most épp kattintgat-e a program (True/False = logikai típus)
clicking = False
# Miért globális? Mert két különböző szál (thread) olvassa/írja: a klikkelő és a billentyűfigyelő

# A klikkelő szálat is el kell tárolni, hogy le tudjuk állítani
click_thread = None


# ============================================================
#  FÜGGVÉNYEK  (def = define, azaz meghatároz)
# ============================================================

def click_loop():
    """
    Ez a függvény fut a háttérszálban.
    Addig kattint, amíg a 'clicking' változó True.
    """
    # 'global clicking' megmondja Pythonnak: ne csinálj helyi változót,
    # hanem a fentebb deklarált globálisat használd
    global clicking

    while clicking:                          # Végtelen ciklus, amíg clicking == True
        mouse.click(CLICK_BUTTON)            # Ténylegesen kattint egyet
        # mouse.click(Button.left, 2)        # Alternatíva: dupla kattintás
        time.sleep(CLICK_INTERVAL)           # Vár N másodpercet a következő kattintás előtt
        # time.sleep(0) – azonnali, de processzort terheli maximálisan!


def start_clicking():
    """Elindítja a kattintgatást egy új háttérszálon."""
    global clicking, click_thread

    if clicking:          # Ha már fut, nem indít másodikat
        return

    clicking = True
    print("▶  Autoclicker BEKAPCSOLVA  –  nyomj F8-at a leállításhoz")

    # Thread: egy külön "mini-program" fut párhuzamosan a főszállal
    # target=click_loop → ezt a függvényt fogja futtatni a szál
    # daemon=True       → ha a főprogram véget ér, ez a szál is automatikusan leáll
    #                     (daemon nélkül a szál "életben tartja" a programot bezárás után is)
    # Alternatíva: asyncio – de threadinghez képest bonyolultabb kezdőknek
    click_thread = threading.Thread(target=click_loop, daemon=True)
    click_thread.start()   # .start() ELINDÍTJA a szálat (nem .run()! az blokkolna)


def stop_clicking():
    """Leállítja a kattintgatást."""
    global clicking

    if not clicking:      # Ha már áll, nem csinál semmit
        return

    clicking = False      # A click_loop() while-ja ezt figyeli → kilép a ciklusból
    print("⏹  Autoclicker KIKAPCSOLVA")


def on_press(key):
    """
    Ezt a függvényt hívja meg a KeyboardListener minden billentyűnyomásra.
    Paraméter 'key': a lenyomott billentyű Key-objektuma vagy karaktere.
    """
    # A toggle (kapcsoló) logika: ha fut → állítsd le, ha áll → indítsd el
    if key == TOGGLE_KEY:
        if clicking:
            stop_clicking()
        else:
            start_clicking()

    # ESC → teljesen kilép a programból
    # A Listener.stop() leállítja a billentyűfigyelőt, a főszál pedig véget ér
    elif key == Key.esc:
        stop_clicking()
        print("👋  Kilépés – ESC lenyomva")
        return False   # False visszatérési értékkel jelezzük a Listenernek: állj le!
        # Alternatíva: os._exit(0) – azonnali, durva kilépés; raise SystemExit – szebb


# ============================================================
#  BELÉPÉSI PONT  –  if __name__ == "__main__"
# ===========================================================
# Ez a sor biztosítja, hogy az alábbi kód CSAK akkor fusson le,
# ha közvetlenül futtatják a fájlt (pl. python autoclicker.py),
# de NE fusson le, ha másik Python-fájl importálja ezt modulként.
# Alternatíva: nincs igazán – ez a Python bevált konvenciója

if __name__ == "__main__":
    print("=" * 50)
    print("  🖱️  Python Autoclicker")
    print(f"  Kapcsoló: F8  |  Kilépés: ESC")
    print(f"  Sebesség: {1 / CLICK_INTERVAL:.0f} kattintás/mp")
    print("=" * 50)

    # KeyboardListener indítása
    # suppress=False → a billentyűlenyomások továbbra is eljutnak más programokhoz is
    # Ha suppress=True lenne: "elnyeli" az F8-at, nem látná más szoftver
    with KeyboardListener(on_press=on_press) as listener:
        # A 'with' blokk (context manager) automatikusan elvégzi a takarítást (listener.stop())
        # ha a blokk véget ér – akár normálisan, akár hiba miatt.
        # Alternatíva: listener.start() + listener.join() – manuálisan, 'with' nélkül
        listener.join()   # .join() = várakozás: addig tartja életben a főszálat,
                          #           amíg a listener fut (tehát amíg ESC-et nem nyomunk)