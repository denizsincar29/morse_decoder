from decoder import KeyDecoder
import wx
import time

def dbg(val):
    """Debug print and return value"""
    print(val)
    return val  # for debugging


class MorseDecoder(wx.Frame):
    """Morse Decoder GUI"""
    def __init__(self, *args, **kwargs):
        super(MorseDecoder, self).__init__(*args, **kwargs)
        self.init_ui()
        self.key_decoder = KeyDecoder()
        self.t=0
        self.pressed=False  # stupid wxpython triggers key down many times if key is held down
        self.button.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.button.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def init_ui(self):
        """Initialize the UI"""
        self.SetTitle("Morse Decoder")
        self.SetSize((500, 500))
        # make a big read only text field in a sizer in panel
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.text, 1, wx.EXPAND)
        # add a morse key button:
        self.button = wx.Button(panel, label="Morse Key")
        sizer.Add(self.button, 0, wx.EXPAND)
        
        panel.SetSizer(sizer)
        self.CreateStatusBar()
        self.Centre()

    def elapsed(self, reset: bool=False) -> int:
        """
        Return the elapsed time since last reset

        parameters:
        reset: bool

        returns:
        elapsed: int
        """
        t = time.time() - self.t if self.t>0 else 0.0
        if reset:
            self.t = time.time()
        return (round(t*1000))  # milliseconds (with debug print)

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        # if escape key is pressed, close the window
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        # if enter key, call the decoder debug method
        if keycode == wx.WXK_RETURN:
            self.key_decoder.debug()
        if keycode != wx.WXK_SPACE:
            return
        if not self.pressed:
            elapsed=self.elapsed(reset=True)
            # if elapsed is too long, reset the decoder
            if elapsed>2000:
                self.key_decoder.clear()
                self.text.SetValue("")
            else:
                self.key_decoder.add_pause(elapsed)
                self.text.SetValue(self.key_decoder.decode())
        self.pressed = True
        event.Skip()

    def on_key_up(self, event):
        keycode = event.GetKeyCode()
        if not keycode == wx.WXK_SPACE:
            return
        self.pressed = False
        # if elapsed is too long, reset the decoder
        elapsed=self.elapsed(reset=True)
        if elapsed>2000:
            self.key_decoder.clear()
            self.text.SetValue("")
        else:
            self.key_decoder.add_beep(elapsed)
            self.text.SetValue(self.key_decoder.decode())
        event.Skip()

    def on_close(self, event):
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    MorseDecoder(None)
    app.MainLoop()