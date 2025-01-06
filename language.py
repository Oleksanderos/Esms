import ctypes

# Константи для зміни розкладки клавіатури
LANG_ENGLISH = 0x0409  # Код англійської мови
LANG_UKRAINIAN = 0x0422  # Код української мови

def get_current_language():
    """Отримує поточний код мови вводу."""
    user32 = ctypes.windll.user32
    current_lang = user32.GetKeyboardLayout(0) & 0xFFFF  # Отримуємо поточну мову
    return current_lang

def set_keyboard_language(lang_id):
    """Змінює розкладку клавіатури на задану."""
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()  # Отримуємо активне вікно
    user32.PostMessageW(hwnd, 0x50, 0, lang_id)  # Змінюємо мову

def reset_keyboard_language(initial_lang):
    """Повертає початкову розкладку."""
    set_keyboard_language(initial_lang)
