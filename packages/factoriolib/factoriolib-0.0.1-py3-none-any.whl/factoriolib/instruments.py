from factoriolib._decorators import id

class Instrument:

    def __init__(self, note_id: int):

        self._noteId = note_id


    @staticmethod
    def id() -> int:

        return None


    def note_id(self) -> int:

        return self._noteId




@id(3)
class Piano(Instrument): 

    F3 = 0
    Fs3 = 1
    G3 = 2
    Gs3 = 3
    A3 = 4
    As3 = 5
    B3 = 6
    C4 = 7
    Cs4 = 8
    D4 = 9
    Ds4 = 10
    E4 = 11
    F4 = 12
    Fs4 = 13
    G4 = 14
    Gs4 = 15
    A4 = 16
    As4 = 17
    B4 = 18
    C5 = 19
    Cs5 = 20
    D5 = 21
    Ds5 = 22
    E5 = 23
    F5 = 24
    Fs5 = 25
    G5 = 26
    Gs5 = 27
    A5 = 28
    As5 = 29
    B5 = 30
    C6 = 31
    Cs6 = 32
    D6 = 33
    Ds6 = 34
    E6 = 35
    F6 = 36
    Fs6 = 37
    G6 = 38
    Gs6 = 39
    A6 = 40
    As6 = 41
    B6 = 42
    C7 = 43
    Cs7 = 44
    D7 = 45
    Ds7 = 46
    E7 = 47

    
@id(4)
class Bass(Instrument): 

    F2 = 0
    Fs2  = 1
    G2 = 2
    Gs2  = 3
    A2 = 4
    As2  = 5
    B2 = 6
    C3 = 7
    Cs3  = 8
    D3 = 9
    Ds3  = 10
    E3  = 11
    F3 = 12
    Fs3  = 13
    G3 = 14
    Gs3  = 15
    A3 = 16
    As3  = 17
    B3 = 18
    C4 = 19
    Cs4  = 20
    D4 = 21
    Ds4  = 22
    E4  = 23
    F4  = 24
    Fs4  = 25
    G4  = 26
    Gs4  = 27
    A4  = 28
    As4  = 29
    B4  = 30
    C5  = 31
    Cs5  = 32
    D5  = 33
    Ds5  = 34
    E5  = 35