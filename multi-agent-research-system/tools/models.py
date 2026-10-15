from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    excerpt: str

    def to_dict(self):
        return asdict(self)
