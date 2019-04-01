import tkinter.ttk
import colorsys
import webcolors
import pybs


blinkstick = None


def use_black_text(rgb):
    r, g, b = rgb
    luminance = 1 - (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5


def main():
    def get_device():
        global blinkstick
        if blinkstick is None:
            try:
                blinkstick = pybs.BlinkStick(brightness=30)
            except:
                top.tk.globalsetvar('dev_button', 'No device')
            else:
                top.tk.globalsetvar('dev_button', blinkstick.get_name() or blinkstick.serial)
                change_brightness(0)

    def change_brightness(value):
        global blinkstick
        if blinkstick is not None:
            blinkstick.brightness = int(top.tk.globalgetvar('dev_brightness'))
            blinkstick.set_color([int(top.tk.globalgetvar(n)) for n in ['red', 'green', 'blue']])

    def update_color(rgb, update_name=True):
        global blinkstick

        c_hex = webcolors.rgb_to_hex(rgb)
        try:
            c_name = webcolors.hex_to_name(c_hex)
        except:
            c_name = ''
        fg = '#000' if use_black_text(rgb) else '#fff'
        canvas.configure(text=c_hex + '\n' + c_name, bg=c_hex, fg=fg)

        if update_name:
            try:
                old_name = top.tk.globalgetvar('name')
            except:
                old_name = None
            if c_name and c_name != old_name:
                top.tk.globalsetvar('name', c_name)

        if blinkstick is not None:
            try:
                blinkstick.set_color(rgb)
            except:
                blinkstick = None
                top.tk.globalsetvar('dev_button', 'No device')

    def change_hsv(value, update_name=True):
        h, s, v = (float(top.tk.globalgetvar(n)) for n in ['hue', 'saturation', 'value'])
        rgb = [int(i) for i in colorsys.hsv_to_rgb(h, s, v)]
        for name, val in zip(['red', 'green', 'blue'], rgb):
            top.tk.globalsetvar(name, val)
        update_color(rgb, update_name)

    def change_rgb(value, update_name=True):
        rgb = [int(top.tk.globalgetvar(n)) for n in ['red', 'green', 'blue']]
        h, s, v = colorsys.rgb_to_hsv(*rgb)
        # Protect agains reseetting the Hue and Saturation values needlesly when color is black
        update_vars = [('value', v)]
        if v > 0:
            update_vars.append(('saturation', s))
        if s > 0:
            update_vars.append(('hue', h))
        for name, val in update_vars:
            top.tk.globalsetvar(name, val)
        update_color(rgb, update_name)

    def change_name(*a):
        name = top.tk.globalgetvar('name')
        try:
            rgb = webcolors.html5_parse_legacy_color(name)
        except:
            return

        for name, val in zip(['red', 'green', 'blue'], rgb):
            top.tk.globalsetvar(name, val)

        change_rgb(None, False)

    top = tkinter.Tk()
    top.title('Color Tester')

    tkinter.Button(top, text='No device', command=get_device, textvariable='dev_button').pack()
    tkinter.Scale(top, takefocus=True, label='LED Brightness', orient=tkinter.HORIZONTAL, length=300, from_=0, to=100, resolution=1, variable='dev_brightness', command=change_brightness).pack(fill=tkinter.X, expand=True)
    tkinter.ttk.Separator().pack(fill=tkinter.X)
    tkinter.Scale(top, takefocus=True, label='Hue', orient=tkinter.HORIZONTAL, length=300, from_=0, to=1, resolution=0.001, variable='hue', command=change_hsv).pack(fill=tkinter.X, expand=True)
    tkinter.Scale(top, takefocus=True, label='Saturation', orient=tkinter.HORIZONTAL, length=300, from_=0, to=1, resolution=0.01, variable='saturation', command=change_hsv).pack(fill=tkinter.X, expand=True)
    tkinter.Scale(top, takefocus=True, label='Value', orient=tkinter.HORIZONTAL, length=300, from_=0, to=255, resolution=1, variable='value', command=change_hsv).pack(fill=tkinter.X, expand=True)
    tkinter.ttk.Separator().pack(fill=tkinter.X)
    tkinter.Scale(top, takefocus=True, label='Red', orient=tkinter.HORIZONTAL, length=300, from_=0, to=255, resolution=1, variable='red', command=change_rgb).pack(fill=tkinter.X, expand=True)
    tkinter.Scale(top, takefocus=True, label='Green', orient=tkinter.HORIZONTAL, length=300, from_=0, to=255, resolution=1, variable='green', command=change_rgb).pack(fill=tkinter.X, expand=True)
    tkinter.Scale(top, takefocus=True, label='Blue', orient=tkinter.HORIZONTAL, length=300, from_=0, to=255, resolution=1, variable='blue', command=change_rgb).pack(fill=tkinter.X, expand=True)
    tkinter.ttk.Separator().pack(fill=tkinter.X)
    tkinter.ttk.Combobox(top, textvariable='name', values=list(webcolors.CSS3_NAMES_TO_HEX.keys())).pack()
    tkinter.ttk.Separator().pack(fill=tkinter.X)
    canvas = tkinter.Label(top, bd=1, relief=tkinter.SUNKEN, height=5, width=20)
    canvas.pack(side=tkinter.BOTTOM)

    dummy_var = tkinter.Variable(top, name='_dummy')
    variable_callback_name = dummy_var._register(change_name)

    top.tk.call('trace', 'add', 'variable', 'name', 'write', (variable_callback_name,))

    top.tk.globalsetvar('dev_brightness', 50)

    get_device()
    update_color([0, 0, 0])

    top.mainloop()


if __name__ == "__main__":
    main()
