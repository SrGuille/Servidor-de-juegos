import matplotlib.font_manager as fm

# Obtener todas las fuentes disponibles
fonts = sorted(set([f.name for f in fm.fontManager.ttflist]))

print(f"=== Fuentes disponibles en matplotlib ({len(fonts)}) ===\n")
for font in fonts:
    print(font)
