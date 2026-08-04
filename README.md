# Dur_Decode

Parse, convert, and compare duration strings — zero dependencies, Python stdlib only.

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**

## Features

- **Parse** any duration string and see all equivalent formats in one shot.
- **Add** multiple durations together.
- **Compare** two durations for equality.
- **Format** raw seconds into your preferred display style.

## Supported Formats

| Format | Example | Notes |
|--------|---------|-------|
| Human shorthand | `2h30m15s`, `1w2d`, `45m` | Units: `w` `d` `h` `m` `s` (any order) |
| ISO 8601 | `PT2H30M15S`, `P1WT3H` | Standard duration format |
| Colon | `2:30:15`, `5:45` | `H:MM:SS` or `M:SS` |
| Plain seconds | `9015`, `9015s` | Raw integer seconds |

## Installation

```bash
# Clone and run — no dependencies beyond Python 3.9+
git clone https://github.com/realMNohgee/Dur_Decode.git
cd Dur_Decode
./Dur_Decode.py --help
```

## Usage

### `parse` — decode a duration string into all formats

```bash
$ ./Dur_Decode.py parse --input '2h30m15s'
 seconds : 9015
   human : 2h30m15s
     iso : PT2H30M15S
   colon : 2:30:15

$ ./Dur_Decode.py parse --input 'PT2H30M15S'
 seconds : 9015
   human : 2h30m15s
     iso : PT2H30M15S
   colon : 2:30:15

$ ./Dur_Decode.py parse --input '1w2d5h'
 seconds : 781200
   human : 1w2d5h
     iso : P1W2DT5H
   colon : 216:00:00
```

### `add` — sum multiple durations

```bash
$ ./Dur_Decode.py add --durations 1h30m 45m 2h
 seconds : 15300
   human : 4h15m
     iso : PT4H15M
   colon : 4:15:00
```

### `compare` — check if two durations are equal

```bash
$ ./Dur_Decode.py compare --a 2h --b 120m
EQUAL: both are 2h (7200 seconds)

$ ./Dur_Decode.py compare --a 2h --b 130m
NOT EQUAL: '2h' → 2h (7200s)  ≠  '130m' → 2h10m (7800s)
```

### `format` — convert seconds to a specific style

```bash
$ ./Dur_Decode.py format --seconds 9015 --style human
2h30m15s

$ ./Dur_Decode.py format --seconds 9015 --style iso
PT2H30M15S

$ ./Dur_Decode.py format --seconds 9015 --style colon
2:30:15
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success; `compare` durations are equal |
| 1 | `compare` durations are not equal |
| 2 | Invalid style argument |

## License

MIT — see [LICENSE](LICENSE).
