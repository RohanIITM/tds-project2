import io, base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from app.settings import settings

# Ensure each chart is a single plot; caller provides x/y and labels

def scatter_with_regression(x, y, xlabel: str, ylabel: str, dotted_red: bool = False):
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    # regression
    m, b = np.polyfit(x, y, 1)
    xs = np.array([min(x), max(x)])
    ys = m * xs + b
    if dotted_red:
        ax.plot(xs, ys, linestyle=":", color="red")
    else:
        ax.plot(xs, ys)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)

    # size guard: re-encode via PIL and optimize to stay < MAX_IMAGE_BYTES
    buf.seek(0)
    img = Image.open(buf)
    # downscale if needed
    max_side = 900
    if max(img.size) > max_side:
        ratio = max_side / max(img.size)
        img = img.resize((int(img.width*ratio), int(img.height*ratio)))
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    data = out.getvalue()
    # last resort: reduce DPI/resize
    while len(data) > settings.MAX_IMAGE_BYTES and max(img.size) > 400:
        img = img.resize((int(img.width*0.9), int(img.height*0.9)))
        out = io.BytesIO()
        img.save(out, format="PNG", optimize=True)
        data = out.getvalue()
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}", float(m)
