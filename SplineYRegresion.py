import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# -------- SPLINE CÚBICO NATURAL --------
def spline_cubico_natural(x, y, x_eval):
    n = len(x)
    h = [x[i+1] - x[i] for i in range(n - 1)]
    alpha = [0] * n

    for i in range(1, n - 1):
        alpha[i] = (3/h[i]) * (y[i+1] - y[i]) - (3/h[i-1]) * (y[i] - y[i-1])

    l = [1] + [0]*(n - 1)
    mu = [0] * n
    z = [0] * n

    for i in range(1, n - 1):
        l[i] = 2 * (x[i+1] - x[i-1]) - h[i-1] * mu[i-1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i-1]*z[i-1]) / l[i]

    l[n-1] = 1
    z[n-1] = 0
    c = [0] * n
    b = [0] * (n - 1)
    d = [0] * (n - 1)
    a = y[:-1]

    for j in reversed(range(n - 1)):
        c[j] = z[j] - mu[j] * c[j+1]
        b[j] = (y[j+1] - y[j]) / h[j] - h[j] * (c[j+1] + 2 * c[j]) / 3
        d[j] = (c[j+1] - c[j]) / (3 * h[j])

    # Evaluar en el intervalo correspondiente
    i = 0
    for j in range(n - 1):
        if x[j] <= x_eval <= x[j+1]:
            i = j
            break

    dx = x_eval - x[i]
    resultado = a[i] + b[i]*dx + c[i]*dx**2 + d[i]*dx**3

    detalles = f"Spline en intervalo [{x[i]}, {x[i+1]}]:\n"
    detalles += f"P(x) = {a[i]:.4f} + {b[i]:.4f}(x - {x[i]}) + {c[i]:.4f}(x - {x[i]})² + {d[i]:.4f}(x - {x[i]})³\n"
    detalles += f"\nEvaluación: P({x_eval}) = {resultado:.6f}"

    return resultado, detalles

# -------- REGRESIÓN LINEAL SIMPLE --------
def regresion_lineal(x, y, x_eval):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum([x[i] * y[i] for i in range(n)])
    sum_xx = sum([xi**2 for xi in x])

    m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
    b = (sum_y - m * sum_x) / n
    resultado = m * x_eval + b

    detalles = f"Recta: y = {m:.4f}x + {b:.4f}\n"
    detalles += f"Evaluación: y({x_eval}) = {resultado:.6f}"
    return resultado, detalles

# -------- GRÁFICO EN CANVAS --------
def dibujar_grafico(x_vals, y_vals, x_eval, y_eval, metodo):
    canvas.delete("all")
    w, h = 400, 300
    margin = 40
    if not x_vals or not y_vals:
        return

    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)
    x_range = x_max - x_min or 1
    y_range = y_max - y_min or 1

    def transform_x(x): return margin + (x - x_min) / x_range * (w - 2*margin)
    def transform_y(y): return h - margin - (y - y_min) / y_range * (h - 2*margin)

    # Ejes
    canvas.create_line(margin, h - margin, w - margin, h - margin)  # eje X
    canvas.create_line(margin, margin, margin, h - margin)          # eje Y

    # Puntos
    for xi, yi in zip(x_vals, y_vals):
        x_pix = transform_x(xi)
        y_pix = transform_y(yi)
        canvas.create_oval(x_pix-3, y_pix-3, x_pix+3, y_pix+3, fill='blue')

    # Punto evaluado
    canvas.create_oval(transform_x(x_eval)-4, transform_y(y_eval)-4,
                       transform_x(x_eval)+4, transform_y(y_eval)+4, fill='red')

    # Dibujar la curva (spline o regresión)
    px = []
    if metodo == "Spline":
        for i in range(100):
            xi = x_min + i * (x_max - x_min) / 99
            try:
                yi, _ = spline_cubico_natural(x_vals, y_vals, xi)
                px.append((transform_x(xi), transform_y(yi)))
            except:
                continue
    else:  # Regresión
        for i in range(100):
            xi = x_min + i * (x_max - x_min) / 99
            yi, _ = regresion_lineal(x_vals, y_vals, xi)
            px.append((transform_x(xi), transform_y(yi)))

    for i in range(1, len(px)):
        canvas.create_line(px[i-1][0], px[i-1][1], px[i][0], px[i][1], fill='green')

# -------- ACCIÓN DE BOTÓN --------
def calcular():
    try:
        x_vals = list(map(float, entry_x.get().split(',')))
        y_vals = list(map(float, entry_y.get().split(',')))
        x_eval = float(entry_eval.get())

        if len(x_vals) != len(y_vals):
            raise ValueError("Las listas X e Y deben tener la misma longitud.")

        metodo = metodo_seleccionado.get()
        if metodo == "Spline":
            resultado, detalle = spline_cubico_natural(x_vals, y_vals, x_eval)
        else:
            resultado, detalle = regresion_lineal(x_vals, y_vals, x_eval)

        label_resultado.config(text=f"Resultado: {resultado:.6f}")
        texto_detalle.delete('1.0', tk.END)
        texto_detalle.insert(tk.END, detalle)
        dibujar_grafico(x_vals, y_vals, x_eval, resultado, metodo)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# -------- INTERFAZ --------
root = tk.Tk()
root.title("Spline Cúbico y Regresión Lineal")
root.geometry("850x650")
root.configure(bg="#f8f8ff")

ttk.Label(root, text="Valores X (separados por coma):").pack()
entry_x = ttk.Entry(root, width=60)
entry_x.pack()

ttk.Label(root, text="Valores Y (separados por coma):").pack()
entry_y = ttk.Entry(root, width=60)
entry_y.pack()

ttk.Label(root, text="Valor de X a evaluar:").pack()
entry_eval = ttk.Entry(root, width=20)
entry_eval.pack()

ttk.Label(root, text="Método:").pack()
metodo_seleccionado = ttk.Combobox(root, values=["Spline", "Regresión"], state="readonly")
metodo_seleccionado.current(0)
metodo_seleccionado.pack()

ttk.Button(root, text="Calcular", command=calcular).pack(pady=10)

label_resultado = tk.Label(root, text="Resultado: ", font=("Helvetica", 14), bg="#f8f8ff")
label_resultado.pack()

texto_detalle = scrolledtext.ScrolledText(root, width=100, height=10, font=("Courier", 10))
texto_detalle.pack(padx=10, pady=10)

canvas = tk.Canvas(root, width=400, height=300, bg="white")
canvas.pack(pady=10)

root.mainloop()



