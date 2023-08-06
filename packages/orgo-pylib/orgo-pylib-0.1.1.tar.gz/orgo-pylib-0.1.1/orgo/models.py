class OrgoLocalCenter:
    def __init__(self, json):
        self.id: int = json["id"]
        self.name: str = json["name"]


class OrgoDate:
    def __init__(self, json):
        self.date: str = json["date"]
        self.timezone_type: int = json["timezone_type"]
        self.timezone: str = json["timezone"]


class OrgoTown:
    def __init__(self, json):
        self.id: int = json["id"]
        self.name: str = json["name"]


class OrgoUser:
    def __init__(self, json):
        self.id: int = json["id"]
        self.cardId: int = json["cardId"]
        self.firstName: str = json["firstName"]
        self.lastName: str = json["lastName"]
        self.email: str = json["email"]
        self.feeValidUntilDate: OrgoDate = OrgoDate(json["feeValidUntilDate"])
        self.feeValidLast: str = json["feeValidLast"]
        self.town: OrgoTown = OrgoTown(json["town"])
        self.age: int = json["age"]
        self.dateOfBirth: OrgoDate = OrgoDate(json["dateOfBirth"])
        self.dateJoined: OrgoDate = OrgoDate(json["dateJoined"])
        self.status: str = json["status"]
        self.isFulMember: bool = json["isFulMember"]
        self.profileImage: str = json["profileImage"]
