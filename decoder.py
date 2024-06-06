import json
from rust_enum import enum, Case   # a rusted pythonista here.
import numpy as np
from sklearn.cluster import KMeans


@enum
class Morse:
    """Morse code symbols"""
    Beep=Case(value=int)
    Pause=Case(value=int)

    @property
    def is_beep(self) -> bool:
        """returns True if the Morse instance is a beep"""
        match self:
            case Morse.Beep(_):
                return True
            case Morse.Pause(_):
                return False
            

    @property
    def is_pause(self):
        """returns True if the Morse instance is a pause"""
        return not self.is_beep  # clever! :)


    @property
    def val(self):
        """returns the value of the Morse instance"""
        match self:
            case Morse.Beep(value):
                return value
            case Morse.Pause(value):
                return value

def save_durations_to_file(durations: list[Morse], filename: str):
    """
    Save the durations to a file

    parameters:
    durations: list of Morse instances
    filename: str
    """
    # to json list. positive values are beeps, negative values are pauses
    durations = [d.val if d.is_beep else -d.val for d in durations]
    with open(filename, "w") as f:
        json.dump(durations, f)

def load_durations_from_file(filename: str) -> list[Morse]:
    """
    Load the durations from a file

    parameters:
    filename: str

    returns:
    durations: list of Morse instances
    """
    with open(filename, "r") as f:
        durations = json.load(f)
    # convert to Morse instances
    durations = [Morse.Beep(d) if d>0 else Morse.Pause(-d) for d in durations]
    return durations

def decode(durations: list[Morse]) -> str:
    """
    Decode the morse code from the durations of beeps and pauses

    parameters:
    durations: list of Morse instances

    returns:
    decoded_message: str
    """
    on_times = np.array([d.val for d in durations if d.is_beep])
    off_times = np.array([d.val for d in durations if d.is_pause])
    # Apply KMeans clustering to categorize the signals and pauses
    clustering_signal_on = KMeans(n_clusters=2, random_state=0).fit(on_times.reshape(-1, 1))
    clustering_signal_off = KMeans(n_clusters=3, random_state=0).fit(off_times.reshape(-1, 1))

    # Determine the length of a dot
    dot_length = np.min(clustering_signal_on.cluster_centers_)

    # Order the clusters for signals
    signal_on_order = np.argsort(clustering_signal_on.cluster_centers_.flatten())
    dot_cluster = np.where(signal_on_order == 0)[0][0]
    dash_cluster = np.where(signal_on_order == 1)[0][0]
    dash_dot_map = {dot_cluster: '.', dash_cluster: '-'}
    dash_dot_characters = np.vectorize(dash_dot_map.get)(clustering_signal_on.labels_)

    # Order the clusters for pauses
    signal_off_order = np.argsort(clustering_signal_off.cluster_centers_.flatten())
    intra_space_cluster = np.where(signal_off_order == 0)[0][0]
    char_space_cluster = np.where(signal_off_order == 1)[0][0]
    word_space_cluster = np.where(signal_off_order == 2)[0][0]

    # Identify positions of any space (either character space or word space)
    any_space_idx = np.nonzero(clustering_signal_off.labels_ != intra_space_cluster)[0]
    char_or_word_space_arr = clustering_signal_off.labels_[clustering_signal_off.labels_ != intra_space_cluster]

    # Identify positions of word spaces
    word_space_idx = np.nonzero(char_or_word_space_arr == word_space_cluster)[0]

    # Break signals into characters and words
    char_start_idx = [0] + (any_space_idx + 1).tolist()
    char_end_idx = (any_space_idx + 1).tolist() + [len(dash_dot_characters)]
    morse_characters = ["".join(dash_dot_characters[i:j]) for i, j in zip(char_start_idx, char_end_idx)]

    word_start_idx = [0] + (word_space_idx + 1).tolist()
    word_end_idx = (word_space_idx + 1).tolist() + [len(morse_characters)]
    morse_words = [" ".join(morse_characters[i:j]) for i, j in zip(word_start_idx, word_end_idx)]

    # Combine words into a single string
    decoded_message = "   ".join(morse_words)
    return decoded_message


with open("morse.json", "r", encoding="utf-8") as f:
    morse = json.load(f)
morse["_"] = " "  # word separator
back_morse = {v: k for k, v in morse.items()}

def decode_from_morse(morse_code: str) -> str:
    """
    Decode morse code to text

    parameters:
    morse_code: str

    returns:
    decoded: str
    """
    morse_code= morse_code.replace("  ", " _ ")  # word separator
    morse_code = morse_code.split()
    decoded = "".join([back_morse.get(letter, letter) for letter in morse_code])
    return decoded.replace("_", " ")

def encode_to_morse(text: str) -> str:
    """
    Encode text to morse code

    parameters:
    text: str

    returns:
    morse_code: str
    """
    text = text.lower()
    morse_code = [morse.get(letter.replace(" ", "_"), letter) for letter in text]
    return " ".join(morse_code)


class KeyDecoder:
    """Morse key decoder"""
    def __init__(self):
        self.morse_code = []  # list of beep durations and pauses
        self.decoded = ""

    def add_beep(self, duration: int):
        """
        Add a beep to the morse code

        parameters:
        duration: int
        """
        if duration<=1:
            return
        self.morse_code.append(Morse.Beep(duration))

    def add_pause(self, duration):
        """
        Add a pause to the morse code

        parameters:
        duration: int
        """
        if duration<=1:
            return
        self.morse_code.append(Morse.Pause(duration))

    def debug(self):
        """Print the morse code and the dotspeed and dashspeed"""
        print(self.morse_code)
        print(self.dotspeed, self.dashspeed)


    def decode(self) -> str:
        """
        Decode the morse code to text

        returns:
        decoded: str
        """
        # if length of morse_code is <8, we can't decode it.
        if len(self.morse_code) < 8:
            return self.decoded
        # convert durations (self.morse_code) to dots and dashes
        morse_code = decode(self.morse_code)
        self.decoded = decode_from_morse(morse_code)
        return self.decoded

    def clear(self):
        """Clear the morse code"""
        self.morse_code = []
        self.decoded = ""

    def __str__(self):
        return self.decoded


# if main, bench the decoder
if __name__ == "__main__":
    # time it!
    from timeit import timeit
    durations = load_durations_from_file("durs.json")
    time = timeit(lambda: decode(durations), number=1000)
    print(f"Decoding time: {time:.2f} seconds")