from enum import Enum

class GenreEnum(Enum):
    Alternative = 'Alternative'
    Blue = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic' 
    Folk = 'Folk' 
    Funk = 'Funk' 
    HipHop = 'Hip-Hop' 
    HeavyMetal = 'Heavy Metal' 
    Instrumental = 'Instrumental' 
    Jazz = 'Jazz' 
    MusicalTheatre = 'Musical Theatre' 
    Pop = 'Pop' 
    Punk = 'Punk' 
    RB = 'R&B' 
    Reggae = 'Reggae' 
    RocknRoll = 'Rock n Roll' 
    Soul = 'Soul' 
    Other = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)

class StateEnum(Enum):
    AL 	=	1
    AK 	=	2
    AZ 	=	3
    AR 	=	4
    CA 	=	5
    CO 	=	6
    CT 	=	7
    DE 	=	8
    DC 	=	9
    FL 	=	10
    GA 	=	11
    HI 	=	12
    ID 	=	13
    IL 	=	14
    IN 	=	15
    IA 	=	16
    KS 	=	17
    KY 	=	18
    LA 	=	19
    ME 	=	20
    MT 	=	21
    NE 	=	22
    NV 	=	23
    NH 	=	24
    NJ 	=	25
    NM 	=	26
    NY 	=	27
    NC 	=	28
    ND 	=	29
    OH 	=	30
    OK 	=	31
    OR 	=	32
    MD 	=	33
    MA 	=	34
    MI 	=	35
    MN 	=	36
    MS 	=	37
    MO 	=	38
    PA 	=	39
    RI 	=	40
    SC 	=	41
    SD 	=	42
    TN 	=	43
    TX 	=	44
    UT 	=	45
    VT 	=	46
    VA 	=	47
    WA 	=	48
    WV 	=	49
    WI 	=	50
    WY 	=	51

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.name)