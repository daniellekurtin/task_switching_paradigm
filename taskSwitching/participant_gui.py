import tkinter as tk

class Participant:
    """
    Participant has various unique properties per given session
    """

    id = ''
    gender = ''
    age = ''
    session = ''

class ParticipantGUI(tk.Tk):
    """
    Creates a pop-up box at the beginning of the experiment
    """
    fields = 'id', 'gender', 'age', 'session'

    def __init__(self, **kwargs): 

        super().__init__(**kwargs)

        self.ents = self.makeform()
        self.bind('<Return>', (lambda event, e=self.ents: self.fetch()))   
        b1 = tk.Button(self, text='OK',
                    command=(lambda e=self.ents: self.fetch()))
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(self, text='Quit', command=self.quit)
        b2.pack(side=tk.LEFT, padx=5, pady=5)
        self.mainloop()

    def fetch(self):
        self.participant = Participant()
        for entry in self.entries:
            field = entry[0]
            text  = entry[1].get()
            print('%s: "%s"' % (field, text)) 
            self.participant.__setattr__(field, text)
        self.quit()

    def makeform(self):
        self.entries = []
        for field in self.fields:
            row = tk.Frame(self)
            lab = tk.Label(row, width=15, text=field, anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries.append((field, ent))
