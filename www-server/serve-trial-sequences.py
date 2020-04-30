from taskSwitching import ExperimentTaskSwitch
import jsonpickle
import enum

from flask import Flask, jsonify
from flask_cors import CORS

# Create the application instance
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    class Config(enum.Enum):
        SYNCH_CONFIG = 'config.json'
        IN_SCANNER = False
        TR = 2  # seconds
        MIN_LOG_LEVEL = 'INFO'
        QUIT_BUTTON = 'q'

    def get_sequence():
        """
        This function just responds to the browser URL localhost:5000/

        :return: new trial sequence
        """
        exp = ExperimentTaskSwitch(
            window=None,
            config=Config,
            online=True
        )

        # Convert to JSON
        for t in range(len(exp.trials)):
            for k in ['experiment', 'countdown', 'grid']:
                if hasattr(exp.trials[t], k):
                    exp.trials[t].__delattr__(k)
            if hasattr(exp.trials[t], 'stimulus'):
                exp.trials[t].stimulus = [i.tolist() for i in exp.trials[t].stimulus]
            if hasattr(exp.trials[t], "prepare_answers"):
                exp.trials[t].prepare_answers()
                exp.trials[t].answer_index = exp.trials[t].answer_index.__int__()
                exp.trials[t].answers = [x.tolist() for x in exp.trials[t].answers]

        out = exp.trials
        del exp
        return out

    out = jsonify({"trials": jsonpickle.encode(get_sequence())})
    # out = jsonify({"trials": ["hello, world"]})
    return out


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)


