import taskSwitching as tS
from psychopy import visual
from pyniexp import scannersynch
import enum
import tkinter as tk


# Set some useful constants
class Config(enum.Enum):
    SYNCH_CONFIG = 'config.json'
    IN_SCANNER = False
    TR = 2 # seconds
    MIN_LOG_LEVEL = 'INFO'


if __name__ == '__main__':
    # Create the window we'll display the experiment in
    win = visual.Window(
        size=[800, 800],
        units="pix",
        fullscr=False,
        color=[0, 0, 0],
        gammaErrorPolicy="warn"
    )

    # Create interface for scanner pulse and response box
    SSO = scannersynch.scanner_synch(
        config=Config.SYNCH_CONFIG.value,
        emul_synch=not Config.IN_SCANNER.value,
        emul_buttons=not Config.IN_SCANNER.value
    )
    SSO.set_synch_readout_time(0.5)
    SSO.TR = Config.TR.value

    SSO.set_buttonbox_readout_time(0.5)
    if not SSO.emul_buttons:
        SSO.add_buttonbox('Nata')
    else:
        SSO.buttons = ['1','2','3']

    SSO.start_process()

    # Create the experiment object
    exp = tS.Experiment(
        window=win,
        synch=SSO,
        log_level=Config.MIN_LOG_LEVEL.value
    )


fields = 'Participant ID', 'Session ID', 'Date'


def fetch(entries):
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        print('%s: "%s"' % (field, text)) 


def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries


if __name__ == '__main__':
    root = tk.Tk()
    ents = makeform(root, fields)
    root.bind('', (lambda event, e=ents: fetch(e)))   
    b1 = tk.Button(root, text='Show',
                  command=(lambda e=ents: fetch(e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(root, text='Quit', command=root.quit)
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    root.mainloop()

# master = tk.Tk()
# tk.Label(master, text="First Name").grid(row=0)
# tk.Label(master, text="Last Name").grid(row=1)

# e1 = tk.Entry(master)
# e2 = tk.Entry(master)

# e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)

# master.mainloop()

    info = [tS.ComponentStart(experiment=exp)]
    exp.trials = info

    exp.synch.wait_for_synch()
    exp.run()

    exp = None
    SSO = None
