import io, base64
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from app.config import MAX_IMAGE_BYTES

def scatter_with_regression(data_x, data_y, x_label: str, y_label: str, dotted_red: bool = False) -> str:
    x = np.asarray(data_x, dtype=float)
    y = np.asarray(data_y, dtype=float)
    m, b = np.polyfit(x[~(np.isnan(x)|np.isnan(y))], y[~(np.isnan(x)|np.isnan(y))], 1)

    fig = plt.figure(figsize=(5, 4), dpi=120)
    ax = fig.gca()
    ax.scatter(x, y)
    yy = m*x + b
    if dotted_red:
        ax.plot(x, yy, linestyle=":", color="red")
    else:
        ax.plot(x, yy)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle=":", linewidth=0.5)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)

    # Shrink if needed
    img_bytes = buf.getvalue()
    if len(img_bytes) > MAX_IMAGE_BYTES:
        # Try WebP fallback
        try:
            from PIL import Image
            buf2 = io.BytesIO(img_bytes)
            im = Image.open(buf2)
            out = io.BytesIO()
            im.save(out, format="WEBP", quality=55, method=6)
            data = out.getvalue()
            mime = "image/webp"
        except Exception:
            data = img_bytes[:MAX_IMAGE_BYTES]
            mime = "image/png"
    else:
        data = img_bytes
        mime = "image/png"

    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"
